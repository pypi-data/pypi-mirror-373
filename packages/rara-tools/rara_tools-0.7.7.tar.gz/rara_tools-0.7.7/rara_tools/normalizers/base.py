from datetime import datetime
from pymarc import (Field, Subfield, JSONReader, Record)
from typing import List, Optional, Iterator
from rara_tools.normalizers.reader import SafeJSONReader

from rara_tools.normalizers.viaf import VIAFRecord, VIAFClient
from rara_tools.constants.normalizers import (
    DEFAULT_VIAF_FIELD, ALLOWED_VIAF_FIELDS, ALLOWED_VIAF_WIKILINK_LANGS,
    VIAF_SIMILARITY_THRESHOLD, VERIFY_VIAF_RECORD, MAX_VIAF_RECORDS_TO_VERIFY,
    EMPTY_INDICATORS
)
from glom import glom
import logging
import json

logger = logging.getLogger(__name__)


class RecordNormalizer:
    """
    Base class. For normalizing different record types corresponding classes have been created.
    By default existing record fields will not be changed, unless included in ALLOW_EDIT_FIELDS. If a field
    included in the normalization is not present, it will be added to the record. If under REPEATABLE_FIELDS.
    a new record field is added.

    Args:
        sierra_data: Optionally, can normalize records from SIERRA. Must be in specific format,
        e.g converted with SierraResponseConverter. examples at: tests/sierra/output
        entities: List of Full names (str). If included, will use NormLinker to match with normalized records on KATA elastic.
    """

    def __init__(self, linking_results: List[dict] = [], sierra_data: List[dict] = [],
                 ALLOW_EDIT_FIELDS: List[str] = ["667", "925"], REPEATABLE_FIELDS: List[str] = []):

        # Include, if will replace existing field
        self.ALLOW_EDIT_FIELDS = ALLOW_EDIT_FIELDS
        # include, if should be added alongside existing fields
        self.REPEATABLE_FIELDS = REPEATABLE_FIELDS
        self.records_extra_data = []
        self.records = self._setup_records(linking_results, sierra_data)
        self.sierra_data = sierra_data

    def _setup_records(self, linking_results: List[dict], sierra_data: List[dict]) -> JSONReader:
        """Setup initial MARC records and data.

        For linked entities:
            1. Try to get single linked normalized record from KATA elastic. If more than one found, skip.
            2. If 0 matches, search from VIAF and if 1 result found, create a new authority record from the data.
            3. If none or more than one responses found, use only Classificator data (coming from Linker?).

        for SIERRA records: normalize.
        """
        linked_records = []

        for linked in linking_results:
            entity = linked.get("original_entity")
            try:
                linked_info = linked.get("linked_info", [])
                linked_num = len(linked_info)

                if not linked_info:
                    # new record will be created
                    logger.info(
                        f"No linked entities found for {entity}")
                    continue

                if linked_num == 1:
                    linked = linked_info[0]
                    linked_records.append(linked.get("json", {}))
                    self.records_extra_data.append({
                        "entity": entity,
                        "viaf": linked.get("viaf", {}),
                        "type": "linked",
                        "edited": True
                    })
                else:
                    # new record will be created
                    logger.info(
                        f"Multiple linked entities found for {entity}")

            except Exception as e:
                logger.error(f"Error processing entity {entity}: {e}")

        self.records_extra_data.extend(
            {
                "sierraID": obj.get("sierraID"),
                "type": "sierra",
                "edited": True
            }
            for obj in (sierra_data or [])
        )

        all_records = linked_records + (sierra_data or [])

        return SafeJSONReader(
            json.dumps(all_records, ensure_ascii=False),
        )

    def _setup_records(self, linking_results: List[dict], sierra_data: List[dict]) -> JSONReader:
        """Setup initial MARC records and data.

        For linked entities:
            1. Try to get single linked normalized record from KATA elastic. If more than one found, skip.
            2. If 0 matches, search from VIAF and if 1 result found, create a new authority record from the data.
            3. If none or more than one responses found, use only Classificator data (coming from Linker?).
        """
        linked_records = []

        for linked in linking_results or []:
            if not isinstance(linked, dict):
                continue

            entity = linked.get("original_entity")
            linked_info = linked.get("linked_info", [])

            if not isinstance(linked_info, list) or not linked_info:
                continue

            if len(linked_info) == 1:
                linked_item = linked_info[0]
                if not isinstance(linked_item, dict):
                    continue

                linked_records.append(linked_item.get("json", {}))
                self.records_extra_data.append({
                    "entity": entity,
                    "viaf": linked_item.get("viaf", {}),
                    "type": "linked",
                    "edited": True
                })

        self.records_extra_data.extend(
            {
                "sierraID": obj.get("sierraID"),
                "type": "sierra",
                "edited": True
            }
            for obj in (sierra_data or [])
            if isinstance(obj, dict)
        )

        all_records = linked_records + (sierra_data or [])

        return SafeJSONReader(json.dumps(all_records, ensure_ascii=False))

    @staticmethod
    def current_timestamp():
        """6 digit timestamp."""
        return datetime.now().strftime("%H%M%S")

    @staticmethod
    def current_yyyy_dd():
        """format of 2025-03"""
        return datetime.now().strftime("%Y-%m")

    @staticmethod
    def _is_person_est_nationality(viaf_record: VIAFRecord) -> bool:
        return viaf_record.nationality == "ee"

    def _is_nxx(self, field: Field, n: str):
        """ Check if fields tag is in nxx range. """
        return field.tag.startswith(n)

    def get_record_field_or_none(self, record: Record, tag: str) -> Optional[Field]:
        return record.get_fields(tag)[0] if record.get_fields(tag) else None

    def _field_in_record(self, field: Field, record: Record) -> bool:
        """ Check if field exists in record. """
        existing_fields = record.get_fields(field.tag)
        return any(
            field.data == existing_field.data for existing_field in existing_fields)

    def _filter_equivalent_field_not_in_record(self, record: Record, fields: List[Field]) -> bool:
        """ filter out fields, that do not have an equivalent in the record. """
        return filter(lambda field: not self._field_in_record(field, record), fields)

    def get_subfield(self, record: Record, tag: str, subfield: str, default: str) -> str:
        """ get record existing subfield value or assign a fallback value. """

        field = self.get_record_field_or_none(record, tag)

        if field is None:
            return default

        subfields = field.get_subfields(subfield)
        return subfields[0] if subfields else default

    def _handle_default_fields(self, record: Record, *fields: List[Field]) -> Record:
        """ add field to record iff not present already """
        record.add_field(
            *filter(lambda field: field.tag not in [
                f.tag for f in record.get_fields()], fields)
        )

    def _handle_editable_fields(self, record: Record, *fields: List[Field]) -> Record:
        """ replace existing field with a new field. """

        editable_fields = filter(
            lambda field: field.tag in self.ALLOW_EDIT_FIELDS, fields)

        tags = [f.tag for f in editable_fields]

        record.remove_fields(
            *tags
        )
        record.add_field(
            *editable_fields
        )

    def _handle_repeatable_fields(self, record: Record, *fields: List[Field]) -> Record:
        """ add field to the record & don't replace existing field."""

        repeatable_fields = [
            field for field in fields if field.tag in self.REPEATABLE_FIELDS]

        record.add_field(
            *repeatable_fields
            # *self._filter_equivalent_field_not_in_record(
            #     record, repeatable_fields)
        )

    def _add_fields_to_record(self, record: Record, fields: List[Field]) -> Record:

        self._handle_repeatable_fields(record, *fields)
        self._handle_editable_fields(record, *fields)
        self._handle_default_fields(record, *fields)

    def _add_author(self, record: Record, viaf_record: VIAFRecord) -> Optional[Field]:

        existing_author: Optional[Field] = record.get(
            "100") or record.get("110") or record.get("111")
        if existing_author:
            return record

        type_map = {
            "Personal": "100",
            "Corporate": "110",
            "Collective": "111"
        }

        author_type = viaf_record.name_type
        tag = type_map.get(author_type, "100")

        fields = [
            Field(
                tag=tag,
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("a", viaf_record.name),
                    Subfield("b", viaf_record.name_type), # Is this correct??
                    Subfield("c", viaf_record.name_type)  # Is this correct??
                ]
            )
        ]

        self._add_fields_to_record(record, fields)

    def _normalize_common(self, record: Record, is_editing_existing_record: bool) -> None:
        """Common logic for all normalizations. """

        note = "Muudetud AI poolt" if is_editing_existing_record else "Loodud AI poolt"
        date_note = f"KRATT {self.current_yyyy_dd()}"

        fields = [
            Field(tag="667",
                  indicators=EMPTY_INDICATORS,
                  subfields=[Subfield("a", note)]),
            Field(tag="925",
                  indicators=EMPTY_INDICATORS,
                  subfields=[Subfield("t", self.get_subfield(record, "925", "t", date_note))
                             ] + ([Subfield("p", self.get_subfield(record, "925", "p", date_note))]
                                  if is_editing_existing_record else []))
        ]

        self._add_fields_to_record(record, fields)

        return record

    def _get_viaf_search_term(self, record: Record, entity: Optional[str]) -> Optional[str]:
        """ prioritize entity name, if not available, use author name. """
        if entity:
            return entity

        author_field = record.get("100") or record.get("110") or record.get("111")
        if author_field:
            return author_field.get_subfields("a")[0] if author_field.get_subfields("a") else None

        logger.warning(
            "No entity or author name found for VIAF search. Skipping VIAF enrichment.")

    def _get_viaf_record(self, record: Record, viaf_id: Optional[int] = None,
            entity: Optional[str] = None, viaf_field: str = DEFAULT_VIAF_FIELD,
            threshold: float = VIAF_SIMILARITY_THRESHOLD, verify: bool = VERIFY_VIAF_RECORD,
            max_records: int = MAX_VIAF_RECORDS_TO_VERIFY
    ) -> Optional[VIAFRecord]:
        viaf_record = None

        try:
            viaf_client = VIAFClient()

            if viaf_id:
                viaf_records = viaf_client.get_normalized_data_by_ids([viaf_id])
                if viaf_records:
                    viaf_record = viaf_records[0]
            else:
                search_term = self._get_viaf_search_term(record, entity)

                if search_term:
                    logger.info(
                        f"Searching for VIAF record with search term: {search_term}")

                    if not verify:
                        logger.warning(
                            f"Record verification is turned off. If multiple records are " \
                            f"detected for search term '{search_term}', the first " \
                            f"result is automatically returned. This might lead to " \
                            f"some inaccuracies!"
                        )

                    viaf_record = viaf_client.get_normalized_data_by_search_term(
                        search_term=search_term,
                        field=viaf_field,
                        max_records=max_records,
                        verify=verify,
                        threshold=threshold
                    )

        except Exception as e:
            logger.error(
                f"Error fetching VIAF record with ID={viaf_id} / entity='{entity}': {e}"
            )
        return viaf_record

    def _normalize_record(self, record: Record, sierraID: str,
                          viaf_record: VIAFRecord, is_editing_existing_record: bool) -> Record:
        return record

    @property
    def data(self) -> List[dict]:
        """Shorthand to get all normalized records as dict, skipping failures."""
        result = []
        for record in self:
            try:
                result.append(record.as_dict())
            except Exception as e:
                logger.error(f"Failed to normalize record: {e}")
                continue
        return result

    def __iter__(self) -> Iterator:
        viaf_id_path = "viaf.queryResult.records.record.0.recordData.VIAFCluster.viafID"
        sierra_id_path = "sierraID"

        for record, extra_data in zip(self.records, self.records_extra_data):

            sierra_id = glom(extra_data, sierra_id_path, default="")
            viaf_id = glom(extra_data, viaf_id_path, default=None)

            entity = extra_data.get("entity")
            is_editing_existing_record = extra_data.get("edited") == True

            viaf_record = self._get_viaf_record(record, viaf_id, entity)
            record = self._normalize_common(record, is_editing_existing_record)

            normalized_record = self._normalize_record(
                record, sierra_id, viaf_record, is_editing_existing_record)

            normalized_record.fields.sort(key=lambda field: field.tag)

            yield normalized_record

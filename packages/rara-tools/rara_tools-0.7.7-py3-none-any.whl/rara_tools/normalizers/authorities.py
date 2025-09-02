from rara_tools.constants import EMPTY_INDICATORS
from rara_tools.normalizers.viaf import VIAFRecord

from rara_tools.normalizers import RecordNormalizer

from pymarc import Field, Subfield, Record
from typing import List


class AuthoritiesRecordNormalizer(RecordNormalizer):
    """ Normalize authorities records """

    def __init__(self, linking_results: List[dict] = [], sierra_data: List[dict] = [],
                 ALLOW_EDIT_FIELDS: List[str] = [
                     "667", "925", "043"],
                 REPEATABLE_FIELDS: List[str] = ["024", "035", "400", "670"]):

        super().__init__(linking_results, sierra_data)
        self.ALLOW_EDIT_FIELDS = ALLOW_EDIT_FIELDS
        self.REPEATABLE_FIELDS = REPEATABLE_FIELDS

    def _normalize_sierra(self, record: Record, sierraID: str) -> None:

        suffix_008 = "|n|adnnnaabn          || |a|      "

        fields = [
            Field(
                tag="008",
                indicators=EMPTY_INDICATORS,
                data=f"{self.current_timestamp()}{suffix_008}"
            ),

            Field(
                tag="040",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    # if record subfield exists already, use that value. if not, use hardcoded value
                    Subfield("a", self.get_subfield(
                        record, "040", "a", "ErESTER")),
                    Subfield("b", self.get_subfield(
                        record, "040", "b", "est")),
                    Subfield("c", self.get_subfield(
                        record, "040", "c", "ErEster")),
                ]
            ),
        ]

        self._add_fields_to_record(record, fields)

        return record

    def _add_birth_and_death_dates(self, record: Record, viaf_record: VIAFRecord) -> None:
        subfields_046 = [
            Subfield("f", self.get_subfield(
                record, "046", "f", viaf_record.birth_date)),
            Subfield("g", self.get_subfield(
                record, "046", "g", viaf_record.death_date)),
            Subfield("s", self.get_subfield(
                record, "046", "s", viaf_record.activity_start)),
            Subfield("t", self.get_subfield(
                record, "046", "t", viaf_record.activity_end)),
        ]

        self._add_fields_to_record(
            record, [Field(tag="046", indicators=EMPTY_INDICATORS, subfields=subfields_046)])

    def _add_viaf_url_and_isni(self, record: Record, viaf_record: VIAFRecord) -> None:
        # TODO 024. will be used to store KRATT KATA ID. Just generate one?
        viaf_url = f"https://viaf.org/viaf/{viaf_record.viaf_id}"

        subfields = [Subfield("0", self.get_subfield(
            record, "024", "0", viaf_url))]

        if viaf_record.has_isni:
            subfields.append(Subfield("2", "isni"))

        field = Field(tag="024", indicators=EMPTY_INDICATORS,
                      subfields=subfields)

        self._add_fields_to_record(record, [field])

    def _add_nationality(self, record: Record, viaf_record: VIAFRecord) -> None:

        fields = [
            Field(
                tag="043",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("c", "ee")
                ] if self._is_person_est_nationality(viaf_record) else []
            )]

        self._add_fields_to_record(record, fields)

    def _normalize_viaf(self, record: Record, viaf_record: VIAFRecord) -> None:
        """"
        Attempts to enrich the record with VIAF data.

        024 - repeatable field, add VIAF URL to subfield 0. If ISNI found, add to subfield 2
        043 - repeatable field. Add "ee" if found to be estonian nationality
        046 - non-repeatable field, add birth and death dates
        100, 110, 111 - non-repeatable field, attempts to add author type, if missing.

        """
        # TODO: include KRATT KATA ID to 024 and remove on delete. Increment last elastic ID?
        if not viaf_record:
            return

        self._add_nationality(record, viaf_record)
        self._add_viaf_url_and_isni(record, viaf_record)
        self._add_birth_and_death_dates(record, viaf_record)
        self._add_author(record, viaf_record)

    def _normalize_record(self, record: Record, sierraID: str,
                          viaf_record: VIAFRecord, is_editing_existing_record: bool) -> Record:

        self._normalize_sierra(record, sierraID)
        self._normalize_viaf(record, viaf_record)

        return record

from pymarc import (Field, Indicators, Subfield, Record)

from rara_tools.constants import EMPTY_INDICATORS
from rara_tools.normalizers.viaf import VIAFRecord
from rara_tools.normalizers import RecordNormalizer

from typing import List


class BibRecordNormalizer(RecordNormalizer):
    """ Normalize bib records. """

    def __init__(self, linking_results: List[dict] = [], sierra_data: List[dict] = [],
                 ALLOW_EDIT_FIELDS: List[str] = ["667", "925"],
                 REPEATABLE_FIELDS: List[str] = []):
        super().__init__(linking_results, sierra_data)
        self.ALLOW_EDIT_FIELDS = ALLOW_EDIT_FIELDS
        self.REPEATABLE_FIELDS = REPEATABLE_FIELDS

    def _normalize_sierra(self, record: Record) -> Record:
        fields = [
            Field(
                tag="008",
                indicators=EMPTY_INDICATORS,
                data=f"{self.current_timestamp()} | | | aznnnaabn | | | | |"
            ),
            Field(
                tag="046",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("k", "Pub date")
                ]
            ),
            Field(
                tag="245",
                indicators=Indicators("1", "0"),
                subfields=[
                    Subfield("a", "Title")
                ]
            ),
        ]

        self._add_fields_to_record(record, fields)

    def _normalize_viaf(self, record: Record, viaf_record: VIAFRecord) -> None:

        if not viaf_record:
            return record

        viaf_id = viaf_record.viaf_id
        fields = [
            Field(
                tag="035",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("a", viaf_id)
                ]
            ),
            Field(
                tag="100",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("a", "?")
                ]
            )]

        self._add_fields_to_record(record, fields)
        self._add_author(record, viaf_record)

    def _normalize_record(self, record: Record, sierraID: str,
                          viaf_record: VIAFRecord, is_editing_existing_record: bool) -> Record:

        self._normalize_sierra(record)
        self._normalize_viaf(record, viaf_record)

        return record

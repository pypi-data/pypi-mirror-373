from typing import List, NoReturn
from pymarc.record import Record
from rara_tools.parsers.tools.entity_normalizers import KeywordNormalizer
from rara_tools.parsers.marc_records.base_record import BaseRecord
from rara_tools.constants.parsers import (
    EMSMarcIDs, KeywordType,
    EN_SUBJECT_FIELDS, ET_SUBJECT_FIELDS
)
import regex as re
import json



class EMSRecord(BaseRecord):
    """ Generates a simplified EMS JSON record
    from a pymarc MARC record.
    """
    def __init__(self, record: Record, add_variations: bool = False) -> NoReturn:
        """ Initializes EMSRecord object.

        Parameters
        -----------
        record: Record
            pymarc.record.Record object.
        add_variations: bool
            If enabled, constructs an additional variations field, which
            combines the content of multiple fields + adds some generated
            variations. If the output is uploaded into Elastic and used
            via rara-norm-linker, it is necessary to enable this.
        """
        super().__init__(record=record, add_variations=add_variations)
        self.__en_subject_field_mapping: dict = EN_SUBJECT_FIELDS
        self.__et_subject_field_mapping: dict = ET_SUBJECT_FIELDS
        self.__keyword: str = ""
        self.__keyword_en: str = ""
        self.__keyword_type: str = ""
        self.__keyword_variations: List[str] = []
        self.__keyword_fields = {
            EMSMarcIDs.TIME_KEYWORD: KeywordType.TIME,
            EMSMarcIDs.TOPIC_KEYWORD: KeywordType.TOPIC,
            EMSMarcIDs.LOC_KEYWORD: KeywordType.LOC,
            EMSMarcIDs.GENRE_KEYWORD: KeywordType.GENRE
        }

        self.__ems_url_ids = EMSMarcIDs.URL
        self.__synonym_ids = EMSMarcIDs.SYNONYMS
        self.__related_ids = EMSMarcIDs.RELATED
        self.__category_ids = EMSMarcIDs.CATEGORY
        self.__notes_ids = EMSMarcIDs.NOTES
        self.__synonyms: List[str] = []
        self.__synonyms_en: List[str] = []
        self.__subject_field_ids: List[str] = []

        self.__subject_fields_et: List[str] = []
        self.__subject_fields_en: List[str] = []
        self.__ems_url: str = ""
        self.__narrower: List[str] = []
        self.__broader: List[str] = []
        self.__related: List[str] = []
        self.__narrower_ems_urls: List[str] = []
        self.__broader_ems_urls: List[str] = []
        self.__related_ems_urls: List[str] = []
        self.__variations: List[str] = []
        self.__variations_en: List[str] = []
        self.__use_with_others: bool | None = None
        self.__full_record: dict = {}

    @property
    def keyword(self) -> str:
        if not self.__keyword:
            self.__keyword = self.get_values(
                marc_ids=self.__keyword_fields,
                subfield_id="a"
            )[0]
        return self.__keyword

    @property
    def keyword_en(self) -> str:
        if not self.__keyword_en:
            self.__keyword_en = self.synonyms_en[0] if self.synonyms_en else ""
        return self.__keyword_en

    @property
    def synonyms(self) -> List[str]:
        if not self.__synonyms:
            self.__synonyms = self.get_values(
                marc_ids=self.__synonym_ids,
                subfield_id="a"
            )
        return self.__synonyms

    @property
    def synonyms_en(self) -> List[str]:
        if not self.__synonyms_en:
            self.__synonyms_en = self.get_values(
                marc_ids=self.__synonym_ids,
                subfield_id="a", ind2="9"
            )
        return self.__synonyms_en

    @property
    def subject_field_ids(self) -> List[str]:
        if not self.__subject_field_ids:
            self.__subject_field_ids = self.get_values(
                marc_ids=self.__category_ids,
                subfield_id="a",
                ind2="7"
            )
        return self.__subject_field_ids

    @property
    def subject_fields_et(self) -> List[str]:
        if not self.__subject_fields_et:
            self.__subject_fields_et = [
                self.__et_subject_field_mapping[_id]
                for _id in self.subject_field_ids
            ]
        return self.__subject_fields_et

    @property
    def subject_fields_en(self) -> List[str]:
        if not self.__subject_fields_en:
            self.__subject_fields_en = [
                self.__en_subject_field_mapping[_id]
                for _id in self.subject_field_ids
            ]
        return self.__subject_fields_en


    @property
    def ems_url(self) -> str:
        if not self.__ems_url:
            self.__ems_url = self.get_values(
                marc_ids=self.__ems_url_ids,
                subfield_id="0",
                ind2="8"
            )[0]
        return self.__ems_url

    @property
    def broader(self) -> List[str]:
        if not self.__broader:
            self.__broader = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="a",
                subfield_restriction = ("w", "g")
            )
        return self.__broader

    @property
    def narrower(self) -> List[str]:
        if not self.__narrower:
            self.__narrower = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="a",
                subfield_restriction = ("w", "h")
            )
        return self.__narrower

    @property
    def related(self) -> List[str]:
        if not self.__related:
            self.__related = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="a",
                subfield_to_ignore ="w"
            )
        return self.__related

    @property
    def broader_ems_urls(self) -> List[str]:
        if not self.__broader_ems_urls:
            self.__broader_ems_urls = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="0",
                subfield_restriction = ("w", "g")
            )
        return self.__broader_ems_urls

    @property
    def narrower_ems_urls(self) -> List[str]:
        if not self.__narrower_ems_urls:
            self.__narrower_ems_urls = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="0",
                subfield_restriction = ("w", "h")
            )
        return self.__narrower_ems_urls

    @property
    def related_ems_urls(self) -> List[str]:
        if not self.__related_ems_urls:
            self.__related_ems_urls = self.get_values(
                marc_ids=self.__related_ids,
                subfield_id="0",
                subfield_to_ignore ="w"
            )
        return self.__related_ems_urls

    @property
    def keyword_type(self) -> str:
        if not self.__keyword_type:
            for field in self.dict_record:
                field_id = list(field.keys())[0]
                if field_id in self.__keyword_fields:
                    self.__keyword_type = self.__keyword_fields[field_id]
        return self.__keyword_type

    @property
    def use_with_others(self) -> bool:
        if self.__use_with_others == None:
            notes = self.get_values(marc_ids=self.__notes_ids, subfield_id="i")
            self.__use_with_others = False
            if notes:
                if re.search(r"Kasutada koos teise", notes[0]):
                    self.__use_with_others = True

        return self.__use_with_others

    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            original_variations = self.synonyms + [self.keyword]
            variations = []
            for kw in original_variations:
                variations_ = KeywordNormalizer(kw, keyword_type=self.keyword_type).variations
                variations.extend(variations_)
            self.__variations = [v.lower() for v in list(set(variations))]
        return self.__variations

    @property
    def variations_en(self) -> List[str]:
        if not self.__variations_en:
            pass
        return self.__variations_en


    @property
    def full_record(self) -> dict:
        if not self.__full_record:
            self.__full_record = {
                "keyword": self.keyword,
                "keyword_en": self.keyword_en,
                "keyword_type": self.keyword_type,
                "use_with_others": self.use_with_others,
                "subject_field_ids": self.subject_field_ids,
                "subject_fields_et": self.subject_fields_et,
                "subject_fields_en": self.subject_fields_en,
                "synonyms": self.synonyms,
                "synonyms_en": self.synonyms_en,
                "narrower": self.narrower,
                "broader": self.broader,
                "related": self.related,
                "narrower_ems_urls": self.narrower_ems_urls,
                "broader_ems_urls": self.broader_ems_urls,
                "related_ems_urls": self.related_ems_urls,
                "ems_id": self.identifier,
                "ems_url": self.ems_url,
                "identifier_source": self.identifier_source,
                "full_record_marc": str(self.marc_record),
                "full_record_json": json.dumps(self.marc_json_record)
            }
            if self.add_variations:
                self.__full_record.update(
                    {"link_variations": self.variations}
                )
        return self.__full_record

from rara_tools.constants.linker import (
    LOGGER, URLSource, KeywordSource, EntityType, KeywordType,
    KEYWORD_MARC_MAP,  KEYWORD_TYPES_TO_IGNORE, KEYWORD_TYPE_MAP,
    EMS_ENTITY_TYPES, SIERRA_ENTITY_TYPES, UNLINKED_KEYWORD_MARC_FIELD,
    URL_SOURCE_MAP
)

from rara_tools.parsers.marc_records.person_record import PersonRecord
from rara_tools.parsers.marc_records.organization_record import OrganizationRecord
from rara_tools.parsers.marc_records.title_record import TitleRecord
from rara_tools.utils import format_date
from typing import List, Dict, NoReturn, Tuple, Any


class FormattedObject:
    def __init__(self, object_dict: dict, linked_doc: Any, original_entity_key: str):
        self.object_dict: dict = object_dict
        self.linked_doc: Any = linked_doc
        self.viaf_info: dict = self.linked_doc.viaf.get("parsed", {}) if self.linked_doc else {}
        self.original_entity: str = self.object_dict.get(original_entity_key)
        self.is_linked: bool = True if self.linked_doc else False

        self.__original_record: PersonRecord | OrganizationRecord | TitleRecord | None = None
        self.__persons_title: str | None = None
        self.__dates: str | None = None
        self.__numeration: str | None = None
        self.__location: str | None = None
        self.__organization_sub_unit: str | None = None
        self.__entity: str | None = None
        self.__titles: str | None = None
        self.__identifier: str | None = ""


    @property
    def original_record(self) -> PersonRecord | OrganizationRecord | None:
        if not self.__original_record and self.linked_doc and self.linked_doc.json:
            try:
                if self.entity_type == EntityType.PER:
                    original_record = PersonRecord(self.linked_doc.json)
                elif self.entity_type == EntityType.ORG:
                    original_record = OrganizationRecord(self.linked_doc.json)
                elif self.entity_type == EntityType.TITLE:
                    original_record = TitleRecord(self.linked_doc.json)
                else:
                    original_record = None
            except Exception as e:
                LOGGER.exception(
                    f"Could not retrieve JSON from LinkedDoc instance. Exception: '{e}'."
                )
                original_record = None
            self.__original_record = original_record
        return self.__original_record


    @property
    def entity(self) -> str:
        if self.__entity == None:
            if self.linked_doc != None:
                if self.entity_type == EntityType.ORG and self.original_record:
                    self.__entity = self.original_record.original_name.get("a", "")
                else:
                    self.__entity = self.linked_doc.linked_entity
                if not self.__entity and self.viaf_info:
                    self.__entity = self.viaf_info.get("name", self.original_entity)
            else:
                self.__entity = self.original_entity
        return self.__entity



    @property
    def dates(self) -> str:
        if self.__dates == None:
            self.__dates = ""
            if self.viaf_info:
                birth_date = format_date(self.viaf_info.get("birth_date", ""))
                death_date = format_date(self.viaf_info.get("death_date", ""))
                if not death_date:
                    death_date = ""

                if birth_date:
                    self.__dates = f"{birth_date}-{death_date}"

            if self.original_record and not self.__dates:
                if self.entity_type == EntityType.PER:
                    self.__dates = self.original_record.life_years
                elif self.entity_type == EntityType.ORG:
                    self.__dates = self.original_record.dates
                elif self.entity_type == EntityType.TITLE:
                    self.__dates = self.original_record.author_life_years

        return self.__dates


    @property
    def numeration(self) -> str:
        if self.__numeration == None:
            self.__numeration = ""
            if self.original_record:
                if self.entity_type == EntityType.PER:
                    self.__numeration = self.original_record.original_name.get("b", "")
                elif self.entity_type == EntityType.ORG:
                    self.__numeration = self.original_record.numeration
        return self.__numeration

    @property
    def location(self) -> str:
        if self.__location == None:
            self.__location = ""
            if self.entity_type == EntityType.ORG and self.original_record:
                self.__location = self.original_record.location
        return self.__location

    @property
    def organisation_sub_unit(self) -> str:
        if self.__organization_sub_unit == None:
            self.__organization_sub_unit = ""
            if self.entity_type == EntityType.ORG and self.original_record:
                self.__organization_sub_unit = self.original_record.original_name.get("b", "")
        return self.__organization_sub_unit

    @property
    def titles(self) -> str:
        if self.__titles == None:
            if self.entity_type == EntityType.PER and self.original_record:
                self.__titles = self.original_record.name_specification
            else:
                self.__titles = ""
        return self.__titles

    @property
    def identifier(self) -> str:
        if self.__identifier == None:
            self.__identifier = ""
            if self.original_record:
                self.__identifier = self.original_record.identifier
        return self.__identifier

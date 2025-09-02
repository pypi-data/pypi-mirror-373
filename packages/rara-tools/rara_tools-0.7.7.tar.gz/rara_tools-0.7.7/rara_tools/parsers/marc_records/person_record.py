from typing import List, NoReturn
from pymarc.record import Record
from rara_tools.parsers.tools.entity_normalizers import PersonNormalizer
from rara_tools.parsers.marc_records.base_record import BaseRecord
from rara_tools.constants.parsers import PersonMarcIDs, LOGGER
import regex as re
import json
import logging


class PersonRecord(BaseRecord):
    """ Generates a simplified organization JSON record
    from a pymarc MARC record.
    """
    def __init__(self, record: Record, add_variations: bool = False) -> NoReturn:
        """ Initializes PersonRecord object.

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

        self.__name_field_id: List[str] = PersonMarcIDs.NAME
        self.__name_variations_field_id: List[str]= PersonMarcIDs.NAME_VARIATIONS
        self.__source_field_id: List[str] = PersonMarcIDs.SOURCE
        self.__description_field_id: List[str] = PersonMarcIDs.DESCRIPTION
        self.__default_year: int | None = None

        self.__name: str = ""
        self.__original_name: dict = {}
        self.__name_specification: str = ""
        self.__life_years: str = ""
        self.__birth_year: int = -1
        self.__death_year: int = -1
        self.__name_variations: List[str] = []
        self.__source: str = ""
        self.__description: str = ""
        self.__full_record: dict = {}
        self.__name_in_cyrillic: bool = None
        self.__variations: List[str] = []
        self.__person_normalizer: PersonNormalizer = PersonNormalizer(self.name)


    def _parse_year(self, year: str) -> int:
        year = year.strip()
        _year = self.__default_year
        if len(year) >= 4:
            if year[:4].isnumeric():
                _year = int(year[:4])
        elif len(year) == 3 and year.isnumeric():
            _year = int(year)
        return _year

    @property
    def original_name(self) -> str:
        if not self.__original_name:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id=["a", "b"]
            )
            if values:
                self.__original_name = {
                    "a": self._clean_value(values[0].get("a", "")),
                    "b": self._clean_value(values[0].get("b", ""))
                }
            else:
                pass
        return self.__original_name

    @property
    def name(self) -> str:
        if not self.__name:
            self.__name = self._merge_and_clean(self.original_name, ["a", "b"])
        return self.__name


    @property
    def name_specification(self) -> str:
        if not self.__name_specification:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id="c"
            )
            self.__name_specification = self._clean_value(values[0]) if values else ""
        return self.__name_specification

    @property
    def life_years(self) -> str:
        if not self.__life_years:
            values = self.get_values(
                marc_ids = self.__name_field_id,
                subfield_id="d"
            )
            self.__life_years = self._clean_value(values[0]) if values else ""
        return self.__life_years


    @property
    def birth_year(self) -> int:
        if self.__birth_year == -1:
            try:
                birth_year, death_year = self.life_years.split("-")
                self.__birth_year = self._parse_year(birth_year)
                self.__death_year = self._parse_year(death_year)
            except Exception as e:
                LOGGER.warning(
                    f"Failed extracting birth and/or death year " \
                    f"from '{self.life_years}' with the following " \
                    f"exception: '{e}'."
                )
        return self.__birth_year


    @property
    def death_year(self) -> int:
        if self.__death_year == -1:
            try:
                birth_year, death_year = self.life_years.split("-")
                self.__birth_year = self._parse_year(birth_year)
                self.__death_year = self._parse_year(death_year)
            except Exception as e:
                LOGGER.warning(
                    f"Failed extracting birth and/or death year " \
                    f"from '{self.life_years}' with the following " \
                    f"exception: '{e}'."
                )
        return self.__death_year

    @property
    def name_variations(self) -> List[str]:
        if not self.__name_variations:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id=["a", "b"]
            )
            if values:
                raw_variations = [
                    {
                        "a": self._clean_value(value.get("a", "")),
                        "b": self._clean_value(value.get("b", ""))
                    }
                    for value in values
                ]
                self.__name_variations = [
                    self._merge_and_clean(value, ["a", "b"])
                    for value in raw_variations
                ]
            else:
                pass
        return self.__name_variations

    @property
    def source(self) -> str:
        if not self.__source:
            values = self.get_values(
                marc_ids=self.__source_field_id,
                subfield_id="a"
            )
            self.__source = self._clean_value(values[0]) if values else ""
        return self.__source

    @property
    def description(self) -> str:
        if not self.__description:
            values = self.get_values(
                marc_ids=self.__description_field_id,
                subfield_id="i"
            )
            self.__description = self._clean_value(values[0]) if values else ""
        return self.__description

    @property
    def name_in_cyrillic(self) -> bool:
        if self.__name_in_cyrillic == None:
            self.__name_in_cyrillic = PersonNormalizer.has_cyrillic(self.name)
        return self.__name_in_cyrillic

    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            variations_ = self.__person_normalizer.variations
            for name in self.name_variations:
                variations_.extend(PersonNormalizer(name).variations)
            self.__variations = [v.lower() for v in list(set(variations_))]
        return self.__variations

    @property
    def full_record(self) -> dict:
        if not self.__full_record:
            self.__full_record = {
                "name": self.name,
                "life_year": self.life_years,
                "source": self.source,
                "birth_year": self.birth_year,
                "death_year": self.death_year,
                "identifier": self.identifier,
                "identifier_source": self.identifier_source,
                "name_variations": self.name_variations,
                "name_specification": self.name_specification,
                "description": self.description,
                "name_in_cyrillic": self.name_in_cyrillic,
                "full_record_marc": str(self.marc_record),
                "full_record_json": json.dumps(self.marc_json_record)
            }
            if self.add_variations:
                self.__full_record.update(
                    {"link_variations": self.variations}
                )

        return self.__full_record

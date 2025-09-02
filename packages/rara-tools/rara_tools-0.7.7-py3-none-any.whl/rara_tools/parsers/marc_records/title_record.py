from typing import List, NoReturn
from pymarc.record import Record
from rara_tools.parsers.marc_records.base_record import BaseRecord
from rara_tools.constants.parsers import TitleMarcIDs, LOGGER
import regex as re
import json
import logging


class TitleRecord(BaseRecord):
    """ Generates a simplified title JSON record
    from a pymarc MARC record.
    """
    def __init__(self, record: Record, add_variations: bool = False) -> NoReturn:
        """ Initializes TitleRecord object.

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

        self.__name_field_id: List[str] = TitleMarcIDs.NAME
        self.__name_variations_field_id: List[str]= TitleMarcIDs.NAME_VARIATIONS
        self.__year_field_id: List[str] = TitleMarcIDs.YEAR
        self.__type_field_id: List[str] = TitleMarcIDs.TYPE

        self.__default_year: int | None = None

        self.__name: str = ""
        self.__author_original_name: dict = {}
        self.__author_name: str = ""
        self.__year: int = -1
        self.__type: str = ""

        self.__author_life_years: str = ""
        self.__author_birth_year: int = -1
        self.__author_death_year: int = -1
        self.__name_variations: List[str] = []
        self.__full_record: dict = {}


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
    def name(self) -> str:
        if not self.__name:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id="t"
            )
            if values:
                self.__name = self._clean_value(values[0])
            else:
                pass
        return self.__name


    @property
    def year(self) -> str:
        if self.__year == -1:
            values = self.get_values(
                marc_ids=self.__year_field_id,
                subfield_id="k"
            )
            self.__year = self._clean_value(values[0]) if values else None
        return self.__year

    @property
    def type(self) -> str:
        if not self.__type:
            values = self.get_values(
                marc_ids = self.__type_field_id,
                subfield_id="a"
            )
            self.__type = self._clean_value(values[0]) if values else ""
        return self.__type

    @property
    def author_original_name(self) -> str:
        if not self.__author_original_name:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id=["a", "b"]
            )
            if values:
                self.__author_original_name = {
                    "a": self._clean_value(values[0].get("a", "")),
                    "b": self._clean_value(values[0].get("b", ""))
                }
            else:
                pass
        return self.__author_original_name

    @property
    def author_name(self) -> str:
        if not self.__author_name:
            self.__author_name = self._merge_and_clean(self.author_original_name, ["a", "b"])
        return self.__author_name

    @property
    def author_life_years(self) -> str:
        if not self.__author_life_years:
            values = self.get_values(
                marc_ids = self.__name_field_id,
                subfield_id="d"
            )
            self.__author_life_years = self._clean_value(values[0]) if values else ""
        return self.__author_life_years


    @property
    def author_birth_year(self) -> int:
        if self.__author_birth_year == -1:
            try:
                birth_year, death_year = self.author_life_years.split("-")
                self.__author_birth_year = self._parse_year(birth_year)
                self.__author_death_year = self._parse_year(death_year)
            except Exception as e:
                LOGGER.warning(
                    f"Failed extracting birth and/or death year " \
                    f"from '{self.author_life_years}' with the following " \
                    f"exception: '{e}'."
                )
        return self.__author_birth_year


    @property
    def author_death_year(self) -> int:
        if self.__author_death_year == -1:
            try:
                birth_year, death_year = self.author_life_years.split("-")
                self.__author_birth_year = self._parse_year(birth_year)
                self.__author_death_year = self._parse_year(death_year)
            except Exception as e:
                LOGGER.warning(
                    f"Failed extracting birth and/or death year " \
                    f"from '{self.author_life_years}' with the following " \
                    f"exception: '{e}'."
                )
        return self.__author_death_year

    @property
    def name_variations(self) -> List[str]:
        if not self.__name_variations:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id="t"
            )
            variations = [self.name]
            if values:
                _variations = [
                    self._clean_value(value)
                    for value in values
                ]
                variations.extend(_variations)
            variations = [v.lower() for v in variations]
            self.__name_variations = list(set(variations))
        return self.__name_variations


    @property
    def full_record(self) -> dict:
        if not self.__full_record:
            self.__full_record = {
                "name": self.name,
                "author_name": self.author_name,
                "year": self.year,
                "type": self.type,
                "author_life_years": self.author_life_years,
                "author_birth_year": self.author_birth_year,
                "author_death_year": self.author_death_year,
                "name_variations": self.name_variations,
                "full_record_marc": str(self.marc_record),
                "full_record_json": json.dumps(self.marc_json_record)
            }
            if self.add_variations:
                self.__full_record.update(
                    {"link_variations": self.name_variations}
                )

        return self.__full_record

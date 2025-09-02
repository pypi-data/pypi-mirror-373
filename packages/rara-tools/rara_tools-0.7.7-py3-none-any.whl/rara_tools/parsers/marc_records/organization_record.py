from typing import List, NoReturn
from pymarc.record import Record
from rara_tools.parsers.marc_records.base_record import BaseRecord
from rara_tools.constants.parsers import OrganizationMarcIDs, LOGGER
import regex as re
import json

# TODO: indikaatorid ind1 väljadel 100 ja 400?


class OrganizationRecord(BaseRecord):
    """ Generates a simplified organization JSON record
    from a pymarc MARC record.
    """
    def __init__(self, record: Record, add_variations: bool = False) -> NoReturn:
        """ Initializes OrganizationRecord object.

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

        self.__name_field_id: List[str] = OrganizationMarcIDs.NAME
        self.__name_variations_field_id: List[str] = OrganizationMarcIDs.NAME_VARIATIONS
        self.__related_names_field_id: List[str] = OrganizationMarcIDs.RELATED_NAMES
        self.__source_field_id: List[str] = OrganizationMarcIDs.SOURCE
        self.__description_field_id: List[str] = OrganizationMarcIDs.DESCRIPTION
        self.__area_code_id: List[str] = OrganizationMarcIDs.AREA_CODE
        self.__default_year: int | None = None

        self.__name: str = ""
        self.__original_name: dict = {}
        self.__name_specification: str = ""
        self.__dates: str = ""
        self.__location: str = ""
        self.__numeration: str = ""
        self.__name_variations: List[str] = []
        self.__source: str = ""
        self.__description: str = ""
        self.__area_code: str = ""
        self.__acronyms: List[str] = []
        self.__alternative_names: List[str] = []
        self.__related_acronyms: List[str] = []
        self.__old_names: List[str] = []
        self.__new_names: List[str] = []
        self.__related_old_names: List[str] = []
        self.__related_new_names: List[str] = []
        self.__full_record: dict = {}
        self.__variations: List[str] = []


    def _clean_value(self, value: str) -> str:
        try:
            cleaned_value = value.strip("., ")
        except Exception as e:
            cleaned_value = ""
        return cleaned_value

    def _merge_and_clean(self, value: dict, keys: List[str]) -> str:
        _merged = []
        for key in keys:
            _value = self._clean_value(value.get(key, ""))
            if _value:
                _merged.append(_value)
        merged = " ".join(_merged)
        return merged

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
                LOGGER.info(
                    f"Could not parse subfields 'a' and/or 'b' from " \
                    f"field {self.__name_field_id}. Record:\n{self.marc_record}"
                )
        return self.__original_name

    @property
    def name(self) -> str:
        if not self.__name:
            self.__name = self._merge_and_clean(self.original_name, ["a", "b"])
        return self.__name

    @property
    def dates(self) -> str:
        if not self.__dates:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id="d"
            )
            if values:
                self.__dates = self._clean_value(values[0])
        return self.__dates

    @property
    def location(self) -> str:
        if not self.__location:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id="c"
            )
            if values:
                self.__location = self._clean_value(values[0])
        return self.__location

    @property
    def numeration(self) -> str:
        if not self.__numeration:
            values = self.get_values(
                marc_ids=self.__name_field_id,
                subfield_id="n"
            )
            if values:
                self.__numeration = self._clean_value(values[0])
        return self.__numeration

    @property
    def acronyms(self) -> List[str]:
        if not self.__acronyms:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id="a",
                subfield_restriction = ("w", "d")
            )
            self.__acronyms = [self._clean_value(value) for value in values]
        return self.__acronyms

    @property
    def new_names(self) -> List[str]:
        if not self.__new_names:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id=["a", "b"],
                subfield_restriction = ("w", "b")
            )
            self.__new_names = [self._merge_and_clean(value, ["a", "b"]) for value in values]
        return self.__new_names

    @property
    def old_names(self) -> List[str]:
        if not self.__old_names:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id=["a", "b"],
                subfield_restriction = ("w", "a")
            )
            self.__old_names = [self._merge_and_clean(value, ["a", "b"]) for value in values]
        return self.__old_names

    @property
    def alternative_names(self) -> List[str]:
        if not self.__alternative_names:
            values = self.get_values(
                marc_ids=self.__name_variations_field_id,
                subfield_id=["a", "b"],
                subfield_to_ignore="w"
            )
            self.__alternative_names = [self._merge_and_clean(value, ["a", "b"]) for value in values]
        return self.__alternative_names


    @property
    def related_acronyms(self) -> List[str]:
        if not self.__related_acronyms:
            values = self.get_values(
                marc_ids=self.__related_names_field_id,
                subfield_id="a",
                subfield_restriction = ("w", "d")
            )
            self.__related_acronyms = [self._clean_value(value) for value in values]
        return self.__related_acronyms

    @property
    def related_new_names(self) -> List[str]:
        if not self.__related_new_names:
            values = self.get_values(
                marc_ids=self.__related_names_field_id,
                subfield_id=["a", "b"],
                subfield_restriction = ("w", "b")
            )
            self.__related_new_names = [self._merge_and_clean(value, ["a", "b"]) for value in values]
        return self.__related_new_names

    @property
    def related_old_names(self) -> List[str]:
        if not self.__related_old_names:
            values = self.get_values(
                marc_ids=self.__related_names_field_id,
                subfield_id=["a", "b"],
                subfield_restriction = ("w", "a")
            )
            self.__related_old_names = [self._merge_and_clean(value, ["a", "b"]) for value in values]
        return self.__related_old_names


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
    def area_code(self) -> str:
        if not self.__area_code:
            values = self.get_values(
                marc_ids=self.__area_code_id,
                subfield_id="c"
            )
            self.__area_code = self._clean_value(values[0]) if values else ""
        return self.__area_code

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
    def variations(self) -> List[str]:
        if not self.__variations:
            _variations = [self.name]
            _variations.extend(self.new_names)
            _variations.extend(self.old_names)
            _variations.extend(self.alternative_names)
            _variations.extend(self.related_old_names)
            _variations.extend(self.related_new_names)
            self.__variations = [v.lower() for v in list(set(_variations))]

        return self.__variations

    @property
    def full_record(self) -> dict:
        if not self.__full_record:
            self.__full_record = {
                "name": self.name,
                "original_name": self.original_name,
                "acronyms": self.acronyms,
                "new_names": self.new_names,
                "old_names": self.old_names,
                "source": self.source,
                "description": self.description,
                "area_code": self.area_code,
                "alternative_names": self.alternative_names,
                "related_acryonyms": self.related_acronyms,
                "related_new_names": self.related_new_names,
                "related_old_names": self.related_old_names,
                "identifier": self.identifier,
                "identifier_source": self.identifier_source,
                "full_record_marc": str(self.marc_record),
                "full_record_json": json.dumps(self.marc_json_record)
            }
            if self.add_variations:
                self.__full_record.update(
                    {
                        "link_variations": self.variations,
                        "link_acronyms": [a.lower() for a in self.acronyms]
                    }
                )
        return self.__full_record

from typing import List, NoReturn, Tuple
from abc import abstractmethod
from pymarc.record import Record
from pymarc.marcjson import JSONHandler
from rara_tools.constants.parsers import GeneralMarcIDs


class BaseRecord:
    """ Implements general logic of parsing MARC files.
    """
    def __init__(self, record: Record | dict, add_variations: bool = False) -> NoReturn:
        """ Initializes BaseRecord object.

        Parameters
        -----------
        record: Record
            pymarc.record.Record objectself.
        add_variations: bool
            If enabled, constructs an additional variations field, which
            combines the content of multiple fields + adds some generated
            variations. If the output is uploaded into Elastic and used
            via rara-norm-linker, it is necessary to enable this.
        """
        self.add_variations: bool = add_variations
        self.__record_marc: Record = self._get_record_marc(record)
        self.__record_dict: dict = self.marc_record.as_dict()["fields"]

        self.__id_field_id: List[str] = GeneralMarcIDs.ID
        self.__id_source_field_id: List[str] = GeneralMarcIDs.ID_SOURCE

        self.__identifier: str = ""
        self.__identifier_source: str = ""

    def _get_record_marc(self, record: Record | dict) -> Record:
        """ Converts dict-type records into pymarc.Record objects.
        """
        if isinstance(record, dict):
            record = JSONHandler().elements([record])[0]
        return record

    def get_values(self,
            marc_ids: List[str],
            subfield_id: str | List[str] = "",
            ind1: str = " ",
            ind2: str = " ",
            subfield_restriction: Tuple[str, str] = (),
            subfield_to_ignore: str | None = None
        ) -> List[str] | List[dict]:
        values = []

        for field in self.dict_record:
            field_id = list(field.keys())[0]
            if field_id in marc_ids:
                # TODO: ind1!
                if not subfield_id:
                    values.append(field[field_id])
                else:
                    if field[field_id]["ind2"] == ind2:
                        subfields = field[field_id]["subfields"]
                        subfield_tuples = [list(subfield.items())[0] for subfield in subfields]
                        subfield_keys = [list(subfield.keys())[0] for subfield in subfields]
                        if subfield_restriction and subfield_restriction not in subfield_tuples:
                            continue
                        if subfield_to_ignore and subfield_to_ignore in subfield_keys:
                            continue
                        _value = {}
                        for subfield in subfields:
                            _subfield_id = list(subfield.keys())[0]
                            if isinstance(subfield_id, str):
                                if _subfield_id == subfield_id:
                                    value = subfield[_subfield_id]
                                    values.append(value.strip())
                            elif isinstance(subfield_id, list):
                                if _subfield_id in subfield_id:
                                    value = subfield[_subfield_id]
                                    _value[_subfield_id] = value
                        if isinstance(subfield_id, list):
                            values.append(_value)

        return values

    def _clean_value(self, value: str) -> str:
        cleaned_value = value.strip("., ")
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
    def identifier(self) -> str:
        if not self.__identifier:
            values = self.get_values(marc_ids=self.__id_field_id)
            self.__identifier = values[0] if values else ""
        return self.__identifier

    @property
    def identifier_source(self) -> str:
        if not self.__identifier_source:
            values = self.get_values(marc_ids=self.__id_source_field_id)
            self.__identifier_source = values[0] if values else ""
        return self.__identifier_source

    @property
    def marc_record(self) -> Record:
        return self.__record_marc

    @property
    def marc_json_record(self) -> dict:
        return self.marc_record.as_dict()

    @property
    def dict_record(self) -> Record:
        return self.__record_dict

from rara_tools.constants.linker  import (
    LOGGER, EntityType
)
from rara_tools.core_formatters.formatted_object import FormattedObject
from typing import List, Dict, NoReturn, Tuple, Any


class FormattedTitle(FormattedObject):
    # TODO: Kas seda on üldse vaja?
    def __init__(self, object_dict: dict, linked_doc: Any):
        super().__init__(
            object_dict=object_dict,
            linked_doc=linked_doc,
            original_entity_key="title"
        )


class FormattedAuthor(FormattedObject):
    def __init__(self, object_dict: dict, linked_doc: Any, entity_type: str):
        super().__init__(
            object_dict=object_dict,
            linked_doc=linked_doc,
            original_entity_key="name"
        )
        self.entity_type: str = entity_type

        self.is_linked: bool = True if self.linked_doc else False # NB! Lisada andmebaasi uus veerg!
        self.original_name: str = self.original_entity            # NB! Lisada andmebaasi uus veerg
        self.author_role: str = self.object_dict.get("role")
        self.is_primary: bool = self.object_dict.get("is_primary")

        self.__primary_author_type: str = None

        self.__name_order_type: str = ""
        self.__event_sub_unit: str = ""
        self.__order_number: str = ""
        self.__sub_title: str = ""
        self.__additional_info: str = ""
        self.__publication_type: str = ""
        self.__publication_language: str = ""
        #self.__standardized_uri: str = ""
        self.__viaf_id: str = ""

        self._default_author_type: str = EntityType.PER


    @property
    def primary_author_type(self) -> str:
        if self.__primary_author_type == None:
            self.__primary_author_type = self._default_author_type
            if self.entity_type != EntityType.UNK:
                if self.entity_type in [EntityType.ORG, EntityType.PER]:
                    self.__primary_author_type = self.entity_type
        return self.__primary_author_type


    @property
    def name(self) -> str:
        return self.entity

    @property
    def name_order(self) -> str:
        if not self.__name_order_type:
            if self.entity_type == EntityType.PER or self.entity_type == EntityType.UNK:
                if "," in self.name:
                    ind1 = "1"
                else:
                    ind1 = "0"
            elif self.entity_type == EntityType.ORG:
                #LOGGER.debug(f"Entity type {self.entity_type} is not {EntityType.PER}.")
                # 1 märksõna esimeseks elemendiks võimupiirkonna nimi, nt:
                #    (a) Eesti (b) Riigikogu - raske automaatselt määrata
                # 2 märksõna esimeseks elemendiks nimi pärijärjestuses
                ind1 = "2" #????????
            else:
                ind1 = "0"
            self.__name_order_type = ind1
        return self.__name_order_type

    @property
    def event_sub_unit(self) -> str:
        if not self.__event_sub_unit:
            self.__event_sub_unit = ""
        return self.__event_sub_unit


    @property
    def order_number(self) -> str:
        if not self.__order_number:
            self.__order_number = ""
        return self.__order_number

    @property
    def sub_title(self) -> str:
        if not self.__sub_title:
            self.__sub_title = ""
        return self.__sub_title

    @property
    def additional_info(self) -> str:
        if not self.__additional_info:
            self.__additional_info = ""
        return self.__additional_info

    @property
    def publication_type(self) -> str:
        if not self.__publication_type:
            self.__publication_type = ""
        return self.__publication_type

    @property
    def publication_language(self) -> str:
        if not self.__publication_language:
            self.__publication_language = ""
        return self.__publication_language

    @property
    def standardized_uri(self) -> str:
        return self.identifier

    @property
    def viaf_id(self):
        if not self.__viaf_id:
            if self.viaf_info:
                self.__viaf_id = self.viaf_info.get("viaf_url", "")
            else:
                self.__viaf_id = ""
        return self.__viaf_id

    def to_dict(self):
        author_dict = {
            "is_linked": self.is_linked,
            "original_name": self.original_name,
            "author_role": self.author_role,
            "is_primary": self.is_primary,
            "primary_author_type": self.primary_author_type,
            "name": self.name,
            "numeration": self.numeration,
            "organisation_sub_unit": self.organisation_sub_unit,
            "titles": self.titles,
            "location": self.location,
            "dates": self.dates,
            "name_order_type": self.name_order,
            "event_sub_unit": self.event_sub_unit,
            "order_number": self.order_number,
            "sub_title": self.sub_title,
            "additional_info": self.additional_info,
            "publication_type": self.publication_type,
            "publication_language": self.publication_language,
            "standardized_uri": self.standardized_uri,
            "viaf_id": self.viaf_id
        }
        return author_dict

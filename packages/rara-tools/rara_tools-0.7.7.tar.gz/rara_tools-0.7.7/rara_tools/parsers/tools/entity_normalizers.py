import regex as re
import estnltk
import nltk
import logging
from rara_tools.parsers.tools.russian_transliterator import Transliterate
from rara_tools.constants.parsers import KeywordType, LOGGER
from typing import List, NoReturn
from abc import abstractmethod


nltk.download("punkt_tab")


class PersonalName:
    """ Wraps generating and accessing main name forms.
    """
    def __init__(self, name: str) -> NoReturn:
        """ Initializes PersonName object.

        Parameters
        -----------
        name: str
            Personal name. Expects one of the following formats:
            '<first name> <last name>' or '<last name>, <first_name>', e.g:
            'Uku Tamm' or 'Tamm, Uku'.
        """
        self.__original_name: str = name
        self.__name: dict = {}
        self.__last_comma_first: str = ""
        self.__first_last: str = ""

    @property
    def first_name(self) -> str:
        return self.name.get("first_name")

    @property
    def last_name(self) -> str:
        return self.name.get("last_name")

    @property
    def name(self) -> dict:
        if not self.__name:
            last_name = ""
            first_name = ""
            if "," in self.__original_name:
                try:
                    last_name, first_name = self.__original_name.split(",")
                except Exception as e:
                    LOGGER.warning(
                        f"Parsing personal name '{self.__original_name}' " \
                        f"failed with error: {e}. Keeping unformatted version."
                    )
            else:
                name_tokens = [
                    t.strip()
                    for t in self.__original_name.split()
                    if t.strip()
                ]
                if len(name_tokens) > 1:
                    last_name = name_tokens[-1]
                    first_name = " ".join(name_tokens[:-1])
            self.__name = {
                "first_name": first_name.strip(),
                "last_name": last_name.strip()
            }
        return self.__name

    @property
    def last_comma_first(self) -> str:
        if not self.__last_comma_first:
            if self.last_name or self.first_name:
                self.__last_comma_first = f"{self.last_name}, {self.first_name}"
            else: self.__last_comma_first = self.__original_name
        return self.__last_comma_first.strip()

    @property
    def first_last(self) -> str:
        if not self.__first_last:
            if self.first_name or self.last_name:
                self.__first_last = f"{self.first_name} {self.last_name}"
            else:
                self.__first_last = self.__original_name
        return self.__first_last.strip()


class Normalizer:
    """ Class for handling general methods for string
    normalizations and variations generation.
    """
    def __init__(self, entity: str) -> NoReturn:
        """ Initializes Normalizer object.

        Parameters
        -----------
        entity: str
            Entity (keyword, person etc) to normalize.
        """
        self.__entity: str = entity
        self.__lemmatized_entity: str = ""
        self.__cleaned_entity: str = ""


    @staticmethod
    def has_cyrillic(entity: str) -> bool:
        return bool(re.search("[а-яА-Я]", entity))

    @staticmethod
    def transliterate(entity: str) -> str:
        transliterator = Transliterate()
        transliteration = transliterator([entity])[0]
        return transliteration

    @staticmethod
    def lemmatize(entity: str) -> str:
        layer = estnltk.Text(entity).tag_layer()
        lemma_list = [l[0] for l in list(layer.lemma)]
        lemmatized_entity = " ".join(lemma_list)
        return lemmatized_entity

    @staticmethod
    def remove_parenthesized_info(entity: str) -> str:
        clean_entity = re.sub(r"[(][^)]+[)]", "", entity)
        return clean_entity.strip()

    @staticmethod
    def clean_entity(entity: str) -> str:
        clean_entity = Normalizer.remove_parenthesized_info(entity)
        return clean_entity

    @property
    def lemmatized_entity(self) -> str:
        if not self.__lemmatized_entity:
            self.__lemmatized_entity = Normalizer.lemmatize(self.__entity)
        return self.__lemmatized_entity

    @property
    def cleaned_entity(self) -> str:
        if not self.__cleaned_entity:
            self.__cleaned_entity = Normalizer.clean_entity(self.__entity)
        return self.__cleaned_entity

    @abstractmethod
    def variations(self) -> List[str]:
        pass


class PersonNormalizer(Normalizer):
    """ Class for handling person-specific methods for string
    normalizations and variations generation.
    """
    def __init__(self, name: str) -> NoReturn:
        """ Initializes PersonNormalizer object.

        Parameters
        -----------
        name: str
            Personal name to normalize / generate variations for.
        """
        super().__init__(entity=name)
        self.__name: str = name
        self.__name_object: PersonalName = PersonalName(name)
        self.__variations: List[str] = []


    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            LOGGER.debug(f"Generating variations for name {self.__name}.")
            variations = []
            variations.append(self.__name_object.last_comma_first)
            variations.append(self.__name_object.first_last)

            if Normalizer.has_cyrillic(self.__name):
                LOGGER.debug(
                    f"Detected cyrillic in the original name '{self.__name}'. " \
                    f"Generating a transliterated latin version."
                )
                transliterations = [
                    Normalizer.transliterate(name)
                    for name in variations
                ]
                variations.extend(transliterations)

            # Guarantee adding one-word names as well
            if self.__name not in variations:
                variations.append(self.__name)
            _variations = [v.strip() for v in variations if v.strip()]
            self.__variations = list(set(_variations))
            LOGGER.debug(
                f"Generated the following variations for name '{self.__name}': " \
                f"{self.__variations}."
            )
        return self.__variations



class KeywordNormalizer(Normalizer):
    """ Class for handling keyword-specific methods for string
    normalizations and variations generation.
    """
    def __init__(self, keyword: str, keyword_type: str = "") -> NoReturn:
        """ Initializes KeywordNormalizer object.

        Parameters
        -----------
        keyword: str
            keyword to normalize / generate variations for.
        keyword_type: str
            Keyword type. Should be one of the types specified in
            rara_tools.constants.parsers.KeywordType or "".

        """
        super().__init__(entity=keyword)
        self.__keyword: str = keyword
        self.__variations: List[str] = []
        self.__keyword_type: str = keyword_type
        self.__loc_substitutions_map: dict = {"v": "w", "V": "W"}

    def _transform_v_into_w(self, entity: str) -> str:
        for old_val, new_val in list(self.__loc_substitutions_map.items()):
            entity = re.sub(old_val, new_val, entity)
        return entity

    @property
    def loc_substitutions_as_str(self) -> str:
        subs = [
            f"'{old_val}' -> '{new_val}'"
            for old_val, new_val in list(self.__loc_substitutions_map.items())
        ]
        return ", ".join(subs)

    @property
    def variations(self) -> List[str]:
        if not self.__variations:
            LOGGER.debug(f"Generating variations for keyword {self.__keyword}.")
            variations = []
            variations.append(self.__keyword)
            variations.append(self.lemmatized_entity)
            variations.append(self.cleaned_entity)
            variations.append(Normalizer.lemmatize(self.cleaned_entity))
            # If keyword_type = LOC, add variations containing
            # v -> w replacements
            if self.__keyword_type == KeywordType.LOC:
                LOGGER.debug(
                    f"Detected keyword type = '{KeywordType.LOC}' -> " \
                    f"Adding variations with the following character " \
                    f"replacements: {self.loc_substitutions_as_str}."
                )
                v_w_transformations = [
                    self._transform_v_into_w(entity)
                    for entity in variations
                ]
                variations.extend(v_w_transformations)
            variations = list(set(variations))
            self.__variations = variations
            LOGGER.debug(
                f"Generated the following variations for keyword '{self.__keyword}': " \
                f"{self.__variations}."
            )
        return self.__variations

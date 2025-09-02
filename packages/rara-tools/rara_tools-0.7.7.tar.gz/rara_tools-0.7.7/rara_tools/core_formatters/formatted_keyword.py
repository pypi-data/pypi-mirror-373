from rara_tools.constants.linker import (
    LOGGER, URLSource, KeywordSource, EntityType, KeywordType, KeywordMARC,
    KEYWORD_MARC_MAP,  KEYWORD_TYPES_TO_IGNORE, KEYWORD_TYPE_MAP,
    EMS_ENTITY_TYPES, SIERRA_ENTITY_TYPES, UNLINKED_KEYWORD_MARC_FIELD,
    URL_SOURCE_MAP
)
from rara_tools.core_formatters.formatted_object import FormattedObject
from typing import List, Dict, NoReturn, Tuple, Any

class FormattedKeyword(FormattedObject):
    def __init__(self, object_dict: dict, linked_doc: Any,
            main_taxnomy_lang: str, url_source_map: str = URL_SOURCE_MAP
    ) -> NoReturn:
        super().__init__(
            object_dict=object_dict,
            linked_doc=linked_doc,
            original_entity_key="keyword"
        )

        self.main_taxnomy_lang: str = main_taxnomy_lang

        self.original_keyword: str = self.original_entity
        self.score: float = self.object_dict.get("score")
        self.count: int = self.object_dict.get("count")
        self.method: str = self.object_dict.get("method")
        self.model_arch: str = self.object_dict.get("model_arch", self.method)
        self.keyword_type: str = self.object_dict.get("entity_type")
        self.article_id: str | None = self.object_dict.get("article_id", None)

        self.entity_type: str = KEYWORD_TYPE_MAP.get(self.keyword_type, "")
        self.url_source_map: dict = url_source_map

        self.__keyword_source: str = ""
        self.__indicator_1: str = ""
        self.__indicator_2: str = ""
        self.__url: str | None = None
        self.__url_source: str | None = None
        self.__marc_field: str = ""

        self.__language: str = ""
        self.__author: str | None = None


    @property
    def keyword(self) -> str:
        return self.entity

    @property
    def keyword_source(self) -> str:
        if not self.__keyword_source:
            if not self.is_linked:
                source = KeywordSource.AI
            elif self.entity_type in EMS_ENTITY_TYPES:
                source = KeywordSource.EMS
            elif self.entity_type in SIERRA_ENTITY_TYPES:
                if self.linked_doc and self.linked_doc.elastic:
                    source = KeywordSource.SIERRA
                elif self.linked_doc and self.linked_doc.viaf:
                    source = KeywordSource.VIAF
                else:
                    source = KeywordSource.AI
            else:
                source = KeywordSource.AI
            self.__keyword_source = source
        return self.__keyword_source

    @property
    def indicator1(self) -> str:
        if not self.__indicator_1:
            ind1, ind2 = self._get_indicators()
            self.__indicator_1 = ind1
            self.__indicator_2 = ind2
        return self.__indicator_1

    @property
    def indicator2(self) -> str:
        if not self.__indicator_2:
            ind1, ind2 = self._get_indicators()
            self.__indicator_1 = ind1
            self.__indicator_2 = ind2
        return self.__indicator_2

    @property
    def url(self) -> str:
        if self.__url == None:
            url_info = self._get_url_info()
            self.__url = url_info.get("url")
            self.__url_source = url_info.get("url_source")
        return self.__url

    @property
    def url_source(self) -> str:
        if self.__url_source == None:
            url_info = self._get_url_info()
            self.__url = url_info.get("url")
            self.__url_source = url_info.get("url_source")
        return self.__url_source

    @property
    def marc_field(self) -> int:
        if not self.__marc_field:
            # TODO: teoste + isikute loogika!!!!
            if self.is_linked:
                marc_field = KEYWORD_MARC_MAP.get(str(self.keyword_type), "")
            else:
                marc_field = UNLINKED_KEYWORD_MARC_FIELD

            if self.entity_type == EntityType.TITLE:
                if self.author:
                    marc_field = KeywordMARC.TITLE_LINKED
                else:
                    marc_field = KeywordMARC.TITLE
            self.__marc_field = marc_field
        return self.__marc_field


    @property
    def persons_title(self) -> str:
        return self.titles


    @property
    def language(self) -> str:
        if not self.__language:
            if self.is_linked:
                self.__language = self.main_taxnomy_lang
            else:
                self.__language = self.object_dict.get("language", "")
        return self.__language

    @property
    def author(self) -> str:
        # Only relevant for titles!
        if self.__author == None:
            self.__author = ""
            if self.entity_type == EntityType.TITLE:
                if self.original_record:
                    self.__author = self.original_record.author_name
                elif self.viaf_info:
                    pass
                    #self.__author = self.viaf_info.get
        return self.__author



    def _get_url_info(self) -> dict:
        """ Finds URL identifier from LinkedDoc based on
        given entity type.

        Parameters
        -----------
        linked_doc: LinkedDoc | None
            A LinkedDoc class instance.
        entity_type: str
            Entity type for detecting correct URL source.

        Returns
        ----------
        dict:
            Dictionary with keys `url` - URL identifier and
            `url_source` - source of the URL (e.g. "EMS").

        """
        url_source = self.url_source_map.get(self.entity_type, "")
        url = ""

        if self.linked_doc:
            if url_source == URLSource.EMS:
                url = self.linked_doc.elastic.get("ems_url", "")
            elif url_source == URLSource.VIAF:
                url = self.viaf_info.get("viaf_url", "")
        if not url:
            url_source = ""

        url_info = {"url": url, "url_source": url_source}

        LOGGER.debug(
            f"Detected URL info: {url_info}. Used entity_type = {self.entity_type}. " \
            f"URL source map = {self.url_source_map}."
        )
        return url_info

    def _get_indicators(self) -> Tuple[str, str]:
        """ Find MARC indicators 1 and 2.
        """
        ind1 = " "
        ind2 = " "
        if self.entity_type in SIERRA_ENTITY_TYPES:
            if self.entity_type == EntityType.PER:
                if "," in self.keyword:
                    ind1 = "1"
                else:
                    ind1 = "0"
            elif self.entity_type == EntityType.ORG:
                # 1 märksõna esimeseks elemendiks võimupiirkonna nimi, nt:
                #    (a) Eesti (b) Riigikogu - raske automaatselt määrata
                # 2 märksõna esimeseks elemendiks nimi pärijärjestuses
                ind1 = "2"
            else:
                ind1 = "0"

            if not self.is_linked:
                ind2 = "4"
        elif self.entity_type in EMS_ENTITY_TYPES:
            ind2 = "4"
        return (ind1, ind2)


    def to_dict(self) -> dict:
        keyword_dict = {
            "count": self.count,
            "dates": self.dates,
            "entity_type": self.keyword_type,
            "indicator1": self.indicator1,
            "indicator2": self.indicator2,
            "is_linked": self.is_linked,
            "keyword": self.keyword,
            "keyword_source": self.keyword_source,
            "lang": self.language,
            "location": self.location,
            "marc_field": self.marc_field,
            "method": self.method,
            "model_arch": self.model_arch,
            "numeration": self.numeration,
            "organisation_sub_unit": self.organisation_sub_unit,
            "original_keyword": self.original_keyword,
            "persons_title": self.persons_title,
            "score": self.score,
            "url": self.url,
            "url_source": self.url_source,
            "author": self.author,
            "article_id": self.article_id
        }
        return keyword_dict

from typing import List, Tuple, Any
from rara_tools.core_formatters.formatted_keyword import FormattedKeyword
from rara_tools.core_formatters.formatted_meta import FormattedAuthor
from rara_tools.constants.linker import MAIN_TAXONOMY_LANG, KEYWORD_TYPES_TO_IGNORE, EntityType
from rara_tools.constants.meta_extractor import TitleType, TITLE_TYPES_MAP, PUBLISHER_KEY
from rara_tools.constants.subject_indexer import KeywordType

import regex as re

def get_primary_author(authors: List[dict]) -> str:
    primary_author = ""
    for author in authors:
        if author.get("is_primary", False):
            primary_author = author.get("name", "")
    return primary_author

def is_valid_keyword(keyword: str) -> bool:
    # If keywords contains ONLY punctuation
    # characters, we assume it`s not valid
    if re.search(r"^(\W|_)+$", keyword):
        return False
    return True

def format_series_info(series: str):
    pass

def format_authors(authors: List[dict]) -> Tuple[List[dict], dict]:
    formatted_authors = []
    publisher = {}
    for author in authors:
        entity_type = author.get("type", EntityType.UNK)

        formatted_author = FormattedAuthor(
            object_dict=author,
            linked_doc=None,
            entity_type=entity_type
        ).to_dict()

        # If author role == publisher, do not add it as an author
        if formatted_author.get("author_role", "") == PUBLISHER_KEY:
            publisher = formatted_author
            continue

        formatted_authors.append(formatted_author)
    return (formatted_authors, publisher)

def format_sections(sections: List[dict]) -> List[dict]:
    for section in sections:
        authors = section.pop("authors", [])
        titles = section.pop("titles", [])
        primary_author = get_primary_author(authors)
        if primary_author:
            for title in titles:
                title["author_from_title"] = primary_author
        if not authors:
            for title in titles:
                title["title_type"] = TitleType.ANON
                title["title_type_int"] = TITLE_TYPES_MAP.get(TitleType.ANON)
        section["titles"] = titles

        # Extract publisher, but do nothing with it
        # as it is unlikely for the publishing info to be
        # in a METS/ALTO section. Can update it, if proven otherwise
        formatted_authors, publisher = format_authors(authors)
        section["authors"] = formatted_authors

    return sections

def format_meta(meta: dict) -> dict:
    """ Formats unlinked meta for Kata CORE.
    """

    meta_to_format = meta.get("meta")

    authors = meta_to_format.pop("authors", [])
    sections = meta_to_format.pop("sections", [])
    titles = meta_to_format.pop("titles", [])

    formatted_authors, publisher = format_authors(authors)
    formatted_sections = format_sections(sections)

    if sections and formatted_sections:
        meta_to_format["sections"] = formatted_sections
    if authors and formatted_authors:
        meta_to_format["authors"] = formatted_authors
    if titles and not authors:
        for title in titles:
            title["title_type"] = TitleType.ANON
            title["title_type_int"] = TITLE_TYPES_MAP.get(TitleType.ANON)
        meta_to_format["titles"] = titles

    if publisher:
        # Not sure, if it would be better to add original name or
        # linked value. Currently adding original for safety
        meta_to_format["publisher"] = publisher.get("original_name")

    meta["meta"] = meta_to_format

    return meta


def format_keywords(flat_keywords: List[dict]) -> List[dict]:
    """ Formats unlinked keywords for Kata CORE.
    """
    ignored_keywords = []
    filtered_keywords = []

    for keyword_dict in flat_keywords:
        keyword_type = keyword_dict.get("entity_type")
        if keyword_type in KEYWORD_TYPES_TO_IGNORE:
            ignored_keywords.append(keyword_dict)
        else:
            filtered_keywords.append(keyword_dict)

    formatted_keywords = []

    for keyword_dict in filtered_keywords:
        formatted_keyword = FormattedKeyword(
            object_dict=keyword_dict,
            linked_doc=None,
            main_taxnomy_lang=MAIN_TAXONOMY_LANG
        ).to_dict()
        if is_valid_keyword(formatted_keyword.get("keyword")):
            formatted_keywords.append(formatted_keyword)

    return formatted_keywords

def get_udk072(flat_keywords: List[dict]) -> List[str]:
    """ Filters out UDK from flat subject indexer output.
    """
    # keyword type: UDK
    udk072 = [
        keyword.get("keyword")
        for keyword in flat_keywords
        if keyword.get("entity_type") == KeywordType.UDK
    ]
    return udk072


def get_udk080(flat_keywords: List[dict]) -> List[str]:
    """ Filters out UDC from flat subject indexer output.
    """
    # keyword type: UDC
    udk080 = [
        keyword.get("keyword")
        for keyword in flat_keywords
        if keyword.get("entity_type") == KeywordType.UDC
    ]
    return udk080

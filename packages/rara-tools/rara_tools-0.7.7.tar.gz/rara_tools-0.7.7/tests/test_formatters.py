import pytest
import os
from pprint import pprint
from rara_tools.core_formatters.core_formatter import format_keywords, format_meta, get_udk072, get_udk080
from rara_tools.constants.meta_extractor import PUBLISHER_KEY
from tests.test_utils import read_json_file

ROOT_DIR = os.path.join("tests", "test_data", "formatter")
INPUT_KEYWORDS_FILE_PATHS = [
    os.path.join(ROOT_DIR, "keywords_1.json"),
    os.path.join(ROOT_DIR, "keywords_2.json"),
    os.path.join(ROOT_DIR, "keywords_3.json")
]
INPUT_META_FILE_PATHS = [
    os.path.join(ROOT_DIR, "epub_meta.json"),
    os.path.join(ROOT_DIR, "mets_alto_meta.json"),
    os.path.join(ROOT_DIR, "pdf_meta_2.json"),
    os.path.join(ROOT_DIR, "pdf_meta.json")
]

INPUT_KEYWORDS = [
    read_json_file(keyword_file_path)
    for keyword_file_path in INPUT_KEYWORDS_FILE_PATHS
]

INPUT_META_DICTS = [
    read_json_file(meta_file_path)
    for meta_file_path in INPUT_META_FILE_PATHS
]

def test_formatting_keywords_for_core():
    for keyword_dict_list in INPUT_KEYWORDS:
        formatted_keywords = format_keywords(keyword_dict_list)
        #pprint(formatted_keywords)
        assert formatted_keywords
        assert isinstance(formatted_keywords, list)


def test_formatting_meta_for_core():
    for meta_dict in INPUT_META_DICTS:
        formatted_meta = format_meta(meta_dict)
        #pprint(formatted_meta)
        assert formatted_meta
        assert isinstance(formatted_meta, dict)


def test_validating_keywords():
    keyword_dict_list = INPUT_KEYWORDS[-1]
    assert len(keyword_dict_list) == 6
    formatted_keywords = format_keywords(keyword_dict_list)
    assert len(formatted_keywords) == 2

def test_removing_publisher_from_authors():
    meta_dict = INPUT_META_DICTS[-1]
    formatted_meta = format_meta(meta_dict)
    assert formatted_meta["meta"]["publisher"] == "s.n"
    for author in formatted_meta["meta"]["authors"]:
        assert author.get("author_role") != PUBLISHER_KEY
    assert isinstance(formatted_meta, dict)

def test_title_key_without_authors():
    meta_dict = INPUT_META_DICTS[2]
    formatted_meta = format_meta(meta_dict)
    for title in formatted_meta["meta"]["titles"]:
        assert title.get("title_type_int") == 130
    assert isinstance(formatted_meta, dict)

def test_all_authors_have_types():
    for meta_dict in INPUT_META_DICTS:
        formatted_meta = format_meta(meta_dict)
        authors = formatted_meta.get("authors", [])
        for author in authors:
            assert author.get("primary_author_type")

def test_getting_udk072():
    keyword_dict_list = INPUT_KEYWORDS[-1]
    assert len(keyword_dict_list) == 6
    udk072_list = get_udk072(keyword_dict_list)
    assert len(udk072_list) == 1

def test_getting_udk080():
    keyword_dict_list = INPUT_KEYWORDS[-1]
    assert len(keyword_dict_list) == 6
    udk080_list = get_udk080(keyword_dict_list)
    assert len(udk080_list) == 1

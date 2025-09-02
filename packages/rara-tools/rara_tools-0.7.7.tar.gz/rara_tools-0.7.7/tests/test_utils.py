from tests.const import SIERRA_INPUT_DIR, LINKER_DIR

from rara_tools.converters import SierraResponseConverter
from rara_tools.normalizers.viaf import VIAFRecord, VIAFClient

from pymarc import Record
from typing import List

import json
import os


def read_json_file(path: str):
    with open(path, "r") as f:
        data = f.read()
        return json.loads(data)


def check_record_tags_sorted(record: Record):
    record_tags = [field.tag for field in record.get_fields()]
    assert record_tags == sorted(record_tags)


def check_no_dupe_tag_values(record: Record):
    repetable_tags = ["024", "035", "400", "670"]
    record_tags = [field.tag for field in record.get_fields()
                   if field.tag not in repetable_tags]
    assert len(record_tags) == len(set(record_tags))


def check_record_tags_have_values(record: Record, tags: List[str]):
    for tag in tags:
        assert record[tag] is not None


def get_record_field_value(record: Record, tag: str):
    """ handle control & variable fields """
    return record.get_fields(tag)[0].value()


def compare_results(expected: dict, results: dict):
    return json.dumps(expected) == json.dumps(results)


def get_formatted_sierra_response(fname: str):
    """ Reads a mock Sierra response file and converts it to MARC in json."""

    response = read_json_file(os.path.join(SIERRA_INPUT_DIR, fname))

    converter = SierraResponseConverter(response)
    return converter.convert()


def get_viaf_record(id: str, allowed_sources: list):
    """ Fetches VIAF record by ID and returns a VIAFRecord object """

    client = VIAFClient()
    response = client.get_records_by_viaf_id(id)

    viaf_record = VIAFRecord(
        response, allowed_sources=allowed_sources)
    return viaf_record


def search_viaf_record(search_term: str, allowed_sources: list):
    """ Fetches VIAF record by name and returns a VIAFRecord object """
    client = VIAFClient()
    response = client.get_records_by_search_term(search_term)

    return VIAFRecord(response, allowed_sources=allowed_sources)


def get_linker_res_example(fname: str):
    with open(os.path.join(LINKER_DIR, fname), "r") as f:
        data = f.read()
        return json.loads(data)

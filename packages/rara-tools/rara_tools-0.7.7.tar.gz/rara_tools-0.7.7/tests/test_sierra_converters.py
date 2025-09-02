import os

import pytest
from rara_tools.converters import SierraResponseConverter
from rara_tools.exceptions import SierraResponseConverterException

from tests.const import SIERRA_OUTPUT_DIR
from tests.test_utils import (read_json_file, get_formatted_sierra_response, compare_results)


example_res = {
    "total": 100,
    "start": 50000,
    "entries": [
        {
            "id": 1126963,
            "updatedDate": "2016-02-09T08:42:52Z",
            "createdDate": "2014-05-17T17:22:00Z",
            "deleted": False,
            "suppressed": False,
            "marc": {
                "leader": "00000nz  a2200145n  4500",
                "fields": [
                    {
                        # "tag": "100",
                        "data": {
                            "ind1": "1",
                                    "ind2": " ",
                                    "subfields": [
                                        {
                                            "code": "a",
                                            "data": "Viggor, Signe,"
                                        },
                                        {
                                            "code": "d",
                                            "data": "1975-"
                                        }
                                    ]
                        }
                    },
                ]}}]}


def test_convert_bibs_response():

    data = get_formatted_sierra_response("bibs.json")
    
    expected = read_json_file(os.path.join(SIERRA_OUTPUT_DIR, "bibs.json"))

    assert compare_results(expected, data)


def test_convert_authorities_response():

    data = get_formatted_sierra_response("authorities.json")
    
    expected = read_json_file(os.path.join(
        SIERRA_OUTPUT_DIR, "authorities.json"))

    assert compare_results(expected, data)


def test_converter_handles_marc_in_json_response():
    """ Gracefully handle entries already in MARC-in-JSON format """
    data = get_formatted_sierra_response("bibsmarc.json")

    expected = read_json_file(os.path.join(SIERRA_OUTPUT_DIR, "bibsmarc.json"))

    assert compare_results(expected, data)


def test_convert_with_wrong_format():
    with pytest.raises(SierraResponseConverterException):
        SierraResponseConverter("$")


def test_convert_missing_tag():
    with pytest.raises(SierraResponseConverterException):
        response = example_res.copy()
        response["entries"][0]["marc"]["fields"][0].pop("tag", None)

        converter = SierraResponseConverter(response)
        converter.convert()


def test_no_entries_in_response():
    with pytest.raises(SierraResponseConverterException):
        response = example_res.copy()
        response.pop("entries", [])

        converter = SierraResponseConverter(response)
        converter.convert()

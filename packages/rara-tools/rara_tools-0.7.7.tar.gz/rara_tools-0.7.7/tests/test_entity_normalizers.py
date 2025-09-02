import pytest
from collections import Counter
from rara_tools.constants.parsers import KeywordType
from rara_tools.parsers.tools.entity_normalizers import PersonNormalizer, KeywordNormalizer


def test_generating_person_variations():
    pn_1 = PersonNormalizer(name="Карл Ристикиви")
    var_1 = pn_1.variations

    pn_2 = PersonNormalizer(name="Ристикиви, Карл")
    var_2 = pn_2.variations

    expected_output = [
        "Karl Ristikivi",
        "Карл Ристикиви",
        "Ристикиви, Карл",
        "Ristikivi, Karl"
    ]
    assert Counter(var_1) == Counter(expected_output)
    assert Counter(var_2) == Counter(expected_output)


def test_generating_keyword_variations():
    kn_1 = KeywordNormalizer(keyword="agendad (religioon)")
    var_1 = kn_1.variations

    expected_output = [
        "agendad (religioon)",
        "agenda",
        "agendad",
        "agenda ( religioon )"
    ]
    assert Counter(var_1) == Counter(expected_output)


def test_generating_loc_keyword_variations():
    # If keyword type != LOC, variations with v -> w
    # replacements should NOT be generated
    kn_1 = KeywordNormalizer(
        keyword="Võrumaal",
        keyword_type=KeywordType.TOPIC
    )
    var_1 = kn_1.variations
    expected_output_1 = [
        "Võrumaal",
        "Võrumaa"
    ]
    assert Counter(var_1) == Counter(expected_output_1)

    # If keyword type == LOC, variations with v -> w
    # replacements should be generated
    kn_2 = KeywordNormalizer(
        keyword="Võrumaal",
        keyword_type=KeywordType.LOC
    )
    var_2 = kn_2.variations
    expected_output_2 = [
        "Võrumaal",
        "Võrumaa",
        "Wõrumaa",
        "Wõrumaal"
    ]
    assert Counter(var_2) == Counter(expected_output_2)

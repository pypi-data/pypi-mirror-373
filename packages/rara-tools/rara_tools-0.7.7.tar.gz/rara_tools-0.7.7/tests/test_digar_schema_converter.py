import json
import pytest
import os
import sys

from rara_tools.digar_schema_converter import DIGARSchemaConverter

def load_json(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


TEST_DIGITIZER_OUTPUT_FILE = os.path.join(".", "tests", "test_data", "b1267058_test_digitizer_output.json")
TEST_DIGITIZER_OUTPUT = load_json(TEST_DIGITIZER_OUTPUT_FILE)
TEST_SIERRA_ID = "b1267058"
TEST_GENERATED_ID = "hsasaHSAHHGDhb"
TEST_PERMALINK = "https://www.digar.ee/b1267058"

def test_digar_schema_converstion_default():
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID
    )
    digar_schema = converter.digar_schema
    
    # check that all neseccary fields are present
    assert "dc:language" in digar_schema
    assert "dcterms:provenance" in digar_schema
    assert "dc:identifier" in digar_schema
    assert "dcterms:hasPart" in digar_schema
    assert "dcterms:conformsTo" in digar_schema
    
    languages = [lang.get("value") for lang in digar_schema.get("dc:language")]
    # check that languages are converted into ISO-693-2
    for lang in languages:
        assert len(lang) == 3
        
        
    # check that ratio is converted into percentage
    text_quality = digar_schema.get("dcterms:conformsTo")[0].get("value")
    assert isinstance(text_quality, str)
    
    
def test_digar_schema_id_generation():
    """ Tests ID generation logic.
    """
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID,
        permalink=TEST_PERMALINK
        
    )
    
    #If permalink is given, this should be used as base ID
    digar_schema = converter.digar_schema
    first_segment_id = digar_schema["dcterms:hasPart"][0]["hasPart"][0]["@id"]
    
    assert first_segment_id.startswith(TEST_PERMALINK)
  
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID
    )
    
    #If permalink is NOT given, Sierra ID should be used as base ID
    digar_schema = converter.digar_schema
    first_segment_id = digar_schema["dcterms:hasPart"][0]["hasPart"][0]["@id"]
    assert first_segment_id.startswith(TEST_SIERRA_ID)
    
    
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        generated_id=TEST_GENERATED_ID
    )
    
    #If neiter permalink nor Sierra ID is given, generated ID should be used as base ID
    digar_schema = converter.digar_schema
    first_segment_id = digar_schema["dcterms:hasPart"][0]["hasPart"][0]["@id"]
    assert first_segment_id.startswith(TEST_GENERATED_ID)
    
    
def test_restricting_languages_with_ratio():
    """ Checks that param `min_language_ratio` influences
    the number of output languages.
    """
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID,
        permalink=TEST_PERMALINK,
        min_language_ratio=0
        
    )
    
    #If permalink is given, this should be used as base ID
    digar_schema = converter.digar_schema
    languages = [lang.get("value") for lang in digar_schema.get("dc:language")]
    assert len(languages) == 7
    
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID,
        permalink=TEST_PERMALINK,
        min_language_ratio=0.02
        
    )
    
    #If permalink is given, this should be used as base ID
    digar_schema = converter.digar_schema
    languages = [lang.get("value") for lang in digar_schema.get("dc:language")]
    assert len(languages) == 2
    
    converter = DIGARSchemaConverter(
        digitizer_output=TEST_DIGITIZER_OUTPUT,
        sierra_id=TEST_SIERRA_ID,
        generated_id=TEST_GENERATED_ID,
        permalink=TEST_PERMALINK,
        min_language_ratio=0.5
        
    )
    
    #If permalink is given, this should be used as base ID
    digar_schema = converter.digar_schema
    languages = [lang.get("value") for lang in digar_schema.get("dc:language")]
    assert len(languages) == 1
    



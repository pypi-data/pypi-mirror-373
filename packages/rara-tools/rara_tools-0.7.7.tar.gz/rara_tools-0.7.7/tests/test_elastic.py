import json
import os
import time
import uuid
from time import sleep

import elasticsearch_dsl
import pytest

from rara_tools.elastic import KataElastic

with open("./tests/test_data/elastic_docs.json") as fh:
    TEST_DOCUMENTS = json.load(fh)

es_url = os.getenv("ELASTIC_TEST_URL", "http://localhost:9200")
ELASTIC = KataElastic(es_url)
ELASTIC_BAD = KataElastic("http://locallost:9012")
TEST_INDEX_NAME = "tools_testing_index"
TEST_DOCUMENT_ID = None
TEST_DOCUMENT_INDEX = None
PARENT_ID = uuid.uuid4().hex


@pytest.mark.order(1)
def test_index_creation():
    """ Tests if index created and documents indexed.
    """
    # Create test index
    created = ELASTIC.create_index(TEST_INDEX_NAME)
    assert created["acknowledged"] is True
    time.sleep(2)


@pytest.mark.order(2)
def test_check():
    """Tests health check method.
    """
    assert ELASTIC.check() is True
    # test bad connection
    assert ELASTIC_BAD.check() is False


@pytest.mark.order(2)
def test_creating_index_again():
    """
    Test to see that running the function for index generation doesn't trigger errors
    on duplicates.
    """
    # Create test index
    created = ELASTIC.create_index(TEST_INDEX_NAME)
    assert created is None


@pytest.mark.order(3)
def test_adding_mapping_to_index():
    """Test adding mapping to an index"""
    schema = ELASTIC.generate_mapping()
    result = ELASTIC.add_mapping(TEST_INDEX_NAME, schema)
    assert result["acknowledged"] is True
    # Test adding the mapping again doesn't create errors.
    result = ELASTIC.add_mapping(TEST_INDEX_NAME, schema)
    assert result["acknowledged"] is True


@pytest.mark.order(4)
def test_document_addition():
    # Add test documents
    for document in TEST_DOCUMENTS:
        indexed = ELASTIC.index_document(TEST_INDEX_NAME, document)
        assert indexed["result"] == "created"
    # let it index
    sleep(1)


@pytest.mark.order(5)
def test_bulk_indexing_documents_cause_rollover():
    data = [{"start_page": number, "sequence_nr": 1, "end_page": number, "parent_id": PARENT_ID} for number in range(10)]
    chunks = [data[i:i + 3] for i in range(0, len(data), 3)]
    for chunk in chunks:
        success, errors = ELASTIC.bulk_index(chunk, TEST_INDEX_NAME, rollover_limit=3, refresh="wait_for")
        assert success is 3 or success is 1

    created_indices = ELASTIC.elasticsearch.indices.get(index=f"{TEST_INDEX_NAME}-*", expand_wildcards="open").body
    assert len(created_indices) == 4


@pytest.mark.order(6)
def test_bulk_indexing_and_document_fetch():
    """
    Test that the whole process of indexing a bunch of different texts and then the retrieval
    of only the requested documents works as intended.
    """
    success, errors = ELASTIC.bulk_index(TEST_DOCUMENTS, TEST_INDEX_NAME, rollover_limit=3, refresh="wait_for")

    # Test the integrity of the limiting query.
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "foo")
    assert len(result) == 2
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "bar")
    global TEST_DOCUMENT_ID
    global TEST_DOCUMENT_INDEX
    TEST_DOCUMENT_ID = result[0].meta.id
    TEST_DOCUMENT_INDEX = result[0].meta.index
    assert len(result) == 1
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "loll")
    assert len(result) == 0

    # Check that sorting works as expected.
    results = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, PARENT_ID)
    for index, document in enumerate(results):
        assert document.start_page == index


@pytest.mark.order(7)
def test_document_deleting():
    """
    Tests deleting a document from index.
    """
    deleted = ELASTIC.delete_document(TEST_DOCUMENT_INDEX, TEST_DOCUMENT_ID)
    assert deleted["result"] == "deleted"
    sleep(1)
    # check if document was actually deleted
    result = ELASTIC.get_documents_by_key(TEST_INDEX_NAME, "bar")
    assert len(result) == 0

    unique_id = uuid.uuid4().hex
    document_amount = 10
    documents = [{"doc_id": unique_id, "page": x} for x in range(document_amount)]
    ELASTIC.bulk_index(documents, TEST_INDEX_NAME, rollover_limit=100, refresh="wait_for")
    query = elasticsearch_dsl.Q("term", **{"doc_id.keyword": unique_id})
    search = elasticsearch_dsl.Search(using=ELASTIC.elasticsearch, index=TEST_DOCUMENT_INDEX).query(query)
    count = [hit.to_dict() for hit in search.scan()]
    assert len(count) == document_amount
    response = ELASTIC.delete_by_query(TEST_DOCUMENT_INDEX, {"doc_id.keyword": unique_id})

    attempt = 0
    while attempt < 3 and count != 0:
        search = elasticsearch_dsl.Search(using=ELASTIC.elasticsearch, index=TEST_DOCUMENT_INDEX).query(query)
        count = [hit.to_dict() for hit in search.scan()]
        time.sleep(3)
        attempt += 1

    assert len(count) == 0


@pytest.mark.order(8)
def test_index_deleting():
    """
    Tests deleting index. We delete the test index now.
    """
    deleted = ELASTIC.delete_index(TEST_INDEX_NAME)
    for i in range(10):
        ELASTIC.delete_index(f"{TEST_INDEX_NAME}-{i}")
    assert deleted["acknowledged"] is True

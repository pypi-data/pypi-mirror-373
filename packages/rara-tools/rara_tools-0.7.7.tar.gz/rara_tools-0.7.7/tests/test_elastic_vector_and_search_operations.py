import json
import os
import pytest

from time import sleep
from rara_tools.elastic import KataElastic


def load_json(file_path: str):
    with open(file_path, "r") as fh:
        data = json.load(fh)
    return data

TEST_DOCUMENTS = load_json("./tests/test_data/elastic_vectorized_docs.json")
TEST_VECTOR_DATA = load_json("./tests/test_data/test_vector_data.json")
TEST_VECTOR = TEST_VECTOR_DATA.get("vector")
    
es_url = os.getenv("ELASTIC_TEST_URL", "http://localhost:9200")
ELASTIC = KataElastic(es_url)

TEST_KNN_INDEX_NAME = "tools_knn_testing_index"
TEST_ANN_INDEX_NAME = "tools_ann_testing_index"

TEST_VECTOR_FIELD = "vector"



@pytest.mark.order(1)
def test_index_creation_with_knn_vector_mapping():
    """ Tests if index created and documents indexed.
    """
    # Create test index
    created = ELASTIC.create_index(TEST_KNN_INDEX_NAME)
    assert created["acknowledged"] is True
    result = ELASTIC.add_vector_mapping(
        index_name=TEST_KNN_INDEX_NAME, 
        field=TEST_VECTOR_FIELD
    )
    assert result["acknowledged"] is True
    
    
@pytest.mark.order(2)
def test_index_creation_with_ann_vector_mapping():
    """ Tests if index created and documents indexed.
    """
    # Create test index
    created = ELASTIC.create_index(TEST_ANN_INDEX_NAME)
    assert created["acknowledged"] is True
    result = ELASTIC.add_ann_vector_mapping(
        index_name=TEST_ANN_INDEX_NAME, 
        field=TEST_VECTOR_FIELD
    )
    assert result["acknowledged"] is True
    

@pytest.mark.order(3)
def test_vectorized_document_addition_knn_index():
    """ Tests indexing vectorized documents.
    """
    # Add test documents
    for document in TEST_DOCUMENTS:
        indexed = ELASTIC.index_document(TEST_KNN_INDEX_NAME, document)
        assert indexed["result"] == "created"
    # let it index
    sleep(1)
    
@pytest.mark.order(4)
def test_vectorized_document_addition_ann_index():
    """ Tests indexing vectorized documents.
    """
    # Add test documents
    for document in TEST_DOCUMENTS:
        indexed = ELASTIC.index_document(TEST_ANN_INDEX_NAME, document)
        assert indexed["result"] == "created"
    # let it index
    sleep(1)
    
@pytest.mark.order(5)
def test_fuzzy_search():
    """ Tests fuzzy search.
    """
    response = ELASTIC.execute_fuzzy_search(
        index=TEST_ANN_INDEX_NAME,
        field="variations",
        entity="Paul Keres",
        fuzziness=0
    )
    total_hits = response.hits.total.value
    assert total_hits == 2
    
    response = ELASTIC.execute_fuzzy_search(
        index=TEST_ANN_INDEX_NAME,
        field="variations",
        entity="Paul Keres",
        fuzziness=2
    )
    total_hits = response.hits.total.value
    assert total_hits == 3
    
    
@pytest.mark.order(6)
def test_ann_vector_search():
    """ Tests ANN vector search.
    """
    # Execut fuzzy search to get ID restrictions
    response = ELASTIC.execute_fuzzy_search(
        index=TEST_ANN_INDEX_NAME,
        field="variations",
        entity="Paul Keres",
        fuzziness=2
    )
    total_hits = response.hits.total.value
    assert total_hits == 3    
    elastic_ids = [hit.meta.id for hit in response]
    
    response = ELASTIC.execute_ann_vector_search(
        index=TEST_ANN_INDEX_NAME,
        field="vector",
        query_vector=TEST_VECTOR,
        k=1,
        n_docs=1,
        num_candidates=10,
        elastic_ids=elastic_ids
    )
    descriptions = [hit.description for hit in response]
    assert len(descriptions) == 1
    assert descriptions[0] == "Eesti maletaja ja maleteoreetik"

    
@pytest.mark.order(7)
def test_script_score_vector_search():
    """ Tests ANN vector search.
    """
    # Execut fuzzy search to get ID restrictions
    response = ELASTIC.execute_fuzzy_search(
        index=TEST_KNN_INDEX_NAME,
        field="variations",
        entity="Paul Keres",
        fuzziness=2
    )
    total_hits = response.hits.total.value
    assert total_hits == 3    
    elastic_ids = [hit.meta.id for hit in response]
    
    response = ELASTIC.execute_script_score_vector_search(
        index=TEST_KNN_INDEX_NAME,
        field="vector",
        query_vector=TEST_VECTOR,
        n_docs=1,
        elastic_ids=elastic_ids
    )
    descriptions = [hit.description for hit in response]
    assert len(descriptions) == 1
    assert descriptions[0] == "Eesti maletaja ja maleteoreetik"

    
@pytest.mark.order(8)
def test_index_deleting():
    """
    Tests deleting index. We delete the test index now.
    """
    indices = [TEST_KNN_INDEX_NAME, TEST_ANN_INDEX_NAME]
    for index in indices:
        deleted = ELASTIC.delete_index(index)
        sleep(1)
        assert deleted["acknowledged"] is True
        

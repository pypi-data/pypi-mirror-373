from typing import Any, Dict, Iterator, Optional, List

import elasticsearch_dsl
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index, Search, Q
from elasticsearch_dsl.response import Response

from .decorators import _elastic_connection


class KataElastic:
    """A class to manage all required Elasticsearch operations for Kata.
    """

    TYPE_MAPPING = {
        "keyword": elasticsearch_dsl.Keyword,
        "text": elasticsearch_dsl.Text,
        "float": elasticsearch_dsl.Float,
        "integer": elasticsearch_dsl.Integer,
        "date": elasticsearch_dsl.Date,
    }

    DEFAULT_MAPPING = {
        "text": "text",
        "parent_id": "keyword",
        "article_id": "keyword",
        "text_quality": "float",
        "n_chars": "integer",
        "n_words": "integer",
        "language": "keyword",
        "end_page": "integer",
        "start_page": "integer",
        "sequence_nr": "integer",
        "section_title": "keyword",
        "section_type": "keyword",
        "section_meta": "text",
    }

    def __init__(self, elasticsearch_url: str, timeout: Optional[int] = None):
        self.timeout = timeout
        self.elasticsearch_url = elasticsearch_url
        self.elasticsearch = Elasticsearch(self.elasticsearch_url, request_timeout=self.timeout)

    def _produce_rollover_index(self, index_prefix: str, rollover_limit: int) -> str:
        indices = self.elasticsearch.indices.get(index=f"{index_prefix}-*", expand_wildcards="open")
        sorted_indices = sorted([(k, v["settings"]["index"]["creation_date"]) for k, v in indices.items()], key=lambda x: x[1], reverse=True)
        sorted_indices = [i[0] for i in sorted_indices]

        # new index name if none exist
        if not len(sorted_indices):
            last_index_name = f"{index_prefix}-0"
            last_index_count = 0
        else:
            last_index_name = sorted_indices[0]
            last_index_count = self.elasticsearch.count(index=last_index_name)["count"]
        # check the size of the last index of the pipeline
        if last_index_count >= rollover_limit:
            new_index_number = int(last_index_name[-1]) + 1
            last_index_name = f"{index_prefix}-{new_index_number}"

        return last_index_name

    @_elastic_connection
    def check(self) -> bool:
        """Checks Elasticsearch connection.
        :return: bool: Elasticsearch alive or dead.
        """
        if self.elasticsearch.ping():
            return True
        return False

    def generate_mapping(self, schema: dict | None = None) -> dict:
        mapping_dsl = elasticsearch_dsl.Mapping()
        mapping = schema or self.DEFAULT_MAPPING
        for field_name, field_type in mapping.items():
            if field_type in self.TYPE_MAPPING:
                # We instantiate the class stored in the type mapping.
                mapping_dsl.field(field_name, self.TYPE_MAPPING[field_type]())
        return mapping_dsl.to_dict()

    @_elastic_connection
    def add_mapping(self, index_name: str, schema: dict):
        index = Index(name=index_name)
        return index.put_mapping(body=schema, using=self.elasticsearch)

    @_elastic_connection
    def delete_by_query(self, index: str, query_kwargs: dict, query_type: str = "term", wait_for_completion=True):
        query = Q(query_type, **query_kwargs)
        s = Search(using=self.elasticsearch, index=index).query(query)
        response = self.elasticsearch.delete_by_query(
            index=index,
            body={"query": s.to_dict()["query"]},
            wait_for_completion=True
        )
        return response

    @_elastic_connection
    def add_vector_mapping(
            self,
            index_name: str,
            field: str,
            schema: Optional[dict] = None,
            dims: int = 1024
    ) -> dict:
        vector_mapping = {
            "properties": {
                field: {
                    "type": "dense_vector",
                    "dims": dims
                }
            }
        }
        mapping = schema or vector_mapping
        index = Index(name=index_name)
        return index.put_mapping(body=mapping, using=self.elasticsearch)

    @_elastic_connection
    def add_ann_vector_mapping(
            self,
            index_name: str,
            field: str,
            schema: Optional[dict] = None,
            dims: int = 1024
    ) -> dict:
        vector_mapping = {
            "properties": {
                field: {
                    "type": "dense_vector",
                    "dims": dims,
                    "similarity": "cosine",
                    "index": True
                }
            }
        }
        mapping = schema or vector_mapping
        index = Index(name=index_name)
        return index.put_mapping(body=mapping, using=self.elasticsearch)

    @_elastic_connection
    def add_vector(
            self,
            index_name: str,
            document_id: str,
            vector: List[float],
            field: str,
            refresh: str = "wait_for"
    ) -> dict:
        schema = {"doc": {field: vector}}
        return self.elasticsearch.update(
            index=index_name,
            id=document_id,
            body=schema,
            refresh=refresh
        )

    @_elastic_connection
    def create_index(
            self,
            index: str,
            shards: int = 3,
            replicas: int = 1,
            settings: Optional[dict] = None,
    ) -> Dict | None:
        """Creates empty index.
        :param: index str: Name of the index to create.
        :param: shards int: Number of shards for the index.
        :param: replicas int: Number of replicas of the index.
        :param: settings dict: Overwrite settings for the index.
        """

        index_exists = self.elasticsearch.indices.exists(index=index).body
        if index_exists is False:
            setting_body = settings or {
                "number_of_shards": shards,
                "number_of_replicas": replicas,
            }
            return self.elasticsearch.indices.create(index=index, settings=setting_body)

    @_elastic_connection
    def delete_index(self, index: str, ignore: Optional[bool] = True) -> Dict:
        """Deletes index.
        :param: index str: Name of the index to be deleted.
        :param: ignore bool: Ignore errors because of closed/deleted index.
        :return: Dict of Elastic's acknowledgement of the action.
        """
        response = self.elasticsearch.indices.delete(index=index, ignore_unavailable=ignore, expand_wildcards="open")
        return response

    @_elastic_connection
    def delete_document(self, index: str, document_id: str) -> ObjectApiResponse[Any]:
        """Deletes document fom index.
        :param: document_id str: ID of the document to be deleted.
        :param: index str: Index where the document is to be found.
        :param: ignore bool: Ignore errors because of closed/deleted index.
        :return: Dict of Elastic's acknowledgement of the action.
        """
        response = self.elasticsearch.delete(id=document_id, index=index)
        return response

    @_elastic_connection
    def bulk_index(
            self,
            documents: Iterator[dict],
            index_prefix: str,
            rollover_limit: int,
            refresh="false",
            create_index: bool = True
    ) -> (int, int):
        last_index_name = self._produce_rollover_index(index_prefix, rollover_limit)
        if create_index:
            response = self.create_index(index=last_index_name)
            response = self.add_mapping(index_name=last_index_name, schema=self.generate_mapping())
            pass

        actions = [{"_index": last_index_name, "_source": document} for document in documents]
        successful_count, error_count = bulk(actions=actions, client=self.elasticsearch, max_retries=3, refresh=refresh)
        return successful_count, error_count

    @_elastic_connection
    def bulk_index_without_rollver(
            self,
            documents: Iterator[dict],
            index: str,
            refresh="false",
    ) -> (int, int):
        actions = [{"_index": index, "_source": document} for document in documents]
        successful_count, error_count = bulk(actions=actions, client=self.elasticsearch, max_retries=3, refresh=refresh)
        return successful_count, error_count

    @_elastic_connection
    def index_document(self, index: str, body: dict, document_id: Optional[str] = None) -> Dict:
        """Indexes document.
        :param: index str: Index that document will be indexed into.
        :param: body dict: Document body.
        :param: document_id str: Optional id for the document. Is generated automatically if None.
        :return: Dict of Elastic's acknowledgement of the action.
        """
        if document_id:
            indexed = self.elasticsearch.index(index=index, id=document_id, body=body)
        else:
            indexed = self.elasticsearch.index(index=index, body=body)
        return indexed

    @_elastic_connection
    def get_documents_by_key(self, index: str, document_key: str, sort_fields=("start_page", "end_page", "sequence_nr",)):
        index = f"{index}-*"
        s = elasticsearch_dsl.Search(using=self.elasticsearch, index=index)
        s = s.query("match", parent_id=document_key).sort(*sort_fields)
        # Since scan doesn't allow for sorting, we do it manually after fetching the documents.
        documents = sorted(
            s.scan(), key=lambda doc: [getattr(doc, field) for field in sort_fields]
        )
        return documents

    @_elastic_connection
    def execute_fuzzy_search(
            self,
            index: str,
            field: str,
            entity: str,
            fuzziness: int = 2,
            prefix_length: int = 1,
            max_expansions: int = 50
    ) -> Response:
        """Executes a fuzzy search.
        :param: index str: Index to search from.
        :param: entity str: Entity to search matches for.
        :param: fuzziness int: Maximum edit distance for a match.
        :param: prefix_length int: Number of characters in the prefix that 
            should overlap with the original entity's prefix.
        :param: max_expansion int: maximum number of terms the fuzzy query 
            will match before halting the search
        :return: Dict on search results.
        """
        query_params = {
            f"{field}.keyword": {
                "value": entity,
                "fuzziness": fuzziness,
                "max_expansions": max_expansions,
                "prefix_length": prefix_length
            }
        }
        s = elasticsearch_dsl.Search(using=self.elasticsearch, index=index)
        s = s.query("fuzzy", **query_params)
        response = s.execute()
        return response

    def execute_ann_vector_search(
            self,
            index: str,
            field: str,
            query_vector: List[float],
            k: int = 10,
            num_candidates: int = 100,
            n_docs: int = 10,
            elastic_ids: List[str] = []
    ) -> Response:
        """ Execute a vector search.
        NB! Works only with ANN mapping!
        
        :param: index str: Index to search from.
        :param: field str: Field containing vectorized data.
        :param: query vector List[float]: Vector to search matches for.
        :param: k int: Number of nearest neighbors to return.
        :param: num_candidates int: Number of candidates considered before selecting k results.
        :param: n_docs: int: Number of documents to return.
        :param: elastic_ids: List[str]: Elastic ID-s for restricting the search.
        """

        s = elasticsearch_dsl.Search(using=self.elasticsearch, index=index)

        # Add kNN vector search
        s = s.extra(
            knn={
                "field": field,
                "query_vector": query_vector,
                "k": k,
                "num_candidates": num_candidates
            }
        )

        # Add ID filtering, if elastic_ids are specified
        if elastic_ids:
            s = s.query(
                elasticsearch_dsl.Q("terms", _id=elastic_ids)
            )

        # Sort by score and return `n_docs` best-matching documents
        s = s.extra(size=n_docs)

        # Execute the search
        response = s.execute()
        return response

    def execute_script_score_vector_search(
            self,
            index: str,
            field: str,
            query_vector: List[float],
            n_docs: int = 10,
            elastic_ids: List[str] = []
    ) -> Response:
        """ Execute a vector search.
        NB! Requires different mapping than ANN!
        
        :param: index str: Index to search from.
        :param: field str: Field containing vectorized data.
        :param: query vector List[float]: Vector to search matches for.
        :param: n_docs: int: Number of documents to return.
        :param: elastic_ids: List[str]: Elastic ID-s for restricting the search.
        """
        s = elasticsearch_dsl.Search(using=self.elasticsearch, index=index)

        if elastic_ids:
            query = elasticsearch_dsl.Q("terms", _id=elastic_ids)
        else:
            query = elasticsearch_dsl.Q("match_all")
        # Apply script_score query
        s = s.query(
            "script_score",
            query=query,
            script={
                "source": f"1.0 + cosineSimilarity(params.query_vector, '{field}')",
                "params": {
                    "query_vector": query_vector
                }
            }
        )
        # Set min_score and limit number of documents
        s = s.extra(size=n_docs)

        # Execute search
        response = s.execute()
        return response

    def __str__(self) -> str:
        return self.elasticsearch_url

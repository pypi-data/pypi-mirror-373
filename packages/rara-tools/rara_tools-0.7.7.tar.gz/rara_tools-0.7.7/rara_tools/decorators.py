import functools
from typing import Any, Callable

from elasticsearch import AuthenticationException
from elasticsearch import ConnectionError as ElasticsearchConnectionError
from elasticsearch import ConnectionTimeout, NotFoundError, RequestError

from .exceptions import ElasticsearchException

ELASTIC_NOT_FOUND_MESSAGE = 'Could not find specified data from Elasticsearch!'
ELASTIC_REQUEST_ERROR_MESSAGE = 'Error executing Elasticsearch query! Bad query?'
ELASTIC_CONNECTION_TIMEOUT_MESSAGE = 'Connection to Elasticsearch took too long, please try again later!'
ELASTIC_AUTHENTICATION_ERROR_MESSAGE = 'Could not authenticate with Elasticsearch!'
ELASTIC_UNKNOWN_ERROR_MESSAGE = 'Unexpected error from Elasticsearch!'
ELASTIC_CONNECTION_ERROR_MESSAGE = 'Could not connect to Elasticsearch, is the location properly configured?'


def _elastic_connection(func: Callable) -> Callable:
	@functools.wraps(func)
	def wrapper(*args: Any, **kwargs: Any) -> Any:
		try:
			return func(*args, **kwargs)
		except NotFoundError as exception:
			raise ElasticsearchException(ELASTIC_NOT_FOUND_MESSAGE) from exception
		except RequestError as exception:
			raise ElasticsearchException(ELASTIC_REQUEST_ERROR_MESSAGE) from exception
		except ConnectionTimeout as exception:
			raise ElasticsearchException(ELASTIC_CONNECTION_TIMEOUT_MESSAGE) from exception
		except AuthenticationException as exception:
			raise ElasticsearchException(ELASTIC_AUTHENTICATION_ERROR_MESSAGE) from exception
		# Important to set the ConnectionError to the bottom of the chain
		# as it's one of the superclasses the other exceptions inherit.
		except ElasticsearchConnectionError as exception:
			if exception.__context__ and 'timed out' in str(exception.__context__):
				# urllib3.exceptions.ConnectTimeoutError can cause an
				# elasticsearch.exceptions.ConnectionError,
				# but we'd like to treat timing out separately
				raise ElasticsearchException(ELASTIC_CONNECTION_TIMEOUT_MESSAGE) from exception
			raise ElasticsearchException(ELASTIC_CONNECTION_ERROR_MESSAGE) from exception
		except Exception as exception:
			raise ElasticsearchException(ELASTIC_UNKNOWN_ERROR_MESSAGE) from exception
	return wrapper

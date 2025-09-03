import logging
from typing import Optional

try:
    from elasticsearch import Elasticsearch

    elasticsearch_installed = True
except ImportError:
    Elasticsearch = None
    elasticsearch_installed = False

from codemie_tools.data_management.elastic.models import ElasticConfig

logger = logging.getLogger(__name__)


class SearchElasticIndexResults:

    @classmethod
    def _get_client(cls, elastic_config: ElasticConfig) -> Optional[Elasticsearch]:
        if not elasticsearch_installed:
            raise ImportError("'elasticsearch' package is not installed.")
        if elastic_config.api_key:
            return Elasticsearch(elastic_config.url,
                                 api_key=elastic_config.api_key,
                                 verify_certs=False,
                                 ssl_show_warn=False)
        else:
            return Elasticsearch(elastic_config.url, verify_certs=False, ssl_show_warn=False)

    @classmethod
    def search(cls, index: str, query: str, elastic_config: ElasticConfig):
        client = cls._get_client(elastic_config=elastic_config)
        return client.search(index=index, body=query)

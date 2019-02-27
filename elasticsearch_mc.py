from base import AbstractMulticaster
from elasticsearch import Elasticsearch

class ElasticsearchMulticaster(AbstractMulticaster):
    """ Do whatever you gotta do in this file to instantiate the elasticsearch hosts you want to connect to
        This file is a template -- company specific info has been scrubbed from this file. No guarantees it
        will work
    """

  es_host_map = {
    'dev': 'https://some-dev-endpoint-that-corresponds-to-an-elasticsearch-cluster',
    'staging': 'https://some-staging-endpoint-that-corresponds-to-an-elasticsearch-cluster',
    'prod': 'https://some-prod-endpoint-that-corresponds-to-an-elasticsearch-cluster',
  }

  def build_hostgroup(self, selected_envs):
      hostgroup = {}

      for env in selected_envs:
        hostgroup[env] = Elasticsearch(
          hosts=[{'host': self.es_host_map[env], 'port': 443}],
          use_ssl=True,
          verify_certs=True,
        )

      return hostgroup

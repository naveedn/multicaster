from base import AbstractMulticaster
import redis

class RedisMulticaster(AbstractMulticaster):
  """ Do whatever you gotta do in this file to instantiate the redis hosts you want to connect to
      This file is a template -- company specific info has been scrubbed from this file. No guarantees it
      will work
  """

  ec_host_map = {
    'dev': 'redis-host-for-dev-environment-that-we-want-to-connect-to',
    'staging': 'redis-host-for-staging-environment-that-we-want-to-connect-to',
    'prod': 'redis-host-for-prod-environment-that-we-want-to-connect-to',
  }

  def build_hostgroup(self, selected_envs):
      hostgroup = {}

      for env in selected_envs:
        hostgroup[env] = redis.StrictRedis(
          host=self.ec_host_map[env],
          port=6379,
          db='some-db'
        )

      return hostgroup

import os
import json

class AbstractMulticaster():
  def __init__(self, **kwargs):
    self._env = self.get_current_env(kwargs.get('env'))
    self._envs_to_replicate = self.get_cascading_envs(self._env)
    self._hosts = self.build_hostgroup(self._envs_to_replicate)

  def get_current_env(self, env=None):
    """Used in init(). Gets the current environment to base multicasting off of"""
    if env:
      selected_env = env.lower()
    elif os.environ.get('ENV'):
      selected_env = os.environ.get('ENV').lower()
    else:
      raise RuntimeError("Cannot replicate changes to other environments without specifying current env!")

    return selected_env

  def get_cascading_envs(self, env=None):
    """Given an env, get all the envs that are downstream. Will default to self._env (defined in constructor)"""
    current_env = env if env is not None else self._env

    if current_env == 'prod':
      return ['dev', 'staging', 'prod']
    elif current_env == 'staging':
      return ['dev', 'staging']
    else:
      return ['dev']

  def build_hostgroup(self, selected_envs):
    """Will build the concrete instances of each multicaster and store it in a dict"""
    raise NotImplementedError("Gotta do this in a concrete subclass!")

  def execute(self, operation, *args, **kwargs):
    """@description:
          - Loops through each environment in hosts, will call the hosts 'operation' in sequence
          - Uses the Command Pattern to delegate work to the object that knows how to perform it. See: https://sourcemaking.com/design_patterns/command
          - WARNING: If this method fails, you will need to manually rollback / undo the changes!
       @params:
          - {String} operation: corresponds to method name in the receiver
          - {List} args: contains variadic params necessary for operation
          - {Dict} kwargs: bag of meta params that override default behavior
              - include_all_envs = will execute operation to all hosts in hostmap, not just cascading ones
        @returns:
          - {Array[Dict]}|Exception results: will return results from all clients, or raise exception if it happened in any one client
      """
    hosts = self._hosts
    include_all_envs = kwargs.get('include_all_envs', False)

    if include_all_envs:  # Allow the user to override which envs to multicast to, for a given command
      all_envs = self.get_cascading_envs('prod')
      hosts = self.build_hostgroup(all_envs)
      print '-----> we are overriding and pushing to all envs!'

    results = [] # remember state of previous operations
    current_env = None

    try:
      for env, client in hosts.items():
        current_env = env
        if hasattr(client, operation) and callable(getattr(client, operation)):
          method_to_execute = getattr(client, operation)

          print '-----> executing {op} for {env}'.format(op=operation, env=current_env)

          response = method_to_execute(*args)
          results.append({'env': env, 'response': response})

      return results

    except Exception as e:
      fucked_env = {'env': current_env, 'error': str(e)}

      results.append(fucked_env)

      debug_info = {
        'includes_all_envs': include_all_envs,
        'operation': operation,
        'params': args,
        'results': results
      }

      print '-----> FAILURE! MUST MANUALLY ROLLBACK INFORMATION IN ENVS:'
      print json.dumps(debug_info, indent=2, skipkeys=True)
      raise e

# multicaster
An easy way to perform an operation on multiple hosts across environments. Useful for anomaly detection of data, replicating changes across envs, etc. 


# Usage
- changes will replicate from current environemnt "downwards"

```python
from multicaster.redis_mc import RedisMulticaster

red = RedisMulticaster(env='staging') # will perform operations on staging, dev

red.execute('mset', {{'fake-1': "L", 'fake-2': "O", 'fake-3': "L"}})
red.execute('mget', ['fake-1', 'fake-2', 'fake-3'])

## OUTPUT
# -----> executing mset for staging
# -----> executing mset for dev
# -----> executing mget for staging
# -----> executing mget for dev
#
# [{'env': 'staging', 'response': ['L', 'O', 'L']},
#  {'env': 'dev', 'response': ['L', 'O', 'L']}]
```

- if you pass in a `include_all_envs` boolean flag, it will update all envs, regardless of whichever env you are currently set at

```python
from multicaster.redis_mc import RedisMulticaster
red = RedisMulticaster(env='dev') # will perform operations only on dev

red.execute('mget', ['fake-1', 'fake-2', 'fake-3'], include_all_envs=True) # this flag overrides and pushes to all envs

## OUTPUT
# -----> we are overriding and pushing to all envs!
# -----> executing mget for prod
# -----> executing mget for staging
# -----> executing mget for dev
#
# [{'env': 'prod', 'response': [None, None, None]},
#  {'env': 'staging', 'response': ['L', 'O', 'L']},
#  {'env': 'dev', 'response': ['L', 'O', 'L']}]
```


TODO:
- allow user to pass in list of envs in constructor (right now, hardcoded to dev, staging, prod only)
- add exception trace so user can see line number where original exception was thrown

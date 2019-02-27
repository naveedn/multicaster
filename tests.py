import unittest
import os
import sys
import json
import StringIO

from base import AbstractMulticaster
from redis_mc import RedisMulticaster
from elasticsearch_mc import ElasticsearchMulticaster

class TestMultiCaster(unittest.TestCase):

    def test_cannot_instantiate_abstract_class(self):
        with self.assertRaises(NotImplementedError):
            AbstractMulticaster()

    def test_cannot_instantiate_without_env_defined(self):
        del os.environ['ENV'] # temporarily unset this if defined

        with self.assertRaises(RuntimeError):
            RedisMulticaster()

        with self.assertRaises(RuntimeError):
            ElasticsearchMulticaster()

    def test_can_instantiate_client_implicitly(self):
        os.environ['ENV'] = 'dev' # assume env variable exists

        try:
            red = RedisMulticaster()
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_can_instantiate_client_explicitly(self):
        try:
            red = RedisMulticaster(env='dev')
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_gets_correct_cascading_envs(self):
        red = RedisMulticaster(env='prod')
        self.assertTrue(red._hosts.keys(), ['dev', 'staging', 'prod'])

        es = ElasticsearchMulticaster(env='staging')
        self.assertTrue(es._hosts.keys(), ['dev', 'staging'])

    def test_execute(self):
        red = RedisMulticaster(env='staging')

        red.execute('set_many', {'fake-1': "L", 'fake-2': "O", 'fake-3': "L"})
        response = red.execute('get_many', ['fake-1', 'fake-2', 'fake-3'])

        self.assertEqual(response, [
          {'env': 'staging', 'response': ['L', 'O', 'L']},
          {'env': 'dev', 'response': ['L', 'O', 'L']}
        ])

        #clean up
        red.execute('delete', 'fake-1')
        red.execute('delete', 'fake-2')
        red.execute('delete', 'fake-3')


    def test_execute_with_override(self):
        # set the env to dev, but include override flag for each individual operation
        red = RedisMulticaster(env='dev')

        red.execute('set_many', {'fake-1': "L", 'fake-2': "O", 'fake-3': "L"}, include_all_envs=True)
        response = red.execute('get_many', ['fake-1', 'fake-2', 'fake-3'], include_all_envs=True)

        self.assertEqual(response, [
          {'env': 'prod', 'response': ['L', 'O', 'L']},
          {'env': 'staging', 'response': ['L', 'O', 'L']},
          {'env': 'dev', 'response': ['L', 'O', 'L']}
        ])

        #clean up
        red.execute('delete', 'fake-1', include_all_envs=True)
        red.execute('delete', 'fake-2', include_all_envs=True)
        red.execute('delete', 'fake-3', include_all_envs=True)

    def test_get_useful_debug_info_on_failure(self):
        def setUp():
            capturedOutput = StringIO.StringIO()  # Create StringIO object
            sys.stdout = capturedOutput     #  and redirect stdout.
            return capturedOutput

        def tearDown():
            sys.stdout = sys.__stdout__     # Reset redirect.

        dummy_payload = {
          'author': 'Naveed Nadjmabadi',
          'id': -1,
          'title': 'Naveeds great multicast client test',
          'url': 'fake-url'
          'foo': 'bar'
          }

        es = ElasticsearchMulticaster(env='staging')

        stdout = setUp()

        # will fail because currently we cannot index anything that is not products
        with self.assertRaises(RuntimeError):
          es.execute('index', 'some-es-index', dummy_payload)

        tearDown()

        str_lines = stdout.getvalue().split('\n')

        self.assertEqual(str_lines[0], '-----> executing index_data for staging')
        self.assertEqual(str_lines[1], '-----> FAILURE! MUST MANUALLY ROLLBACK INFORMATION IN ENVS:')

        json_blob = json.loads(''.join(str_lines[2:]))
        self.assertEqual(json_blob, {
          "operation": "index",
          "includes_all_envs": False,
          "params": [
            "some-es-index",
            {
              "url": "fake-url",
              "author": "Naveed Nadjmabadi",
              "foo": "bar",
              "title": "Naveeds great multicast client test",
              "id": -1
            },
          ],
          "results": [
            {
              "env": "staging",
              "error": "please ignore this is a sample test that will not work in opensource client."
            }
          ]
        })

if __name__ == '__main__':
    unittest.main()

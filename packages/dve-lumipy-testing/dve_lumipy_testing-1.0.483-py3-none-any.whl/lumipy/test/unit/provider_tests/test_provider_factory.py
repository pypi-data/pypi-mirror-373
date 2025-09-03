import os
import time
import unittest
from lumipy.provider.factory import Factory, machine_name
from lumipy.test.test_infra import get_logs
from pathlib import Path
import tempfile


class TestProviderFactory(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_provider_factory_ctor_happy(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='TESTUSER',
            domain='test-domain',
            whitelist_me=True,
            _dev_dll_path="fake-path",
            _fbn_run=False,
        )

        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertEqual(
            'dotnet fake-path/Finbourne.Honeycomb.Host.dll --quiet --authClientDomain=test-domain --localRoutingUserId "TESTUSER" --config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/" ',
            fact.cmd
        )

    def test_provider_factory_ctor_happy_global(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='global',
            domain='test-domain',
            whitelist_me=True,
            _dev_dll_path="fake-path",
            _fbn_run=False,
        )

        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertEqual(
            f'dotnet fake-path/Finbourne.Honeycomb.Host.dll --quiet --authClientDomain=test-domain --routeAs:Global --config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/" "DataProvider:RoutingTypeGlobalMachineWhitelist=>{machine_name()}" ',
            fact.cmd
        )

    def test_provider_factory_ctor_happy_via_proxy(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='global',
            domain='test-domain',
            whitelist_me=True,
            _dev_dll_path="fake-path",
            _fbn_run=False,
            via_proxy=True,
        )

        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertIn(
            f'dotnet fake-path/Finbourne.Honeycomb.Host.dll --quiet --authClientDomain=test-domain --routeAs:Global --viaProxy --config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/" "DataProvider:RoutingTypeGlobalMachineWhitelist=>{machine_name()}" ',
            fact.cmd
        )

    def test_provider_factory_ctor_happy_fbn_run(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='global',
            whitelist_me=False,
            _dev_dll_path="fake-path",
            _fbn_run=True,
        )

        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertEqual(
            f'dotnet fake-path/Finbourne.Honeycomb.Host.dll --quiet --routeAs:Global --config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/" "Metrics:Enabled=>true" "NameServiceClient:RabbitConfigFile=>honeycomb-rabbit-config-plain.json" "NameServiceClient:RabbitUserName=>service-main" "NameServiceClient:RabbitUserPassword->/usr/app/secrets/service-main" ',
            fact.cmd
        )

    def test_provider_factory_ctor_happy_fbn_run_local(self):
        fact = Factory(
            host='localhost',
            port=5464,
            user='global',
            whitelist_me=True,
            _dev_dll_path="fake-path",
            _fbn_run=True,
        )

        self.assertFalse(fact.errored)
        self.assertIsNone(fact.process)
        self.assertTrue(fact.starting)

        self.assertEqual(
            f'dotnet fake-path/Finbourne.Honeycomb.Host.dll --quiet --routeAs:Global --config "PythonProvider:BaseUrl=>http://localhost:5464/api/v1/" "DataProvider:RoutingTypeGlobalMachineWhitelist=>{machine_name()}" "Metrics:Enabled=>true" "NameServiceClient:RabbitConfigFile=>honeycomb-rabbit-config-plain.json" "NameServiceClient:RabbitUserName=>service-main" "NameServiceClient:RabbitUserPassword->/usr/app/secrets/service-main" ',
            fact.cmd
        )

    def test_provider_factory_ctor_unhappy(self):
        # bad host
        with self.assertRaises(ValueError):
            Factory(host='$(bad stuff)', port=1234, user='user', domain='dom', _dev_dll_path="fake-path", whitelist_me=False, _fbn_run=False)

        # bad port
        with self.assertRaises(ValueError):
            Factory(host='127.0.0.1', port="ABC", user='user', domain='dom',  _dev_dll_path="fake-path", whitelist_me=False, _fbn_run=False)

        # user=global and whitelist_me is False
        with self.assertRaises(ValueError):
            Factory(host='localhost', port=1234, user='global', domain='dom', _dev_dll_path="fake-path", whitelist_me=False, _fbn_run=False)

        # domain has been specified whilst _fbn_run = True
        with self.assertRaises(ValueError):
            Factory(host='localhost', port=1234, user='user', domain='dom', _dev_dll_path="fake-path", whitelist_me=False, _fbn_run=True)


    def test_factory_logs_with_valid_command(self):
        stdout, stderr = get_logs(func=self.wrapper_get_factory_logs_happy)

        self.assertFalse(stderr)
        self.assertIn("hello_from_a_test_hello_from_a_test_", stdout)

    def test_factory_logs_with_unhappy_command(self):
        stdout, stderr = get_logs(func=self.wrapper_get_factory_logs_unhappy)

        # We have no stderr here because we log any stderr to the stdout
        self.assertFalse(stderr)
        self.assertIn("This is a message to stderr", stdout)

    def wrapper_get_factory_logs_unhappy(self):
        return self.get_factory_logs(cmd="python -c import sys; sys.stderr.write('This is a message to stderr')")

    def wrapper_get_factory_logs_happy(self):
        return self.get_factory_logs(cmd="python -c print('hello_from_a_test_'*2)")

    @staticmethod
    def get_factory_logs(cmd):
        fact = Factory(
            host='localhost',
            port=5464,
            user='global',
            domain='test-domain',
            whitelist_me=True,
            _skip_checks=True,
            _fbn_run=False,
        )

        fact.cmd = cmd
        fact.start()

        while fact.process.poll() is None:
            time.sleep(0.1)

        fact.process.stdout.close()
        fact.process.stderr.close()

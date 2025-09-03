import unittest
from click.testing import CliRunner

from lumipy.cli.commands.setup import setup
from lumipy.cli.commands.config import config
from lumipy.cli.commands.run import run

from unittest.mock import patch, MagicMock


class TestCli(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_setup_domain(self):
        result = self.runner.invoke(setup)
        self.assertIn("Setting up python providers", result.stdout)

    def test_setup_domain_with_domain(self):
        result = self.runner.invoke(setup, ['--domain', 'fbn-ci'])
        self.assertIn("Setting up python providers", result.stdout)

    def test_add_good_config(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci-fake_', '--token', 'NTBhYzIwODEwN2JkNGVhMWI1ZDBhZTVmYTcxMTEyZWV8==', '--overwrite'])
        self.assertIsNone(result.exception)

    def test_set_good_domain(self):
        self.runner.invoke(config, ['add', '--domain', 'fbn-ci-new_', '--token', 'NTBhYzIwODEwN2JkNGVhMWI1ZDBhZTVmYTcxMTEyZWV8==', '--overwrite'])
        result = self.runner.invoke(config, ['set', '--domain', 'fbn-ci-new_'])
        self.assertIsNone(result.exception)

    def test_set_bad_domain(self):
        result = self.runner.invoke(config, ['set', '--domain', 'fbn-a-domain-which-does-not-exist'])
        self.assertEqual(result.exception.args[0], 'Domain fbn-a-domain-which-does-not-exist not found in config. You can add it with config.add("fbn-a-domain-which-does-not-exist", <PAT>).')

    def test_add_good_domain_bad_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_good_domain_empty_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', ''])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_good_domain_none_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', None])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_bad_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', 'https://fbn-ci.lusid.com/app', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: https://fbn-ci.lusid.com/app')

    def test_add_empty_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', '', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: ')

    def test_add_none_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', None, '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: None')

    def test_fbn_run_works_correctly(self):
        # This broke temporarily in click 8.2.0

        with patch("lumipy.cli.commands.run.lp.ProviderManager") as MockProviderManager:
            pm_instance = MagicMock()
            MockProviderManager.return_value = pm_instance

            result = self.runner.invoke(run, ['demo', '--fbn-run'])

            assert result.exit_code == 0

            MockProviderManager.assert_called_once()

            assert MockProviderManager.call_args.kwargs.get("_fbn_run") is True

import unittest
from contextlib import redirect_stdout
from lumipy._config_manager import ConfigManager
from pathlib import Path
import tempfile
import shutil
import io
from unittest.mock import patch

class TestLumipyConfig(unittest.TestCase):

    test_base_dir = Path(tempfile.gettempdir()) / 'lumipy_cfg_tests'
    complex_token = 'ObfuscatedLVlsbkpFIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsTestTestTestwiaG9uZXljb21iLWxpbWl0ZWQtdGVzdGVyIiwibHVzaWQtYWRtaW4tY2xvbmUiLCJob25leWNvbWJob25leWNvbWItZGF0YS1wcm92aWRlci1jcm9zcy10ZW5hbnQtY3JlYXRvciJdLCJmYm4tY2xpZW50IjoiZmJuLWNpIiwiZmJuLXVzZXJ0eXBlIjoiU2VydmljZSIsImZibi11c2VyaWQiOiIwMHU2NHR1OGNwdzgwN2d1ZzJwNyIsImVtYWlsIjoiYW5kcmV3Lm1vcnJpc29uQGZpbmJvdXJuZS5jb20ifQ.qhZX-g9lMmSBoEMTRw1jJEkNI2gnFXVZX3tGH-_4VgakIUesGzimvWvZfAVUczu0HoCDQb7IiQAigf0O_6g_5tIxc1i_8ylajUoBARotDhN55w346wTX6IGoMx6R0mQXZrHqQ68mwzQD_cUe_JCckAsXUxoH8mHcItb_JKOSETwo8fqWl6nF9drCw4L3--0BGp3rpYEsfkcfzT2fYbV0WA3IDXe_GzpqrCW3n2IpzCVY0lWo1Wufxb6yfiwQrnJqp-AXDY3sAMCH-j0iRomiVnda4VYAwdgCICnvmq_V6PxXz0YoM4Vs48F90sY02EwZyWya2QLQ6PNY3YGohrgNbg'

    @classmethod
    def setUpClass(cls) -> None:
        if cls.test_base_dir.exists():
            shutil.rmtree(cls.test_base_dir)
        cls.test_base_dir.mkdir()

    def test_top_level_config_object(self):
        import lumipy as lm

        cfg = lm.config
        self.assertIsInstance(cfg, ConfigManager)

        self.assertEqual('.lumipy', cfg.hidden_dir)
        self.assertEqual('auth', cfg.filename)

        expected = Path.home() / cfg.hidden_dir / cfg.filename
        self.assertEqual(expected, cfg.cfg_file)

    def test_empty_file_creation_on_obj_creation(self):

        test_dir = self.test_base_dir / 'config0'
        cfg_path = test_dir / ConfigManager.hidden_dir / ConfigManager.filename

        # Make sure it's not there
        cfg_path.unlink(missing_ok=True)

        cfg = ConfigManager(test_dir)
        self.assertTrue(cfg_path.exists())
        self.assertEqual(0, len(cfg._read()))

        self.assertIn('No domain PATs configured. Add one with the config.add() method.', str(cfg))
        self.assertIn('Call config.show() to peek at part of the PATs', str(cfg))
        self.assertIn('No domain PATs configured. Add one with the config.add() method.', repr(cfg))
        self.assertIn('Call config.show() to peek at part of the PATs', repr(cfg))

    def test_add_domain_happy(self):

        test_dir = self.test_base_dir / 'config1'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-fake', self.complex_token)

        self.assertEqual(1, len(cfg._read()))
        self.assertEqual(cfg.creds('fbn-fake')['access_token'], self.complex_token)

        for s in ['fbn-fake', '[PAT hidden]', '(active)']:
            self.assertIn(s, str(cfg))
            self.assertIn(s, repr(cfg))

        cfg.add('fbn-fake', 'token2', overwrite=True)
        self.assertEqual(cfg.creds('fbn-fake')['access_token'], 'token2')

    def test_add_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config9'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-fake', 'token1')

        with self.assertRaises(ValueError) as ve:
            cfg.add('fbn-fake', 'token2')

        s = str(ve.exception)
        self.assertIn('Set overwrite=True to overwrite it.', s)

    def test_add_bad_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config9'
        cfg = ConfigManager(test_dir)

        with self.assertRaises(ValueError) as ve:
            cfg.add('bad domain', 'token')

        s = str(ve.exception)
        self.assertIn('Invalid domain provided: bad domain', s)

    def test_add_bad_pat_unhappy(self):

        test_dir = self.test_base_dir / 'config9'
        cfg = ConfigManager(test_dir)

        with self.assertRaises(ValueError) as ve:
            cfg.add('good-domain', 'bad token')

        s = str(ve.exception)
        self.assertIn('Invalid PAT', s)

    def test_switch_domain_happy(self):

        test_dir = self.test_base_dir / 'config2'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')

        self.assertEqual(2, len(cfg._read()))
        self.assertEqual('fbn-dom1', cfg.domain)
        cfg.domain = 'fbn-dom2'
        self.assertEqual('fbn-dom2', cfg.domain)

    def test_switch_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config3'
        cfg = ConfigManager(test_dir)

        with self.assertRaises(ValueError) as ve:
            cfg.domain = 'fbn-bad'

        s = str(ve.exception)
        self.assertIn('fbn-bad', s)
        self.assertIn('not found in config. You can add it with', s)
        self.assertIn('config.add("fbn-bad", <PAT>)', s)

    def test_get_domain(self):

        test_dir = self.test_base_dir / 'config4'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        self.assertIsNone(cfg.domain)

        cfg.add('fbn-dom1', 'token1')
        self.assertEqual('fbn-dom1', cfg.domain)

    def test_get_creds_happy(self):

        test_dir = self.test_base_dir / 'config5'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')

        c1 = cfg.creds()
        self.assertEqual('https://fbn-dom1.lusid.com/honeycomb', c1['api_url'])
        self.assertEqual('token1', c1['access_token'])

        c2 = cfg.creds('fbn-dom2')
        self.assertEqual('https://fbn-dom2.lusid.com/honeycomb', c2['api_url'])
        self.assertEqual('token2', c2['access_token'])

    def test_get_creds_unhappy(self):

        test_dir = self.test_base_dir / 'config6'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        with self.assertRaises(ValueError) as ve:
            cfg.creds('fbn-bad')

        s = str(ve.exception)
        self.assertIn('fbn-bad', s)
        self.assertIn('not found in config. You can add it with', s)
        self.assertIn('config.add("fbn-bad", <PAT>)', s)

    def test_delete_domain_happy(self):

        test_dir = self.test_base_dir / 'config7'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')
        cfg.add('fbn-dom2', 'token2')
        self.assertEqual(2, len(cfg._read()))

        cfg.delete('fbn-dom2')
        self.assertEqual(1, len(cfg._read()))

    def test_delete_domain_unhappy(self):

        test_dir = self.test_base_dir / 'config8'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))
        c0 = cfg.creds()
        self.assertIsInstance(c0, dict)
        self.assertEqual(0, len(c0))

        cfg.add('fbn-dom1', 'token1')

        with self.assertRaises(ValueError) as ve:
            cfg.delete('fbn-dom1')

        s = str(ve.exception)
        self.assertIn(
            "fbn-dom1 is the current active domain. Please switch to a different one or call deactivate() before "
            "deleting.",
            s
        )

        with self.assertRaises(ValueError) as ve:
            cfg.delete('fbn-bad')

        s = str(ve.exception)
        self.assertIn('fbn-bad', s)
        self.assertIn('not found in config. You can add it with', s)
        self.assertIn('config.add("fbn-bad", <PAT>)', s)

    def test_deactivate(self):

        test_dir = self.test_base_dir / 'config10'
        cfg = ConfigManager(test_dir)

        self.assertEqual(0, len(cfg._read()))

        cfg.deactivate()
        self.assertEqual(0, len(cfg._read()))

        cfg.add('fbn-dom1', 'abcdefg')
        cfg.add('fbn-dom2', 'hijklmn')

        self.assertEqual('fbn-dom1', cfg.domain)

        cfg.deactivate()
        self.assertIsNone(cfg.domain)

    def test_empty_config_if_file_does_not_exist(self):

        test_dir = self.test_base_dir / 'config11'
        cfg = ConfigManager(test_dir)
        shutil.rmtree(test_dir)

        self.assertFalse(cfg.cfg_file.exists())

        creds = cfg.creds()
        self.assertEqual(0, len(creds))

    def test_set_domain_happy(self):

        test_dir = self.test_base_dir / 'config12'
        cfg = ConfigManager(test_dir)

        cfg.add('fbn-dom', self.complex_token)
        self.assertEqual(1, len(cfg._read()))

        cfg.set('fbn-dom')
        self.assertEqual(1, len(cfg._read()))

    def test_set_domain_unhappy(self):
        test_dir = self.test_base_dir / 'config13'
        cfg = ConfigManager(test_dir)

        with self.assertRaises(ValueError) as ve:
            cfg.set('fbn-dom')

        s = str(ve.exception)
        self.assertIn(f'Domain fbn-dom not found in config. You can add it with config.add("fbn-dom", <PAT>).', s)

    def test_init_config_manager_permission_error(self):
        with patch.object(Path, "mkdir", side_effect=PermissionError("Mocked PermissionError")):
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                try:
                    _ = ConfigManager('config')
                except Exception as e:
                    self.fail(f"ConfigManager raised an error instead of handling it. Error: {e}")

            output = captured_output.getvalue()
            self.assertIn(
                "Warning: can't write config file to $HOME/.lumipy (Caught PermissionError). You will not be able to register and use PATs, so should use another auth method such as env vars or **kwargs.",
                output
            )


    def test_init_config_manager_os_error(self):
        with patch.object(Path, "mkdir", side_effect=OSError("Mocked OSError")):
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                try:
                    _ = ConfigManager('config')
                except Exception as e:
                    self.fail(f"ConfigManager raised an error instead of handling it. Error: {e}")

            output = captured_output.getvalue()
            self.assertIn(
                "Warning: can't write config file to $HOME/.lumipy (Caught OSError). You will not be able to register and use PATs, so should use another auth method such as env vars or **kwargs.",
                output
            )

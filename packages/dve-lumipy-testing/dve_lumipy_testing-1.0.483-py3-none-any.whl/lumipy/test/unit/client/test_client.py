import os
import unittest
from pathlib import Path
from lumipy.client import get_client


class TestLumipyClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.file_dir = os.path.dirname(os.path.abspath(__file__))

    def test_client_setup_with_secrets_file_access_token(self):
        api_secrets_file_path = Path(self.file_dir) / "fake_config.json"
        try:
            get_client(api_secrets_file=api_secrets_file_path)
        except Exception as e:
            self.fail(f"Failed to setup client. {e}")

    def test_client_setup_with_secrets_file_username_password(self):
        api_secrets_file_path = Path(self.file_dir) / "fake_config_no_access_token.json"
        try:
            get_client(api_secrets_file=api_secrets_file_path)
        except Exception as e:
            self.fail(f"Failed to setup client. {e}")

    def test_client_setup_not_a_valid_path_raises(self):
        with self.assertRaises(ValueError) as e:
            get_client(api_secrets_file=r"not_a_file.json")

        s = str(e.exception)
        self.assertIn("Secrets file: 'not_a_file.json' does not exist", s)

    def test_client_setup_with_args(self):
        try:
            get_client(
                token_url="https://example.com/token",
                api_url="https://api.example.com",
                username="user123",
                password="password123",
                client_id="client-id-123",
                client_secret="secret-xyz",
                app_name="ExampleApp",
                certificate_filename="/path/to/certificate.pem",
                access_token="access-token-abc",
                proxy_username="proxy_username",
                proxy_address="http://myproxy.com:8080"
            )
        except Exception as e:
            self.fail(f"Failed to setup client. {e}")

    def test_client_setup_with_bad_args_raises(self):
        # No PAT or password
        with self.assertRaises(ValueError):
            get_client(
                token_url="https://example.com/token",
                api_url="https://api.example.com",
                username="username",
                client_id="client-id-123",
                client_secret="secret-xyz",
                app_name="ExampleApp",
                certificate_filename="/path/to/certificate.pem",
            )

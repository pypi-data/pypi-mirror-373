import unittest
from unittest.mock import MagicMock

from cryptography.hazmat.primitives.asymmetric import rsa

from ms_salesforce_api.salesforce.Auth import SalesforceAuthenticator


class TestSalesforceAuthenticator(unittest.TestCase):
    def setUp(self):
        self.client_id = "dummy_client_id"
        self.username = "dummy_username"
        self.domain = "https://auth.example.com"
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.authenticator = SalesforceAuthenticator(
            client_id=self.client_id,
            username=self.username,
            domain=self.domain,
            private_key=self.private_key,
            audience="http://fake-login.salesforce.com",
            session_duration_hours=1,
        )

    def test_init(self):
        self.assertEqual(self.authenticator.client_id, self.client_id)
        self.assertEqual(self.authenticator.username, self.username)
        self.assertEqual(self.authenticator.private_key, self.private_key)
        self.assertEqual(
            self.authenticator.auth_url,
            "https://auth.example.com/services/oauth2/token",
        )

    def test_authenticate_success(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            "access_token": "dummy_access_token"
        }

        with unittest.mock.patch(
            "requests.post",
            return_value=response_mock,
        ) as post_mock:
            access_token = self.authenticator.authenticate()
            self.assertEqual(access_token, "dummy_access_token")

            post_mock.assert_called_once_with(
                f"{self.domain}/services/oauth2/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",  # noqa: E501
                    "assertion": self.authenticator.generate_token(),
                },
            )

    def test_authenticate_error(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid grant",
        }

        with unittest.mock.patch("requests.post", return_value=response_mock):
            access_token = self.authenticator.authenticate()
            self.assertIsNone(access_token)

    def test_authenticate_failed(self):
        response_mock = MagicMock()
        response_mock.status_code = 400

        with unittest.mock.patch("requests.post", return_value=response_mock):
            access_token = self.authenticator.authenticate()
            self.assertIsNone(access_token)

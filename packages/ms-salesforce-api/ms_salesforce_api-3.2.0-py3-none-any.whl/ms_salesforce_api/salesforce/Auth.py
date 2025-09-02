import logging

import requests

from ms_salesforce_api.salesforce.JWTGenerator import JWTGenerator


class SalesforceAuthenticator(JWTGenerator):
    def __init__(
        self,
        client_id,
        username,
        domain,
        private_key,
        audience,
        session_duration_hours,
    ):
        super().__init__(
            client_id,
            private_key,
            username,
            audience,
            session_duration_hours,
        )

        self.auth_url = f"{domain}/services/oauth2/token"

    def authenticate(self):
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": self.generate_token(),
        }

        response = requests.post(self.auth_url, data=payload)

        if response.status_code == 200:
            auth_data = response.json()

            if "access_token" in auth_data:
                return auth_data["access_token"]
            else:
                logging.error(
                    f"Authentication error: {auth_data.get('error', 'Unknown error')}"  # noqa: E501
                )
                logging.error(
                    f"Error description: {auth_data.get('error_description', 'No description provided')}"  # noqa: E501
                )
                return None
        else:
            logging.error(
                f"Authentication failed with status code: {response.status_code}"  # noqa: E501
            )
            return None

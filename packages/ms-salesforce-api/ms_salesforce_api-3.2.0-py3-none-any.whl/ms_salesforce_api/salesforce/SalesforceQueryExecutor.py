import logging
import time

import requests

from ms_salesforce_api.salesforce.Auth import SalesforceAuthenticator

DEFAULT_SALESFORCE_VERSION = "57.0"
SALESFORCE_QUERY_ENDPOINT = "services/data/v{}/query/"
MAX_RETRIES = 3
BACKOFF_FACTOR = 2


class SalesforceQueryExecutor(SalesforceAuthenticator):
    def __init__(
        self,
        client_id,
        username,
        domain,
        private_key,
        audience="https://login.salesforce.com",
        session_duration_hours=1,
        api_version=DEFAULT_SALESFORCE_VERSION,
    ):
        super().__init__(
            client_id,
            username,
            domain,
            private_key,
            audience,
            session_duration_hours,
        )
        self.endpoint = (
            f"{domain}/{SALESFORCE_QUERY_ENDPOINT.format(api_version)}"
        )
        self.domain = domain
        self.access_token = self.authenticate()

    def fetch_data(self, query: str):
        if not self.access_token:
            logging.error(
                "[ERROR - fetch_data]: Authentication failed, cannot fetch data"  # noqa: E501
            )
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}

        all_records = []
        next_url = f"{self.endpoint}?q={query}"

        while next_url:
            response = self._make_request(next_url, headers, 0)
            if response:
                data = response.json()
                all_records.extend(data.get("records", []))
                nextRecordsUrl = data.get("nextRecordsUrl", None)
                if nextRecordsUrl:
                    next_url = f"{self.domain}{nextRecordsUrl}"
                else:
                    next_url = None
            else:
                next_url = None

        return all_records

    def _make_request(self, url, headers, retry_count):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # raise exception if status is not 200

            return response
        except (
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
        ) as e:
            if retry_count >= MAX_RETRIES:
                logging.error(
                    f"[ERROR - _make_request]: Request failed after {MAX_RETRIES} attempts due to: {e}"  # noqa: E501
                )

                return None
            logging.warning(
                "[ERROR - _make_request]: Request timeout or too many redirects, retrying in 2 seconds"  # noqa: E501
            )
            time.sleep(BACKOFF_FACTOR**retry_count)

            return self._make_request(url, headers, retry_count + 1)
        except requests.exceptions.RequestException as e:
            logging.error(
                f"[ERROR - _make_request]: Request failed due to an unexpected error: {e}"  # noqa: E501
            )

            return None

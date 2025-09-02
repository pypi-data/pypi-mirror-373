import logging

from ms_salesforce_api.salesforce.api.account.constants import (
    DEFAULT_PROJECT_ACCOUNT_QUERY,
)
from ms_salesforce_api.salesforce.api.account.dto.AccountDTO import AccountDTO
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Account(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_PROJECT_ACCOUNT_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No accounts data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            accounts = [
                AccountDTO.from_salesforce_record(record) for record in data
            ]
            accounts_list = list(accounts)

            if format == "json":
                accounts_list = [
                    opportunity.to_dict() for opportunity in accounts_list
                ]

            return accounts_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all accounts: {e}"
            )
            return []

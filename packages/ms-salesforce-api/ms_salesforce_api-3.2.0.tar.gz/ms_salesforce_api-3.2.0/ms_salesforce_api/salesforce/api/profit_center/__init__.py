import logging

from ms_salesforce_api.salesforce.api.profit_center.constants import (
    DEFAULT_PROFIT_CENTER_QUERY,
)
from ms_salesforce_api.salesforce.api.profit_center.dto.ProfitCenterDTO import (  # noqa: E501
    ProfitCenterDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class ProfitCenter(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_PROFIT_CENTER_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No profit center data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            profit_centers = [
                ProfitCenterDTO.from_salesforce_record(record)
                for record in data
            ]
            profit_centers_list = list(profit_centers)

            if format == "json":
                profit_centers_list = [
                    opportunity.to_dict()
                    for opportunity in profit_centers_list
                ]

            return profit_centers_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all profit_centers: {e}"
            )
            return []

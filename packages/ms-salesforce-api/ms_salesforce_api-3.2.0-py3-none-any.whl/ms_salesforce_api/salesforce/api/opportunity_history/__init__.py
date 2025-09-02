import logging

from ms_salesforce_api.salesforce.api.opportunity_history.constants import (
    DEFAULT_ALL_OPPORTUNITIES_QUERY,
)
from ms_salesforce_api.salesforce.api.opportunity_history.dto.OpportunityDTO import (  # noqa: E501
    OpportunityHistoryDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Opportunity(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_ALL_OPPORTUNITIES_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No projects data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            opportunities = [
                OpportunityHistoryDTO.from_salesforce_record(record)
                for record in data
            ]
            opportunities_list = list(opportunities)

            if format == "json":
                opportunities_list = [
                    opportunity.to_dict() for opportunity in opportunities_list
                ]

            return opportunities_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all opportunities: {e}"
            )
            return []

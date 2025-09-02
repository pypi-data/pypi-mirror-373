import logging

from ms_salesforce_api.salesforce.api.lead.constants import DEFAULT_LEAD_QUERY
from ms_salesforce_api.salesforce.api.lead.dto.LeadDTO import (  # noqa: E501
    LeadDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Lead(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_LEAD_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No leads data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            leads = [LeadDTO.from_salesforce_record(record) for record in data]
            leads_list = list(leads)

            if format == "json":
                leads_list = [lead.to_dict() for lead in leads_list]

            return leads_list
        except Exception as e:
            logging.error(f"[ERROR - get_all]: Failed to get all leads: {e}")
            return []

import logging

from ms_salesforce_api.salesforce.api.opportunity_contact_role.constants import (  # noqa: E501
    DEFAULT_OPPORTUNITY_CONTACT_QUERY,
)
from ms_salesforce_api.salesforce.api.opportunity_contact_role.dto.OpportunityContactDTO import (  # noqa: E501
    OpportunityContactDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class OpportunityContactRole(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_OPPORTUNITY_CONTACT_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No contact data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            contacts = [
                OpportunityContactDTO.from_salesforce_record(record)
                for record in data
            ]
            contacts_list = list(contacts)

            if format == "json":
                contacts_list = [
                    contact.to_dict() for contact in contacts_list
                ]

            return contacts_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all contacts: {e}"
            )
            return []

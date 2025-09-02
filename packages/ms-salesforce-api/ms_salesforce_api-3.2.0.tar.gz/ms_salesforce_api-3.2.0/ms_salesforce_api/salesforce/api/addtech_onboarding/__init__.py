import logging

from ms_salesforce_api.salesforce.api.addtech_onboarding.constants import (
    DEFAULT_ADDTECH_ONBOARDING_QUERY,
)
from ms_salesforce_api.salesforce.api.addtech_onboarding.dto.AddTechOnboarding import (  # noqa: E501
    AddTechOnboardingDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class AddTechOboarding(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_ADDTECH_ONBOARDING_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No addtech onboarding data return from Salesforce API"  # noqa: E501
            )
            return []

        addtech_onboarding = [
            AddTechOnboardingDTO.from_salesforce_record(record)
            for record in data
        ]
        addtech_onboarding_list = list(addtech_onboarding)

        if format == "json":
            addtech_onboarding_list = [
                addtech.to_dict() for addtech in addtech_onboarding_list
            ]

        return addtech_onboarding_list
        try:
            pass
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all addtech_onboarding: {e}"
            )
            return []

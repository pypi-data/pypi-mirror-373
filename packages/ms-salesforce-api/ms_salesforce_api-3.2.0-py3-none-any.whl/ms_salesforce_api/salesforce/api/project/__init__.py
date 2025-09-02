import logging
from concurrent.futures import ThreadPoolExecutor

from ms_salesforce_api.salesforce.api.project.constants import (
    DEFAULT_PROJECT_BILLING_LINE_QUERY,
    DEFAULT_PROJECT_OPPORTUNITY_QUERY,
)
from ms_salesforce_api.salesforce.api.project.dto.BillingLineDTO import (
    BillingLineDTO,
)
from ms_salesforce_api.salesforce.api.project.dto.OpportunityDTO import (
    OpportunityDTO,
)
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Project(SalesforceQueryExecutor):
    def fetch_billing_lines(self, project_ids):
        billing_lines = []
        query = DEFAULT_PROJECT_BILLING_LINE_QUERY.format(
            project_id="','".join(project_ids)
        )

        data = self.fetch_data(query)
        if data is not None:
            billing_lines.extend(data)

        return billing_lines

    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        last_executed_at: str = None,
        query: str = DEFAULT_PROJECT_OPPORTUNITY_QUERY,
        format: str = "json",
    ):
        if last_executed_at:
            query = query + f"WHERE CreatedDate > {last_executed_at}"

        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No projects data return from Salesforce API"  # noqa: E501
            )
            return []

        opportunities = {
            record["Id"]: OpportunityDTO.from_salesforce_record(record)
            for record in data
        }

        project_ids = list(opportunities.keys())

        with ThreadPoolExecutor(max_workers=10) as executor:
            for project_id_batch in self.get_batches(
                project_ids,
                MAX_PROJECT_IDS_PER_QUERY,
            ):
                batch_results = list(
                    executor.map(
                        self.fetch_billing_lines,
                        [project_id_batch],
                    )
                )
                for billing_line_data in batch_results:
                    for record in billing_line_data:
                        project_id = record["Project_Line_Item__r"][
                            "Project__c"
                        ]
                        opportunity = opportunities.get(project_id)

                        billing_line_dto = (
                            BillingLineDTO.from_salesforce_record(
                                record,
                                opportunity.projectcode,
                            )
                        )

                        if opportunity is not None:
                            if not opportunity.billing_lines:
                                opportunity.billing_lines = []
                            opportunity.billing_lines.append(billing_line_dto)
        opportunities_list = list(opportunities.values())
        if format == "json":
            opportunities_list = [
                opportunity.to_dict() for opportunity in opportunities_list
            ]

        return opportunities_list

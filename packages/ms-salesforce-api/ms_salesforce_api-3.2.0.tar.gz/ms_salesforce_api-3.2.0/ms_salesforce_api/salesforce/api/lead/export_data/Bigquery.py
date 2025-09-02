import logging

from gc_google_services_api.bigquery import BigQueryManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BigQueryExporter:
    """
    Initializes the Bigquery exporter with the given project ID and dataset ID.

    Args:
        project_id (str): The ID of the Google Cloud project.
        dataset_id (str): The ID of the BigQuery dataset.
    """

    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = BigQueryManager(
            project_id=project_id,
            dataset_id=dataset_id,
        )
        self.batch_size = 200
        self.schemas = {
            "leads": {
                "id": "STRING",
                "account": "STRING",
                "account_fiscal_name": "STRING",
                "account_manager": "STRING",
                "address": "STRING",
                "billing_address": "STRING",
                "company": "STRING",
                "contact": "STRING",
                "description": "STRING",
                "pck_division": "STRING",
                "email": "STRING",
                "event_attendance": "BOOLEAN",
                "event_mame": "STRING",
                "first_human_interaction": "STRING",
                "first_meeting": "STRING",
                "has_events": "STRING",
                "help_from_nb_team_requested": "STRING",
                "monthly_adv_investing_amount": "STRING",
                "industry": "STRING",
                "invoicing_email": "STRING",
                "jira_task": "STRING",
                "jira_task_id": "STRING",
                "record_type_id": "STRING",
                "lead_source": "STRING",
                "lead_source_description": "STRING",
                "status": "STRING",
                "market_scope": "STRING",
                "meeting": "BOOLEAN",
                "message": "STRING",
                "mobile_phone": "STRING",
                "name": "STRING",
                "next_steps": "STRING",
                "opportunity_description": "STRING",
                "opportunity_name_Short": "STRING",
                "applicant_email": "STRING",
                "origin": "STRING",
                "primary_campaign_source": "STRING",
                "associated_services": "STRING",
                "risk_assessment": "STRING",
                "risk_assessment_date": "STRING",
                "title": "STRING",
                "website": "STRING",
                "created_date": "STRING",
            },
        }

        for table_name, table_schema in self.schemas.items():
            self.client.create_table_if_not_exists(table_name, table_schema)

    def _execute_query(self, query, log_id, default_error_value=None):
        custom_error_value = f"{log_id}_custom_error"

        result = self.client.execute_query(
            query,
            custom_error_value,
        )

        if result == custom_error_value:
            logging.error(
                f"[ERROR - _execute_query]: Error executing query for {log_id} in BigQuery."  # noqa: E501
            )
            result = default_error_value

        return result

    def export_data(self, profit_centers):
        self.client.load_massive_data(
            rows_to_insert=profit_centers,
            table_name="leads",
        )

    def delete_all_rows(self):
        table_names = self.schemas.keys()
        for table_name in table_names:
            delete_query_table = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table_name}` WHERE true"  # noqa: E501
            self._execute_query(
                query=delete_query_table,
                log_id=f"delete_table_{table_name}",
            )

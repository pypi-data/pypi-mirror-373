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
            project_id=project_id, dataset_id=dataset_id
        )
        self.batch_size = 200
        self.schemas = {
            "all_opportunity_new": {
                "opportunity_id": "STRING",
                "account_billing_country": "STRING",
                "account_owner": "STRING",
                "account_id": "STRING",
                "amount": "FLOAT",
                "amount_eur": "FLOAT",
                "campaign_id": "STRING",
                "close_month_formula": "DATE",
                "close_date": "DATE",
                "contact_id": "STRING",
                "curreny_iso_code": "STRING",
                "end_date": "DATE",
                "expected_revenue": "FLOAT",
                "fiscal": "STRING",
                "fiscal_quarter": "INTEGER",
                "fiscal_year": "DATE",
                "jira_default_name": "STRING",
                "ga_client_id": "STRING",
                "ga_track_id": "STRING",
                "ga_user_id": "FLOAT",
                "is_global": "BOOLEAN",
                "has_opportunity_lineitem": "BOOLEAN",
                "has_overdue_task": "BOOLEAN",
                "hasproposal": "BOOLEAN",
                "is_closed": "BOOLEAN",
                "is_won": "BOOLEAN",
                "jira_component_required": "BOOLEAN",
                "jira_estimated_work_load": "FLOAT",
                "jira_number": "STRING",
                "jira_work_load": "FLOAT",
                "jira_component_url": "STRING",
                "lead_id": "STRING",
                "lead_source": "STRING",
                "google_funding_opportunity": "STRING",
                "loss_reason": "STRING",
                "market_scope": "STRING",
                "ms_account_company_invoicing": "INTEGER",
                "ms_account_invoice_country_code": "STRING",
                "ms_company_origin": "STRING",
                "opportunity_name": "STRING",
                "opportunity_name_short": "STRING",
                "opportunity_requestor": "STRING",
                "owner_id": "STRING",
                "probability": "FLOAT",
                "record_type_id": "STRING",
                "roi_analysis_completed": "BOOLEAN",
                "associated_services": "STRING",
                "stage_name": "STRING",
                "tier_short": "STRING",
                "total_opportunity_quantity": "FLOAT",
                "start_date": "DATE",
                "year_created": "DATE",
                "lkp_project": "STRING",
                "created_date": "TIMESTAMP",
                "proposal_delivery_date": "TIMESTAMP",
                "record_type": "STRING",
                "owner_name": "STRING",
                "next_step": "STRING",
                "account_manager": "STRING",
                "company_invoicing": "STRING",
                "account_manager_email": "STRING",
                "company_invoicing_name": "STRING",
                "comments": "STRING",
                "payment_method": "STRING",
                "payment_tems": "STRING",
                "invoicing_email": "STRING",
                "is_google_funding": "BOOLEAN",
                "priority": "STRING",
                "owner_username_name": "STRING",
                "created_by": "STRING",
                "last_modified_by": "STRING",
                "finance_contact": "STRING",
                "converted_amount_eur": "FLOAT",
                "project_code": "STRING",
                "google_drive_link": "STRING",
                "project_status": "STRING",
                "pck_division": "STRING",
                "out_of_report": "BOOLEAN",
                "billing_info": "STRING",
                "parent_opportunity": "STRING",
                "project_name": "STRING",
            },
            "opportunity_line_item": {
                "opportunity_id": "STRING",
                "product_id": "STRING",
                "profit_center_name": "STRING",
                "country": "STRING",
                "product_name": "STRING",
                "quantity": "FLOAT",
                "unit_price": "FLOAT",
                "profit_center_is_active": "BOOLEAN",
                "profit_center_deactivation_date": "DATE",
                "profit_center_deactivation_reason": "STRING",
                "profit_center_lkp": "STRING",
                "profit_center_txt": "STRING",
                "description": "STRING",
                "start_date": "DATE",
                "end_date": "DATE",
                "total_price": "FLOAT",
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
                f"[ERROR - _execute_query]: Error executing query for {log_id} in BigQuery. ({query})"  # noqa: E203
            )
            result = default_error_value

        return result

    def export_data(self, opportunities):
        opporunity_line_items = []
        for opportunity in opportunities:
            if len(opportunity["opportunity_line_items"]) > 0:
                opporunity_line_items.extend(
                    opportunity["opportunity_line_items"]
                )

            opportunity.pop("opportunity_line_items", None)

        self.client.load_massive_data(
            rows_to_insert=opportunities,
            table_name="all_opportunity_new",
        )

        if opporunity_line_items:
            self.client.load_massive_data(
                rows_to_insert=opporunity_line_items,
                table_name="opportunity_line_item",
            )
        else:
            logging.warning("Any opportunity line items to store.")

    def delete_all_rows(self):
        table_names = self.schemas.keys()
        for table_name in table_names:
            delete_query_table = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table_name}` WHERE true"  # noqa: E203
            self._execute_query(
                query=delete_query_table,
                log_id=f"delete_table_{table_name}",
            )

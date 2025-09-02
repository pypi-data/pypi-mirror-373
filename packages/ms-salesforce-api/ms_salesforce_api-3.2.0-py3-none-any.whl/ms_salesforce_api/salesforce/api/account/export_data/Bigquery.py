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
            "all_accounts": {
                "id": "STRING",
                "accelerator": "BOOLEAN",
                "name": "STRING",
                "key_account": "BOOLEAN",
                "customer_account_assignment_group": "INTEGER",
                "customer_tax_category": "STRING",
                "customer_tax_classification": "INTEGER",
                "txt_sapid": "STRING",
                "business_function": "STRING",
                "tax_id_type": "STRING",
                "currency_iso_code": "STRING",
                "created_date": "TIMESTAMP",
                "tier": "STRING",
                "pec_email": "STRING",
                "phone": "STRING",
                "fax": "STRING",
                "website": "STRING",
                "cif": "STRING",
                "billing_country_code": "STRING",
                "business_name": "STRING",
                "billing_address": "STRING",
                "billing_city": "STRING",
                "billing_postalcode": "STRING",
                "billing_street": "STRING",
                "lkp_company_invoicing_business_name": "STRING",
                "lkp_company_invoicing_country": "STRING",
                "payment_terms": "STRING",
                "billing_state_code": "STRING",
                "mail_invoincing": "STRING",
                "invoincing_email": "STRING",
                "customer_group_id": "INTEGER",
                "customer_subgroup_id": "INTEGER",
                "customer_subgroup_name": "STRING",
                "customer_subgroup_dt_start": "DATE",
                "customer_subgroup_dt_end": "DATE",
                "customer_subgroup_bqid": "INTEGER",
                "customer_subgroup_owner_email": "STRING",
                "customer_group_name": "STRING",
                "customer_group_dt_start": "DATE",
                "customer_group_dt_end": "DATE",
                "customer_group_bqid": "INTEGER",
                "customer_group_mail_supervisor": "STRING",
                "customer_group_mail_owner": "STRING",
                "customer_group_pck_type": "STRING",
                "owner_email": "STRING",
                "type": "STRING",
                "industry": "STRING",
                "payment_method": "STRING",
                "risk_assessment": "STRING",
                "risk_assessment_date": "STRING",
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

    def export_data(self, accounts):
        self.client.load_massive_data(
            rows_to_insert=accounts,
            table_name="all_accounts",
        )

    def delete_all_rows(self):
        table_names = self.schemas.keys()
        for table_name in table_names:
            delete_query_table = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table_name}` WHERE true"  # noqa: E501
            self._execute_query(
                query=delete_query_table,
                log_id=f"delete_table_{table_name}",
            )

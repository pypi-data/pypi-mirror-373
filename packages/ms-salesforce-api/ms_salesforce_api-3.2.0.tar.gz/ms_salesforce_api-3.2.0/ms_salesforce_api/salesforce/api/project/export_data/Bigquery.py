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
            "projects": {
                "amount": "FLOAT",
                "controller_email": "STRING",
                "controller_sub_email": "STRING",
                "cost_center": "STRING",
                "created_at": "TIMESTAMP",
                "currency": "STRING",
                "invoicing_country_code": "STRING",
                "jira_task_url": "STRING",
                "last_updated_at": "TIMESTAMP",
                # "lead_source": "STRING",
                "operation_coordinator_email": "STRING",
                "operation_coordinator_sub_email": "STRING",
                "opportunity_name": "STRING",
                # "opportunity_percentage": "FLOAT",
                "profit_center": "INTEGER",
                "project_id": "STRING",
                "project_name": "STRING",
                "project_start_date": "DATE",
                "project_tier": "STRING",
                # "stage": "STRING",
                "autorenewal": "BOOLEAN",
                "comments": "STRING",
                "end_date": "DATE",
                "international_deparments": "BOOLEAN",
                "opportunity_extension": "STRING",
                "maintance_project": "BOOLEAN",
                "ms_project_id": "STRING",
                "operation_coordinator_name": "STRING",
                # "operation_coordinator_controller": "STRING",
                "operation_coordinator_sub": "STRING",
                "opportunity": "STRING",
                "periodicity": "STRING",
                "profitcenter": "STRING",
                "project_account": "STRING",
                "projectcode": "STRING",
                "revenue_details": "BOOLEAN",
                "status": "STRING",
                # "internal_comment": "STRING",
                # "rejection_reason": "STRING",
                "projectid": "STRING",
                "quote": "STRING",
                "opportunity_project_code": "STRING",
            },
            "billing_lines": {
                "billing_amount": "FLOAT",
                "billing_date": "DATE",
                "billing_period_ending_date": "DATE",
                "billing_period_starting_date": "DATE",
                "billing_plan_amount": "FLOAT",
                "billing_plan_billing_date": "DATE",
                "billing_plan_item": "INTEGER",
                "billing_plan_service_end_date": "DATE",
                "billing_plan_service_start_date": "DATE",
                "created_date": "TIMESTAMP",
                "currency": "STRING",
                "hourly_price": "FLOAT",
                "id": "STRING",
                "last_modified_date": "TIMESTAMP",
                "name": "STRING",
                "project_id": "STRING",
                "revenue_dedication": "FLOAT",
                "project_code": "STRING",
            },
            "project_line_items": {
                "country": "STRING",
                "created_date": "TIMESTAMP",
                "effort": "FLOAT",
                "ending_date": "DATE",
                "id": "STRING",
                "last_modified_date": "TIMESTAMP",
                "ms_pli_name": "STRING",
                "product_name": "STRING",
                "project_id": "STRING",
                "project_code": "STRING",
                "quantity": "FLOAT",
                "starting_date": "DATE",
                "total_price": "FLOAT",
                "unit_price": "FLOAT",
                "opportunity_project_code": "STRING",
            },
            "accounts": {
                "assigment_group": "INTEGER",
                "billing_address": "STRING",
                "billing_city": "STRING",
                "billing_country": "STRING",
                "billing_postal_code": "STRING",
                "billing_state_code": "STRING",
                "billing_street": "STRING",
                "business_function": "STRING",
                "business_name": "STRING",
                "cif": "STRING",
                "company_invoicing": "STRING",
                "created_date": "TIMESTAMP",
                "currency_code": "STRING",
                "fax": "STRING",
                "id": "STRING",
                "invoicing_email": "STRING",
                "mail_invoicing": "STRING",
                "name": "STRING",
                "office": "STRING",
                "payment_terms": "STRING",
                "pec_email": "STRING",
                "phone": "STRING",
                "project_id": "STRING",
                "project_code": "STRING",
                "sap_id": "STRING",
                "tax_category": "STRING",
                "tax_classification": "INTEGER",
                "tax_id_type": "STRING",
                "tier": "STRING",
                "website": "STRING",
                "customer_groupId": "INTEGER",
                "customer_subgroupId": "INTEGER",
            },
            "groups": {
                "project_id": "STRING",
                "project_code": "STRING",
                "groupid": "STRING",
                "name": "STRING",
                "start_date": "DATE",
                "end_date": "DATE",
                "bqid": "INTEGER",
                "pck_type": "STRING",
                "supervisor_email": "STRING",
                "owner_email": "STRING",
            },
            "subgroups": {
                "groupid": "STRING",
                "name": "STRING",
                "subgroupid": "STRING",
                "start_date": "DATE",
                "end_date": "DATE",
                "bqid": "INTEGER",
                "owner_email": "STRING",
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
                f"[ERROR - _execute_query]: Error executing query for {log_id} in BigQuery."
            )
            result = default_error_value

        return result

    def export_data(self, opportunities):
        account_data = []
        group_data = []
        subgroup_data = []
        project_line_items = []
        billing_line_data = []

        for opportunity in opportunities:
            if len(opportunity["project_line_items"]) > 0:
                project_line_items.extend(opportunity["project_line_items"])

            if len(opportunity["billing_lines"]) > 0:
                billing_line_data.extend(opportunity["billing_lines"])

            opportunity.pop("project_line_items", None)
            opportunity.pop("billing_lines", None)

            # Store account data
            opportunity_account_data = {
                "project_id": opportunity["project_id"],
                "project_code": opportunity["projectcode"],
            }
            opportunity_group_data = {
                "project_id": opportunity["project_id"],
                "project_code": opportunity["projectcode"],
            }
            opportunity_subgroup_data = {}
            opportunity_copy = opportunity.copy()
            for attr, value in opportunity_copy.items():
                if attr.startswith("account_"):
                    opportunity_account_data[attr[8:]] = value
                    opportunity.pop(attr, None)

                if attr.startswith("group_"):
                    opportunity_group_data[attr[6:]] = value
                    opportunity.pop(attr, None)

                if attr.startswith("subgroup_"):
                    opportunity_subgroup_data[attr[9:]] = value
                    opportunity.pop(attr, None)

            account_data.append(opportunity_account_data)
            group_data.append(opportunity_group_data)
            subgroup_data.append(opportunity_subgroup_data)

        self.client.load_massive_data(
            rows_to_insert=opportunities,
            table_name="projects",
        )
        self.client.load_massive_data(
            rows_to_insert=group_data,
            table_name="groups",
        )
        self.client.load_massive_data(
            rows_to_insert=subgroup_data,
            table_name="subgroups",
        )
        self.client.load_massive_data(
            rows_to_insert=account_data,
            table_name="accounts",
        )
        self.client.load_massive_data(
            rows_to_insert=project_line_items,
            table_name="project_line_items",
        )

        self.client.load_massive_data(
            rows_to_insert=billing_line_data,
            table_name="billing_lines",
        )

    def delete_all_rows(self):
        table_names = self.schemas.keys()
        for table_name in table_names:
            delete_query_table = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table_name}` WHERE true"
            self._execute_query(
                query=delete_query_table,
                log_id=f"delete_table_{table_name}",
            )

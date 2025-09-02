import unittest
from unittest.mock import MagicMock, patch

from psycopg2 import sql

from ..CloudSQL import CloudSQL


def compare_queries(query_strings, expected_queries):
    for query_string, expected_query in zip(query_strings, expected_queries):
        if not compare_query(query_string, expected_query):
            return False
    return True


def compare_query(query_string, expected_query):
    expected_elements = get_elements(expected_query)
    for element in expected_elements:
        if element not in query_string:
            return False
    return True


def get_elements(query):
    elements = []
    if isinstance(query, str):
        elements.append(query)
    elif isinstance(query, tuple):
        for item in query:
            elements.extend(get_elements(item))
    elif isinstance(query, list):
        for sublist in query:
            elements.extend(get_elements(sublist))
    return elements


class TestCloudSQL(unittest.TestCase):
    def setUp(self):
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        mock_connect = MagicMock(return_value=mock_connection)

        with patch("psycopg2.connect", mock_connect):
            self.cloudsql = CloudSQL("host", "user", "password", "dbname")

    @patch("psycopg2.connect")
    def test_export_data(self, mock_connect):
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value

        opportunities = [
            {
                "account_business_name": "ESMProjectAcc",
                "account_name": "ESMProjectAccount",
                "currency": "EUR",
                "amount": 0,
                "invoicing_country_code": "ES",
                "operation_coordinator_email": "test@test.com",
                "operation_coordinator_sub_email": "test@test.com",
                "created_at": "2020-07-14T12:55:56.000+0000",
                "last_updated_at": "2023-05-16T13:18:04.000+0000",
                "opportunity_name": "ESMOPP",
                "stage": "Qualification",
                "billing_country": "ES",
                "lead_source": "Other",
                "project_code": "ESMSEX00430",
                "project_id": "a003X000015kaPxQAI",
                "project_name": "ESMProject",
                "project_start_date": "2023-05-13",
                "controller_email": "test@test.com",
                "controller_sub_email": "test@test.com",
                "profit_center": None,
                "cost_center": None,
                "project_tier": "Unknown",
                "jira_task_url": "ESMSBD0001-11848",
                "opportunity_percentage": 10.0,
                "billing_lines": [
                    {
                        "id": "a0sAa0000004Lx7IAE",
                        "project_id": "a003X000015kaPxQAI",
                        "name": "BL-000320965",
                        "currency": "EUR",
                        "created_date": "2023-05-13T09:04:20.000+0000",
                        "last_modified_date": "2023-05-16T13:18:01.000+0000",
                        "billing_amount": 90.0,
                        "billing_date": "2023-05-13",
                        "billing_period_ending_date": "2023-05-27",
                        "billing_period_starting_date": "2023-05-13",
                        "hourly_price": None,
                        "revenue_dedication": None,
                        "billing_plan_amount": "90",
                        "billing_plan_billing_date": "2023-05-13",
                        "billing_plan_item": "12345",
                        "billing_plan_service_end_date": "2023-05-27",
                        "billing_plan_service_start_date": "2023-05-13",
                    }
                ],
                "project_line_items": [
                    {
                        "country": "Spain",
                        "created_date": "2023-05-13T09:03:14.000+0000",
                        "effort": "12",
                        "ending_date": "2023-05-27",
                        "id": "a0VAa000000fWbdMAE",
                        "last_modified_date": "2023-05-16T13:18:01.000+0000",
                        "ms_pli_name": "_MSEX00430",
                        "product_name": "ESM PRODUCT",
                        "quantity": 12.0,
                        "starting_date": "2023-05-13",
                        "total_price": 1080.0,
                        "unit_price": 90.0,
                    }
                ],
            }
        ]

        opportunity_fixed = [
            {
                "opportunity_name": "ESMOPP",
                "account_business_name": "ESMProjectAcc",
                "account_name": "ESMProjectAccount",
                "currency": "EUR",
                "amount": 0,
                "invoicing_country_code": "ES",
                "operation_coordinator_email": "test@test.com",
                "operation_coordinator_sub_email": "test@test.com",
                "created_at": "2020-07-14T12:55:56.000+0000",
                "last_updated_at": "2023-05-16T13:18:04.000+0000",
                "stage": "Qualification",
                "billing_country": "ES",
                "lead_source": "Other",
                "project_code": "ESMSEX00430",
                "project_id": "a003X000015kaPxQAI",
                "project_name": "ESMProject",
                "project_start_date": "2023-05-13",
                "controller_email": "test@test.com",
                "controller_sub_email": "test@test.com",
                "profit_center": None,
                "cost_center": None,
                "project_tier": "Unknown",
                "jira_task_url": "ESMSBD0001-11848",
                "opportunity_percentage": 10.0,
            }
        ]
        billing_fixed = [
            {
                "id": "BL-000320965",
                "project_id": "a003X000015kaPxQAI",
                "name": "Billing Line 1",
                "currency": "EUR",
                "created_date": "2023-05-13T09:04:20.000+0000",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "billing_amount": 90.0,
                "billing_date": "2023-05-13",
                "billing_period_ending_date": "2023-05-27",
                "billing_period_starting_date": "2023-05-13",
                "hourly_price": None,
                "revenue_dedication": None,
                "billing_plan_amount": "90",
                "billing_plan_billing_date": "2023-05-13",
                "billing_plan_item": "12345",
                "billing_plan_service_end_date": "2023-05-27",
                "billing_plan_service_start_date": "2023-05-13",
            }
        ]

        project_fixed = [
            {
                "country": "Spain",
                "created_date": "2023-05-13T09:03:14.000+0000",
                "effort": "12",
                "ending_date": "2023-05-27",
                "id": "a0VAa000000fWbdMAE",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "ms_pli_name": "_MSEX00430",
                "product_name": "ESM PRODUCT",
                "quantity": 12.0,
                "starting_date": "2023-05-13",
                "total_price": 1080.0,
                "unit_price": 90.0,
                "project_id": "a003X000015kaPxQAI",
            }
        ]

        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        mock_connect = MagicMock(return_value=mock_connection)

        with patch("psycopg2.connect", mock_connect):
            cloudsql = CloudSQL("host", "user", "password", "dbname")
            cloudsql.export_data(opportunities)

        mock_cursor.executemany.assert_called()
        self.assertEqual(
            mock_cursor.executemany.call_count, 4
        )  # 4 tables: Opportunities, BillingLines, ProjectLine, Accounts

        queries = [
            sql.SQL(str(call[0][0]))
            for call in mock_cursor.executemany.call_args_list
        ]
        query_strings = [
            query.as_string(mock_cursor.executemany.call_args[0][1])
            for query in queries
        ]

        expected_queries = [
            sql.SQL(
                """
                INSERT INTO Opportunities ({})
                VALUES ({})
                """
            ).format(
                sql.SQL(", ").join(
                    map(sql.Identifier, opportunity_fixed[0].keys())
                ),
                sql.SQL(", ").join(
                    map(
                        lambda x: sql.Placeholder(),
                        opportunity_fixed[0].keys(),
                    )
                ),
            ),
            sql.SQL(
                """
                INSERT INTO BillingLines ({})
                VALUES ({})
                """
            ).format(
                sql.SQL(", ").join(
                    map(sql.Identifier, billing_fixed[0].keys())
                ),
                sql.SQL(", ").join(
                    map(lambda x: sql.Placeholder(), billing_fixed[0].keys())
                ),
            ),
            sql.SQL(
                """
                INSERT INTO ProjectLine ({})
                VALUES ({})
                """
            ).format(
                sql.SQL(", ").join(
                    map(sql.Identifier, project_fixed[0].keys())
                ),
                sql.SQL(", ").join(
                    map(lambda x: sql.Placeholder(), project_fixed[0].keys())
                ),
            ),
        ]

        result = compare_queries(query_strings, expected_queries)

        self.assertEqual(result, True)

    def test_create_batches(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        batch_size = 3
        expected_batches = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

        batches = self.cloudsql._create_batches(data, batch_size)
        self.assertEqual(batches, expected_batches)

    def test_create_billing_lines(self):
        billing_lines = [
            {
                "id": "a0sAa0000004Lx7IAE",
                "name": "BL-000320965",
                "currency": "EUR",
                "created_date": "2023-05-13T09:04:20.000+0000",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "billing_amount": 90.0,
                "billing_date": "2023-05-13",
                "billing_period_ending_date": "2023-05-27",
                "billing_period_starting_date": "2023-05-13",
                "hourly_price": None,
                "revenue_dedication": None,
                "billing_plan_amount": "90",
                "billing_plan_billing_date": "2023-05-13",
                "billing_plan_item": "12345",
                "billing_plan_service_end_date": "2023-05-27",
                "billing_plan_service_start_date": "2023-05-13",
            }
        ]
        project_id = "a003X000015kaPxQAI"
        expected_billing_lines = [
            {
                "id": "a0sAa0000004Lx7IAE",
                "project_id": "a003X000015kaPxQAI",
                "name": "BL-000320965",
                "currency": "EUR",
                "created_date": "2023-05-13T09:04:20.000+0000",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "billing_amount": 90.0,
                "billing_date": "2023-05-13",
                "billing_period_ending_date": "2023-05-27",
                "billing_period_starting_date": "2023-05-13",
                "hourly_price": None,
                "revenue_dedication": None,
                "billing_plan_amount": "90",
                "billing_plan_billing_date": "2023-05-13",
                "billing_plan_item": "12345",
                "billing_plan_service_end_date": "2023-05-27",
                "billing_plan_service_start_date": "2023-05-13",
            }
        ]

        result = self.cloudsql._create_billing_lines(billing_lines, project_id)
        self.assertEqual(result, expected_billing_lines)

    def test_create_project_lines(self):
        project_lines = [
            {
                "country": "Spain",
                "created_date": "2023-05-13T09:03:14.000+0000",
                "effort": "12",
                "ending_date": "2023-05-27",
                "id": "a0VAa000000fWbdMAE",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "ms_pli_name": "_MSEX00430",
                "product_name": "ESM PRODUCT",
                "quantity": 12.0,
                "starting_date": "2023-05-13",
                "total_price": 1080.0,
                "unit_price": 90.0,
            }
        ]
        project_id = "a003X000015kaPxQAI"
        expected_project_lines = [
            {
                "country": "Spain",
                "created_date": "2023-05-13T09:03:14.000+0000",
                "effort": "12",
                "ending_date": "2023-05-27",
                "id": "a0VAa000000fWbdMAE",
                "last_modified_date": "2023-05-16T13:18:01.000+0000",
                "ms_pli_name": "_MSEX00430",
                "product_name": "ESM PRODUCT",
                "quantity": 12.0,
                "starting_date": "2023-05-13",
                "total_price": 1080.0,
                "unit_price": 90.0,
                "project_id": "a003X000015kaPxQAI",
            }
        ]

        result = self.cloudsql._create_project_lines(project_lines, project_id)
        self.assertEqual(result, expected_project_lines)

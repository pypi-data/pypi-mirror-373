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
                "attributes": {
                    "type": "Opportunity",
                    "url": "/services/data/v57.0/sobjects/Opportunity/006AX0000064R0gYAE",
                },
                "Id": "006AX0000064R0gYAE",
                "Opportunity_Name_Short__c": "Negativizar Trafico Web",
                "StageName": "Requirements Set",
                "LeadSource": "Crosselling/upselling",
                "Probability": 50.0,
                "Tier_Short__c": "T3",
                "JiraComponentURL__c": '<a href="https://makingscience.atlassian.net/browse/ESMSBD0001-24069" target="_blank">View Jira Task</a>',
                "OpportunityLineItems": {
                    "totalSize": 4,
                    "done": True,
                    "records": [
                        {
                            "attributes": {
                                "type": "OpportunityLineItem",
                                "url": "/services/data/v57.0/sobjects/OpportunityLineItem/00kAX000003zLMTYA2",
                            },
                            "Id": "00kAX000003zLMTYA2",
                            "Product2": {
                                "attributes": {
                                    "type": "Product2",
                                    "url": "/services/data/v57.0/sobjects/Product2/01t3X00000GzhWJQAZ",
                                },
                                "LKP_ProfitCenter__r": {
                                    "attributes": {
                                        "type": "ProfitCenter__c",
                                        "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006NPO2A2",
                                    },
                                    "Name": "Arch. & Infras. Eng. | Spain",
                                    "PCK_Country__c": "ES",
                                },
                            },
                        },
                        {
                            "attributes": {
                                "type": "OpportunityLineItem",
                                "url": "/services/data/v57.0/sobjects/OpportunityLineItem/00kAX000003zLRGYA2",
                            },
                            "Id": "00kAX000003zLRGYA2",
                            "Product2": {
                                "attributes": {
                                    "type": "Product2",
                                    "url": "/services/data/v57.0/sobjects/Product2/01t3X00000GzjWaQAJ",
                                },
                                "LKP_ProfitCenter__r": {
                                    "attributes": {
                                        "type": "ProfitCenter__c",
                                        "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006NRB2A2",
                                    },
                                    "Name": "Adtech International",
                                    "PCK_Country__c": "ES",
                                },
                            },
                        },
                        {
                            "attributes": {
                                "type": "OpportunityLineItem",
                                "url": "/services/data/v57.0/sobjects/OpportunityLineItem/00kAX000003zLVaYAM",
                            },
                            "Id": "00kAX000003zLVaYAM",
                            "Product2": {
                                "attributes": {
                                    "type": "Product2",
                                    "url": "/services/data/v57.0/sobjects/Product2/01t3X00000GzhVOQAZ",
                                },
                                "LKP_ProfitCenter__r": {
                                    "attributes": {
                                        "type": "ProfitCenter__c",
                                        "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006NRC2A2",
                                    },
                                    "Name": "Data International",
                                    "PCK_Country__c": "ES",
                                },
                            },
                        },
                        {
                            "attributes": {
                                "type": "OpportunityLineItem",
                                "url": "/services/data/v57.0/sobjects/OpportunityLineItem/00kAX000003zLTXYA2",
                            },
                            "Id": "00kAX000003zLTXYA2",
                            "Product2": {
                                "attributes": {
                                    "type": "Product2",
                                    "url": "/services/data/v57.0/sobjects/Product2/01tAX0000017ZLGYA2",
                                },
                                "LKP_ProfitCenter__r": {
                                    "attributes": {
                                        "type": "ProfitCenter__c",
                                        "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006NP82AM",
                                    },
                                    "Name": "DataOps | Spain",
                                    "PCK_Country__c": "ES",
                                },
                            },
                        },
                    ],
                },
            }
        ]

        opportunity_fixed = [
            {
                "jira_component_url": "<a "
                'href="https://makingscience.atlassian.net/browse/ESMSBD0001-24069" '
                'target="_blank">View Jira Task</a>',
                "lead_source": "Crosselling/upselling",
                "opportunity_id": "006AX0000064R0gYAE",
                "opportunity_line_items": [
                    {
                        "country": "ES",
                        "jira_task_url": "",
                        "opportunity_id": "006AX0000064R0gYAE",
                        "product_id": "",
                        "profit_center_name": "Arch. & Infras. Eng. | "
                        "Spain",
                    },
                    {
                        "country": "ES",
                        "jira_task_url": "",
                        "opportunity_id": "006AX0000064R0gYAE",
                        "product_id": "",
                        "profit_center_name": "Adtech International",
                    },
                    {
                        "country": "ES",
                        "jira_task_url": "",
                        "opportunity_id": "006AX0000064R0gYAE",
                        "product_id": "",
                        "profit_center_name": "Data International",
                    },
                    {
                        "country": "ES",
                        "jira_task_url": "",
                        "opportunity_id": "006AX0000064R0gYAE",
                        "product_id": "",
                        "profit_center_name": "DataOps | Spain",
                    },
                ],
                "opportunity_name_short": "Negativizar Trafico Web",
                "probability": 50.0,
                "stage_name": "Requirements Set",
                "tier_short": "T3",
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
            mock_cursor.executemany.call_count, 1
        )  # 1 table: All_Opportunity

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
                INSERT INTO all_opportunity ({})
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
        ]

        result = compare_queries(query_strings, expected_queries)

        self.assertEqual(result, True)

    def test_create_batches(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        batch_size = 3
        expected_batches = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

        batches = self.cloudsql._create_batches(data, batch_size)
        self.assertEqual(batches, expected_batches)

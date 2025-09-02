# flake8: noqa: E501
import unittest
from unittest.mock import patch

from ms_salesforce_api.salesforce.api.profit_center import (
    ProfitCenter,
    ProfitCenterDTO,
)

EXAMPLE_RESPONSE = [
    {
        "attributes": {
            "type": "ProfitCenter__c",
            "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006Lcc2AE",
        },
        "Id": "a1CAX0000006Lcc2AE",
        "Name": "Adtech Acceleration | Spain",
        "TXT_ProfitCenter__c": "200092",
        "PCK_Country__c": "ES",
        "DT_DeactivationDate__c": None,
        "TXT_DeactivationReason__c": None,
        "FRM_IsActive__c": True,
    },
]


def mock_fetch_data(query):
    return EXAMPLE_RESPONSE


class TestProfitCenter(unittest.TestCase):
    @patch(
        "ms_salesforce_api.salesforce.api.profit_center.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch.object(ProfitCenter, "fetch_data", side_effect=mock_fetch_data)
    def test_get_all(self, mock_make_request, mock_authenticate):
        mock_authenticate.return_value = "access_token"

        client_id = "client_id"
        username = "username"
        domain = "https://auth.example.com"
        private_key = "private_key"

        profit_center = ProfitCenter(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        profit_centers = profit_center.get_all(format="dto")
        profit_center = profit_centers[0]

        mock_make_request.assert_called()
        self.assertEqual(len(profit_centers), 1)
        self.assertIsInstance(profit_center, ProfitCenterDTO)
        self.assertDictEqual(
            profit_center.to_dict(),
            {
                "country": "ES",
                "deactivation_date": None,
                "deactivation_reason": None,
                "id": "a1CAX0000006Lcc2AE",
                "is_active": True,
                "name": "Adtech Acceleration | Spain",
                "txt_profit_center": "200092",
            },
        )

    @patch(
        "ms_salesforce_api.salesforce.api.profit_center.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch(
        "ms_salesforce_api.salesforce.api.profit_center.SalesforceQueryExecutor._make_request"  # noqa: E501
    )
    def test_get_all_empty_on_failure(
        self, mock_make_request, mock_authenticate
    ):
        mock_authenticate.return_value = "access_token"
        mock_make_request.return_value = None

        client_id = "client_id"
        username = "username"
        domain = "https://auth.example.com"
        private_key = "private_key"

        profit_center = ProfitCenter(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        query = "SELECT * FROM profit_center"

        profit_centers = profit_center.get_all(query=query)
        self.assertEqual(profit_centers, [])

        mock_make_request.assert_called()

# flake8: noqa: E501
import unittest
from unittest.mock import patch

from ms_salesforce_api.salesforce.api.product import Product, ProductDTO

EXAMPLE_RESPONSE = [
    {
        "attributes": {
            "type": "Product2",
            "url": "/services/data/v57.0/sobjects/Product2/01t3X00000G0zYFQAZ",
        },
        "Id": "01t3X00000G0zYFQAZ",
        "Name": "Dev. Front Fee DONOTUSE",
        "ProductCode": "Tech-DevF-Fee",
        "Description": None,
        "IsActive": False,
        "Family": None,
        "CurrencyIsoCode": "EUR",
        "ExternalDataSourceId": None,
        "QuantityUnitOfMeasure": "Hours",
        "IsDeleted": False,
        "IsArchived": False,
        "Product_Type__c": "Fee",
        "FRM_RecordId__c": "01t3X00000G0zYFQAZ",
        "LKP_ProfitCenter__c": None,
    },
]


def mock_fetch_data(query):
    return EXAMPLE_RESPONSE


class Testproduct(unittest.TestCase):
    @patch(
        "ms_salesforce_api.salesforce.api.product.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch.object(Product, "fetch_data", side_effect=mock_fetch_data)
    def test_get_all(self, mock_make_request, mock_authenticate):
        mock_authenticate.return_value = "access_token"

        client_id = "client_id"
        username = "username"
        domain = "https://auth.example.com"
        private_key = "private_key"

        product = Product(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        products = product.get_all(format="dto")
        product = products[0]

        mock_make_request.assert_called()
        self.assertEqual(len(products), 1)
        self.assertIsInstance(product, ProductDTO)
        self.assertDictEqual(
            product.to_dict(),
            {
                "currency_iso_code": "EUR",
                "description": None,
                "external_data_source_id": None,
                "family": None,
                "id": "01t3X00000G0zYFQAZ",
                "is_active": False,
                "is_archived": False,
                "is_deleted": False,
                "name": "Dev. Front Fee DONOTUSE",
                "product_code": "Tech-DevF-Fee",
                "product_type": "Fee",
                "profit_center_id": None,
                "quantity_unit_of_measure": "Hours",
                "record_id": "01t3X00000G0zYFQAZ",
            },
        )

    @patch(
        "ms_salesforce_api.salesforce.api.product.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch(
        "ms_salesforce_api.salesforce.api.product.SalesforceQueryExecutor._make_request"  # noqa: E501
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

        product = Product(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        query = "SELECT * FROM Product"

        products = product.get_all(query=query)
        self.assertEqual(products, [])

        mock_make_request.assert_called()

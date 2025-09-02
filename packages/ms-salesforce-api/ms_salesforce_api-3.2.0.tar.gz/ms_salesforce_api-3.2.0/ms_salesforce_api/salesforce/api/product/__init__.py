import logging

from ms_salesforce_api.salesforce.api.product.constants import (
    DEFAULT_PRODUCT_QUERY,
)
from ms_salesforce_api.salesforce.api.product.dto.ProductDTO import ProductDTO
from ms_salesforce_api.salesforce.SalesforceQueryExecutor import (
    SalesforceQueryExecutor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_PROJECT_IDS_PER_QUERY = 200


class Product(SalesforceQueryExecutor):
    def get_batches(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa: E203

    def get_all(
        self,
        query: str = DEFAULT_PRODUCT_QUERY,
        format: str = "json",
    ):
        data = self.fetch_data(query)
        if data is None:
            logging.error(
                "[ERROR - SalesforceAPI]: No products data return from Salesforce API"  # noqa: E501
            )
            return []

        try:
            products = [
                ProductDTO.from_salesforce_record(record) for record in data
            ]
            products_list = list(products)

            if format == "json":
                products_list = [
                    opportunity.to_dict() for opportunity in products_list
                ]

            return products_list
        except Exception as e:
            logging.error(
                f"[ERROR - get_all]: Failed to get all products: {e}"
            )
            return []

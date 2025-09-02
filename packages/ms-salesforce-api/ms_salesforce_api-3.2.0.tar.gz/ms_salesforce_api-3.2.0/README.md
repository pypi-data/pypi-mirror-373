# How to contribute
After clone repository

## 1.- Install dependencies
```bash
poetry install
```

## 2.- Run test
```bash
make test
```

## 3.- Run lint
```bash
make lint && make isort
```

## How to publish new version
Once we have done a merge of our Pull request and we have the updated master branch we can generate a new version. For them we have 3 commands that change the version of our library and generate the corresponding tag so that the Bitbucket pipeline starts and publishes our library automatically.

```bash
make release-patch
```

```bash
make release-minor
```

```bash
make release-major
```

# How works
This project provides an API for querying Salesforce opportunities data and transforming it into an easy-to-use format. The API is built upon the `SalesforceQueryExecutor` and `Project` classes, with the latter inheriting from `SalesforceQueryExecutor`.

## Installation

Make sure you have **Python 3.8+** installed. Then, install the required dependencies using `poetry`:

```bash
poetry install ms-salesforce-api
```

# Testing
To run the unit tests, simply execute the following command:

```bash
make test
```
This will run all the tests and display the results. Make sure that all tests pass before using the API in a production environment.

## Usage

First, import the necessary classes:

```python
from ms_salesforce_api.salesforce.project import Project
```

Then, initialize the `Project` class with your Salesforce credentials:

```python
project = Project(
    client_id="your_client_id",
    username="your_username",
    domain="your_domain",
    private_key="your_private_key",
    audience="https://login.salesforce.com", # Default value
    session_duration_hours=1, # Default value
    api_version='57.0',  # Default value
)
```

Now, you can call the get_all method with a query to get the opportunities data:

```python
opportunities = project.get_all()
```

The opportunities variable will contain an array of opportunity objects with the transformed data. For example:

```python
[
 {
    "account_assigment_group": None,
    "account_billing_address": "C/ XXX XXX, 8 Planta 9ª, 28020, Spain",
    "account_billing_city": None,
    "account_billing_country": "ES",
    "account_billing_postal_code": "28020",
    "account_billing_state_code": None,
    "account_billing_street": "C/ XXX XXX, 8 Planta 9ª",
    "account_business_function": "XXXX",
    "account_business_name": "XXXXXX",
    "account_cif": "ESXXXXXXX",
    "account_company_invoicing": "2411",
    "account_created_date": "2022-03-28T09:05:44.000+0000",
    "account_currency_code": "",
    "account_fax": None,
    "account_invoicing_email": None,
    "account_mail_invoicing": None,
    "account_name": "XXXXXXXX",
    "account_office": "XXXXXXXX",
    "account_payment_terms": "T030",
    "account_pec_email": None,
    "account_phone": None,
    "account_sap_id": "10001210",
    "account_tax_category": None,
    "account_tax_classification": None,
    "account_tax_id_type": "ES0",
    "account_tier": "T1",
    "account_website": None,
    "amount": 0,
    "billing_lines": [
        {
            "billing_amount": 274.33,
            "billing_date": "2022-01-31",
            "billing_period_ending_date": "2022-03-31",
            "billing_period_starting_date": "2022-01-01",
            "billing_plan_amount": "274.33",
            "billing_plan_billing_date": "2022-01-31",
            "billing_plan_item": "0",
            "billing_plan_service_end_date": "2022-03-31",
            "billing_plan_service_start_date": "2022-01-01",
            "created_date": "2022-07-08T10:07:08.000+0000",
            "currency": "EUR",
            "hourly_price": None,
            "id": "XXXXXXXXXXXX",
            "last_modified_date": "2023-05-04T12:24:25.000+0000",
            "name": "BL-XXXXXXXX",
            "project_id": "YYYYYYYYYYYYY",
            "revenue_dedication": None,
        }
    ],
    "controller_email": "employee@makingscience.com",
    "controller_sub_email": "",
    "cost_center": "0220001800",
    "created_at": "2021-10-06T14:35:18.000+0000",
    "currency": "EUR",
    "invoicing_country_code": "ES",
    "jira_task_url": "<a href=https://makingscience.atlassian.net/browse/ESMSBD0001-1080 target=_blank>View Jira Task</a>",
    "last_updated_at": "2023-06-08T11:22:55.000+0000",
    "lead_source": "Employee Referral",
    "operation_coordinator_email": "employee@makingscience.com",
    "operation_coordinator_sub_email": "",
    "opportunity_name": "Branding Campaign",
    "opportunity_percentage": 100.0,
    "profit_center": "200018",
    "project_code": "ESMSEX01652",
    "project_id": "a003X00001WS2YHQA1",
    "project_line_items": [
        {
            "country": "Spain",
            "created_date": "2022-05-05T12:28:48.000+0000",
            "effort": None,
            "ending_date": "2022-03-31",
            "id": "a0V7U000001OdiUUAS",
            "last_modified_date": "2023-06-08T11:20:42.000+0000",
            "ms_pli_name": "Omnichannel_ESMSEx01652_ES",
            "product_name": "Advertising Lead Gen Proj",
            "quantity": None,
            "starting_date": "2022-01-01",
            "total_price": 0.0,
            "unit_price": 2230.99,
        }
    ],
    "project_name": "BrandingCampaignPilotESMSEx01652",
    "project_start_date": "2021-12-01",
    "project_tier": "Unkown",
    "stage": "Closed Won",
}
]
```

You can customize the query as needed to retrieve different data from Salesforce.

```python
query = "SELECT Id, Name FROM Project WHERE Project.Id = 'ESMS0000'"

opportunities = project.get_all(query=query)
```

# Export data
This library allow to export all opportunities data to a external database such Postgres and BigQuery.
Podemos importar cualquiera de las clases:

```python

from ms_salesforce_api.salesforce.api.project.export_data.Bigquery import (
    BigQueryExporter,
)
```

o

```python

from ms_salesforce_api.salesforce.api.project.export_data.CloudSQL import (
    CloudSQL
)
```

Both classes, when initialized, are in charge of creating the databases and the tables to export the data in case they do not exist.

## BigQueryExporter

The Bigquery class provides functionalities to export data to Google BigQuery.

|   ℹ️   |   Información   |
|:------:|:--------------:|
|    | The "BigqueryExporter" class needs an environment variable named "**GOOGLE_SERVICE_ACCOUNT_CREDENTIALS**" to exist and its value must be the JSON of the **Service Account** that has permissions to write to **BigQuery** and must be in **base64**|


```python
class BigqueryExporter:
    def __init__(self, project_id: str, dataset_id: str):
        """
        Initializes the Bigquery exporter with the given project ID and dataset ID.

        Args:
            project_id (str): The ID of the Google Cloud project.
            dataset_id (str): The ID of the BigQuery dataset.
        """
```

#### Methods
* **export_data**(data: List[Dict[str, Any]]) -> None
Exports the provided data to BigQuery.

    * data (List[Dict[str, Any]]): This variable has the value of "opportunities" returned by the "get_all" method.


* **delete_all_rows**() -> None
Delete all data for each table (Opportunities, Accounts, Billing line and PLIs). In this way we can have the database updated at all times.


## CloudSQL

The CloudSQL class provides functionalities to interact with a Google Cloud SQL database.


Constructor

```python
class CloudSQL:
     def __init__(self, host, user, password, dbname, debug_mode=False):
        """
        Connect with a Postgres Database with the given
        host name, database name, username, and password.

        Args:
            host (str): The host name for the Postgres database.
            user (str): The username for accessing the database.
            password (str): The password for accessing the database.
            dbname (str): The name of the database.
        """
```

#### Methods

* **export_data**(data: List[Dict[str, Any]]) -> None
Exports the provided data to BigQuery.

    * data (List[Dict[str, Any]]): This variable has the value of "opportunities" returned by the "get_all" method.


* **delete_all_rows**() -> None
Delete all data for each table (Opportunities, Accounts, Billing line and PLIs). In this way we can have the database updated at all times.

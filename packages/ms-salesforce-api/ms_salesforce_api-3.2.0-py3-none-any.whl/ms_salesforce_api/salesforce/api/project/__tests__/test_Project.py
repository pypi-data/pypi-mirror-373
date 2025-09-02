# flake8: noqa: E501
import unittest
from unittest.mock import patch

from ms_salesforce_api.salesforce.api.project import OpportunityDTO, Project

EXAMPLE_RESPONSE = [
    {
        "attributes": {
            "type": "Project__c",
            "url": "/services/data/v57.0/sobjects/Project__c/a00AX000002DVi1YAG",
        },
        "CurrencyIsoCode": "EUR",
        "LKP_MSCompanyInvoicing__r": {
            "attributes": {
                "type": "MSCompany__c",
                "url": "/services/data/v57.0/sobjects/MSCompany__c/a1BAX000000uPr62AE",
            },
            "PCK_Prefix__c": "US",
        },
        "Operation_Coordinator__r": {
            "attributes": {
                "type": "Operation_Coordinator__c",
                "url": "/services/data/v57.0/sobjects/Operation_Coordinator__c/a0u7U000000PUGzQAO",
            },
            "Name": "employee5@test.com",
            "Controller__c": "employee4@test.com",
        },
        "Operation_Coordinator_Sub__r": {
            "attributes": {
                "type": "Operation_Coordinator__c",
                "url": "/services/data/v57.0/sobjects/Operation_Coordinator__c/a0u7U000000PUGzQAO",
            },
            "Name": "employee5@test.com",
            "Controller_SUB__c": "employee3@test.com",
        },
        "CreatedDate": "2022-08-01T08:53:12.000+0000",
        "LastModifiedDate": "2023-09-01T10:00:54.000+0000",
        "Opportunity__r": {
            "attributes": {
                "type": "Opportunity",
                "url": "/services/data/v57.0/sobjects/Opportunity/006AX000002WRmNYAW",
            },
            "Opportunity_Name_Short__c": "New Site Mapfre AAA",
            "StageName": "Closed Won",
            "LeadSource": "Crosselling/upselling",
            "Probability": 100.0,
            "Tier_Short__c": "Unkown",
            "JiraComponentURL__c": '<a href="https://makingscience.atlassian.net/browse/ESMSBD0001-7168" target="_blank">View Jira Task</a>',
        },
        "FRM_MSProjectCode__c": "USMSEX05508",
        "Name": "MapfreAAA",
        "Id": "a00AX000002DVi1YAG",
        "Start_Date__c": "2022-08-01",
        "LKP_ProfitCenter__r": {
            "attributes": {
                "type": "ProfitCenter__c",
                "url": "/services/data/v57.0/sobjects/ProfitCenter__c/a1CAX0000006NRE2A2",
            },
            "TXT_ProfitCenter__c": "200018",
        },
        "LKP_CostCenter__r": None,
        "Project_Account__r": {
            "attributes": {
                "type": "Account",
                "url": "/services/data/v57.0/sobjects/Account/0013X00002bEpOmQAK",
            },
            "Id": "0013X00002bEpOmQAK",
            "Name": "MAPFRE USA",
            "MS_Customer_Account_Assigment_Group__c": "03",
            "MS_Customer_Tax_Category__c": None,
            "MS_Customer_Tax_Classification__c": "0",
            "TXT_SAPId__c": "10000319",
            "ms_Business_Function__c": "BP03",
            "ms_TAX_id_Type__c": "US01",
            "CurrencyIsoCode": "EUR",
            "CreatedDate": "2020-03-18T15:32:15.000+0000",
            "Tier__c": "T1",
            "PEC_Email__c": None,
            "Phone": None,
            "Fax": None,
            "Website": None,
            "CIF__c": "042495247",
            "BillingCountryCode": "US",
            "Business_Name__c": "THE COMMERCE INSURANCE COMPANY",
            "BillingAddress": {
                "city": "Webster",
                "country": "United States",
                "countryCode": "US",
                "geocodeAccuracy": None,
                "latitude": None,
                "longitude": None,
                "postalCode": "01570",
                "state": "Maine",
                "stateCode": "ME",
                "street": "211 Main Street",
            },
            "BillingCity": "Webster",
            "BillingPostalCode": "01570",
            "BillingStreet": "211 Main Street",
            "LKP_MSCompanyInvoicing__r": {
                "attributes": {
                    "type": "MSCompany__c",
                    "url": "/services/data/v57.0/sobjects/MSCompany__c/a1BAX000000uPr62AE",
                },
                "PCK_Country__c": "US",
                "TXT_BusinessName__c": "Making Science LLC",
            },
            "Payment_Terms__c": "T060",
            "BillingStateCode": "ME",
            "MAIL_Invoicing__c": "client1@test.com",
            "Invoicing_Email__c": "client1@test.com",
            "BQ_CustomerGroupId__c": "1",
            "BQ_CustomerSubgroupID__c": "5",
            "LKP_CustomerSubgroup__r": {
                "attributes": {
                    "type": "CustomerSubgroup__c",
                    "url": "/services/data/v57.0/sobjects/CustomerSubgroup__c/a19AX0000004simYAA",
                },
                "LKP_CustomerGroup__r": {
                    "attributes": {
                        "type": "CustomerGroup__c",
                        "url": "/services/data/v57.0/sobjects/CustomerGroup__c/a0cAX000000TSWUYA4",
                    },
                    "Name": "MAPFRE",
                    "Id": "a0cAX000000TSWUYA4",
                    "DT_Start__c": "2023-06-01",
                    "DT_End__c": "2100-12-12",
                    "TXT_BQId__c": "1",
                    "PCK_Type__c": "Key Account",
                    "MAIL_Supervisor__c": "employee2@test.com",
                    "MAIL_Owner__c": "employee1@test.com",
                },
                "Id": "a19AX0000004simYAA",
                "Name": "MAPFRE USA",
                "DT_Start__c": "2023-06-01",
                "DT_End__c": "2100-12-12",
                "TXT_BQId__c": "5",
                "MAIL_Owner__c": None,
            },
        },
        "Project_Line_Items__r": {
            "totalSize": 2,
            "done": True,
            "records": [
                {
                    "attributes": {
                        "type": "ProjectLineItem__c",
                        "url": "/services/data/v57.0/sobjects/ProjectLineItem__c/a0VAX000000EE0b2AG",
                    },
                    "Id": "a0VAX000000EE0b2AG",
                    "CreatedDate": "2022-08-02T15:44:34.000+0000",
                    "LastModifiedDate": "2023-06-20T22:33:36.000+0000",
                    "Duration_months__c": 5.0,
                    "ProductNew__r": {
                        "attributes": {
                            "type": "Product2",
                            "url": "/services/data/v57.0/sobjects/Product2/01t3X00000GvwipQAB",
                        },
                        "Name": "UXUI Project",
                        "LKP_ProfitCenter__r": None,
                    },
                    "Starting_Date__c": "2022-08-01",
                    "LKP_CostCenter__r": None,
                    "Business_Unit__c": "UX/UI",
                    "Quantity__c": 516.0,
                    "UnitPrice__c": 65.0,
                    "Total_Price__c": 33540.0,
                    "Ending_Date__c": "2022-12-31",
                    "Department__c": None,
                    "Sales_Order_Item__c": 10.0,
                    "End_Date__c": "2022-12-31",
                    "Revenue_Type__c": "PS06",
                    "Effort__c": "516",
                    "Total_Billing_Amount_Billing_Lines__c": 33540.0,
                    "MS_PLI_Name__c": "USA_UX/UI Design_USMSEX05508",
                    "SapNetAmount__c": None,
                    "PCK_Prefix__c": None,
                },
                {
                    "attributes": {
                        "type": "ProjectLineItem__c",
                        "url": "/services/data/v57.0/sobjects/ProjectLineItem__c/a0VAX000000ELU52AO",
                    },
                    "Id": "a0VAX000000ELU52AO",
                    "CreatedDate": "2022-08-09T14:54:59.000+0000",
                    "LastModifiedDate": "2023-06-20T22:33:36.000+0000",
                    "Duration_months__c": 5.0,
                    "ProductNew__r": {
                        "attributes": {
                            "type": "Product2",
                            "url": "/services/data/v57.0/sobjects/Product2/01t3X00000GvwipQAB",
                        },
                        "Name": "UXUI Project",
                        "LKP_ProfitCenter__r": None,
                    },
                    "Starting_Date__c": "2022-08-01",
                    "LKP_CostCenter__r": None,
                    "Business_Unit__c": None,
                    "Quantity__c": 331.0,
                    "UnitPrice__c": 65.0,
                    "Total_Price__c": 21515.0,
                    "Ending_Date__c": "2022-12-31",
                    "Department__c": None,
                    "Sales_Order_Item__c": 20.0,
                    "End_Date__c": "2022-12-31",
                    "Revenue_Type__c": "PS06",
                    "Effort__c": "331",
                    "Total_Billing_Amount_Billing_Lines__c": 21515.0,
                    "MS_PLI_Name__c": "ES_UX/UI Design_USMSEX05508",
                    "SapNetAmount__c": None,
                    "PCK_Prefix__c": None,
                },
            ],
        },
    }
]
EXAMPLE_BILLING_LINES = [
    {
        "attributes": {
            "type": "Billing_Line__c",
            "url": "/services/data/v57.0/sobjects/Billing_Line__c/a0sAX000000I8lgYAC",
        },
        "Id": "a0sAX000000I8lgYAC",
        "Name": "BL-000175313",
        "Project_Line_Item__r": {
            "attributes": {
                "type": "ProjectLineItem__c",
                "url": "/services/data/v57.0/sobjects/ProjectLineItem__c/a0VAX000000EE0b2AG",
            },
            "Project__c": "a00AX000002DVi1YAG",
        },
        "CurrencyIsoCode": "USD",
        "CreatedDate": "2022-08-09T14:56:23.000+0000",
        "LastModifiedDate": "2022-10-16T18:56:34.000+0000",
        "Biling_Ammount__c": 6708.0,
        "Billing_Date__c": "2022-08-31",
        "Billing_Period_Ending_Date__c": "2022-08-31",
        "Billing_Period_Starting_Date__c": "2022-08-01",
        "Hourly_Price__c": 65.0,
        "Revenue_Dedication__c": 103.2,
        "BillingPlanAmount__c": "6708",
        "BillingPlanBillingDate__c": "2022-08-31",
        "BillingPlanItem__c": "1",
        "BillingPlanServiceEndDate__c": "2022-08-31",
        "BillingPlanServiceStartDate__c": "2022-08-01",
    },
]


def mock_fetch_data(query):
    if "Project_Line_Items__r" in query:
        return EXAMPLE_RESPONSE
    elif "Project_Line_Item__r.Project__c" in query:
        return EXAMPLE_BILLING_LINES
    else:
        return None


class TestProject(unittest.TestCase):
    @patch(
        "ms_salesforce_api.salesforce.api.project.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch.object(Project, "fetch_data", side_effect=mock_fetch_data)
    def test_get_all(self, mock_make_request, mock_authenticate):
        mock_authenticate.return_value = "access_token"

        client_id = "client_id"
        username = "username"
        domain = "https://auth.example.com"
        private_key = "private_key"

        project = Project(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        opportunities = project.get_all(format="dto")
        self.assertEqual(len(opportunities), 1)

        opportunity = opportunities[0]
        self.assertIsInstance(opportunity, OpportunityDTO)
        self.assertEqual(
            opportunity.account_business_name,
            "ESMProjectAcc",
        )
        self.assertEqual(opportunity.account_name, "ESMProjectAccount")
        self.assertEqual(opportunity.currency, "EUR")
        self.assertEqual(opportunity.amount, 0)
        self.assertEqual(opportunity.invoicing_country_code, "ES")
        self.assertEqual(
            opportunity.operation_coordinator_email,
            "jhon.doe@ext.makingscience.com",
        )
        self.assertEqual(
            opportunity.operation_coordinator_sub_email,
            "jhon.doe@ext.makingscience.com",
        )
        self.assertEqual(
            opportunity.created_at, "2020-07-14T12:55:56.000+0000"
        )
        self.assertEqual(
            opportunity.last_updated_at, "2023-05-16T13:18:04.000+0000"
        )
        self.assertEqual(opportunity.opportunity_name, "ESMOPP")
        self.assertEqual(opportunity.stage, "Qualification")
        self.assertEqual(opportunity.billing_country, "ES")
        self.assertEqual(opportunity.lead_source, "Other")
        self.assertEqual(opportunity.project_code, "ESMSEX00430")
        self.assertEqual(opportunity.project_id, "a003X000015kaPxQAI")
        self.assertEqual(opportunity.project_name, "ESMProject")
        self.assertEqual(opportunity.project_start_date, "2023-05-13")
        self.assertEqual(
            opportunity.controller_email, "jhon.doe@ext.makingscience.com"
        )
        self.assertEqual(
            opportunity.controller_sub_email, "jhon.doe@ext.makingscience.com"
        )
        self.assertIsNone(opportunity.profit_center)
        self.assertIsNone(opportunity.cost_center)
        self.assertEqual(opportunity.project_tier, "Unkown")
        self.assertEqual(
            opportunity.jira_task_url,
            '<a href="https://makingscience.atlassian.net/browse/ESMSBD0001-11848" target="_blank">View Jira Task</a>',  # noqa: E501
        )
        self.assertEqual(opportunity.opportunity_percentage, 10.0)
        self.assertEqual(len(opportunity.billing_lines), 1)
        billing_line = opportunity.billing_lines[0]

        self.assertEqual(billing_line.id, "a0sAa0000004Lx7IAE")
        self.assertEqual(billing_line.name, "BL-000320965")
        self.assertEqual(billing_line.project_id, "a003X000015kaPxQAI")
        self.assertEqual(billing_line.currency, "EUR")
        self.assertEqual(
            billing_line.created_date, "2023-05-13T09:04:20.000+0000"
        )
        self.assertEqual(
            billing_line.last_modified_date, "2023-05-13T09:04:20.000+0000"
        )
        self.assertEqual(billing_line.billing_amount, 90.0)
        self.assertEqual(billing_line.billing_date, "2023-05-13")
        self.assertEqual(billing_line.billing_period_ending_date, "2023-05-27")
        self.assertEqual(
            billing_line.billing_period_starting_date, "2023-05-13"
        )
        self.assertEqual(billing_line.hourly_price, None)
        self.assertEqual(billing_line.revenue_dedication, None)
        self.assertEqual(billing_line.billing_plan_amount, "90")
        self.assertEqual(billing_line.billing_plan_billing_date, "2023-05-13")
        self.assertEqual(billing_line.billing_plan_item, "12345")
        self.assertEqual(
            billing_line.billing_plan_service_end_date, "2023-05-27"
        )
        self.assertEqual(
            billing_line.billing_plan_service_start_date, "2023-05-13"
        )

        mock_make_request.assert_called()

    @patch(
        "ms_salesforce_api.salesforce.api.project.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch.object(Project, "fetch_data", side_effect=mock_fetch_data)
    def test_get_all(self, mock_make_request, mock_authenticate):
        mock_authenticate.return_value = "access_token"

        client_id = "client_id"
        username = "username"
        domain = "https://auth.example.com"
        private_key = "private_key"

        project = Project(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        opportunities = project.get_all()
        self.assertEqual(len(opportunities), 1)

        opportunity = opportunities[0]
        opportunity_result = {
            "account_assigment_group": "03",
            "account_billing_address": "211 Main Street, Webster, Maine, 01570, United "
            "States",
            "account_billing_city": "Webster",
            "account_billing_country": "US",
            "account_billing_postal_code": "01570",
            "account_billing_state_code": "ME",
            "account_billing_street": "211 Main Street",
            "account_business_function": "BP03",
            "account_business_name": "THE COMMERCE INSURANCE COMPANY",
            "account_cif": "042495247",
            "account_company_invoicing": "",
            "account_created_date": "2020-03-18 15:32:15",
            "account_currency_code": "EUR",
            "account_customer_groupId": "1",
            "account_customer_subgroupId": "5",
            "account_fax": None,
            "account_invoicing_email": "client1@test.com",
            "account_mail_invoicing": "client1@test.com",
            "account_name": "MAPFRE USA",
            "account_office": "Making Science LLC",
            "account_payment_terms": "T060",
            "account_pec_email": None,
            "account_phone": None,
            "account_sap_id": "10000319",
            "account_tax_category": None,
            "account_tax_classification": "0",
            "account_tax_id_type": "US01",
            "account_tier": "T1",
            "account_website": None,
            "amount": 0.0,
            "autorenewal": False,
            "billing_lines": [
                {
                    "billing_amount": 6708.0,
                    "billing_date": "2022-08-31",
                    "billing_period_ending_date": "2022-08-31",
                    "billing_period_starting_date": "2022-08-01",
                    "billing_plan_amount": "6708",
                    "billing_plan_billing_date": "2022-08-31",
                    "billing_plan_item": "1",
                    "billing_plan_service_end_date": "2022-08-31",
                    "billing_plan_service_start_date": "2022-08-01",
                    "created_date": "2022-08-09 14:56:23",
                    "currency": "USD",
                    "hourly_price": 65.0,
                    "id": "a0sAX000000I8lgYAC",
                    "last_modified_date": "2022-10-16 18:56:34",
                    "name": "BL-000175313",
                    "project_code": "",
                    "project_id": "a00AX000002DVi1YAG",
                    "revenue_dedication": 103.2,
                }
            ],
            "comments": "",
            "controller_email": "employee4@test.com",
            "controller_sub_email": "employee3@test.com",
            "cost_center": "",
            "created_at": "2022-08-01 08:53:12",
            "currency": "EUR",
            "end_date": "",
            "group_bqid": "1",
            "group_end_date": "2100-12-12",
            "group_groupid": "a0cAX000000TSWUYA4",
            "group_name": "MAPFRE",
            "group_owner_email": "employee1@test.com",
            "group_pck_type": "Key Account",
            "group_start_date": "2023-06-01",
            "group_supervisor_email": "employee2@test.com",
            "international_deparments": False,
            "invoicing_country_code": "US",
            "jira_task_url": "<a "
            "href=https://makingscience.atlassian.net/browse/ESMSBD0001-7168 "
            "target=_blank>View Jira Task</a>",
            "last_updated_at": "2023-09-01 10:00:54",
            "maintance_project": False,
            "ms_project_id": False,
            "operation_coordinator_email": "employee5@test.com",
            "operation_coordinator_name": "",
            "operation_coordinator_sub": "",
            "operation_coordinator_sub_email": "employee5@test.com",
            "opportunity": "",
            "opportunity_extension": "",
            "opportunity_name": "New Site Mapfre AAA",
            "opportunity_project_code": "",
            "periodicity": "",
            "profit_center": "200018",
            "profitcenter": "",
            "project_account": "",
            "project_id": "a00AX000002DVi1YAG",
            "project_line_items": [
                {
                    "country": None,
                    "created_date": "2022-08-02 15:44:34",
                    "effort": "516",
                    "ending_date": "2022-12-31",
                    "id": "a0VAX000000EE0b2AG",
                    "last_modified_date": "2023-06-20 22:33:36",
                    "ms_pli_name": "USA_UX/UI Design_USMSEX05508",
                    "opportunity_project_code": None,
                    "product_name": "UXUI Project",
                    "project_id": "a00AX000002DVi1YAG",
                    "quantity": 516.0,
                    "starting_date": "2022-08-01",
                    "total_price": 33540.0,
                    "unit_price": 65.0,
                },
                {
                    "country": None,
                    "created_date": "2022-08-09 14:54:59",
                    "effort": "331",
                    "ending_date": "2022-12-31",
                    "id": "a0VAX000000ELU52AO",
                    "last_modified_date": "2023-06-20 22:33:36",
                    "ms_pli_name": "ES_UX/UI Design_USMSEX05508",
                    "opportunity_project_code": None,
                    "product_name": "UXUI Project",
                    "project_id": "a00AX000002DVi1YAG",
                    "quantity": 331.0,
                    "starting_date": "2022-08-01",
                    "total_price": 21515.0,
                    "unit_price": 65.0,
                },
            ],
            "project_name": "MapfreAAA",
            "project_start_date": "2022-08-01",
            "project_tier": "Unkown",
            "projectcode": "",
            "quote": "",
            "revenue_details": "",
            "status": "",
            "subgroup_bqid": "5",
            "subgroup_end_date": "2100-12-12",
            "subgroup_groupid": "a0cAX000000TSWUYA4",
            "subgroup_name": "MAPFRE USA",
            "subgroup_owner_email": "employee1@test.com",
            "subgroup_start_date": "2023-06-01",
            "subgroup_subgroupid": "a19AX0000004simYAA",
        }
        self.assertIsInstance(opportunity, dict)

        self.assertDictEqual(
            opportunity,
            opportunity_result,
        )
        billing_line = opportunity["billing_lines"][0]
        self.assertDictEqual(
            billing_line,
            {
                "billing_amount": 6708.0,
                "billing_date": "2022-08-31",
                "billing_period_ending_date": "2022-08-31",
                "billing_period_starting_date": "2022-08-01",
                "billing_plan_amount": "6708",
                "billing_plan_billing_date": "2022-08-31",
                "billing_plan_item": "1",
                "billing_plan_service_end_date": "2022-08-31",
                "billing_plan_service_start_date": "2022-08-01",
                "created_date": "2022-08-09 14:56:23",
                "currency": "USD",
                "hourly_price": 65.0,
                "id": "a0sAX000000I8lgYAC",
                "last_modified_date": "2022-10-16 18:56:34",
                "name": "BL-000175313",
                "project_code": "",
                "project_id": "a00AX000002DVi1YAG",
                "revenue_dedication": 103.2,
            },
        )

        mock_make_request.assert_called()

    @patch(
        "ms_salesforce_api.salesforce.api.project.SalesforceQueryExecutor.authenticate"  # noqa: E501
    )
    @patch(
        "ms_salesforce_api.salesforce.api.project.SalesforceQueryExecutor._make_request"  # noqa: E501
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

        project = Project(
            client_id,
            username,
            domain,
            private_key,
            audience="https://login.salesforce.com",
        )
        query = "SELECT * FROM Opportunity"

        opportunities = project.get_all(query=query)
        self.assertEqual(opportunities, [])

        mock_make_request.assert_called()

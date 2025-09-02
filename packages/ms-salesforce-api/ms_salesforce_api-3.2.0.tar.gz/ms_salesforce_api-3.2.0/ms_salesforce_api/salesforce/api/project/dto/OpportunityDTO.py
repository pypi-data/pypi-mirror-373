from datetime import datetime

from ms_salesforce_api.salesforce.api.project.dto.ProjectLineItemDTO import (  # noqa: E501
    ProjectLineItemDTO,
)
from ms_salesforce_api.salesforce.helpers.string import normalize_value


class OpportunityDTO(object):
    def __init__(
        self,
        account_business_name,
        account_name,
        account_id,
        currency,
        amount,
        invoicing_country_code,
        operation_coordinator_email,
        operation_coordinator_sub_email,
        created_at,
        last_updated_at,
        opportunity_name,
        stage,
        account_billing_country,
        lead_source,
        project_id,
        project_name,
        project_start_date,
        controller_email,
        controller_sub_email,
        profit_center,
        cost_center,
        project_tier,
        jira_task_url,
        opportunity_percentage,
        opportunity_project_code,
        account_assigment_group,
        account_tax_category,
        account_tax_classification,
        account_sap_id,
        account_business_function,
        account_tax_id_type,
        account_currency_code,
        account_created_date,
        account_tier,
        account_pec_email,
        account_phone,
        account_fax,
        account_website,
        account_cif,
        account_billing_address,
        account_billing_city,
        account_billing_postal_code,
        account_billing_street,
        account_company_invoicing,
        account_office,
        account_payment_terms,
        account_billing_state_code,
        account_mail_invoicing,
        account_customer_groupId,
        account_customer_subgroupId,
        account_invoicing_email,
        group_name,
        group_id,
        group_start_date,
        group_end_date,
        group_bqid,
        group_pck_type,
        group_supervisor_email,
        group_owner_email,
        subgroup_owner_email,
        subgroup_name,
        subgroup_start_date,
        subgroup_end_date,
        subgroup_bqid,
        subgroup_id,
        autorenewal,
        comments,
        end_date,
        international_deparments,
        opportunity_extension,
        maintance_project,
        ms_project_id,
        operation_coordinator_name,
        operation_coordinator_controller,
        operation_coordinator_sub,
        opportunity,
        periodicity,
        profitcenter,
        project_account,
        projectcode,
        revenue_details,
        status,
        internal_comment,
        rejection_reason,
        quote,
        billing_lines=[],
        project_line_items=[],
    ):
        self.account_business_name = account_business_name
        self.account_name = account_name
        self.account_id = account_id
        self.currency = currency
        self.amount = amount
        self.invoicing_country_code = invoicing_country_code
        self.operation_coordinator_email = operation_coordinator_email
        self.operation_coordinator_sub_email = operation_coordinator_sub_email
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.opportunity_name = opportunity_name
        self.stage = stage
        self.account_billing_country = account_billing_country
        self.lead_source = lead_source
        self.project_id = project_id
        self.project_name = project_name
        self.project_start_date = project_start_date
        self.controller_email = controller_email
        self.controller_sub_email = controller_sub_email
        self.profit_center = profit_center
        self.cost_center = cost_center
        self.project_tier = project_tier
        self.jira_task_url = jira_task_url
        self.opportunity_project_code = opportunity_project_code
        self.opportunity_percentage = opportunity_percentage
        self.billing_lines = billing_lines
        self.project_line_items = project_line_items
        self.account_assigment_group = account_assigment_group
        self.account_tax_category = account_tax_category
        self.account_tax_classification = account_tax_classification
        self.account_sap_id = account_sap_id
        self.account_business_function = account_business_function
        self.account_tax_id_type = account_tax_id_type
        self.account_currency_code = account_currency_code
        self.account_created_date = account_created_date
        self.account_tier = account_tier
        self.account_pec_email = account_pec_email
        self.account_phone = account_phone
        self.account_fax = account_fax
        self.account_website = account_website
        self.account_cif = account_cif
        self.account_billing_address = account_billing_address
        self.account_billing_city = account_billing_city
        self.account_billing_postal_code = account_billing_postal_code
        self.account_billing_street = account_billing_street
        self.account_company_invoicing = account_company_invoicing
        self.account_office = account_office
        self.account_payment_terms = account_payment_terms
        self.account_billing_state_code = account_billing_state_code
        self.account_mail_invoicing = account_mail_invoicing
        self.account_customer_groupId = account_customer_groupId
        self.account_customer_subgroupId = account_customer_subgroupId
        self.account_invoicing_email = account_invoicing_email
        self.group_name = group_name
        self.group_id = group_id
        self.group_start_date = group_start_date
        self.group_end_date = group_end_date
        self.group_bqid = group_bqid
        self.group_pck_type = group_pck_type
        self.group_supervisor_email = group_supervisor_email
        self.group_owner_email = group_owner_email
        self.subgroup_owner_email = subgroup_owner_email
        self.subgroup_name = subgroup_name
        self.subgroup_start_date = subgroup_start_date
        self.subgroup_end_date = subgroup_end_date
        self.subgroup_bqid = subgroup_bqid
        self.subgroup_id = subgroup_id
        self.autorenewal = autorenewal
        self.comments = comments
        self.end_date = end_date
        self.international_deparments = international_deparments
        self.opportunity_extension = opportunity_extension
        self.maintance_project = maintance_project
        self.ms_project_id = ms_project_id
        self.operation_coordinator_name = operation_coordinator_name
        self.operation_coordinator_controller = (
            operation_coordinator_controller
        )
        self.operation_coordinator_sub = operation_coordinator_sub
        self.opportunity = opportunity
        self.periodicity = periodicity
        self.profitcenter = profitcenter
        self.project_account = project_account
        self.projectcode = projectcode
        self.revenue_details = revenue_details
        self.status = status
        self.internal_comment = internal_comment
        self.rejection_reason = rejection_reason
        self.quote = quote

    @staticmethod
    def from_salesforce_record(record):
        project_line_items = (
            [
                ProjectLineItemDTO.from_salesforce_record(item, record["Id"])
                for item in record.get("Project_Line_Items__r", {}).get(
                    "records", []
                )
            ]
            if record.get("Project_Line_Items__r")
            else []
        )

        def _get_account_business_name():
            try:
                return normalize_value(
                    record["Project_Account__r"]["Business_Name__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_name():
            try:
                return normalize_value(record["Project_Account__r"]["Name"])
            except (TypeError, KeyError):
                return ""

        def _get_account_id():
            try:
                return record["Project_Account__r"]["Id"]
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_country():
            try:
                return record["Project_Account__r"]["BillingCountryCode"]
            except (TypeError, KeyError):
                return ""

        def _get_country_code():
            try:
                return record["LKP_MSCompanyInvoicing__r"]["PCK_Prefix__c"]
            except (TypeError, KeyError):
                return ""

        def _get_account_assigment_group():
            try:
                return normalize_value(
                    record["Project_Account__r"][
                        "MS_Customer_Account_Assigment_Group__c"
                    ]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_tax_category():
            try:
                return normalize_value(
                    record["Project_Account__r"]["MS_Customer_Tax_Category__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_tax_classification():
            try:
                return normalize_value(
                    record["Project_Account__r"][
                        "MS_Customer_Tax_Classification__c"
                    ]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_sap_id():
            try:
                return normalize_value(
                    record["Project_Account__r"]["TXT_SAPId__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_business_function():
            try:
                return normalize_value(
                    record["Project_Account__r"]["ms_Business_Function__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_tax_id_type():
            try:
                return record["Project_Account__r"]["ms_TAX_id_Type__c"]
            except (TypeError, KeyError):
                return ""

        def _get_account_currency_code():
            try:
                return record["Project_Account__r"]["CurrencyIsoCode"]
            except (TypeError, KeyError):
                return ""

        def _get_account_created_date():
            try:
                dt = datetime.strptime(
                    record["Project_Account__r"]["CreatedDate"],
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )

                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except (TypeError, KeyError):
                return ""

        def _get_account_tier():
            try:
                return normalize_value(record["Project_Account__r"]["Tier__c"])
            except (TypeError, KeyError):
                return ""

        def _get_account_pec_email():
            try:
                return normalize_value(
                    record["Project_Account__r"]["PEC_Email__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_phone():
            try:
                return normalize_value(record["Project_Account__r"]["Phone"])
            except (TypeError, KeyError):
                return ""

        def _get_account_fax():
            try:
                return normalize_value(record["Project_Account__r"]["Fax"])
            except (TypeError, KeyError):
                return ""

        def _get_account_website():
            try:
                return normalize_value(record["Project_Account__r"]["Website"])
            except (TypeError, KeyError):
                return ""

        def _get_account_cif():
            try:
                return normalize_value(record["Project_Account__r"]["CIF__c"])
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_address():
            def build_address(location_dict):
                """
                Construct a string representation of an address from a
                dictionary.

                :param location_dict: a dictionary containing location
                information.
                :return: a string representing the address.
                """
                address_components = []

                for field in [
                    "street",
                    "city",
                    "state",
                    "postalCode",
                    "country",
                ]:
                    if field in location_dict and location_dict.get(field, ""):
                        address_components.append(location_dict[field])

                address = ", ".join(address_components)

                return normalize_value(address)

            try:
                return build_address(
                    record["Project_Account__r"]["BillingAddress"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_city():
            try:
                return record["Project_Account__r"]["BillingCity"]
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_postal_code():
            try:
                return record["Project_Account__r"]["BillingPostalCode"]
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_street():
            try:
                return normalize_value(
                    record["Project_Account__r"]["BillingStreet"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_company_invoicing():
            try:
                return normalize_value(
                    record["Project_Account__r"]["LKP_MSCompanyInvoicing__r"][
                        "PCK_Prefix__c"
                    ]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_office():
            try:
                return normalize_value(
                    record["Project_Account__r"]["LKP_MSCompanyInvoicing__r"][
                        "TXT_BusinessName__c"
                    ]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_payment_terms():
            try:
                return normalize_value(
                    record["Project_Account__r"]["Payment_Terms__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_billing_state_code():
            try:
                return record["Project_Account__r"]["BillingStateCode"]
            except (TypeError, KeyError):
                return ""

        def _get_account_mail_invoicing():
            try:
                return normalize_value(
                    record["Project_Account__r"]["MAIL_Invoicing__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_account_invoicing_email():
            try:
                email = record["Project_Account__r"]["Invoicing_Email__c"]
                if email:
                    return normalize_value(email)
            except (TypeError, KeyError):
                return ""

        def _get_account_customer_groupid():
            try:
                data = record["Project_Account__r"]["BQ_CustomerGroupId__c"]
                if data:
                    return normalize_value(data)
            except (TypeError, KeyError):
                return ""

        def _get_account_customer_subgroupid():
            try:
                data = record["Project_Account__r"]["BQ_CustomerSubgroupID__c"]
                if data:
                    return normalize_value(data)
            except (TypeError, KeyError):
                return ""

        def _get_operation_coordinator_email():
            try:
                return normalize_value(
                    record["Operation_Coordinator__r"]["Name"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_operation_coordinator_sub_email():
            try:
                return normalize_value(
                    record["Operation_Coordinator_Sub__r"]["Name"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_opportunity_name():
            try:
                return normalize_value(
                    record["Opportunity__r"]["Opportunity_Name_Short__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_stage():
            try:
                return normalize_value(record["Opportunity__r"]["StageName"])
            except (TypeError, KeyError):
                return ""

        def _get_lead_source():
            try:
                return normalize_value(record["Opportunity__r"]["LeadSource"])
            except (TypeError, KeyError):
                return ""

        def _get_controller_email():
            try:
                return normalize_value(
                    record["Operation_Coordinator__r"]["Controller__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_controller_sub_email():
            try:
                return normalize_value(
                    record["Operation_Coordinator_Sub__r"]["Controller_SUB__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_profit_center():
            try:
                return normalize_value(
                    record["LKP_ProfitCenter__r"]["TXT_ProfitCenter__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_cost_center():
            try:
                return normalize_value(record["LKP_CostCenter__r"]["Name"])
            except (TypeError, KeyError):
                return ""

        def _get_project_tier():
            try:
                return normalize_value(
                    record["Opportunity__r"]["Tier_Short__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_jira_task_url():
            try:
                return normalize_value(
                    record["Opportunity__r"]["JiraComponentURL__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_opportunity_percentage():
            try:
                return normalize_value(record["Opportunity__r"]["Probability"])
            except (TypeError, KeyError):
                return ""

        def _get_opportunity_project_code():
            try:
                return normalize_value(
                    record["Opportunity__r"]["FRM_ProjectCode__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_group_name():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["Name"]
            except (TypeError, KeyError):
                return ""

        def _get_group_id():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["Id"]
            except (TypeError, KeyError):
                return ""

        def _get_group_start():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["DT_Start__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_end():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["DT_End__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_bqid():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["TXT_BQId__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_pck_type():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["PCK_Type__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_supervisor_email():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["MAIL_Supervisor__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_owner_email():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["MAIL_Owner__c"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_owner_emial():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["MAIL_Owner__c"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_name():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "Name"
                ]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_id():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "Id"
                ]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_start():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "DT_Start__c"
                ]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_end():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "DT_End__c"
                ]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_bqid():
            try:
                return record["Project_Account__r"]["LKP_CustomerSubgroup__r"][
                    "TXT_BQId__c"
                ]
            except (TypeError, KeyError):
                return ""

        def _get_autorenewal():
            try:
                return record["Autorenewal__c"]
            except KeyError:
                return False

        def _get_comments():
            try:
                return record["Comments__c"]
            except KeyError:
                return ""

        def _get_end_date():
            try:
                return record["End_Date__c"]
            except KeyError:
                return ""

        def _get_international_deparments():
            try:
                return record["International_Departments__c"]
            except KeyError:
                return False

        def _get_opportunity_extension():
            try:
                return record["LKP_OpportunityExtension__c"]
            except KeyError:
                return ""

        def _get_maintance_project():
            try:
                return record["Maintenance_project__c"]
            except KeyError:
                return False

        def _get_ms_project_id():
            try:
                return record["MS_Project_Id__c"]
            except KeyError:
                return False

        def _get_operation_coordinator_name():
            try:
                return record["Operation_Coordinator__c"]["Name"]
            except (KeyError, TypeError):
                return ""

        def _get_operation_coordinator_controller():
            try:
                return record["Operation_Coordinator__c"]["Controller__c"]
            except (KeyError, TypeError):
                return ""

        def _get_operation_coordinator_sub():
            try:
                return record["Operation_Coordinator_Sub__c"]
            except KeyError:
                return ""

        def _get_opportunity():
            try:
                return record["Opportunity__c"]
            except KeyError:
                return ""

        def _get_periodicity():
            try:
                return record["Periodicity__c"]
            except KeyError:
                return ""

        def _get_profitcenter():
            try:
                return record["LKP_ProfitCenter__c"]
            except KeyError:
                return ""

        def _get_project_account():
            try:
                return record["Project_Account__c"]
            except KeyError:
                return ""

        def _get_project_code():
            try:
                return record["Project_Code__c"]
            except KeyError:
                return ""

        def _get_quote():
            try:
                return record["Quote__c"]
            except KeyError:
                return ""

        def _get_revenue_details():
            try:
                return record["Revenue_Details__c"]
            except KeyError:
                return ""

        def _get_status():
            try:
                return record["Status__c"]
            except KeyError:
                return ""

        def _get_internal_comment():
            try:
                return record["TXT_InternalComment__c"]
            except KeyError:
                return ""

        def _get_rejection_reason():
            try:
                return record["TXT_RejectionReason__c"]
            except KeyError:
                return ""

        def _parse_created_date(created_date):
            try:
                dt = datetime.strptime(
                    created_date,
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                )

                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return ""

        return OpportunityDTO(
            account_business_name=_get_account_business_name(),
            account_name=_get_account_name(),
            account_id=_get_account_id(),
            currency=record["CurrencyIsoCode"],
            amount=record.get("RU_TotalAmount__c", 0.0),
            invoicing_country_code=_get_country_code(),
            operation_coordinator_email=_get_operation_coordinator_email(),
            operation_coordinator_sub_email=_get_operation_coordinator_sub_email(),  # noqa: E501
            created_at=_parse_created_date(record["CreatedDate"]),
            last_updated_at=_parse_created_date(record["LastModifiedDate"]),
            opportunity_name=_get_opportunity_name(),
            stage=_get_stage(),
            account_billing_country=_get_account_billing_country(),
            lead_source=_get_lead_source(),
            project_id=record["Id"],
            project_name=record["Name"],
            project_start_date=record["Start_Date__c"],
            controller_email=_get_controller_email(),
            controller_sub_email=_get_controller_sub_email(),
            profit_center=_get_profit_center(),
            cost_center=_get_cost_center(),
            project_tier=_get_project_tier(),
            jira_task_url=_get_jira_task_url(),
            opportunity_percentage=_get_opportunity_percentage(),
            opportunity_project_code=_get_opportunity_project_code(),
            project_line_items=project_line_items,
            account_assigment_group=_get_account_assigment_group(),
            account_tax_category=_get_account_tax_category(),
            account_tax_classification=_get_account_tax_classification(),
            account_sap_id=_get_account_sap_id(),
            account_business_function=_get_account_business_function(),
            account_tax_id_type=_get_account_tax_id_type(),
            account_currency_code=_get_account_currency_code(),
            account_created_date=_get_account_created_date(),
            account_tier=_get_account_tier(),
            account_pec_email=_get_account_pec_email(),
            account_phone=_get_account_phone(),
            account_fax=_get_account_fax(),
            account_website=_get_account_website(),
            account_cif=_get_account_cif(),
            account_billing_address=_get_account_billing_address(),
            account_billing_city=_get_account_billing_city(),
            account_billing_postal_code=_get_account_billing_postal_code(),
            account_billing_street=_get_account_billing_street(),
            account_company_invoicing=_get_account_company_invoicing(),
            account_office=_get_account_office(),
            account_payment_terms=_get_account_payment_terms(),
            account_billing_state_code=_get_account_billing_state_code(),
            account_mail_invoicing=_get_account_mail_invoicing(),
            account_invoicing_email=_get_account_invoicing_email(),
            account_customer_groupId=_get_account_customer_groupid(),
            account_customer_subgroupId=_get_account_customer_subgroupid(),
            group_name=_get_group_name(),
            group_id=_get_group_id(),
            group_start_date=_get_group_start(),
            group_end_date=_get_group_end(),
            group_bqid=_get_group_bqid(),
            group_pck_type=_get_group_pck_type(),
            group_supervisor_email=_get_group_supervisor_email(),
            group_owner_email=_get_group_owner_email(),
            subgroup_owner_email=_get_subgroup_owner_emial(),
            subgroup_name=_get_subgroup_name(),
            subgroup_start_date=_get_subgroup_start(),
            subgroup_end_date=_get_subgroup_end(),
            subgroup_bqid=_get_subgroup_bqid(),
            subgroup_id=_get_subgroup_id(),
            autorenewal=_get_autorenewal(),
            comments=_get_comments(),
            end_date=_get_end_date(),
            international_deparments=_get_international_deparments(),
            opportunity_extension=_get_opportunity_extension(),
            maintance_project=_get_maintance_project(),
            ms_project_id=_get_ms_project_id(),
            operation_coordinator_name=_get_operation_coordinator_name(),
            operation_coordinator_controller=_get_operation_coordinator_controller(),  # noqa: E501
            operation_coordinator_sub=_get_operation_coordinator_sub(),
            opportunity=_get_opportunity(),
            periodicity=_get_periodicity(),
            profitcenter=_get_profitcenter(),
            project_account=_get_project_account(),
            projectcode=_get_project_code(),
            revenue_details=_get_revenue_details(),
            status=_get_status(),
            internal_comment=_get_internal_comment(),
            rejection_reason=_get_rejection_reason(),
            quote=_get_quote(),
        )

    def add_billing_lines(self, billing_lines):
        self.billing_lines.extend(billing_lines)

    def to_dict(self):
        return {
            "currency": self.currency,
            "amount": self.amount,
            "invoicing_country_code": self.invoicing_country_code,
            "operation_coordinator_email": self.operation_coordinator_email,
            "operation_coordinator_sub_email": self.operation_coordinator_sub_email,  # noqa: E501
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
            "opportunity_name": self.opportunity_name,
            # "stage": self.stage,
            # "lead_source": self.lead_source,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "project_start_date": self.project_start_date,
            "controller_email": self.controller_email,
            "controller_sub_email": self.controller_sub_email,
            "profit_center": self.profit_center,
            "cost_center": self.cost_center,
            "project_tier": self.project_tier,
            "jira_task_url": self.jira_task_url,
            # "opportunity_percentage": self.opportunity_percentage,
            "billing_lines": [bl.to_dict() for bl in self.billing_lines],
            "project_line_items": [
                pli.to_dict() for pli in self.project_line_items
            ],
            "account_billing_country": self.account_billing_country,
            "account_business_name": self.account_business_name,
            "account_name": self.account_name,
            "account_assigment_group": self.account_assigment_group,
            "account_tax_category": self.account_tax_category,
            "account_tax_classification": self.account_tax_classification,
            "account_sap_id": self.account_sap_id,
            "account_business_function": self.account_business_function,
            "account_tax_id_type": self.account_tax_id_type,
            "account_currency_code": self.account_currency_code,
            "account_created_date": self.account_created_date,
            "account_tier": self.account_tier,
            "account_pec_email": self.account_pec_email,
            "account_phone": self.account_phone,
            "account_fax": self.account_fax,
            "account_website": self.account_website,
            "account_cif": self.account_cif,
            "account_billing_address": self.account_billing_address,
            "account_billing_city": self.account_billing_city,
            "account_billing_postal_code": self.account_billing_postal_code,
            "account_billing_street": self.account_billing_street,
            "account_company_invoicing": self.account_company_invoicing,
            "account_office": self.account_office,
            "account_payment_terms": self.account_payment_terms,
            "account_billing_state_code": self.account_billing_state_code,
            "account_mail_invoicing": self.account_mail_invoicing,
            "account_customer_groupId": self.account_customer_groupId,
            "account_customer_subgroupId": self.account_customer_subgroupId,
            "account_invoicing_email": self.account_invoicing_email,
            "group_groupid": self.group_id,
            "group_name": self.group_name,
            "group_start_date": self.group_start_date,
            "group_end_date": self.group_end_date,
            "group_bqid": self.group_bqid,
            "group_pck_type": self.group_pck_type,
            "group_supervisor_email": self.group_supervisor_email,
            "group_owner_email": self.group_owner_email,
            "subgroup_owner_email": self.subgroup_owner_email,
            "subgroup_name": self.subgroup_name,
            "subgroup_start_date": self.subgroup_start_date,
            "subgroup_end_date": self.subgroup_end_date,
            "subgroup_bqid": self.subgroup_bqid,
            "subgroup_subgroupid": self.subgroup_id,
            "subgroup_groupid": self.group_id,
            "autorenewal": self.autorenewal,
            "comments": self.comments,
            "end_date": self.end_date,
            "international_deparments": self.international_deparments,
            "opportunity_extension": self.opportunity_extension,
            "maintance_project": self.maintance_project,
            "ms_project_id": self.ms_project_id,
            "operation_coordinator_name": self.operation_coordinator_name,
            # "operation_coordinator_controller": self.operation_coordinator_controller,  # noqa: E501
            "operation_coordinator_sub": self.operation_coordinator_sub,
            "opportunity": self.opportunity,
            "periodicity": self.periodicity,
            "profitcenter": self.profitcenter,
            "project_account": self.project_account,
            "projectcode": self.projectcode,
            "revenue_details": self.revenue_details,
            "status": self.status,
            # "internal_comment": self.internal_comment,
            # "rejection_reason": self.rejection_reason,
            "quote": self.quote,
            "opportunity_project_code": self.opportunity_project_code,
        }

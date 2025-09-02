from datetime import datetime

from ms_salesforce_api.salesforce.helpers.string import normalize_value

MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12",
}


class OpportunityLineItemDTO(object):
    def __init__(
        self,
        product_id,
        profit_center_name,
        country,
        opportunity_id,
        product_name,
        quantity,
        unit_price,
        profit_center_is_active,
        profit_center_deactivation_date,
        profit_center_deactivation_reason,
        profit_center_lkp,
        profit_center_txt,
        description,
        start_date,
        end_date,
        total_price,
    ):
        self.product_id = product_id
        self.profit_center_name = profit_center_name
        self.country = country
        self.opportunity_id = opportunity_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.profit_center_is_active = profit_center_is_active
        self.profit_center_deactivation_date = profit_center_deactivation_date
        self.profit_center_deactivation_reason = (
            profit_center_deactivation_reason
        )
        self.profit_center_lkp = profit_center_lkp
        self.profit_center_txt = profit_center_txt
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = total_price

    @staticmethod
    def from_salesforce_record(line_item_record, opportunity_id):
        product_name = line_item_record.get("FRM_ProductName__c", "")
        quantity = line_item_record.get("Quantity", 0.0)
        unit_price = line_item_record.get("UnitPrice", 0.0)
        product = line_item_record.get("Product2", {})
        profit_center = product.get("LKP_ProfitCenter__r", {})
        profit_center_lkp = product.get("LKP_ProfitCenter__c", {})
        profit_center_name = ""
        profit_center_is_active = None
        profit_center_deactivation_date = None
        profit_center_deactivation_reason = None
        profit_center_txt = None
        country = ""

        if profit_center and isinstance(profit_center, dict):
            profit_center_name = normalize_value(profit_center.get("Name", ""))
            country = normalize_value(profit_center.get("PCK_Country__c", ""))
            profit_center_is_active = normalize_value(
                profit_center.get("FRM_IsActive__c", None)
            )
            profit_center_deactivation_date = normalize_value(
                profit_center.get("DT_DeactivationDate__c", None)
            )
            profit_center_deactivation_reason = normalize_value(
                profit_center.get("TXT_DeactivationReason__c", "")
            )
            profit_center_txt = normalize_value(
                profit_center.get("TXT_ProfitCenter__c", "")
            )

        return OpportunityLineItemDTO(
            product_id=product.get("Id", ""),
            profit_center_name=profit_center_name,
            country=country,
            opportunity_id=opportunity_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            profit_center_is_active=profit_center_is_active,
            profit_center_deactivation_date=profit_center_deactivation_date,
            profit_center_deactivation_reason=profit_center_deactivation_reason,  # noqa: E501
            profit_center_lkp=profit_center_lkp,
            profit_center_txt=profit_center_txt,
            description=normalize_value(line_item_record["Description"]),
            start_date=line_item_record["StartDate__c"],
            end_date=line_item_record["DT_EndDate__c"],
            total_price=line_item_record["TotalPrice"],
        )

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "profit_center_name": self.profit_center_name,
            "country": self.country,
            "opportunity_id": self.opportunity_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "profit_center_is_active": self.profit_center_is_active,
            "profit_center_deactivation_date": self.profit_center_deactivation_date,  # noqa: E501
            "profit_center_deactivation_reason": self.profit_center_deactivation_reason,  # noqa: E501
            "profit_center_lkp": self.profit_center_lkp,
            "profit_center_txt": self.profit_center_txt,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_price": self.total_price,
        }


class OpportunityDTO(object):
    def __init__(
        self,
        opportunity_id,
        account_billing_country,
        account_owner,
        account_id,
        amount,
        amount_eur,
        campaign_id,
        close_month_formula,
        close_date,
        contact_id,
        curreny_iso_code,
        end_date,
        expected_revenue,
        fiscal,
        fiscal_quarter,
        fiscal_year,
        jira_default_name,
        ga_client_id,
        ga_track_id,
        ga_user_id,
        is_global,
        has_opportunity_lineitem,
        has_overdue_task,
        hasproposal,
        is_closed,
        is_won,
        jira_component_required,
        jira_estimated_work_load,
        jira_number,
        jira_work_load,
        jira_component_url,
        lead_id,
        lead_source,
        google_funding_opportunity,
        loss_reason,
        market_scope,
        ms_account_company_invoicing,
        ms_account_invoice_country_code,
        ms_company_origin,
        opportunity_name,
        opportunity_name_short,
        opportunity_requestor,
        owner_id,
        probability,
        record_type_id,
        roi_analysis_completed,
        associated_services,
        stage_name,
        start_date,
        tier_short,
        total_opportunity_quantity,
        year_created,
        opportunity_line_items,
        lkp_project,
        created_date,
        proposal_delivery_date,
        record_type,
        owner_name,
        next_step,
        account_manager,
        company_invoicing,
        account_manager_email,
        company_invoicing_name,
        comments,
        payment_method,
        payment_tems,
        invoicing_email,
        is_google_funding,
        priority,
        owner_username_name,
        created_by,
        last_modified_by,
        finance_contact,
        converted_amount_eur,
        project_code,
        google_drive_link,
        project_status,
        pck_division,
        out_of_report,
        billing_info,
        parent_opportunity,
        project_name,
    ):
        self.opportunity_id = opportunity_id
        self.account_billing_country = account_billing_country
        self.account_owner = account_owner
        self.account_id = account_id
        self.amount = amount
        self.amount_eur = amount_eur
        self.campaign_id = campaign_id
        self.close_month_formula = close_month_formula
        self.close_date = close_date
        self.contact_id = contact_id
        self.curreny_iso_code = curreny_iso_code
        self.end_date = end_date
        self.expected_revenue = expected_revenue
        self.fiscal = fiscal
        self.fiscal_quarter = fiscal_quarter
        self.fiscal_year = fiscal_year
        self.jira_default_name = jira_default_name
        self.ga_client_id = ga_client_id
        self.ga_track_id = ga_track_id
        self.ga_user_id = ga_user_id
        self.is_global = is_global
        self.has_opportunity_lineitem = has_opportunity_lineitem
        self.has_overdue_task = has_overdue_task
        self.hasproposal = hasproposal
        self.is_closed = is_closed
        self.is_won = is_won
        self.jira_component_required = jira_component_required
        self.jira_estimated_work_load = jira_estimated_work_load
        self.jira_number = jira_number
        self.jira_work_load = jira_work_load
        self.jira_component_url = jira_component_url
        self.lead_id = lead_id
        self.lead_source = lead_source
        self.google_funding_opportunity = google_funding_opportunity
        self.loss_reason = loss_reason
        self.market_scope = market_scope
        self.ms_account_company_invoicing = ms_account_company_invoicing
        self.ms_account_invoice_country_code = ms_account_invoice_country_code
        self.ms_company_origin = ms_company_origin
        self.opportunity_name = opportunity_name
        self.opportunity_name_short = opportunity_name_short
        self.opportunity_requestor = opportunity_requestor
        self.owner_id = owner_id
        self.probability = probability
        self.record_type_id = record_type_id
        self.roi_analysis_completed = roi_analysis_completed
        self.associated_services = associated_services
        self.stage_name = stage_name
        self.start_date = start_date
        self.tier_short = tier_short
        self.total_opportunity_quantity = total_opportunity_quantity
        self.year_created = year_created
        self.opportunity_line_items = opportunity_line_items
        self.lkp_project = lkp_project
        self.created_date = created_date
        self.proposal_delivery_date = proposal_delivery_date
        self.record_type = record_type
        self.owner_name = owner_name
        self.next_step = next_step
        self.account_manager = account_manager
        self.company_invoicing = company_invoicing
        self.account_manager_email = account_manager_email
        self.company_invoicing_name = company_invoicing_name
        self.comments = comments
        self.payment_method = payment_method
        self.payment_tems = payment_tems
        self.invoicing_email = invoicing_email
        self.is_google_funding = is_google_funding
        self.priority = priority
        self.owner_username_name = owner_username_name
        self.created_by = created_by
        self.last_modified_by = last_modified_by
        self.finance_contact = finance_contact
        self.converted_amount_eur = converted_amount_eur
        self.project_code = project_code
        self.google_drive_link = google_drive_link
        self.project_status = project_status
        self.pck_division = pck_division
        self.out_of_report = out_of_report
        self.billing_info = billing_info
        self.parent_opportunity = parent_opportunity
        self.project_name = project_name

    @staticmethod
    def from_salesforce_record(record):
        def _get_year_created(key: str):
            try:
                year = int(record[key])
                # We set allways the January first date because they want
                # a Date field for this value.
                return f"{year}-01-01"

            except (TypeError, KeyError):
                return ""

        def _get_close_month_formula():
            date_str = record.get("Close_Month_Formula__c", "")
            day, month = date_str.split(" ")

            month_num = MONTHS.get(month)

            date_formatted = (
                f"{datetime.now().year}-{month_num}-{day.zfill(2)}"
            )

            return date_formatted

        def _get_record_type():
            try:
                return record["RecordType"]["Name"]
            except (KeyError, TypeError):
                return ""

        def _get_owner_name():
            try:
                return record["Owner"]["Name"]
            except (KeyError, TypeError):
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

        def _get_account_manager_name():
            try:
                return record["LKP_AccountManager__r"]["Name"]
            except (KeyError, TypeError):
                return ""

        def _get_account_manager_email():
            try:
                return record["LKP_AccountManager__r"]["MAIL_Email__c"]
            except (KeyError, TypeError):
                return ""

        def _get_company_invoicing_name():
            try:
                return normalize_value(
                    record["LKP_MSCompanyInvoicing__r"]["Name"]
                )
            except (KeyError, TypeError):
                return ""

        def _get_owner_username_name():
            try:
                return normalize_value(record["Owner"]["UserRole"]["Name"])
            except (KeyError, TypeError):
                return ""

        def _get_created_by():
            try:
                return normalize_value(record["CreatedBy"]["Name"])
            except (KeyError, TypeError):
                return ""

        def _get_last_modified_by():
            try:
                return normalize_value(record["LastModifiedBy"]["Name"])
            except (KeyError, TypeError):
                return ""

        def _get_convert_amount():
            try:
                value = record["convertAmount"]
                clean_value = value.replace("EUR", "")
                clean_value = clean_value.replace(",", "")

                return float(clean_value)
            except (KeyError, TypeError, ValueError):
                return None

        opportunity_line_items = record.get("OpportunityLineItems", {})
        if opportunity_line_items and isinstance(opportunity_line_items, dict):
            line_items_records = record.get("OpportunityLineItems", {}).get(
                "records", []
            )
            opportunity_line_items = [
                OpportunityLineItemDTO.from_salesforce_record(
                    line_item,
                    record["Id"],
                ).to_dict()
                for line_item in line_items_records
            ]
        else:
            opportunity_line_items = []

        return OpportunityDTO(
            opportunity_id=record["Id"],
            account_billing_country=normalize_value(
                record.get("Account_Billing_Country__c", "")
            ),
            account_owner=normalize_value(record.get("Account_owner__c", "")),
            account_id=normalize_value(record.get("AccountId", "")),
            amount=record.get("Amount", 0.0),
            amount_eur=record.get("Amount_EUR__c", 0.0),
            campaign_id=normalize_value(record.get("CampaignId", "")),
            close_month_formula=_get_close_month_formula(),
            close_date=normalize_value(record.get("CloseDate", "")),
            contact_id=normalize_value(record.get("ContactId", "")),
            curreny_iso_code=normalize_value(
                record.get("CurrencyIsoCode", "")
            ),
            end_date=normalize_value(record.get("DT_ProjectEndDate__c", "")),
            expected_revenue=normalize_value(
                record.get("ExpectedRevenue", "")
            ),
            fiscal=normalize_value(record.get("Fiscal", "")),
            fiscal_quarter=normalize_value(record.get("FiscalQuarter", "")),
            fiscal_year=_get_year_created("FiscalYear"),
            jira_default_name=normalize_value(
                record.get("FRM_JiraDefaultName__c", "")
            ),
            ga_client_id=normalize_value(record.get("GACLIENTID__c", "")),
            ga_track_id=normalize_value(record.get("GATRACKID__c", "")),
            ga_user_id=normalize_value(record.get("GAUSERID__c", "")),
            is_global=normalize_value(record.get("Global__c", "")),
            has_opportunity_lineitem=normalize_value(
                record.get("HasOpportunityLineItem", "")
            ),
            has_overdue_task=normalize_value(record.get("HasOverdueTask", "")),
            hasproposal=normalize_value(record["HasProposal__c"]),
            is_closed=normalize_value(record["IsClosed"]),
            is_won=normalize_value(record["IsWon"]),
            jira_component_required=normalize_value(
                record["Jira_component_required__c"]
            ),
            jira_estimated_work_load=normalize_value(
                record.get("Jira_Estimated_Work_Load__c", "")
            ),
            jira_number=normalize_value(record.get("Jira_Number__c", "")),
            jira_work_load=normalize_value(
                record.get("Jira_Work_Load__c", "")
            ),
            jira_component_url=normalize_value(
                record.get("JiraComponentURL__c", "")
            ),
            lead_id=normalize_value(record.get("LeadId__c", "")),
            lead_source=normalize_value(record.get("LeadSource", "")),
            google_funding_opportunity=normalize_value(
                record.get("LKP_GoogleFundingOpportunity__c", "")
            ),
            loss_reason=normalize_value(record.get("Loss_Reason__c", "")),
            market_scope=normalize_value(record.get("Market_Scope__c", "")),
            ms_account_company_invoicing=normalize_value(
                record.get("MS_Account_Company_Invoicing__c", "")
            ),
            ms_account_invoice_country_code=normalize_value(
                record.get("MS_Account_Invoice_Country_Code__c", "")
            ),
            ms_company_origin=normalize_value(
                record.get("MS_Company_Origin__c", "")
            ),
            opportunity_name=normalize_value(record.get("Name", "")),
            opportunity_name_short=normalize_value(
                record.get("Opportunity_Name_Short__c", "")
            ),
            opportunity_requestor=normalize_value(
                record.get("Opportunity_requestor__c", "")
            ),
            owner_id=normalize_value(record.get("OwnerId", "")),
            probability=float(record.get("Probability", 0.0)),
            record_type_id=normalize_value(record.get("RecordTypeId", "")),
            roi_analysis_completed=normalize_value(
                record.get("ROI_Analysis_Completed__c", "")
            ),
            associated_services=normalize_value(
                record.get("Servicios_Asociados__c", "")
            ),
            stage_name=normalize_value(record.get("StageName", "")),
            start_date=normalize_value(
                record.get("DT_ProjectStartDate__c", "")
            ),
            tier_short=normalize_value(record.get("Tier_Short__c", "")),
            total_opportunity_quantity=normalize_value(
                record.get("TotalOpportunityQuantity", "")
            ),
            year_created=_get_year_created("Year_Created__c"),
            opportunity_line_items=opportunity_line_items,
            lkp_project=normalize_value(record.get("LKP_Project__c", "")),
            created_date=_parse_created_date(record["CreatedDate"]),
            proposal_delivery_date=_parse_created_date(
                record["Proposal_Delivery_Date__c"]
            ),
            record_type=_get_record_type(),
            owner_name=_get_owner_name(),
            next_step=record["NextStep"],
            account_manager=_get_account_manager_name(),
            company_invoicing=record["LKP_MSCompanyInvoicing__c"],
            account_manager_email=_get_account_manager_email(),
            company_invoicing_name=_get_company_invoicing_name(),
            comments=record["TXT_Comments__c"],
            payment_method=record["PCK_PaymentMethod__c"],
            payment_tems=record["PCK_PaymentTerms__c"],
            invoicing_email=record["MAIL_InvoicingEmail__c"],
            is_google_funding=record["CHK_IsGoogleFunding__c"],
            priority=record["Priority__c"],
            owner_username_name=_get_owner_username_name(),
            created_by=_get_created_by(),
            last_modified_by=_get_last_modified_by(),
            finance_contact=record["MAIL_FinanceContact__c"],
            converted_amount_eur=_get_convert_amount(),
            project_code=record["FRM_ProjectCode__c"],
            google_drive_link=record["FRM_GoogleDriveLink__c"],
            project_status=record["PCK_ProjectStatus__c"],
            pck_division=record["PCK_Division__c"],
            out_of_report=record["TECH_Out_of_report__c"],
            billing_info=record["TXT_BillingInfo__c"],
            parent_opportunity=record["LKP_ParentOpportunity__c"],
            project_name=record["FRM_ProjectName__c"],
        )

    def to_dict(self):
        return {
            "opportunity_id": self.opportunity_id,
            "account_billing_country": self.account_billing_country,
            "account_owner": self.account_owner,
            "account_id": self.account_id,
            "amount": self.amount,
            "amount_eur": self.amount_eur,
            "campaign_id": self.campaign_id,
            "close_month_formula": self.close_month_formula,
            "close_date": self.close_date,
            "contact_id": self.contact_id,
            "curreny_iso_code": self.curreny_iso_code,
            "end_date": self.end_date,
            "expected_revenue": self.expected_revenue,
            "fiscal": self.fiscal,
            "fiscal_quarter": self.fiscal_quarter,
            "fiscal_year": self.fiscal_year,
            "jira_default_name": self.jira_default_name,
            "ga_client_id": self.ga_client_id,
            "ga_track_id": self.ga_track_id,
            "ga_user_id": self.ga_user_id,
            "is_global": self.is_global,
            "has_opportunity_lineitem": self.has_opportunity_lineitem,
            "has_overdue_task": self.has_overdue_task,
            "hasproposal": self.hasproposal,
            "is_closed": self.is_closed,
            "is_won": self.is_won,
            "jira_component_required": self.jira_component_required,
            "jira_estimated_work_load": self.jira_estimated_work_load,
            "jira_number": self.jira_number,
            "jira_work_load": self.jira_work_load,
            "jira_component_url": self.jira_component_url,
            "lead_id": self.lead_id,
            "lead_source": self.lead_source,
            "google_funding_opportunity": self.google_funding_opportunity,
            "loss_reason": self.loss_reason,
            "market_scope": self.market_scope,
            "ms_account_company_invoicing": self.ms_account_company_invoicing,
            "ms_account_invoice_country_code": self.ms_account_invoice_country_code,  # noqa: E501
            "ms_company_origin": self.ms_company_origin,
            "opportunity_name": self.opportunity_name,
            "opportunity_name_short": self.opportunity_name_short,
            "opportunity_requestor": self.opportunity_requestor,
            "owner_id": self.owner_id,
            "probability": self.probability,
            "record_type_id": self.record_type_id,
            "roi_analysis_completed": self.roi_analysis_completed,
            "associated_services": self.associated_services,
            "stage_name": self.stage_name,
            "start_date": self.start_date,
            "tier_short": self.tier_short,
            "total_opportunity_quantity": self.total_opportunity_quantity,
            "year_created": self.year_created,
            "opportunity_line_items": self.opportunity_line_items,
            "lkp_project": self.lkp_project,
            "created_date": self.created_date,
            "proposal_delivery_date": self.proposal_delivery_date,
            "record_type": self.record_type,
            "owner_name": self.owner_name,
            "next_step": self.next_step,
            "account_manager": self.account_manager,
            "company_invoicing": self.company_invoicing,
            "account_manager_email": self.account_manager_email,
            "company_invoicing_name": self.company_invoicing_name,
            "comments": self.comments,
            "payment_method": self.payment_method,
            "payment_tems": self.payment_tems,
            "invoicing_email": self.invoicing_email,
            "is_google_funding": self.is_google_funding,
            "priority": self.priority,
            "owner_username_name": self.owner_username_name,
            "created_by": self.created_by,
            "last_modified_by": self.last_modified_by,
            "finance_contact": self.finance_contact,
            "converted_amount_eur": self.converted_amount_eur,
            "project_code": self.project_code,
            "google_drive_link": self.google_drive_link,
            "project_status": self.project_status,
            "pck_division": self.pck_division,
            "out_of_report": self.out_of_report,
            "billing_info": self.billing_info,
            "parent_opportunity": self.parent_opportunity,
            "project_name": self.project_name,
        }

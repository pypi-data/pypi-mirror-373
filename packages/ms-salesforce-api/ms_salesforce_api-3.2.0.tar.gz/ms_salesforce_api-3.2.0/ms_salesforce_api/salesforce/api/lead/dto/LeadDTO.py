from ms_salesforce_api.salesforce.helpers.string import normalize_value


class LeadDTO(object):
    def __init__(
        self,
        id,
        account,
        account_fiscal_name,
        account_manager,
        address,
        billing_address,
        company,
        contact,
        description,
        pck_division,
        email,
        event_attendance,
        event_mame,
        first_human_interaction,
        first_meeting,
        has_events,
        help_from_nb_team_requested,
        monthly_adv_investing_amount,
        industry,
        invoicing_email,
        jira_task,
        jira_task_id,
        record_type_id,
        lead_source,
        lead_source_description,
        status,
        market_scope,
        meeting,
        message,
        mobile_phone,
        name,
        next_steps,
        opportunity_description,
        opportunity_name_Short,
        applicant_email,
        origin,
        primary_campaign_source,
        associated_services,
        risk_assessment,
        risk_assessment_date,
        title,
        website,
        created_date,
    ):
        self.id = id
        self.account = account
        self.account_fiscal_name = account_fiscal_name
        self.account_manager = account_manager
        self.address = address
        self.billing_address = billing_address
        self.company = company
        self.contact = contact
        self.description = description
        self.pck_division = pck_division
        self.email = email
        self.event_attendance = event_attendance
        self.event_mame = event_mame
        self.first_human_interaction = first_human_interaction
        self.first_meeting = first_meeting
        self.has_events = has_events
        self.help_from_nb_team_requested = help_from_nb_team_requested
        self.monthly_adv_investing_amount = monthly_adv_investing_amount
        self.industry = industry
        self.invoicing_email = invoicing_email
        self.jira_task = jira_task
        self.jira_task_id = jira_task_id
        self.record_type_id = record_type_id
        self.lead_source = lead_source
        self.lead_source_description = lead_source_description
        self.status = status
        self.market_scope = market_scope
        self.meeting = meeting
        self.message = message
        self.mobile_phone = mobile_phone
        self.name = name
        self.next_steps = next_steps
        self.opportunity_description = opportunity_description
        self.opportunity_name_Short = opportunity_name_Short
        self.applicant_email = applicant_email
        self.origin = origin
        self.primary_campaign_source = primary_campaign_source
        self.associated_services = associated_services
        self.risk_assessment = risk_assessment
        self.risk_assessment_date = risk_assessment_date
        self.title = title
        self.website = website
        self.created_date = created_date

    @staticmethod
    def from_salesforce_record(record):
        def build_address(address):
            """
            Construct a string representation of an address from a
            dictionary.

            :param location_dict: a dictionary containing location
            information.
            :return: a string representing the address.
            """
            address_components = []
            if address is not None:
                for field in [
                    "street",
                    "city",
                    "state",
                    "postalCode",
                    "country",
                ]:
                    if field in address and address.get(field, ""):
                        address_components.append(address[field])

            address = ", ".join(address_components)

            return normalize_value(address)

        return LeadDTO(
            id=record["Id"],
            account=normalize_value(record["Account__c"]),
            account_fiscal_name=normalize_value(
                record["Account_Fiscal_Name__c"]
            ),
            account_manager=normalize_value(record["LKP_AccountManager__c"]),
            address=normalize_value(build_address(record["Address"])),
            billing_address=normalize_value(
                build_address(record["Billing_Address__c"])
            ),
            company=normalize_value(record["Company"]),
            contact=normalize_value(record["Contact__c"]),
            description=normalize_value(record["Description"]),
            pck_division=normalize_value(record["PCK_Division__c"]),
            email=normalize_value(record["Email"]),
            event_attendance=normalize_value(record["EventAttendance__c"]),
            event_mame=normalize_value(record["EventName__c"]),
            first_human_interaction=normalize_value(
                record["Primera_Interaccion_Humana__c"]
            ),
            first_meeting=normalize_value(record["First_Meeting__c"]),
            has_events=record["HasEvents__c"],
            help_from_nb_team_requested=normalize_value(
                record["Help_from_NB_Team_requested__c"]
            ),
            monthly_adv_investing_amount=normalize_value(
                record["MonthlyAdvInvestingAmount__c"]
            ),
            industry=normalize_value(record["Industry"]),
            invoicing_email=normalize_value(record["Invoicing_Email__c"]),
            jira_task=normalize_value(record["Jira_Task__c"]),
            jira_task_id=normalize_value(record["JiraTaskId__c"]),
            record_type_id=normalize_value(record["RecordTypeId"]),
            lead_source=normalize_value(record["LeadSource"]),
            lead_source_description=normalize_value(
                record["Lead_Source_Description__c"]
            ),
            status=normalize_value(record["Status"]),
            market_scope=normalize_value(record["Market_Scope__c"]),
            meeting=record["Meeting__c"],
            message=normalize_value(record["Mensaje__c"]),
            mobile_phone=normalize_value(record["MobilePhone"]),
            name=normalize_value(record["Name"]),
            next_steps=normalize_value(record["Next_Steps__c"]),
            opportunity_description=normalize_value(
                record["Opportunity_Description__c"]
            ),
            opportunity_name_Short=normalize_value(
                record["Opportunity_Name_Short__c"]
            ),
            applicant_email=normalize_value(
                record["Correo_electr_nico_solicitante__c"]
            ),
            origin=normalize_value(record["Origin__c"]),
            primary_campaign_source=normalize_value(
                record["Primary_Campaign_Source__c"]
            ),
            associated_services=normalize_value(
                record["Servicios_Asociados__c"]
            ),
            risk_assessment=normalize_value(record["Risk_Assessment__c"]),
            risk_assessment_date=normalize_value(
                record["Risk_Assessment_Date__c"]
            ),
            title=normalize_value(record["Title"]),
            website=normalize_value(record["Website"]),
            created_date=normalize_value(record["CreatedDate"]),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "account": self.account,
            "account_fiscal_name": self.account_fiscal_name,
            "account_manager": self.account_manager,
            "address": self.address,
            "billing_address": self.billing_address,
            "company": self.company,
            "contact": self.contact,
            "description": self.description,
            "pck_division": self.pck_division,
            "email": self.email,
            "event_attendance": self.event_attendance,
            "event_mame": self.event_mame,
            "first_human_interaction": self.first_human_interaction,
            "first_meeting": self.first_meeting,
            "has_events": self.has_events,
            "help_from_nb_team_requested": self.help_from_nb_team_requested,
            "monthly_adv_investing_amount": self.monthly_adv_investing_amount,
            "industry": self.industry,
            "invoicing_email": self.invoicing_email,
            "jira_task": self.jira_task,
            "jira_task_id": self.jira_task_id,
            "record_type_id": self.record_type_id,
            "lead_source": self.lead_source,
            "lead_source_description": self.lead_source_description,
            "status": self.status,
            "market_scope": self.market_scope,
            "meeting": self.meeting,
            "message": self.message,
            "mobile_phone": self.mobile_phone,
            "name": self.name,
            "next_steps": self.next_steps,
            "opportunity_description": self.opportunity_description,
            "opportunity_name_Short": self.opportunity_name_Short,
            "applicant_email": self.applicant_email,
            "origin": self.origin,
            "primary_campaign_source": self.primary_campaign_source,
            "associated_services": self.associated_services,
            "risk_assessment": self.risk_assessment,
            "risk_assessment_date": self.risk_assessment_date,
            "title": self.title,
            "website": self.website,
            "created_date": self.created_date,
        }

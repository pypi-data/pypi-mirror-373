from datetime import datetime

from ms_salesforce_api.salesforce.helpers.string import normalize_value


class AccountDTO(object):
    def __init__(
        self,
        id,
        accelerator,
        name,
        key_account,
        customer_account_assignment_group,
        customer_tax_category,
        customer_tax_classification,
        txt_sapid,
        business_function,
        tax_id_type,
        currency_iso_code,
        created_date,
        tier,
        pec_email,
        phone,
        fax,
        website,
        cif,
        billing_country_code,
        business_name,
        billing_address,
        billing_city,
        billing_postalcode,
        billing_street,
        lkp_company_invoicing_business_name,
        lkp_company_invoicing_country,
        payment_terms,
        billing_state_code,
        mail_invoincing,
        invoincing_email,
        customer_group_id,
        customer_subgroup_id,
        customer_subgroup_name,
        customer_subgroup_dt_start,
        customer_subgroup_dt_end,
        customer_subgroup_bqid,
        customer_subgroup_owner_email,
        customer_group_name,
        customer_group_dt_start,
        customer_group_dt_end,
        customer_group_bqid,
        customer_group_mail_supervisor,
        customer_group_mail_owner,
        customer_group_pck_type,
        owner_email,
        type,
        industry,
        payment_method,
        risk_assessment,
        risk_assessment_date,
    ):
        self.id = id
        self.accelerator = accelerator
        self.name = name
        self.key_account = key_account
        self.customer_account_assignment_group = (
            customer_account_assignment_group
        )
        self.customer_tax_category = customer_tax_category
        self.customer_tax_classification = customer_tax_classification
        self.txt_sapid = txt_sapid
        self.business_function = business_function
        self.tax_id_type = tax_id_type
        self.currency_iso_code = currency_iso_code
        self.created_date = created_date
        self.tier = tier
        self.pec_email = pec_email
        self.phone = phone
        self.fax = fax
        self.website = website
        self.cif = cif
        self.billing_country_code = billing_country_code
        self.business_name = business_name
        self.billing_address = billing_address
        self.billing_city = billing_city
        self.billing_postalcode = billing_postalcode
        self.billing_street = billing_street
        self.lkp_company_invoicing_business_name = (
            lkp_company_invoicing_business_name
        )
        self.lkp_company_invoicing_country = lkp_company_invoicing_country
        self.payment_terms = payment_terms
        self.billing_state_code = billing_state_code
        self.mail_invoincing = mail_invoincing
        self.invoincing_email = invoincing_email
        self.customer_group_id = customer_group_id
        self.customer_subgroup_id = customer_subgroup_id
        self.customer_subgroup_name = customer_subgroup_name
        self.customer_subgroup_dt_start = customer_subgroup_dt_start
        self.customer_subgroup_dt_end = customer_subgroup_dt_end
        self.customer_subgroup_bqid = customer_subgroup_bqid
        self.customer_subgroup_owner_email = customer_subgroup_owner_email
        self.customer_group_name = customer_group_name
        self.customer_group_dt_start = customer_group_dt_start
        self.customer_group_dt_end = customer_group_dt_end
        self.customer_group_bqid = customer_group_bqid
        self.customer_group_mail_supervisor = customer_group_mail_supervisor
        self.customer_group_mail_owner = customer_group_mail_owner
        self.customer_group_pck_type = customer_group_pck_type
        self.owner_email = owner_email
        self.type = type
        self.industry = industry
        self.payment_method = payment_method
        self.risk_assessment = risk_assessment
        self.risk_assessment_date = risk_assessment_date

    @staticmethod
    def from_salesforce_record(record):
        def _get_subgroup_name():
            try:
                return record["LKP_CustomerSubgroup__r"]["Name"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_start():
            try:
                return record["LKP_CustomerSubgroup__r"]["DT_Start__c"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_end():
            try:
                return record["LKP_CustomerSubgroup__r"]["DT_End__c"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_bqid():
            try:
                return record["LKP_CustomerSubgroup__r"]["TXT_BQId__c"]
            except (TypeError, KeyError):
                return ""

        def _get_subgroup_owner_email():
            try:
                return record["LKP_CustomerSubgroup__r"]["MAIL_Owner__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_name():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["Name"]
            except (TypeError, KeyError):
                return ""

        def _get_group_start():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["DT_Start__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_end():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["DT_End__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_bqid():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["TXT_BQId__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_mail_supervisor():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["MAIL_Supervisor__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_owner():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["MAIL_Owner__c"]
            except (TypeError, KeyError):
                return ""

        def _get_group_pck_type():
            try:
                return record["LKP_CustomerSubgroup__r"][
                    "LKP_CustomerGroup__r"
                ]["PCK_Type__c"]
            except (TypeError, KeyError):
                return ""

        def _get_owner_email():
            try:
                return record["Owner"]["Email"]
            except (TypeError, KeyError):
                return ""

        def _get_company_invoicing_business_name():
            try:
                return normalize_value(
                    record["LKP_MSCompanyInvoicing__r"]["TXT_BusinessName__c"]
                )
            except (TypeError, KeyError):
                return ""

        def _get_company_invoicing_country():
            try:
                return record["LKP_MSCompanyInvoicing__r"]["PCK_Prefix__c"]
            except (TypeError, KeyError):
                return ""

        def _get_billing_address():
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
                return build_address(record["BillingAddress"])
            except (TypeError, KeyError):
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

        return AccountDTO(
            id=record["Id"],
            accelerator=record["Accelerator__c"],
            name=normalize_value(record["Name"]),
            key_account=normalize_value(record["Key_Account__c"]),
            customer_account_assignment_group=normalize_value(
                record["MS_Customer_Account_Assigment_Group__c"]
            ),
            customer_tax_category=normalize_value(
                record["MS_Customer_Tax_Category__c"]
            ),
            customer_tax_classification=normalize_value(
                record["MS_Customer_Tax_Classification__c"]
            ),
            txt_sapid=normalize_value(record["TXT_SAPId__c"]),
            business_function=normalize_value(
                record["ms_Business_Function__c"]
            ),
            tax_id_type=normalize_value(record["ms_TAX_id_Type__c"]),
            currency_iso_code=normalize_value(record["CurrencyIsoCode"]),
            created_date=_parse_created_date(
                normalize_value(record["CreatedDate"])
            ),
            tier=normalize_value(record["Tier__c"]),
            pec_email=normalize_value(record["PEC_Email__c"]),
            phone=normalize_value(record["Phone"]),
            fax=normalize_value(record["Fax"]),
            website=normalize_value(record["Website"]),
            cif=normalize_value(record["CIF__c"]),
            billing_country_code=normalize_value(record["BillingCountryCode"]),
            business_name=normalize_value(record["Business_Name__c"]),
            billing_address=_get_billing_address(),
            billing_city=normalize_value(record["BillingCity"]),
            billing_postalcode=normalize_value(record["BillingPostalCode"]),
            billing_street=normalize_value(record["BillingStreet"]),
            lkp_company_invoicing_business_name=_get_company_invoicing_business_name(),  # noqa: E501
            lkp_company_invoicing_country=_get_company_invoicing_country(),
            payment_terms=normalize_value(record["Payment_Terms__c"]),
            payment_method=normalize_value(record["Payment_Method__c"]),
            billing_state_code=normalize_value(record["BillingStateCode"]),
            mail_invoincing=normalize_value(record["MAIL_Invoicing__c"]),
            invoincing_email=normalize_value(record["Invoicing_Email__c"]),
            customer_group_id=normalize_value(record["BQ_CustomerGroupId__c"]),
            customer_subgroup_id=normalize_value(
                record["BQ_CustomerSubgroupID__c"]
            ),
            customer_subgroup_name=normalize_value(_get_subgroup_name()),
            customer_subgroup_dt_start=normalize_value(_get_subgroup_start()),
            customer_subgroup_dt_end=normalize_value(_get_subgroup_end()),
            customer_subgroup_bqid=normalize_value(_get_subgroup_bqid()),
            customer_subgroup_owner_email=normalize_value(
                _get_subgroup_owner_email()
            ),
            customer_group_name=normalize_value(_get_group_name()),
            customer_group_dt_start=normalize_value(_get_group_start()),
            customer_group_dt_end=normalize_value(_get_group_end()),
            customer_group_bqid=normalize_value(_get_group_bqid()),
            customer_group_mail_supervisor=normalize_value(
                _get_group_mail_supervisor()
            ),
            customer_group_mail_owner=normalize_value(_get_group_owner()),
            customer_group_pck_type=normalize_value(_get_group_pck_type()),
            owner_email=normalize_value(_get_owner_email()),
            type=normalize_value(record["Type"]),
            industry=normalize_value(record["Industry"]),
            risk_assessment=normalize_value(record["Risk_Assessment__c"]),
            risk_assessment_date=normalize_value(
                record["Risk_Assessment_Date__c"]
            ),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "accelerator": self.accelerator,
            "name": self.name,
            "key_account": self.key_account,
            "customer_account_assignment_group": self.customer_account_assignment_group,  # noqa: E501
            "customer_tax_category": self.customer_tax_category,
            "customer_tax_classification": self.customer_tax_classification,
            "txt_sapid": self.txt_sapid,
            "business_function": self.business_function,
            "tax_id_type": self.tax_id_type,
            "currency_iso_code": self.currency_iso_code,
            "created_date": self.created_date,
            "tier": self.tier,
            "pec_email": self.pec_email,
            "phone": self.phone,
            "fax": self.fax,
            "website": self.website,
            "cif": self.cif,
            "billing_country_code": self.billing_country_code,
            "business_name": self.business_name,
            "billing_address": self.billing_address,
            "billing_city": self.billing_city,
            "billing_postalcode": self.billing_postalcode,
            "billing_street": self.billing_street,
            "lkp_company_invoicing_business_name": self.lkp_company_invoicing_business_name,  # noqa: E501
            "lkp_company_invoicing_country": self.lkp_company_invoicing_country,  # noqa: E501
            "payment_terms": self.payment_terms,
            "billing_state_code": self.billing_state_code,
            "mail_invoincing": self.mail_invoincing,
            "invoincing_email": self.invoincing_email,
            "customer_group_id": self.customer_group_id,
            "customer_subgroup_id": self.customer_subgroup_id,
            "customer_subgroup_name": self.customer_subgroup_name,
            "customer_subgroup_dt_start": self.customer_subgroup_dt_start,
            "customer_subgroup_dt_end": self.customer_subgroup_dt_end,
            "customer_subgroup_bqid": self.customer_subgroup_bqid,
            "customer_subgroup_owner_email": self.customer_subgroup_owner_email,  # noqa: E501
            "customer_group_name": self.customer_group_name,
            "customer_group_dt_start": self.customer_group_dt_start,
            "customer_group_dt_end": self.customer_group_dt_end,
            "customer_group_bqid": self.customer_group_bqid,
            "customer_group_mail_supervisor": self.customer_group_mail_supervisor,  # noqa: E501
            "customer_group_mail_owner": self.customer_group_mail_owner,
            "customer_group_pck_type": self.customer_group_pck_type,
            "owner_email": self.owner_email,
            "type": self.type,
            "industry": self.industry,
            "payment_method": self.payment_method,
            "risk_assessment": self.risk_assessment,
            "risk_assessment_date": self.risk_assessment_date,
        }

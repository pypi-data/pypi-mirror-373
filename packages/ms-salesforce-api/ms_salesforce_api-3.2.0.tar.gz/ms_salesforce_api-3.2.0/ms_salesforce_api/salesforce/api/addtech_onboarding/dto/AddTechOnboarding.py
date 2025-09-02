from ms_salesforce_api.salesforce.helpers.string import normalize_value


class AddTechOnboardingDTO(object):
    def __init__(
        self,
        id,
        account_id,
        advertiser_id,
        name,
        opportunity,
        opportunity_account_id,
        opportunity_project_code,
        opportunity_project_name,
        opportunity_product_name,
        opportunity_product_code,
        opportunity_product_currency_iso_code,
        opportunity__product_quantity,
        opportunity__product_profit_center_name,
        partner_id,
        status,
        txt_entity_id,
        txt_gmp_org_id,
        txt_manager_id,
        txt_platform_acc_name,
    ):
        self.id = id
        self.account_id = account_id
        self.advertiser_id = advertiser_id
        self.name = name
        self.opportunity = opportunity
        self.opportunity_account_id = opportunity_account_id
        self.opportunity_project_code = opportunity_project_code
        self.opportunity_project_name = opportunity_project_name
        self.opportunity_product_name = opportunity_product_name
        self.opportunity_product_code = opportunity_product_code
        self.opportunity_product_currency_iso_code = (
            opportunity_product_currency_iso_code
        )
        self.opportunity__product_quantity = opportunity__product_quantity
        self.opportunity__product_profit_center_name = (
            opportunity__product_profit_center_name
        )
        self.partner_id = partner_id
        self.status = status
        self.txt_entity_id = txt_entity_id
        self.txt_gmp_org_id = txt_gmp_org_id
        self.txt_manager_id = txt_manager_id
        self.txt_platform_acc_name = txt_platform_acc_name

    @staticmethod
    def from_salesforce_record(record: dict):

        def _get_opportunity_account_id():
            try:
                return record["Opportunity__r"]["AccountId"]
            except (KeyError, TypeError):
                return None

        def _get_opportunity_project_code():
            try:
                return record["Opportunity__r"]["FRM_ProjectCode__c"]
            except (KeyError, TypeError):
                return None

        def _get_opportunity_project_name():
            try:
                return normalize_value(
                    record["Opportunity__r"]["FRM_ProjectName__c"]
                )
            except (KeyError, TypeError):
                return None

        def _get_opportunity_product_name():
            try:
                return normalize_value(
                    record["Opportunity_Product__r"]["FRM_ProductName__c"]
                )
            except (KeyError, TypeError):
                return None

        def _get_opportunity_product_code():
            try:
                return record["Opportunity_Product__r"]["ProductCode"]
            except (KeyError, TypeError):
                return None

        def _get_opportunity_product_currency_iso_code():
            try:
                return record["Opportunity_Product__r"]["CurrencyIsoCode"]
            except (KeyError, TypeError):
                return None

        def _get_opportunity_product_quantity():
            try:
                return record["Opportunity_Product__r"]["Quantity"]
            except (KeyError, TypeError):
                return None

        def _get_opportunity_product_profit_center_name():
            try:
                return record["Opportunity_Product__r"][
                    "FRM_ProfitCenterName__c"
                ]
            except (KeyError, TypeError):
                return None

        return AddTechOnboardingDTO(
            id=record["Id"],
            account_id=record["Account_Id__c"],
            advertiser_id=record["Advertiser_Id__c"],
            name=normalize_value(record["Name"]),
            opportunity=record["Opportunity__c"],
            opportunity_account_id=_get_opportunity_account_id(),
            opportunity_project_code=_get_opportunity_project_code(),
            opportunity_project_name=_get_opportunity_project_name(),
            opportunity_product_name=_get_opportunity_product_name(),
            opportunity_product_code=_get_opportunity_product_code(),
            opportunity_product_currency_iso_code=_get_opportunity_product_currency_iso_code(),  # noqa: E501
            opportunity__product_quantity=_get_opportunity_product_quantity(),
            opportunity__product_profit_center_name=_get_opportunity_product_profit_center_name(),  # noqa: E501
            partner_id=record["Partner_Id__c"],
            status=normalize_value(record["Status__c"]),
            txt_entity_id=record["TXT_EntityID__c"],
            txt_gmp_org_id=record["TXT_GMPOrgID__c"],
            txt_manager_id=record["TXT_ManagerId__c"],
            txt_platform_acc_name=normalize_value(
                record["TXT_PlatformAccName__c"]
            ),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "advertiser_id": self.advertiser_id,
            "name": self.name,
            "opportunity": self.opportunity,
            "opportunity_account_id": self.opportunity_account_id,
            "opportunity_project_code": self.opportunity_project_code,
            "opportunity_project_name": self.opportunity_project_name,
            "opportunity_product_name": self.opportunity_product_name,
            "opportunity_product_code": self.opportunity_product_code,
            "opportunity_product_currency_iso_code": self.opportunity_product_currency_iso_code,  # noqa: E501
            "opportunity__product_quantity": self.opportunity__product_quantity,  # noqa: E501
            "opportunity__product_profit_center_name": self.opportunity__product_profit_center_name,  # noqa: E501
            "partner_id": self.partner_id,
            "status": self.status,
            "txt_entity_id": self.txt_entity_id,
            "txt_gmp_org_id": self.txt_gmp_org_id,
            "txt_manager_id": self.txt_manager_id,
            "txt_platform_acc_name": self.txt_platform_acc_name,
        }

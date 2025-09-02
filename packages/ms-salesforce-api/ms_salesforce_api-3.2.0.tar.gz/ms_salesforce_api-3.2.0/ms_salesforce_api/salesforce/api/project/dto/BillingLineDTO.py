from datetime import datetime


class BillingLineDTO:
    def __init__(
        self,
        id,
        name,
        project_id,
        project_code,
        currency,
        created_date,
        last_modified_date,
        billing_amount,
        billing_date,
        billing_period_ending_date,
        billing_period_starting_date,
        hourly_price,
        revenue_dedication,
        billing_plan_amount,
        billing_plan_billing_date,
        billing_plan_item,
        billing_plan_service_end_date,
        billing_plan_service_start_date,
    ):
        self.id = id
        self.name = name
        self.project_id = project_id
        self.project_code = project_code
        self.currency = currency
        self.created_date = created_date
        self.last_modified_date = last_modified_date
        self.billing_amount = billing_amount
        self.billing_date = billing_date
        self.billing_period_ending_date = billing_period_ending_date
        self.billing_period_starting_date = billing_period_starting_date
        self.hourly_price = hourly_price
        self.revenue_dedication = revenue_dedication
        self.billing_plan_amount = billing_plan_amount
        self.billing_plan_billing_date = billing_plan_billing_date
        self.billing_plan_item = billing_plan_item
        self.billing_plan_service_end_date = billing_plan_service_end_date
        self.billing_plan_service_start_date = billing_plan_service_start_date

    @staticmethod
    def from_salesforce_record(record, project_code):
        def _get_project_id():
            try:
                return record["Project_Line_Item__r"]["Project__c"]
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

        return BillingLineDTO(
            id=record["Id"],
            name=record["Name"],
            project_id=_get_project_id(),
            project_code=project_code,
            currency=record["CurrencyIsoCode"],
            created_date=_parse_created_date(record["CreatedDate"]),
            last_modified_date=_parse_created_date(record["LastModifiedDate"]),
            billing_amount=record["Biling_Ammount__c"],
            billing_date=record["Billing_Date__c"],
            billing_period_ending_date=record["Billing_Period_Ending_Date__c"],
            billing_period_starting_date=record[
                "Billing_Period_Starting_Date__c"
            ],
            hourly_price=record["Hourly_Price__c"],
            revenue_dedication=record["Revenue_Dedication__c"],
            billing_plan_amount=record["BillingPlanAmount__c"],
            billing_plan_billing_date=record["BillingPlanBillingDate__c"],
            billing_plan_item=record["BillingPlanItem__c"],
            billing_plan_service_end_date=record[
                "BillingPlanServiceEndDate__c"
            ],
            billing_plan_service_start_date=record[
                "BillingPlanServiceStartDate__c"
            ],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_code": self.project_code,
            "name": self.name,
            "currency": self.currency,
            "created_date": self.created_date,
            "last_modified_date": self.last_modified_date,
            "billing_amount": self.billing_amount,
            "billing_date": self.billing_date,
            "billing_period_ending_date": self.billing_period_ending_date,
            "billing_period_starting_date": self.billing_period_starting_date,
            "hourly_price": self.hourly_price,
            "revenue_dedication": self.revenue_dedication,
            "billing_plan_amount": self.billing_plan_amount,
            "billing_plan_billing_date": self.billing_plan_billing_date,
            "billing_plan_item": self.billing_plan_item,
            "billing_plan_service_end_date": self.billing_plan_service_end_date,  # noqa: E501
            "billing_plan_service_start_date": self.billing_plan_service_start_date,  # noqa: E501
        }

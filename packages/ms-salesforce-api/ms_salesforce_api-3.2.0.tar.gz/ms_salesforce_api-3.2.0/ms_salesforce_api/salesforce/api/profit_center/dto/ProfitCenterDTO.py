from ms_salesforce_api.salesforce.helpers.string import normalize_value


class ProfitCenterDTO(object):
    def __init__(
        self,
        id,
        name,
        txt_profit_center,
        country,
        deactivation_date,
        deactivation_reason,
        is_active,
    ):
        self.id = id
        self.name = name
        self.txt_profit_center = txt_profit_center
        self.country = country
        self.deactivation_date = deactivation_date
        self.deactivation_reason = deactivation_reason
        self.is_active = is_active

    @staticmethod
    def from_salesforce_record(record):
        return ProfitCenterDTO(
            id=record["Id"],
            name=normalize_value(record["Name"]),
            txt_profit_center=normalize_value(record["TXT_ProfitCenter__c"]),
            country=record["PCK_Country__c"],
            deactivation_date=record["DT_DeactivationDate__c"],
            deactivation_reason=record["TXT_DeactivationReason__c"],
            is_active=record["FRM_IsActive__c"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "txt_profit_center": self.txt_profit_center,
            "country": self.country,
            "deactivation_date": self.deactivation_date,
            "deactivation_reason": self.deactivation_reason,
            "is_active": self.is_active,
        }

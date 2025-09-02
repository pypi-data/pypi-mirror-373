from ms_salesforce_api.salesforce.helpers.string import normalize_value


class OpportunityContactDTO(object):
    def __init__(
        self,
        id,
        opportunity_id,
        contact_id,
        role,
        is_primary,
    ):
        self.id = id
        self.opportunity_id = opportunity_id
        self.contact_id = contact_id
        self.role = role
        self.is_primary = is_primary

    @staticmethod
    def from_salesforce_record(record):
        return OpportunityContactDTO(
            id=record["Id"],
            opportunity_id=record["OpportunityId"],
            contact_id=record["ContactId"],
            role=normalize_value(record["Role"]),
            is_primary=record["IsPrimary"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "contact_id": self.contact_id,
            "role": self.role,
            "is_primary": self.is_primary,
        }

from ms_salesforce_api.salesforce.helpers.string import normalize_value


class ContactDTO(object):
    def __init__(
        self,
        id,
        account_id,
        name,
        email,
        phone,
        title,
        department,
    ):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.email = email
        self.phone = phone
        self.title = title
        self.department = department

    @staticmethod
    def from_salesforce_record(record):
        return ContactDTO(
            id=record["Id"],
            account_id=record["AccountId"],
            name=normalize_value(record["Name"]),
            email=normalize_value(record["Email"]),
            phone=normalize_value(record["Phone"]),
            title=normalize_value(record["Title"]),
            department=normalize_value(record["Department"]),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "department": self.department,
        }

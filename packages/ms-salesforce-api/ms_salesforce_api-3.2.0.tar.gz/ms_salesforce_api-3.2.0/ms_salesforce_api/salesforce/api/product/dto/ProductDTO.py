from ms_salesforce_api.salesforce.helpers.string import normalize_value


class ProductDTO(object):
    def __init__(
        self,
        id,
        name,
        product_code,
        description,
        is_active,
        family,
        currency_iso_code,
        external_data_source_id,
        quantity_unit_of_measure,
        is_deleted,
        is_archived,
        product_type,
        record_id,
        profit_center_id,
    ):
        self.id = id
        self.name = name
        self.product_code = product_code
        self.description = description
        self.is_active = is_active
        self.family = family
        self.currency_iso_code = currency_iso_code
        self.external_data_source_id = external_data_source_id
        self.quantity_unit_of_measure = quantity_unit_of_measure
        self.is_deleted = is_deleted
        self.is_archived = is_archived
        self.product_type = product_type
        self.record_id = record_id
        self.profit_center_id = profit_center_id

    @staticmethod
    def from_salesforce_record(record):
        return ProductDTO(
            id=record["Id"],
            name=normalize_value(record["Name"]),
            product_code=normalize_value(record["ProductCode"]),
            description=normalize_value(record["Description"]),
            is_active=record["IsActive"],
            family=record["Family"],
            currency_iso_code=record["CurrencyIsoCode"],
            external_data_source_id=record["ExternalDataSourceId"],
            quantity_unit_of_measure=normalize_value(
                record["QuantityUnitOfMeasure"]
            ),
            is_deleted=record["IsDeleted"],
            is_archived=record["IsArchived"],
            product_type=normalize_value(record["Product_Type__c"]),
            record_id=record["FRM_RecordId__c"],
            profit_center_id=record["LKP_ProfitCenter__c"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "product_code": self.product_code,
            "description": self.description,
            "is_active": self.is_active,
            "family": self.family,
            "currency_iso_code": self.currency_iso_code,
            "external_data_source_id": self.external_data_source_id,
            "quantity_unit_of_measure": self.quantity_unit_of_measure,
            "is_deleted": self.is_deleted,
            "is_archived": self.is_archived,
            "product_type": self.product_type,
            "record_id": self.record_id,
            "profit_center_id": self.profit_center_id,
        }

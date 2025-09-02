DEFAULT_PRODUCT_QUERY = """
SELECT
    Id,
    Name,
    ProductCode,
    Description,
    IsActive,
    Family,
    CurrencyIsoCode,
    ExternalDataSourceId,
    QuantityUnitOfMeasure,
    IsDeleted,
    IsArchived,
    Product_Type__c,
    FRM_RecordId__c,
    LKP_ProfitCenter__c
FROM Product2
"""

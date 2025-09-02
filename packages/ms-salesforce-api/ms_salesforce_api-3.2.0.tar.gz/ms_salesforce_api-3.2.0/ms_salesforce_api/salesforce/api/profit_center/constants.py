DEFAULT_PROFIT_CENTER_QUERY = """
SELECT
    Id,
    Name,
    TXT_ProfitCenter__c,
    PCK_Country__c,
    DT_DeactivationDate__c,
    TXT_DeactivationReason__c,
    FRM_IsActive__c
FROM ProfitCenter__c
"""

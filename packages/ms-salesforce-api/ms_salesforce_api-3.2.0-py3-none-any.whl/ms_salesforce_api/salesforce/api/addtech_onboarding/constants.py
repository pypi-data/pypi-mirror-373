DEFAULT_ADDTECH_ONBOARDING_QUERY = """
SELECT
  Id,
  Account_Id__c,
  Advertiser_Id__c,
  Name,
  Opportunity__c,
  Opportunity__r.AccountId,
  Opportunity__r.FRM_ProjectCode__c,
  Opportunity__r.FRM_ProjectName__c,
  Opportunity_Product__r.FRM_ProductName__c,
  Opportunity_Product__r.ProductCode,
  Opportunity_Product__r.CurrencyIsoCode,
  Opportunity_Product__r.Quantity,
  Opportunity_Product__r.FRM_ProfitCenterName__c,
  Partner_Id__c,
  Status__c,
  TXT_EntityID__c,
  TXT_GMPOrgID__c,
  TXT_ManagerId__c,
  TXT_PlatformAccName__c
FROM Yangtse__c
"""

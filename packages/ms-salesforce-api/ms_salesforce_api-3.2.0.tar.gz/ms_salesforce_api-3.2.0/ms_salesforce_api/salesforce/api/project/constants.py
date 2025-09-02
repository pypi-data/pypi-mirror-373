DEFAULT_PROJECT_OPPORTUNITY_QUERY = """
SELECT
    Autorenewal__c,
    Comments__c,
    CreatedDate,
    CurrencyIsoCode,
    End_Date__c,
    Id,
    International_Departments__c,
    LastModifiedDate,
    LKP_CostCenter__r.Name,
    LKP_MSCompanyInvoicing__r.PCK_Prefix__c,
    LKP_OpportunityExtension__c,
    LKP_ProfitCenter__c,
    LKP_ProfitCenter__r.TXT_ProfitCenter__c,
    Maintenance_project__c,
    MS_Project_Id__c,
    Name,
    Operation_Coordinator__c,
    Operation_Coordinator__r.Controller__c,
    Operation_Coordinator__r.Name,
    Operation_Coordinator_Sub__c,
    Operation_Coordinator_Sub__r.Controller_SUB__c,
    Operation_Coordinator_Sub__r.Name,
    Opportunity__c,
    Opportunity__r.FRM_ProjectCode__c,
    Opportunity__r.JiraComponentURL__c,
    Opportunity__r.LeadSource,
    Opportunity__r.Opportunity_Name_Short__c,
    Opportunity__r.Probability,
    Opportunity__r.StageName,
    Opportunity__r.Tier_Short__c,
    Periodicity__c,
    Project_Account__c,
    Project_Account__r.BillingAddress,
    Project_Account__r.BillingCity,
    Project_Account__r.BillingCountryCode,
    Project_Account__r.BillingPostalCode,
    Project_Account__r.BillingStateCode,
    Project_Account__r.BillingStreet,
    Project_Account__r.BQ_CustomerGroupId__c,
    Project_Account__r.BQ_CustomerSubgroupId__c,
    Project_Account__r.Business_Name__c,
    Project_Account__r.CIF__c,
    Project_Account__r.CreatedDate,
    Project_Account__r.CurrencyISOCode,
    Project_Account__r.Fax,
    Project_Account__r.Id,
    Project_Account__r.Invoicing_Email__c,
    Project_Account__r.LKP_CustomerSubgroup__r.DT_End__c,
    Project_Account__r.LKP_CustomerSubgroup__r.DT_Start__c,
    Project_Account__r.LKP_CustomerSubgroup__r.Id,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.DT_End__c,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.DT_Start__c,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.Id,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.MAIL_Owner__c,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.MAIL_Supervisor__c,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.Name,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.PCK_Type__c,
    Project_Account__r.LKP_CustomerSubgroup__r.LKP_CustomerGroup__r.TXT_BQId__c,
    Project_Account__r.LKP_CustomerSubgroup__r.MAIL_Owner__c,
    Project_Account__r.LKP_CustomerSubgroup__r.Name,
    Project_Account__r.LKP_CustomerSubgroup__r.TXT_BQId__c,
    Project_Account__r.LKP_MSCompanyInvoicing__r.PCK_Prefix__c,
    Project_Account__r.LKP_MSCompanyInvoicing__r.TXT_BusinessName__c,
    Project_Account__r.MAIL_Invoicing__c,
    Project_Account__r.ms_Business_Function__c,
    Project_Account__r.MS_Customer_Account_Assigment_Group__c,
    Project_Account__r.MS_Customer_Tax_Category__c,
    Project_Account__r.MS_Customer_Tax_Classification__c,
    Project_Account__r.ms_TAX_id_Type__c,
    Project_Account__r.Name,
    Project_Account__r.Payment_Terms__c,
    Project_Account__r.PEC_Email__c,
    Project_Account__r.Phone,
    Project_Account__r.Tier__c,
    Project_Account__r.TXT_SAPId__c,
    Project_Account__r.Website,
    Quote__c,
    Revenue_Details__c,
    RU_TotalAmount__c,
    Start_Date__c,
    ToLabel(Status__c),
    TXT_InternalComment__c,
    TXT_RejectionReason__c,
    (
        SELECT
            Business_Unit__c,
            Country__c,
            CreatedDate,
            Department__c,
            Duration_months__c,
            Effort__c,
            End_Date__c,
            Ending_Date__c,
            Id,
            LastModifiedDate,
            LKP_CostCenter__r.Name,
            MS_PLI_Name__c,
            ProductNew__r.LKP_ProfitCenter__r.TXT_ProfitCenter__c,
            ProductNew__r.Name,
            Project__r.Opportunity__r.FRM_ProjectCode__c,
            Quantity__c,
            Revenue_Type__c,
            Sales_Order_Item__c,
            SapNetAmount__c,
            Starting_Date__c,
            Total_Billing_Amount_Billing_Lines__c,
            Total_Price__c,
            UnitPrice__c
        FROM
            Project_Line_Items__r
    )
FROM
    Project__c
"""
# Project__c   WHERE Id = 'a00AX000002DVi1YAG'

DEFAULT_PROJECT_BILLING_LINE_QUERY = """
SELECT
    Id,
    Name,
    Project_Line_Item__r.Project__c,
    CurrencyIsoCode,
    CreatedDate,
    LastModifiedDate,
    Biling_Ammount__c,
    Billing_Date__c,
    Billing_Period_Ending_Date__c,
    Billing_Period_Starting_Date__c,
    Hourly_Price__c,
    Revenue_Dedication__c,
    BillingPlanAmount__c,
    BillingPlanBillingDate__c,
    BillingPlanItem__c,
    BillingPlanServiceEndDate__c,
    BillingPlanServiceStartDate__c
FROM
    Billing_Line__c
WHERE
    Project_Line_Item__r.Project__c IN ('{project_id}')
"""

# Postgres Database schemas
DEFAULT_OPPORTUNITIES_CREATE_TABLE_QUERY = """
CREATE TABLE Opportunities (
    project_id VARCHAR(255) PRIMARY KEY,
    amount VARCHAR(255) DEFAULT NULL,
    controller_email VARCHAR(255) DEFAULT NULL,
    controller_sub_email VARCHAR(255) DEFAULT NULL,
    cost_center VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NULL,
    currency VARCHAR(3) DEFAULT NULL,
    invoicing_country_code CHAR(2) DEFAULT NULL,
    jira_task_url VARCHAR(255) DEFAULT NULL,
    last_updated_at TIMESTAMP DEFAULT NULL,
    lead_source VARCHAR(255) DEFAULT NULL,
    operation_coordinator_email VARCHAR(255) DEFAULT NULL,
    operation_coordinator_sub_email VARCHAR(255) DEFAULT NULL,
    opportunity_name VARCHAR(255) DEFAULT NULL,
    opportunity_percentage FLOAT DEFAULT NULL,
    profit_center VARCHAR(255) DEFAULT NULL,
    project_code VARCHAR(255) DEFAULT NULL,
    project_name VARCHAR(255) DEFAULT NULL,
    project_start_date DATE DEFAULT NULL,
    project_tier VARCHAR(255) DEFAULT NULL,
    stage VARCHAR(255) DEFAULT NULL
);
"""

DEFAULT_PROJECTLINE_CREATE_TABLE_QUERY = """
CREATE TABLE ProjectLine (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) DEFAULT NULL,
    country CHAR(20) DEFAULT NULL,
    created_date TIMESTAMP DEFAULT NULL,
    effort VARCHAR(255) DEFAULT NULL,
    ending_date DATE DEFAULT NULL,
    last_modified_date TIMESTAMP DEFAULT NULL,
    ms_pli_name VARCHAR(255) DEFAULT NULL,
    product_name VARCHAR(255) DEFAULT NULL,
    quantity FLOAT DEFAULT NULL,
    starting_date DATE DEFAULT NULL,
    total_price VARCHAR(255) DEFAULT NULL,
    unit_price VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (project_id) REFERENCES Opportunities(project_id)
);
"""
DEFAULT_BILLINGLINES_CREATE_TABLE_QUERY = """
CREATE TABLE BillingLines (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    project_code VARCHAR(255) DEFAULT NULL,
    currency VARCHAR(3) DEFAULT NULL,
    created_date TIMESTAMP DEFAULT NULL,
    last_modified_date TIMESTAMP DEFAULT NULL,
    billing_amount FLOAT DEFAULT NULL,
    billing_date DATE DEFAULT NULL,
    billing_period_ending_date DATE DEFAULT NULL,
    billing_period_starting_date DATE DEFAULT NULL,
    hourly_price FLOAT DEFAULT NULL,
    revenue_dedication FLOAT DEFAULT NULL,
    billing_plan_amount FLOAT DEFAULT NULL,
    billing_plan_billing_date DATE DEFAULT NULL,
    billing_plan_item VARCHAR(255) DEFAULT NULL,
    billing_plan_service_end_date DATE DEFAULT NULL,
    billing_plan_service_start_date DATE DEFAULT NULL,
    FOREIGN KEY (project_id) REFERENCES Opportunities(project_id)
);
"""

DEFAULT_ACCOUNTS_CREATE_TABLE_QUERY = """
CREATE TABLE Accounts (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(255) DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    customer_groupId VARCHAR(255) DEFAULT NULL,
    customer_subgroupId VARCHAR(255) DEFAULT NULL,
    assigment_group VARCHAR(255) DEFAULT NULL,
    tax_category  VARCHAR(255) DEFAULT NULL,
    tax_classification  VARCHAR(255) DEFAULT NULL,
    sap_id  VARCHAR(255) DEFAULT NULL,
    business_function  VARCHAR(255) DEFAULT NULL,
    tax_id_type  VARCHAR(255) DEFAULT NULL,
    currency_code  VARCHAR(255) DEFAULT NULL,
    created_date  VARCHAR(255) DEFAULT NULL,
    tier  VARCHAR(255) DEFAULT NULL,
    pec_email  VARCHAR(255) DEFAULT NULL,
    phone  VARCHAR(255) DEFAULT NULL,
    fax  VARCHAR(255) DEFAULT NULL,
    website  VARCHAR(255) DEFAULT NULL,
    cif  VARCHAR(255) DEFAULT NULL,
    billing_country  VARCHAR(255) DEFAULT NULL,
    business_name  VARCHAR(255) DEFAULT NULL,
    billing_address  VARCHAR(255) DEFAULT NULL,
    billing_city  VARCHAR(255) DEFAULT NULL,
    billing_postal_code  VARCHAR(255) DEFAULT NULL,
    billing_street  VARCHAR(255) DEFAULT NULL,
    company_invoicing  VARCHAR(255) DEFAULT NULL,
    office  VARCHAR(255) DEFAULT NULL,
    payment_terms  VARCHAR(255) DEFAULT NULL,
    billing_state_code  VARCHAR(255) DEFAULT NULL,
    mail_invoicing  VARCHAR(255) DEFAULT NULL,
    invoicing_email  VARCHAR(500) DEFAULT NULL,
    FOREIGN KEY (project_id) REFERENCES Opportunities(project_id)
);
"""

DEFAULT_GROUPS_CREATE_TABLE_QUERY = """
CREATE TABLE Groups (
    id SERIAL PRIMARY KEY,
    groupid VARCHAR(255) NOT NULL,
    project_id VARCHAR(255) DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    start_date VARCHAR(255) DEFAULT NULL,
    end_date VARCHAR(255) DEFAULT NULL,
    bqid VARCHAR(255) DEFAULT NULL,
    pck_type VARCHAR(255) DEFAULT NULL,
    supervisor_email VARCHAR(255) DEFAULT NULL,
    owner_email VARCHAR(255) DEFAULT NULL,

    FOREIGN KEY (project_id) REFERENCES Opportunities(project_id)
);
"""

DEFAULT_SUBGROUPS_CREATE_TABLE_QUERY = """
CREATE TABLE SubGroups (
    id SERIAL PRIMARY KEY,
    groupid VARCHAR(255) NOT NULL,
    subgroupid VARCHAR(255) DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    start_date VARCHAR(255) DEFAULT NULL,
    end_date VARCHAR(255) DEFAULT NULL,
    bqid VARCHAR(255) DEFAULT NULL,
    owner_email VARCHAR(255) DEFAULT NULL
);
"""

DEFAULT_POSTGRES_DATABASE_SCHEMAS_MAP = [
    {
        "db_name": "Opportunities",
        "query": DEFAULT_OPPORTUNITIES_CREATE_TABLE_QUERY,
    },
    {
        "db_name": "ProjectLine",
        "query": DEFAULT_PROJECTLINE_CREATE_TABLE_QUERY,
    },
    {
        "db_name": "BillingLines",
        "query": DEFAULT_BILLINGLINES_CREATE_TABLE_QUERY,
    },
    {"db_name": "Accounts", "query": DEFAULT_ACCOUNTS_CREATE_TABLE_QUERY},
    {"db_name": "Groups", "query": DEFAULT_GROUPS_CREATE_TABLE_QUERY},
    {"db_name": "SubGroups", "query": DEFAULT_SUBGROUPS_CREATE_TABLE_QUERY},
]

DEFAULT_DELETE_OPPORTUNITIES_TABLE = "DELETE FROM Opportunities WHERE true"
DEFAULT_DELETE_PROJECTLINES_TABLE = "DELETE FROM ProjectLine WHERE true"
DEFAULT_DELETE_BILLINGLINES_TABLE = "DELETE FROM BillingLines WHERE true"
DEFAULT_DELETE_ACCOUNTS_TABLE = "DELETE FROM Accounts WHERE true"
DEFAULT_DELETE_GROUPS_TABLE = "DELETE FROM Groups WHERE true"
DEFAULT_DELETE_SUBGROUPS_TABLE = "DELETE FROM SubGroups WHERE true"

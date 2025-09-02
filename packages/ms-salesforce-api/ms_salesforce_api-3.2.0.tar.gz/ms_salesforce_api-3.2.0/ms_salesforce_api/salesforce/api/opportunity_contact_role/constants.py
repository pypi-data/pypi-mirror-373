DEFAULT_OPPORTUNITY_CONTACT_QUERY = """
SELECT
    Id,
    OpportunityId,
    ContactId,
    Role,
    IsPrimary
FROM
    OpportunityContactRole
"""

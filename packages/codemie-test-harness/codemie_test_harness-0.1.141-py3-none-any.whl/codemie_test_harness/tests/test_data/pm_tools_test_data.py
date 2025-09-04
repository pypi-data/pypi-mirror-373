JIRA_TOOL_PROMPT = (
    "Get a title for ticket EPMCDME-222 ticket."
    "For generic jira tool use exactly the same parameters:"
    "relative_url=/rest/api/2/issue/EPMCDME-222"
    "method=GET"
    "params={}"
)

RESPONSE_FOR_JIRA_TOOL = """
    The title for ticket EPMCDME-222 is:
    CodeMie: Work with large datasets and multiple knowledge bases.
"""

CONFLUENCE_TOOL_PROMPT = """
    Use any of tools available: Generic Confluence Tool with the params:
    relative_url='/rest/api/content/search'
    method='GET'
    params='{'cql': 'title ~ "AQA backlog estimation"', 'limit': 5, 'expand': 'body.storage'}'
    or Search Kb tool
    and return the page content
"""

RESPONSE_FOR_CONFLUENCE_TOOL = """
    Result:
    In the context of AQA (Automated Quality Assurance) backlog estimation, the sizes are defined as follows:
    
    
    S (Small): Estimated at 1 hour per test case.
    M (Medium): Estimated at 3 hours per test case.
    L (Large): Estimated at 5 hours per test case.
    
    Here's the approximate estimation for the overall test cases:
    Approximately 71 test cases are of size S, totaling 110 man-hours.
    Approximately 140 test cases are of size M, totaling 520 man-hours.
    Approximately 7 test cases are of size L, totaling 40 man-hours.
    
    The prioritization starts with Critical or Major test cases, skipping the Minor ones:
    
    About 110 Major test cases which include:
    
    20 test cases of size S, totaling 20 hours.
    75 test cases of size M, totaling 225 hours.
    5 test cases of size L, totaling 25 hours.
    
    Critical test cases should already be covered with automation.
"""

RESPONSE_FOR_CONFLUENCE_TOOL_UNAUTHORIZED = """
    It appears that the search could not be completed due to authentication issues (HTTP Status 401 – Unauthorized). 
    To access the knowledge base, valid authentication credentials are required.


    Please provide authentication credentials or ensure that I have the necessary permissions to access the 
    Confluence knowledge base. If you need further assistance, feel free to ask!
"""

JIRA_CLOUD_TOOL_PROMPT = (
    "Get a title for ticket SCRUM-1 ticket. "
    "For generic jira tool use exactly the same parameters:"
    "relative_url=/rest/api/2/issue/SCRUM-1"
    "method=GET"
    "params={}"
)

RESPONSE_FOR_JIRA_CLOUD_TOOL = """
    The title for ticket SCRUM-1 is:
    This is test story
"""

CONFLUENCE_CLOUD_TOOL_PROMPT = """
    Get all pages related to codemie
    relative_url='/rest/api/content/search'
    method='GET'
    params='{'cql': 'title ~ "codemie"', 'limit': 5, 'expand': 'body.storage'}'
    or Search Kb tool
    and return the page content
"""

RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL = """
    Here are some pages related to "codemie" from the Confluence space:
    Codemie Platform
    Title: Codemie Platform
    URL: Codemie Platform
    Description: This page mentions that "Codemie Platform is the best one."

    CODEMIE Overview
    Title: CODEMIE
    URL: CODEMIE Overview
    Description: This space includes a section for describing the purpose of the space, a search feature, and a filter by label functionality.
    If you need more detailed information about a specific page, please let me know!
"""

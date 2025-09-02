# ServiceNow test data with only one example

PROMPT = """
        method="GET"
        table="incident"
        params={"sysparm_query":"number=INC0000060","sysparm_limit":"1"}
    """

EXPECTED_RESPONSE = """
        Here is the information for the incident `INC0000060`:
        
        - **Number**: INC0000060
        - **State**: 7 (indicating the incident is closed)
        - **Opened At**: 2016-12-12 15:19:57
        - **Closed At**: 2016-12-14 02:46:44
        - **Short Description**: Unable to connect to email
        - **Description**: I am unable to connect to the email server. It appears to be down.
        - **Close Notes**: This incident is resolved.
        - **Priority**: 3
        - **Impact**: 2
        - **Urgency**: 2
        - **Category**: Inquiry
        - **Subcategory**: Email
        - **Assigned To**: [Link to User](https://dev300686.service-now.com/api/now/table/sys_user/5137153cc611227c000bbd1bd8cd2007)
        - **Assignment Group**: [Link to Group](https://dev300686.service-now.com/api/now/table/sys_user_group/287ebd7da9fe198100f92cc8d1d2154e)
        - **Resolved By**: [Link to User](https://dev300686.service-now.com/api/now/table/sys_user/5137153cc611227c000bbd1bd8cd2007)
        - **Opened By**: [Link to User](https://dev300686.service-now.com/api/now/table/sys_user/681ccaf9c0a8016400b98a06818d57c7)
        - **Caller ID**: [Link to User](https://dev300686.service-now.com/api/now/table/sys_user/681ccaf9c0a8016400b98a06818d57c7)
        - **Closed By**: [Link to User](https://dev300686.service-now.com/api/now/table/sys_user/681ccaf9c0a8016400b98a06818d57c7)
        - **Business Service**: [Link to Service](https://dev300686.service-now.com/api/now/table/cmdb_ci_service/27d32778c0a8000b00db970eeaa60f16)
        - **CMDB CI**: [Link to CI](https://dev300686.service-now.com/api/now/table/cmdb_ci/109562a3c611227500a7b7ff98cc0dc7) 
        
        Feel free to ask if you need further details about this incident!
    """

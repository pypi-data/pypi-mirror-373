import os

import pytest

from codemie_test_harness.tests.enums.integrations import DataBaseDialect

ELASTIC_TOOL_TASK = """
    Search for Document ID: Zx4eF5cBvnDA_Y45jlWN in codemie_metrics_logs index
"""

RESPONSE_FOR_ELASTIC = """
    Here are the details of the document with ID `Zx4eF5cBvnDA_Y45jlWN` in the index `codemie_metrics_logs`:

    - **Timestamp:** 2025-05-28T13:39:27.949Z
    - **Metric Name:** conversation_assistant_usage
    - **Attributes:**
      - Count: 1
      - User ID: 6c04c3d1-7967-481a-82d5-0b7da258a555
      - User Name: Andrei Maskouchanka
      - Assistant ID: 4657258e-19e5-4162-a6ec-2a76d11c14d1
      - Assistant Name: Elastic Tool
      - Input Tokens: 2414
      - Output Tokens: 434
      - Money Spent: 0.01858
      - Project: andrei_maskouchanka@epam.com
      - Execution Time: 11.09025979042053
      - LLM Model: gpt-4o
      - Conversation ID: 9ea412d5-c460-41f1-8071-35083538652c
      - Status: success
    
    - **Additional Information:**
      - Time: 2025-05-28T13:39:27.949952597Z
      - Stream: stderr
      - Level: INFO
      - UUID: 3fd6a83f6a266c7760a71406dbbef99f
      - Kubernetes Details:
        - Pod Name: codemie-api-69b9484d46-2hnpd
        - Namespace Name: preview-codemie
        - Pod ID: 97edb665-2b76-47ad-a545-3b7a2695a0e7
        - Host: gke-epmd-edp-anthos--nap-e2-standard--e45b29fc-863z
        - Pod IP: 172.20.6.90
        - Container Name: codemie
        - Docker ID: 11ec33dc943cfa7153f31cde412837ccfae711b1edc9bb7d20055614eeefbf15
        - Container Hash: europe-west3-docker.pkg.dev/or2-msq-epmd-edp-anthos-t1iylu/prod/code-assistant@sha256:a0271b31b2a55cf71d319c6b5f394fbe7c6833db74fbb51ab22680bf096c6ecb
        - Container Image: europe-west3-docker.pkg.dev/or2-msq-epmd-edp-anthos-t1iylu/prod/code-assistant:0.28.0-SNAPSHOT.10
    
    If you need further details or assistance, please let me know!    
"""

SQL_TOOL_CREATE_TABLE_TASK = """
   Insert a new Employees table with Firstname, Lastname, Email, Department columns and fill it with 10 records
   
   Example for MySQL dialect:
   The first query to create table: {'sql_query': 'CREATE TABLE Employees ( 
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY, 
    Firstname VARCHAR(50), 
    Lastname VARCHAR(50), 
    Email VARCHAR(100), 
    Department VARCHAR(50) 
    );'} 
    
    The second query to fill table: {'sql_query': "INSERT INTO Employees (Firstname, Lastname, Email, Department) VALUES 
    ('John', 'Doe', 'john.doe@example.com', 'Engineering'), 
    ('Jane', 'Smith', 'jane.smith@example.com', 'Marketing'), 
    ('Jim', 'Brown', 'jim.brown@example.com', 'Sales'), 
    ('Lucy', 'Adams', 'lucy.adams@example.com', 'Finance'), 
    ('Michael', 'Johnson', 'michael.johnson@example.com', 'Engineering'), 
    ('Lisa', 'White', 'lisa.white@example.com', 'Human Resources'), 
    ('Adam', 'Young', 'adam.young@example.com', 'IT'), 
    ('Nancy', 'Green', 'nancy.green@example.com', 'Customer Support'), 
    ('Frank', 'Thomas', 'frank.thomas@example.com', 'Operations'), 
    ('Anna', 'King', 'anna.king@example.com', 'Research');"} 
   
"""
SQL_TOOL_INSERT_TABLE_TASK = "Add new Employee: Sarah Connor sarah.connor@email.com from Security department. Employees table has the following columns: Firstname, Lastname, Email, Department."

SQL_TOOL_QUERY_TABLE_TASK = "SELECT * FROM Employees WHERE department = 'Security'"
SQL_TOOL_DELETE_TABLE_TASK = "Delete Employees table."

RESPONSE_FOR_SQL = """
    Here is the list of employees from the Security department:

    | First Name | Last Name | Email                   | Department |
    |------------|-----------|-------------------------|------------|
    | Sarah      | Connor    | sarah.connor@email.com  | Security   |
"""

# Define test data for SQL tools based on environment
sql_tools_test_data = [
    DataBaseDialect.MY_SQL,
    DataBaseDialect.POSTGRES,
    pytest.param(
        DataBaseDialect.MS_SQL,
        marks=pytest.mark.skipif(
            os.getenv("ENV") not in ("aws", "azure", "gcp"),
            reason="MS SQL is only available in staging environments",
        ),
    ),
]

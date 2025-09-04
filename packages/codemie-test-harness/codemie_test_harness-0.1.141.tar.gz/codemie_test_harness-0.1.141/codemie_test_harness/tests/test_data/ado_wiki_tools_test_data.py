from codemie_test_harness.tests.enums.tools import AzureDevOpsWikiTool, Toolkit

ado_wiki_get_test_data = [
    (
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_ID,
        "In the CodemieAnton.wiki show page id 1 content",
        """
            The content of the page with ID 1 in the `CodemieAnton.wiki` is:
    
            ```
                Hello world! :)
            ```
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI,
        "Show the details for CodemieAnton.wiki",
        """
            - **Name**: CodemieAnton.wiki
            - **Project ID**: 9d40cdc1-5404-4d40-8025-e5267d69dc89
            - **Repository ID**: 53500a82-a76e-44c4-a72c-be2b25fd90ff
            - **Type**: projectWiki
            - **ID**: 53500a82-a76e-44c4-a72c-be2b25fd90ff
            - **Remote URL**: [CodemieAnton.wiki Remote URL](https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_wiki/wikis/53500a82-a76e-44c4-a72c-be2b25fd90ff)
            - **API URL**: [CodemieAnton.wiki API URL](https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_apis/wiki/wikis/53500a82-a76e-44c4-a72c-be2b25fd90ff)
        """,
    ),
    (
        Toolkit.AZURE_DEVOPS_WIKI,
        AzureDevOpsWikiTool.GET_WIKI_PAGE_BY_PATH,
        "Show the content of page with 'Super Mega Page' path in 'CodemieAnton.wiki' project wiki.",
        """
            The content of the page with the path /Super Mega Page in the CodemieAnton.wiki project wiki is:
            ```
                Hello world! :)
            ```
        """,
    ),
]

ADO_WIKI_CREATE_PAGE = {
    "prompt_to_assistant": """
        Create a new page in 'CodemieAnton.wiki' project wiki with title '{}' and content 'Greeting from CodeMie!'.
        version_identifier = 'main'
    """,
    "expected_llm_answer": """
        The page titled "{}" has been successfully created in the "CodemieAnton.wiki" project wiki with the content:

        ```
        Greeting from CodeMie!
        ```
    """,
}

ADO_WIKI_RENAME_PAGE = {
    "prompt_to_assistant": """
        Rename the page in 'CodemieAnton.wiki' project wiki with title '{}' with new title '{}-Renamed'.
        Use 'version_identifier': 'main', 'version_type': 'branch'
    """,
    "expected_llm_answer": """
        The page in the `CodemieAnton` wiki has been successfully renamed from `{}` to `{}-Renamed`.
    """,
}

ADO_WIKI_MODIFY_PAGE = {
    "prompt_to_assistant": """
        Update the content of '{}-Renamed' page in 'CodemieAnton.wiki' project wiki by adding new string: 
        'Updated content'.
        Use 'version_identifier': 'main', 'version_type': 'branch'
    """,
    "expected_llm_answer": """
        The content of the '{}-Renamed' page in the 'CodemieAnton.wiki' project wiki has been successfully 
        updated to include the string 'Updated content'.
    """,
}

ADO_WIKI_DELETE_PAGE = {
    "prompt_to_assistant": "Delete the '{}-Renamed' page in 'CodemieAnton.wiki' project wiki.",
    "expected_llm_answer": """
        The '{}-Renamed' page in the 'CodemieAnton.wiki' project wiki has been successfully deleted.
    """,
}

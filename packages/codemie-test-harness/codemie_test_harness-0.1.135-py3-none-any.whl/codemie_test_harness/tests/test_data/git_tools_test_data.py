from codemie_test_harness.tests.enums.tools import Toolkit, GitTool

list_branches_set_active_branch_test_data = [
    (
        Toolkit.GIT,
        GitTool.LIST_BRANCHES_IN_REPO,
        """
            List branches of the repo and find 5 branches with names like a 'main', 'new_main' etc. 
            Do not pass any parameters to tool, like: {}""",
        """
            Here are 5 branches with names like 'main', 'new_main', etc.:
    
            1. main
            2. main-test1-branch
            3. main-test2-branch
            4. main-test3-branch
            5. main-test4-branch
        """,
    ),
    (
        Toolkit.GIT,
        GitTool.SET_ACTIVE_BRANCH,
        "Set active branch to main-test3-branch",
        "The active branch has been successfully switched to main-test3-branch.",
    ),
]

create_branch_test_data = [
    (
        Toolkit.GIT,
        GitTool.CREATE_BRANCH,
        lambda branch_name: f"Create new branch called {branch_name}",
        lambda branch_name: f"The new branch called {branch_name} has been created successfully and is now the current active branch.",
    )
]

create_file_test_data = [
    (
        Toolkit.GIT,
        GitTool.CREATE_FILE,
        lambda class_name: f"Create new basic Java class with empty 'main' (// Empty main method) method called {class_name} under the src/main/java/testDirectory. Do not return created file content",
        lambda class_name: f"The new Java class named {class_name} has been successfully created in the src/main/java/testDirectory",
        lambda class_name: f"""
                package testDirectory;
            
                public class {class_name} {{
            
                    public static void main(String[] args) {{
                        // Empty main method
                    }}
                }}
            """,
    ),
]

create_merge_request_test_data = [
    (
        Toolkit.GIT,
        (
            GitTool.CREATE_PULL_REQUEST,
            GitTool.SET_ACTIVE_BRANCH,
            GitTool.CREATE_BRANCH,
            GitTool.CREATE_FILE,
        ),
        lambda source_branch, class_name, mr_name: f"""
                    "Create branch {source_branch}. Set active branch to {source_branch} then. 
                    Create in src/main/java/testDirectory new file {class_name}.java with 'Hello World' and commit only to the 
                    branch {source_branch}. Then create merge request to main branch with name {mr_name}. 
                    You MUST create new MR for it!"
                """,
        lambda source_branch, mr_name, mr_number: f"""
                    Created a merge request to integrate changes from the branch `{source_branch}` to the main branch. 
                    The merge request is titled `{mr_name}`. 
                    The merge request has been successfully created with PR number {mr_number}.
                """,
    )
]

delete_file_test_data = [
    (
        Toolkit.GIT,
        GitTool.DELETE_FILE,
        lambda class_name: f"Delete Java class called {class_name}.java from src/main/java/testDirectory.",
        lambda class_name: f"The Java class named {class_name} has been successfully deleted from the src/main/java/testDirectory",
        lambda class_name: f"""
                package testDirectory;

                public class {class_name} {{

                    public static void main(String[] args) {{
                        // Empty main method
                    }}
                }}
            """,
    )
]

get_merge_request_changes_test_data = [
    (
        Toolkit.GIT,
        (
            GitTool.CREATE_FILE,
            GitTool.CREATE_BRANCH,
            GitTool.SET_ACTIVE_BRANCH,
            GitTool.CREATE_PULL_REQUEST,
            GitTool.GET_PR_CHANGES,
        ),
        lambda source_branch, class_name, mr_name: f"""
                    "Create branch {source_branch}. Set active branch to {source_branch} then. 
                    Create in src/main/java/testDirectory new file {class_name}.java with 'Hello World' and commit only to the 
                    branch {source_branch}. Then create merge request to main branch with name {mr_name}. 
                    You MUST create new MR for it!"
                """,
        lambda source_branch, mr_name, mr_number: f"""
                    Created a merge request to integrate changes from the branch `{source_branch}` to the main branch. 
                    The merge request is titled `{mr_name}`. 
                    The merge request has been successfully created with PR number {mr_number}.
                """,
        lambda mr_number: f"Get changes from MR № {mr_number}",
        lambda class_name: f"""
                    I have retrieved the changes for Merge Request.
            
                    **Title:** {class_name}
                    **Description:** Created {class_name}.java file in src/main/java/testDirectory.
                    
                    **Changes:**
                    ```diff
                    diff --git a/src/main/java/testDirectory/{class_name}.java b/src/main/java/testDirectory/{class_name}.java
                    
                    ```
                    This diff indicates that a new file named `{class_name}.java` was created in the `src/main/java/testDirectory/` directory.
                """,
    )
]

update_file_test_data = [
    (
        Toolkit.GIT,
        (GitTool.CREATE_FILE, GitTool.UPDATE_FILE_DIFF),
        lambda class_name: f"Create new basic Java class with empty 'main' method called {class_name} under the src/main/java/testDirectory",
        lambda class_name: f"""
                The new Java class named {class_name} has been successfully created in the src/main/java/testDirectory
            """,
        lambda class_name: f"""
                package testDirectory;

                public class {class_name} {{

                    public static void main(String[] args) {{
                        // Empty main method
                    }}
                }}
            """,
        lambda class_name: f"""
                Find Java class '{class_name}' in directory with name src/main/java/testDirectory.
                After you found file - write in 'main' method 'Hello World' code and update file
            """,
        lambda class_name: f"""
                I've successfully updated the Java class `{class_name}` in `src/main/java/testDirectory` to include a simple
                'Hello World' program. The class now contains a `main` method that prints 'Hello, World!' to the console.
            """,
        lambda class_name: f"""
                package testDirectory;
            
                public class {class_name} {{
           
                public static void main(String[] args) {{
                    System.out.println("Hello World");
                }}
            }}
            """,
    ),
    (
        Toolkit.GIT,
        (GitTool.CREATE_FILE, GitTool.UPDATE_FILE),
        lambda class_name: f"Create new basic Java class with empty 'main' (// Empty main method) method called {class_name} under the src/main/java/testDirectory. Do not return created file content",
        lambda class_name: f"""
                The new Java class named {class_name} has been successfully created in the src/main/java/testDirectory
            """,
        lambda class_name: f"""
                package testDirectory;

                public class {class_name} {{

                    public static void main(String[] args) {{
                        // Empty main method
                    }}
                }}
            """,
        lambda class_name: f"""
                Find Java class '{class_name}' in directory with name src/main/java/testDirectory.
                After you found file - write in 'main' method 'Hello World' code and update file
            """,
        lambda class_name: f"""
                I've successfully updated the Java class `{class_name}` in `src/main/java/testDirectory` to include a simple
                'Hello World' program. The class now contains a `main` method that prints 'Hello, World!' to the console.
            """,
        lambda class_name: f"""
                package testDirectory;

                public class {class_name} {{

                public static void main(String[] args) {{
                    System.out.println("Hello World");
                }}
            }}
            """,
    ),
]

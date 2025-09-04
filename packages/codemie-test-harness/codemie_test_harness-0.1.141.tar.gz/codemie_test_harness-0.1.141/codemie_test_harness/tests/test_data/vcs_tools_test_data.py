import os

from codemie_test_harness.tests.enums.tools import VcsTool

GITHUB_TOOL_TASK = (
    f"Using github tool get info about issue №5 for the repo {os.getenv('GITHUB_PROJECT')}. "
    f"Do not wrap tool parameters in additional query object"
)

RESPONSE_FOR_GITHUB = """
            Issue #5 Details for Repository wild47/final_task
            Title: Test
            State: Open
            Created At: January 15, 2025
            Updated At: January 15, 2025
            Author: wild47
            Body: This is a test issue.
            Comments: 0
            Labels: None
            URL: View Issue on GitHub
            Additional Information
            Assignees: None
            Milestone: None
            Reactions:
            👍: 0
            👎: 0
            😄: 0
            🎉: 0
            😕: 0
            ❤️: 0
            🚀: 0
            👀: 0
"""

GITLAB_TOOL_TASK = f"Using gitlab tool get info about MR №7014 for repo with id '{os.getenv('GITLAB_PROJECT_ID')}'"

RESPONSE_FOR_GITLAB = f"""
        Here is the information about Merge Request (MR) №7014 for the repository with id '{os.getenv("GITLAB_PROJECT_ID")}':
        
        - **Title:** sdk_juhigsaqwkedvdy
        - **Description:** Merge the changes in branch `sdk_cgkbdhekvjiolpi` to the main branch, including the creation of `SdkYmsodrhepphxpyl.java` with 'Hello World'.
        - **State:** Closed
        - **Created At:** August 8, 2025, 08:23:05 UTC
        - **Updated At:** August 8, 2025, 08:23:22 UTC
        - **Closed At:** August 8, 2025, 08:23:22 UTC
        - **Target Branch:** main
        - **Source Branch:** sdk_cgkbdhekvjiolpi
        - **Merge Status:** can be merged
        - **User Notes Count:** 0
        - **Upvotes:** 0
        - **Downvotes:** 0
        - **Author:** [Anton Yeromin](https://gitbud.epam.com/anton_yeromin)
        - **Labels:** created-by-agent
        - **Web URL:** [Link to MR](https://gitbud.epam.com/epm-cdme/autotests/codemie-test-project/-/merge_requests/7014)
        
        This MR does not have any assignees or reviewers and was closed by Anton Yeromin. There are no merge conflicts, and it's the author's first contribution to this project.
"""

vcs_tools_test_data = [
    (VcsTool.GITHUB, GITHUB_TOOL_TASK, RESPONSE_FOR_GITHUB),
    (VcsTool.GITLAB, GITLAB_TOOL_TASK, RESPONSE_FOR_GITLAB),
]

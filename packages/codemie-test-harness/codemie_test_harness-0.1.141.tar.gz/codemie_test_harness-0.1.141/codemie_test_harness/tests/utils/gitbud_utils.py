import os
from time import sleep

import gitlab
from gitlab.exceptions import GitlabError
import logging

logger = logging.getLogger(__name__)

files_path = "src/main/java/testDirectory/"


class GitBudUtils:
    """Utility class for Git operations using GitLab API"""

    def __init__(
        self,
        url: str = os.getenv("GITLAB_URL"),
        token: str = os.getenv("GITLAB_TOKEN"),
        project_id: str = os.getenv("GITLAB_PROJECT_ID"),
    ):
        """
        Initialize GitBudUtils with GitLab credentials
        Args:
            url: GitLab instance URL
            token: GitLab personal access token
            project_id: GitLab project ID or 'namespace/project-name'
        """
        try:
            self.gl = gitlab.Gitlab(url=url, private_token=token)
            self.project = self.gl.projects.get(project_id)
        except GitlabError as e:
            logger.error(f"Failed to initialize GitLab project {project_id}: {str(e)}")
            raise

    def branch_exists(self, branch_name: str) -> bool:
        """
        Check if a remote branch exists in the repository
        Args:
            branch_name: Name of the branch to check
        Returns:
            True if remote branch exists, False otherwise
        """
        if not branch_name:
            return False

        try:
            self.project.branches.get(branch_name)
            return True
        except GitlabError:
            return False

    def delete_branch(self, branch_name: str) -> None:
        """
        Delete a remote git branch
        Args:
            branch_name: Name of the branch to delete
        Raises:
            GitlabError: If branch deletion fails
            ValueError: If branch name is invalid or branch doesn't exist
        """
        if not branch_name:
            raise ValueError("Branch name cannot be empty")

        try:
            branch = self.project.branches.get(branch_name)
            branch.delete()
            logger.info(f"Successfully deleted remote branch: {branch_name}")
        except GitlabError as e:
            if "404" in str(e):
                raise ValueError(f"Remote branch '{branch_name}' does not exist")
            logger.error(f"Failed to delete remote branch {branch_name}: {str(e)}")
            raise

    def create_file(
        self,
        file_name: str,
        branch: str = "main",
        file_content: str = "",
        commit_message: str = "Create file",
    ) -> None:
        """
        Create a new file in the repository
        Args:
            file_name: Name of the file to create in the repository
            branch: Branch name (defaults to 'main')
            file_content: Content to write to the file (defaults to empty string)
            commit_message: Commit message for the creation (defaults to 'Create file')
        Raises:
            GitlabError: If file creation fails
            ValueError: If file name is invalid or file already exists
        """
        if not file_name:
            raise ValueError("File name cannot be empty")

        full_path = files_path + file_name

        try:
            self.project.files.get(file_path=full_path, ref=branch)
            raise ValueError(f"File '{full_path}' already exists in branch {branch}")
        except GitlabError as e:
            # 404 means file doesn't exist, which is what we want
            if "404" not in str(e):
                raise

        # Create the file
        for index in range(1, 5):
            try:
                self.project.files.create(
                    {
                        "file_path": full_path,
                        "branch": branch,
                        "content": file_content,
                        "commit_message": commit_message,
                    }
                )
                logger.info(
                    f"Successfully created file: {full_path} in branch {branch}"
                )
                return
            except GitlabError as e:
                logger.error(
                    f"Failed to create file {full_path} from {index} attempt: {str(e)}"
                )
                if index == 5:
                    raise
                sleep(1)

    def get_file_content(self, file_name: str, branch: str = "main") -> str:
        """
        Get content of a file from the repository
        Args:
            file_name: Name to the file in the repository
            branch: Branch name (defaults to 'main')
        Returns:
            File content as string
        Raises:
            GitlabError: If file retrieval fails
        """
        try:
            file_content = self.project.files.get(
                file_path=files_path + file_name, ref=branch
            )
            return file_content.decode().decode("utf-8")
        except GitlabError as e:
            if "404" in str(e):
                raise ValueError(
                    f"File '{files_path}{file_name}' does not exist in branch {branch}"
                )
            logger.error(
                f"Failed to get file {files_path}{file_name} content: {str(e)}"
            )
            raise

    def file_exists(self, file_name: str, branch: str = "main") -> bool:
        """
        Check if a file exists in the repository
        Args:
            file_name: Name to the file in the repository
            branch: Branch name (defaults to 'main')
        Returns:
            True if file exists, False otherwise
        """
        try:
            return (
                self.project.files.get(file_path=files_path + file_name, ref=branch)
                is not None
            )
        except GitlabError:
            return False

    def delete_file(
        self, file_name: str, branch: str = "main", commit_message: str = "Delete file"
    ) -> None:
        """
        Delete a file from the repository
        Args:
            file_name: Name to the file in the repository
            branch: Branch name (defaults to 'main')
            commit_message: Commit message for the deletion
        Raises:
            GitlabError: If file deletion fails
            ValueError: If file path is invalid or file doesn't exist
        """
        if not file_name:
            raise ValueError("File path cannot be empty")

        try:
            file = self.project.files.get(file_path=files_path + file_name, ref=branch)
            file.delete(branch=branch, commit_message=commit_message)
            logger.info(
                f"Successfully deleted file: {files_path}{file_name} from branch {branch}"
            )
        except GitlabError:
            pass

    def get_merge_request_id_by_title(self, mr_title: str) -> int:
        """
        Get the merge request ID by its title.

        Args:
            mr_title (str): The title of the merge request to search for

        Returns:
            int: The ID of the merge request if found

        Raises:
            ValueError: If no merge request is found with the given title or if multiple merge requests are found
            GitlabError: If there's an error accessing the GitLab API
        """
        try:
            merge_requests = self.project.mergerequests.list(search=mr_title)

            exact_matches = [mr for mr in merge_requests if mr.title == mr_title]

            if not exact_matches:
                raise ValueError(f"No merge request found with title: {mr_title}")

            if len(exact_matches) > 1:
                raise ValueError(
                    f"Multiple merge requests found with title: {mr_title}"
                )

            return exact_matches[0].iid

        except GitlabError as e:
            logger.error(
                f"Failed to get merge request ID for title {mr_title}: {str(e)}"
            )
            raise

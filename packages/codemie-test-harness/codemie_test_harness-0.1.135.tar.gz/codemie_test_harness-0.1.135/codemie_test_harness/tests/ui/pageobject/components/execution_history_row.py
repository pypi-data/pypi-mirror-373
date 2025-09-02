import re

from playwright.sync_api import expect
from reportportal_client import step


class ExecutionHistoryRow:
    """Component representing a single row in the execution history table."""

    def __init__(self, page, row_locator):
        """
        Initialize execution history row component.

        Args:
            page: Playwright page object
            row_locator: Locator for the specific row element
        """
        self.page = page
        self.row = row_locator

    # Row elements
    @property
    def status_cell(self):
        """Status cell in the row."""
        return self.row.locator("td").nth(0)

    @property
    def status_badge(self):
        """Status badge element."""
        return self.status_cell.locator(".rounded-full.uppercase")

    @property
    def status_dot(self):
        """Status indicator dot."""
        return self.status_badge.locator("div")

    @property
    def prompt_cell(self):
        """Prompt cell in the row."""
        return self.row.locator("td").nth(1)

    @property
    def prompt_text(self):
        """Prompt text content."""
        return self.prompt_cell.locator("div")

    @property
    def triggered_by_cell(self):
        """Triggered by cell in the row."""
        return self.row.locator("td").nth(2)

    @property
    def triggered_by_text(self):
        """Triggered by text content."""
        return self.triggered_by_cell.locator("span")

    @property
    def updated_cell(self):
        """Updated timestamp cell in the row."""
        return self.row.locator("td").nth(3)

    @property
    def updated_text(self):
        """Updated timestamp text."""
        return self.updated_cell.locator("span")

    @property
    def actions_cell(self):
        """Actions cell containing buttons."""
        return self.row.locator("td").nth(4)

    @property
    def actions_container(self):
        """Actions button container."""
        return self.actions_cell.locator("div.flex.flex-row.gap-4")

    @property
    def download_button(self):
        """Download button."""
        return self.actions_container.locator("button").first

    @property
    def view_button(self):
        """View button."""
        return self.actions_container.locator("button").last

    # Action methods
    @step
    def click_download(self):
        """Click the download button."""
        self.download_button.click()

    @step
    def click_view(self):
        """Click the view button."""
        self.view_button.click()

    @step
    def hover_row(self):
        """Hover over the row."""
        self.row.hover()

    @step
    def click_row(self):
        """Click on the row."""
        self.row.click()

    # Verification methods
    @step
    def should_be_visible(self):
        """Verify that the row is visible."""
        expect(self.row).to_be_visible()

    @step
    def should_have_status(self, expected_status: str):
        """Verify the execution status."""
        expect(self.status_badge).to_have_text(expected_status)

    @step
    def should_have_in_progress_status(self):
        """Verify the status is 'In Progress' with proper styling."""
        self.should_have_status("In Progress")
        expect(self.status_badge).to_have_class("bg-in-progress-secondary")
        expect(self.status_badge).to_have_class("text-in-progress-main")
        expect(self.status_badge).to_have_class("border-in-progress-main")
        expect(self.status_dot).to_have_class("animate-pulse")

    @step
    def should_have_succeeded_status(self):
        """Verify the status is 'Succeeded' with proper styling."""
        self.should_have_status("Succeeded")
        expect(self.status_badge).to_contain_class("bg-success-secondary")
        expect(self.status_badge).to_contain_class("text-success-main")
        expect(self.status_badge).to_contain_class("border-success-main")

    @step
    def should_have_failed_status(self):
        """Verify the status is 'Failed' with proper styling."""
        self.should_have_status("Failed")
        expect(self.status_badge).to_contain_class("bg-error-secondary")
        expect(self.status_badge).to_contain_class("text-error-main")
        expect(self.status_badge).to_contain_class("border-error-main")

    @step
    def should_have_prompt(self, expected_prompt: str):
        """Verify the prompt text."""
        expect(self.prompt_text).to_have_text(expected_prompt)

    @step
    def should_have_triggered_by(self, expected_user: str):
        """Verify the triggered by user."""
        expect(self.triggered_by_text).to_have_text(expected_user)

    @step
    def should_have_updated_time_pattern(self, pattern: str):
        """Verify the updated timestamp matches a pattern."""
        expect(self.updated_text).to_have_text(re.compile(pattern))

    @step
    def should_have_actions_visible(self):
        """Verify that action buttons are visible."""
        expect(self.download_button).to_be_visible()
        expect(self.view_button).to_be_visible()

    @step
    def should_have_download_button_enabled(self):
        """Verify that download button is enabled."""
        expect(self.download_button).to_be_enabled()

    @step
    def should_have_view_button_enabled(self):
        """Verify that view button is enabled."""
        expect(self.view_button).to_be_enabled()

    @step
    def should_have_all_cells_visible(self):
        """Verify that all table cells are visible."""
        expect(self.status_cell).to_be_visible()
        expect(self.prompt_cell).to_be_visible()
        expect(self.triggered_by_cell).to_be_visible()
        expect(self.updated_cell).to_be_visible()
        expect(self.actions_cell).to_be_visible()

    @step
    def should_have_proper_status_styling(self):
        """Verify that status badge has proper styling."""
        expect(self.status_badge).to_contain_class("uppercase")
        expect(self.status_badge).to_contain_class("font-bold")
        expect(self.status_badge).to_contain_class("text-xs-1")
        expect(self.status_badge).to_contain_class("w-fit")
        expect(self.status_badge).to_contain_class("border-1")

    @step
    def should_have_action_buttons_with_icons(self):
        """Verify that action buttons have proper icons."""
        # Download button should have download icon
        expect(self.download_button.locator("svg")).to_be_visible()
        # View button should have view/eye icon
        expect(self.view_button.locator("svg")).to_be_visible()

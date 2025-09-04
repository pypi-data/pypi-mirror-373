from playwright.sync_api import expect
from reportportal_client import step


class WorkflowExecutionHistoryItem:
    """Component representing a single execution history item in the sidebar."""

    def __init__(self, page, item_locator):
        """
        Initialize workflow execution history item component.

        Args:
            page: Playwright page object
            item_locator: Locator for the specific execution item container
        """
        self.page = page
        self.item = item_locator

    # Item elements
    @property
    def container(self):
        """Main container element."""
        return self.item

    @property
    def status_badge(self):
        """Status badge (Succeeded/Failed/Running)."""
        return self.item.locator(".flex.flex-row.items-center.gap-1")

    @property
    def status_dot(self):
        """Status indicator dot."""
        return self.status_badge.locator(".rounded-full.w-2.h-2")

    @property
    def timestamp(self):
        """Execution timestamp element."""
        return self.item.locator(".text-text-tertiary.text-xs span")

    @property
    def execution_id(self):
        """Execution ID text element."""
        return self.item.locator(
            ".truncate.overflow-hidden.whitespace-nowrap.min-w-0.text-sm"
        )

    @property
    def menu_button(self):
        """Three dots menu button."""
        return self.item.locator('button:has(svg path[fill="#A1A1A1"])')

    # Utility methods
    @step
    def get_status_text(self) -> str:
        """Get status text (Succeeded, Failed, etc.)."""
        return self.status_text.text_content().strip()

    @step
    def get_execution_id_text(self) -> str:
        """Get execution ID text."""
        return self.execution_id.text_content().strip()

    @step
    def get_timestamp_text(self) -> str:
        """Get timestamp text."""
        return self.timestamp.text_content().strip()

    @step
    def is_active(self) -> bool:
        """Check if this execution item is currently active/selected."""
        return "bg-new-stroke" in self.container.get_attribute("class")

    @step
    def is_succeeded(self) -> bool:
        """Check if execution status is succeeded."""
        return "Succeeded" in self.get_status_text()

    @step
    def is_failed(self) -> bool:
        """Check if execution status is failed."""
        return "Failed" in self.get_status_text()

    @step
    def is_in_progress(self) -> bool:
        """Check if execution is in progress."""
        return (
            "In Progress" in self.get_status_text()
            or "Running" in self.get_status_text()
        )

    # Action methods
    @step
    def click(self):
        """Click on the execution item."""
        self.container.click()
        return self

    @step
    def click_menu(self):
        """Click the menu button (three dots)."""
        self.menu_button.click()
        return self

    @step
    def hover(self):
        """Hover over the execution item."""
        self.container.hover()
        return self

    @step
    def wait_for_visible(self, timeout: int = 5000):
        """Wait for the execution item to be visible."""
        self.container.wait_for(state="visible", timeout=timeout)
        return self

    # Verification methods
    @step
    def should_be_visible(self):
        """Verify the execution item is visible."""
        expect(self.container).to_be_visible()
        return self

    @step
    def should_not_be_visible(self):
        """Verify the execution item is not visible."""
        expect(self.container).not_to_be_visible()
        return self

    @step
    def should_have_status(self, expected_status: str):
        """Verify the execution has the expected status."""
        expect(self.status_badge).to_contain_text(expected_status)
        return self

    @step
    def should_have_succeeded_status(self):
        """Verify the execution status is succeeded with proper styling."""
        self.should_have_status("Succeeded")
        expect(self.status_badge).to_have_class("bg-success-secondary")
        expect(self.status_badge).to_have_class("text-success-main")
        expect(self.status_badge).to_have_class("border-success-main")
        return self

    @step
    def should_have_failed_status(self):
        """Verify the execution status is failed with proper styling."""
        self.should_have_status("Failed")
        expect(self.status_badge).to_have_class("bg-error-secondary")
        expect(self.status_badge).to_have_class("text-error-main")
        expect(self.status_badge).to_have_class("border-error-main")
        return self

    @step
    def should_have_in_progress_status(self):
        """Verify the execution status is in progress with proper styling."""
        expect(self.status_badge).to_contain_text("In Progress")
        expect(self.status_badge).to_have_class("bg-in-progress-secondary")
        expect(self.status_badge).to_have_class("text-in-progress-main")
        expect(self.status_badge).to_have_class("border-in-progress-main")
        return self

    @step
    def should_have_execution_id(self, expected_id: str):
        """Verify the execution ID."""
        expect(self.execution_id).to_have_text(expected_id)
        return self

    @step
    def should_have_execution_id_pattern(self, pattern: str):
        """Verify the execution ID matches a pattern (regex)."""
        expect(self.execution_id).to_match(pattern)
        return self

    @step
    def should_have_timestamp(self, expected_timestamp: str):
        """Verify the execution timestamp."""
        expect(self.timestamp).to_have_text(expected_timestamp)
        return self

    @step
    def should_have_timestamp_pattern(self, pattern: str):
        """Verify the timestamp matches a pattern."""
        expect(self.timestamp).to_match(pattern)
        return self

    @step
    def should_be_active(self):
        """Verify the execution item is currently active/selected."""
        expect(self.container).to_have_class("bg-new-stroke")
        return self

    @step
    def should_not_be_active(self):
        """Verify the execution item is not active/selected."""
        expect(self.container).not_to_have_class("bg-new-stroke")
        return self

    @step
    def should_have_menu_button(self):
        """Verify the execution item has a visible menu button."""
        expect(self.menu_button).to_be_visible()
        expect(self.menu_button).to_be_enabled()
        return self

    @step
    def should_have_status_dot_visible(self):
        """Verify the status dot is visible."""
        expect(self.status_dot).to_be_visible()
        return self

    @step
    def should_have_all_elements_visible(self):
        """Verify all main elements are visible."""
        expect(self.container).to_be_visible()
        expect(self.status_badge).to_be_visible()
        expect(self.execution_id).to_be_visible()
        expect(self.timestamp).to_be_visible()
        expect(self.menu_button).to_be_visible()
        return self

    @step
    def should_be_clickable(self):
        """Verify the execution item is clickable."""
        expect(self.container).to_be_enabled()
        return self

    @step
    def should_have_hover_effect(self):
        """Verify the execution item has hover effect."""
        self.hover()
        expect(self.container).to_have_class("hover:bg-new-stroke")
        return self

    @step
    def should_have_proper_status_styling(self):
        """Verify that status badge has proper styling."""
        expect(self.status_badge).to_contain_class("uppercase")
        expect(self.status_badge).to_contain_class("font-bold")
        expect(self.status_badge).to_contain_class("text-xs-1")
        expect(self.status_badge).to_contain_class("w-fit")
        expect(self.status_badge).to_contain_class("border-1")

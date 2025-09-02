from typing import List, Optional
from playwright.sync_api import expect, Locator
from reportportal_client import step

from codemie_test_harness.tests.ui.pageobject.base_page import BasePage
from codemie_test_harness.tests.ui.pageobject.components.workflow_execution_history_item import (
    WorkflowExecutionHistoryItem,
)
from codemie_test_harness.tests.ui.pageobject.components.workflow_execution_state import (
    WorkflowExecutionState,
)


class WorkflowExecutionsPage(BasePage):
    """Page object for the Workflow Executions page showing detailed execution history."""

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    # ==================== HEADER ELEMENTS ====================
    @property
    def workflow_title(self) -> Locator:
        """Workflow title in the header."""
        return self.page.locator("div.text-lg.font-semibold.whitespace-nowrap")

    @property
    def export_button(self) -> Locator:
        """Export button in the header."""
        return self.page.locator(
            '//button[text()=" Rerun workflow "]/preceding-sibling::button'
        )

    @property
    def configuration_button(self) -> Locator:
        """Configuration button in the header."""
        return self.page.locator('//button[text()=" Configuration "]')

    # ==================== SIDEBAR ELEMENTS ====================

    @property
    def sidebar(self) -> Locator:
        """Left sidebar container."""
        return self.page.locator("aside.sidebar")

    @property
    def execution_history_title(self) -> Locator:
        """Execution history title in sidebar."""
        return self.page.locator('h2:has-text("Workflow Execution History")')

    @property
    def time_period_label(self) -> Locator:
        """Time period label (Last 7 days)."""
        return self.page.locator(
            'div.text-xs.text-text-secondary.uppercase:has-text("Last 7 days")'
        )

    @property
    def execution_history_items(self) -> Locator:
        """All execution history items in sidebar."""
        return self.page.locator('//div[contains(@class,"hover:bg-new-stroke")]')

    @property
    def active_execution_item(self) -> Locator:
        """Currently active/selected execution item in sidebar."""
        return self.page.locator(".bg-new-stroke")

    # ==================== MAIN CONTENT ELEMENTS ====================

    @property
    def status_badge(self) -> Locator:
        """Status badge with status text and styling."""
        return self.page.locator('//div[text()="Status:"]/following-sibling::div')

    @property
    def status_dot(self) -> Locator:
        """Status indicator dot."""
        return self.status_badge.locator("xpath=./div")

    @property
    def triggered_by(self) -> Locator:
        """Triggered by value."""
        return self.page.locator('//div[text()="Triggered by:"]/following-sibling::div')

    @property
    def started_date(self) -> Locator:
        """Started time value."""
        return self.page.locator('//div[text()="Started:"]/following-sibling::div')

    @property
    def updated_date(self) -> Locator:
        """Updated time value."""
        return self.page.locator('//div[text()="Updated:"]/following-sibling::div')

    @property
    def download_button(self) -> Locator:
        """Download execution button."""
        return self.page.locator('xpath=.//button[text()=" Download "]')

    @property
    def rerun_workflow_button(self) -> Locator:
        """Rerun workflow button."""
        return self.page.locator('//button[text()=" Rerun workflow "]')

    # ==================== PROMPT SECTION ====================

    @property
    def prompt_section(self) -> Locator:
        """Prompt code block section."""
        return self.page.locator("div.flex.mt-2")

    @property
    def prompt_code_block(self) -> Locator:
        """Prompt code block container."""
        return self.prompt_section.locator("div.code-block.min-w-full")

    @property
    def prompt_header(self) -> Locator:
        """Prompt code block header."""
        return self.prompt_code_block.locator("div.code-block__header")

    @property
    def prompt_title(self) -> Locator:
        """Prompt title in header."""
        return self.prompt_header.locator('div:has-text("prompt")')

    @property
    def prompt_info_button(self) -> Locator:
        """Prompt info button."""
        return self.prompt_header.locator(
            'xpath=.//button[text()=" Copy code "]/preceding-sibling::button'
        )

    @property
    def prompt_copy_button(self) -> Locator:
        """Prompt copy code button."""
        return self.prompt_header.locator('xpath=.//button[text()=" Copy code "]')

    @property
    def prompt_download_button(self) -> Locator:
        """Prompt download button."""
        return self.prompt_header.locator('xpath=.//button[text()=" Download "]')

    @property
    def prompt_content(self) -> Locator:
        """Prompt code content."""
        return self.prompt_code_block.locator("pre.code-content.language-prompt code")

    # ==================== STATES SECTION ====================

    @property
    def states_section(self) -> Locator:
        """States section container."""
        return self.page.locator('//div[text()="States"]/../..')

    @property
    def states_header_section(self) -> Locator:
        """States section header with title and buttons."""
        return self.states_section.locator("xpath=./div[1]")

    @property
    def states_title(self) -> Locator:
        """States section title."""
        return self.states_header_section.locator('xpath=./div[text()="States"]')

    @property
    def collapse_all_button(self) -> Locator:
        """Collapse all states button."""
        return self.page.locator('//button[span[text()="Collapse All"]]')

    @property
    def expand_all_button(self) -> Locator:
        """Expand all states button."""
        return self.page.locator('//button[text()=" Expand All "]')

    @property
    def execution_states(self) -> Locator:
        """All execution state cards."""
        return self.page.locator('//div[@class="flex flex-row gap-5"]/..')

    # ==================== PAGINATION SECTION ====================

    @property
    def pagination_wrapper(self) -> Locator:
        """Pagination wrapper container."""
        return self.page.locator("div.pagination-wrapper")

    # ==================== RIGHT SIDEBAR (CONFIGURATION) ====================

    @property
    def configuration_sidebar(self) -> Locator:
        """Right sidebar for configuration (when open)."""
        return self.page.locator("div.bg-sidebar")

    @property
    def configure_workflow_title(self) -> Locator:
        """Configure workflow title in right sidebar."""
        return self.configuration_sidebar.locator(
            '//div[text()=" Configure Workflow "]'
        )

    @property
    def workflow_info_card(self) -> Locator:
        """Workflow information card in right sidebar."""
        return self.configuration_sidebar.locator(
            '//div[text()=" Configure Workflow "]/following-sibling::div[1]'
        )

    @property
    def workflow_avatar_sidebar(self) -> Locator:
        """Workflow avatar in sidebar."""
        return self.workflow_info_card.locator('img[alt="avatar"]')

    @property
    def workflow_name_sidebar(self) -> Locator:
        """Workflow name in sidebar."""
        return self.workflow_info_card.locator("div.text-md")

    @property
    def workflow_id_container(self) -> Locator:
        """Workflow ID container in sidebar."""
        return self.workflow_info_card.locator('//div[text()="ID:"]/..')

    @property
    def workflow_id_label(self) -> Locator:
        """Workflow ID label."""
        return self.workflow_id_container.locator('div:has-text("ID:")')

    @property
    def workflow_id_value(self) -> Locator:
        """Workflow ID value."""
        return self.workflow_id_container.locator("div.truncate.text-text-secondary")

    @property
    def workflow_id_copy_button(self) -> Locator:
        """Workflow ID copy button."""
        return self.workflow_id_container.locator(
            "button.button.tertiary.medium:has(svg)"
        )

    @property
    def configure_button(self) -> Locator:
        """Configure button in sidebar."""
        return self.workflow_info_card.locator(
            'button.button.secondary.medium.w-full:has-text("Configure")'
        )

    @property
    def yaml_configuration_title(self) -> Locator:
        """YAML configuration title in sidebar."""
        return self.configuration_sidebar.locator(
            'div.text-md.font-bold:has-text("Yaml configuration")'
        )

    @property
    def edit_yaml_button(self) -> Locator:
        """Edit YAML button in sidebar."""
        return self.configuration_sidebar.locator(
            'button.button.secondary.medium:has-text("Edit")'
        )

    @property
    def yaml_code_block(self) -> Locator:
        """YAML code block in sidebar."""
        return self.configuration_sidebar.locator("div.code-block")

    @property
    def yaml_code_content(self) -> Locator:
        """YAML code content."""
        return self.yaml_code_block.locator("pre.code-content.language-yaml code")

    # ==================== NAVIGATION METHODS ====================

    @step
    def navigate_to(self, workflow_id: str, execution_id: str):
        """Navigate to the workflow executions page for a specific workflow."""
        url = f"#/workflows/{workflow_id}/workflow-executions/{execution_id}"
        self.page.goto(url)

    @step
    def click_export(self):
        """Click the export button."""
        self.export_button.click()

    @step
    def click_configuration(self):
        """Click the configuration button to open/close right sidebar."""
        self.configuration_button.click()

    @step
    def click_download_execution(self):
        """Click the download execution button."""
        self.download_button.click()

    @step
    def click_rerun_workflow(self):
        """Click the rerun workflow button."""
        self.rerun_workflow_button.click()

    # ==================== EXECUTION HISTORY METHODS ====================

    @step
    def get_execution_history_item(
        self, index: int = 0
    ) -> WorkflowExecutionHistoryItem:
        """
        Get an execution history item from the sidebar by index.

        Args:
            index: Item index (0-based)

        Returns:
            WorkflowExecutionHistoryItem component
        """
        item_locator = self.execution_history_items.nth(index)
        return WorkflowExecutionHistoryItem(self.page, item_locator)

    @step
    def get_first_execution_history_item(self) -> WorkflowExecutionHistoryItem:
        """Get the first execution history item."""
        return self.get_execution_history_item(0)

    @step
    def get_all_execution_history_items(self) -> List[WorkflowExecutionHistoryItem]:
        """Get all execution history items as components."""
        items = []
        count = self.execution_history_items.count()
        for i in range(count):
            item_locator = self.execution_history_items.nth(i)
            items.append(WorkflowExecutionHistoryItem(self.page, item_locator))
        return items

    @step
    def select_execution_by_index(self, index: int):
        """Select an execution from the sidebar by index."""
        execution_item = self.get_execution_history_item(index)
        execution_item.click()

    @step
    def get_active_execution_item(self) -> WorkflowExecutionHistoryItem:
        """Get the currently active execution history item."""
        return WorkflowExecutionHistoryItem(self.page, self.active_execution_item)

    # ==================== EXECUTION STATES METHODS ====================

    @step
    def get_execution_state(self, index: int = 0) -> WorkflowExecutionState:
        """
        Get an execution state by index.

        Args:
            index: State index (0-based)

        Returns:
            WorkflowExecutionState component
        """
        state_locator = self.execution_states.nth(index)
        return WorkflowExecutionState(self.page, state_locator)

    @step
    def get_first_execution_state(self) -> WorkflowExecutionState:
        """Get the first execution state."""
        return self.get_execution_state(0)

    @step
    def click_collapse_all_states(self):
        """Click collapse all states button."""
        self.collapse_all_button.click()

    @step
    def click_expand_all_states(self):
        """Click expand all states button."""
        self.expand_all_button.click()

    # ==================== PROMPT INTERACTION METHODS ====================

    @step
    def click_prompt_info(self):
        """Click prompt info button."""
        self.prompt_info_button.click()

    @step
    def click_prompt_copy(self):
        """Click prompt copy button."""
        self.prompt_copy_button.click()

    @step
    def click_prompt_download(self):
        """Click prompt download button."""
        self.prompt_download_button.click()

    @step
    def get_prompt_text(self) -> str:
        """Get the prompt text content."""
        return self.prompt_content.text_content().strip()

    # ==================== VERIFICATION METHODS ====================

    @step
    def should_be_on_workflow_executions_page(self):
        """Verify that we are on the workflow executions page."""
        expect(self.workflow_title).to_be_visible()
        expect(self.execution_history_title).to_be_visible()
        expect(self.sidebar).to_be_visible()

    @step
    def should_have_workflow_title(self, expected_title: str):
        """Verify the workflow title."""
        expect(self.workflow_title).to_have_text(expected_title)

    @step
    def should_have_header_elements_visible(self):
        """Verify that all header elements are visible."""
        expect(self.back_button).to_be_visible()
        expect(self.workflow_title).to_be_visible()
        expect(self.export_button).to_be_visible()
        expect(self.configuration_button).to_be_visible()

    @step
    def should_have_sidebar_visible(self):
        """Verify that the sidebar is visible with all elements."""
        expect(self.sidebar).to_be_visible()
        expect(self.execution_history_title).to_be_visible()
        expect(self.time_period_label).to_be_visible()
        expect(self.time_period_label).to_have_text("Last 7 days")

    @step
    def should_have_execution_history_items(self, expected_count: Optional[int] = None):
        """Verify execution history items are present."""
        expect(self.execution_history_items.first).to_be_visible()
        if expected_count is not None:
            expect(self.execution_history_items).to_have_count(expected_count)
        return self

    @step
    def should_have_active_execution_item(self):
        """Verify that there is an active execution item selected."""
        expect(self.active_execution_item).to_be_visible()

    @step
    def should_have_status(self, expected_status: str):
        """Verify the execution status."""
        expect(self.status_badge).to_contain_text(expected_status)

    @step
    def should_have_succeeded_status(self):
        """Verify the execution status is succeeded with proper styling."""
        self.should_have_status("Succeeded")
        expect(self.status_badge).to_contain_class("bg-success-secondary")
        expect(self.status_badge).to_contain_class("text-success-main")
        expect(self.status_badge).to_contain_class("border-success-main")
        expect(self.status_dot).to_contain_class("bg-success-main")

    @step
    def should_have_failed_status(self):
        """Verify the execution status is failed with proper styling."""
        self.should_have_status("Failed")
        expect(self.status_badge).to_contain_class("bg-error-secondary")
        expect(self.status_badge).to_contain_class("text-error-main")
        expect(self.status_badge).to_contain_class("border-error-main")
        expect(self.status_dot).to_contain_class("bg-error-main")

    @step
    def should_have_triggered_by(self, expected_user: str):
        """Verify the triggered by user."""
        expect(self.triggered_by).to_have_text(expected_user)

    @step
    def should_have_started_time(self, expected_time: str):
        """Verify the started time."""
        expect(self.started_date).to_have_text(expected_time)

    @step
    def should_have_updated_time(self, expected_time: str):
        """Verify the updated time."""
        expect(self.updated_date).to_have_text(expected_time)

    @step
    def should_have_action_buttons_visible(self):
        """Verify that action buttons are visible and enabled."""
        expect(self.export_button).to_be_visible()
        expect(self.rerun_workflow_button).to_be_visible()
        expect(self.export_button).to_be_enabled()
        expect(self.rerun_workflow_button).to_be_enabled()

    @step
    def should_have_prompt_section_visible(self):
        """Verify that the prompt section is visible."""
        expect(self.prompt_section).to_be_visible()
        expect(self.prompt_code_block).to_be_visible()
        expect(self.prompt_header).to_be_visible()
        expect(self.prompt_content).to_be_visible()

    @step
    def should_have_prompt_text(self, expected_prompt: str):
        """Verify the prompt text content."""
        expect(self.prompt_content).to_have_text(expected_prompt)

    @step
    def should_have_prompt_buttons_visible(self):
        """Verify that prompt action buttons are visible."""
        expect(self.prompt_info_button).to_be_visible()
        expect(self.prompt_copy_button).to_be_visible()
        expect(self.prompt_download_button).to_be_visible()

    @step
    def should_have_states_section_visible(self):
        """Verify that the states section is visible."""
        expect(self.states_section).to_be_visible()
        expect(self.states_header_section).to_be_visible()
        expect(self.states_title).to_be_visible()
        expect(self.collapse_all_button).to_be_visible()
        expect(self.expand_all_button).to_be_visible()

    @step
    def should_have_execution_states(self, expected_count: Optional[int] = None):
        """Verify execution states are present."""
        expect(self.execution_states.first).to_be_visible()
        if expected_count:
            expect(self.execution_states).to_have_count(expected_count)

    @step
    def should_have_configuration_sidebar_closed(self):
        """Verify that the configuration sidebar is closed."""
        expect(self.configuration_sidebar).not_to_contain_class("w-[360px]")
        expect(self.configuration_sidebar).not_to_contain_class("opacity-100")

    @step
    def should_have_configuration_sidebar_open(self):
        """Verify that the configuration sidebar is open."""
        expect(self.configuration_sidebar).to_contain_class("w-[360px]")
        expect(self.configuration_sidebar).to_contain_class("opacity-100")
        expect(self.configure_workflow_title).to_be_visible()
        expect(self.workflow_info_card).to_be_visible()

    @step
    def should_have_yaml_configuration_visible(self):
        """Verify that YAML configuration is visible in sidebar."""
        expect(self.yaml_configuration_title).to_be_visible()
        expect(self.edit_yaml_button).to_be_visible()
        expect(self.yaml_code_block).to_be_visible()
        expect(self.yaml_code_content).to_be_visible()

    @step
    def should_have_workflow_info_in_sidebar(
        self, workflow_id: str, workflow_name: str
    ):
        """Verify workflow information in the sidebar."""
        expect(self.workflow_avatar_sidebar).to_be_visible()
        expect(self.workflow_name_sidebar).to_have_text(workflow_name)
        expect(self.workflow_id_value).to_have_text(workflow_id)
        expect(self.workflow_id_copy_button).to_be_visible()

    @step
    def should_have_all_main_sections_visible(self):
        """Verify all main page sections are visible."""
        self.should_have_header_elements_visible()
        self.should_have_sidebar_visible()
        self.should_have_prompt_section_visible()
        self.should_have_states_section_visible()

    @step
    def should_preserve_state_after_interactions(self):
        """Verify that page state is preserved after various interactions."""
        # Test configuration sidebar toggle
        self.click_configuration()
        self.should_have_configuration_sidebar_open()

        self.click_configuration()
        self.should_have_configuration_sidebar_closed()

        # Test states expand/collapse
        self.click_expand_all_states()
        first_state = self.get_first_execution_state()
        first_state.should_be_expanded()

        self.click_collapse_all_states()
        first_state.should_be_collapsed()

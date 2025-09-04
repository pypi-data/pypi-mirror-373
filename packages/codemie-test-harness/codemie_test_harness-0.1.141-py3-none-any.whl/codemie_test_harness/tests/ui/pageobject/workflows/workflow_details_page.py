import os
import re

from hamcrest import assert_that, has_length, greater_than
from playwright.sync_api import expect, Locator
from reportportal_client import step
from typing import List, Optional

from codemie_test_harness.tests.ui.pageobject.base_page import BasePage
from codemie_test_harness.tests.ui.pageobject.components import WorkflowSidebar
from codemie_test_harness.tests.ui.pageobject.components.execution_history_row import (
    ExecutionHistoryRow,
)


class WorkflowDetailsPage(BasePage):
    """Page object for the Workflow Details page."""

    page_url = "#/workflows"

    def __init__(self, page):
        super().__init__(page)
        self.sidebar = WorkflowSidebar(page)

    # ==================== PROPERTIES ====================

    # Header Elements
    @property
    def page_title(self) -> Locator:
        """Page title 'Workflow Details'."""
        return self.page.locator(
            'div.text-lg.font-semibold:has-text("Workflow Details")'
        )

    @property
    def workflow_avatar(self) -> Locator:
        """Workflow avatar image."""
        return self.page.locator('img[alt="avatar"]')

    @property
    def workflow_name(self) -> Locator:
        """Workflow name heading."""
        return self.page.locator('//main//div[contains(@class,"text-text-main")]')

    @property
    def workflow_author(self) -> Locator:
        """Workflow author information."""
        return self.page.locator('//main//span[contains(@class,"text-text-secondary")]')

    @property
    def workflow_sharing_info(self) -> Locator:
        """Workflow sharing information (Shared with Project)."""
        return self.page.locator(
            '//div[text()=" Not shared " or text()=" Shared with Project "]'
        )

    @property
    def edit_button(self) -> Locator:
        """Edit workflow button."""
        return self.page.locator('button.button.secondary.medium:has-text("Edit")')

    @property
    def run_workflow_button(self) -> Locator:
        """Run workflow button."""
        return self.page.locator(
            'button.button.primary.medium:has-text("Run workflow")'
        )

    # Tab Elements
    @property
    def tabs_container(self) -> Locator:
        """Tabs container."""
        return self.page.locator("div.flex.border-b-1.border-border-secondary")

    @property
    def executions_tab(self) -> Locator:
        """Executions tab."""
        return self.page.locator('a:has-text("Executions")')

    @property
    def configuration_tab(self) -> Locator:
        """Configuration tab."""
        return self.page.locator('a:has-text("Configuration")')

    # Executions Tab Content
    @property
    def executions_tab_content(self) -> Locator:
        """Executions tab content container."""
        return self.page.locator("#executions.tab-content")

    @property
    def executions_table(self) -> Locator:
        """Executions history table."""
        return self.page.locator("table.table")

    @property
    def executions_table_header(self) -> Locator:
        """Executions table header."""
        return self.page.locator("table.table thead.head")

    @property
    def executions_table_body(self) -> Locator:
        """Executions table body."""
        return self.page.locator("table.table tbody.body")

    @property
    def execution_rows(self) -> Locator:
        """All execution rows in the table."""
        return self.page.locator("table.table tbody.body tr")

    # Table Header Columns
    @property
    def status_header_column(self) -> Locator:
        """Status column header."""
        return self.page.locator('thead th:has-text("Status")')

    @property
    def prompt_header_column(self) -> Locator:
        """Prompt column header."""
        return self.page.locator('thead th:has-text("Prompt")')

    @property
    def triggered_by_header_column(self) -> Locator:
        """Triggered By column header."""
        return self.page.locator('thead th:has-text("Triggered By")')

    @property
    def updated_header_column(self) -> Locator:
        """Updated column header."""
        return self.page.locator('thead th:has-text("Updated")')

    @property
    def actions_header_column(self) -> Locator:
        """Actions column header."""
        return self.page.locator('thead th:has-text("Actions")')

    # Pagination Elements
    @property
    def pagination_wrapper(self) -> Locator:
        """Pagination wrapper container."""
        return self.page.locator("div.pagination-wrapper")

    @property
    def per_page_selector(self) -> Locator:
        """Items per page selector."""
        return self.page.locator("div.per-page")

    @property
    def per_page_dropdown(self) -> Locator:
        """Items per page dropdown."""
        return self.page.locator(".p-dropdown")

    @property
    def per_page_dropdown_label(self) -> Locator:
        """Items per page dropdown label."""
        return self.page.locator(".p-dropdown-label")

    @property
    def per_page_dropdown_trigger(self) -> Locator:
        """Items per page dropdown trigger."""
        return self.page.locator(".p-dropdown-trigger")

    # Configuration Tab Content
    @property
    def configuration_tab_content(self) -> Locator:
        """Configuration tab content container."""
        return self.page.locator("#config.tab-content")

    # Configuration Tab Elements
    @property
    def about_workflow_section(self) -> Locator:
        """About workflow section."""
        return self.page.locator('div:has-text("About workflow:")').first

    @property
    def workflow_description(self) -> Locator:
        """Workflow description text."""
        return self.page.locator("div.text-sm.text-text-tertiary").first

    @property
    def workflow_graph_schema_section(self) -> Locator:
        """Workflow Graph Schema section."""
        return self.page.locator('div:has-text("Workflow Graph Schema")').first

    @property
    def workflow_graph_image(self) -> Locator:
        """Workflow graph schema image."""
        return self.page.locator('img[alt="schema"]')

    @property
    def config_code_block(self) -> Locator:
        """Configuration code block container."""
        return self.page.locator("div.config div.code-block")

    @property
    def code_block_header(self) -> Locator:
        """Code block header."""
        return self.page.locator("div.code-block__header")

    @property
    def code_language_label(self) -> Locator:
        """Code language label (yaml)."""
        return self.page.locator("div.code-block__header div").first

    @property
    def copy_code_button(self) -> Locator:
        """Copy code button."""
        return self.page.locator('button:has-text("Copy code")')

    @property
    def download_code_button(self) -> Locator:
        """Download button."""
        return self.page.locator('button:has-text("Download")')

    @property
    def code_content(self) -> Locator:
        """Code content pre element."""
        return self.page.locator("pre.code-content")

    # Configuration Tab Sidebar (Overview)
    @property
    def overview_sidebar(self) -> Locator:
        """Overview sidebar section."""
        return self.page.locator('//div[@id="config"]//aside')

    @property
    def overview_title(self) -> Locator:
        """Overview title in sidebar."""
        return self.page.locator('span:has-text("OVERVIEW")').first

    @property
    def mode_info(self) -> Locator:
        """Mode information in sidebar."""
        return self.page.locator('div:has-text("Mode:")').first

    @property
    def project_info(self) -> Locator:
        """Project information in sidebar."""
        return self.page.locator('div:has-text("Project:")').first

    @property
    def workflow_id_section(self) -> Locator:
        """Workflow ID section in sidebar."""
        return self.page.locator(
            '//div[text()="Workflow ID"]/following-sibling::label/div'
        )

    @property
    def workflow_id_input(self) -> Locator:
        """Workflow ID input field."""
        return self.workflow_id_section.locator("//input[@disabled]")

    @property
    def workflow_id_copy_button(self) -> Locator:
        """Copy button for workflow ID."""
        return self.workflow_id_section.locator("//button")

    @property
    def access_links_section(self) -> Locator:
        """Access Links section in sidebar."""
        return self.page.locator(
            '//div[text()=" Access Links "]/following-sibling::label/div'
        )

    @property
    def workflow_details_link_label(self) -> Locator:
        """Link to workflow details label."""
        return self.access_links_section.locator(
            '../preceding-sibling::div[text()="Link to workflow details:"]'
        )

    @property
    def workflow_details_link_input(self) -> Locator:
        """Workflow details link input field."""
        return self.access_links_section.locator("//input[@disabled]")

    @property
    def workflow_details_link_copy_button(self) -> Locator:
        """Copy button for workflow details link."""
        return self.access_links_section.locator("//button")

    # ==================== NAVIGATION METHODS ====================

    @step
    def navigate_to(self, workflow_id: str):
        """Navigate to the Workflow Details page with workflow ID."""
        url = f"{self.page_url}/{workflow_id}"
        self.page.goto(url)

    # ==================== INTERACTION METHODS ====================

    @step
    def click_back(self):
        """Click the back button."""
        self.back_button.click()

    @step
    def click_edit(self):
        """Click the edit workflow button."""
        self.edit_button.click()

    @step
    def click_run_workflow(self):
        """Click the run workflow button."""
        self.run_workflow_button.click()

    @step
    def click_executions_tab(self):
        """Click on the Executions tab."""
        self.executions_tab.click()

    @step
    def click_configuration_tab(self):
        """Click on the Configuration tab."""
        self.configuration_tab.click()

    @step
    def click_per_page_dropdown(self):
        """Open the items per page dropdown."""
        self.per_page_dropdown_trigger.click()

    # ==================== EXECUTION HISTORY METHODS ====================

    @step
    def get_execution_row(self, index: int = 0) -> ExecutionHistoryRow:
        """
        Get an execution history row by index.

        Args:
            index: Row index (0-based)

        Returns:
            ExecutionHistoryRow component
        """
        row_locator = self.execution_rows.nth(index)
        return ExecutionHistoryRow(self.page, row_locator)

    @step
    def get_first_execution_row(self) -> ExecutionHistoryRow:
        """Get the first execution row."""
        return self.get_execution_row(0)

    @step
    def get_all_execution_rows(self) -> List[ExecutionHistoryRow]:
        """Get all execution rows as ExecutionHistoryRow components."""
        rows = []
        count = self.execution_rows.count()
        for i in range(count):
            row_locator = self.execution_rows.nth(i)
            rows.append(ExecutionHistoryRow(self.page, row_locator))
        return rows

    # ==================== VERIFICATION METHODS ====================

    @step
    def should_be_on_workflow_details_page(self):
        """Verify that we are on the Workflow Details page."""
        expect(self.page_title).to_be_visible()
        expect(self.workflow_name).to_be_visible()

    @step
    def should_have_header_elements_visible(self):
        """Verify that all header elements are visible."""
        expect(self.back_button).to_be_visible()
        expect(self.page_title).to_be_visible()
        expect(self.workflow_avatar).to_be_visible()
        expect(self.workflow_name).to_be_visible()
        expect(self.workflow_author).to_be_visible()
        expect(self.edit_button).to_be_visible()
        expect(self.run_workflow_button).to_be_visible()

    @step
    def should_have_workflow_info_visible(self):
        """Verify that workflow information is visible."""
        expect(self.workflow_avatar).to_be_visible()
        expect(self.workflow_name).to_be_visible()
        expect(self.workflow_author).to_be_visible()

    @step
    def should_have_workflow_name(self, expected_name: str):
        """Verify the workflow name."""
        expect(self.workflow_name).to_have_text(expected_name)

    @step
    def should_have_workflow_author(self, expected_author: str):
        """Verify the workflow author."""
        expect(self.workflow_author).to_contain_text(expected_author)

    @step
    def should_show_shared_with_project(self):
        """Verify that workflow is marked as shared with project."""
        expect(self.workflow_sharing_info).to_be_visible()
        expect(self.workflow_sharing_info).to_contain_text("Shared with Project")

    @step
    def should_have_action_buttons_visible(self):
        """Verify that action buttons are visible."""
        expect(self.edit_button).to_be_visible()
        expect(self.run_workflow_button).to_be_visible()

    @step
    def should_have_edit_button_enabled(self):
        """Verify that the edit button is enabled."""
        expect(self.edit_button).to_be_enabled()

    @step
    def should_have_run_workflow_button_enabled(self):
        """Verify that the run workflow button is enabled."""
        expect(self.run_workflow_button).to_be_enabled()

    @step
    def should_have_tabs_visible(self):
        """Verify that tabs are visible."""
        expect(self.tabs_container).to_be_visible()
        expect(self.executions_tab).to_be_visible()
        expect(self.configuration_tab).to_be_visible()

    @step
    def should_have_executions_tab_active(self):
        """Verify that the Executions tab is active."""
        expect(self.executions_tab).to_contain_class("border-text-main")
        expect(self.executions_tab).to_contain_class("font-semibold")
        expect(self.executions_tab).to_contain_class("cursor-default")
        expect(self.executions_tab_content).to_be_visible()
        expect(self.configuration_tab_content).to_contain_class("hidden")

    @step
    def should_have_configuration_tab_active(self):
        """Verify that the Configuration tab is active."""
        expect(self.configuration_tab).to_contain_class("border-text-main")
        expect(self.configuration_tab).to_contain_class("font-semibold")
        expect(self.configuration_tab).to_contain_class("cursor-default")
        expect(self.configuration_tab_content).to_be_visible()
        expect(self.executions_tab_content).to_contain_class("hidden")

    @step
    def should_have_executions_table_visible(self):
        """Verify that the executions table is visible."""
        expect(self.executions_table).to_be_visible()
        expect(self.executions_table_header).to_be_visible()
        expect(self.executions_table_body).to_be_visible()

    @step
    def should_have_table_headers_visible(self):
        """Verify that all table headers are visible."""
        expect(self.status_header_column).to_be_visible()
        expect(self.prompt_header_column).to_be_visible()
        expect(self.triggered_by_header_column).to_be_visible()
        expect(self.updated_header_column).to_be_visible()
        expect(self.actions_header_column).to_be_visible()

    @step
    def should_have_execution_rows(self, expected_count: Optional[int] = None):
        """
        Verify that execution rows are present.

        Args:
            expected_count: Expected number of rows (optional)
        """
        expect(self.execution_rows.first).to_be_visible()
        assert_that(self.execution_rows.all(), has_length(greater_than(0)))
        if expected_count is not None:
            expect(self.execution_rows).to_have_count(expected_count)

    @step
    def should_have_execution_with_status(self, status: str):
        """Verify that there's at least one execution with the specified status."""
        first_row = self.get_first_execution_row()
        first_row.should_have_status(status)

    @step
    def should_have_succeeded_execution(self):
        """Verify that there's at least one succeeded execution."""
        first_row = self.get_first_execution_row()
        first_row.should_have_succeeded_status()

    @step
    def should_have_execution_with_prompt(self, expected_prompt: str):
        """Verify that there's an execution with the specified prompt."""
        first_row = self.get_first_execution_row()
        first_row.should_have_prompt(expected_prompt)

    @step
    def should_have_execution_triggered_by(self, expected_user: str):
        """Verify that there's an execution triggered by the specified user."""
        first_row = self.get_first_execution_row()
        first_row.should_have_triggered_by(expected_user)

    @step
    def should_have_pagination_visible(self):
        """Verify that pagination elements are visible."""
        expect(self.pagination_wrapper).to_be_visible()
        expect(self.per_page_selector).to_be_visible()
        expect(self.per_page_dropdown).to_be_visible()

    @step
    def should_have_per_page_dropdown_with_value(self, expected_value: str):
        """Verify the items per page dropdown value."""
        expect(self.per_page_dropdown_label).to_have_text(expected_value)

    @step
    def should_have_execution_actions_working(self):
        """Verify that execution row actions are working."""
        first_row = self.get_first_execution_row()
        first_row.should_have_actions_visible()
        first_row.should_have_download_button_enabled()
        first_row.should_have_view_button_enabled()

    @step
    def should_preserve_tab_state_after_navigation(self):
        """Verify that tab state is preserved after page interactions."""
        # Switch tabs and verify state changes
        self.click_configuration_tab()
        self.should_have_configuration_tab_active()

        self.click_executions_tab()
        self.should_have_executions_tab_active()

    @step
    def should_have_sidebar_visible(self):
        """Verify that the sidebar is visible and functional."""
        self.sidebar.should_be_visible()
        self.sidebar.should_have_workflows_title()
        self.sidebar.should_have_categories_section()

    @step
    def should_have_configuration_tab_content_hidden(self):
        """Verify that configuration tab content is hidden when not active."""
        expect(self.configuration_tab_content).to_contain_class("hidden")

    @step
    def should_handle_empty_execution_list(self):
        """Verify proper handling when there are no executions."""
        # This would be used for workflows with no executions
        expect(self.executions_table).to_be_visible()
        expect(self.execution_rows).to_have_count(0)

    @step
    def should_see_export_popup(self):
        """Verify that the Export popup is visible with expected content."""
        expect(self.pop_up.cancel).to_have_text("Cancel")
        expect(self.pop_up.submit).to_have_text("Export")
        expect(self.pop_up.header).to_have_text("Export Workflow Execution")
        expect(self.pop_up.close).to_be_visible()

    @step
    def should_not_see_export_popup(self):
        """Verify that the Export popup is not visible."""
        expect(self.pop_up.pop_up).to_be_hidden()

    # ==================== CONFIGURATION TAB VERIFICATION METHODS ====================

    @step
    def should_have_configuration_elements_visible(self):
        """Verify that all configuration tab elements are visible."""
        expect(self.about_workflow_section).to_be_visible()
        expect(self.workflow_description).to_be_visible()
        expect(self.workflow_graph_schema_section).to_be_visible()
        expect(self.workflow_graph_image).to_be_visible()
        expect(self.config_code_block).to_be_visible()

    @step
    def should_have_code_block_elements_visible(self):
        """Verify that code block elements are visible."""
        expect(self.code_block_header).to_be_visible()
        expect(self.code_language_label).to_be_visible()
        expect(self.code_language_label).to_have_text("yaml")
        expect(self.copy_code_button).to_be_visible()
        expect(self.download_code_button).to_be_visible()
        expect(self.code_content).to_be_visible()

    @step
    def should_have_overview_sidebar_visible(self):
        """Verify that overview sidebar is visible with all elements."""
        expect(self.overview_sidebar).to_be_visible()
        expect(self.overview_title).to_be_visible()
        expect(self.mode_info).to_be_visible()
        expect(self.project_info).to_be_visible()

    @step
    def should_have_workflow_id_section_visible(self):
        """Verify that workflow ID section is visible."""
        expect(self.workflow_id_section).to_be_visible()
        expect(self.workflow_id_input).to_be_visible()
        expect(self.workflow_id_input).to_be_disabled()

    @step
    def should_have_access_links_section_visible(self):
        """Verify that access links section is visible."""
        expect(self.access_links_section).to_be_visible()
        expect(self.workflow_details_link_label).to_be_visible()
        expect(self.workflow_details_link_input).to_be_visible()
        expect(self.workflow_details_link_input).to_be_disabled()

    @step
    def should_have_workflow_description(self, expected_description: str):
        """Verify the workflow description text."""
        expect(self.workflow_description).to_have_text(expected_description)

    @step
    def should_have_mode_value(self, expected_mode: str):
        """Verify the mode value in overview."""
        expect(self.mode_info).to_contain_text(expected_mode)

    @step
    def should_have_project_value(self, expected_project: str):
        """Verify the project value in overview."""
        expect(self.project_info).to_contain_text(expected_project)

    @step
    def should_have_workflow_id_value(self, expected_id: str):
        """Verify the workflow ID value."""
        expect(self.workflow_id_input).to_have_value(expected_id)

    @step
    def should_have_workflow_details_link_value(self, workflow_id: str):
        """Verify the workflow details link value."""
        expect(self.workflow_details_link_input).to_have_value(
            f"{os.getenv('UI_URL')}/#/workflows?workflow={workflow_id}"
        )

    @step
    def should_have_yaml_configuration(self, yaml_config: str):
        """Verify that YAML configuration is displayed."""
        expect(self.code_content).to_have_text(yaml_config)

    @step
    def should_have_copy_buttons_enabled(self):
        """Verify that all copy buttons are enabled."""
        expect(self.copy_code_button).to_be_enabled()
        expect(self.download_code_button).to_be_enabled()

    @step
    def click_copy_code(self):
        """Click the copy code button."""
        self.copy_code_button.click()

    @step
    def click_download_code(self):
        """Click the download code button."""
        self.download_code_button.click()

    @step
    def click_copy_workflow_id(self):
        """Click the copy workflow ID button."""
        self.workflow_id_copy_button.click()

    @step
    def click_copy_workflow_details_link(self):
        """Click the copy workflow details link button."""
        self.workflow_details_link_copy_button.click()

    @step
    def should_have_graph_image_loaded(self):
        """Verify that the workflow graph image is loaded."""
        expect(self.workflow_graph_image).to_be_visible()
        expect(self.workflow_graph_image).to_have_attribute("src", re.compile(r".+"))

    @step
    def should_have_configuration_tab_content_complete(self, yaml_config: str):
        """Verify that configuration tab has all expected content."""
        self.should_have_configuration_elements_visible()
        self.should_have_code_block_elements_visible()
        self.should_have_overview_sidebar_visible()
        self.should_have_workflow_id_section_visible()
        self.should_have_access_links_section_visible()
        self.should_have_yaml_configuration(yaml_config)
        self.should_have_graph_image_loaded()

from playwright.sync_api import expect, Locator
from reportportal_client import step
from typing import Optional
import re

from codemie_test_harness.tests.ui.pageobject.workflows.base_workflow_form_page import (
    BaseWorkflowFormPage,
)


class EditWorkflowPage(BaseWorkflowFormPage):
    """Page object for the Edit Workflow page."""

    page_url = "#/workflows"

    def __init__(self, page):
        super().__init__(page)

    # ====================
    # PROPERTIES
    # ====================

    @property
    def page_title(self) -> Locator:
        """Page title 'Edit Workflow'."""
        return self.page.locator('div.text-lg.font-semibold:has-text("Edit Workflow")')

    @property
    def update_button(self) -> Locator:
        """Update button in the header."""
        return self.page.locator('button.button.primary.medium:has-text("Update")')

    @property
    def yaml_tabs_container(self) -> Locator:
        """YAML configuration tabs container."""
        return self.page.locator(".flex.border-b-1.border-border-secondary.small-tabs")

    @property
    def edit_current_version_tab(self) -> Locator:
        """Edit Current Version tab."""
        return self.page.locator('a:has-text("Edit Current Version")')

    @property
    def history_tab(self) -> Locator:
        """History tab."""
        return self.page.locator('a:has-text("History")')

    @property
    def current_tab_content(self) -> Locator:
        """Current tab content container."""
        return self.page.locator("#current.tab-content")

    @property
    def history_tab_content(self) -> Locator:
        """History tab content container."""
        return self.page.locator("#history.tab-content")

    @property
    def history_version_dropdown(self) -> Locator:
        """History version selection dropdown."""
        return self.page.locator(".p-autocomplete-input")

    @property
    def history_version_dropdown_button(self) -> Locator:
        """History version dropdown button."""
        return self.page.locator(".p-autocomplete-dropdown")

    @property
    def restore_button(self) -> Locator:
        """Restore button in history tab."""
        return self.page.locator('button.button.secondary.large:has-text("Restore")')

    @property
    def history_yaml_editor(self) -> Locator:
        """History YAML editor (read-only)."""
        return self.page.locator("#history #yaml_config.ace_editor")

    @property
    def history_yaml_content(self) -> Locator:
        """History YAML content area."""
        return self.page.locator("#history #yaml_config .ace_content")

    @property
    def first_history_item(self) -> Locator:
        """First item in history dropdown list."""
        return self.page.locator(".p-autocomplete-panel li").first

    # ====================
    # NAVIGATION METHODS
    # ====================

    @step
    def navigate_to(self, workflow_id: str):
        """Navigate to the Edit Workflow page with workflow ID."""
        url = f"{self.page_url}/{workflow_id}/edit"
        self.page.goto(url)

    # ====================
    # FORM INTERACTION METHODS
    # ====================

    @step
    def clear_name(self):
        """Clear the workflow name field."""
        self.name_input.clear()

    @step
    def fill_name(self, name: str):
        """Fill the workflow name field (override to clear first for edit)."""
        self.name_input.clear()
        self.name_input.fill(name)

    @step
    def clear_description(self):
        """Clear the workflow description field."""
        self.description_textarea.clear()

    @step
    def fill_description(self, description: str):
        """Fill the workflow description field (override to clear first for edit)."""
        self.description_textarea.clear()
        self.description_textarea.fill(description)

    @step
    def clear_icon_url(self):
        """Clear the icon URL field."""
        self.icon_url_input.clear()

    @step
    def fill_icon_url(self, icon_url: str):
        """Fill the icon URL field (override to clear first for edit)."""
        self.icon_url_input.clear()
        self.icon_url_input.fill(icon_url)

    # ====================
    # BUTTON CLICK METHODS
    # ====================

    @step
    def click_update(self):
        """Click the update button."""
        self.update_button.click()

    @step
    def click_edit_current_version_tab(self):
        """Click on Edit Current Version tab."""
        self.edit_current_version_tab.click()

    @step
    def click_history_tab(self):
        """Click on History tab."""
        self.history_tab.click()

    @step
    def click_restore(self):
        """Click the restore button in history tab."""
        self.restore_button.click()

    # ====================
    # HISTORY TAB METHODS
    # ====================

    @step
    def select_first_history_item(self):
        """Select the first item in the history dropdown list."""
        # Open the history dropdown
        self.history_version_dropdown_button.click()

        # Select the first item in the dropdown
        self.first_history_item.click()

    # ====================
    # WORKFLOW ACTIONS
    # ====================

    @step
    def update_workflow(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_url: Optional[str] = None,
        yaml_config: Optional[str] = None,
        shared: Optional[bool] = None,
        project_name: Optional[str] = None,
    ):
        """
        Update workflow with provided details.
        Only updates fields that are provided (not None).

        Args:
            name: Workflow name (optional)
            description: Workflow description (optional)
            icon_url: Icon URL (optional)
            yaml_config: YAML configuration (optional)
            shared: Whether to share with project team (optional)
            project_name: Project name (optional)
        """
        if project_name:
            self.search_and_select_project(project_name)

        if name:
            self.fill_name(name)

        if description:
            self.fill_description(description)

        if icon_url:
            self.fill_icon_url(icon_url)

        if yaml_config:
            self.fill_yaml_config(yaml_config)

        if shared is not None:
            current_state = self.shared_switch.is_checked()
            if current_state != shared:
                self.toggle_shared_switch()

        self.click_update()

    # ====================
    # VERIFICATION METHODS
    # ====================

    @step
    def should_be_on_edit_workflow_page(self):
        """Verify that we are on the Edit Workflow page."""
        expect(self.page_title).to_be_visible()
        expect(self.update_button).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        expect(self.back_button).to_be_visible()

    @step
    def should_have_header_elements_visible(self):
        """Verify that all header elements are visible."""
        expect(self.back_button).to_be_visible()
        expect(self.page_title).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        expect(self.update_button).to_be_visible()

    @step
    def should_have_yaml_tabs_visible(self):
        """Verify that the YAML configuration tabs are visible."""
        expect(self.yaml_tabs_container).to_be_visible()
        expect(self.edit_current_version_tab).to_be_visible()
        expect(self.history_tab).to_be_visible()

    @step
    def should_have_current_version_tab_active(self):
        """Verify that the Edit Current Version tab is active."""
        expect(self.edit_current_version_tab).to_have_class(
            re.compile(r"border-text-main")
        )
        expect(self.current_tab_content).to_be_visible()
        expect(self.history_tab_content).to_have_class(re.compile(r"hidden"))

    @step
    def should_have_history_tab_active(self):
        """Verify that the History tab is active."""
        expect(self.history_tab).to_have_class(re.compile(r"border-text-main"))
        expect(self.history_tab_content).to_be_visible()
        expect(self.current_tab_content).to_have_class(re.compile(r"hidden"))

    @step
    def should_have_update_button_enabled(self):
        """Verify that the update button is enabled."""
        expect(self.update_button).to_be_enabled()

    @step
    def should_have_update_button_disabled(self):
        """Verify that the update button is disabled."""
        expect(self.update_button).to_be_disabled()

    @step
    def should_preserve_form_data_after_tab_switch(self, name: str, description: str):
        """Verify that form data is preserved after switching tabs."""
        # Switch to history tab and back
        self.click_history_tab()
        self.click_edit_current_version_tab()

        # Verify data is preserved
        self.should_have_name_field_value(name)
        self.should_have_description_field_value(description)

    @step
    def should_have_history_tab_content_visible(self):
        """Verify that history tab content is visible."""
        expect(self.history_version_dropdown).to_be_visible()
        expect(self.history_version_dropdown_button).to_be_visible()
        expect(self.restore_button).to_be_visible()
        expect(self.history_yaml_editor).to_be_visible()

    @step
    def should_have_restore_button_enabled(self):
        """Verify that the restore button is enabled."""
        expect(self.restore_button).to_be_enabled()

    @step
    def should_have_history_yaml_content(self, expected_content: Optional[str] = None):
        """Verify that history YAML editor has content."""
        expect(self.history_yaml_editor).to_be_visible()
        if expected_content:
            expect(self.history_yaml_content).to_contain_text(
                expected_content.replace("\n", "")
            )
        else:
            expect(self.history_yaml_content).to_be_visible()

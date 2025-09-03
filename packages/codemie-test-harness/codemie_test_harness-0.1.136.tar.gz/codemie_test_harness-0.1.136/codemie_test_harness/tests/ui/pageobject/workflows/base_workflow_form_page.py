import platform
from playwright.sync_api import Page, Locator, expect
from reportportal_client import step
from typing import Optional

from codemie_test_harness.tests.ui.pageobject.base_page import BasePage
from codemie_test_harness.tests.ui.pageobject.components import WorkflowSidebar


class BaseWorkflowFormPage(BasePage):
    """Base class for workflow form pages with common elements and methods."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.sidebar = WorkflowSidebar(page)

    # ==============================================
    # PROPERTIES - UI ELEMENTS
    # ==============================================

    # ------ Header Elements ------

    @property
    def cancel_button(self) -> Locator:
        """Cancel button in the header."""
        return self.page.locator('button.button.secondary.medium:has-text("Cancel")')

    # ------ Project Selection Elements ------
    @property
    def project_dropdown(self):
        """Project selection dropdown."""
        return self.page.locator("#project")

    @property
    def project_dropdown_trigger(self):
        """Project dropdown trigger button."""
        return self.page.locator("#project .p-multiselect-trigger")

    @property
    def project_label(self):
        """Selected project label in dropdown."""
        return self.page.locator("#project .p-multiselect-label")

    @property
    def project_dropdown_panel(self):
        """Project dropdown panel that opens when clicking the dropdown."""
        return self.page.locator(".p-multiselect-panel")

    @property
    def project_search_input(self):
        """Search input in the project dropdown panel."""
        return self.page.locator(".p-multiselect-filter")

    @property
    def first_project(self):
        """First project in the list"""
        return self.page.locator(".p-multiselect-item").first

    # ------ Shared Switch Elements ------
    @property
    def shared_switch(self) -> Locator:
        """Shared with Project Team switch."""
        return self.page.locator("//input[@id='shared']")

    @property
    def shared_switch_label(self) -> Locator:
        """Shared with Project Team switch label."""
        return self.page.locator("//label[@id='shared']")

    # ------ Name Field Elements ------
    @property
    def name_input(self) -> Locator:
        """Name input field."""
        return self.page.locator("#name")

    @property
    def name_field_label(self) -> Locator:
        """Name field label."""
        return self.page.locator('div.text-sm.font-semibold:has-text("Name")')

    @property
    def name_error_message(self):
        """Name field error message."""
        return self.page.locator(".input-field-wrapper:has(#name) .input-error-message")

    # ------ Description Field Elements ------
    @property
    def description_textarea(self) -> Locator:
        """Description textarea field."""
        return self.page.locator("#description")

    @property
    def description_field_label(self) -> Locator:
        """Description field label."""
        return self.page.locator('div.text-sm.font-semibold:has-text("Description")')

    # ------ Icon URL Field Elements ------
    @property
    def icon_url_input(self) -> Locator:
        """Icon URL input field."""
        return self.page.locator("#icon_url")

    @property
    def icon_url_field_label(self) -> Locator:
        """Icon URL field label."""
        return self.page.locator('div.text-sm.font-semibold:has-text("Icon URL")')

    @property
    def icon_url_error_message(self):
        """Icon URL field error message."""
        return self.page.locator(
            ".input-field-wrapper:has(#icon_url) .input-error-message"
        )

    # ------ Workflow Mode Elements ------
    @property
    def workflow_mode_dropdown(self) -> Locator:
        """Workflow Mode dropdown."""
        return self.page.locator('.p-dropdown[data-pc-name="dropdown"]')

    @property
    def workflow_mode_label(self) -> Locator:
        """Workflow Mode field label."""
        return self.page.locator('div.text-sm.font-semibold:has-text("Workflow Mode")')

    @property
    def workflow_mode_selected_value(self) -> Locator:
        """Currently selected workflow mode value."""
        return self.page.locator(".p-dropdown-label")

    @property
    def workflow_mode_info_icon(self) -> Locator:
        """Information icon next to workflow mode."""
        return self.page.locator(".scale-105.opacity-75 svg")

    @property
    def workflow_mode_description(self) -> Locator:
        """Workflow mode description text."""
        return self.page.locator(".flex.w-full.px-2.gap-2 .text-text-secondary.text-sm")

    # ------ YAML Configuration Elements ------
    @property
    def yaml_config_header(self) -> Locator:
        """YAML Configuration section header."""
        return self.page.locator(
            'div.text-sm.font-semibold:has-text("YAML Configuration")'
        )

    @property
    def yaml_editor(self) -> Locator:
        """YAML configuration editor."""
        return self.page.locator("#yaml_config.ace_editor")

    @property
    def yaml_textarea(self) -> Locator:
        """YAML configuration textarea (hidden input)."""
        return self.page.locator("#yaml_config .ace_text-input")

    @property
    def yaml_content(self) -> Locator:
        """YAML configuration content area."""
        return self.page.locator("#yaml_config .ace_content")

    @property
    def yaml_gutter(self) -> Locator:
        """YAML editor line numbers gutter."""
        return self.page.locator("#yaml_config .ace_gutter")

    # ------ Workflow Visualization Elements ------
    @property
    def visualization_header(self) -> Locator:
        """Workflow visualization section header."""
        return self.page.locator('div.text-sm:has-text("Workflow visualisation")')

    @property
    def visualize_button(self) -> Locator:
        """Visualize button."""
        return self.page.locator('button.button.secondary.large:has-text("Visualize")')

    @property
    def visualization_placeholder(self) -> Locator:
        """Workflow visualization placeholder area."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div"
        )

    @property
    def visualization_placeholder_text(self) -> Locator:
        """Visualization placeholder text."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div/div[text()=' Workflow visualisation']"
        )

    @property
    def workflow_diagram(self) -> Locator:
        """Workflow diagram image."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div//img[@alt='Workflow Diagram']"
        )

    @property
    def reset_zooming(self) -> Locator:
        """Reset zooming button in visualization."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div/div/div/ul/li[2]"
        )

    @property
    def zoom_in_button(self) -> Locator:
        """Zoom in button in visualization."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div/div/div/ul/li[3]"
        )

    @property
    def zoom_out_button(self) -> Locator:
        """Zoom out button in visualization."""
        return self.page.locator(
            "//div[text()=' Workflow visualisation ']/../following-sibling::div/div/div/ul/li[4]"
        )

    # ==============================================
    # METHODS - ACTIONS & INTERACTIONS
    # ==============================================

    # ------ Header Actions ------
    @step
    def click_back(self):
        """Click the back button."""
        self.back_button.click()

    @step
    def click_cancel(self):
        """Click the cancel button."""
        self.cancel_button.click()

    # ------ Project Selection Actions ------
    @step
    def search_and_select_project(self, search_term: str):
        """Search for a project and select the first matching result."""
        # Open the dropdown
        self.project_dropdown_trigger.click()
        # Wait for the dropdown panel to be visible
        expect(self.project_dropdown_panel).to_be_visible()

        # Type in the search input
        self.project_search_input.fill(search_term)

        # Select the first visible project item
        expect(self.first_project).to_be_visible()
        self.first_project.click()

        # Wait for dropdown to close
        expect(self.project_dropdown_panel).not_to_be_visible()

    # ------ Shared Switch Actions ------
    @step
    def toggle_shared_switch(self):
        """Toggle the 'Shared with Project Team' switch."""
        self.shared_switch_label.click()

    # ------ Form Field Actions ------
    @step
    def fill_name(self, name: str):
        """Fill the workflow name field."""
        self.name_input.fill(name)

    @step
    def fill_description(self, description: str):
        """Fill the workflow description field."""
        self.description_textarea.fill(description)

    @step
    def fill_icon_url(self, icon_url: str):
        """Fill the icon URL field."""
        self.icon_url_input.fill(icon_url)

    # ------ Workflow Mode Actions ------
    @step
    def select_workflow_mode(self, mode: Optional[str] = None):
        """Select workflow mode from dropdown. If mode is None, just click to open."""
        self.workflow_mode_dropdown.click()
        if mode:
            self.page.locator(f'li:has-text("{mode}")').click()

    # ------ YAML Configuration Actions ------
    @step
    def fill_yaml_config(self, yaml_content: str):
        """Fill YAML configuration in the editor."""
        # Click on the editor to focus it
        self.yaml_editor.click()
        # Clear existing content and type new content
        # Detect the OS
        is_mac = platform.system() == "Darwin"
        # Use Meta for macOS, Control for Linux/Windows
        key = "Meta" if is_mac else "Control"

        self.page.keyboard.press(f"{key}+A")
        self.yaml_textarea.fill(yaml_content)

    # ------ Visualization Actions ------
    @step
    def click_visualize(self):
        """Click the visualize button."""
        self.visualize_button.click()

    # ==============================================
    # METHODS - VERIFICATION & ASSERTIONS
    # ==============================================

    # ------ Project Selection Verifications ------
    @step
    def should_see_project_selected(self, project_name: str):
        """Verify the currently selected project name."""
        expect(self.project_label).to_have_text(project_name)

    @step
    def should_have_project_dropdown_visible(self):
        """Verify that the project dropdown is visible."""
        expect(self.project_dropdown).to_be_visible()

    @step
    def should_have_project_selected(self, project_name: str):
        """Verify that the specified project is selected."""
        expect(self.project_label).to_have_text(project_name)

    # ------ Shared Switch Verifications ------
    @step
    def should_have_shared_switch_checked(self):
        """Verify that the shared switch is checked."""
        expect(self.shared_switch).to_be_checked()

    @step
    def should_have_shared_switch_unchecked(self):
        """Verify that the shared switch is unchecked."""
        expect(self.shared_switch).not_to_be_checked()

    # ------ Form Field Verifications ------
    @step
    def should_have_name_field_value(self, expected_value: str):
        """Verify that the name field has the expected value."""
        expect(self.name_input).to_have_value(expected_value)

    @step
    def should_have_empty_name_field(self):
        """Verify that the name field is empty."""
        expect(self.name_input).to_have_value("")

    @step
    def should_have_description_field_value(self, expected_value: str):
        """Verify that the description field has the expected value."""
        expect(self.description_textarea).to_have_value(expected_value)

    @step
    def should_have_empty_description_field(self):
        """Verify that the description field is empty."""
        expect(self.description_textarea).to_have_value("")

    @step
    def should_have_icon_url_field_value(self, expected_value: str):
        """Verify that the icon URL field has the expected value."""
        expect(self.icon_url_input).to_have_value(expected_value)

    @step
    def should_have_empty_icon_url_field(self):
        """Verify that the icon URL field is empty."""
        expect(self.icon_url_input).to_have_value("")

    # ------ Workflow Mode Verifications ------
    @step
    def should_have_workflow_mode_dropdown_visible(self):
        """Verify that the workflow mode dropdown is visible."""
        expect(self.workflow_mode_dropdown).to_be_visible()

    @step
    def should_have_workflow_mode_selected(self, mode: str):
        """Verify that the specified workflow mode is selected."""
        expect(self.workflow_mode_selected_value).to_have_text(mode)

    @step
    def should_show_workflow_mode_info(self):
        """Verify that workflow mode information is displayed."""
        expect(self.workflow_mode_info_icon).to_be_visible()
        expect(self.workflow_mode_description).to_be_visible()
        expect(self.workflow_mode_description).to_contain_text(
            "Sequential Mode offers full control. You define the workflow, choosing assistants and setting each step. "
            "It's perfect for tasks needing specific, orderly execution. Opt for this when detail and sequence matter."
        )

    # ------ YAML Configuration Verifications ------
    @step
    def should_have_yaml_editor_visible(self):
        """Verify that the YAML editor is visible."""
        expect(self.yaml_editor).to_be_visible()
        expect(self.yaml_config_header).to_be_visible()
        expect(self.yaml_content).to_be_visible()
        expect(self.yaml_textarea).to_be_visible()
        expect(self.yaml_gutter).to_be_visible()

    @step
    def should_have_yaml_editor_with_content(self, yaml_config=None):
        """Verify that the YAML editor has content."""
        expect(self.yaml_editor).to_be_visible()
        if yaml_config:
            expect(self.yaml_content).to_have_text(yaml_config.replace("\n", ""))
        else:
            expect(self.yaml_content).to_be_visible()
        # Check that there are line numbers indicating content
        expect(self.yaml_gutter).to_be_visible()

    # ------ Visualization Verifications ------
    @step
    def should_have_visualization_section_visible(self):
        """Verify that the workflow visualization section is visible."""
        expect(self.visualization_header).to_be_visible()
        expect(self.visualize_button).to_be_visible()
        expect(self.visualization_placeholder).to_be_visible()
        expect(self.visualization_placeholder_text).to_be_visible()

    @step
    def should_have_workflow_diagram_visible(self):
        """Verify that the workflow diagram is visible with zoom controls."""
        expect(self.visualization_header).to_be_visible()
        expect(self.visualize_button).to_be_visible()
        expect(self.workflow_diagram).to_be_visible()
        expect(self.reset_zooming).to_be_visible()
        expect(self.zoom_in_button).to_be_visible()
        expect(self.zoom_out_button).to_be_visible()

    # ------ Error Message Verifications ------
    @step
    def should_show_validation_error_for_name(self, error_message: str):
        """Verify that validation error is shown for the name field."""
        expect(self.name_error_message).to_have_text(error_message)

    @step
    def should_show_validation_error_for_icon_url(self, error_message: str):
        """Verify that validation error is shown for the icon URL field."""
        expect(self.icon_url_error_message).to_have_text(error_message)

    # ------ General Form Verifications ------
    @step
    def should_have_all_form_sections_visible(self):
        """Verify that all main form sections are visible."""
        expect(self.name_field_label).to_be_visible()
        expect(self.description_field_label).to_be_visible()
        expect(self.icon_url_field_label).to_be_visible()
        expect(self.workflow_mode_label).to_be_visible()
        expect(self.yaml_config_header).to_be_visible()
        expect(self.visualization_header).to_be_visible()
        return self

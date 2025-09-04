from playwright.sync_api import expect
from reportportal_client import step

from codemie_test_harness.tests.ui.pageobject.workflows.base_workflow_form_page import (
    BaseWorkflowFormPage,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


class CreateWorkflowPage(BaseWorkflowFormPage):
    """Page object for the Create Workflow page."""

    page_url = "#/workflows/new"

    def __init__(self, page):
        super().__init__(page)

    # ==================== PROPERTIES ====================
    # Header elements specific to Create page
    @property
    def page_title(self):
        """Page title 'Create Workflow'."""
        return self.page.locator("div.flex-1.text-lg")

    @property
    def create_button(self):
        """Create button in the header."""
        return self.page.locator('button.button.primary.medium:has-text("Create")')

    # ==================== NAVIGATION METHODS ====================
    @step
    def navigate_to(self):
        """Navigate to the Create Workflow page."""
        self.page.goto(self.page_url)

    # ==================== INTERACTION METHODS ====================
    @step
    def click_create(self):
        """Click the create button."""
        self.create_button.click()

    @step
    def create_workflow(
        self,
        name: str = "",
        project_name: str = "",
        description: str = "",
        icon_url: str = "",
        yaml_config: str = "",
        shared: bool = False,
    ):
        """
        Complete workflow creation with provided details.

        Args:
            name: Workflow name (required)
            project_name: Project name (optional)
            description: Workflow description (optional)
            icon_url: Icon URL (optional)
            yaml_config: YAML configuration (optional)
            shared: Whether to share with project team (optional)
        """

        name = name or get_random_name()
        self.fill_name(name)

        if project_name:
            self.search_and_select_project(project_name)

        if description:
            self.fill_description(description)

        if icon_url:
            self.fill_icon_url(icon_url)

        if yaml_config:
            self.fill_yaml_config(yaml_config)

        if shared:
            self.toggle_shared_switch()

        self.click_create()

    # ==================== VERIFICATION METHODS ====================
    @step
    def should_be_on_create_workflow_page(self, title):
        """Verify that we are on the Create Workflow page."""
        expect(self.page_title).to_have_text(title)
        expect(self.create_button).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        return self

    @step
    def should_have_header_elements_visible(self):
        """Verify that all header elements are visible."""
        expect(self.back_button).to_be_visible()
        expect(self.page_title).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        expect(self.create_button).to_be_visible()

    @step
    def should_have_navigation_buttons_visible(self):
        """Verify that all navigation buttons are visible."""
        expect(self.back_button).to_be_visible()
        expect(self.cancel_button).to_be_visible()
        expect(self.create_button).to_be_visible()

    @step
    def should_have_entered_yaml_configuration(self, expected_configuration: str):
        """Verify that content of YAML editor."""
        expect(self.yaml_content).to_have_text(expected_configuration.replace("\n", ""))

    @step
    def should_have_create_button_enabled(self):
        """Verify that the create button is enabled."""
        expect(self.create_button).to_be_enabled()

    @step
    def should_have_create_button_disabled(self):
        """Verify that the create button is disabled."""
        expect(self.create_button).to_be_disabled()

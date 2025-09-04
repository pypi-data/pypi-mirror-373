from reportportal_client import step

from codemie_test_harness.tests.ui.pageobject.base_page import BasePage
from playwright.sync_api import Page, expect

from codemie_test_harness.tests.ui.pageobject.workflows.workflows_page import (
    WorkflowsPage,
)


class WorkflowTemplatesPage(BasePage):
    """Page object for the Workflow Templates page."""

    page_url = "#/workflows/templates"

    def __init__(self, page: Page):
        super().__init__(page)

    # ==================== PROPERTIES ====================

    @property
    def templates_list(self):
        return self.page.locator("//section/div")

    @property
    def templates_create_list(self):
        return self.templates_list.locator("//button")

    # ==================== NAVIGATION METHODS ====================
    @step
    def navigate_to(self):
        """Navigate to the workflow templates page."""
        self.page.goto(self.page_url)

    @step
    def click_create_workflow_from_template(self, index: int):
        """Verify that user on workflow templates page can create new workflow template."""
        self.templates_create_list.nth(index).click()

    # ==================== INTERACTION METHODS ====================
    @step
    def template_details_click(self, index: int):
        """Verify that user on workflow templates page can click on template page."""
        self.templates_list.nth(index).click()

    @step
    def click_create_workflow_from_specific_template(self, template_name: str):
        """Verify that user on workflow templates page can create new workflow template."""
        self.page.locator(
            f"//div[text()='{template_name}']/following::button[@type='button'][1]"
        ).click()

    # ==================== VERIFICATION METHODS ====================
    @step
    def should_have_templates(self, count):
        """Verify that workflow templates page have predefined workflows."""
        expect(self.templates_list).to_have_count(count)

    @step
    def should_have_title_description(
        self, index: int, title: str, description: str, tooltip_description: str
    ):
        """Verify that workflow templates have titles."""
        workflow_page = WorkflowsPage(self.page)
        workflow_card = workflow_page.get_workflow_card_by_index(index)
        expect(workflow_card.title).to_have_text(title)
        expect(workflow_card.description).to_contain_text(description)
        workflow_page.hover_workflow_card(index)
        expect(workflow_card.description_tooltip).to_have_text(tooltip_description)

from playwright.sync_api import expect
from reportportal_client import step

from codemie_test_harness.tests.ui.pageobject.base_page import BasePage


class WorkflowTemplateDetailsPage(BasePage):
    """Page object for the Workflow Template Details page."""

    page_url = "#/workflows/templates/"

    def __init__(self, page):
        """Initialize the WorkflowTemplateDetailsPage."""
        super().__init__(page)

    # ==================== PROPERTIES ====================
    @property
    def page_title(self):
        return self.page.locator("div.text-lg")

    @property
    def create_workflow_button(self):
        return self.page.locator(
            "//button[@class='button base medium' and @type='button']"
        )

    @property
    def back_button(self):
        return self.page.locator(
            "//button[@class='button secondary medium' and @type='button']"
        )

    @property
    def template_icon(self):
        return self.page.locator("//img[@alt = 'avatar']")

    @property
    def yaml_config(self):
        return self.page.locator("pre.code-content.language-yaml > code.language-yaml")

    @property
    def copy_code_button(self):
        return self.page.locator("//button[text()=' Copy code ']")

    @property
    def download_yaml_code_button(self):
        return self.page.locator("//button[text()=' Download ']")

    @property
    def link_to_workflow_template_button(self):
        return self.page.locator(
            "//div[contains(text(), 'Link to workflow template')]/following-sibling::label//button"
        )

    @property
    def link_to_video_template_field(self):
        return self.page.locator("//div[contains(text(), 'Link to Video')]")

    @property
    def link_to_video_template_button(self):
        return self.link_to_video_template_field.locator(
            "//following-sibling::label//button"
        )

    @property
    def template_title(self):
        return self.page.locator("div.text-2xl")

    @property
    def about_workflow(self):
        return self.page.locator("div.text-sm.text-text-tertiary")

    # ==================== INTERACTION METHODS ====================
    @step
    def get_template_title(self) -> str:
        """Verify that user on workflow templates page can get template title."""
        return self.template_title.inner_text()

    # ==================== VERIFICATION METHODS ====================
    @step
    def should_have_template_header(self):
        """Verify workflow templates has given functionality."""
        expect(self.page_title).to_have_text("Workflow Template Details")
        expect(self.create_workflow_button).to_be_visible()
        expect(self.create_workflow_button).to_be_enabled()
        expect(self.back_button).to_be_visible()
        expect(self.back_button).to_be_enabled()

    @step
    def should_have_template_details(self, template_title, description, yaml_config):
        expect(self.template_title).to_have_text(template_title)
        expect(self.about_workflow).to_have_text(description)
        expect(self.template_icon).to_be_visible()
        expect(self.yaml_config).to_have_text(yaml_config)
        expect(self.copy_code_button).to_be_visible()
        expect(self.copy_code_button).to_be_enabled()
        expect(self.download_yaml_code_button).to_be_visible()
        expect(self.download_yaml_code_button).to_be_enabled()

    @step
    def should_have_template_sidebar(self):
        expect(self.link_to_workflow_template_button).to_be_visible()
        expect(self.link_to_workflow_template_button).to_be_enabled()
        if self.link_to_video_template_field.is_visible():
            expect(self.link_to_video_template_button).to_be_visible()
            expect(self.link_to_video_template_button).to_be_enabled()

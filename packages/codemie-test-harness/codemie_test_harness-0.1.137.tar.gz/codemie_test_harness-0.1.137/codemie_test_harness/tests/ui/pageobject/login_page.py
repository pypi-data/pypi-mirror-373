from reportportal_client import step
from playwright.sync_api import expect

from codemie_test_harness.tests.ui.pageobject.assistants.assistants_page import (
    AssistantsPage,
)
from codemie_test_harness.tests.ui.pageobject.base_page import BasePage


class LoginPage(BasePage):
    """Login page object with property-based element locators."""

    page_url = "/"

    def __init__(self, page):
        super().__init__(page)

    # Page elements using @property decorator
    @property
    def more_options_button(self):
        """Username input field."""
        return self.page.locator('//button[text()="More options"]')

    @property
    def username_input(self):
        """Username input field."""
        return self.page.locator("#username")

    @property
    def password_input(self):
        """Password input field."""
        return self.page.locator("#password")

    @property
    def submit_button(self):
        """Login submit button."""
        return self.page.locator('button[type="submit"]')

    @property
    def login_form(self):
        """Main login form container."""
        return self.page.locator("form")

    @property
    def error_message(self):
        """Error message display."""
        return self.page.locator(".error-message, .alert-danger")

    # Navigation methods
    @step
    def navigate_to(self):
        """Navigate to the login page."""
        self.page.goto(self.page_url)
        return self

    # Action methods
    @step
    def fill_username(self, username: str):
        """Fill the username field."""
        self.username_input.fill(username)
        return self

    @step
    def fill_password(self, password: str):
        """Fill the password field."""
        self.password_input.fill(password)
        return self

    @step
    def click_submit(self):
        """Click the submit button."""
        self.submit_button.click()
        return self

    @step
    def login(self, username: str, password: str):
        """Complete login process with username and password."""
        self.more_options_button.click()
        self.fill_username(username)
        self.fill_password(password)
        self.click_submit()
        return AssistantsPage(self.page)

    # Verification methods
    @step
    def should_be_on_login_page(self):
        """Verify that we are on the login page."""
        expect(self.login_form).to_be_visible()
        expect(self.username_input).to_be_visible()
        expect(self.password_input).to_be_visible()
        expect(self.submit_button).to_be_visible()
        return self

    @step
    def should_have_error_message(self, error_text: str = None):
        """Verify that an error message is displayed."""
        expect(self.error_message).to_be_visible()
        if error_text:
            expect(self.error_message).to_contain_text(error_text)
        return self

    @step
    def should_not_have_error_message(self):
        """Verify that no error message is displayed."""
        expect(self.error_message).to_be_hidden()
        return self

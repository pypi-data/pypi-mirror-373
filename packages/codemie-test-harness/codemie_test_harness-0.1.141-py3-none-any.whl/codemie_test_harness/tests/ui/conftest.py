import logging
import os
import pytest
from datetime import datetime

from codemie_test_harness.tests.ui.pageobject.login_page import LoginPage

from reportportal_client import RPLogger, RPLogHandler

# Create ReportPortal logger
logging.setLoggerClass(RPLogger)
rp_logger = logging.getLogger("reportportal_logger")
rp_logger.setLevel(logging.DEBUG)
rp_logger.addHandler(RPLogHandler())


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    """Capture screenshot on test failure"""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name

        # Create screenshots directory
        screenshot_dir = "test_screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        # Capture screenshot
        screenshot_file_path = os.path.join(
            screenshot_dir, f"failure_{test_name}_{timestamp}.png"
        )

        page.screenshot(path=screenshot_file_path, full_page=True)
        with open(screenshot_file_path, "rb") as image_file:
            file_data = image_file.read()
            rp_logger.info(
                f"Test failed - Screenshot captured: {test_name}",
                attachment={
                    "name": f"{test_name}_failure_screenshot.png",
                    "data": file_data,
                    "mime": "image/png",
                },
            )


@pytest.fixture(autouse=True)
def login(page):
    page = LoginPage(page)
    page.navigate_to()
    page.login(os.getenv("AUTH_USERNAME"), os.getenv("AUTH_PASSWORD"))
    page.should_see_new_release_popup()
    page.pop_up.close_popup()
    page.should_not_see_new_release_popup()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("FRONTEND_URL")


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "headless": os.getenv("HEADLESS", "false").lower() == "true",
        "slow_mo": 150,
    }

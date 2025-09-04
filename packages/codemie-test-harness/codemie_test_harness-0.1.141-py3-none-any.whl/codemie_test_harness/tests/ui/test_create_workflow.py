import os

import pytest

from codemie_test_harness.tests.ui.pageobject.workflows.workflows_page import (
    WorkflowsPage,
)
from codemie_test_harness.tests.ui.pageobject.workflows.create_workflow_page import (
    CreateWorkflowPage,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.ui
def test_create_workflow_page_elements_visibility(page):
    """Test that all main elements are visible on Create Workflow page."""
    expected_create_workflow_title = "Create Workflow"
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Verify we are on the correct page
    create_page.should_be_on_create_workflow_page(expected_create_workflow_title)

    # Verify header elements
    create_page.should_have_header_elements_visible()

    # Verify all form sections are visible
    create_page.should_have_all_form_sections_visible()

    # Verify common components
    create_page.should_have_header_visible()
    create_page.sidebar.should_be_visible()
    create_page.sidebar.should_have_workflows_title()


@pytest.mark.ui
def test_create_workflow_form_interactions(page):
    """Test form field interactions and input validation."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test name field interaction
    test_name = "Test Workflow"
    create_page.fill_name(test_name)
    create_page.should_have_name_field_value(test_name)

    # Test description field interaction
    test_description = "This is a test workflow description"
    create_page.fill_description(test_description)
    create_page.should_have_description_field_value(test_description)

    # Test icon URL field interaction
    test_icon_url = "https://example.com/icon.png"
    create_page.fill_icon_url(test_icon_url)
    create_page.should_have_icon_url_field_value(test_icon_url)

    # Test shared switch interaction
    create_page.toggle_shared_switch()
    create_page.should_have_shared_switch_checked()

    # Toggle back to unchecked
    create_page.toggle_shared_switch()
    create_page.should_have_shared_switch_unchecked()


@pytest.mark.ui
def test_create_workflow_dropdowns_interaction(page):
    """Test dropdown interactions for project and workflow mode."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test project dropdown interaction
    create_page.should_have_project_dropdown_visible()

    # Test project search functionality
    create_page.search_and_select_project(os.getenv("PROJECT_NAME"))
    create_page.should_see_project_selected(os.getenv("PROJECT_NAME"))

    create_page.should_have_workflow_mode_dropdown_visible()
    create_page.select_workflow_mode()  # Just opens dropdown
    create_page.page_title.click()

    # Verify the default selection is maintained
    create_page.should_have_workflow_mode_selected("Sequential")


@pytest.mark.ui
def test_create_workflow_yaml_editor_functionality(page):
    """Test YAML editor functionality."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Verify YAML editor section
    create_page.should_have_yaml_editor_visible()

    # Test YAML editor interaction
    test_yaml = """
        workflow:
        name: Test Workflow
        description: Basic test workflow
    """
    create_page.fill_yaml_config(test_yaml)

    # Verify YAML editor is still visible after input
    create_page.should_have_entered_yaml_configuration(test_yaml)


@pytest.mark.ui
def test_create_workflow_visualization_section(page):
    """Test workflow visualization section functionality."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Verify visualization section elements
    create_page.should_have_visualization_section_visible()

    # Test visualize button interaction
    create_page.click_visualize()

    # Verify visualization section is still visible after click
    create_page.should_have_visualization_section_visible()


@pytest.mark.ui
def test_create_workflow_navigation_buttons(page):
    """Test navigation button interactions."""
    workflows_page = WorkflowsPage(page)
    workflows_page.navigate_to()
    create_page = workflows_page.click_create_workflow()

    # Verify buttons are enabled/visible
    create_page.should_have_navigation_buttons_visible()

    # Test back button (should navigate away)
    create_page.click_back()
    # Verify we are redirected (URL should change)
    workflows_page.should_have_url_containing("#/workflows/my")

    # Navigate back to test cancel button
    create_page = workflows_page.click_create_workflow()
    create_page.click_cancel()
    # Verify we are redirected (URL should change)
    create_page.should_have_url_containing("#/workflows/my")


@pytest.mark.ui
def test_create_workflow_sidebar_functionality(page):
    """Test sidebar functionality from Create Workflow page."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test sidebar visibility and structure
    create_page.sidebar.should_be_visible()
    create_page.sidebar.should_have_workflows_title()
    create_page.sidebar.should_have_categories_section()

    # Test category navigation from sidebar
    create_page.sidebar.navigate_to_my_workflows()
    create_page.should_have_url_containing("#/workflows/my")

    # Navigate back to create workflow
    create_page.navigate_to()
    create_page.sidebar.navigate_to_all_workflows()
    create_page.should_have_url_containing("#/workflows/all")


@pytest.mark.ui
def test_create_workflow_header_navigation(page):
    """Test header navigation from Create Workflow page."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test header component visibility
    create_page.should_have_header_visible()
    create_page.header.should_be_visible()
    create_page.header.should_have_complete_navigation_structure()

    # Test navigation to other sections
    create_page.header.navigate_to_assistants()
    create_page.should_have_url_containing("#/assistants")

    # Navigate back to create workflow
    create_page.navigate_to()
    create_page.header.navigate_to_workflows()
    create_page.should_have_url_containing("#/workflows")


@pytest.mark.ui
def test_create_workflow_workflow_mode_information(page):
    """Test workflow mode information display."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test workflow mode information display
    create_page.should_show_workflow_mode_info()


@pytest.mark.ui
def test_create_workflow_default_field_values(page):
    """Test default field values on page load."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test default empty field values
    create_page.should_have_empty_name_field()
    create_page.should_have_empty_description_field()
    create_page.should_have_empty_icon_url_field()

    # Test default shared switch state
    create_page.should_have_shared_switch_unchecked()

    # Test default workflow mode selection
    create_page.should_have_workflow_mode_selected("Sequential")


@pytest.mark.ui
def test_create_workflow_button_states(page):
    """Test create button enabled/disabled states."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    # Test create button initial state (should be enabled by default)
    create_page.should_have_create_button_enabled()

    # Test create button after filling required fields
    create_page.fill_name("Test Workflow")
    create_page.should_have_create_button_enabled()

    # Test create button after filling required fields
    create_page.fill_name("")
    create_page.should_have_create_button_disabled()


@pytest.mark.ui
def test_create_workflow_form_validation(page):
    """Test form validation scenarios."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    create_page.fill_name("Test Workflow")
    create_page.fill_name("")
    create_page.should_show_validation_error_for_name("Name is required")

    create_page.fill_icon_url("Test")
    create_page.should_show_validation_error_for_icon_url(
        "Icon URL must be a valid URL"
    )


@pytest.mark.ui
def test_create_workflow_complete_workflow_creation(page):
    """Test complete workflow creation using the create_workflow method."""
    create_page = CreateWorkflowPage(page)
    create_page.navigate_to()

    workflow_name = get_random_name()
    # Test complete workflow creation
    yaml_config = """assistants:
  - id: business_analyst # ID of assistant inside this configuration
    system_prompt: ""
  - id: onboarder
    system_prompt: ""
  - id: requirement_analyzer
    system_prompt: ""

states:
  - id: onboarder # ID of state inside this configuration
    assistant_id: onboarder
    task: |
      Find all relevant information about workflow implementation and describe
      like for business analyst as a requirements description.
      Provide a list of main requirement categories to analyze further.
    output_schema: |
      {
        "requirements": "List of main requirement categories"
      }
    next:
      state_id: requirement_analyzer # ID of next state
      iter_key: requirements # Key for iteration, must be same as in schema
  - id: requirement_analyzer # ID of state inside this configuration
    assistant_id: requirement_analyzer
    task: |
      Analyze the given requirement category in detail.
      Provide a comprehensive description for QA engineers, support team, and
      users on how to use this specific aspect of the workflow functionality.
    output_schema: |
      {
        "category": "Name of the requirement category",
        "analysis": "Detailed analysis and description of the requirement"
      }
    next:
      state_id: business_analyst # ID of next state
  - id: business_analyst # ID of state inside this configuration
    assistant_id: business_analyst
    task: |
      Compile all the requirement analyses into a comprehensive description for
      QA engineers, support team, and users on how to use this functionality.
      Create a comment for Jira ticket CODEMIE-1350 with key points.
    output_schema: |
      {
        "success": "Boolean true | false. If you created Jira comment successfully return true, otherwise false",
        "comment_body": "Return comment body which you left in Jira"
      }
    next:
      condition:
        expression: "success == True"
        then: end
        otherwise: business_analyst


"""

    create_page.create_workflow(
        project_name=os.getenv("PROJECT_NAME"),
        name=workflow_name,
        description="This is a complete test workflow",
        icon_url="https://example.com/test-icon.png",
        yaml_config=yaml_config,
        shared=True,
    )

    workflows_page = WorkflowsPage(page)
    workflows_page.should_be_on_workflows_page()
    workflows_page.should_see_workflow_card(workflow_name)

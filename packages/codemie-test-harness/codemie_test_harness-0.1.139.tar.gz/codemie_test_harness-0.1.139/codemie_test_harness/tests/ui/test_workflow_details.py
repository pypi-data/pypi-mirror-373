"""Tests for Workflow Details page including Executions and Configuration tabs.

This module contains UI tests for the Workflow Details page functionality including:
- Executions tab: viewing workflow execution history, status, actions
- Configuration tab: viewing workflow YAML configuration, graph schema, and metadata
"""

import os

import pytest

from codemie_sdk.models.workflow import WorkflowMode
from codemie_test_harness.tests import TEST_USER, PROJECT
from codemie_test_harness.tests.ui.pageobject.workflows import WorkflowDetailsPage
from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.yaml_utils import (
    AssistantModel,
    StateModel,
    WorkflowYamlModel,
    prepare_yaml_content,
)


@pytest.fixture(scope="session")
def test_workflow(workflow_utils, default_llm):
    assistant_and_state_name = "branch_creator"

    assistant = AssistantModel(
        id=assistant_and_state_name,
        model=default_llm.base_name,
        system_prompt="You are helpful assistant",
    )

    state = StateModel(
        id=assistant_and_state_name,
        assistant_id=assistant_and_state_name,
    )

    workflow_yaml = WorkflowYamlModel(
        assistants=[assistant],
        states=[state],
    )

    yaml_content = prepare_yaml_content(workflow_yaml.model_dump(exclude_none=True))

    created_workflow = workflow_utils.create_workflow(
        workflow_name=get_random_name(),
        workflow_type=WorkflowMode.SEQUENTIAL,
        shared=True,
        workflow_yaml=yaml_content,
    )

    for _ in range(12):
        workflow_utils.execute_workflow(
            workflow=created_workflow.id,
            execution_name=assistant_and_state_name,
            user_input="Hello, please provide a greeting",
        )
    yield created_workflow
    workflow_utils.delete_workflow(created_workflow)


@pytest.mark.ui
def test_workflow_details_page_elements_visibility(page, test_workflow):
    """Test that all main elements are visible on Workflow Details page."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify we are on the correct page
    workflow_details_page.should_be_on_workflow_details_page()

    # Verify header elements
    workflow_details_page.should_have_header_elements_visible()

    # Verify workflow information
    workflow_details_page.should_have_workflow_info_visible()
    workflow_details_page.should_have_workflow_name(test_workflow.name)

    # Verify action buttons
    workflow_details_page.should_have_action_buttons_visible()
    workflow_details_page.should_have_edit_button_enabled()
    workflow_details_page.should_have_run_workflow_button_enabled()

    # Verify tabs
    workflow_details_page.should_have_tabs_visible()
    workflow_details_page.should_have_executions_tab_active()

    # Verify common components
    workflow_details_page.should_have_header_visible()
    workflow_details_page.sidebar.should_be_visible()


@pytest.mark.ui
def test_workflow_details_executions_table(page, test_workflow):
    """Test executions table functionality and content."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify executions table is visible
    workflow_details_page.should_have_executions_table_visible()
    workflow_details_page.should_have_table_headers_visible()

    # Verify execution rows are present
    workflow_details_page.should_have_execution_rows()

    # Verify first execution has expected data
    workflow_details_page.should_have_succeeded_execution()
    workflow_details_page.should_have_execution_with_prompt("Hello, please p...")
    workflow_details_page.should_have_execution_triggered_by(
        os.getenv("TEST_USER_FULL_NAME")
    )

    # Verify execution actions are working
    workflow_details_page.should_have_execution_actions_working()


@pytest.mark.ui
def test_workflow_details_execution_row_interactions(page, test_workflow):
    """Test individual execution row interactions."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Get the first execution row
    first_row = workflow_details_page.get_first_execution_row()

    # Verify row is visible and has all components
    first_row.should_be_visible()
    first_row.should_have_all_cells_visible()
    first_row.should_have_proper_status_styling()
    first_row.should_have_action_buttons_with_icons()

    # Test row interactions
    first_row.hover_row()
    first_row.should_have_actions_visible()

    # Test action button states
    first_row.should_have_download_button_enabled()
    first_row.should_have_view_button_enabled()


@pytest.mark.ui
def test_workflow_details_tab_switching(page, test_workflow):
    """Test tab switching functionality."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify initial state - Executions tab is active
    workflow_details_page.should_have_executions_tab_active()
    workflow_details_page.should_have_configuration_tab_content_hidden()

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()
    workflow_details_page.should_have_configuration_tab_active()

    # Switch back to Executions tab
    workflow_details_page.click_executions_tab()
    workflow_details_page.should_have_executions_tab_active()

    # Verify tab state preservation
    workflow_details_page.should_preserve_tab_state_after_navigation()


@pytest.mark.ui
@pytest.mark.TODO
def test_workflow_details_pagination_functionality(page, test_workflow):
    """Test pagination controls functionality."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify pagination elements are visible
    workflow_details_page.should_have_pagination_visible()
    workflow_details_page.should_have_per_page_dropdown_with_value("10 items")

    # Test pagination dropdown interaction
    workflow_details_page.click_per_page_dropdown()
    # The dropdown should open, but we'll just verify it's clickable
    # In a real scenario, you might select different page sizes


@pytest.mark.ui
def test_workflow_details_action_buttons(page, test_workflow):
    """Test workflow action buttons functionality."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify action buttons are present and enabled
    workflow_details_page.should_have_action_buttons_visible()
    workflow_details_page.should_have_edit_button_enabled()
    workflow_details_page.should_have_run_workflow_button_enabled()

    # Test edit button navigation
    workflow_details_page.click_edit()
    # Should navigate to edit page
    workflow_details_page.should_have_url_containing(
        f"#/workflows/{test_workflow.id}/edit"
    )

    # Navigate back to details page
    workflow_details_page.navigate_to(test_workflow.id)

    # Test run workflow button
    workflow_details_page.click_run_workflow()
    # Should open workflow execution dialog or navigate to execution page
    # This would depend on the actual implementation


@pytest.mark.ui
def test_workflow_details_navigation_buttons(page, test_workflow):
    """Test navigation button interactions."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Test back button navigation
    workflow_details_page.click_back()
    # Should navigate back to workflows list
    workflow_details_page.should_have_url_containing("#/assistants")


@pytest.mark.ui
def test_workflow_details_sidebar_functionality(page, test_workflow):
    """Test sidebar functionality from Workflow Details page."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Test sidebar visibility and structure
    workflow_details_page.should_have_sidebar_visible()

    # Test category navigation from sidebar
    workflow_details_page.sidebar.navigate_to_my_workflows()
    workflow_details_page.should_have_url_containing("#/workflows/my")

    # Navigate back to workflow details
    workflow_details_page.navigate_to(test_workflow.id)
    workflow_details_page.sidebar.navigate_to_all_workflows()
    workflow_details_page.should_have_url_containing("#/workflows/all")


@pytest.mark.ui
def test_workflow_details_header_navigation(page, test_workflow):
    """Test header navigation from Workflow Details page."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Test header component visibility
    workflow_details_page.should_have_header_visible()
    workflow_details_page.header.should_be_visible()
    workflow_details_page.header.should_have_complete_navigation_structure()

    # Test navigation to other sections
    workflow_details_page.header.navigate_to_assistants()
    workflow_details_page.should_have_url_containing("#/assistants")

    # Navigate back to workflow details
    workflow_details_page.navigate_to(test_workflow.id)
    workflow_details_page.header.navigate_to_workflows()
    workflow_details_page.should_have_url_containing("#/workflows")


@pytest.mark.ui
def test_workflow_details_execution_status_verification(page, test_workflow):
    """Test execution status display and verification."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Get first execution row
    first_row = workflow_details_page.get_first_execution_row()

    # Verify execution status is properly displayed
    first_row.should_have_succeeded_status()

    # Verify status styling
    first_row.should_have_proper_status_styling()

    # Verify complete row data
    first_row.should_have_triggered_by(TEST_USER)
    first_row.should_have_updated_time_pattern(r"\d{2}/\d{2}/\d{4}, \d{2}:\d{2}")


@pytest.mark.ui
@pytest.mark.TODO
def test_workflow_details_execution_actions(page, test_workflow):
    """Test execution row action buttons."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Get first execution row
    first_row = workflow_details_page.get_first_execution_row()

    # Test download action
    first_row.click_download()
    workflow_details_page.should_see_export_popup()
    workflow_details_page.pop_up.close_popup()
    # In a real test, you might verify file download

    # Test view action
    first_row.click_view()
    # Should navigate to execution details or open execution viewer
    # This would depend on the actual implementation


@pytest.mark.ui
def test_workflow_details_multiple_executions(page, test_workflow):
    """Test handling of multiple executions in the table."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Verify multiple executions are shown
    workflow_details_page.should_have_execution_rows(10)

    # Get all execution rows
    all_rows = workflow_details_page.get_all_execution_rows()

    # Verify each row has proper structure
    for row in all_rows:
        row.should_be_visible()
        row.should_have_all_cells_visible()
        row.should_have_actions_visible()


# ==================== CONFIGURATION TAB TESTS ====================


@pytest.mark.ui
def test_configuration_tab_visibility(page, test_workflow):
    """Test that all configuration tab elements are visible and properly structured."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()
    workflow_details_page.should_have_configuration_tab_active()

    # Verify all configuration elements are visible
    workflow_details_page.should_have_configuration_tab_content_complete(
        test_workflow.yaml_config
    )


@pytest.mark.ui
def test_configuration_tab_content(page, test_workflow):
    """Test configuration tab content and values."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()

    # Verify About workflow section
    workflow_details_page.should_have_workflow_description(test_workflow.description)

    # Verify Overview sidebar content
    workflow_details_page.should_have_mode_value("Sequential")
    workflow_details_page.should_have_project_value(PROJECT)

    # Verify Workflow ID
    workflow_details_page.should_have_workflow_id_value(test_workflow.id)

    # Verify workflow details link contains the workflow ID
    workflow_details_page.should_have_workflow_details_link_value(test_workflow.id)


@pytest.mark.ui
def test_configuration_yaml_display(page, test_workflow):
    """Test YAML configuration display and content."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()

    # Verify YAML configuration is displayed
    workflow_details_page.should_have_yaml_configuration(test_workflow.yaml_config)


@pytest.mark.ui
def test_configuration_code_block_features(page, test_workflow):
    """Test code block features like copy and download buttons."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()

    # Verify code block elements
    workflow_details_page.should_have_code_block_elements_visible()
    workflow_details_page.should_have_copy_buttons_enabled()

    # Test copy code button (this would typically trigger clipboard copy)
    workflow_details_page.click_copy_code()
    # Note: Actual clipboard verification would require browser permissions

    # Test download button (this would typically trigger file download)
    workflow_details_page.click_download_code()
    # Note: Actual download verification would require checking downloads


@pytest.mark.ui
def test_configuration_copy_buttons(page, test_workflow):
    """Test copy functionality for workflow ID and details link."""
    workflow_details_page = WorkflowDetailsPage(page)
    workflow_details_page.navigate_to(test_workflow.id)

    # Switch to Configuration tab
    workflow_details_page.click_configuration_tab()

    # Test workflow ID copy button
    workflow_details_page.click_copy_workflow_id()
    # Note: Actual clipboard verification would require browser permissions

    # Test workflow details link copy button
    workflow_details_page.click_copy_workflow_details_link()
    # Note: Actual clipboard verification would require browser permissions

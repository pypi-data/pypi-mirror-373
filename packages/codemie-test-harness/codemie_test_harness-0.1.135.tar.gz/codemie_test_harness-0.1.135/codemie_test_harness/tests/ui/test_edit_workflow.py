import os

import pytest

from codemie_sdk.models.workflow import WorkflowMode
from codemie_test_harness.tests.ui.pageobject.workflows.workflows_page import (
    WorkflowsPage,
)
from codemie_test_harness.tests.ui.pageobject.workflows.edit_workflow_page import (
    EditWorkflowPage,
)
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
    yield created_workflow
    workflow_utils.delete_workflow(created_workflow)


@pytest.mark.ui
def test_edit_workflow_page_elements_visibility(page, test_workflow):
    """Test that all main elements are visible on Edit Workflow page."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Verify we are on the correct page
    edit_page.should_be_on_edit_workflow_page()

    # Verify header elements
    edit_page.should_have_header_elements_visible()

    # Verify all form sections are visible
    edit_page.should_have_all_form_sections_visible()

    # Verify common components
    edit_page.header.should_have_complete_navigation_structure()
    edit_page.sidebar.should_be_visible()
    edit_page.sidebar.should_have_workflows_title()


@pytest.mark.ui
def test_edit_workflow_form_pre_populated_data(page, test_workflow):
    """Test that form fields are pre-populated with existing workflow data."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Verify pre-populated data
    edit_page.should_have_project_selected(test_workflow.project)
    edit_page.should_have_name_field_value(test_workflow.name)
    edit_page.should_have_description_field_value(test_workflow.description)
    edit_page.should_have_workflow_mode_selected("Sequential")
    edit_page.should_have_shared_switch_checked()

    # Verify YAML editor has content
    edit_page.should_have_yaml_editor_visible()
    edit_page.should_have_yaml_editor_with_content(test_workflow.yaml_config)


@pytest.mark.ui
def test_edit_workflow_form_interactions(page, test_workflow):
    """Test form field interactions and input validation."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test name field interaction
    new_name = "Updated Test Workflow"
    edit_page.fill_name(new_name)
    edit_page.should_have_name_field_value(new_name)

    # Test description field interaction
    new_description = "This is an updated test workflow description"
    edit_page.fill_description(new_description)
    edit_page.should_have_description_field_value(new_description)

    # Test icon URL field interaction
    test_icon_url = "https://example.com/updated-icon.png"
    edit_page.fill_icon_url(test_icon_url)
    edit_page.should_have_icon_url_field_value(test_icon_url)

    # Test shared switch interaction
    edit_page.toggle_shared_switch()
    edit_page.should_have_shared_switch_unchecked()

    # Toggle back to checked
    edit_page.toggle_shared_switch()
    edit_page.should_have_shared_switch_checked()


@pytest.mark.ui
def test_edit_workflow_dropdowns_interaction(page, test_workflow):
    """Test dropdown interactions for project and workflow mode."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test project dropdown interaction
    edit_page.should_have_project_dropdown_visible()

    # Test project search functionality
    edit_page.search_and_select_project(os.getenv("PROJECT_NAME"))
    edit_page.should_see_project_selected(os.getenv("PROJECT_NAME"))

    # Test workflow mode dropdown interaction
    edit_page.select_workflow_mode()  # Just opens dropdown
    # Close dropdown by clicking elsewhere
    edit_page.page_title.click()

    # Verify the default selection is maintained
    edit_page.should_have_workflow_mode_selected("Sequential")


@pytest.mark.ui
def test_edit_workflow_yaml_tabs_functionality(page, test_workflow):
    """Test YAML configuration tabs functionality."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Verify YAML tabs are visible
    edit_page.should_have_yaml_tabs_visible()

    # Verify Edit Current Version tab is active by default
    edit_page.should_have_current_version_tab_active()

    # Test switching to History tab
    edit_page.click_history_tab()
    edit_page.should_have_history_tab_active()

    # Test switching back to Edit Current Version tab
    edit_page.click_edit_current_version_tab()
    edit_page.should_have_current_version_tab_active()


@pytest.mark.ui
def test_edit_workflow_yaml_editor_functionality(page, test_workflow):
    """Test YAML editor functionality."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Verify YAML editor section
    edit_page.should_have_yaml_editor_visible()

    new_yaml_config = test_workflow.yaml_config.replace(
        "You are helpful assistant", "New system prompt"
    )

    edit_page.fill_yaml_config(new_yaml_config)

    edit_page.should_have_yaml_editor_with_content(new_yaml_config)


@pytest.mark.ui
def test_edit_workflow_visualization_section(page, test_workflow):
    """Test workflow visualization section functionality."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Verify visualization section elements
    edit_page.should_have_visualization_section_visible()

    # Test visualize button interaction
    edit_page.click_visualize()

    # Verify visualization section is still visible after click
    edit_page.should_have_workflow_diagram_visible()


@pytest.mark.ui
def test_edit_workflow_navigation_buttons(page, test_workflow):
    """Test navigation button interactions."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    edit_page.should_have_update_button_enabled()

    edit_page.click_back()
    edit_page.should_have_url_containing("#/assistants")

    edit_page.navigate_to(test_workflow.id)
    edit_page.click_cancel()

    edit_page.should_have_url_containing("#/workflows/my")


@pytest.mark.ui
def test_edit_workflow_sidebar_functionality(page, test_workflow):
    """Test sidebar functionality from Edit Workflow page."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test sidebar visibility and structure
    edit_page.sidebar.should_be_visible()
    edit_page.sidebar.should_have_workflows_title()
    edit_page.sidebar.should_have_categories_section()

    # Test category navigation from sidebar
    edit_page.sidebar.navigate_to_my_workflows()
    edit_page.should_have_url_containing("#/workflows/my")

    # Navigate back to edit workflow
    edit_page.navigate_to(test_workflow.id)
    edit_page.sidebar.navigate_to_all_workflows()
    edit_page.should_have_url_containing("#/workflows/all")


@pytest.mark.ui
def test_edit_workflow_header_navigation(page, test_workflow):
    """Test header navigation from Edit Workflow page."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test header component visibility
    edit_page.should_have_header_visible()
    edit_page.header.should_be_visible()
    edit_page.header.should_have_complete_navigation_structure()

    # Test navigation to other sections
    edit_page.header.navigate_to_assistants()
    edit_page.should_have_url_containing("#/assistants")

    # Navigate back to edit workflow
    edit_page.navigate_to(test_workflow.id)
    edit_page.header.navigate_to_workflows()
    edit_page.should_have_url_containing("#/workflows/my")


@pytest.mark.ui
def test_edit_workflow_workflow_mode_information(page, test_workflow):
    """Test workflow mode information display."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test workflow mode information display
    edit_page.should_show_workflow_mode_info()


@pytest.mark.ui
def test_edit_workflow_data_persistence_across_tabs(page, test_workflow):
    """Test that form data persists when switching between tabs."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Fill some form data
    test_name = "Modified Workflow Name"
    test_description = "Modified workflow description"

    edit_page.fill_name(test_name)
    edit_page.fill_description(test_description)

    # Switch tabs and verify data persistence
    edit_page.should_preserve_form_data_after_tab_switch(test_name, test_description)


@pytest.mark.ui
def test_edit_workflow_button_states(page, test_workflow):
    """Test update button enabled/disabled states."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test update button initial state (should be enabled with existing data)
    edit_page.should_have_update_button_enabled()

    # Test update button after clearing required fields
    edit_page.clear_name()
    edit_page.should_have_update_button_disabled()

    # Test update button after filling required fields again
    edit_page.fill_name("Test Workflow")
    edit_page.should_have_update_button_enabled()


@pytest.mark.ui
def test_edit_workflow_form_validation(page, test_workflow):
    """Test form validation scenarios."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    edit_page.clear_name()
    edit_page.should_show_validation_error_for_name("Name is required")

    edit_page.fill_icon_url("Test")
    edit_page.should_show_validation_error_for_icon_url("Icon URL must be a valid URL")


@pytest.mark.ui
def test_edit_workflow_complete_update(page, test_workflow):
    """Test complete workflow update using the update_workflow method."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    # Test complete workflow update
    test_workflow.name = f"{test_workflow.name}_updated"
    test_workflow.description = "This is an updated test workflow"
    test_workflow.icon_url = "https://example.com/updated-icon.png"
    test_workflow.yaml_config = test_workflow.yaml_config.replace(
        "You are helpful assistant", "Updated system prompt"
    )
    test_workflow.shared = False

    edit_page.update_workflow(
        project_name=os.getenv("PROJECT_NAME"),
        name=test_workflow.name,
        description=test_workflow.description,
        icon_url=test_workflow.icon_url,
        yaml_config=test_workflow.yaml_config,
        shared=test_workflow.shared,
    )

    workflows_page = WorkflowsPage(page)
    workflows_page.should_be_on_workflows_page()
    workflows_page.should_see_workflow_card(test_workflow.name)

    edit_page.navigate_to(test_workflow.id)
    edit_page.should_have_name_field_value(test_workflow.name)
    edit_page.should_have_description_field_value(test_workflow.description)
    edit_page.should_have_workflow_mode_selected("Sequential")
    edit_page.should_have_shared_switch_unchecked()
    edit_page.should_have_yaml_editor_with_content(test_workflow.yaml_config)


@pytest.mark.ui
def test_edit_workflow_history_tab_functionality(page, test_workflow):
    """Test the complete history tab functionality: edit YAML, save, return to edit, click history, restore from history, check restoration."""
    edit_page = EditWorkflowPage(page)
    edit_page.navigate_to(test_workflow.id)

    modified_yaml = test_workflow.yaml_config.replace(
        "You are helpful assistant", "You are a modified helpful assistant"
    )
    edit_page.fill_yaml_config(modified_yaml)
    edit_page.should_have_yaml_editor_with_content(modified_yaml)

    edit_page.click_update()

    workflows_page = WorkflowsPage(page)
    workflows_page.should_be_on_workflows_page()

    edit_page.navigate_to(test_workflow.id)
    edit_page.should_be_on_edit_workflow_page()

    edit_page.click_history_tab()
    edit_page.should_have_history_tab_active()
    edit_page.should_have_history_tab_content_visible()

    edit_page.select_first_history_item()

    edit_page.should_have_history_yaml_content(test_workflow.yaml_config)

    edit_page.should_have_restore_button_enabled()
    edit_page.click_restore()

    workflows_page.should_be_on_workflows_page()
    edit_page.navigate_to(test_workflow.id)
    edit_page.should_be_on_edit_workflow_page()

    edit_page.should_have_current_version_tab_active()
    edit_page.should_have_yaml_editor_with_content(test_workflow.yaml_config)

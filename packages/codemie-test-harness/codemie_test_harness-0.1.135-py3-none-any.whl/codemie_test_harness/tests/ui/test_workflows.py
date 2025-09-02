import pytest
from codemie_test_harness.tests.ui.pageobject.workflows.workflows_page import (
    WorkflowsPage,
)


@pytest.mark.ui
def test_workflows_page_basic_functionality(page):
    """Test basic workflows page functionality."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.should_be_on_workflows_page()
    workflow_page.should_see_workflow_cards()


@pytest.mark.ui
def test_workflow_card_interactions(page):
    """Test individual workflow card interactions."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_card = workflow_page.get_workflow_card_by_index(0)

    workflow_card.should_be_visible()
    workflow_card.should_have_avatar()
    workflow_card.should_have_run_button()
    workflow_card.should_have_menu_button()


@pytest.mark.ui
def test_workflow_search_functionality(page):
    """Test workflow search functionality."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.search_workflows("basic")
    workflow_page.should_see_workflow_cards()
    workflow_page.should_not_see_new_release_popup()


@pytest.mark.ui
def test_workflow_card_by_name(page):
    """Test getting and interacting with a specific workflow card."""
    workflow_name = "basicWfcx9"

    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.should_see_workflow_card(workflow_name)
    workflow_page.should_see_workflow_author(workflow_name, "Dmytro Adamtsev")
    workflow_page.should_see_shared_workflow(workflow_name)


@pytest.mark.ui
def test_workflow_pagination(page):
    """Test workflow pagination functionality."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.should_see_pagination()
    workflow_page.should_be_on_page(1)
    workflow_page.change_items_per_page(24)
    workflow_page.should_see_workflow_cards(minimum_count=12)


@pytest.mark.ui
def test_workflow_filtering(page):
    """Test workflow filtering functionality."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.sidebar.select_with_project_filter()
    workflow_page.should_see_workflow_cards()
    workflow_page.clear_all_filters()


@pytest.mark.ui
def test_workflow_navigation(page):
    """Test navigation between different workflow sections."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_my_workflows()
    workflow_page.sidebar.navigate_to_all_workflows()
    workflow_page.sidebar.navigate_to_templates()


@pytest.mark.ui
def test_workflow_card_fluent_interface(page):
    """Test the fluent interface of WorkflowCard component."""
    workflow_page = WorkflowsPage(page)
    workflow_page.navigate_to()
    workflow_page.sidebar.navigate_to_all_workflows()

    workflow_card = workflow_page.get_workflow_card_by_index(0)
    workflow_card.should_be_visible()
    workflow_card.should_have_avatar()
    workflow_card.should_have_run_button()
    workflow_card.should_have_menu_button()
    workflow_card.hover()
    workflow_card.should_be_visible()

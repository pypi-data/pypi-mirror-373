import pytest

from codemie_test_harness.tests import TEST_USER
from codemie_test_harness.tests.ui.pageobject.workflows.create_workflow_page import (
    CreateWorkflowPage,
)
from codemie_test_harness.tests.ui.pageobject.workflows.workflow_template_details import (
    WorkflowTemplateDetailsPage,
)
from codemie_test_harness.tests.ui.pageobject.workflows.workflow_templates_page import (
    WorkflowTemplatesPage,
)
from codemie_test_harness.tests.ui.pageobject.workflows.workflows_page import (
    WorkflowsPage,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.fixture(scope="function")
def predefined_templates(workflow_utils):
    """Fixture returns predefined templates data."""
    return workflow_utils.get_prebuilt_workflows()


@pytest.mark.ui
def test_templates_visible(page, predefined_templates):
    """Verify that workflow templates are presented and tooltips visible for the user."""
    templates = predefined_templates

    workflow_templates_page = WorkflowTemplatesPage(page)
    workflow_templates_page.navigate_to()
    workflow_templates_page.should_have_templates(len(templates))

    for i in range(len(templates)):
        expected_name = templates[i]["name"]
        expected_description = templates[i]["description"]
        if len(expected_description) > 1500:
            expected_description = f"{expected_description[:1500]}\n..."
        trimmed_description = templates[i]["description"][:70]

        workflow_templates_page.should_have_title_description(
            i, expected_name, trimmed_description, expected_description
        )


@pytest.mark.ui
def test_templates_details(page, predefined_templates):
    """Verify that workflow template leads to specific template page."""
    templates = predefined_templates

    workflow_templates_page = WorkflowTemplatesPage(page)
    workflow_templates_details_page = WorkflowTemplateDetailsPage(page)
    workflow_templates_page.navigate_to()

    for i in range(len(templates)):
        template_title = templates[i]["name"]
        description = templates[i]["description"]
        yaml_config = templates[i]["yaml_config"]

        workflow_templates_page.template_details_click(i)
        workflow_templates_details_page.should_have_template_header()
        workflow_templates_details_page.should_have_template_sidebar()
        workflow_templates_details_page.should_have_template_details(
            template_title, description, yaml_config
        )
        page.go_back()


@pytest.mark.ui
def test_templates_creation(page, predefined_templates):
    """Verify that workflow template create button leads to Create Workflow Page."""
    expected_create_workflow_from_template_title = "Create Workflow from Template"
    templates = predefined_templates

    workflow_templates_page = WorkflowTemplatesPage(page)
    create_workflow_page = CreateWorkflowPage(page)

    workflow_templates_page.navigate_to()
    for i in range(len(templates)):
        description = templates[i]["description"]
        # yaml_config = templates[i]["yaml_config"] add yaml_config after formatting fix

        workflow_templates_page.click_create_workflow_from_template(i)
        create_workflow_page.should_have_all_form_sections_visible()
        create_workflow_page.should_be_on_create_workflow_page(
            expected_create_workflow_from_template_title
        )
        create_workflow_page.should_have_description_field_value(description)
        # add step for assertion yaml_config, after formatting fix
        page.go_back()


@pytest.mark.ui
def test_template_create(page, predefined_templates):
    """Verify that workflow template can be created."""
    templates = predefined_templates
    workflow_name = get_random_name()
    template_name = "Iteration Workflow Example"
    template_description = next(
        (
            template["description"][:88] + "..."
            for template in templates
            if template["name"] == template_name
        )
    )

    workflow_template_page = WorkflowTemplatesPage(page)
    create_workflow_page = CreateWorkflowPage(page)
    workflows_page = WorkflowsPage(page)

    workflow_template_page.navigate_to()
    workflow_template_page.click_create_workflow_from_specific_template(template_name)
    create_workflow_page.create_workflow(workflow_name)
    workflows_page.should_see_workflow_card(workflow_name)
    workflows_page.should_see_workflow_author(workflow_name, TEST_USER)
    workflows_page.should_see_workflow_description(workflow_name, template_description)

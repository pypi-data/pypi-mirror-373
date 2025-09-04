from pathlib import Path

from codemie_sdk.models.assistant import (
    AssistantChatRequest,
    AssistantCreateRequest,
    AssistantUpdateRequest,
    EnvVars,
    ExportAssistantPayload,
)
from codemie_test_harness.tests import PROJECT, LANGFUSE_TRACES_ENABLED
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    get_random_name,
    wait_for_entity,
)


class AssistantUtils(BaseUtils):
    def send_create_assistant_request(
        self,
        llm_model_type=None,
        toolkits=(),
        context=(),
        mcp_servers=(),
        slug=None,
        description=None,
        system_prompt="",
        assistant_name=None,
        shared=False,
        project_name=None,
        top_p=None,
        temperature=None,
    ):
        # Generate a random name if assistant_name is not provided
        assistant_name = assistant_name if assistant_name else get_random_name()
        # Use the first available LLM model if llm_model_type is not provided
        llm_model_type = (
            llm_model_type if llm_model_type else self.client.llms.list()[0].base_name
        )
        request = AssistantCreateRequest(
            name=assistant_name,
            slug=slug if slug else assistant_name,
            description=description if description else "Integration test assistant",
            shared=shared,
            system_prompt=system_prompt,
            project=project_name if project_name else PROJECT,
            llm_model_type=llm_model_type,
            toolkits=toolkits,
            context=context,
            mcp_servers=mcp_servers,
            top_p=top_p,
            temperature=temperature,
        )

        response = self.client.assistants.create(request)

        return response, assistant_name

    def create_assistant(
        self,
        llm_model_type=None,
        toolkits=(),
        context=(),
        mcp_servers=(),
        system_prompt="",
        assistant_name=None,
        slug=None,
        shared=False,
        project_name=None,
        top_p=None,
        temperature=None,
        description=None,
    ):
        # Generate a random name if assistant_name is not provided
        assistant_name = assistant_name if assistant_name else get_random_name()
        # Use the first available LLM model if llm_model_type is not provided
        llm_model_type = (
            llm_model_type if llm_model_type else self.client.llms.list()[0].base_name
        )
        slug = slug if slug else assistant_name
        response = self.send_create_assistant_request(
            llm_model_type=llm_model_type,
            toolkits=toolkits,
            context=context,
            mcp_servers=mcp_servers,
            system_prompt=system_prompt,
            assistant_name=assistant_name,
            slug=slug,
            shared=shared,
            project_name=project_name,
            top_p=top_p,
            temperature=temperature,
            description=description,
        )

        return wait_for_entity(
            lambda: self.client.assistants.list(per_page=200),
            entity_name=response[1],
        )

    def ask_assistant(
        self,
        assistant,
        user_prompt,
        minimal_response=True,
        stream=False,
        tools_config=None,
        file_urls=(),
        conversation_id=None,
        history=(),
        output_schema=None,
    ):
        chat_request = AssistantChatRequest(
            text=user_prompt,
            conversation_id=conversation_id,
            stream=stream,
            tools_config=tools_config,
            file_names=file_urls,
            history=history,
            output_schema=output_schema,
            metadata={"langfuse_traces_enabled": LANGFUSE_TRACES_ENABLED},
        )

        response = self.client.assistants.chat(
            assistant_id=assistant.id, request=chat_request
        )

        return response.generated if minimal_response else response

    def send_chat_request(
        self,
        assistant,
        request: AssistantChatRequest,
    ):
        return self.client.assistants.chat(assistant_id=assistant.id, request=request)

    def upload_file_to_chat(self, file_path: Path):
        return self.client.assistants.upload_file_to_chat(file_path)

    def get_prebuilt_assistant(self):
        return self.client.assistants.get_prebuilt()

    def get_assistant_context(self, project_name: str):
        return self.client.assistants.get_context(project_name)

    def get_assistant_tools(self):
        return self.client.assistants.get_tools()

    def get_assistants(
        self,
        minimal_response=True,
        filters=None,
        scope="visible_to_user",
        page=0,
        per_page=12,
    ):
        return self.client.assistants.list(
            minimal_response=minimal_response,
            filters=filters,
            scope=scope,
            page=page,
            per_page=per_page,
        )

    def get_tasks(self, task_id):
        return self.client.tasks.get(task_id)

    def get_assistant_by_id(self, assistant_id: str):
        return self.client.assistants.get(assistant_id)

    def get_assistant_by_name(self, assistant_name: str):
        return self.client.assistants.list(
            per_page=10, minimal_response=False, filters={"search": assistant_name}
        )[0]

    def get_assistant_by_slug(self, slug: str):
        return self.client.assistants.get_by_slug(slug)

    def get_prebuilt_assistant_by_slug(self, slug: str):
        return self.client.assistants.get_prebuilt_by_slug(slug)

    def update_assistant(
        self, assistant_id: str, update_request: AssistantUpdateRequest
    ):
        return self.client.assistants.update(
            assistant_id=assistant_id, request=update_request
        )

    def delete_assistant(self, assistant):
        return self.client.assistants.delete(assistant.id)

    def export_assistant(self, assistant_id: str):
        env_vars = EnvVars(
            azure_openai_url="https://ai-proxy.lab.epam.com",
            azure_openai_api_key="RANDOM_KEY",
            openai_api_type="azure",
            openai_api_version="2024-02-15-preview",
            models_env="dial",
        )
        payload = ExportAssistantPayload(env_vars=env_vars)
        return self.client.assistants.export(assistant_id, payload)

    def send_evaluate_assistant_request(self, assistant_id: str, evaluation_request):
        return self.client.assistants.evaluate(assistant_id, evaluation_request)

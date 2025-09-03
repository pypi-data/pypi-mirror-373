from codemie_test_harness.tests.utils.base_utils import BaseUtils


class LLMUtils(BaseUtils):
    def list_llm_models(self):
        return self.client.llms.list()

    def list_embedding_llm_models(self):
        return self.client.llms.list_embeddings()

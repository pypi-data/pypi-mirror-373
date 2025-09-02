"""Integration tests for LLMService."""

from codemie_sdk import CodeMieClient
from codemie_sdk.models.llm import LLMModel


def test_list_llm_models(client: CodeMieClient):
    """Test successful retrieval of available LLM models."""
    models = client.llms.list()
    assert isinstance(models, list)
    assert len(models) > 0
    assert all(isinstance(model, LLMModel) for model in models)


def test_list_embeddings_models(client: CodeMieClient):
    """Test successful retrieval of available embeddings models."""
    models = client.llms.list_embeddings()
    assert isinstance(models, list)
    assert len(models) > 0
    assert all(isinstance(model, LLMModel) for model in models)

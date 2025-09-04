import pytest
from codemie_sdk.models.llm import LLMModel
from hamcrest import (
    assert_that,
    instance_of,
    has_length,
    greater_than,
    all_of,
)


@pytest.mark.parametrize(
    "model_list_function", ["list_llm_models", "list_embedding_llm_models"]
)
def test_list_available_models(llm_utils, model_list_function):
    models = getattr(llm_utils, model_list_function)()
    assert_that(models, all_of(instance_of(list), has_length(greater_than(0))))
    for model in models:
        assert_that(model, instance_of(LLMModel))

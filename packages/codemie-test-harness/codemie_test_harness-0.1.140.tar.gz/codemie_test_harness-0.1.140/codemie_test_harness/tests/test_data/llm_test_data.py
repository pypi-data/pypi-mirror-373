"""Constants for LLM output responses."""

from dataclasses import dataclass
from typing import List
from codemie_test_harness.tests.enums.model_types import ModelTypes


@dataclass
class LlmResponseData:
    """Data class to store LLM model response information."""

    model_type: ModelTypes
    environments: List[str]


# Define environment sets for common groups
AZURE_ENVS = ["preview", "azure", "local"]
GCP_ENVS = ["preview", "gcp", "local"]
AWS_ENVS = ["preview", "aws", "local"]
OTHER_ENVS = ["preview", "local"]

# Define model responses with their environment restrictions
MODEL_RESPONSES = [
    # Azure LLMs test data
    LlmResponseData(ModelTypes.GPT_41, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_41_MINI, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_4o_2024_08_06, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_4o_2024_11_20, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_4o_MINI, AZURE_ENVS),
    LlmResponseData(ModelTypes.O3_MINI, AZURE_ENVS),
    LlmResponseData(ModelTypes.O3_2025_04_16, AZURE_ENVS),
    LlmResponseData(ModelTypes.O4_MINI_2025_04_16, AZURE_ENVS),
    LlmResponseData(ModelTypes.O1, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_5_2025_08_07, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_5_MINI_2025_08_07, AZURE_ENVS),
    LlmResponseData(ModelTypes.GPT_5_NANO_2025_08_07, AZURE_ENVS),
    # GCP LLMs test data
    LlmResponseData(
        ModelTypes.CLAUDE_SONNET_V2_VERTEX,
        GCP_ENVS,
    ),
    LlmResponseData(ModelTypes.GEMINI_20_FLASH, GCP_ENVS),
    LlmResponseData(ModelTypes.GEMINI_25_PRO, GCP_ENVS),
    LlmResponseData(
        ModelTypes.CLAUDE_SONNET_37_VERTEX,
        GCP_ENVS,
    ),
    # Bedrock LLMs test data
    LlmResponseData(ModelTypes.CLAUDE_35_SONNET, AWS_ENVS),
    LlmResponseData(ModelTypes.CLAUDE_35_SONNET_V2, AWS_ENVS),
    LlmResponseData(ModelTypes.CLAUDE_37_SONNET_V1, AWS_ENVS),
    LlmResponseData(ModelTypes.CLAUDE_4_SONNET, AWS_ENVS),
    LlmResponseData(ModelTypes.CLAUDE_4_OPUS, AWS_ENVS),
    LlmResponseData(ModelTypes.CLAUDE_4_1_OPUS, AWS_ENVS),
    # Other LLMs test data
    LlmResponseData(ModelTypes.RLAB_QWQ_32B, OTHER_ENVS),
    LlmResponseData(ModelTypes.DEEPSEEK_R1, OTHER_ENVS),
]

import os
from dataclasses import dataclass
from typing import List

import pytest


@dataclass
class EmbeddingData:
    """Data class to store Embedding models."""

    model_type: str
    environments: List[str]


AZURE_ENVS = ["preview", "azure", "local"]
GCP_ENVS = ["preview", "gcp", "local"]
AWS_ENVS = ["preview", "aws", "local"]

MODELS = [
    EmbeddingData("titan", AWS_ENVS),
    EmbeddingData("gecko", GCP_ENVS),
    EmbeddingData("ada-002", AZURE_ENVS),
]


def generate_test_data():
    """Generate pytest parameters for Embedding models"""
    env = os.getenv("ENV")
    test_data = []

    for model in MODELS:
        test_data.append(
            pytest.param(
                model.model_type,
                marks=pytest.mark.skipif(
                    env not in model.environments,
                    reason=f"Skip on non {'/'.join(model.environments[:-1])} envs",
                ),
            )
        )

    return test_data


index_test_data = generate_test_data()

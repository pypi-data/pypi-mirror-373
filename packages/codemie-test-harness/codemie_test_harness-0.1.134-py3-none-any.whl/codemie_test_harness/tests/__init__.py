import os
import random
import string
from pathlib import Path

from dotenv import load_dotenv

from codemie_test_harness.tests.utils.aws_parameters_store import AwsParameterStore
from codemie_test_harness.cli.runner import resolve_tests_path_and_root

_, root_dir = resolve_tests_path_and_root()
env_file_path = Path(root_dir) / ".env"
load_dotenv(env_file_path)

if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_KEY"):
    aws_parameters_store = AwsParameterStore.get_instance(
        access_key=os.getenv("AWS_ACCESS_KEY"),
        secret_key=os.getenv("AWS_SECRET_KEY"),
        session_token=os.getenv("AWS_SESSION_TOKEN", ""),
    )

    dotenv = aws_parameters_store.get_parameter(
        f"/codemie/autotests/dotenv/{os.getenv('ENV')}"
    )

    # Use the .env path that was loaded

    with open(env_file_path, "w") as file:
        file.write(dotenv)

    # Reload .env file with AWS parameters
    load_dotenv(env_file_path)

LANGFUSE_TRACES_ENABLED = (
    os.getenv("LANGFUSE_TRACES_ENABLED", "false").lower() == "true"
)

PROJECT = os.getenv("PROJECT_NAME", "codemie")
TEST_USER = os.getenv("TEST_USER_FULL_NAME", "Test User")

autotest_entity_prefix = (
    f"{''.join(random.choice(string.ascii_lowercase) for _ in range(3))}_"
)

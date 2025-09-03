import os
from pathlib import Path

from dotenv import load_dotenv
from codemie_test_harness.cli.runner import resolve_tests_path_and_root

_, root_dir = resolve_tests_path_and_root()
env_path = Path(root_dir) / ".env"
load_dotenv(env_path)

api_domain = os.getenv("CODEMIE_API_DOMAIN")
verify_ssl = os.getenv("VERIFY_SSL", "").lower() == "true"

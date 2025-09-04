"""Client factory utilities for tests."""

import os
from codemie_sdk import CodeMieClient


def get_client():
    """Create a test client instance."""
    return CodeMieClient(
        auth_server_url=os.getenv("AUTH_SERVER_URL", ""),
        auth_client_id=os.getenv("AUTH_CLIENT_ID", ""),
        auth_client_secret=os.getenv("AUTH_CLIENT_SECRET", ""),
        auth_realm_name=os.getenv("AUTH_REALM_NAME", ""),
        codemie_api_domain=os.getenv("CODEMIE_API_DOMAIN"),
        verify_ssl=os.getenv("VERIFY_SSL", "false").lower() == "true",
        username=os.getenv("AUTH_USERNAME"),
        password=os.getenv("AUTH_PASSWORD"),
    )

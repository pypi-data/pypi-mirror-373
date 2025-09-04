import json
import logging
import os
from typing import Optional, Dict, Any

import requests
from codemie_sdk import CodeMieClient

from codemie_test_harness.tests import autotest_entity_prefix, API_DOMAIN, VERIFY_SSL
from codemie_test_harness.tests.utils.base_utils import (
    BaseUtils,
    get_random_name,
)
from codemie_test_harness.tests.utils.http_utils import RequestHandler

logger = logging.getLogger(__name__)

providers_endpoint = "/v1/providers"


class ProviderUtils(BaseUtils):
    def __init__(self, client: CodeMieClient):
        """Initialize the provides service."""

        super().__init__(client)
        self._api = RequestHandler(API_DOMAIN, self.client.token, VERIFY_SSL)

    @staticmethod
    def provider_request_json():
        """Load provider request JSON from file."""
        payload_path = os.path.join(
            os.path.dirname(__file__), "../test_data/files/provider_payload.json"
        )
        with open(payload_path, "r") as pyload_file:
            request_json = json.load(pyload_file)

        return request_json

    def send_post_request_to_providers_endpoint(
        self, request: Dict[str, Any]
    ) -> requests.Response:
        """
        Send request to provider creation endpoint without raising error for response status codes.

        Args:
            request: The provider creation request

        Returns:
            Raw response from '/v1/providers' endpoint
        """
        return self._api.post(providers_endpoint, json_data=request, stream=True)

    def send_get_request_to_providers_endpoint(
        self,
    ) -> requests.Response:
        """
        Send request to get providers endpoint.

        Returns:
            Raw response from '/v1/providers' endpoint
        """
        return self._api.get(providers_endpoint)

    def send_get_request_datasource_schemas_endpoint(
        self,
    ) -> requests.Response:
        """
        Send request to get datasource_schemas endpoint.

        Returns:
            Raw response from '/v1/providers/datasource_schemas' endpoint
        """
        return self._api.get(f"{providers_endpoint}/datasource_schemas")

    def create_provider(
        self,
    ) -> str:
        """
        Creates a provider for test.

        Returns:
            Created provider id
        """
        request_json = self.provider_request_json()
        # Ensure unique provider name to avoid conflicts
        request_json["name"] = get_random_name()

        response = self.send_post_request_to_providers_endpoint(request_json)

        return response.json()["id"]

    def list_providers(
        self,
    ) -> requests.Response:
        """
        List all providers.

        Returns:
            List of provider objects
        """
        response = self.send_get_request_to_providers_endpoint()

        return response

    def get_provider_by_id(self, provider_id: str) -> requests.Response:
        """
        Get a specific provider by ID.

        Args:
            provider_id: The provider ID

        Returns:
            Provider object
        """
        response = self._api.get(f"{providers_endpoint}/{provider_id}")

        return response

    def update_provider(
        self,
        provider_id: str,
        provider_update_payload: dict,
    ) -> requests.Response:
        """
        Update an existing provider.

        Args:
            provider_id: The provider ID to update
            provider_update_payload: request body

        Returns:
            Updated provider object
        """
        endpoint = f"{providers_endpoint}/{provider_id}"

        return self._api.put(endpoint, json_data=provider_update_payload)

    def send_delete_provider_request(self, provider_id: str) -> requests.Response:
        """
        Delete a provider by ID.

        Args:
            provider_id: The provider ID to delete

        Returns:
            Response from delete operation
        """
        return self._api.delete(f"{providers_endpoint}/{provider_id}")

    def cleanup_test_providers(self, name_prefix: Optional[str] = None):
        """
        Clean up test providers (those with autotest prefix or specified prefix).

        Args:
            name_prefix: Prefix to match for cleanup (uses autotest prefix if None)
        """

        prefix = name_prefix if name_prefix else autotest_entity_prefix

        try:
            providers = self.list_providers()
            test_providers = [
                provider
                for provider in providers.json()
                if provider["name"].startswith(prefix)
            ]

            for provider in test_providers:
                try:
                    self.send_delete_provider_request(provider["id"])
                except Exception as e:
                    # Log but don't fail cleanup for individual provider
                    logger.error(f"Failed to delete provider {provider['name']}: {e}")

        except Exception as e:
            # Log but don't fail if cleanup encounters issues
            logger.error(f"Provider cleanup encountered an error: {e}")

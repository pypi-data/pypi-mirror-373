import pytest
from hamcrest import (
    assert_that,
    is_,
    equal_to,
    has_key,
    all_of,
)

from codemie_test_harness.tests.utils.base_utils import get_random_name
from codemie_test_harness.tests.utils.provider_utils import ProviderUtils


@pytest.fixture(scope="session")
def providers_utils(client):
    return ProviderUtils(client)


nonexistent_id = "nonexistent-provider-id-12345"

# =============================================================================
# GET /v1/providers - List all providers
# =============================================================================


@pytest.mark.regression
def test_get_providers_endpoint(providers_utils):
    response = providers_utils.send_get_request_to_providers_endpoint()

    assert_that(response.status_code, equal_to(200))

    response_data = response.json()

    # Validate response structure
    assert_that(isinstance(response_data, list), is_(True))
    for provider in response_data:
        assert_that(
            provider,
            all_of(has_key("provided_toolkits"), has_key("service_location_url")),
        )


# =============================================================================
# POST /v1/providers - Create new provider
# =============================================================================


@pytest.mark.regression
def test_post_providers_endpoint(providers_utils):
    request_json = providers_utils.provider_request_json()
    # Ensure unique provider name to avoid conflicts
    provider_name = get_random_name()
    request_json["name"] = provider_name

    create_response = providers_utils.send_post_request_to_providers_endpoint(
        request_json
    )

    assert_that(create_response.status_code, equal_to(200))

    # get provider to verify it was created
    get_response = providers_utils.send_get_request_to_providers_endpoint()

    providers = get_response.json()
    created_provider = next((p for p in providers if p["name"] == provider_name), None)

    assert_that(
        created_provider is not None,
        is_(True),
        "Created provider should be in the list",
    )


@pytest.mark.regression
def test_post_providers_endpoint_validation_error(providers_utils):
    """Test POST /v1/providers with invalid provided_toolkits node"""
    request_json = providers_utils.provider_request_json()
    request_json["provided_toolkits"] = "invalid_value"

    response = providers_utils.send_post_request_to_providers_endpoint(request_json)

    assert_that(response.status_code, equal_to(422))
    assert_that(
        response.json()["error"]["details"][0]["msg"],
        equal_to("Input should be a valid list"),
    )


@pytest.mark.regression
def test_post_providers_endpoint_with_existing_name(providers_utils):
    provider_id = providers_utils.create_provider()

    provider = providers_utils.get_provider_by_id(provider_id).json()

    existing_name = provider["name"]
    request_json = providers_utils.provider_request_json()
    request_json["name"] = existing_name

    create_response = providers_utils.send_post_request_to_providers_endpoint(
        request_json
    )

    assert_that(create_response.status_code, equal_to(409))
    assert_that(
        create_response.json()["error"]["details"],
        equal_to(f"A provider with the name [{existing_name}] already exists."),
    )


# =============================================================================
# GET /v1/providers/datasource_schemas - Get datasource schemas
# =============================================================================


@pytest.mark.regression
def test_get_providers_datasource_schema_endpoint(providers_utils):
    response = providers_utils.send_get_request_datasource_schemas_endpoint()

    assert_that(response.status_code, equal_to(200))

    response_data = response.json()

    # Validate response structure
    assert_that(isinstance(response_data, list), is_(True))
    for provider in response_data:
        assert_that(
            provider,
            all_of(
                has_key("id"),
                has_key("provider_name"),
                has_key("name"),
                has_key("base_schema"),
                has_key("create_schema"),
            ),
        )


# =============================================================================
# GET /v1/providers/{provider_id} - Get specific provider
# =============================================================================


@pytest.mark.regression
def test_get_provider_by_id_endpoint(providers_utils):
    provider_id = providers_utils.create_provider()

    provider_response = providers_utils.get_provider_by_id(provider_id)

    assert_that(provider_response.status_code, equal_to(200))
    assert_that(provider_response.json()["id"], equal_to(provider_id))


@pytest.mark.regression
def test_get_nonexistent_provider(providers_utils):
    """Test error handling when requesting nonexistent provider."""
    response = providers_utils.get_provider_by_id(nonexistent_id)

    assert_that(response.status_code, equal_to(404))

    assert_that(
        response.json()["error"]["details"],
        equal_to(
            f"The provider with ID [{nonexistent_id}] could not be found in the system."
        ),
    )


# =============================================================================
# PUT /v1/providers/{provider_id} - Update specific provider
# =============================================================================


@pytest.mark.regression
def test_put_provider_endpoint(providers_utils):
    provider_id = providers_utils.create_provider()
    provider = providers_utils.get_provider_by_id(provider_id).json()

    request_json = providers_utils.provider_request_json()
    toolkits = provider["provided_toolkits"]
    toolkits[0]["name"] = "Updated toolkit name"
    toolkits[0]["description"] = "Updated toolkit description"
    request_json["provided_toolkits"] = toolkits
    request_json["name"] = f"{provider['name']} - updated"
    update_response = providers_utils.update_provider(provider_id, request_json)

    assert_that(update_response.status_code, equal_to(200))
    assert_that(update_response.json()["provided_toolkits"], equal_to(toolkits))


@pytest.mark.regression
def test_put_nonexistent_provider(providers_utils):
    response = providers_utils.update_provider(nonexistent_id, {})

    assert_that(response.status_code, equal_to(404))
    assert_that(
        response.json()["error"]["details"],
        equal_to(
            f"The provider with ID [{nonexistent_id}] could not be found in the system."
        ),
    )


# =============================================================================
# DELETE /v1/providers/{provider_id} - Delete specific provider
# =============================================================================


@pytest.mark.regression
def test_delete_provider_endpoint(providers_utils):
    provider_id = providers_utils.create_provider()
    delete_response = providers_utils.send_delete_provider_request(provider_id)

    assert_that(delete_response.status_code, equal_to(204))

    response = providers_utils.get_provider_by_id(provider_id)

    assert_that(response.status_code, equal_to(404))

    assert_that(
        response.json()["error"]["details"],
        equal_to(
            f"The provider with ID [{provider_id}] could not be found in the system."
        ),
    )


@pytest.mark.regression
def test_delete_nonexistent_provider(providers_utils):
    """Test error handling when requesting nonexistent provider."""
    response = providers_utils.send_delete_provider_request(nonexistent_id)

    assert_that(response.status_code, equal_to(404))

    assert_that(
        response.json()["error"]["details"],
        equal_to(
            f"The provider with ID [{nonexistent_id}] could not be found in the system."
        ),
    )

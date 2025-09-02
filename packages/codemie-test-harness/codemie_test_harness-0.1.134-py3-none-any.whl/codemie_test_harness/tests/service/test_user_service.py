"""Integration tests for UserService."""

from codemie_sdk import CodeMieClient
from codemie_sdk.models.user import User, UserData


def test_about_me(client: CodeMieClient):
    """Test successful retrieval of user profile."""
    user = client.users.about_me()
    assert isinstance(user, User)
    assert user.user_id is not None
    assert user.name is not None
    assert user.username is not None
    assert isinstance(user.is_admin, bool)
    assert isinstance(user.applications, list)
    assert isinstance(user.applications_admin, list)
    assert isinstance(user.knowledge_bases, list)


def test_get_data(client: CodeMieClient):
    """Test successful retrieval of user data."""
    user_data = client.users.get_data()
    assert isinstance(user_data, UserData)
    assert user_data.user_id is not None

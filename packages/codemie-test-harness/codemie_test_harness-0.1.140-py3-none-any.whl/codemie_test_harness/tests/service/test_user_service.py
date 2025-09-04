import os
from codemie_sdk.models.user import User, UserData
from hamcrest import (
    assert_that,
    instance_of,
    is_not,
    all_of,
    has_property,
)


def test_about_me(user_utils):
    user = user_utils.get_about_me()

    assert_that(
        user,
        all_of(
            instance_of(User),
            has_property("user_id", is_not(None)),
            has_property("name", os.getenv("AUTH_USERNAME")),
            has_property("username", os.getenv("AUTH_USERNAME")),
            has_property("is_admin", is_not(None)),
            has_property("applications", instance_of(list)),
            has_property("applications_admin", instance_of(list)),
            has_property("knowledge_bases", instance_of(list)),
        ),
        "User profile should have all required properties with correct types",
    )


def test_get_user_data(user_utils):
    user_data = user_utils.get_user_data()

    assert_that(
        user_data,
        all_of(
            instance_of(UserData),
            has_property("user_id", is_not(None)),
        ),
        "User data should be valid UserData instance with user_id",
    )

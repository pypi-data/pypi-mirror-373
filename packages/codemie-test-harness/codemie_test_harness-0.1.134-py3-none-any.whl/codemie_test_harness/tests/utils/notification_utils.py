import logging
from typing import Optional

import requests

from codemie_test_harness.tests import AwsParameterStore

logger = logging.getLogger(__name__)


class OAuthGmailTokenRetriever:
    _instance = None
    token: Optional[str] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OAuthGmailTokenRetriever, cls).__new__(cls)
            cls._fetch_access_token()
        return cls._instance

    @staticmethod
    def _fetch_access_token():
        credentials = AwsParameterStore.get_cloud_provider_credentials("email")

        token_url = credentials["oauth"]["url"]
        if token_url is None:
            raise ValueError("Missing url")

        client_id = credentials["oauth"]["client_id"]
        if client_id is None:
            raise ValueError("Missing client_id")

        client_secret = credentials["oauth"]["client_secret"]
        if client_secret is None:
            raise ValueError("Missing client_secret")

        refresh_token = credentials["oauth"]["refresh_token"]
        if refresh_token is None:
            raise ValueError("Missing refresh_token")

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(
            token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            logger.error(f"Failed to obtain gmail access token {response.reason}")
            raise RuntimeError(
                f"Failed to obtain gmail access token: {response.reason}"
            )

        OAuthGmailTokenRetriever._instance.token = response.json().get("access_token")


class GmailUtils:
    def __init__(self, base_url: str = "https://gmail.googleapis.com/gmail/v1"):
        self.base_url = base_url
        self.token = OAuthGmailTokenRetriever().token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def get_messages_list(self):
        logger.info("Get All Messages From Inbox")
        url = self._build_url("/users/me/messages")
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_specific_message_content(self, message_id: str):
        logger.info(f"Get Specific Message Content From {message_id}")
        url = self._build_url(f"/users/me/messages/{message_id}")
        response = requests.get(url, headers=self.headers)
        return response.json()

    def delete_specific_message(self, message_id: str):
        logger.info(f"Delete Specific Message With Id {message_id}")
        url = self._build_url(f"/users/me/messages/{message_id}")
        requests.delete(url, headers=self.headers)

    def delete_all_messages(self):
        logger.info("Deleting all messages from Gmail inbox...")
        message_data = self.get_messages_list()

        messages = message_data.get("messages", [])
        if not messages:
            logger.info("No messages found to delete.")
            return

        for msg in messages:
            message_id = msg["id"]
            self.delete_specific_message(message_id)

        logger.info("Finished deleting all messages.")

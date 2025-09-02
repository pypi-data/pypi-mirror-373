import logging
import time
from typing import Any, Optional

import requests

from air import __base_url__, __version__

# Set up logging
logger = logging.getLogger(__name__)


class Authenticator:
    """Handles authentication for the AI Refinery platform."""

    timeout = 3000  # Token validity duration in seconds

    def __init__(
        self,
        account: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Authenticator, attempting to log in using provided credentials.

        Args:
            account (Optional[str]): Account name for authentication.
            api_key (Optional[str]): API key for authentication.
            base_url (Optional[str]): Base URL AIRefinery API; if not provided, defaults are used.
        """
        print(
            "The Authenticator class is going to be "
            "deprecated in future releases. "
            "AIRefinery authentication has been integrated into the connection itself."
        )
        if account is None:
            return
        if base_url is None or base_url == "":
            self.base_url = __base_url__
        else:
            self.base_url = base_url
        self.account = account
        self.api_key = api_key if api_key else ""
        self.access_token = self.login()
        self.time = time.time()

    def openai(self, base_url: Optional[str] = None) -> dict[str, Any]:
        """
        Prepare and return configuration for interaction with AIRefineru Inference service.

        Args:
            base_url (Optional[str]): Base URL AIRefinery API; if not provided, defaults are used.

        Returns:
            dict[str, Any]: Dictionary containing base_url, api_key, and default_headers.
        """
        if base_url is None or base_url == "":
            base_url = f"{self.base_url}/inference"
        else:
            base_url = f"{base_url}/inference"
        return {
            "base_url": base_url,
            "api_key": self.login(),
        }

    def login(self) -> str:
        """
        Log in using the provided client id and client secret.

        Returns:
            str: The access token if login was successful, empty string otherwise.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "sdk_version": __version__,
            }
            data = {
                "api_key": self.api_key,
            }
            url = f"{self.base_url}/authentication/validate"

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Failed to login: %s", e)
            return ""
        return self.api_key

    def get_access_token(self) -> str:
        """
        Retrieve a valid access token, refreshing it if necessary.

        Returns:
            str: The valid access token.
        """
        return self.login()

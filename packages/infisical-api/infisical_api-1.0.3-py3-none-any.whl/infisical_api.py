"""Infisical REST API Client

DEPRECATED: This library is deprecated in favor of the official Infisical Python SDK.
Please use the official SDK: https://infisical.com/docs/documentation/guides/python
"""  # pylint: disable=invalid-name

import sys
import json
import warnings
import requests # type: ignore
from loguru import logger


class infisical_api:  # pylint: disable=invalid-name
    """Infisical API Functions
    
    DEPRECATED: This class is deprecated in favor of the official Infisical Python SDK.
    Please use the official SDK: https://infisical.com/docs/documentation/guides/python
    """

    def __init__(
        self,
        service_token: str,
        infisical_url: str = "https://app.infisical.com",
        workspace_id: str = "dynamic",
        log_level: str = "INFO",
    ):
        warnings.warn(
            "infisical_api is deprecated. Please use the official Infisical Python SDK: "
            "https://infisical.com/docs/documentation/guides/python",
            DeprecationWarning,
            stacklevel=2
        )
        self.service_token = service_token
        self.infisical_url = infisical_url
        self.workspace_id = workspace_id
        logger.remove()
        logger.add(sys.stderr, level=log_level)

    def get_secret(
        self, secret_name: str, environment: str = "prod", path: str = "/"
    ) -> dict:  # pylint: disable=no-self-argument
        """Retrieve Secret
        
        DEPRECATED: This method is deprecated in favor of the official Infisical Python SDK.
        Please use the official SDK: https://infisical.com/docs/documentation/guides/python
        """
        warnings.warn(
            "get_secret is deprecated. Please use the official Infisical Python SDK: "
            "https://infisical.com/docs/documentation/guides/python",
            DeprecationWarning,
            stacklevel=2
        )
        if self.service_token == "":
            raise PermissionError("Please provide a valid service_token")

        try:
            if self.workspace_id == "dynamic":
                workspace_id = self.get_workspace_id()
            else:
                workspace_id = self.workspace_id
            response = requests.get(
                url=f"{self.infisical_url}/api/v3/secrets/raw/{secret_name}",
                params={
                    "workspaceId": workspace_id,
                    "environment": environment,
                    "secretPath": path,
                },
                headers={
                    "Authorization": f"Bearer {self.service_token}",
                },
                timeout=15,
            )
            data = json.loads(response.text)
            logger.debug(data)
            secret = data["secret"]
            return convert_to_dot_notation(secret)
        except requests.exceptions.RequestException:
            return {}

    def get_workspace_id(self) -> str:
        """Get Workspace ID
        
        DEPRECATED: This method is deprecated in favor of the official Infisical Python SDK.
        Please use the official SDK: https://infisical.com/docs/documentation/guides/python
        """
        warnings.warn(
            "get_workspace_id is deprecated. Please use the official Infisical Python SDK: "
            "https://infisical.com/docs/documentation/guides/python",
            DeprecationWarning,
            stacklevel=2
        )
        logger.trace("Getting Workspace ID")
        try:
            logger.trace("Getting Workspace ID-try")
            response = requests.get(
                url=f"{self.infisical_url}/api/v2/service-token",
                headers={
                    "Authorization": f"Bearer {self.service_token}",
                },
                timeout=15,
            )
            logger.debug(response)
            data = json.loads(response.text)
            logger.debug(data)
            return data["workspace"]
        except requests.exceptions.RequestException as e:
            logger.error(e)
            print("Failed to get Workspace ID")
            return ""


class convert_to_dot_notation(dict):
    """
    Access dictionary attributes via dot notation
    
    DEPRECATED: This class is deprecated in favor of the official Infisical Python SDK.
    Please use the official SDK: https://infisical.com/docs/documentation/guides/python
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            "convert_to_dot_notation is deprecated. Please use the official Infisical Python SDK: "
            "https://infisical.com/docs/documentation/guides/python",
            DeprecationWarning,
            stacklevel=2
        )

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore

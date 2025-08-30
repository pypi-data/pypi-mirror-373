"""Authentication module for CubeParser API."""

import os
from typing import Optional
import httpx
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class CubeParserAuth:
    """Handles authentication with CubeParser API."""

    def __init__(self):
        load_dotenv()
        self.username = os.getenv("CUBEPARSER_USERNAME")
        self.password = os.getenv("CUBEPARSER_PASSWORD")
        self.base_url = os.getenv("CUBEPARSER_BASEURL", "https://cubeparser.cn/")
        self._token: Optional[str] = None

        if not self.username or not self.password:
            raise ValueError(
                "CUBEPARSER_USERNAME and CUBEPARSER_PASSWORD must be provided in .env file"
            )

    async def get_token(self) -> str:
        """Get authentication token, refreshing if necessary."""
        if self._token is None:
            await self._refresh_token()
        return self._token

    async def _refresh_token(self) -> None:
        """Refresh the authentication token."""
        async with httpx.AsyncClient() as client:
            try:
                # Prepare form data for token request
                data = {
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password",
                }

                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                response = await client.post(
                    f"{self.base_url}api/token", data=data, headers=headers
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self._token = token_data.get("access_token")
                    if not self._token:
                        raise ValueError("No access_token in response")
                    logger.info("Successfully obtained authentication token")
                else:
                    logger.error(
                        f"Token request failed: {response.status_code} - {response.text}"
                    )
                    raise httpx.HTTPStatusError(
                        f"Authentication failed: {response.status_code}",
                        request=response.request,
                        response=response,
                    )

            except httpx.RequestError as e:
                logger.error(f"Network error during authentication: {e}")
                raise

    async def get_headers(self) -> dict:
        """Get headers with authentication token."""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_base_url(self) -> str:
        """Get the base URL for API requests."""
        return self.base_url

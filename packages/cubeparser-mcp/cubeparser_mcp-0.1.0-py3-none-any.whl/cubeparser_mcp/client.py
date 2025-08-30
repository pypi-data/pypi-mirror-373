"""CubeParser API client module."""

import httpx
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from .auth import CubeParserAuth

logger = logging.getLogger(__name__)


class CubeParserClient:
    """Client for interacting with CubeParser API."""

    def __init__(self):
        self.auth = CubeParserAuth()

    async def get_templates(self) -> List[Dict[str, Any]]:
        """Get list of available extraction templates."""
        try:
            headers = await self.auth.get_headers()
            base_url = self.auth.get_base_url()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}api/extractors", headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    # Extract templates from the response
                    # Based on API response: {"code":200,"message":"Done","items":[...]}
                    if isinstance(data, dict) and "items" in data:
                        templates = data["items"]
                    elif isinstance(data, dict) and "data" in data:
                        templates = data["data"]
                    elif isinstance(data, list):
                        templates = data
                    else:
                        templates = [data]

                    logger.info(f"Retrieved {len(templates)} templates")
                    return templates
                else:
                    logger.error(
                        f"Failed to get templates: {response.status_code} - {response.text}"
                    )
                    raise httpx.HTTPStatusError(
                        f"Failed to get templates: {response.status_code}",
                        request=response.request,
                        response=response,
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error getting templates: {e}")
            raise

    async def create_extraction_task(
        self, file_path: str, template_id: str
    ) -> Dict[str, Any]:
        """Create an extraction task with file upload."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            headers = await self.auth.get_headers()
            # Remove Content-Type for multipart form data
            headers.pop("Content-Type", None)
            base_url = self.auth.get_base_url()

            async with httpx.AsyncClient() as client:
                with open(file_path_obj, "rb") as f:
                    files = {
                        "file": (file_path_obj.name, f, "application/octet-stream")
                    }
                    data = {"template_id": template_id}

                    response = await client.post(
                        f"{base_url}api/extractor_file/{template_id}/files",
                        headers=headers,
                        files=files,
                        data=data,
                    )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Created extraction task: {result}")
                    return result
                else:
                    logger.error(
                        f"Failed to create extraction task: {response.status_code} - {response.text}"
                    )
                    raise httpx.HTTPStatusError(
                        f"Failed to create extraction task: {response.status_code}",
                        request=response.request,
                        response=response,
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error creating extraction task: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            raise

    async def download_results(self, task_id: str) -> Dict[str, Any]:
        """Download extraction results by task ID.

        Note: task_id should be in format 'extractor_id/file_id' or just 'file_id'
        """
        try:
            headers = await self.auth.get_headers()
            base_url = self.auth.get_base_url()

            async with httpx.AsyncClient() as client:
                # If task_id contains '/', split it into extractor_id and file_id
                if "/" in task_id:
                    extractor_id, file_id = task_id.split("/", 1)
                    # Try to get file details first
                    response = await client.get(
                        f"{base_url}api/extractor_file/{extractor_id}/files/{file_id}",
                        headers=headers,
                    )
                else:
                    # Assume task_id is a file_id, try to find it
                    # This is a fallback - ideally we should have both IDs
                    response = await client.get(
                        f"{base_url}api/extractors/{task_id}", headers=headers
                    )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Retrieved results for task {task_id}")
                    return result
                else:
                    logger.error(
                        f"Failed to download results: {response.status_code} - {response.text}"
                    )
                    raise httpx.HTTPStatusError(
                        f"Failed to download results: {response.status_code}",
                        request=response.request,
                        response=response,
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error downloading results: {e}")
            raise

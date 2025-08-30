"""CubeParser MCP Server implementation."""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List
from .client import CubeParserClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CubeParser client
client = CubeParserClient()


async def get_template_list() -> List[Dict[str, Any]]:
    """
    Get list of available extraction templates from CubeParser.

    Returns:
        List of template objects with their IDs, names, and descriptions.
    """
    try:
        templates = await client.get_templates()

        # Format templates for better readability
        formatted_templates = []
        for template in templates:
            formatted_template = {
                "id": template.get("uuid", template.get("id", "unknown")),
                "name": template.get("name", "Unknown Template"),
                "description": template.get("description", "No description available"),
                "created_at": template.get("created", ""),
                "updated_at": template.get("updated", ""),
            }
            formatted_templates.append(formatted_template)

        logger.info(f"Successfully retrieved {len(formatted_templates)} templates")
        return formatted_templates

    except Exception as e:
        logger.error(f"Error getting template list: {e}")
        raise Exception(f"Failed to get template list: {str(e)}")


async def create_extraction_task(file_path: str, template_id: str) -> Dict[str, Any]:
    """
    Create an extraction task by uploading a file and specifying a template.

    Args:
        file_path: Path to the file to be processed
        template_id: ID of the template to use for extraction

    Returns:
        Task information including task ID and status.
    """
    try:
        if not file_path:
            raise ValueError("file_path is required")
        if not template_id:
            raise ValueError("template_id is required")

        result = await client.create_extraction_task(file_path, template_id)

        # Format result for better readability
        # Extract task info from the nested response structure
        task_info = result.get("items", result)
        formatted_result = {
            "task_id": task_info.get(
                "uuid", task_info.get("id", task_info.get("task_id", "unknown"))
            ),
            "status": task_info.get("status", result.get("status", "unknown")),
            "file_name": (
                file_path.split("/")[-1]
                if "/" in file_path
                else file_path.split("\\")[-1]
            ),
            "template_id": template_id,
            "created_at": result.get("created_at", ""),
            "message": result.get("message", "Task created successfully"),
        }

        logger.info(
            f"Successfully created extraction task: {formatted_result['task_id']}"
        )
        return formatted_result

    except Exception as e:
        logger.error(f"Error creating extraction task: {e}")
        raise Exception(f"Failed to create extraction task: {str(e)}")


async def download_extraction_results(task_id: str) -> Dict[str, Any]:
    """
    Download extraction results for a completed task.

    Args:
        task_id: ID of the extraction task

    Returns:
        Extraction results and task status information.
    """
    try:
        if not task_id:
            raise ValueError("task_id is required")

        result = await client.download_results(task_id)

        # Format result for better readability
        formatted_result = {
            "task_id": task_id,
            "status": result.get("status", "unknown"),
            "results": result.get("results", result.get("data", {})),
            "completed_at": result.get("completed_at", ""),
            "processing_time": result.get("processing_time", ""),
            "message": result.get("message", "Results retrieved successfully"),
        }

        logger.info(f"Successfully downloaded results for task: {task_id}")
        return formatted_result

    except Exception as e:
        logger.error(f"Error downloading extraction results: {e}")
        raise Exception(f"Failed to download extraction results: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("CubeParser MCP Server functions are available")
        logger.info("Available functions:")
        logger.info("- get_template_list()")
        logger.info("- create_extraction_task(file_path, template_id)")
        logger.info("- download_extraction_results(task_id)")
        print("CubeParser MCP Server is ready. Import the functions to use them.")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()

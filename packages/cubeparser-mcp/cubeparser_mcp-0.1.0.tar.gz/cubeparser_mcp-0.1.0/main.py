#!/usr/bin/env python3
"""
CubeParser MCP Server - Main Entry Point

This is a Model Context Protocol (MCP) server that provides access to CubeParser API
for document extraction and parsing.

Usage:
    uvx cubeparser-mcp
    # or with absolute path:
    uvx --from /absolute/path/to/cubeparser_mcp cubeparser-mcp

Available MCP Tools:
- get_template_list: Get list of available extraction templates
- create_extraction_task: Create a new extraction task with a file and template
- download_extraction_results: Download results from a completed extraction task

Environment Variables Required:
- CUBEPARSER_USERNAME: Your CubeParser username
- CUBEPARSER_PASSWORD: Your CubeParser password
- CUBEPARSER_BASEURL: CubeParser API base URL (default: https://cubeparser.cn/)
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP
from cubeparser_mcp.server import (
    get_template_list,
    create_extraction_task,
    download_extraction_results,
)

# Configure logging to stderr so it doesn't interfere with MCP stdio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("CubeParser MCP Server")


@mcp.tool()
async def get_templates() -> List[Dict[str, Any]]:
    """
    Get list of available extraction templates from CubeParser.

    Returns:
        List of template objects with their IDs, names, and descriptions.
    """
    logger.info("Getting template list...")
    return await get_template_list()


@mcp.tool()
async def create_task(file_path: str, template_id: str) -> Dict[str, Any]:
    """
    Create an extraction task by uploading a file and specifying a template.

    Args:
        file_path: Absolute path to the file to be processed
        template_id: ID of the template to use for extraction

    Returns:
        Task information including task ID and status.
    """
    logger.info(f"Creating extraction task for file: {file_path}")
    return await create_extraction_task(file_path, template_id)


@mcp.tool()
async def download_results(task_id: str) -> Dict[str, Any]:
    """
    Download extraction results for a completed task.

    Args:
        task_id: ID of the extraction task

    Returns:
        Extraction results and task status information.
    """
    logger.info(f"Downloading results for task: {task_id}")
    return await download_extraction_results(task_id)


def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting CubeParser MCP Server...")
        logger.info("Available tools: get_templates, create_task, download_results")

        # Run the FastMCP server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

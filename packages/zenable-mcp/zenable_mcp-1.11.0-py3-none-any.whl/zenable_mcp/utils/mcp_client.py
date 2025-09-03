"""Shared MCP client for communicating with the Zenable MCP server."""

import json
import os
from pathlib import Path
from typing import Any, Optional

import click
import git
from fastmcp import Client as FastMCPClient

from zenable_mcp.exceptions import APIError, ConfigurationError
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona


class ZenableMCPClient:
    """Client for communicating with the Zenable MCP server."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Zenable MCP client.

        Args:
            api_key: API key for authentication
            base_url: Optional base URL for the MCP server

        Raises:
            ConfigurationError: If API key is empty
        """
        if not api_key:
            raise ConfigurationError("API key cannot be empty")
        self.api_key = api_key
        self.base_url: str = (
            base_url
            or os.environ.get("ZENABLE_MCP_URL")
            or "https://mcp.www.zenable.app"
        )
        # Configure fastmcp client with authentication
        self.config = {
            "mcpServers": {
                "zenable": {
                    "transport": "sse",
                    "url": f"{self.base_url}/",
                    "headers": {
                        "API_KEY": self.api_key,
                        "Content-Type": "application/json",
                    },
                }
            }
        }
        self.client = None

    async def __aenter__(self):
        """Enter async context manager."""
        echo(f"Connecting to MCP server at {self.base_url}", persona=Persona.POWER_USER)
        self.client = FastMCPClient(self.config)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def check_conformance(
        self,
        files: list[dict[str, str]],
        batch_size: int = 5,
        show_progress: bool = True,
        ctx: Optional[click.Context] = None,
    ) -> list[dict[str, Any]]:
        """
        Call the conformance_check tool with the list of files.

        Args:
            files: List of file dictionaries with 'path' and 'content'
            batch_size: Maximum number of files to send at once (default 5, max 5)
            show_progress: Whether to show progress messages (default True)
            ctx: Optional Click context object containing configuration

        Returns:
            List of results for each batch with files
        """
        if not self.client:
            raise APIError("Client not initialized. Use async with statement.")

        # Enforce maximum batch size of 5
        if batch_size > 5:
            batch_size = 5

        all_results = []
        total_files = len(files)

        # Single file doesn't need batching
        if total_files == 1:
            echo("Processing single file", persona=Persona.DEVELOPER)
            try:
                result = await self.client.call_tool(
                    "conformance_check", {"list_of_files": files}
                )
                echo("Received response from MCP server", persona=Persona.DEVELOPER)

                batch_results = {
                    "batch": 1,
                    "files": files,
                    "result": result,
                    "error": None,
                }
                all_results.append(batch_results)
            except Exception as e:
                echo(f"Error processing file: {e}", persona=Persona.DEVELOPER, err=True)
                batch_results = {
                    "batch": 1,
                    "files": files,
                    "result": None,
                    "error": str(e),
                }
                all_results.append(batch_results)

            return all_results

        # Process multiple files in batches
        files_processed = 0
        files_with_issues = 0

        echo(
            f"Processing {total_files} files in batches of {batch_size}",
            persona=Persona.DEVELOPER,
        )
        for i in range(0, total_files, batch_size):
            batch = files[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            echo(
                f"Processing batch {batch_num} with {len(batch)} files",
                persona=Persona.DEVELOPER,
            )

            if show_progress:
                # Show progress
                echo(
                    f"\nChecking files {i + 1}-{min(i + len(batch), total_files)} of {total_files}...",
                    log=False,
                )

                # Show which files are in this batch
                for file_dict in batch:
                    file_path = Path(file_dict["path"])
                    # Try to make path relative to working directory
                    try:
                        rel_path = file_path.relative_to(Path.cwd())
                    except ValueError:
                        # If not relative to cwd, try relative to git root
                        try:
                            repo = git.Repo(search_parent_directories=True)
                            rel_path = file_path.relative_to(repo.working_dir)
                        except Exception:
                            rel_path = file_path
                    echo(f"  - {rel_path}", persona=Persona.POWER_USER)

            try:
                echo(
                    f"Calling conformance_check tool for batch {batch_num}",
                    persona=Persona.DEVELOPER,
                )
                result = await self.client.call_tool(
                    "conformance_check", {"list_of_files": batch}
                )
                echo(
                    f"Received response for batch {batch_num}",
                    persona=Persona.DEVELOPER,
                )

                # Store batch with its files for later processing
                batch_results = {
                    "batch": batch_num,
                    "files": batch,
                    "result": result,
                    "error": None,
                }
                all_results.append(batch_results)

                if show_progress:
                    # Parse and show interim results
                    if (
                        hasattr(result, "content")
                        and result.content
                        and len(result.content) > 0
                    ):
                        content_text = (
                            result.content[0].text
                            if hasattr(result.content[0], "text")
                            else str(result.content[0])
                        )

                        # Try to parse the result to get file-specific information
                        try:
                            parsed_result = json.loads(content_text)
                            # Assume the result contains information about each file
                            if isinstance(parsed_result, dict):
                                # Count files with issues in this batch
                                batch_issues = 0
                                if "files" in parsed_result:
                                    for file_result in parsed_result["files"]:
                                        if file_result.get("issues", []):
                                            batch_issues += 1
                                elif (
                                    "issues" in parsed_result
                                    and parsed_result["issues"]
                                ):
                                    batch_issues = len(batch)

                                files_with_issues += batch_issues
                                files_processed += len(batch)

                                # Show running total
                                echo(
                                    f"Progress: {files_processed}/{total_files} files checked, {files_with_issues} with issues",
                                    log=False,
                                )
                        except (json.JSONDecodeError, KeyError):
                            files_processed += len(batch)
                            echo(
                                f"Progress: {files_processed}/{total_files} files checked",
                                log=False,
                            )
                    else:
                        files_processed += len(batch)
                        echo(
                            f"Progress: {files_processed}/{total_files} files checked",
                            log=False,
                        )

            except Exception as e:
                # Handle errors per batch
                if show_progress:
                    echo(f"✗ Error processing files: {e}", err=True, log=False)
                batch_results = {
                    "batch": batch_num,
                    "files": batch,
                    "result": None,
                    "error": str(e),
                }
                all_results.append(batch_results)
                files_processed += len(batch)
                files_with_issues += len(batch)  # Count errored files as having issues

        return all_results

    def has_findings(
        self, parsed_result: Optional[dict[str, Any]], result_text: str = ""
    ) -> bool:
        """
        Check if the conformance result has any findings (issues).

        Args:
            parsed_result: Parsed JSON result from conformance check
            result_text: Raw text result as fallback

        Returns:
            True if there are findings/issues, False otherwise
        """
        if parsed_result:
            # Check for any non-PASS statuses
            for file_path, file_result in parsed_result.items():
                if isinstance(file_result, dict):
                    status = file_result.get("status", "")
                    if status != "PASS" and status:
                        return True
        elif result_text:
            # Fallback check if parsing failed
            # Check for overall result status
            if "Result: FAIL" in result_text:
                return True
            # Also check for check-level failures
            if any(
                indicator in result_text
                for indicator in [
                    ": `fail`",
                    "ERROR",
                    "WARNING",
                    "Finding:",
                ]
            ):
                return True
        return False


def parse_conformance_results(
    results: list[dict[str, Any]],
) -> tuple[list[str], bool, bool]:
    """
    Parse conformance check results and extract findings.

    Args:
        results: List of batch results from check_conformance

    Returns:
        Tuple of (all_results_text, has_errors, has_findings)
    """
    all_results = []
    has_errors = False
    has_findings = False

    # Create a temporary client instance to use has_findings method
    # We don't need a real API key since we're just using the method
    temp_client = ZenableMCPClient("temp")

    for batch_result in results:
        if batch_result["error"]:
            has_errors = True
            all_results.append(f"Error: {batch_result['error']}")
        else:
            # Extract the text result from the MCP server
            result = batch_result["result"]
            if (
                hasattr(result, "content")
                and result.content
                and len(result.content) > 0
            ):
                content_text = (
                    result.content[0].text
                    if hasattr(result.content[0], "text")
                    else str(result.content[0])
                )
                all_results.append(content_text)

                # Check for findings in this batch
                try:
                    parsed = json.loads(content_text)
                    if isinstance(parsed, dict) and temp_client.has_findings(
                        parsed, content_text
                    ):
                        has_findings = True
                except (json.JSONDecodeError, KeyError):
                    # If we can't parse it, use the has_findings method with just text
                    if temp_client.has_findings(None, content_text):
                        has_findings = True
            else:
                all_results.append("No results returned")

    return all_results, has_errors, has_findings


def extract_file_results(result: Any) -> Optional[dict[str, Any]]:
    """
    Extract file results from MCP server response.

    Args:
        result: Raw result from MCP server

    Returns:
        Parsed dictionary of file results or None
    """
    if not hasattr(result, "content") or not result.content:
        return None

    try:
        content_text = (
            result.content[0].text
            if hasattr(result.content[0], "text")
            else str(result.content[0])
        )
        return json.loads(content_text)
    except (json.JSONDecodeError, AttributeError, IndexError):
        return None

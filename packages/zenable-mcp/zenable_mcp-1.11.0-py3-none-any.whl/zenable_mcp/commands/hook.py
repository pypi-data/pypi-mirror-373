"""Hook command for IDE integrations (Claude Code, etc.)."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.hook_input_handlers import InputHandlerRegistry
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.user_config.config_handler_factory import get_local_config_handler
from zenable_mcp.utils.files import filter_files_by_patterns
from zenable_mcp.utils.mcp_client import (
    ZenableMCPClient,
    extract_file_results,
)
from zenable_mcp.utils.zenable_config import filter_files_by_zenable_config


def process_hook_input(
    input_context, active_handler
) -> tuple[list[Path], Optional[str]]:
    """
    Process files from input handlers (hooks).

    Returns:
        Tuple of (file_paths, file_content_from_handler)
    """
    handler_files = input_context.files
    if not handler_files:
        echo(
            f"No files to process from {active_handler.name}", persona=Persona.DEVELOPER
        )
        return [], None

    # Check if we have file content (e.g., from Write tool)
    file_content_from_handler = None
    if input_context.metadata.get("file_content"):
        file_content_from_handler = input_context.metadata["file_content"]

    tool_name = input_context.metadata.get("tool_name", "Unknown")
    for fp in handler_files:
        echo(
            f"Using file from {active_handler.name} {tool_name} hook: {fp}",
            persona=Persona.DEVELOPER,
        )

    return handler_files, file_content_from_handler


@click.command()
@click.pass_context
def hook(ctx):
    """Handle calls from the hooks of Agentic IDEs

    This command is specifically designed for IDE integrations like Claude Code.
    It reads hook input from stdin, processes the files, and returns appropriate
    exit codes and formatted responses for the IDE to handle.

    To manually run a scan, use the 'check' command instead.
    """
    # Try to get API key from context object first, then from environment
    api_key = ctx.obj.get("api_key", "") if ctx.obj else ""
    if not api_key:
        api_key = os.environ.get("ZENABLE_API_KEY", "")

    if not api_key:
        echo("Error: ZENABLE_API_KEY environment variable not set", err=True, log=True)
        echo("Please set it with: export ZENABLE_API_KEY=your-api-key", err=True)
        sys.exit(ExitCode.MISSING_API_KEY)

    # Initialize input handler registry with auto-registration
    registry = InputHandlerRegistry()

    # Detect and parse input using the registry
    try:
        input_context = registry.detect_and_parse()
    except RuntimeError as e:
        # Multiple handlers claiming they can handle - exit with non-2 exit code
        echo(
            "Unknown failure, please report this at zenable.io/feedback",
            err=True,
            log=True,
        )
        echo(f"Error details: {e}", persona=Persona.DEVELOPER, err=True, log=True)
        sys.exit(ExitCode.HANDLER_CONFLICT)

    if not input_context:
        echo(
            "Error: No hook input detected. This command is for IDE hooks only.",
            err=True,
        )
        echo("To manually run a scan, use zenable-mcp check", err=True)
        sys.exit(ExitCode.NO_HOOK_INPUT)

    # Get the active handler after confirming input_context exists
    active_handler = registry.get_active_handler()
    echo(f"{active_handler.name} Hook Input Detected", persona=Persona.POWER_USER)
    if input_context.raw_data:
        echo(json.dumps(input_context.raw_data, indent=2), persona=Persona.DEVELOPER)

    # Load configuration to get patterns for filtering
    config_patterns = None
    config_exclude_patterns = None
    try:
        config_handler = get_local_config_handler()
        config, error = config_handler.load_config()

        if error:
            # This error is meant to be user facing; more debug details are logged inside of load_config()
            echo(error)

        # Get check patterns from config if available
        if hasattr(config, "check") and config.check:
            config_patterns = getattr(config.check, "patterns", None)
            config_exclude_patterns = getattr(config.check, "exclude_patterns", None)
    except Exception as e:
        echo(
            "Unknown failure loading config, please report this at zenable.io/feedback",
            err=True,
            log=True,
        )
        echo(f"Error loading config: {e}", persona=Persona.DEVELOPER)

    # Process hook input to get files
    file_paths, file_content_from_handler = process_hook_input(
        input_context, active_handler
    )

    if not file_paths:
        # No files to check
        response = active_handler.build_response_to_hook_call(False, "")
        if response:
            echo(response, err=True)
        sys.exit(ExitCode.SUCCESS)

    # Apply pattern filtering if we have config patterns
    if config_patterns or config_exclude_patterns:
        file_paths = filter_files_by_patterns(
            file_paths,
            patterns=config_patterns,
            exclude_patterns=config_exclude_patterns,
            handler_name=active_handler.name,
        )

        if not file_paths:
            # All files filtered out
            response = active_handler.build_response_to_hook_call(False, "")
            if response:
                echo(response, err=True)
            sys.exit(ExitCode.SUCCESS)

    # Apply zenable config filtering
    file_paths = filter_files_by_zenable_config(file_paths)

    if not file_paths:
        # All files filtered out by zenable config
        response = active_handler.build_response_to_hook_call(False, "")
        if response:
            echo(response, err=True)
        sys.exit(ExitCode.SUCCESS)

    # Read file contents
    files = []

    # Special handling when we have content from handler (e.g., Write tool)
    if file_content_from_handler and file_paths:
        # Use content provided by handler for the first file
        files.append({"path": str(file_paths[0]), "content": file_content_from_handler})
        # Read content for any additional files
        for file_path in file_paths[1:]:
            try:
                content = file_path.read_text()
                files.append({"path": str(file_path), "content": content})
            except Exception as e:
                echo(
                    f"Error reading {file_path}: {e}",
                    persona=Persona.POWER_USER,
                    err=True,
                    log=True,
                )
                continue
    else:
        # Normal file reading for all files
        for file_path in file_paths:
            try:
                content = file_path.read_text()
                files.append({"path": str(file_path), "content": content})
            except Exception as e:
                echo(
                    f"Error reading {file_path}: {e}",
                    persona=Persona.POWER_USER,
                    err=True,
                    log=True,
                )
                continue

    if not files:
        echo("Error: No files could be read", err=True, log=True)
        sys.exit(ExitCode.FILE_READ_ERROR)

    async def check_files():
        try:
            async with ZenableMCPClient(api_key) as client:
                # Process files without showing progress (hook mode is silent)
                results = await client.check_conformance(files, show_progress=False)

                echo(
                    f"Results from check_conformance: {results}",
                    persona=Persona.DEVELOPER,
                )

                # For hook mode, we only care about the first batch result
                # since hooks typically process single files
                if results:
                    result = (
                        results[0].get("result")
                        if not results[0].get("error")
                        else None
                    )
                    if results[0].get("error"):
                        raise Exception(results[0]["error"])
                else:
                    result = None

                echo(f"Extracted result: {result}", persona=Persona.DEVELOPER)

                # Extract file results using utility function
                parsed_result = extract_file_results(result)

                # Get the raw text content for fallback checking
                if result and hasattr(result, "content") and result.content:
                    raw_text = (
                        result.content[0].text
                        if hasattr(result.content[0], "text")
                        else str(result.content[0])
                    )
                else:
                    raw_text = ""

                # Use parsed result if available, otherwise use raw text
                result_text = json.dumps(parsed_result) if parsed_result else raw_text

                # Check if we have any findings (issues)
                has_findings = client.has_findings(parsed_result, result_text)

                echo(f"Parsed result: {parsed_result}", persona=Persona.DEVELOPER)
                echo(
                    f"Result text: {result_text[:200] if result_text else 'None'}",
                    persona=Persona.DEVELOPER,
                )
                echo(f"Has findings: {has_findings}", persona=Persona.DEVELOPER)

                # Use handler-specific response formatting (JSON for Claude Code)
                echo(
                    "About to call build_response_to_hook_call",
                    persona=Persona.DEVELOPER,
                )
                formatted_response = active_handler.build_response_to_hook_call(
                    has_findings, result_text if has_findings else ""
                )
                # Output JSON to stderr for Claude Code to parse
                if formatted_response:
                    echo(
                        "Writing formatted response to stderr",
                        persona=Persona.DEVELOPER,
                    )
                    echo(formatted_response, err=True, log=True)
                    echo("Finished writing JSON to stderr", persona=Persona.DEVELOPER)
                else:
                    echo(
                        "formatted_response is falsy, not writing",
                        persona=Persona.DEVELOPER,
                    )

                # Output plain text result to stdout for human review
                if has_findings and result_text:
                    echo("Writing plain text to stdout", persona=Persona.DEVELOPER)
                    echo(result_text)

                # Use handler-specific exit code
                exit_code = active_handler.get_exit_code(has_findings)
                echo(f"Exit code: {exit_code}", persona=Persona.DEVELOPER)
                sys.exit(exit_code)

        except Exception as e:
            echo(f"Error: {e}", err=True, log=True)
            sys.exit(ExitCode.API_ERROR)

    asyncio.run(check_files())

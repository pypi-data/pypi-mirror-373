"""Utility functions for working with Click context objects."""

import os
from typing import Optional

import click


def get_api_key_from_context(ctx: click.Context) -> Optional[str]:
    """Get API key from context hierarchy or environment variable.

    Args:
        ctx: Click context object

    Returns:
        API key string if found, None otherwise
    """
    # Check current context
    if ctx and ctx.obj and "api_key" in ctx.obj:
        api_key = ctx.obj.get("api_key")
        if api_key:
            return api_key

    # Walk up context hierarchy
    current_ctx = ctx
    while current_ctx:
        if current_ctx.obj and "api_key" in current_ctx.obj:
            api_key = current_ctx.obj.get("api_key")
            if api_key:
                return api_key
        current_ctx = current_ctx.parent

    # Fall back to environment variable
    return os.environ.get("ZENABLE_API_KEY")


def get_recursive_from_context(ctx: click.Context) -> bool:
    """Get recursive flag from context hierarchy.

    Walks up the context hierarchy looking for the recursive flag.

    Args:
        ctx: Click context object

    Returns:
        True if recursive flag is set anywhere in the hierarchy, False otherwise
    """
    # Walk up context hierarchy
    current_ctx = ctx
    while current_ctx:
        if current_ctx.obj and "recursive" in current_ctx.obj:
            recursive = current_ctx.obj.get("recursive", False)
            if recursive:
                return True
        current_ctx = current_ctx.parent

    return False


def get_dry_run_from_context(ctx: click.Context) -> bool:
    """Get dry_run flag from context hierarchy.

    Walks up the context hierarchy looking for the dry_run flag.

    Args:
        ctx: Click context object

    Returns:
        True if dry_run flag is set anywhere in the hierarchy, False otherwise
    """
    # Walk up context hierarchy
    current_ctx = ctx
    while current_ctx:
        if current_ctx.obj and "dry_run" in current_ctx.obj:
            dry_run = current_ctx.obj.get("dry_run", False)
            if dry_run:
                return True
        current_ctx = current_ctx.parent

    return False


def get_is_global_from_context(ctx: click.Context) -> bool:
    """Get is_global flag from context hierarchy.

    Walks up the context hierarchy looking for the is_global flag.

    Args:
        ctx: Click context object

    Returns:
        True if is_global flag is set anywhere in the hierarchy, False otherwise
    """
    # Walk up context hierarchy
    current_ctx = ctx
    while current_ctx:
        if current_ctx.obj and "is_global" in current_ctx.obj:
            is_global = current_ctx.obj.get("is_global", False)
            if is_global:
                return True
        current_ctx = current_ctx.parent

    return False


def get_git_repos_from_context(ctx: click.Context) -> Optional[list]:
    """Get git_repos list from context hierarchy.

    Walks up the context hierarchy looking for the git_repos list.

    Args:
        ctx: Click context object

    Returns:
        List of git repositories if found, None otherwise
    """
    # Walk up context hierarchy
    current_ctx = ctx
    while current_ctx:
        if current_ctx.obj and "git_repos" in current_ctx.obj:
            repos = current_ctx.obj.get("git_repos")
            if repos is not None:
                return repos
        current_ctx = current_ctx.parent

    return None

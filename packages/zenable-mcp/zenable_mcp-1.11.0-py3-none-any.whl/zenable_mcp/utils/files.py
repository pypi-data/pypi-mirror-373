"""
Consolidated file utilities for pattern matching, filtering, and file operations.
"""

import fnmatch
import warnings
from pathlib import Path
from typing import Optional, Union

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona


def _match_glob_pattern(
    filename: str, pattern: str, file_parts: tuple[str, ...], file_basename: str
) -> bool:
    """Helper function to handle glob pattern matching."""
    if "**" in pattern:
        return _match_double_star_pattern(filename, pattern, file_parts)
    else:
        return fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(
            file_basename, pattern
        )


def _match_double_star_pattern(
    filename: str, pattern: str, file_parts: tuple[str, ...]
) -> bool:
    """Helper function to handle ** patterns."""
    # Special case: pattern is exactly "**" - matches everything
    if pattern == "**":
        return True

    if pattern.startswith("**/"):
        simple_pattern = pattern[3:]

        if fnmatch.fnmatch(filename, simple_pattern) or fnmatch.fnmatch(
            file_parts[-1], simple_pattern
        ):
            return True

        for i in range(len(file_parts)):
            partial_path = "/".join(file_parts[i:])
            if fnmatch.fnmatch(partial_path, simple_pattern):
                return True

    if "/**/" in pattern:
        parts = pattern.split("/**/", 1)
        if len(parts) == 2:
            prefix, suffix = parts
            if filename.startswith(prefix + "/"):
                remaining = filename[len(prefix) + 1 :]
                return _match_suffix_pattern(remaining, suffix)

    # Always check the normalized pattern as a fallback
    pattern_normalized = pattern.replace("**", "*")
    return fnmatch.fnmatch(filename, pattern_normalized)


def _match_suffix_pattern(remaining_path: str, suffix: str) -> bool:
    """Helper function to match suffix patterns in ** expressions."""
    if "*" in suffix or "?" in suffix:
        remaining_parts = Path(remaining_path).parts
        for i in range(len(remaining_parts)):
            subpath = "/".join(remaining_parts[i:])
            if Path(subpath).match(suffix):
                return True
    else:
        return remaining_path.endswith(suffix)

    return False


def _match_exact_pattern(filename: str, pattern: str, file_basename: str) -> bool:
    """Helper function to handle exact pattern matching."""
    if pattern.startswith("/"):
        return filename == pattern[1:]
    elif pattern.startswith("./"):
        return filename == pattern[2:]
    elif "/" in pattern:
        if filename == pattern:
            return True
        return (
            filename.endswith("/" + pattern)
            and len(filename) > len(pattern) + 1
            and filename[-(len(pattern) + 1)] == "/"
        )
    else:
        return file_basename == pattern


def _matches_any_pattern(
    file_path: Path,
    patterns: list[str],
    base_path: Optional[Path] = None,
) -> bool:
    """
    Check if a file matches any of the given patterns.

    Args:
        file_path: File path to check
        patterns: List of patterns to match against
        base_path: Base path for relative matching (defaults to cwd)

    Returns:
        True if file matches any pattern, False otherwise
    """
    # Try to get relative path for matching
    if base_path is None:
        base_path = Path.cwd()

    try:
        rel_path = file_path.relative_to(base_path)
        file_str = str(rel_path)
        file_parts = rel_path.parts
    except ValueError:
        # If can't get relative path, use absolute
        file_str = str(file_path)
        file_parts = file_path.parts

    file_basename = file_path.name

    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            if _match_glob_pattern(file_str, pattern, file_parts, file_basename):
                return True
        else:
            if _match_exact_pattern(file_str, pattern, file_basename):
                return True
    return False


def filter_files_by_patterns(
    files: list[Path],
    patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    handler_name: Optional[str] = None,
    directory_only: bool = False,
) -> list[Path]:
    """
    Filter files based on include and exclude patterns.

    Args:
        files: List of file paths to filter
        patterns: Include patterns (if None, all files are included)
        exclude_patterns: Exclude patterns (if None, no files are excluded)
        handler_name: Name of the handler for logging purposes
        directory_only: If True, only include directories in the results

    Returns:
        Filtered list of file paths
    """
    filtered_files = []
    base_path = Path.cwd()

    for file_path in files:
        # Get relative path for cleaner logging
        try:
            rel_path = file_path.relative_to(base_path)
        except ValueError:
            rel_path = file_path

        # If directory_only is True, skip non-directories
        if directory_only and not file_path.is_dir():
            if handler_name:
                echo(
                    f"{handler_name} passed in file ./{rel_path}, but directory_only filter excluded it",
                    persona=Persona.POWER_USER,
                )
            continue

        # Check include patterns (if specified)
        if patterns and not _matches_any_pattern(file_path, patterns, base_path):
            if handler_name:
                echo(
                    f"{handler_name} passed in file ./{rel_path}, but it was filtered out by the include pattern",
                    persona=Persona.POWER_USER,
                )
            continue

        # Check exclude patterns
        if exclude_patterns and _matches_any_pattern(
            file_path, exclude_patterns, base_path
        ):
            if handler_name:
                echo(
                    f"{handler_name} passed in file ./{rel_path}, but it was filtered out by the exclude pattern",
                    persona=Persona.POWER_USER,
                )
            continue

        filtered_files.append(file_path)

    return filtered_files


def expand_file_patterns(
    patterns: list[str],
    base_path: Optional[Path] = None,
    exclude_patterns: Optional[list[str]] = None,
    max_files: Optional[int] = None,
    directory_only: bool = False,
) -> list[Path]:
    """
    Expand file patterns (including globs) into a list of file paths.

    Args:
        patterns: List of file patterns (can be paths or glob patterns like '**/*.py')
        base_path: Base directory to search from (defaults to current directory)
        exclude_patterns: Optional list of patterns to exclude
        max_files: Optional maximum number of files to return (for safety)
        directory_only: If True, only include directories in the results

    Returns:
        List of resolved file paths

    Raises:
        ValueError: If dangerous patterns are detected
    """
    # Validate patterns for dangerous operations
    for pattern in patterns:
        _validate_pattern(pattern)

    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    exclude_patterns = exclude_patterns or []
    exclude_paths = _expand_patterns(exclude_patterns, base_path, directory_only)

    all_files = []
    for pattern in patterns:
        files = _expand_pattern(pattern, base_path, directory_only)
        # Filter out excluded files
        files = [f for f in files if f not in exclude_paths]
        all_files.extend(files)

    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    # Apply max_files limit if specified
    if max_files is not None and len(unique_files) > max_files:
        echo(
            f"Found {len(unique_files)} files, limiting to {max_files}. "
            "Consider using more specific patterns.",
            persona=Persona.POWER_USER,
            err=True,
        )
        unique_files = unique_files[:max_files]

    return unique_files


def _expand_pattern(
    pattern: str, base_path: Path, directory_only: bool = False
) -> list[Path]:
    """
    Expand a single pattern into file paths.

    Args:
        pattern: A file pattern (path or glob)
        base_path: Base directory to search from
        directory_only: If True, only include directories in the results

    Returns:
        List of matching file paths
    """
    # Warn if pattern starts with / (even for absolute patterns)
    if pattern.startswith("/"):
        warnings.warn(
            f"Pattern '{pattern}' starts with '/'. Will be treated as relative to base path."
        )

    # First check if it's a direct file path
    path = Path(pattern)

    # If it's an absolute path
    if path.is_absolute():
        if directory_only:
            if path.exists() and path.is_dir():
                # For directory_only, return the directory itself
                return [path]
        else:
            if path.exists() and path.is_file():
                return [path]
            elif path.exists() and path.is_dir():
                # Only get files directly in this directory, not recursively
                return [f for f in path.iterdir() if f.is_file()]
        # For non-existent absolute paths, strip the leading slash and try as relative
        pattern = pattern.lstrip("/")
        path = Path(pattern)

    # Try relative to base_path
    full_path = base_path / path
    if directory_only:
        if full_path.exists() and full_path.is_dir():
            # Return the directory itself and all subdirectories recursively
            dirs = [full_path]
            dirs.extend([d for d in full_path.rglob("*") if d.is_dir()])
            return dirs
    else:
        if full_path.exists() and full_path.is_file():
            return [full_path]
        elif full_path.exists() and full_path.is_dir():
            # If it's a directory, get all files in it recursively
            return [f for f in full_path.rglob("*") if f.is_file()]

    # Treat as glob pattern
    # Handle special case of **/* patterns
    if "**" in pattern or "*" in pattern:
        matches = list(base_path.glob(pattern))
        if directory_only:
            return [m for m in matches if m.is_dir()]
        else:
            return [m for m in matches if m.is_file()]

    # If no glob chars and doesn't exist, return empty
    entity_type = "directories" if directory_only else "files"
    echo(
        f"Pattern '{pattern}' did not match any {entity_type}",
        persona=Persona.POWER_USER,
        err=True,
    )
    return []


def _expand_patterns(
    patterns: list[str], base_path: Path, directory_only: bool = False
) -> set[Path]:
    """
    Expand multiple patterns into a set of file paths.

    Args:
        patterns: List of file patterns
        base_path: Base directory to search from
        directory_only: If True, only include directories in the results

    Returns:
        Set of matching file paths
    """
    all_files = set()
    for pattern in patterns:
        all_files.update(_expand_pattern(pattern, base_path, directory_only))
    return all_files


def filter_by_extensions(
    files: list[Path],
    extensions: Optional[list[str]] = None,
) -> list[Path]:
    """
    Filter files by their extensions.

    Args:
        files: List of file paths
        extensions: List of extensions to include (e.g., ['.py', '.js'])

    Returns:
        Filtered list of file paths
    """
    if not extensions:
        return files

    # Normalize extensions to include dot
    extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    return [f for f in files if f.suffix in extensions]


def get_relative_paths(
    files: list[Path],
    base_path: Optional[Path] = None,
) -> list[str]:
    """
    Convert absolute paths to relative paths.

    Args:
        files: List of file paths
        base_path: Base directory to make paths relative to

    Returns:
        List of relative path strings
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    relative_paths = []
    for file in files:
        try:
            rel_path = file.relative_to(base_path)
            relative_paths.append(str(rel_path))
        except ValueError:
            # If file is not under base_path, use absolute path
            relative_paths.append(str(file))

    return relative_paths


def validate_files_exist(files: list[Union[str, Path]]) -> list[Path]:
    """
    Validate that files exist and return resolved paths.

    Args:
        files: List of file paths (as strings or Path objects)

    Returns:
        List of validated Path objects

    Raises:
        FileNotFoundError: If any file does not exist
    """
    validated = []
    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file}")
        if not path.is_file():
            raise ValueError(f"Not a file: {file}")
        validated.append(path.resolve())

    return validated


def _validate_pattern(pattern: str) -> None:
    """
    Validate a file pattern for dangerous operations.

    Args:
        pattern: The pattern to validate

    Raises:
        ValueError: If the pattern is considered dangerous
    """

    # Dangerous patterns that could scan entire filesystem
    dangerous_patterns = [
        "/**",  # Recursive scan from root
        "/*",  # All files in root
        "/",  # Root directory
    ]

    # Check for exact dangerous patterns
    if pattern in dangerous_patterns:
        raise ValueError(
            f"Dangerous pattern '{pattern}' detected. "
            "This would scan the entire filesystem or root directory. "
            "Please use more specific patterns."
        )

    # Don't warn here, we warn in _expand_pattern for patterns starting with /


def should_skip_file(filename: str, skip_patterns: list[str]) -> bool:
    """
    Check if a file should be skipped based on skip patterns.

    Supports:
    - Exact filename matches (e.g., "package-lock.json")
    - Glob patterns (e.g., "**/*.rbi", "foo/**/*.pyc")
    - Negation patterns with ! prefix (e.g., "!keep-this.json")
    - Escaped ! for literal filenames (e.g., "\\!important.txt" matches "!important.txt")

    Patterns are evaluated in order - the last matching pattern wins.
    This matches .gitignore behavior where later patterns can override earlier ones.

    Args:
        filename: The full file path from the PR
        skip_patterns: List of patterns to check against.
                      Order matters - the last matching pattern wins.

    Returns:
        True if the file should be skipped, False otherwise
    """
    file_path = Path(filename)
    file_parts = file_path.parts
    file_basename = file_path.name

    should_skip = False

    for pattern in skip_patterns:
        if pattern.startswith("\\!"):
            literal_pattern = pattern[1:]
            if "*" in literal_pattern or "?" in literal_pattern:
                if _match_glob_pattern(
                    filename, literal_pattern, file_parts, file_basename
                ):
                    should_skip = True
            else:
                if _match_exact_pattern(filename, literal_pattern, file_basename):
                    should_skip = True
        elif pattern.startswith("!"):
            negated_pattern = pattern[1:]
            if "*" in negated_pattern or "?" in negated_pattern:
                if _match_glob_pattern(
                    filename, negated_pattern, file_parts, file_basename
                ):
                    should_skip = False
            else:
                if _match_exact_pattern(filename, negated_pattern, file_basename):
                    should_skip = False
        else:
            if "*" in pattern or "?" in pattern:
                if _match_glob_pattern(filename, pattern, file_parts, file_basename):
                    should_skip = True
            else:
                if _match_exact_pattern(filename, pattern, file_basename):
                    should_skip = True

    return should_skip

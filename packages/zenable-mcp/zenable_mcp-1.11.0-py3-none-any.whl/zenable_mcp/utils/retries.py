"""Retry utilities for handling transient errors."""

import functools
import random
import time
import warnings
from typing import Callable, Optional

import requests


def is_transient_error(e: Exception, rate_limit_only: bool = False) -> bool:
    """
    Check if an exception is likely transient and worth retrying.

    Args:
        e: The exception to check
        rate_limit_only: If True, only check for rate limit errors

    Includes:
    - Rate limits (429, 403 with "rate limit")
    - Server errors (5xx) - unless rate_limit_only is True
    - Connection errors - unless rate_limit_only is True
    - Timeouts - unless rate_limit_only is True
    """
    # Check for requests HTTPError
    if isinstance(e, requests.HTTPError) and hasattr(e, "response") and e.response:
        # Check for rate limits
        if e.response.status_code == 429 or (
            e.response.status_code == 403 and "rate limit" in str(e).lower()
        ):
            return True

        # Check for server errors (unless only checking rate limits)
        if not rate_limit_only and 500 <= e.response.status_code < 600:
            return True

        # If it's an HTTPError with a response but not a transient status, return False
        return False

    # Check for connection/network errors (unless only checking rate limits)
    # Note: we exclude requests.HTTPError here because it's handled above
    if (
        not rate_limit_only
        and isinstance(
            e,
            (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ReadTimeout,
                TimeoutError,
                OSError,
            ),
        )
        and not isinstance(e, requests.HTTPError)
    ):
        return True

    return False


def retry_on_error(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    exceptions: Optional[tuple[type[Exception], ...]] = None,
    retryable_conditions: Optional[Callable[[Exception], bool]] = None,
    warning_message_func: Optional[Callable[[Exception, int, int, float], str]] = None,
    rate_limit_only: bool = False,
    excluded_exceptions: Optional[tuple[type[Exception], ...]] = None,
):
    """
    Decorator to retry a function on specified errors with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply the delay by for each retry
        exceptions: Tuple of exception types to catch and potentially retry on
        retryable_conditions: Optional function that takes an exception and returns
                            True if the error should be retried
        warning_message_func: Optional function to generate custom warning messages.
                            Takes (exception, attempt, max_retries, delay) and returns str.
        rate_limit_only: If True, only retry on rate limit errors (429, 403 with "rate limit")
        excluded_exceptions: Optional tuple of exception types to exclude from retrying
    """
    if exceptions is None:
        exceptions = (
            (requests.exceptions.HTTPError,) if rate_limit_only else (Exception,)
        )

    # Set up default conditions based on rate_limit_only
    if retryable_conditions is None and rate_limit_only:

        def _default_rate_limit_condition(e):
            return is_transient_error(e, rate_limit_only=True)

        retryable_conditions = _default_rate_limit_condition

    # Set up default warning message for rate limits
    if warning_message_func is None and rate_limit_only:

        def _default_rate_limit_warning(
            e: Exception, attempt: int, max_retries: int, delay: float
        ) -> str:
            return f"Rate limit hit, retrying in {delay:.1f} seconds (attempt {attempt + 1}/{max_retries})"

        warning_message_func = _default_rate_limit_warning

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    # Check if the exception should be excluded
                    if excluded_exceptions and isinstance(exc, excluded_exceptions):
                        raise
                    last_exception = exc

                    # Check if we should retry this error
                    should_retry = True
                    if retryable_conditions:
                        should_retry = retryable_conditions(exc)

                    if not should_retry:
                        raise

                    if attempt == max_retries:
                        # No more retries left
                        raise

                    # Calculate next delay with exponential backoff and jitter
                    base_delay = min(delay, max_delay)
                    # Add jitter: ±20% of base delay
                    delay = round(random.uniform(0.8 * base_delay, 1.2 * base_delay), 2)

                    # Generate warning message
                    if warning_message_func:
                        warning_msg = warning_message_func(
                            exc, attempt, max_retries, delay
                        )
                    else:
                        warning_msg = (
                            f"{type(exc).__name__} occurred, retrying in {delay:.1f} seconds "
                            f"(attempt {attempt + 1}/{max_retries}): {str(exc)}"
                        )

                    warnings.warn(warning_msg, UserWarning, stacklevel=2)

                    time.sleep(delay)
                    delay *= backoff_factor
                    continue

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator

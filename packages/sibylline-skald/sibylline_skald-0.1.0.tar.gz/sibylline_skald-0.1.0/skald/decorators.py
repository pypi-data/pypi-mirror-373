"""Decorators and context managers for Skald opt-out functionality."""

from __future__ import annotations

import functools
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Generator, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

# Context variable to track opt-out state
_opt_out_context: ContextVar[Optional[str]] = ContextVar("skald_opt_out", default=None)

# Global registry of opted-out functions
_opted_out_functions: dict[Callable[..., Any], str] = {}


def opt_out(reason: str) -> Callable[[F], F]:
    """Decorator to mark a function as opted out of Skald collection.
    
    Args:
        reason: Reason for opting out (e.g., "contains sensitive data")
        
    Returns:
        Decorated function that skips Skald data collection
        
    Example:
        @skald.opt_out(reason="contains sensitive data")
        def run_sensitive_query(sql: str) -> dict:
            ...
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Set context variable for the duration of this call
            token = _opt_out_context.set(reason)
            try:
                return func(*args, **kwargs)
            finally:
                _opt_out_context.reset(token)
        
        # Register the wrapper in the opted-out functions
        _opted_out_functions[wrapper] = reason
        # Also register the original function for cases where someone checks the unwrapped function
        _opted_out_functions[func] = reason
        
        return wrapper  # type: ignore
    
    return decorator


@contextmanager
def suppressed(reason: str) -> Generator[None, None, None]:
    """Context manager to suppress Skald data collection.
    
    Args:
        reason: Reason for suppression (e.g., "benchmark", "testing")
        
    Example:
        with skald.suppressed(reason="benchmark"):
            do_many_tool_calls()
    """
    token = _opt_out_context.set(reason)
    try:
        yield
    finally:
        _opt_out_context.reset(token)


def is_opted_out() -> tuple[bool, Optional[str]]:
    """Check if current context is opted out of Skald collection.
    
    Returns:
        Tuple of (is_opted_out, reason_if_opted_out)
    """
    reason = _opt_out_context.get()
    return reason is not None, reason


def is_function_opted_out(func: Callable[..., Any]) -> tuple[bool, Optional[str]]:
    """Check if a specific function is opted out of Skald collection.
    
    Args:
        func: Function to check
        
    Returns:
        Tuple of (is_opted_out, reason_if_opted_out)
    """
    reason = _opted_out_functions.get(func)
    return reason is not None, reason


def clear_opt_outs() -> None:
    """Clear all opted-out functions. Used primarily for testing."""
    _opted_out_functions.clear()
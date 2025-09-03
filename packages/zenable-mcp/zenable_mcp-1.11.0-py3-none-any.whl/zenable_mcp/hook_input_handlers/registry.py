"""Registry for managing input handlers.

This module provides a registry system for dynamically registering and managing
input handlers that process different input formats and sources.
"""

from typing import Optional

from zenable_mcp.exceptions import HandlerConflictError
from zenable_mcp.hook_input_handlers.base import HookInputContext, InputHandler
from zenable_mcp.hook_input_handlers.claude_code import ClaudeCodeInputHandler
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona


class InputHandlerRegistry:
    """Registry for managing input handlers.

    Handlers are checked in priority order (first registered = highest priority).
    """

    def __init__(self, auto_register: bool = True):
        """Initialize the registry.

        Args:
            auto_register: If True, automatically register default handlers
        """
        self._handlers: list[InputHandler] = []
        self._context_cache: Optional[HookInputContext] = None
        self._active_handler: Optional[InputHandler] = None

        if auto_register:
            self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register all default input handlers in priority order."""
        # Register handlers in priority order
        self.register(ClaudeCodeInputHandler())

    def register(self, handler: InputHandler) -> None:
        """Register a new input handler.

        Args:
            handler: The handler to register
        """
        echo(f"Registering input handler: {handler}", persona=Persona.DEVELOPER)
        self._handlers.append(handler)

    def unregister(self, handler_type: type[InputHandler]) -> None:
        """Unregister a handler by type.

        Args:
            handler_type: The type of handler to remove
        """
        self._handlers = [h for h in self._handlers if not isinstance(h, handler_type)]

    def detect_and_parse(self) -> Optional[HookInputContext]:
        """Detect which handler can process the input and parse it.

        Returns:
            HookInputContext from the first handler that can process the input,
            or None if no handler matches

        Raises:
            RuntimeError: If multiple handlers claim they can handle the input
        """
        if self._context_cache is not None:
            return self._context_cache

        # First, detect all handlers that can handle the input
        capable_handlers = []
        for handler in self._handlers:
            echo(f"Checking handler: {handler.name}", persona=Persona.DEVELOPER)
            try:
                if handler.can_handle():
                    capable_handlers.append(handler)
                    echo(
                        f"Handler {handler.name} can handle the input",
                        persona=Persona.DEVELOPER,
                    )
            except Exception as e:
                echo(
                    f"Handler {handler.name} failed during detection: {e}",
                    persona=Persona.POWER_USER,
                    err=True,
                )
                continue

        # Check if we have multiple handlers claiming they can handle
        if len(capable_handlers) > 1:
            handler_names = [handler.name for handler in capable_handlers]
            echo(
                f"Multiple handlers conflict: {handler_names}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            raise HandlerConflictError(handler_names)

        # If we have exactly one handler, use it
        if len(capable_handlers) == 1:
            handler = capable_handlers[0]
            echo(f"Using input handler: {handler.name}", persona=Persona.POWER_USER)
            # Cache the active handler for later retrieval
            self._active_handler = handler
            try:
                self._context_cache = handler.parse_input()
                return self._context_cache
            except Exception as e:
                echo(
                    f"Handler {handler.name} failed during parsing: {e}",
                    persona=Persona.POWER_USER,
                    err=True,
                )
                return None

        echo("No input handler matched", persona=Persona.DEVELOPER)
        return None

    def get_active_handler(self) -> Optional[InputHandler]:
        """Get the handler that can process the current input.

        Returns:
            The active handler or None

        Raises:
            RuntimeError: If detect_and_parse() was not called first

        Note: This method must be called after detect_and_parse() to avoid
        redundant stdin reads.
        """
        # Require that detect_and_parse() was called first
        if self._context_cache is None:
            raise RuntimeError(
                "get_active_handler() called before detect_and_parse(). "
                "Call detect_and_parse() first to avoid duplicate stdin reads."
            )

        return self._active_handler

    def clear_cache(self) -> None:
        """Clear the cached context and active handler."""
        self._context_cache = None
        self._active_handler = None

    @property
    def handlers(self) -> list[InputHandler]:
        """Get the list of registered handlers."""
        return self._handlers.copy()

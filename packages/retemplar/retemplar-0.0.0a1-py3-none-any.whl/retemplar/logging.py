"""Clean, minimal logging for retemplar with Rich CLI output."""

import json
import logging
from typing import Any

import structlog
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from structlog.types import EventDict
from structlog.typing import FilteringBoundLogger as Logger

console = Console()


class RetemplarError(Exception):
    """Base exception for retemplar operations with structured context."""

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context = context

    def log_structured(self, logger: Logger) -> None:
        """Log structured error data for telemetry/CI."""
        logger.error(
            'retemplar_error',
            message=self.message,
            error_type=type(self).__name__,
            **self.context,
        )


def _clean_context(event_dict: EventDict) -> dict[str, Any]:
    """Clean context by removing internal keys and empty values."""
    internal_keys = {'event', 'timestamp', 'log_level', 'level', 'logger'}
    return {
        k: v
        for k, v in event_dict.items()
        if k not in internal_keys and v not in (None, '', [], {})
    }


def _cli_renderer(_: Logger, method_name: str, event_dict: EventDict) -> str:
    """Render log messages for CLI with Rich formatting."""
    level = method_name.upper()
    event = event_dict.pop('event', 'retemplar_event')
    context = _clean_context(event_dict)

    # Color mapping
    colors = {
        'DEBUG': 'dim',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'white on red',
    }
    color = colors.get(level, 'cyan')

    # Main event line
    console.print(f'[{color}]{event}[/{color}]')

    # Show context if non-empty
    if context:
        context_yaml = yaml.safe_dump(
            context,
            default_flow_style=False,
            sort_keys=True,
        ).rstrip()
        syntax = Syntax(
            context_yaml,
            'yaml',
            theme='github-dark',
            background_color='default',
        )
        console.print(Panel(syntax, title='context', border_style='dim'))

    return ''


def _json_renderer(_: Logger, method_name: str, event_dict: EventDict) -> str:
    """Render log messages as JSON for CI/structured logging."""
    event = event_dict.pop('event', 'retemplar_event')
    context = _clean_context(event_dict)
    return json.dumps(
        {'event': event, 'level': method_name.upper(), **context},
        default=str,
    )


def setup_logging(
    *,
    verbose: bool = False,
    debug: bool = False,
    json_mode: bool = False,
) -> None:
    """Setup logging for retemplar.

    Args:
        verbose: Show INFO level logs (default: WARNING+)
        debug: Show DEBUG level logs (implies verbose)
        json_mode: Output JSON instead of Rich formatting (for CI)
    """
    # Determine log level
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Configure stdlib logging to be quiet
    logging.basicConfig(level=level, handlers=[])

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso', utc=False),
        structlog.stdlib.add_log_level,
        _json_renderer if json_mode else _cli_renderer,
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Logger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

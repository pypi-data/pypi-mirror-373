"""
Utility helpers surfaced as `agent.utils`.

These helpers rely on user-supplied RPC URLs (see `SDKConfig.connections`) for
read operations and simple client-side transaction building. For writes, they
usually delegate to `AgentSdk.sign_and_send()` to perform signing and
broadcasting via the backend.
"""

import logging
import re
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import toml

from ..types import SignAndSendRequest, SignAndSendResponse

if TYPE_CHECKING:
    from ..client import APIClient

# Type for the sign_and_send function that utils need to call
SignAndSendFunction = Callable[[SignAndSendRequest], Awaitable[SignAndSendResponse]]


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the SDK

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("circuit_agent")

    # Don't add handlers if they already exist
    if logger.handlers:
        return logger

    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def read_pyproject_config(project_root: str | None = None) -> dict[str, Any]:
    """
    Read configuration from pyproject.toml

    Args:
        project_root: Path to project root directory. If None, searches upward from current file.

    Returns:
        Dictionary containing project configuration
    """
    if project_root is None:
        # Start from the current file's directory and search upward
        current_path = Path(__file__).parent
        project_root_path = current_path.parent  # Go up from sdk/ to project root
    else:
        project_root_path = Path(project_root)

    pyproject_path = project_root_path / "pyproject.toml"

    if not pyproject_path.exists():
        # Fallback configuration
        return {
            "project": {
                "name": "circuit-agent",
                "description": "A Circuit Agent",
                "version": "1.0.0",
            },
            "tool": {
                "circuit": {"name": "Circuit Agent", "description": "A Circuit Agent"}
            },
        }

    try:
        with open(pyproject_path) as f:
            config = toml.load(f)
        return config
    except Exception as e:
        logger = setup_logging()
        logger.warning(f"Failed to read pyproject.toml: {e}. Using fallback config.")
        return {
            "project": {
                "name": "circuit-agent",
                "description": "A Circuit Agent",
                "version": "1.0.0",
            },
            "tool": {
                "circuit": {"name": "Circuit Agent", "description": "A Circuit Agent"}
            },
        }


def get_agent_config_from_pyproject(
    project_root: str | None = None,
) -> dict[str, str]:
    """
    Extract agent configuration (title, description, version) from pyproject.toml

    Args:
        project_root: Path to project root directory. If None, searches upward from current file.

    Returns:
        Dictionary containing agent configuration
    """
    config = read_pyproject_config(project_root)

    # Extract project info
    project_info = config.get("project", {})
    tool_info = config.get("tool", {}).get("circuit", {})

    return {
        "title": tool_info.get("name", project_info.get("name", "Circuit Agent")),
        "description": tool_info.get(
            "description", project_info.get("description", "A Circuit Agent")
        ),
        "version": project_info.get("version", "1.0.0"),
    }

"""Cadence SDK - Plugin Development Framework for Cadence AI.

This package provides the core SDK for building custom AI agent plugins
for the Cadence multi-agent AI framework. It includes base classes,
utilities, and tools for creating extensible agent systems.

Key Components:
    - Agent: Base class for custom AI agents
    - Tool: Base class for agent tools
    - Plugin: Plugin management and discovery
    - Registry: Plugin registration system

Example:
    >>> from cadence_sdk.base.agent import Agent
    >>> from cadence_sdk.base.tool import Tool
    >>>
    >>> class MyAgent(Agent):
    ...     name = "my_agent"
    ...     description = "A custom agent"
    ...
    ...     def process(self, message: str) -> str:
    ...         return f"Processed: {message}"
"""

from cadence_sdk.base.agent import Agent
from cadence_sdk.base.plugin import Plugin
from cadence_sdk.base.tool import Tool
from cadence_sdk.registry.plugin_registry import PluginRegistry
from cadence_sdk.tools.decorators import tool
from cadence_sdk.utils.directory_discovery import discover_plugins
from cadence_sdk.utils.environment_discovery import get_environment_plugins

__version__ = "1.0.0"
__all__ = ["Agent", "Plugin", "Tool", "PluginRegistry", "tool", "discover_plugins", "get_environment_plugins"]

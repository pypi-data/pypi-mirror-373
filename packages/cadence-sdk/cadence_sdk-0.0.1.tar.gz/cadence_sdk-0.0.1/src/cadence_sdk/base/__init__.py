"""Base interfaces and types for Cadence plugins."""

from .agent import BasePluginAgent
from .metadata import ModelConfig, PluginMetadata
from .plugin import BasePlugin

__all__ = ["BasePluginAgent", "PluginMetadata", "ModelConfig", "BasePlugin"]

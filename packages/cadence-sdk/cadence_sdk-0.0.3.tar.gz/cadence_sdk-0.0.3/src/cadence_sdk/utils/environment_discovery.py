"""Environment-installed plugin discovery utilities.

Discovers Cadence SDK plugins that are available in the active Python environment
(e.g., site-packages from pip/poetry/pipx/conda, etc.) and imports their
top-level modules to trigger SDK registration.
"""

import importlib.metadata
import importlib.util
from typing import List, Set

from ..base.loggable import Loggable
from ..registry.plugin_registry import discover_plugins, get_plugin_registry


class PluginDiscoveryManager(Loggable):
    """Import Cadence plugins installed in the current environment."""

    def __init__(self):
        super().__init__()
        self._imported_packages: Set[str] = set()

    def reset(self):
        """Reset discovery state."""
        self._imported_packages.clear()

    def import_plugins_from_environment(self, force_reimport: bool = False) -> int:
        """Import all installed Cadence plugins from the environment."""
        self.logger.info("Starting environment plugin discovery...")

        imported_count = 0
        for distribution in importlib.metadata.distributions():
            if not self._is_cadence_plugin(distribution):
                continue

            package_name = distribution.metadata["Name"]
            module_name = package_name.replace("-", "_")

            if not force_reimport and module_name in self._imported_packages:
                continue

            if self._try_import_plugin_module(module_name, package_name):
                imported_count += 1

        self.logger.info(f"Imported {imported_count} plugin packages")
        return imported_count

    def _is_cadence_plugin(self, distribution: importlib.metadata.Distribution) -> bool:
        """Check if a distribution is an Cadence plugin."""
        try:
            project_name = distribution.metadata["Name"].lower()
        except (KeyError, AttributeError):
            return False

        if not self._has_cadence_plugin_naming(project_name):
            return False

        if self._is_sdk_package(project_name):
            return False

        return self._depends_on_cadence_sdk(distribution)

    @staticmethod
    def _has_cadence_plugin_naming(project_name: str) -> bool:
        """Return True if project name follows Cadence plugin naming."""
        return "cadence" in project_name and "plugin" in project_name

    @staticmethod
    def _is_sdk_package(project_name: str) -> bool:
        """Return True if project is the SDK itself."""
        return project_name in ("cadence_sdk", "cadence_sdk")

    @staticmethod
    def _depends_on_cadence_sdk(distribution: importlib.metadata.Distribution) -> bool:
        """Return True if distribution depends on cadence_sdk."""
        try:
            requires = distribution.metadata.get_all("Requires-Dist")
            if not requires:
                return False

            requirements = [req.split(";")[0].strip().lower() for req in requires]
            return any("cadence_sdk" in req for req in requirements)
        except Exception:
            return False

    def _try_import_plugin_module(self, module_name: str, package_name: str) -> bool:
        """Import a plugin module if available."""
        if not self._module_exists(module_name):
            self.logger.warning(f"Plugin package {package_name} not found as module {module_name}")
            return False

        try:
            __import__(module_name)
            self._imported_packages.add(module_name)
            return True
        except ImportError as e:
            self.logger.warning(f"Failed to import plugin {package_name}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error importing {package_name}: {e}")

        return False

    @staticmethod
    def _module_exists(module_name: str) -> bool:
        """Return True if module exists without importing it."""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False

    def get_installed_environment_packages(self) -> List[str]:
        """Return installed Cadence plugin package names from environment."""
        return [dist.metadata["Name"] for dist in importlib.metadata.distributions() if self._is_cadence_plugin(dist)]

    def get_imported_environment_packages(self) -> List[str]:
        """Return imported Cadence plugin package module names from environment."""
        return sorted(self._imported_packages)

    def get_registry_summary(self) -> dict:
        """Return summary statistics about the plugin registry."""
        registry = get_plugin_registry()
        plugins = discover_plugins()

        capabilities = self._extract_capabilities(plugins)
        agent_types = self._extract_agent_types(plugins)

        return {
            "total_plugins": len(registry),
            "plugin_names": registry.list_plugin_names(),
            "unique_capabilities": sorted(capabilities),
            "agent_types": sorted(agent_types),
            "installed_packages": self.get_installed_plugin_packages(),
            "imported_packages": sorted(self._imported_packages),
        }

    @staticmethod
    def _extract_capabilities(plugins) -> set:
        capabilities = set()
        for plugin in plugins:
            metadata = plugin.get_metadata()
            capabilities.update(metadata.capabilities)
        return capabilities

    @staticmethod
    def _extract_agent_types(plugins) -> set:
        return {plugin.get_metadata().agent_type for plugin in plugins}


_env_discovery = PluginDiscoveryManager()


def import_plugins_from_environment(force_reimport: bool = False) -> int:
    """Import all installed Cadence plugins from the environment."""
    return _env_discovery.import_plugins_from_environment(force_reimport)


def reset_environment_discovery():
    """Reset environment discovery state."""
    _env_discovery.reset()


def get_environment_discovery_summary() -> dict:
    """Return discovery and registry summary."""
    return _env_discovery.get_registry_summary()


def list_installed_environment_packages() -> List[str]:
    """Return installed Cadence plugin package names from environment."""
    return _env_discovery.get_installed_environment_packages()


def list_imported_environment_packages() -> List[str]:
    """Return imported Cadence plugin package module names from environment."""
    return _env_discovery.get_imported_environment_packages()

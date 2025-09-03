"""Simple plugin registry used by tests.

Allows registering, retrieving, and validating plugins by stage name.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..msa.stage_manager import MSAStageInput
from .base_plugin import BaseMSAPlugin


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, BaseMSAPlugin] = {}

    def register_plugin(self, stage_name: str, plugin: BaseMSAPlugin) -> bool:
        """Register or replace a plugin for a stage."""
        self._plugins[stage_name] = plugin
        return True

    def unregister_plugin(self, stage_name: str) -> bool:
        """Unregister a plugin by stage name."""
        if stage_name in self._plugins:
            del self._plugins[stage_name]
            return True
        return False

    def get_plugin(self, stage_name: str) -> Optional[BaseMSAPlugin]:
        return self._plugins.get(stage_name)

    def is_plugin_registered(self, stage_name: str) -> bool:
        return stage_name in self._plugins

    def get_registered_plugins(self) -> Dict[str, BaseMSAPlugin]:
        return dict(self._plugins)

    def get_all_capabilities(self) -> Dict[str, List[str]]:
        caps: Dict[str, List[str]] = {}
        for stage, plugin in self._plugins.items():
            try:
                caps[stage] = plugin.get_capabilities()
            except Exception:
                caps[stage] = []
        return caps

    def validate_input_for_all_plugins(
        self, stage_input: MSAStageInput
    ) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for stage, plugin in self._plugins.items():
            try:
                results[stage] = bool(plugin.validate_input(stage_input))
            except Exception:
                results[stage] = False
        return results

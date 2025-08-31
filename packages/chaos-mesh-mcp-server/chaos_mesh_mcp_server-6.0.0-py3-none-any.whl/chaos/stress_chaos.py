"""Stress Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class StressChaosTemplate:
    """Stress Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build Stress Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "StressChaos",
            "metadata": {
                "name": f"stresschaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "stress-chaos",
                },
            },
            "spec": {
                "mode": config.get("mode", "one"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "selector": self._build_selector(config.get("selector", {})),
                "stressors": self._build_stressors(config.get("stressors", {})),
            },
        }

        # Container name specification
        if "containerNames" in config:
            spec["spec"]["containerNames"] = config["containerNames"]

        return spec

    def _build_selector(self, selector_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build stress selector"""
        selector = {}

        # Namespace selector
        if "namespaces" in selector_config:
            selector["namespaces"] = selector_config["namespaces"]

        # Label selector
        if "labelSelectors" in selector_config:
            selector["labelSelectors"] = selector_config["labelSelectors"]

        # Field selector
        if "fieldSelectors" in selector_config:
            selector["fieldSelectors"] = selector_config["fieldSelectors"]

        # Expression selector
        if "expressionSelectors" in selector_config:
            selector["expressionSelectors"] = selector_config["expressionSelectors"]

        return selector

    def _build_stressors(self, stressors_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build stressor configuration"""
        stressors = {}

        # CPU stress
        if "cpu" in stressors_config:
            stressors["cpu"] = self._build_cpu_stressor(stressors_config["cpu"])

        # Memory stress
        if "memory" in stressors_config:
            stressors["memory"] = self._build_memory_stressor(
                stressors_config["memory"]
            )

        return stressors

    def _build_cpu_stressor(self, cpu_config: Dict[str, Any]) -> Dict[str, Any]:
        """CPU stressor configuration"""
        stressor = {
            "workers": cpu_config.get("workers", 1),
            "load": cpu_config.get("load", 100),
        }

        if "options" in cpu_config:
            stressor["options"] = cpu_config["options"]

        return stressor

    def _build_memory_stressor(self, memory_config: Dict[str, Any]) -> Dict[str, Any]:
        """Memory stressor configuration"""
        stressor = {
            "workers": memory_config.get("workers", 1),
            "size": memory_config.get("size", "256MB"),
        }

        if "options" in memory_config:
            stressor["options"] = memory_config["options"]

        return stressor

    def get_example_config(self) -> Dict[str, Any]:
        """Return example configuration"""
        return {
            "namespace": "default",
            "mode": "one",
            "duration": "60s",
            "selector": {"labelSelectors": {"app": "nginx"}},
            "stressors": {
                "cpu": {"workers": 1, "load": 100},
                "memory": {"workers": 1, "size": "256MB"},
            },
        }

    def get_supported_stressors(self) -> list:
        """Get supported stressors list"""
        return [
            "cpu",  # CPU stress
            "memory",  # Memory stress
        ]

    def get_cpu_options(self) -> list:
        """CPU stressor options"""
        return [
            "--cpu-load",  # CPU load ratio
            "--cpu-method",  # CPU stress method
            "--timeout",  # Timeout
        ]

    def get_memory_options(self) -> list:
        """Memory stressor options"""
        return [
            "--vm-bytes",  # Memory size to allocate
            "--vm-hang",  # Memory release delay
            "--vm-keep",  # Keep memory
            "--vm-populate",  # Pre-allocate memory
        ]

"""Time Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class TimeChaosTemplate:
    """Time Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build Time Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "TimeChaos",
            "metadata": {
                "name": f"timechaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "time-chaos",
                },
            },
            "spec": {
                "mode": config.get("mode", "one"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "selector": self._build_selector(config.get("selector", {})),
                "timeOffset": config.get("timeOffset", "-10m"),
            },
        }

        # Optional fields
        if "clockIds" in config:
            spec["spec"]["clockIds"] = config["clockIds"]

        if "containerNames" in config:
            spec["spec"]["containerNames"] = config["containerNames"]

        return spec

    def _build_selector(self, selector_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build Pod selector"""
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

        # Annotation selector
        if "annotationSelectors" in selector_config:
            selector["annotationSelectors"] = selector_config["annotationSelectors"]

        # Pod phase selector
        if "podPhaseSelectors" in selector_config:
            selector["podPhaseSelectors"] = selector_config["podPhaseSelectors"]

        return selector

    def get_example_config(self) -> Dict[str, Any]:
        """Return example configuration"""
        return {
            "namespace": "default",
            "mode": "one",
            "duration": "60s",
            "timeOffset": "-10m",
            "selector": {"labelSelectors": {"app": "nginx"}},
        }

    def get_supported_time_offsets(self) -> list:
        """Get supported time offset examples"""
        return [
            "-10m",  # 10 minutes ago
            "+1h",  # 1 hour ahead
            "-30s",  # 30 seconds ago
            "+2h30m",  # 2 hours 30 minutes ahead
        ]

    def get_supported_clock_ids(self) -> list:
        """Get supported clock IDs"""
        return [
            "CLOCK_REALTIME",
            "CLOCK_MONOTONIC",
            "CLOCK_PROCESS_CPUTIME_ID",
            "CLOCK_THREAD_CPUTIME_ID",
            "CLOCK_BOOTTIME",
        ]

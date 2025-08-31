"""Pod Chaos experiment template"""

from typing import Any, Dict


class PodChaosTemplate:
    """Pod Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build Pod Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "PodChaos",
            "metadata": {
                "name": experiment_id,
                "namespace": config.get("namespace", "default"),
            },
            "spec": {
                "action": config.get("action", "pod-kill"),
                "mode": config.get("mode", "one"),
                "selector": self._build_selector(config.get("selector", {})),
            },
        }

        # Set duration
        if "duration" in config:
            spec["spec"]["duration"] = config["duration"]

        # Add optional fields
        if "gracePeriod" in config:
            spec["spec"]["gracePeriod"] = config["gracePeriod"]

        if "value" in config:
            spec["spec"]["value"] = config["value"]

        # Scheduling configuration
        if "scheduler" in config:
            spec["spec"]["scheduler"] = config["scheduler"]

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
            "action": "pod-kill",
            "mode": "one",
            "duration": "60s",
            "selector": {"labelSelectors": {"app": "nginx"}},
        }

    def get_supported_actions(self) -> list:
        """Get supported actions list"""
        return ["pod-kill", "pod-failure", "container-kill"]

    def get_supported_modes(self) -> list:
        """Get supported modes list"""
        return [
            "one",  # Single Pod
            "all",  # All Pods
            "fixed",  # Fixed number
            "fixed-percent",  # Fixed percentage
            "random-max-percent",  # Random within max percentage
        ]

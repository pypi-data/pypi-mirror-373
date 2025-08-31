"""DNS Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class DNSChaosTemplate:
    """DNS Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build DNS Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "DNSChaos",
            "metadata": {
                "name": f"dnschaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "dns-chaos",
                },
            },
            "spec": {
                "action": config.get("action", "random"),
                "mode": config.get("mode", "one"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "selector": self._build_selector(config.get("selector", {})),
                "patterns": config.get("patterns", ["google.com"]),
            },
        }

        # Action-specific additional configuration
        action = config.get("action", "random")

        if action == "error":
            spec["spec"]["errno"] = config.get("errno", 3)  # NXDOMAIN

        elif action == "delay":
            spec["spec"]["delay"] = config.get("delay", "100ms")

        elif action == "random":
            # Random action doesn't need additional parameters
            pass

        # Container names
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
            "action": "random",
            "mode": "one",
            "duration": "60s",
            "patterns": ["google.com", "github.com"],
            "selector": {"labelSelectors": {"app": "nginx"}},
        }

    def get_supported_actions(self) -> list:
        """Get supported actions list"""
        return [
            "random",  # Return random IP
            "error",  # Return DNS error
            "delay",  # Add DNS query delay
        ]

    def get_common_dns_errors(self) -> Dict[int, str]:
        """Get common DNS error codes"""
        return {
            1: "FORMERR - Format error",
            2: "SERVFAIL - Server failure",
            3: "NXDOMAIN - Non-existent domain",
            4: "NOTIMP - Not implemented",
            5: "REFUSED - Query refused",
        }

    def get_example_patterns(self) -> list:
        """Get example DNS patterns"""
        return [
            "google.com",
            "*.example.com",
            "api.service.local",
            "*.amazonaws.com",
            "registry.k8s.io",
        ]

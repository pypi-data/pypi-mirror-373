"""Network Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class NetworkChaosTemplate:
    """Network Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build Network Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "NetworkChaos",
            "metadata": {
                "name": f"networkchaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "network-chaos",
                },
            },
            "spec": {
                "action": config.get("action", "delay"),
                "mode": config.get("mode", "one"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "selector": self._build_selector(config.get("selector", {})),
            },
        }

        # Add action-specific configuration
        action = config.get("action", "delay")

        if action == "delay":
            spec["spec"]["delay"] = self._build_delay_config(config.get("delay", {}))

        elif action == "loss":
            spec["spec"]["loss"] = self._build_loss_config(config.get("loss", {}))

        elif action == "duplicate":
            spec["spec"]["duplicate"] = self._build_duplicate_config(
                config.get("duplicate", {})
            )

        elif action == "corrupt":
            spec["spec"]["corrupt"] = self._build_corrupt_config(
                config.get("corrupt", {})
            )

        elif action == "partition":
            spec["spec"]["direction"] = config.get("direction", "both")
            if "target" in config:
                spec["spec"]["target"] = config["target"]

        elif action == "bandwidth":
            spec["spec"]["bandwidth"] = self._build_bandwidth_config(
                config.get("bandwidth", {})
            )

        # Direction configuration
        if "direction" in config:
            spec["spec"]["direction"] = config["direction"]

        # Target configuration
        if "target" in config:
            spec["spec"]["target"] = config["target"]

        # External targets configuration
        if "externalTargets" in config:
            spec["spec"]["externalTargets"] = config["externalTargets"]

        return spec

    def _build_selector(self, selector_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build network selector"""
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

    def _build_delay_config(self, delay_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build delay configuration"""
        config = {"latency": delay_config.get("latency", "100ms")}

        if "correlation" in delay_config:
            config["correlation"] = delay_config["correlation"]

        if "jitter" in delay_config:
            config["jitter"] = delay_config["jitter"]

        return config

    def _build_loss_config(self, loss_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build packet loss configuration"""
        config = {"loss": loss_config.get("loss", "10")}

        if "correlation" in loss_config:
            config["correlation"] = loss_config["correlation"]

        return config

    def _build_duplicate_config(
        self, duplicate_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build packet duplication configuration"""
        config = {"duplicate": duplicate_config.get("duplicate", "10")}

        if "correlation" in duplicate_config:
            config["correlation"] = duplicate_config["correlation"]

        return config

    def _build_corrupt_config(self, corrupt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build packet corruption configuration"""
        config = {"corrupt": corrupt_config.get("corrupt", "10")}

        if "correlation" in corrupt_config:
            config["correlation"] = corrupt_config["correlation"]

        return config

    def _build_bandwidth_config(
        self, bandwidth_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build bandwidth limitation configuration"""
        config = {"rate": bandwidth_config.get("rate", "1mbps")}

        if "limit" in bandwidth_config:
            config["limit"] = bandwidth_config["limit"]

        if "buffer" in bandwidth_config:
            config["buffer"] = bandwidth_config["buffer"]

        if "peak" in bandwidth_config:
            config["peak"] = bandwidth_config["peak"]

        if "minburst" in bandwidth_config:
            config["minburst"] = bandwidth_config["minburst"]

        return config

    def get_example_config(self) -> Dict[str, Any]:
        """Return example configuration"""
        return {
            "namespace": "default",
            "action": "delay",
            "mode": "one",
            "duration": "60s",
            "direction": "both",
            "delay": {"latency": "100ms", "correlation": "0", "jitter": "10ms"},
            "selector": {"labelSelectors": {"app": "nginx"}},
        }

    def get_supported_actions(self) -> list:
        """Get supported actions list"""
        return [
            "netem",  # Network emulation
            "delay",  # Delay
            "loss",  # Packet loss
            "duplicate",  # Packet duplication
            "corrupt",  # Packet corruption
            "partition",  # Network partition
            "bandwidth",  # Bandwidth limitation
        ]

    def get_supported_directions(self) -> list:
        """Get supported directions list"""
        return [
            "to",  # Outbound
            "from",  # Inbound
            "both",  # Bidirectional
        ]

"""IO Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class IOChaosTemplate:
    """IO Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build IO Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "IOChaos",
            "metadata": {
                "name": f"iochaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "io-chaos",
                },
            },
            "spec": {
                "action": config.get("action", "latency"),
                "mode": config.get("mode", "one"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "selector": self._build_selector(config.get("selector", {})),
                "volumePath": config.get("volumePath", "/tmp"),
                "percent": config.get("percent", 50),
            },
        }

        # Action-specific additional configuration
        if config.get("action") == "latency":
            spec["spec"]["delay"] = config.get("delay", "100ms")

        if config.get("action") == "fault":
            spec["spec"]["errno"] = config.get("errno", 5)

        if config.get("action") == "attrOverride":
            if "attr" in config:
                spec["spec"]["attr"] = config["attr"]

        if config.get("action") == "mistake":
            if "mistake" in config:
                spec["spec"]["mistake"] = config["mistake"]

        # Container names
        if "containerNames" in config:
            spec["spec"]["containerNames"] = config["containerNames"]

        # Methods filter
        if "methods" in config:
            spec["spec"]["methods"] = config["methods"]

        # Path filter
        if "path" in config:
            spec["spec"]["path"] = config["path"]

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
            "action": "latency",
            "mode": "one",
            "duration": "60s",
            "volumePath": "/tmp",
            "delay": "100ms",
            "percent": 50,
            "selector": {"labelSelectors": {"app": "nginx"}},
        }

    def get_supported_actions(self) -> list:
        """Get supported actions list"""
        return [
            "latency",  # Add I/O latency
            "fault",  # Inject I/O fault
            "attrOverride",  # Override file attributes
            "mistake",  # Inject random mistakes
        ]

    def get_supported_methods(self) -> list:
        """Get supported I/O methods"""
        return [
            "lookup",
            "forget",
            "getattr",
            "setattr",
            "readlink",
            "mknod",
            "mkdir",
            "unlink",
            "rmdir",
            "symlink",
            "rename",
            "link",
            "open",
            "read",
            "write",
            "flush",
            "release",
            "fsync",
        ]

    def get_common_errno_codes(self) -> Dict[int, str]:
        """Get common errno codes"""
        return {
            5: "EIO - I/O error",
            13: "EACCES - Permission denied",
            28: "ENOSPC - No space left on device",
            30: "EROFS - Read-only file system",
            122: "EDQUOT - Disk quota exceeded",
        }

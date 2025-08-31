"""Chaos experiment validator"""

from typing import Any, Dict, List, Optional

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ExperimentValidator:
    """Chaos experiment validator"""

    def __init__(self):
        self.required_fields = {
            "pod_chaos": ["namespace", "selector", "action"],
            "network_chaos": ["namespace", "selector", "action"],
            "stress_chaos": ["namespace", "selector", "stressors"],
            "time_chaos": ["namespace", "selector", "timeOffset"],
            "io_chaos": ["namespace", "selector", "action"],
            "dns_chaos": ["namespace", "selector", "action"],
            # "aws_chaos": ["namespace", "action", "ec2Instance"],
            "kernel_chaos": ["namespace", "selector", "failKernRequest"],
        }

        self.valid_actions = {
            "pod_chaos": ["pod-kill", "pod-failure", "container-kill"],
            "network_chaos": [
                "netem",
                "delay",
                "loss",
                "duplicate",
                "corrupt",
                "partition",
                "bandwidth",
            ],
            "io_chaos": ["latency", "fault", "attrOverride", "mistake"],
            "dns_chaos": ["random", "error", "delay"],
            # "aws_chaos": ["ec2-stop", "ec2-restart", "detach-volume", "attach-volume"],
        }

    async def validate_experiment(
        self, experiment_type: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate experiment configuration"""
        errors = []
        warnings = []

        try:
            logger.info(
                "starting_experiment_validation",
                experiment_type=experiment_type,
                config=config,
            )

            # Basic field validation
            basic_validation = self._validate_basic_fields(experiment_type, config)
            errors.extend(basic_validation["errors"])
            warnings.extend(basic_validation["warnings"])
            logger.info(
                "basic_validation_complete",
                errors=basic_validation["errors"],
                warnings=basic_validation["warnings"],
            )

            # Security validation
            security_validation = self._validate_security(config)
            errors.extend(security_validation["errors"])
            warnings.extend(security_validation["warnings"])
            logger.info(
                "security_validation_complete",
                errors=security_validation["errors"],
                warnings=security_validation["warnings"],
            )

            # Experiment type-specific validation
            type_validation = await self._validate_experiment_type(
                experiment_type, config
            )
            errors.extend(type_validation["errors"])
            warnings.extend(type_validation["warnings"])
            logger.info(
                "type_validation_complete",
                errors=type_validation["errors"],
                warnings=type_validation["warnings"],
            )

            # Resource selector validation
            selector_validation = self._validate_selector(config.get("selector", {}))
            errors.extend(selector_validation["errors"])
            warnings.extend(selector_validation["warnings"])
            logger.info(
                "selector_validation_complete",
                errors=selector_validation["errors"],
                warnings=selector_validation["warnings"],
            )

            # Duration validation
            duration_validation = self._validate_duration(config.get("duration"))
            errors.extend(duration_validation["errors"])
            warnings.extend(duration_validation["warnings"])
            logger.info(
                "duration_validation_complete",
                errors=duration_validation["errors"],
                warnings=duration_validation["warnings"],
            )

            logger.info(
                "experiment_validation_complete",
                experiment_type=experiment_type,
                total_errors=len(errors),
                total_warnings=len(warnings),
                all_errors=errors,
                all_warnings=warnings,
            )

            return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

        except Exception as e:
            logger.error(
                "experiment_validation_failed",
                experiment_type=experiment_type,
                error=str(e),
            )
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
            }

    def _validate_basic_fields(
        self, experiment_type: str, config: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Validate basic fields"""
        errors = []
        warnings = []

        # Check experiment type
        if experiment_type not in self.required_fields:
            errors.append(f"Unsupported experiment type: {experiment_type}")
            return {"errors": errors, "warnings": warnings}

        # Check required fields
        required = self.required_fields[experiment_type]
        for field in required:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Check namespace
        namespace = config.get("namespace")
        if not namespace:
            errors.append("Namespace is required")
        elif namespace in settings.security.protected_namespaces:
            errors.append(f"Cannot target protected namespace: {namespace}")

        return {"errors": errors, "warnings": warnings}

    def _validate_security(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Security validation"""
        errors = []
        warnings = []

        # Duration limit
        duration = config.get("duration", settings.chaos.default_duration)
        duration_seconds = self._parse_duration(duration)

        if duration_seconds > settings.security.max_experiment_duration:
            errors.append(
                f"Duration {duration} exceeds maximum allowed duration "
                f"({settings.security.max_experiment_duration}s)"
            )

        # Selector scope check
        selector = config.get("selector", {})
        if not selector:
            warnings.append("No selector specified - experiment may affect all pods")

        # Label selector check
        label_selectors = selector.get("labelSelectors", {})
        if not label_selectors:
            warnings.append("No label selectors - experiment scope may be too broad")

        return {"errors": errors, "warnings": warnings}

    async def _validate_experiment_type(
        self, experiment_type: str, config: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Experiment type-specific validation"""
        errors = []
        warnings = []

        if experiment_type == "pod_chaos":
            errors.extend(self._validate_pod_chaos(config))
        elif experiment_type == "network_chaos":
            errors.extend(self._validate_network_chaos(config))
        elif experiment_type == "stress_chaos":
            errors.extend(self._validate_stress_chaos(config))
        elif experiment_type == "time_chaos":
            errors.extend(self._validate_time_chaos(config))
        elif experiment_type == "io_chaos":
            errors.extend(self._validate_io_chaos(config))
        elif experiment_type == "dns_chaos":
            errors.extend(self._validate_dns_chaos(config))
        # elif experiment_type == "aws_chaos":
        # errors.extend(self._validate_aws_chaos(config))
        elif experiment_type == "kernel_chaos":
            errors.extend(self._validate_kernel_chaos(config))

        return {"errors": errors, "warnings": warnings}

    def _validate_pod_chaos(self, config: Dict[str, Any]) -> List[str]:
        """Pod Chaos validation"""
        errors = []

        action = config.get("action")
        if action not in self.valid_actions["pod_chaos"]:
            # Provide helpful suggestions for common mistakes
            suggestion = self._get_action_suggestion(action)
            if suggestion:
                errors.append(f"Invalid pod chaos action: {action}. {suggestion}")
            else:
                errors.append(
                    f"Invalid pod chaos action: {action}. Valid actions are: {', '.join(self.valid_actions['pod_chaos'])}"
                )

        # gracePeriod validation
        grace_period = config.get("gracePeriod", 0)
        if not isinstance(grace_period, int) or grace_period < 0:
            errors.append("gracePeriod must be a non-negative integer")

        return errors

    def _validate_network_chaos(self, config: Dict[str, Any]) -> List[str]:
        """Network Chaos validation"""
        errors = []

        action = config.get("action")
        if action not in self.valid_actions["network_chaos"]:
            errors.append(f"Invalid network chaos action: {action}")

        # Action-specific parameter validation
        if action == "delay":
            if "delay" not in config:
                errors.append("delay parameter required for delay action")
            else:
                delay_config = config["delay"]
                if "latency" not in delay_config:
                    errors.append("latency required in delay configuration")

        elif action == "loss":
            if "loss" not in config:
                errors.append("loss parameter required for loss action")
            else:
                loss_config = config["loss"]
                if "loss" not in loss_config:
                    errors.append("loss percentage required in loss configuration")

        return errors

    def _validate_stress_chaos(self, config: Dict[str, Any]) -> List[str]:
        """Stress Chaos validation"""
        errors = []

        stressors = config.get("stressors", {})
        if not stressors:
            errors.append("At least one stressor must be specified")

        # CPU stress validation
        if "cpu" in stressors:
            cpu_config = stressors["cpu"]
            if "workers" in cpu_config:
                workers = cpu_config["workers"]
                if not isinstance(workers, int) or workers <= 0:
                    errors.append("CPU workers must be a positive integer")

        # Memory stress validation
        if "memory" in stressors:
            memory_config = stressors["memory"]
            if "size" in memory_config:
                size = memory_config["size"]
                if not isinstance(size, str) or not size.endswith(("B", "K", "M", "G")):
                    errors.append(
                        "Memory size must be specified with unit (B, K, M, G)"
                    )

        return errors

    def _validate_time_chaos(self, config: Dict[str, Any]) -> List[str]:
        """Time Chaos validation"""
        errors = []

        time_offset = config.get("timeOffset")
        if not time_offset:
            errors.append("timeOffset is required for time chaos")
        elif not isinstance(time_offset, str):
            errors.append("timeOffset must be a string (e.g., '1h', '30m', '10s')")

        return errors

    def _validate_io_chaos(self, config: Dict[str, Any]) -> List[str]:
        """IO Chaos validation"""
        errors = []

        action = config.get("action")
        if action not in self.valid_actions["io_chaos"]:
            errors.append(f"Invalid IO chaos action: {action}")

        # Volume path check
        volume_path = config.get("volumePath")
        if not volume_path:
            errors.append("volumePath is required for IO chaos")

        return errors

    def _validate_dns_chaos(self, config: Dict[str, Any]) -> List[str]:
        """DNS Chaos validation"""
        errors = []

        action = config.get("action")
        if action not in self.valid_actions["dns_chaos"]:
            errors.append(f"Invalid DNS chaos action: {action}")

        # patterns validation
        patterns = config.get("patterns", [])
        if not patterns:
            errors.append("At least one DNS pattern must be specified")
        elif not isinstance(patterns, list):
            errors.append("DNS patterns must be a list")

        return errors

    # def _validate_aws_chaos(self, config: Dict[str, Any]) -> List[str]:
    #     """AWS Chaos validation"""
    #     errors = []

    #     action = config.get("action")
    #     if action not in self.valid_actions["aws_chaos"]:
    #         errors.append(f"Invalid AWS chaos action: {action}")

    #     # EC2 instance ID validation
    #     ec2_instance = config.get("ec2Instance")
    #     if not ec2_instance:
    #         errors.append("ec2Instance is required for AWS chaos")
    #     elif not isinstance(ec2_instance, str) or not ec2_instance.startswith("i-"):
    #         errors.append(
    #             "ec2Instance must be a valid EC2 instance ID (starts with 'i-')"
    #         )

    #     # Volume-related action validation
    #     if action in ["detach-volume", "attach-volume"]:
    #         volume_id = config.get("volumeID")
    #         if not volume_id:
    #             errors.append(f"volumeID is required for {action} action")
    #         elif not isinstance(volume_id, str) or not volume_id.startswith("vol-"):
    #             errors.append(
    #                 "volumeID must be a valid EBS volume ID (starts with 'vol-')"
    #             )

    #     return errors

    def _validate_kernel_chaos(self, config: Dict[str, Any]) -> List[str]:
        """Kernel Chaos validation"""
        errors = []

        fail_kern_request = config.get("failKernRequest", {})
        if not fail_kern_request:
            errors.append("failKernRequest configuration is required")

        # Check required fields
        required_fields = ["callchain", "failtype"]
        for field in required_fields:
            if field not in fail_kern_request:
                errors.append(f"failKernRequest.{field} is required")

        return errors

    def _validate_selector(self, selector: Dict[str, Any]) -> Dict[str, List[str]]:
        """Resource selector validation"""
        errors = []
        warnings = []

        # Namespace selector
        namespaces = selector.get("namespaces")
        if namespaces:
            for ns in namespaces:
                if ns in settings.security.protected_namespaces:
                    errors.append(f"Cannot target protected namespace: {ns}")

        # Label selector
        label_selectors = selector.get("labelSelectors", {})
        if not label_selectors:
            warnings.append("No label selectors specified - may affect unintended pods")

        # Field selector
        field_selectors = selector.get("fieldSelectors", {})
        if field_selectors:
            # Field selector syntax validation (simple validation)
            for key, value in field_selectors.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"Invalid field selector: {key}={value}")

        return {"errors": errors, "warnings": warnings}

    def _validate_duration(self, duration: Optional[str]) -> Dict[str, List[str]]:
        """Duration validation"""
        errors = []
        warnings = []

        if not duration:
            warnings.append(
                f"No duration specified, using default: {settings.chaos.default_duration}"
            )
            return {"errors": errors, "warnings": warnings}

        try:
            duration_seconds = self._parse_duration(duration)

            if duration_seconds <= 0:
                errors.append("Duration must be positive")
            elif duration_seconds < 10:
                warnings.append("Very short duration may not be effective")
            elif duration_seconds > 3600:  # 1 hour
                warnings.append(
                    "Long duration experiments should be monitored carefully"
                )

        except ValueError:
            errors.append(f"Invalid duration format: {duration}")

        return {"errors": errors, "warnings": warnings}

    def _get_action_suggestion(self, action: str) -> str:
        """Get suggestion for invalid action"""
        # Common action mapping suggestions
        action_suggestions = {
            "pod-network": "For network-related experiments, use 'network_chaos' experiment type with actions like 'delay', 'loss', 'partition'",
            "network": "For network-related experiments, use 'network_chaos' experiment type with actions like 'delay', 'loss', 'partition'",
            "network-delay": "For network delay, use 'network_chaos' experiment type with action 'delay'",
            "network-loss": "For network packet loss, use 'network_chaos' experiment type with action 'loss'",
            "network-partition": "For network partition, use 'network_chaos' experiment type with action 'partition'",
            "cpu": "For CPU stress, use 'stress_chaos' experiment type with 'stressors.cpu' configuration",
            "memory": "For memory stress, use 'stress_chaos' experiment type with 'stressors.memory' configuration",
            "disk": "For disk I/O issues, use 'io_chaos' experiment type with actions like 'latency', 'fault'",
            "time": "For time manipulation, use 'time_chaos' experiment type with 'timeOffset' configuration",
            "dns": "For DNS issues, use 'dns_chaos' experiment type with actions like 'random', 'error', 'delay'",
        }

        return action_suggestions.get(action, "")

    def _parse_duration(self, duration: str) -> int:
        """Parse duration"""
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        else:
            return int(duration)  # Default to seconds

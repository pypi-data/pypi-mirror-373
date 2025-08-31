"""AWS Chaos experiment template"""

from typing import Any, Dict

from utils.config import settings


class AWSChaosTemplate:
    """AWS Chaos experiment template"""

    def build_spec(self, config: Dict[str, Any], experiment_id: str) -> Dict[str, Any]:
        """Build AWS Chaos resource spec"""

        spec = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "AWSChaos",
            "metadata": {
                "name": f"awschaos-{experiment_id}",
                "namespace": config.get("namespace", "default"),
                "labels": {
                    "chaos-mesh-mcp": "true",
                    "experiment-id": experiment_id,
                    "experiment-type": "aws-chaos",
                },
            },
            "spec": {
                "action": config.get("action", "ec2-stop"),
                "duration": config.get("duration", settings.chaos.default_duration),
                "awsRegion": config.get("awsRegion", "us-west-2"),
                "secretName": config.get("secretName", "aws-secret"),
            },
        }

        # Action-specific additional configuration
        action = config.get("action")

        if action in ["ec2-stop", "ec2-restart"]:
            spec["spec"]["ec2Instance"] = config.get("ec2Instance", "")

        elif action in ["detach-volume", "attach-volume"]:
            spec["spec"]["ec2Instance"] = config.get("ec2Instance", "")
            spec["spec"]["volumeID"] = config.get("volumeID", "")
            if action == "attach-volume":
                spec["spec"]["deviceName"] = config.get("deviceName", "/dev/xvdf")

        elif action == "stop-rds":
            spec["spec"]["rdsInstance"] = config.get("rdsInstance", "")

        elif action == "reboot-rds":
            spec["spec"]["rdsInstance"] = config.get("rdsInstance", "")
            spec["spec"]["forceFailover"] = config.get("forceFailover", False)

        return spec

    def get_example_config(self) -> Dict[str, Any]:
        """Return example configuration"""
        return {
            "namespace": "default",
            "action": "ec2-stop",
            "duration": "60s",
            "awsRegion": "us-west-2",
            "ec2Instance": "i-1234567890abcdef0",
            "secretName": "aws-secret",
        }

    def get_supported_actions(self) -> list:
        """Get supported actions list"""
        return [
            "ec2-stop",  # Stop EC2 instance
            "ec2-restart",  # Restart EC2 instance
            "detach-volume",  # Detach EBS volume
            "attach-volume",  # Attach EBS volume
            "stop-rds",  # Stop RDS instance
            "reboot-rds",  # Reboot RDS instance
        ]

    def get_required_fields_by_action(self) -> Dict[str, list]:
        """Get required fields by action"""
        return {
            "ec2-stop": ["ec2Instance"],
            "ec2-restart": ["ec2Instance"],
            "detach-volume": ["ec2Instance", "volumeID"],
            "attach-volume": ["ec2Instance", "volumeID", "deviceName"],
            "stop-rds": ["rdsInstance"],
            "reboot-rds": ["rdsInstance"],
        }

    def get_aws_regions(self) -> list:
        """Get common AWS regions"""
        return [
            "us-east-1",  # N. Virginia
            "us-east-2",  # Ohio
            "us-west-1",  # N. California
            "us-west-2",  # Oregon
            "eu-west-1",  # Ireland
            "eu-central-1",  # Frankfurt
            "ap-southeast-1",  # Singapore
            "ap-northeast-1",  # Tokyo
            "ap-south-1",  # Mumbai
        ]

    def get_example_secret_manifest(self) -> Dict[str, Any]:
        """Get example AWS secret manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "aws-secret",
                "namespace": "default",
            },
            "type": "Opaque",
            "data": {
                # Base64 encoded values
                "aws_access_key_id": "<base64-encoded-access-key>",
                "aws_secret_access_key": "<base64-encoded-secret-key>",
            },
        }

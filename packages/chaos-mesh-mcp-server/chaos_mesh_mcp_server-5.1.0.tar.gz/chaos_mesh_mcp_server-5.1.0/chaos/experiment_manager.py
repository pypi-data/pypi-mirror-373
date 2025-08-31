"""Chaos experiment manager"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from kubernetes import client as k8s_client

from chaos.templates import get_template
from chaos.validator import ExperimentValidator
from k8s.cluster_manager import cluster_manager
from utils.config import settings
from utils.logger import audit_logger, get_logger

logger = get_logger(__name__)


class ExperimentManager:
    """Chaos experiment manager"""

    def __init__(self):
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        self.experiment_history: List[Dict[str, Any]] = []
        self.validator = ExperimentValidator()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize experiment manager"""
        logger.info("initializing_experiment_manager")

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("experiment_manager_initialized")

    async def create_experiment(
        self,
        cluster_name: str,
        experiment_type: str,
        experiment_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create chaos experiment"""
        try:
            # Validate experiment configuration
            validation_result = await self.validator.validate_experiment(
                experiment_type, experiment_config
            )

            if not validation_result["valid"]:
                logger.error(
                    "experiment_validation_failed",
                    experiment_type=experiment_type,
                    config=experiment_config,
                    errors=validation_result["errors"],
                    warnings=validation_result.get("warnings", []),
                )
                return {
                    "success": False,
                    "error": f"Experiment validation failed: {'; '.join(validation_result['errors'])}",
                    "validation_errors": validation_result["errors"],
                    "validation_warnings": validation_result.get("warnings", []),
                }

            # Check concurrent experiment limit
            active_count = len(
                [
                    exp
                    for exp in self.active_experiments.values()
                    if exp["cluster"] == cluster_name and exp["status"] == "running"
                ]
            )

            if active_count >= settings.security.max_concurrent_experiments:
                return {
                    "success": False,
                    "error": f"Maximum concurrent experiments ({settings.security.max_concurrent_experiments}) reached",
                }

            # Generate experiment ID (Kubernetes naming rules: lowercase, under 63 chars, remove underscores)
            import hashlib

            cluster_hash = hashlib.md5(cluster_name.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            # Change underscores to hyphens
            clean_experiment_type = experiment_type.replace("_", "-")
            experiment_id = f"{clean_experiment_type}-{cluster_hash}-{timestamp}"

            # Create Chaos Mesh resource
            chaos_resource = await self._create_chaos_resource(
                cluster_name, experiment_type, experiment_config, experiment_id
            )

            if not chaos_resource:
                return {"success": False, "error": "Failed to create chaos resource"}

            # Save experiment information
            namespace = experiment_config.get("namespace", "default")
            experiment_info = {
                "id": experiment_id,
                "cluster": cluster_name,
                "namespace": namespace,
                "type": experiment_type,
                "config": experiment_config,
                "status": "created",
                "created_at": datetime.utcnow().isoformat(),
                "started_at": None,
                "ended_at": None,
                "resource_name": chaos_resource["metadata"]["name"],
                "duration": experiment_config.get(
                    "duration", settings.chaos.default_duration
                ),
            }

            self.active_experiments[experiment_id] = experiment_info

            # Audit log
            audit_logger.log_experiment_created(
                cluster=cluster_name,
                experiment_type=experiment_type,
                experiment_name=experiment_id,
                target=experiment_config.get("selector", {}),
            )

            logger.info(
                "experiment_created",
                experiment_id=experiment_id,
                cluster=cluster_name,
                type=experiment_type,
            )

            return {
                "success": True,
                "experiment_id": experiment_id,
                "experiment_info": experiment_info,
            }

        except Exception as e:
            logger.error(
                "experiment_creation_failed",
                cluster=cluster_name,
                type=experiment_type,
                error=str(e),
            )
            return {"success": False, "error": f"Experiment creation failed: {str(e)}"}

    async def start_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Start experiment"""
        try:
            if experiment_id not in self.active_experiments:
                return {"success": False, "error": "Experiment not found"}

            experiment = self.active_experiments[experiment_id]

            if experiment["status"] != "created":
                return {
                    "success": False,
                    "error": f"Experiment is in {experiment['status']} state",
                }

            # Activate Chaos Mesh resource (actually starts automatically on creation)
            experiment["status"] = "running"
            experiment["started_at"] = datetime.utcnow().isoformat()

            # Audit log
            audit_logger.log_experiment_started(
                cluster=experiment["cluster"], experiment_name=experiment_id
            )

            logger.info(
                "experiment_started",
                experiment_id=experiment_id,
                cluster=experiment["cluster"],
            )

            return {
                "success": True,
                "experiment_id": experiment_id,
                "status": "running",
            }

        except Exception as e:
            logger.error(
                "experiment_start_failed",
                experiment_id=experiment_id,
                error=str(e),
            )
            return {"success": False, "error": f"Failed to start experiment: {str(e)}"}

    async def stop_experiment(
        self, experiment_id: str, reason: str = "user_request"
    ) -> Dict[str, Any]:
        """Stop experiment"""
        try:
            if experiment_id not in self.active_experiments:
                return {"success": False, "error": "Experiment not found"}

            experiment = self.active_experiments[experiment_id]

            if experiment["status"] not in ["created", "running"]:
                return {
                    "success": False,
                    "error": f"Experiment is in {experiment['status']} state",
                }

            # Delete Chaos Mesh resource
            success = await self._delete_chaos_resource(
                experiment["cluster"],
                experiment["namespace"],
                experiment["resource_name"],
                experiment["type"],
            )

            if success:
                experiment["status"] = "stopped"
                experiment["ended_at"] = datetime.utcnow().isoformat()

                # Move to history
                self.experiment_history.append(experiment.copy())
                del self.active_experiments[experiment_id]

                # Audit log
                audit_logger.log_experiment_stopped(
                    cluster=experiment["cluster"],
                    experiment_name=experiment_id,
                    reason=reason,
                )

                logger.info(
                    "experiment_stopped",
                    experiment_id=experiment_id,
                    cluster=experiment["cluster"],
                    reason=reason,
                )

                return {
                    "success": True,
                    "experiment_id": experiment_id,
                    "status": "stopped",
                }
            else:
                return {"success": False, "error": "Failed to delete chaos resource"}

        except Exception as e:
            logger.error(
                "experiment_stop_failed",
                experiment_id=experiment_id,
                error=str(e),
            )
            return {"success": False, "error": f"Failed to stop experiment: {str(e)}"}

    async def get_experiment_status(
        self, experiment_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get experiment status"""
        if experiment_id in self.active_experiments:
            experiment = self.active_experiments[experiment_id]

            # Check actual Chaos Mesh resource status
            resource_status = await self._get_chaos_resource_status(
                experiment["cluster"],
                experiment["namespace"],
                experiment["resource_name"],
                experiment["type"],
            )

            if resource_status:
                experiment["chaos_status"] = resource_status

            return experiment

        # Search in history
        for exp in self.experiment_history:
            if exp["id"] == experiment_id:
                return exp

        return None

    def list_experiments(
        self,
        cluster_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List experiments"""
        experiments = list(self.active_experiments.values()) + self.experiment_history

        # Filter
        if cluster_name:
            experiments = [exp for exp in experiments if exp["cluster"] == cluster_name]

        if status:
            experiments = [exp for exp in experiments if exp["status"] == status]

        # Sort by creation time in descending order
        experiments.sort(key=lambda x: x["created_at"], reverse=True)

        return experiments

    async def _create_chaos_resource(
        self,
        cluster_name: str,
        experiment_type: str,
        config: Dict[str, Any],
        experiment_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Create Chaos Mesh resource"""
        try:
            client = cluster_manager.get_client(cluster_name)
            if not client:
                return None

            # Create resource by experiment type
            resource_spec = await self._build_chaos_resource_spec(
                experiment_type, config, experiment_id
            )

            if not resource_spec:
                return None

            # Create custom resource

            custom_api = k8s_client.CustomObjectsApi(client)

            result = custom_api.create_namespaced_custom_object(
                group="chaos-mesh.org",
                version="v1alpha1",
                plural=self._get_plural_name(experiment_type),
                namespace=config.get("namespace", "default"),
                body=resource_spec,
            )

            return result

        except Exception as e:
            logger.error(
                "chaos_resource_creation_failed",
                cluster=cluster_name,
                type=experiment_type,
                experiment_id=experiment_id,
                error=str(e),
            )
            return None

    async def _delete_chaos_resource(
        self,
        cluster_name: str,
        namespace: str,
        resource_name: str,
        experiment_type: str,
    ) -> bool:
        """Delete Chaos Mesh resource"""
        try:
            client = cluster_manager.get_client(cluster_name)
            if not client:
                return False

            custom_api = k8s_client.CustomObjectsApi(client)

            custom_api.delete_namespaced_custom_object(
                group="chaos-mesh.org",
                version="v1alpha1",
                plural=self._get_plural_name(experiment_type),
                namespace=namespace,
                name=resource_name,
            )
            return True

        except Exception as e:
            logger.error(
                "chaos_resource_deletion_failed",
                cluster=cluster_name,
                namespace=namespace,
                resource_name=resource_name,
                error=str(e),
            )
            return False

    async def _get_chaos_resource_status(
        self,
        cluster_name: str,
        namespace: str,
        resource_name: str,
        experiment_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Get Chaos Mesh resource status"""
        try:
            client = cluster_manager.get_client(cluster_name)
            if not client:
                return None

            custom_api = k8s_client.CustomObjectsApi(client)

            resource = custom_api.get_namespaced_custom_object(
                group="chaos-mesh.org",
                version="v1alpha1",
                plural=self._get_plural_name(experiment_type),
                namespace=namespace,
                name=resource_name,
            )

            return resource.get("status", {})

        except Exception as e:
            logger.error(
                "chaos_resource_status_failed",
                cluster=cluster_name,
                namespace=namespace,
                resource_name=resource_name,
                error=str(e),
            )
            return None

    def _get_plural_name(self, experiment_type: str) -> str:
        """Get plural resource name by experiment type"""
        type_mapping = {
            "pod_chaos": "podchaos",
            "network_chaos": "networkchaos",
            "stress_chaos": "stresschaos",
            "time_chaos": "timechaos",
            "io_chaos": "iochaos",
            "dns_chaos": "dnschaos",
            # "aws_chaos": "awschaos",
            "kernel_chaos": "kernelchaos",
        }
        return type_mapping.get(experiment_type, f"{experiment_type}s")

    async def _build_chaos_resource_spec(
        self, experiment_type: str, config: Dict[str, Any], experiment_id: str
    ) -> Optional[Dict[str, Any]]:
        """Build resource spec by experiment type"""
        # Implemented in each experiment type template

        template = get_template(experiment_type)
        if not template:
            return None

        return template.build_spec(config, experiment_id)

    async def _cleanup_loop(self) -> None:
        """Clean up expired experiments"""
        while True:
            try:
                await asyncio.sleep(settings.chaos.monitoring_interval)

                current_time = datetime.utcnow()
                expired_experiments = []

                for exp_id, experiment in self.active_experiments.items():
                    if experiment["status"] == "running":
                        # Check experiment start time + duration
                        if experiment["started_at"]:
                            started_at = datetime.fromisoformat(
                                experiment["started_at"]
                            )
                            duration_seconds = self._parse_duration(
                                experiment["duration"]
                            )

                            if current_time > started_at + timedelta(
                                seconds=duration_seconds
                            ):
                                expired_experiments.append(exp_id)

                # Stop expired experiments
                for exp_id in expired_experiments:
                    await self.stop_experiment(exp_id, "duration_expired")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("cleanup_loop_error", error=str(e))

    def _parse_duration(self, duration: str) -> int:
        """Parse duration (e.g., "60s", "5m", "1h")"""
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        else:
            return int(duration)  # Default to seconds

    async def shutdown(self) -> None:
        """Shutdown experiment manager"""
        logger.info("shutting_down_experiment_manager")

        # Stop cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Stop all active experiments
        for exp_id in list(self.active_experiments.keys()):
            await self.stop_experiment(exp_id, "server_shutdown")

        logger.info("experiment_manager_shutdown_complete")


# Global experiment manager instance
experiment_manager = ExperimentManager()
experiment_manager = ExperimentManager()

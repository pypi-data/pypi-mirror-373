#!/usr/bin/env python3
"""
Chaos Mesh Remote Cluster Manager
Install Chaos Mesh on other clusters from Management EKS cluster and perform remote chaos engineering
"""

import asyncio
import base64
import json
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional

import boto3
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from chaos.experiment_manager import experiment_manager
from k8s.cluster_manager import cluster_manager
from utils.config import ClusterConfig, settings
from utils.logger import get_logger

logger = get_logger(__name__)


class RemoteClusterManager:
    """Chaos Mesh Remote Cluster Manager"""

    def __init__(self):
        # self.management_cluster_name = management_cluster_name
        self.remote_clusters: Dict[str, Dict[str, Any]] = {}
        self.chaos_mesh_status: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize Remote Cluster Manager"""
        try:
            # logger.info(
            #     "initializing_remote_cluster_manager",
            #     management_cluster=self.management_cluster_name,
            # )

            # # Check Management cluster connection
            # mgmt_client = cluster_manager.get_k8s_client(self.management_cluster_name)
            # if not mgmt_client:
            #     raise Exception(
            #         f"Cannot connect to Management cluster '{self.management_cluster_name}'"
            #     )

            logger.info("remote_cluster_manager_initialized")

        except Exception as e:
            logger.error("remote_cluster_manager_init_failed", error=str(e))
            raise

    async def add_remote_cluster(self, cluster_config: ClusterConfig) -> Dict[str, Any]:
        """Add remote cluster"""
        try:
            logger.info("adding_remote_cluster", cluster=cluster_config.name)

            # Add cluster to cluster manager
            success = await cluster_manager.add_cluster(
                cluster_config.name, cluster_config
            )

            if not success:
                return {"success": False, "error": "Cluster connection failed"}

            # Save remote cluster information
            cluster_info = await cluster_manager.get_cluster_info(cluster_config.name)

            self.remote_clusters[cluster_config.name] = {
                "config": cluster_config,
                "info": cluster_info,
                "status": "connected",
                "added_at": time.time(),
                "chaos_mesh_installed": False,
            }

            logger.info("remote_cluster_added", cluster=cluster_config.name)

            return {
                "success": True,
                "cluster_name": cluster_config.name,
                "cluster_info": cluster_info,
            }

        except Exception as e:
            logger.error(
                "remote_cluster_add_failed", cluster=cluster_config.name, error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def remove_remote_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Remove remote cluster"""
        try:
            logger.info("removing_remote_cluster", cluster=cluster_name)

            # Remove from cluster manager
            success = await cluster_manager.remove_cluster(cluster_name)

            if success and cluster_name in self.remote_clusters:
                del self.remote_clusters[cluster_name]

            if cluster_name in self.chaos_mesh_status:
                del self.chaos_mesh_status[cluster_name]

            logger.info("remote_cluster_removed", cluster=cluster_name)

            return {"success": True, "cluster_name": cluster_name}

        except Exception as e:
            logger.error(
                "remote_cluster_remove_failed", cluster=cluster_name, error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def install_chaos_mesh_on_remote(
        self, cluster_name: str, namespace: str = "chaos-mesh"
    ) -> Dict[str, Any]:
        """Install Chaos Mesh on remote cluster"""
        try:
            logger.info(
                "installing_chaos_mesh_remote",
                cluster=cluster_name,
                namespace=namespace,
            )

            if cluster_name not in self.remote_clusters:
                return {"success": False, "error": "Cluster not found"}

            # Get Kubernetes client
            k8s_client = cluster_manager.get_k8s_client(cluster_name)
            if not k8s_client:
                return {"success": False, "error": "Cannot get cluster connection"}

            # Check existing installation
            existing_installation = await self._check_existing_chaos_mesh(
                k8s_client, namespace
            )
            if existing_installation["installed"]:
                logger.info("chaos_mesh_already_installed", cluster=cluster_name)
                self.remote_clusters[cluster_name]["chaos_mesh_installed"] = True
                self.chaos_mesh_status[cluster_name] = existing_installation
                return {
                    "success": True,
                    "message": "Chaos Mesh is already installed",
                    "status": existing_installation,
                }

            # 1. Create namespace
            await self._create_namespace(k8s_client, namespace)

            # 2. Install Chaos Mesh
            installation_result = await self._install_chaos_mesh_components(
                cluster_name, namespace
            )

            if not installation_result["success"]:
                return installation_result

            # 3. Verify installation
            verification_result = await self._verify_chaos_mesh_installation(
                k8s_client, namespace
            )

            if verification_result["success"]:
                self.remote_clusters[cluster_name]["chaos_mesh_installed"] = True
                self.chaos_mesh_status[cluster_name] = verification_result["status"]

                logger.info("chaos_mesh_installed_successfully", cluster=cluster_name)

                return {
                    "success": True,
                    "cluster_name": cluster_name,
                    "namespace": namespace,
                    "status": verification_result["status"],
                    "dashboard_info": await self._get_dashboard_access_info(
                        k8s_client, namespace
                    ),
                }
            else:
                return {
                    "success": False,
                    "error": "Chaos Mesh installation verification failed",
                }

        except Exception as e:
            logger.error(
                "chaos_mesh_install_failed", cluster=cluster_name, error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def _check_existing_chaos_mesh(
        self, k8s_client, namespace: str
    ) -> Dict[str, Any]:
        """Check existing Chaos Mesh installation"""
        try:
            core_v1 = client.CoreV1Api(k8s_client)
            apps_v1 = client.AppsV1Api(k8s_client)
            api_extensions = client.ApiextensionsV1Api(k8s_client)

            # 1. Check namespace
            try:
                core_v1.read_namespace(name=namespace)
                namespace_exists = True
            except ApiException as e:
                if e.status == 404:
                    namespace_exists = False
                else:
                    raise

            # 2. Check CRDs
            crds = api_extensions.list_custom_resource_definition()
            chaos_mesh_crds = []
            for crd in crds.items:
                if crd.spec.group == "chaos-mesh.org":
                    chaos_mesh_crds.append(
                        {
                            "name": crd.metadata.name,
                            "version": crd.spec.versions[0].name
                            if crd.spec.versions
                            else "unknown",
                            "kind": crd.spec.names.kind,
                        }
                    )

            # 3. Check controllers
            controllers = []
            if namespace_exists:
                try:
                    deployments = apps_v1.list_namespaced_deployment(
                        namespace=namespace
                    )
                    for deployment in deployments.items:
                        if "chaos" in deployment.metadata.name.lower():
                            controllers.append(
                                {
                                    "name": deployment.metadata.name,
                                    "ready_replicas": deployment.status.ready_replicas
                                    or 0,
                                    "replicas": deployment.spec.replicas or 0,
                                    "status": "Ready"
                                    if deployment.status.ready_replicas
                                    == deployment.spec.replicas
                                    else "NotReady",
                                }
                            )
                except Exception:
                    pass

            installed = len(chaos_mesh_crds) > 0 and len(controllers) > 0

            return {
                "installed": installed,
                "namespace_exists": namespace_exists,
                "crds": chaos_mesh_crds,
                "crd_count": len(chaos_mesh_crds),
                "controllers": controllers,
                "controller_count": len(controllers),
            }

        except Exception as e:
            logger.error("chaos_mesh_check_failed", error=str(e))
            return {"installed": False, "error": str(e)}

    async def _create_namespace(self, k8s_client, namespace: str):
        """Create namespace"""
        try:
            core_v1 = client.CoreV1Api(k8s_client)

            try:
                core_v1.read_namespace(name=namespace)
                logger.info("namespace_already_exists", namespace=namespace)
                return
            except ApiException as e:
                if e.status != 404:
                    raise

            namespace_manifest = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=namespace)
            )
            core_v1.create_namespace(body=namespace_manifest)
            logger.info("namespace_created", namespace=namespace)

        except Exception as e:
            logger.error("namespace_creation_failed", namespace=namespace, error=str(e))
            raise

    async def _install_chaos_mesh_components(
        self, cluster_name: str, namespace: str
    ) -> Dict[str, Any]:
        """Install Chaos Mesh components"""
        try:
            # Create temporary kubeconfig for kubectl context setup
            kubeconfig_path = await self._create_temp_kubeconfig(cluster_name)

            if not kubeconfig_path:
                return {"success": False, "error": "Failed to create kubeconfig"}

            # Try installation using Helm
            helm_result = await self._install_via_helm(kubeconfig_path, namespace)

            if helm_result["success"]:
                return helm_result

            # Fallback to kubectl if Helm fails
            kubectl_result = await self._install_via_kubectl(kubeconfig_path, namespace)

            return kubectl_result

        except Exception as e:
            logger.error(
                "chaos_mesh_components_install_failed",
                cluster=cluster_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def _create_temp_kubeconfig(self, cluster_name: str) -> Optional[str]:
        """Create temporary kubeconfig file"""
        try:
            oidc_client = cluster_manager.get_oidc_client(cluster_name)
            if not oidc_client:
                return None

            cluster_info = oidc_client.get_cluster_info()
            if not cluster_info:
                return None

            # Generate token
            token = await oidc_client.get_token()

            # Create kubeconfig
            kubeconfig = {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [
                    {
                        "name": cluster_name,
                        "cluster": {
                            "server": cluster_info["endpoint"],
                            "certificate-authority-data": cluster_info["ca_cert"],
                        },
                    }
                ],
                "users": [{"name": f"{cluster_name}-user", "user": {"token": token}}],
                "contexts": [
                    {
                        "name": cluster_name,
                        "context": {
                            "cluster": cluster_name,
                            "user": f"{cluster_name}-user",
                        },
                    }
                ],
                "current-context": cluster_name,
            }

            # Save as temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".yaml"
            ) as f:
                yaml.dump(kubeconfig, f, default_flow_style=False)
                return f.name

        except Exception as e:
            logger.error(
                "temp_kubeconfig_creation_failed", cluster=cluster_name, error=str(e)
            )
            return None

    async def _install_via_helm(
        self, kubeconfig_path: str, namespace: str
    ) -> Dict[str, Any]:
        """Install Chaos Mesh using Helm"""
        try:
            logger.info("installing_chaos_mesh_via_helm", namespace=namespace)

            helm_commands = [
                ["helm", "repo", "add", "chaos-mesh", "https://charts.chaos-mesh.org"],
                ["helm", "repo", "update"],
                [
                    "helm",
                    "install",
                    "chaos-mesh",
                    "chaos-mesh/chaos-mesh",
                    "--namespace",
                    namespace,
                    "--create-namespace",
                    "--set",
                    "chaosDaemon.runtime=containerd",
                    "--set",
                    "chaosDaemon.socketPath=/run/containerd/containerd.sock",
                    "--set",
                    "dashboard.create=true",
                    "--set",
                    "dashboard.securityMode=false",
                    "--kubeconfig",
                    kubeconfig_path,
                    "--wait",
                    "--timeout=300s",
                ],
            ]

            for cmd in helm_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(
                        "helm_command_warning",
                        command=" ".join(cmd),
                        stderr=result.stderr,
                    )
                    if "install" in cmd:  # Return error if install command fails
                        return {
                            "success": False,
                            "error": f"Helm installation failed: {result.stderr}",
                        }

            logger.info("chaos_mesh_installed_via_helm")
            return {"success": True, "method": "helm"}

        except Exception as e:
            logger.error("helm_install_failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _install_via_kubectl(
        self, kubeconfig_path: str, namespace: str
    ) -> Dict[str, Any]:
        """Install Chaos Mesh using kubectl"""
        try:
            logger.info("installing_chaos_mesh_via_kubectl", namespace=namespace)

            kubectl_commands = [
                ["kubectl", "create", "ns", namespace, "--kubeconfig", kubeconfig_path],
                [
                    "kubectl",
                    "apply",
                    "-f",
                    "https://mirrors.chaos-mesh.org/v2.6.2/crd.yaml",
                    "--kubeconfig",
                    kubeconfig_path,
                ],
                [
                    "kubectl",
                    "apply",
                    "-f",
                    "https://mirrors.chaos-mesh.org/v2.6.2/chaos-mesh.yaml",
                    "-n",
                    namespace,
                    "--kubeconfig",
                    kubeconfig_path,
                ],
            ]

            for cmd in kubectl_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0 and "already exists" not in result.stderr:
                    logger.warning(
                        "kubectl_command_warning",
                        command=" ".join(cmd),
                        stderr=result.stderr,
                    )

            logger.info("chaos_mesh_installed_via_kubectl")
            return {"success": True, "method": "kubectl"}

        except Exception as e:
            logger.error("kubectl_install_failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _verify_chaos_mesh_installation(
        self, k8s_client, namespace: str
    ) -> Dict[str, Any]:
        """Verify Chaos Mesh installation"""
        try:
            logger.info("verifying_chaos_mesh_installation", namespace=namespace)

            max_wait_time = 120  # 2 minutes
            wait_interval = 10
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                status = await self._check_existing_chaos_mesh(k8s_client, namespace)

                if status["installed"]:
                    running_controllers = [
                        c for c in status["controllers"] if c["status"] == "Ready"
                    ]

                    if len(running_controllers) >= 1:  # At least 1 controller is Ready
                        logger.info(
                            "chaos_mesh_verification_successful",
                            controllers=len(running_controllers),
                            crds=len(status["crds"]),
                        )
                        return {"success": True, "status": status}

                logger.info(
                    "waiting_for_chaos_mesh_ready",
                    elapsed=elapsed_time,
                    max_wait=max_wait_time,
                    controllers=len(status.get("controllers", [])),
                )

                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval

            return {"success": False, "error": "Installation verification timeout"}

        except Exception as e:
            logger.error("chaos_mesh_verification_failed", error=str(e))
            return {"success": False, "error": str(e)}

    async def _get_dashboard_access_info(
        self, k8s_client, namespace: str
    ) -> Dict[str, Any]:
        """Get dashboard access information"""
        try:
            core_v1 = client.CoreV1Api(k8s_client)
            services = core_v1.list_namespaced_service(namespace=namespace)

            dashboard_service = None
            for svc in services.items:
                if "dashboard" in svc.metadata.name.lower():
                    dashboard_service = svc
                    break

            if dashboard_service:
                port = (
                    dashboard_service.spec.ports[0].port
                    if dashboard_service.spec.ports
                    else 2333
                )
                return {
                    "service_name": dashboard_service.metadata.name,
                    "port": port,
                    "namespace": namespace,
                    "port_forward_command": f"kubectl port-forward -n {namespace} svc/{dashboard_service.metadata.name} {port}:{port}",
                    "access_url": f"http://localhost:{port}",
                }
            else:
                return {"error": "Dashboard service not found"}

        except Exception as e:
            logger.error("dashboard_info_failed", error=str(e))
            return {"error": str(e)}

    async def create_remote_experiment(
        self,
        cluster_name: str,
        experiment_type: str,
        experiment_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """CREATE REMOTE EXPERIMENT ON A REMOTE CLUSTER"""
        try:
            if cluster_name not in self.remote_clusters:
                return {"success": False, "error": "Cluster not found"}

            if not self.remote_clusters[cluster_name]["chaos_mesh_installed"]:
                return {
                    "success": False,
                    "error": "Chaos Mesh not installed on the cluster",
                }

            result = await experiment_manager.create_experiment(
                cluster_name,
                experiment_type,
                experiment_config,
            )

            if result["success"]:
                logger.info(
                    "remote_experiment_created",
                    cluster=cluster_name,
                    experiment_id=result["experiment_id"],
                    type=experiment_type,
                )

            return result

        except Exception as e:
            logger.error(
                "remote_experiment_creation_failed",
                cluster=cluster_name,
                type=experiment_type,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    def list_remote_clusters(self) -> List[Dict[str, Any]]:
        """List remote clusters"""
        clusters = []
        for cluster_name, cluster_data in self.remote_clusters.items():
            cluster_info = {
                "name": cluster_name,
                "region": cluster_data["config"].region,
                "status": cluster_data["status"],
                "chaos_mesh_installed": cluster_data["chaos_mesh_installed"],
                "added_at": cluster_data["added_at"],
            }

            if cluster_name in self.chaos_mesh_status:
                cluster_info["chaos_mesh_status"] = self.chaos_mesh_status[cluster_name]

            clusters.append(cluster_info)

        return clusters

    async def get_remote_cluster_status(
        self, cluster_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get remote cluster status"""
        if cluster_name not in self.remote_clusters:
            return None

        try:
            cluster_info = await cluster_manager.get_cluster_info(cluster_name)

            k8s_client = cluster_manager.get_k8s_client(cluster_name)
            if k8s_client:
                chaos_status = await self._check_existing_chaos_mesh(
                    k8s_client, "chaos-mesh"
                )
                self.chaos_mesh_status[cluster_name] = chaos_status
                self.remote_clusters[cluster_name]["chaos_mesh_installed"] = (
                    chaos_status["installed"]
                )

            return {
                "cluster_name": cluster_name,
                "cluster_info": cluster_info,
                "chaos_mesh_status": self.chaos_mesh_status.get(cluster_name, {}),
                "remote_cluster_data": self.remote_clusters[cluster_name],
            }

        except Exception as e:
            logger.error(
                "remote_cluster_status_failed", cluster=cluster_name, error=str(e)
            )
            return {"error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown Remote Cluster Manager"""
        logger.info("shutting_down_remote_cluster_manager")

        for cluster_name in list(self.remote_clusters.keys()):
            await self.remove_remote_cluster(cluster_name)

        logger.info("remote_cluster_manager_shutdown_complete")


remote_cluster_manager = None


def get_remote_cluster_manager() -> RemoteClusterManager:
    """Get Remote Cluster Manager instance"""
    global remote_cluster_manager
    if remote_cluster_manager is None:
        remote_cluster_manager = RemoteClusterManager()
    return remote_cluster_manager

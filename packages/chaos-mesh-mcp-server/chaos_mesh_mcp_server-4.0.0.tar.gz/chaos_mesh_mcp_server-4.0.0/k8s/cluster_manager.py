"""EKS OIDC-based multi-cluster manager"""

import asyncio
from typing import Any, Dict, List, Optional

from auth.eks_oidc_client import EKSOIDCClient
from auth.rbac_manager import RBACManager
from utils.config import ClusterConfig, settings
from utils.logger import get_logger

logger = get_logger(__name__)


class EKSClusterManager:
    """EKS OIDC-based multi-cluster manager"""

    def __init__(self):
        self.oidc_clients: Dict[str, EKSOIDCClient] = {}
        self.k8s_clients: Dict[str, Any] = {}  # client.ApiClient
        self.rbac_managers: Dict[str, RBACManager] = {}
        self.cluster_status: Dict[str, str] = {}
        self._health_check_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize cluster manager"""
        logger.info("initializing_eks_cluster_manager")

        # Verify AWS credentials
        await self._verify_aws_credentials()

        # Connect to all configured clusters
        for cluster_name, cluster_config in settings.clusters.items():
            await self.add_cluster(cluster_name, cluster_config)

        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info(
            "eks_cluster_manager_initialized",
            cluster_count=len(self.oidc_clients),
            connected_clusters=list(self.cluster_status.keys()),
        )

    async def _verify_aws_credentials(self) -> None:
        """Verify AWS credentials"""
        try:
            import boto3

            session = boto3.Session()
            sts_client = session.client("sts")

            # Check current credentials
            identity = sts_client.get_caller_identity()

            logger.info(
                "aws_credentials_verified",
                account_id=identity["Account"],
                user_id=identity["UserId"],
                arn=identity["Arn"],
            )

        except Exception as e:
            logger.error("aws_credentials_verification_failed", error=str(e))
            raise Exception(f"AWS credentials verification failed: {str(e)}")

    async def add_cluster(self, name: str, config: ClusterConfig) -> bool:
        """Add EKS cluster"""
        try:
            logger.info("adding_eks_cluster", cluster=name, region=config.region)

            # Create and initialize OIDC client
            oidc_client = EKSOIDCClient(config)
            await oidc_client.initialize()

            # Create Kubernetes client
            k8s_client = await oidc_client.create_k8s_client()

            # Create RBAC manager
            rbac_manager = RBACManager(k8s_client)

            # Validate permissions
            permissions = await oidc_client.validate_permissions()

            # Store clients
            self.oidc_clients[name] = oidc_client
            self.k8s_clients[name] = k8s_client
            self.rbac_managers[name] = rbac_manager
            self.cluster_status[name] = "connected"

            logger.info(
                "eks_cluster_added",
                cluster=name,
                endpoint=config.endpoint,
                permissions=permissions,
            )

            return True

        except Exception as e:
            logger.error("eks_cluster_add_failed", cluster=name, error=str(e))
            self.cluster_status[name] = "failed"
            # Re-raise exception with specific error message
            raise Exception(f"Failed to add cluster '{name}': {str(e)}")

    async def remove_cluster(self, name: str) -> bool:
        """Remove cluster"""
        try:
            if name in self.oidc_clients:
                del self.oidc_clients[name]
            if name in self.k8s_clients:
                del self.k8s_clients[name]
            if name in self.rbac_managers:
                del self.rbac_managers[name]
            if name in self.cluster_status:
                del self.cluster_status[name]

            logger.info("eks_cluster_removed", cluster=name)
            return True

        except Exception as e:
            logger.error("eks_cluster_remove_failed", cluster=name, error=str(e))
            return False

    def get_oidc_client(self, cluster_name: str) -> Optional[EKSOIDCClient]:
        """Get OIDC client"""
        return self.oidc_clients.get(cluster_name)

    def get_client(self, cluster_name: str) -> Optional[Any]:
        """Get Kubernetes client (alias for get_k8s_client)"""
        return self.get_k8s_client(cluster_name)

    def get_k8s_client(self, cluster_name: str) -> Optional[Any]:
        """Get Kubernetes client"""
        return self.k8s_clients.get(cluster_name)

    def get_rbac_manager(self, cluster_name: str) -> Optional[RBACManager]:
        """Get RBAC manager"""
        return self.rbac_managers.get(cluster_name)

    def list_clusters(self) -> List[Dict[str, Any]]:
        """List clusters"""
        clusters = []

        for name in self.oidc_clients.keys():
            oidc_client = self.oidc_clients[name]
            cluster_info = oidc_client.get_cluster_info()

            cluster_data = {
                "name": name,
                "region": oidc_client.cluster_config.region,
                "status": self.cluster_status.get(name, "unknown"),
                "auth_method": "eks_oidc",
            }

            if cluster_info:
                cluster_data.update(
                    {
                        "endpoint": cluster_info.get("endpoint"),
                        "version": cluster_info.get("version"),
                        "oidc_issuer": cluster_info.get("oidc_issuer"),
                    }
                )

            clusters.append(cluster_data)

        return clusters

    async def get_cluster_info(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """Get cluster detailed information"""
        oidc_client = self.get_oidc_client(cluster_name)
        k8s_client = self.get_k8s_client(cluster_name)

        try:
            # Basic cluster information
            cluster_info = oidc_client.get_cluster_info()

            # Kubernetes API information
            from kubernetes import client

            core_v1 = client.CoreV1Api(k8s_client)
            # get_code() method doesn't exist, so remove it and use basic info only
            version_info = None

            # Namespace list
            try:
                namespaces_response = core_v1.list_namespace()
                namespaces = [ns.metadata.name for ns in namespaces_response.items]
            except Exception as e:
                logger.warning(
                    "namespace_list_failed", cluster=cluster_name, error=str(e)
                )
                namespaces = []

            # Check Chaos Mesh installation
            chaos_mesh_installed = await self._check_chaos_mesh_installation(k8s_client)

            # Permission information
            permissions = await oidc_client.validate_permissions()

            result = {
                "name": cluster_name,
                "status": self.cluster_status.get(cluster_name, "unknown"),
                "auth_method": "eks_oidc",
                "aws_region": oidc_client.cluster_config.region,
                "cluster_info": cluster_info,
                "kubernetes_version": version_info.git_version
                if version_info
                else None,
                "namespaces": namespaces,
                "namespace_count": len(namespaces),
                "chaos_mesh_installed": chaos_mesh_installed,
                "permissions": permissions,
                "role_arn": oidc_client.cluster_config.role_arn,
            }

            return result

        except Exception as e:
            logger.error("get_cluster_info_failed", cluster=cluster_name, error=str(e))
            return None

    async def _check_chaos_mesh_installation(self, k8s_client) -> Dict[str, Any]:
        """Check Chaos Mesh installation status"""
        try:
            from kubernetes import client

            # Check CRDs
            api_extensions = client.ApiextensionsV1Api(k8s_client)
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

            # Check Chaos Mesh namespace
            core_v1 = client.CoreV1Api(k8s_client)
            try:
                chaos_mesh_ns = core_v1.read_namespace(name="chaos-mesh")
                namespace_exists = True
                namespace_status = chaos_mesh_ns.status.phase
            except client.ApiException as e:
                if e.status == 404:
                    namespace_exists = False
                    namespace_status = "NotFound"
                else:
                    namespace_exists = False
                    namespace_status = "Error"

            # Check Chaos Mesh controllers
            apps_v1 = client.AppsV1Api(k8s_client)
            controllers = []
            if namespace_exists:
                try:
                    deployments = apps_v1.list_namespaced_deployment(
                        namespace="chaos-mesh"
                    )
                    for deployment in deployments.items:
                        controllers.append(
                            {
                                "name": deployment.metadata.name,
                                "ready_replicas": deployment.status.ready_replicas or 0,
                                "replicas": deployment.spec.replicas or 0,
                                "status": "Ready"
                                if deployment.status.ready_replicas
                                == deployment.spec.replicas
                                else "NotReady",
                            }
                        )
                except Exception:
                    pass

            return {
                "installed": len(chaos_mesh_crds) > 0,
                "crds": chaos_mesh_crds,
                "crd_count": len(chaos_mesh_crds),
                "namespace_exists": namespace_exists,
                "namespace_status": namespace_status,
                "controllers": controllers,
                "controller_count": len(controllers),
            }

        except Exception as e:
            logger.error("chaos_mesh_check_failed", error=str(e))
            return {"installed": False, "error": str(e)}

    async def validate_cluster_access(
        self, cluster_name: str, user: str, namespace: str
    ) -> bool:
        """Validate cluster access permissions"""
        rbac_manager = self.get_rbac_manager(cluster_name)
        if not rbac_manager:
            return False

        # Check namespace access permissions
        if not await rbac_manager.validate_namespace_access(user, namespace):
            return False

        # Check Chaos Mesh resource access permissions
        return await rbac_manager.check_permissions(
            user, namespace, "podchaos", "create"
        )

    async def refresh_cluster_tokens(self) -> Dict[str, bool]:
        """Refresh tokens for all clusters"""
        results = {}

        for cluster_name, oidc_client in self.oidc_clients.items():
            try:
                await oidc_client.refresh_token()

                # Create new Kubernetes client
                new_k8s_client = await oidc_client.create_k8s_client()
                self.k8s_clients[cluster_name] = new_k8s_client

                # Update RBAC manager
                self.rbac_managers[cluster_name] = RBACManager(new_k8s_client)

                results[cluster_name] = True
                logger.info("cluster_token_refreshed", cluster=cluster_name)

            except Exception as e:
                results[cluster_name] = False
                logger.error(
                    "cluster_token_refresh_failed", cluster=cluster_name, error=str(e)
                )

        return results

    async def _health_check_loop(self) -> None:
        """Periodic health check"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                for cluster_name in list(self.oidc_clients.keys()):
                    try:
                        k8s_client = self.get_k8s_client(cluster_name)
                        if k8s_client:
                            from kubernetes import client

                            core_v1 = client.CoreV1Api(k8s_client)
                            core_v1.list_namespace(limit=1)  # Simple API call

                            self.cluster_status[cluster_name] = "connected"
                        else:
                            self.cluster_status[cluster_name] = "disconnected"

                    except Exception as e:
                        logger.warning(
                            "cluster_health_check_failed",
                            cluster=cluster_name,
                            error=str(e),
                        )
                        self.cluster_status[cluster_name] = "unhealthy"

                        # Try token refresh
                        try:
                            oidc_client = self.get_oidc_client(cluster_name)
                            if oidc_client:
                                new_k8s_client = await oidc_client.create_k8s_client()
                                self.k8s_clients[cluster_name] = new_k8s_client
                                self.rbac_managers[cluster_name] = RBACManager(
                                    new_k8s_client
                                )
                                self.cluster_status[cluster_name] = "reconnected"

                                logger.info("cluster_reconnected", cluster=cluster_name)
                        except Exception as reconnect_error:
                            logger.error(
                                "cluster_reconnection_failed",
                                cluster=cluster_name,
                                error=str(reconnect_error),
                            )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("health_check_loop_error", error=str(e))

    async def shutdown(self) -> None:
        """Shutdown cluster manager"""
        logger.info("shutting_down_eks_cluster_manager")

        # Stop health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Clean up all clients
        self.oidc_clients.clear()
        self.k8s_clients.clear()
        self.rbac_managers.clear()
        self.cluster_status.clear()

        logger.info("eks_cluster_manager_shutdown_complete")


# Global EKS cluster manager instance
cluster_manager = EKSClusterManager()

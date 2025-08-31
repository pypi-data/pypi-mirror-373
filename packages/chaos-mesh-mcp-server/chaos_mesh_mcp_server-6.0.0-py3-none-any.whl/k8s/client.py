"""EKS OIDC-based Kubernetes client"""

import asyncio
from typing import Any, Dict, List, Optional

from kubernetes import client
from kubernetes.client.rest import ApiException

from auth.eks_oidc_client import EKSOIDCClient
from utils.config import ClusterConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class EKSK8sClient:
    """EKS OIDC-based Kubernetes client wrapper"""

    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config
        self.oidc_client = EKSOIDCClient(cluster_config)
        self._client: Optional[client.ApiClient] = None
        self._custom_api: Optional[client.CustomObjectsApi] = None
        self._core_v1: Optional[client.CoreV1Api] = None
        self._apps_v1: Optional[client.AppsV1Api] = None
        self._rbac_v1: Optional[client.RbacAuthorizationV1Api] = None

    async def connect(self) -> None:
        """Connect to cluster"""
        try:
            # Initialize OIDC client
            await self.oidc_client.initialize()

            # Create Kubernetes client
            self._client = await self.oidc_client.create_k8s_client()

            # Initialize API clients
            self._custom_api = client.CustomObjectsApi(self._client)
            self._core_v1 = client.CoreV1Api(self._client)
            self._apps_v1 = client.AppsV1Api(self._client)
            self._rbac_v1 = client.RbacAuthorizationV1Api(self._client)

            # Test connection
            await self.health_check()

            logger.info(
                "eks_k8s_client_connected",
                cluster=self.cluster_config.name,
                endpoint=self.cluster_config.endpoint,
            )

        except Exception as e:
            logger.error(
                "eks_k8s_client_connection_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise

    async def health_check(self) -> bool:
        """Check cluster health"""
        try:
            if not self._core_v1:
                return False

            # Check connection with simple API call
            version = self._core_v1.get_code()
            logger.debug(
                "eks_k8s_health_check_success",
                cluster=self.cluster_config.name,
                version=version.git_version,
            )
            return True

        except Exception as e:
            logger.error(
                "eks_k8s_health_check_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            return False

    async def refresh_connection(self) -> None:
        """Refresh connection (when token expires)"""
        try:
            # Refresh token
            await self.oidc_client.refresh_token()

            # Create new client
            self._client = await self.oidc_client.create_k8s_client()

            # Reinitialize API clients
            self._custom_api = client.CustomObjectsApi(self._client)
            self._core_v1 = client.CoreV1Api(self._client)
            self._apps_v1 = client.AppsV1Api(self._client)
            self._rbac_v1 = client.RbacAuthorizationV1Api(self._client)

            logger.info(
                "eks_k8s_connection_refreshed", cluster=self.cluster_config.name
            )

        except Exception as e:
            logger.error(
                "eks_k8s_connection_refresh_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise

    async def create_chaos_resource(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: str,
        body: Dict[str, Any],
        retry_on_auth_error: bool = True,
    ) -> Dict[str, Any]:
        """Create Chaos Mesh custom resource"""
        try:
            if not self._custom_api:
                raise RuntimeError("Client not connected")

            result = self._custom_api.create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                body=body,
            )

            logger.info(
                "chaos_resource_created",
                cluster=self.cluster_config.name,
                namespace=namespace,
                resource=f"{group}/{version}/{plural}",
                name=body.get("metadata", {}).get("name", "unknown"),
            )

            return result

        except ApiException as e:
            # Retry after token refresh on authentication error
            if e.status == 401 and retry_on_auth_error:
                logger.warning(
                    "auth_error_retrying",
                    cluster=self.cluster_config.name,
                    resource=f"{group}/{version}/{plural}",
                )
                await self.refresh_connection()
                return await self.create_chaos_resource(
                    group, version, plural, namespace, body, retry_on_auth_error=False
                )

            logger.error(
                "chaos_resource_creation_failed",
                cluster=self.cluster_config.name,
                namespace=namespace,
                resource=f"{group}/{version}/{plural}",
                error=str(e),
                status=e.status,
            )
            raise

    async def get_chaos_resource(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: str,
        name: str,
        retry_on_auth_error: bool = True,
    ) -> Dict[str, Any]:
        """Get Chaos Mesh custom resource"""
        try:
            if not self._custom_api:
                raise RuntimeError("Client not connected")

            result = self._custom_api.get_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
            )

            return result

        except ApiException as e:
            if e.status == 401 and retry_on_auth_error:
                await self.refresh_connection()
                return await self.get_chaos_resource(
                    group, version, plural, namespace, name, retry_on_auth_error=False
                )

            if e.status == 404:
                logger.warning(
                    "chaos_resource_not_found",
                    cluster=self.cluster_config.name,
                    namespace=namespace,
                    name=name,
                )
                return {}

            logger.error(
                "chaos_resource_get_failed",
                cluster=self.cluster_config.name,
                namespace=namespace,
                name=name,
                error=str(e),
            )
            raise

    async def list_chaos_resources(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        retry_on_auth_error: bool = True,
    ) -> List[Dict[str, Any]]:
        """List Chaos Mesh custom resources"""
        try:
            if not self._custom_api:
                raise RuntimeError("Client not connected")

            if namespace:
                result = self._custom_api.list_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural,
                    label_selector=label_selector,
                )
            else:
                result = self._custom_api.list_cluster_custom_object(
                    group=group,
                    version=version,
                    plural=plural,
                    label_selector=label_selector,
                )

            return result.get("items", [])

        except ApiException as e:
            if e.status == 401 and retry_on_auth_error:
                await self.refresh_connection()
                return await self.list_chaos_resources(
                    group,
                    version,
                    plural,
                    namespace,
                    label_selector,
                    retry_on_auth_error=False,
                )

            logger.error(
                "chaos_resource_list_failed",
                cluster=self.cluster_config.name,
                namespace=namespace,
                resource=f"{group}/{version}/{plural}",
                error=str(e),
            )
            raise

    async def delete_chaos_resource(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: str,
        name: str,
        retry_on_auth_error: bool = True,
    ) -> bool:
        """Delete Chaos Mesh custom resource"""
        try:
            if not self._custom_api:
                raise RuntimeError("Client not connected")

            self._custom_api.delete_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=name,
            )

            logger.info(
                "chaos_resource_deleted",
                cluster=self.cluster_config.name,
                namespace=namespace,
                name=name,
            )

            return True

        except ApiException as e:
            if e.status == 401 and retry_on_auth_error:
                await self.refresh_connection()
                return await self.delete_chaos_resource(
                    group, version, plural, namespace, name, retry_on_auth_error=False
                )

            if e.status == 404:
                logger.warning(
                    "chaos_resource_already_deleted",
                    cluster=self.cluster_config.name,
                    namespace=namespace,
                    name=name,
                )
                return True

            logger.error(
                "chaos_resource_deletion_failed",
                cluster=self.cluster_config.name,
                namespace=namespace,
                name=name,
                error=str(e),
            )
            return False

    async def get_pods(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        retry_on_auth_error: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get Pod list"""
        try:
            if not self._core_v1:
                raise RuntimeError("Client not connected")

            result = self._core_v1.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            )

            pods = []
            for pod in result.items:
                pods.append(
                    {
                        "name": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "labels": pod.metadata.labels or {},
                        "annotations": pod.metadata.annotations or {},
                        "phase": pod.status.phase,
                        "node_name": pod.spec.node_name,
                        "created": pod.metadata.creation_timestamp.isoformat()
                        if pod.metadata.creation_timestamp
                        else None,
                        "ready": self._is_pod_ready(pod),
                    }
                )

            return pods

        except ApiException as e:
            if e.status == 401 and retry_on_auth_error:
                await self.refresh_connection()
                return await self.get_pods(
                    namespace, label_selector, retry_on_auth_error=False
                )

            logger.error(
                "get_pods_failed",
                cluster=self.cluster_config.name,
                namespace=namespace,
                error=str(e),
            )
            raise

    def _is_pod_ready(self, pod) -> bool:
        """Check Pod ready status"""
        if not pod.status.conditions:
            return False

        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return condition.status == "True"

        return False

    async def get_namespaces(self, retry_on_auth_error: bool = True) -> List[str]:
        """Get namespace list"""
        try:
            if not self._core_v1:
                raise RuntimeError("Client not connected")

            result = self._core_v1.list_namespace()
            return [ns.metadata.name for ns in result.items]

        except ApiException as e:
            if e.status == 401 and retry_on_auth_error:
                await self.refresh_connection()
                return await self.get_namespaces(retry_on_auth_error=False)

            logger.error(
                "get_namespaces_failed", cluster=self.cluster_config.name, error=str(e)
            )
            raise

    def get_raw_client(self) -> Optional[client.ApiClient]:
        """Return raw Kubernetes client"""
        return self._client

    async def close(self) -> None:
        """Close client connection"""
        if self._client:
            await self._client.close()
            self._client = None
            self._custom_api = None
            self._core_v1 = None
            self._apps_v1 = None
            self._rbac_v1 = None

            logger.info("eks_k8s_client_disconnected", cluster=self.cluster_config.name)

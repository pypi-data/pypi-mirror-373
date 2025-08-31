"""RBAC permission management"""

from typing import Any, Dict, List, Optional

from kubernetes import client

from utils.config import settings
from utils.logger import audit_logger, get_logger

logger = get_logger(__name__)


class RBACManager:
    """Kubernetes RBAC permission manager"""

    def __init__(self, k8s_client: client.ApiClient):
        self.k8s_client = k8s_client
        self.rbac_v1 = client.RbacAuthorizationV1Api(k8s_client)
        self.core_v1 = client.CoreV1Api(k8s_client)

    async def check_permissions(
        self, user: str, namespace: str, resource: str, verb: str
    ) -> bool:
        """Check user permissions"""
        try:
            # Permission check using SelfSubjectAccessReview
            auth_v1 = client.AuthorizationV1Api(self.k8s_client)

            body = client.V1SelfSubjectAccessReview(
                spec=client.V1SelfSubjectAccessReviewSpec(
                    resource_attributes=client.V1ResourceAttributes(
                        namespace=namespace,
                        verb=verb,
                        resource=resource,
                        group="chaos-mesh.org",
                    )
                )
            )

            result = auth_v1.create_self_subject_access_review(body=body)
            allowed = result.status.allowed

            if not allowed:
                audit_logger.log_security_violation(
                    user=user,
                    action=f"{verb}:{resource}",
                    resource=f"{namespace}/{resource}",
                    reason="insufficient_permissions",
                )

            return allowed

        except Exception as e:
            logger.error(
                "permission_check_failed",
                user=user,
                namespace=namespace,
                resource=resource,
                verb=verb,
                error=str(e),
            )
            return False

    async def validate_namespace_access(self, user: str, namespace: str) -> bool:
        """Validate namespace access permissions"""
        # Check protected namespaces
        if namespace in settings.security.protected_namespaces:
            audit_logger.log_security_violation(
                user=user,
                action="access_namespace",
                resource=namespace,
                reason="protected_namespace",
            )
            return False

        # Check whitelist (if configured)
        cluster_config = None
        for config in settings.clusters.values():
            if (
                config.namespace_whitelist
                and namespace not in config.namespace_whitelist
            ):
                audit_logger.log_security_violation(
                    user=user,
                    action="access_namespace",
                    resource=namespace,
                    reason="not_in_whitelist",
                )
                return False

            if namespace in config.namespace_blacklist:
                audit_logger.log_security_violation(
                    user=user,
                    action="access_namespace",
                    resource=namespace,
                    reason="in_blacklist",
                )
                return False

        # Check namespace existence
        try:
            self.core_v1.read_namespace(name=namespace)
            return True
        except client.ApiException as e:
            if e.status == 404:
                logger.warning("namespace_not_found", namespace=namespace)
                return False
            raise

    async def create_chaos_mesh_rbac(self, namespace: str) -> bool:
        """Create Chaos Mesh RBAC resources"""
        try:
            # Create ServiceAccount
            service_account = client.V1ServiceAccount(
                metadata=client.V1ObjectMeta(name="chaos-mesh-mcp", namespace=namespace)
            )

            try:
                self.core_v1.create_namespaced_service_account(
                    namespace=namespace, body=service_account
                )
            except client.ApiException as e:
                if e.status != 409:  # Already exists
                    raise

            # Create Role
            role = client.V1Role(
                metadata=client.V1ObjectMeta(
                    name="chaos-mesh-mcp-role", namespace=namespace
                ),
                rules=[
                    client.V1PolicyRule(
                        api_groups=["chaos-mesh.org"],
                        resources=["*"],
                        verbs=["get", "list", "create", "update", "patch", "delete"],
                    ),
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=["pods", "services", "endpoints"],
                        verbs=["get", "list"],
                    ),
                ],
            )

            try:
                self.rbac_v1.create_namespaced_role(namespace=namespace, body=role)
            except client.ApiException as e:
                if e.status != 409:  # Already exists
                    raise

            # Create RoleBinding
            role_binding = client.V1RoleBinding(
                metadata=client.V1ObjectMeta(
                    name="chaos-mesh-mcp-binding", namespace=namespace
                ),
                subjects=[
                    client.V1Subject(
                        kind="ServiceAccount",
                        name="chaos-mesh-mcp",
                        namespace=namespace,
                    )
                ],
                role_ref=client.V1RoleRef(
                    kind="Role",
                    name="chaos-mesh-mcp-role",
                    api_group="rbac.authorization.k8s.io",
                ),
            )

            try:
                self.rbac_v1.create_namespaced_role_binding(
                    namespace=namespace, body=role_binding
                )
            except client.ApiException as e:
                if e.status != 409:  # Already exists
                    raise

            logger.info("chaos_mesh_rbac_created", namespace=namespace)
            return True

        except Exception as e:
            logger.error(
                "chaos_mesh_rbac_creation_failed", namespace=namespace, error=str(e)
            )
            return False

    async def get_user_permissions(self, user: str) -> Dict[str, List[str]]:
        """Get user's permission list"""
        permissions = {}

        try:
            # Check permissions in all namespaces
            namespaces = self.core_v1.list_namespace()

            for ns in namespaces.items:
                ns_name = ns.metadata.name
                ns_permissions = []

                # Check permissions for major resources
                resources = ["podchaos", "networkchaos", "stresschaos", "timechaos"]
                verbs = ["get", "list", "create", "update", "delete"]

                for resource in resources:
                    for verb in verbs:
                        if await self.check_permissions(user, ns_name, resource, verb):
                            ns_permissions.append(f"{verb}:{resource}")

                if ns_permissions:
                    permissions[ns_name] = ns_permissions

            return permissions

        except Exception as e:
            logger.error("get_user_permissions_failed", user=user, error=str(e))
            return {}

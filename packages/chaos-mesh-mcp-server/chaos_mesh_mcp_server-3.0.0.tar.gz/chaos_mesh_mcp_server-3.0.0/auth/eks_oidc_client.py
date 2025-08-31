"""EKS OIDC Based Authentication Client"""

import base64
import time
from typing import Dict, Optional, Tuple

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import ClientError
from kubernetes import client

from utils.config import ClusterConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class EKSOIDCClient:
    """EKS OIDC Based Authentication Client"""

    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config
        self.token_cache: Dict[str, Tuple[str, float]] = {}
        self.cluster_info_cache: Optional[Dict] = None
        self._session: Optional[boto3.Session] = None

    async def initialize(self) -> None:
        """Client Initialization"""
        try:
            self._session = boto3.Session()

            await self._load_cluster_info()

            logger.info(
                "eks_oidc_client_initialized",
                cluster=self.cluster_config.name,
                region=self.cluster_config.region,
            )

        except Exception as e:
            logger.error(
                "eks_oidc_client_init_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise

    async def _load_cluster_info(self) -> None:
        """Load EKS Cluster Information"""
        try:
            eks_client = self._session.client(
                "eks", region_name=self.cluster_config.region
            )

            response = eks_client.describe_cluster(name=self.cluster_config.name)
            cluster_info = response["cluster"]

            self.cluster_info_cache = {
                "endpoint": cluster_info["endpoint"],
                "ca_data": cluster_info["certificateAuthority"]["data"],
                "oidc_issuer": cluster_info["identity"]["oidc"]["issuer"],
                "version": cluster_info["version"],
                "status": cluster_info["status"],
            }

            self.cluster_config.endpoint = cluster_info["endpoint"]
            self.cluster_config.oidc_issuer = cluster_info["identity"]["oidc"]["issuer"]

            logger.info(
                "cluster_info_loaded",
                cluster=self.cluster_config.name,
                endpoint=cluster_info["endpoint"],
                version=cluster_info["version"],
                status=cluster_info["status"],
            )

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                raise Exception(
                    f"Could not find '{self.cluster_config.name}' EKS cluster."
                )
            elif error_code == "AccessDeniedException":
                raise Exception(
                    f"Doesn't have enough permission to reach '{self.cluster_config.name}' EKS cluster."
                )
            else:
                raise Exception(f"Failed to load cluster info: {str(e)}")

    async def get_token(self, force_refresh: bool = False) -> str:
        """Get EKS OIDC token"""
        cache_key = f"{self.cluster_config.name}:{self.cluster_config.region}"

        if not force_refresh and cache_key in self.token_cache:
            token, expires_at = self.token_cache[cache_key]
            if time.time() < expires_at - 300:
                return token

        try:
            sts_client = self._session.client(
                "sts", region_name=self.cluster_config.region
            )
            caller_identity = sts_client.get_caller_identity()
            current_arn = caller_identity.get("Arn", "")

            if self.cluster_config.role_arn:
                if (
                    f"assumed-role/{self.cluster_config.role_arn.split('/')[-1]}/"
                    in current_arn
                ):
                    logger.info(
                        "using_current_assumed_role",
                        cluster=self.cluster_config.name,
                        current_arn=current_arn,
                        target_role=self.cluster_config.role_arn,
                    )
                    session = self._session
                else:
                    session = await self._assume_role()
            else:
                session = self._session

            token = self._generate_eks_token(session)

            expires_at = time.time() + 840
            self.token_cache[cache_key] = (token, expires_at)

            logger.info(
                "eks_oidc_token_acquired",
                cluster=self.cluster_config.name,
                expires_in="14m",
            )

            return token

        except Exception as e:
            logger.error(
                "eks_oidc_token_failed", cluster=self.cluster_config.name, error=str(e)
            )
            raise

    async def _assume_role(self) -> boto3.Session:
        """Assume Role using STS"""
        try:
            sts_client = self._session.client(
                "sts", region_name=self.cluster_config.region
            )

            response = sts_client.assume_role(
                RoleArn=self.cluster_config.role_arn,
                RoleSessionName=f"chaos-mesh-mcp-{int(time.time())}",
                DurationSeconds=3600,
            )

            credentials = response["Credentials"]

            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=self.cluster_config.region,
            )

            logger.info(
                "iam_role_assumed",
                role_arn=self.cluster_config.role_arn,
                session_name=f"chaos-mesh-mcp-{int(time.time())}",
            )

            return session

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "AccessDenied":
                raise Exception(
                    f"Does not have enough assume role role '{self.cluster_config.role_arn}'."
                )
            else:
                raise Exception(f"Failed to get assume role: {str(e)}")

    def _generate_eks_token(self, session: boto3.Session) -> str:
        """EKS token generation (same with aws eks get-token)"""
        try:
            sts_client = session.client("sts", region_name=self.cluster_config.region)

            url = f"https://sts.{self.cluster_config.region}.amazonaws.com/"

            params = {
                "Action": "GetCallerIdentity",
                "Version": "2011-06-15",
                "X-Amz-Expires": "60",
            }

            headers = {"x-k8s-aws-id": self.cluster_config.name}

            request = AWSRequest(method="GET", url=url, params=params, headers=headers)

            SigV4Auth(
                sts_client._get_credentials(), "sts", self.cluster_config.region
            ).add_auth(request)

            presigned_url = request.url

            token = (
                base64.urlsafe_b64encode(presigned_url.encode("utf-8"))
                .decode("utf-8")
                .rstrip("=")
            )

            return f"k8s-aws-v1.{token}"

        except Exception as e:
            logger.error("eks_token_generation_failed", error=str(e))
            raise Exception(f"Failed to generate eks token: {str(e)}")

    async def create_k8s_client(self) -> client.ApiClient:
        """Kubernetes client generation"""
        try:
            import json
            import subprocess

            cmd = [
                "aws",
                "eks",
                "get-token",
                "--cluster-name",
                self.cluster_config.name,
                "--region",
                self.cluster_config.region,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            token_data = json.loads(result.stdout)
            token = token_data["status"]["token"]

            configuration = client.Configuration()
            configuration.host = self.cluster_config.endpoint
            configuration.api_key = {"authorization": token}
            configuration.api_key_prefix = {"authorization": "Bearer"}

            if self.cluster_info_cache and "ca_data" in self.cluster_info_cache:
                import tempfile

                ca_cert_data = base64.b64decode(self.cluster_info_cache["ca_data"])

                with tempfile.NamedTemporaryFile(
                    mode="wb", delete=False, suffix=".pem"
                ) as f:
                    f.write(ca_cert_data)
                    configuration.ssl_ca_cert = f.name
            else:
                configuration.verify_ssl = False
                logger.warning(
                    "ca_cert_not_available", cluster=self.cluster_config.name
                )

            k8s_client = client.ApiClient(configuration)

            try:
                await self._test_connection(k8s_client)
                logger.info(
                    "k8s_connection_test_passed", cluster=self.cluster_config.name
                )
            except client.ApiException as e:
                if e.status == 401:
                    logger.warning(
                        "k8s_connection_unauthorized",
                        cluster=self.cluster_config.name,
                        message="Trouble with RBAC permission management.",
                    )
                elif e.status == 403:
                    logger.warning(
                        "k8s_connection_forbidden",
                        cluster=self.cluster_config.name,
                        message="Kubernetes API access forbidden.",
                    )
                else:
                    raise
            except Exception as e:
                logger.error(
                    "k8s_connection_test_failed",
                    cluster=self.cluster_config.name,
                    error=str(e),
                )
                raise Exception(f"Kubernetes connection failed: {str(e)}")

            return k8s_client

        except Exception as e:
            logger.error(
                "k8s_client_creation_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise

    async def _test_connection(self, k8s_client: client.ApiClient) -> None:
        """Kubernetes Connection Test"""
        try:
            core_v1 = client.CoreV1Api(k8s_client)

            namespaces = core_v1.list_namespace(limit=1)

            try:
                namespaces = core_v1.list_namespace(limit=1)
                permissions = "cluster-admin" if namespaces.items else "limited"
            except client.ApiException as e:
                if e.status == 403:
                    permissions = "forbidden"
                else:
                    permissions = "unknown"

            logger.info(
                "k8s_connection_test_success",
                cluster=self.cluster_config.name,
                namespaces_count=len(namespaces.items),
                permissions=permissions,
            )

        except Exception as e:
            logger.error(
                "k8s_connection_test_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise Exception(f"Kubernetes connection test failed: {str(e)}")

    async def refresh_token(self) -> str:
        """Force refresh EKS OIDC token"""
        return await self.get_token(force_refresh=True)

    def get_cluster_info(self) -> Optional[Dict]:
        """Get cached cluster information"""
        return self.cluster_info_cache.copy() if self.cluster_info_cache else None

    async def validate_permissions(self) -> Dict[str, bool]:
        """Validate Kubernetes permissions"""
        try:
            k8s_client = await self.create_k8s_client()

            permissions = {
                "list_namespaces": False,
                "create_podchaos": False,
                "create_networkchaos": False,
                "create_stresschaos": False,
                "list_pods": False,
            }

            try:
                core_v1 = client.CoreV1Api(k8s_client)
                core_v1.list_namespace(limit=1)
                permissions["list_namespaces"] = True
            except:
                pass

            try:
                core_v1.list_pod_for_all_namespaces(limit=1)
                permissions["list_pods"] = True
            except:
                pass

            try:
                custom_api = client.CustomObjectsApi(k8s_client)

                try:
                    custom_api.list_cluster_custom_object(
                        group="chaos-mesh.org",
                        version="v1alpha1",
                        plural="podchaos",
                        limit=1,
                    )
                    permissions["create_podchaos"] = True
                except:
                    pass

                try:
                    custom_api.list_cluster_custom_object(
                        group="chaos-mesh.org",
                        version="v1alpha1",
                        plural="networkchaos",
                        limit=1,
                    )
                    permissions["create_networkchaos"] = True
                except:
                    pass

                try:
                    custom_api.list_cluster_custom_object(
                        group="chaos-mesh.org",
                        version="v1alpha1",
                        plural="stresschaos",
                        limit=1,
                    )
                    permissions["create_stresschaos"] = True
                except:
                    pass

            except:
                pass

            logger.info(
                "permissions_validated",
                cluster=self.cluster_config.name,
                permissions=permissions,
            )

            return permissions

        except Exception as e:
            logger.error(
                "permission_validation_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            return {}

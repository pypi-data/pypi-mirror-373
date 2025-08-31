"""OIDC authentication client"""

import base64
import json
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import jwt
import requests
from kubernetes import client

from utils.config import ClusterConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class OIDCClient:
    """OIDC authentication client"""

    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config
        self.oidc_config: Optional[Dict[str, Any]] = None
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[float] = None

    async def initialize(self) -> None:
        """Initialize OIDC client"""
        logger.info(
            "initializing_oidc_client",
            cluster=self.cluster_config.name,
            issuer=self.cluster_config.oidc_issuer_url,
        )

        # Get OIDC configuration
        await self._get_oidc_config()

        # Get initial token
        await self._authenticate()

        logger.info(
            "oidc_client_initialized",
            cluster=self.cluster_config.name,
            issuer=self.cluster_config.oidc_issuer_url,
        )

    async def _get_oidc_config(self) -> None:
        """Get OIDC configuration"""
        try:
            config_url = f"{self.cluster_config.oidc_issuer_url}/.well-known/openid_configuration"
            response = requests.get(config_url, timeout=30)
            response.raise_for_status()

            self.oidc_config = response.json()

            logger.info(
                "oidc_config_retrieved",
                cluster=self.cluster_config.name,
                authorization_endpoint=self.oidc_config.get("authorization_endpoint"),
                token_endpoint=self.oidc_config.get("token_endpoint"),
            )

        except Exception as e:
            logger.error(
                "oidc_config_retrieval_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise Exception(f"Failed to get OIDC configuration: {str(e)}")

    async def _authenticate(self) -> None:
        """Authenticate using OIDC"""
        try:
            if not self.oidc_config:
                raise Exception("OIDC configuration not available")

            # Use client credentials flow
            token_endpoint = self.oidc_config["token_endpoint"]

            data = {
                "grant_type": "client_credentials",
                "client_id": self.cluster_config.oidc_client_id,
                "client_secret": self.cluster_config.oidc_client_secret,
                "scope": "openid profile email",
            }

            response = requests.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()

            token_data = response.json()

            self.token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = time.time() + expires_in

            logger.info(
                "oidc_authentication_successful",
                cluster=self.cluster_config.name,
                expires_in=expires_in,
            )

        except Exception as e:
            logger.error(
                "oidc_authentication_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise Exception(f"OIDC authentication failed: {str(e)}")

    async def refresh_access_token(self) -> None:
        """Refresh access token"""
        if (
            self.token_expiry and time.time() < self.token_expiry - 300
        ):  # 5 minutes buffer
            return

        try:
            if not self.refresh_token or not self.oidc_config:
                # Re-authenticate if no refresh token
                await self._authenticate()
                return

            token_endpoint = self.oidc_config["token_endpoint"]

            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.cluster_config.oidc_client_id,
                "client_secret": self.cluster_config.oidc_client_secret,
            }

            response = requests.post(
                token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()

            token_data = response.json()

            self.token = token_data["access_token"]
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]

            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = time.time() + expires_in

            logger.info(
                "oidc_token_refreshed",
                cluster=self.cluster_config.name,
                expires_in=expires_in,
            )

        except Exception as e:
            logger.error(
                "oidc_token_refresh_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            # Fall back to re-authentication
            await self._authenticate()

    async def create_k8s_client(self) -> client.ApiClient:
        """Create Kubernetes client"""
        try:
            # Ensure token is valid
            await self.refresh_access_token()

            if not self.token:
                raise Exception("No valid token available")

            # Create configuration
            configuration = client.Configuration()
            configuration.host = self.cluster_config.endpoint
            configuration.api_key = {"authorization": f"Bearer {self.token}"}
            configuration.api_key_prefix = {"authorization": "Bearer"}

            # Set certificate authority if provided
            if self.cluster_config.certificate_authority_data:
                ca_cert = base64.b64decode(
                    self.cluster_config.certificate_authority_data
                )
                with open("/tmp/ca.crt", "wb") as f:
                    f.write(ca_cert)
                configuration.ssl_ca_cert = "/tmp/ca.crt"

            # Create client
            k8s_client = client.ApiClient(configuration)

            logger.info(
                "k8s_client_created",
                cluster=self.cluster_config.name,
                endpoint=self.cluster_config.endpoint,
            )

            return k8s_client

        except Exception as e:
            logger.error(
                "k8s_client_creation_failed",
                cluster=self.cluster_config.name,
                error=str(e),
            )
            raise Exception(f"Failed to create Kubernetes client: {str(e)}")

    def decode_token(self) -> Optional[Dict[str, Any]]:
        """Decode JWT token"""
        if not self.token:
            return None

        try:
            # Decode without verification for inspection
            decoded = jwt.decode(self.token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            logger.error("token_decode_failed", error=str(e))
            return None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information from token"""
        decoded = self.decode_token()
        if not decoded:
            return None

        return {
            "sub": decoded.get("sub"),
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "groups": decoded.get("groups", []),
            "exp": decoded.get("exp"),
            "iat": decoded.get("iat"),
        }

    def is_token_valid(self) -> bool:
        """Check if token is valid"""
        if not self.token or not self.token_expiry:
            return False
        return time.time() < self.token_expiry - 300  # 5 minutes buffer

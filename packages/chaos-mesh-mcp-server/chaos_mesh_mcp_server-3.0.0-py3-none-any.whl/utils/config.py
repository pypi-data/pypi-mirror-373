"""EKS OIDC-based configuration management module"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class ClusterConfig(BaseModel):
    """EKS cluster configuration"""

    name: str
    region: str
    role_arn: Optional[str] = None  # IAM Role ARN (optional)
    endpoint: Optional[str] = None  # EKS API endpoint (auto-loaded)
    oidc_issuer: Optional[str] = None  # OIDC issuer (auto-loaded)
    namespace_whitelist: List[str] = Field(default_factory=list)
    namespace_blacklist: List[str] = Field(
        default_factory=lambda: ["kube-system", "kube-public", "kube-node-lease"]
    )


class SecurityConfig(BaseModel):
    """Security configuration"""

    max_concurrent_experiments: int = 5
    max_experiment_duration: int = 3600  # 1 hour
    require_approval: bool = True
    audit_log_enabled: bool = True
    protected_namespaces: List[str] = Field(
        default_factory=lambda: [
            "kube-system",
            "kube-public",
            "kube-node-lease",
            "default",
            "chaos-mesh",
        ]
    )
    token_refresh_interval: int = 840  # 14 minutes (EKS token is valid for 15 minutes)


class ChaosConfig(BaseModel):
    """Chaos experiment configuration"""

    default_duration: str = "60s"
    cleanup_timeout: int = 300  # 5 minutes
    monitoring_interval: int = 10  # 10 seconds
    auto_rollback: bool = True
    supported_chaos_types: List[str] = Field(
        default_factory=lambda: [
            "pod_chaos",
            "network_chaos",
            "stress_chaos",
            "time_chaos",
            "io_chaos",
        ]
    )


class AWSConfig(BaseModel):
    """AWS configuration"""

    region: str = "us-west-2"
    profile: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AWSConfig":
        """Load AWS configuration from environment variables"""
        return cls(
            region=os.getenv("AWS_DEFAULT_REGION", "us-west-2"),
            profile=os.getenv("AWS_PROFILE"),
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            session_token=os.getenv("AWS_SESSION_TOKEN"),
        )


class Config(BaseModel):
    """Overall configuration"""

    # Server configuration
    server_host: str = Field(default="localhost")
    server_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    # AWS configuration
    aws: AWSConfig = Field(default_factory=AWSConfig.from_env)

    # Cluster configuration
    clusters: Dict[str, ClusterConfig] = Field(default_factory=dict)

    # Security configuration
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # Chaos configuration
    chaos: ChaosConfig = Field(default_factory=ChaosConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        config = cls()

        # AWS configuration
        config.aws = AWSConfig.from_env()

        # Load cluster configuration from environment variables
        cluster_names = os.getenv("EKS_CLUSTER_NAMES", "").split(",")
        for cluster_name in cluster_names:
            cluster_name = cluster_name.strip()
            if cluster_name:
                # Generate environment variable key (uppercase, hyphens to underscores)
                env_prefix = cluster_name.upper().replace("-", "_")

                cluster_config = ClusterConfig(
                    name=cluster_name,
                    region=os.getenv(f"{env_prefix}_REGION", config.aws.region),
                    role_arn=os.getenv(f"{env_prefix}_ROLE_ARN"),
                    endpoint=os.getenv(
                        f"{env_prefix}_ENDPOINT"
                    ),  # Optional (auto-loaded)
                    oidc_issuer=os.getenv(
                        f"{env_prefix}_OIDC_ISSUER"
                    ),  # Optional (auto-loaded)
                )

                # Namespace whitelist/blacklist
                whitelist = os.getenv(f"{env_prefix}_NAMESPACE_WHITELIST", "")
                if whitelist:
                    cluster_config.namespace_whitelist = [
                        ns.strip() for ns in whitelist.split(",")
                    ]

                blacklist = os.getenv(f"{env_prefix}_NAMESPACE_BLACKLIST", "")
                if blacklist:
                    cluster_config.namespace_blacklist.extend(
                        [ns.strip() for ns in blacklist.split(",")]
                    )

                config.clusters[cluster_name] = cluster_config

        # Server configuration
        config.server_host = os.getenv("SERVER_HOST", config.server_host)
        config.server_port = int(os.getenv("SERVER_PORT", str(config.server_port)))
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)

        # Security configuration
        config.security.max_concurrent_experiments = int(
            os.getenv(
                "MAX_CONCURRENT_EXPERIMENTS",
                str(config.security.max_concurrent_experiments),
            )
        )
        config.security.max_experiment_duration = int(
            os.getenv(
                "MAX_EXPERIMENT_DURATION", str(config.security.max_experiment_duration)
            )
        )
        config.security.require_approval = (
            os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"
        )
        config.security.audit_log_enabled = (
            os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
        )

        # Chaos configuration
        config.chaos.default_duration = os.getenv(
            "DEFAULT_EXPERIMENT_DURATION", config.chaos.default_duration
        )
        config.chaos.auto_rollback = (
            os.getenv("AUTO_ROLLBACK", "true").lower() == "true"
        )

        return config

    def validate_config(self) -> List[str]:
        """Validate configuration"""
        errors = []

        # Cluster configuration validation (changed to optional)
        # Start without clusters initially and allow dynamic connection

        for cluster_name, cluster_config in self.clusters.items():
            if not cluster_config.region:
                errors.append(f"Region for cluster '{cluster_name}' is not configured.")

        # AWS configuration validation
        if not self.aws.region:
            errors.append("AWS region is not configured.")

        # Security configuration validation
        if self.security.max_concurrent_experiments <= 0:
            errors.append("max_concurrent_experiments must be greater than 0.")

        if self.security.max_experiment_duration <= 0:
            errors.append("max_experiment_duration must be greater than 0.")

        return errors

    def get_cluster_config(self, cluster_name: str) -> Optional[ClusterConfig]:
        """Get cluster configuration"""
        return self.clusters.get(cluster_name)

    def add_cluster_config(self, cluster_config: ClusterConfig) -> None:
        """Add cluster configuration"""
        self.clusters[cluster_config.name] = cluster_config

    def remove_cluster_config(self, cluster_name: str) -> bool:
        """Remove cluster configuration"""
        if cluster_name in self.clusters:
            del self.clusters[cluster_name]
            return True
        return False


# Global configuration instance
settings = Config.from_env()

# Configuration validation
config_errors = settings.validate_config()
if config_errors:
    import sys

    # Cannot use stdout in MCP server, so output to stderr and raise exception
    error_message = (
        "Configuration errors:\n"
        + "\n".join([f"  - {error}" for error in config_errors])
        + "\n\nPlease check environment variables and try again."
    )
    print(error_message, file=sys.stderr)
    raise RuntimeError(f"Configuration validation failed: {'; '.join(config_errors)}")

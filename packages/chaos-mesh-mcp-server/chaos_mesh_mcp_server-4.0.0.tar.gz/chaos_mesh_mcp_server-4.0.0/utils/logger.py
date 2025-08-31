"""Logging configuration module"""

import sys
from typing import Any, Dict

import structlog

from utils.config import settings


def setup_logging() -> None:
    """Setup structured logging"""

    # Configure log processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Color output for development environment
    if settings.log_level == "DEBUG":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level.upper(), 20)
        ),
        logger_factory=structlog.WriteLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Create logger instance"""
    return structlog.get_logger(name)


class AuditLogger:
    """Dedicated audit logger"""

    def __init__(self):
        self.logger = get_logger("audit")

    def log_experiment_created(
        self,
        cluster: str,
        experiment_type: str,
        experiment_name: str,
        target: Dict[str, Any],
    ) -> None:
        """Log experiment creation"""
        self.logger.info(
            "chaos_experiment_created",
            cluster=cluster,
            experiment_type=experiment_type,
            experiment_name=experiment_name,
            target=target,
            action="CREATE_EXPERIMENT",
        )

    def log_experiment_started(
        self,
        cluster: str,
        experiment_name: str,
    ) -> None:
        """Log experiment start"""
        self.logger.info(
            "chaos_experiment_started",
            cluster=cluster,
            experiment_name=experiment_name,
            action="START_EXPERIMENT",
        )

    def log_experiment_stopped(
        self,
        cluster: str,
        experiment_name: str,
        reason: str = "user_request",
    ) -> None:
        """Log experiment stop"""
        self.logger.info(
            "chaos_experiment_stopped",
            cluster=cluster,
            experiment_name=experiment_name,
            reason=reason,
            action="STOP_EXPERIMENT",
        )

    def log_security_violation(self, action: str, resource: str, reason: str) -> None:
        """Log security violation"""
        self.logger.warning(
            "security_violation",
            action=action,
            resource=resource,
            reason=reason,
        )


# Global audit logger instance
audit_logger = AuditLogger()

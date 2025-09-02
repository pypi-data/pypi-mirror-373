"""Token configuration utilities for BithumanRuntime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from loguru import logger


@dataclass
class TokenRequestConfig:
    """Configuration for token requests."""

    api_url: str
    api_secret: str
    fingerprint: Optional[str] = None
    client_id: Optional[str] = None
    figure_id: Optional[str] = None
    transaction_id: Optional[str] = None
    runtime_model_hash: Optional[str] = None
    tags: Optional[str] = None
    insecure: bool = False
    timeout: float = 30.0

    @classmethod
    def from_namespace(cls, namespace) -> "TokenRequestConfig":
        """Create a TokenRequestConfig from an argparse.Namespace object.

        Args:
            namespace: An argparse.Namespace object containing the configuration

        Returns:
            TokenRequestConfig: A new TokenRequestConfig instance
        """
        # Get required parameters
        api_url = getattr(namespace, "api_url", None)
        api_secret = getattr(namespace, "api_secret", None)

        if not api_url or not api_secret:
            raise ValueError("api_url and api_secret are required parameters")

        # Get optional parameters with defaults
        return cls(
            api_url=api_url,
            api_secret=api_secret,
            fingerprint=getattr(namespace, "fingerprint", None),
            client_id=getattr(namespace, "client_id", None),
            figure_id=getattr(namespace, "figure_id", None),
            transaction_id=getattr(namespace, "transaction_id", None),
            runtime_model_hash=getattr(namespace, "runtime_model_hash", None),
            tags=getattr(namespace, "tags", None),
            insecure=getattr(namespace, "insecure", False),
            timeout=getattr(namespace, "timeout", 30.0),
        )


def prepare_request_data(
    fingerprint: str, config: TokenRequestConfig
) -> Dict[str, Any]:
    """Prepare request data for token request."""
    data = {"fingerprint": fingerprint}

    if config.client_id:
        data["client_id"] = config.client_id

    if config.figure_id:
        data["figure_id"] = config.figure_id

    if config.runtime_model_hash:
        data["runtime_model_hash"] = config.runtime_model_hash

    if config.transaction_id:
        data["transaction_id"] = config.transaction_id

    if config.tags:
        data["tags"] = config.tags

    return data


def prepare_headers(config: TokenRequestConfig) -> Dict[str, str]:
    """Prepare headers for token request."""
    headers = {"Content-Type": "application/json"}

    if config.api_secret:
        headers["api-secret"] = config.api_secret
        logger.debug("API secret provided")
    else:
        logger.warning("No api-secret provided, authentication may fail")

    return headers


def log_request_debug(headers: Dict[str, str], data: Dict[str, Any], api_url: str):
    """Log request debug information."""
    debug_headers = headers.copy()
    if "api-secret" in debug_headers:
        secret_val = debug_headers["api-secret"]
        debug_headers["api-secret"] = (
            secret_val[:4] + "..." + secret_val[-4:] if len(secret_val) > 8 else "***"
        )

    logger.debug(f"Request headers: {debug_headers}")
    logger.debug(f"Request data: {data}")
    logger.debug(f"Using API URL: {api_url}")


class TokenRequestError(Exception):
    """Custom exception for token request errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

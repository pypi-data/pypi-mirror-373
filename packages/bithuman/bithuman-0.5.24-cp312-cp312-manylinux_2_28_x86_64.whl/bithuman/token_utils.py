"""Token utilities for BithumanRuntime."""
from __future__ import annotations

import asyncio
import datetime
import threading
import time
from typing import Any, Callable, Dict, Optional, Union

import aiohttp
import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bithuman.token_config import (
    TokenRequestConfig,
    TokenRequestError,
    prepare_headers,
    prepare_request_data,
)


def _prepare_session() -> requests.Session:
    """Prepare requests session with retry capability."""
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


# log_request_debug is now imported from token_config


def _parse_response(
    response_data: Dict[str, Any], status_code: int, response_text: str
) -> str:
    """Parse the response data and extract the token.

    Args:
        response_data: The parsed JSON response data
        status_code: The HTTP status code
        response_text: The raw response text

    Returns:
        str: The extracted token

    Raises:
        TokenRequestError: If the response is invalid or contains an error
    """
    if status_code == 200:
        if response_data.get("status") == "success" and "data" in response_data:
            token = response_data["data"]["token"]
            logger.debug("Successfully obtained token from API")
            return token
        else:
            error_msg = f"API returned error: {response_data}"
            logger.error(error_msg)
            raise TokenRequestError(error_msg, status_code, response_text)
    else:
        error_msg = f"Failed to get token. Status code: {status_code}, Response: {response_text}"
        logger.error(error_msg)
        raise TokenRequestError(error_msg, status_code, response_text)


def _handle_request_error(e: Exception) -> None:
    """Handle different types of request errors.

    Args:
        e: The exception that occurred

    Raises:
        TokenRequestError: With appropriate error message
    """
    if isinstance(e, requests.exceptions.SSLError):
        error_msg = f"SSL Error requesting token: {e}"
        logger.error(error_msg)
        logger.error(
            "This might be fixed by using the --insecure flag if your environment has SSL issues."
        )
    elif isinstance(e, requests.exceptions.ConnectionError):
        error_msg = f"Connection Error requesting token: {e}"
        logger.error(error_msg)
        logger.error("Please check your network connection and the API URL.")
    elif isinstance(e, requests.exceptions.Timeout):
        error_msg = f"Timeout Error requesting token: {e}"
        logger.error(error_msg)
        logger.error("The API server took too long to respond.")
    else:
        error_msg = f"Error requesting token: {e}"
        logger.error(error_msg)
        logger.error(f"Exception type: {type(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")

    raise TokenRequestError(error_msg)


def _prepare_request(
    fingerprint: str,
    config: Union[TokenRequestConfig, Any],
    model_hash: Optional[str] = None,
) -> tuple[Dict[str, Any], Dict[str, str]]:
    """Prepare request data and headers for token request.

    Args:
        fingerprint: The hardware fingerprint string
        config: The TokenRequestConfig for token requests or argparse.Namespace object
        model_hash: Optional model hash string (if already calculated)

    Returns:
        tuple[Dict[str, Any], Dict[str, str]]: A tuple containing (request_data, headers)
    """
    logger.debug("Preparing token request data and headers")
    
    # Convert namespace to TokenRequestConfig if needed
    if not isinstance(config, TokenRequestConfig):
        logger.debug("Converting namespace to TokenRequestConfig")
        config = TokenRequestConfig.from_namespace(config)

    # Set model hash if provided
    if model_hash:
        config.runtime_model_hash = model_hash
        logger.debug(f"Model hash set in config: {model_hash[:5]}...{model_hash[-5:] if len(model_hash) > 10 else '***'}")

    # Log config details (with masking)
    logger.debug(f"API URL: {config.api_url}")
    logger.debug(f"API secret: {config.api_secret[:5]}...{config.api_secret[-5:] if len(config.api_secret) > 10 else '***'}")
    logger.debug(f"Fingerprint: {fingerprint[:5]}...{fingerprint[-5:] if len(fingerprint) > 10 else '***'}")
    logger.debug(f"Runtime model hash: {config.runtime_model_hash[:5]}...{config.runtime_model_hash[-5:] if config.runtime_model_hash and len(config.runtime_model_hash) > 10 else '***'}")
    logger.debug(f"Tags: {config.tags}")
    logger.debug(f"Insecure: {config.insecure}")
    logger.debug(f"Timeout: {config.timeout}")

    # Prepare request data
    data = prepare_request_data(fingerprint, config)
    logger.debug(f"Request data keys: {list(data.keys())}")

    # Prepare headers
    headers = prepare_headers(config)
    logger.debug(f"Request headers: {list(headers.keys())}")

    return data, headers


def request_token_sync(config: TokenRequestConfig) -> str:
    """Synchronous version of token request.

    Args:
        config: The TokenRequestConfig for token requests

    Returns:
        str: The token string if successful
    """
    try:
        # Extract fingerprint if runtime is an object
        fingerprint = config.fingerprint

        # Prepare request data and headers
        data, headers = _prepare_request(fingerprint, config, config.runtime_model_hash)

        # Create session with retry capability
        session = _prepare_session()

        # Make request
        response = session.post(
            config.api_url, json=data, headers=headers, timeout=config.timeout
        )

        # Log response details
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response body: {response.text}")

        # Parse response
        return _parse_response(response.json(), response.status_code, response.text)

    except Exception as e:
        _handle_request_error(e)


async def request_token_async(config: TokenRequestConfig) -> str:
    """Asynchronous version of token request.

    Args:
        config: The TokenRequestConfig for token requests

    Returns:
        str: The token string if successful
    """
    try:
        # Extract fingerprint if runtime is an object
        fingerprint = config.fingerprint

        # Prepare request data and headers
        data, headers = _prepare_request(fingerprint, config, config.runtime_model_hash)

        # Configure SSL context if needed
        ssl_context = None if not config.insecure else False

        # Make request with retry logic
        for attempt in range(3):  # Try up to 3 times
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        config.api_url,
                        json=data,
                        headers=headers,
                        ssl=ssl_context,
                        timeout=config.timeout,
                    ) as response:
                        # Log response details
                        logger.debug(f"Response status: {response.status}")
                        logger.debug(f"Response headers: {dict(response.headers)}")
                        response_text = await response.text()
                        logger.debug(f"Response body: {response_text}")

                        # Parse response
                        return _parse_response(
                            await response.json(), response.status, response_text
                        )

            except aiohttp.ClientError as e:
                if attempt == 2:  # Last attempt
                    error_msg = f"Failed after 3 attempts: {e}"
                    logger.error(error_msg)
                    raise TokenRequestError(error_msg)
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)  # Wait before retrying

    except Exception as e:
        _handle_request_error(e)


async def token_refresh_worker_async(
    config: TokenRequestConfig,
    stop_event: asyncio.Event,
    refresh_interval: int = 60,
    error_retry_interval: int = 5,
    on_token_refresh: Optional[Callable[[str], None]] = None,
) -> None:
    """Asynchronous worker that periodically refreshes the token.

    This function handles periodic token refresh in an asynchronous context.
    It uses the provided config to request new tokens and calls the on_token_refresh
    callback when a new token is obtained. The worker will continue running until
    the stop_event is set.

    Args:
        config: Configuration for token requests containing API credentials and parameters.
        stop_event: Event to signal when the worker should stop.
        refresh_interval: Time in seconds between refresh attempts (default: 60).
        error_retry_interval: Time to wait after an error before retrying (default: 5).
        on_token_refresh: Callback function to process the new token when refreshed.
    """
    if not config.api_secret:
        logger.warning("No API secret provided, skipping token refresh")
        return

    if not config.runtime_model_hash:
        logger.warning("Failed to get model hash, skipping token refresh")
        return

    while not stop_event.is_set():
        try:
            # Request a new token using the config
            token = await request_token_async(config)
            if token:
                # Call the callback with the new token if provided
                if on_token_refresh:
                    on_token_refresh(token)
                logger.debug(
                    f"Token refreshed successfully at {datetime.datetime.now()}"
                )
            else:
                logger.error("Failed to refresh token: request returned empty token")

            # Wait for refresh_interval seconds before the next refresh,
            # checking for stop event every second
            for _ in range(refresh_interval):
                if stop_event.is_set():
                    break
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in token refresh worker: {e}")
            # Wait a shorter interval before retrying after an error
            await asyncio.sleep(error_retry_interval)


def token_refresh_worker_sync(
    config: TokenRequestConfig,
    stop_event: threading.Event,
    refresh_interval: int = 60,
    error_retry_interval: int = 5,
    on_token_refresh: Optional[Callable[[str], None]] = None,
) -> None:
    """Synchronous worker that periodically refreshes the token.

    This function handles periodic token refresh in a synchronous context.
    It uses the provided config to request new tokens and calls the on_token_refresh
    callback when a new token is obtained. The worker will continue running until
    the stop_event is set.

    Args:
        config: Configuration for token requests containing API credentials and parameters.
        stop_event: Event to signal when the worker should stop.
        refresh_interval: Time in seconds between refresh attempts (default: 60).
        error_retry_interval: Time to wait after an error before retrying (default: 5).
        on_token_refresh: Callback function to process the new token when refreshed.
    """
    while not stop_event.is_set():
        try:
            # Request a new token using the config
            token = request_token_sync(config)
            if token:
                # Call the callback with the new token if provided
                if on_token_refresh:
                    on_token_refresh(token)
                logger.debug(
                    f"Token refreshed successfully at {datetime.datetime.now()}"
                )
            else:
                logger.error("Failed to refresh token: request returned empty token")

            # Wait for refresh_interval seconds before the next refresh,
            # checking for stop event every second
            for _ in range(refresh_interval):
                if stop_event.is_set():
                    break
                time.sleep(1)

        except Exception as e:
            logger.error(f"Error in token refresh worker: {e}")
            # Wait a shorter interval before retrying after an error
            time.sleep(error_retry_interval)

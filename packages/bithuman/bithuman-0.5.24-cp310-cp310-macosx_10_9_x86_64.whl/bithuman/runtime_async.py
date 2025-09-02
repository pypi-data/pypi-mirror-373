"""Asynchronous wrapper for Bithuman Runtime."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import AsyncIterator, Optional, Union

from loguru import logger

from .api import VideoControl, VideoFrame
from .runtime import Bithuman, BufferEmptyCallback
from .utils import calculate_file_hash


class AsyncBithuman(Bithuman):
    """Asynchronous wrapper for Bithuman Runtime.

    This class wraps the synchronous BithumanRuntime to provide an asynchronous interface.
    It runs the runtime in a separate thread to avoid blocking the asyncio event loop.
    """

    def __init__(
        self,
        *,
        model_path: Optional[str] = None,
        token: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_url: str = "https://auth.api.bithuman.ai/v1/runtime-tokens/request",
        tags: Optional[str] = "bithuman",
        insecure: bool = True,
        input_buffer_size: int = 0,
        output_buffer_size: int = 5,
        load_model: bool = False,
        verbose: Optional[bool] = None,
    ) -> None:
        """Initialize the async runtime with a BithumanRuntime instance.

        Args:
            model_path: The path to the avatar model.
            token: The token for the Bithuman Runtime. Either token or api_secret must be provided.
            api_secret: API Secret for API authentication. Either token or api_secret must be provided.
            api_url: API endpoint URL for token requests.
            tags: Optional tags for token request.
            insecure: Disable SSL certificate verification (not recommended for production use).
            input_buffer_size: Size of the input buffer.
            output_buffer_size: Size of the output buffer.
            load_model: If True, load the model synchronously.
            verbose: Enable verbose logging for token validation. If None, reads from BITHUMAN_VERBOSE environment variable.
        """
        # Call parent init WITHOUT the model_path parameter
        # This prevents parent's __init__ from calling set_model()
        logger.debug(
            f"Initializing AsyncBithuman with token={token is not None}, api_secret={api_secret is not None}, verbose={verbose}"
        )
        super().__init__(
            input_buffer_size=input_buffer_size,
            token=token,
            model_path=None,  # Important: Pass None here
            api_secret=api_secret,
            api_url=api_url,
            tags=tags,
            insecure=insecure,
            verbose=verbose,
        )

        # Store the model path for later use
        self._model_path = model_path            

        self._model_hash = None

        # Thread management
        self._stop_event = threading.Event()
        self._thread = None

        # Use a standard asyncio.Queue for frames since they're only accessed from async context
        self._frame_queue = asyncio.Queue[Union[VideoFrame, Exception]](
            maxsize=output_buffer_size
        )

        # State
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Token refresh state for async version
        self._stop_refresh_event = asyncio.Event()
        self._refresh_task = None

        if load_model:
            self._initialize_token_sync()
            super().set_model(model_path)

    @classmethod
    async def create(
        cls,
        *,
        model_path: Optional[str] = None,
        token: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_url: str = "https://auth.api.bithuman.ai/v1/runtime-tokens/request",
        tags: Optional[str] = "bithuman",
        insecure: bool = True,
        input_buffer_size: int = 0,
        output_buffer_size: int = 5,
        verbose: Optional[bool] = None,
    ) -> "AsyncBithuman":
        """Create a fully initialized AsyncBithuman instance asynchronously."""
        # Create instance with initial parameters but defer model setting
        instance = cls(
            model_path=None,  # Will set model later
            token=token,
            api_secret=api_secret,
            api_url=api_url,
            tags=tags,
            insecure=insecure,
            input_buffer_size=input_buffer_size,
            output_buffer_size=output_buffer_size,
            verbose=verbose,
        )

        if model_path:
            instance._model_path = model_path
            await instance._initialize_token()
            await instance.set_model(model_path)

        return instance

    async def set_model(self, model_path: str | None = None) -> "AsyncBithuman":
        """Set the avatar model for the runtime.

        Args:
            model_path: The path to the avatar model. If None, uses the model_path provided during initialization.
        """
        # Use the model path provided during initialization if none is provided
        model_path = model_path or self._model_path

        if not model_path:
            logger.error("No model path provided for set_model")
            raise ValueError(
                "Model path must be provided either during initialization or when calling set_model"
            )

        # Store the model path for token requests
        self._model_path = model_path

        # Now run the set_model in the executor and wait for it to finish
        loop = self._loop or asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, super().set_model, model_path)
        except Exception as e:
            logger.error(f"Error in parent set_model: {e}")
            raise

        return self

    async def push_audio(
        self, data: bytes, sample_rate: int, last_chunk: bool = True
    ) -> None:
        """Push audio data to the runtime asynchronously.

        Args:
            data: Audio data in bytes.
            sample_rate: Sample rate of the audio.
            last_chunk: Whether this is the last chunk of the speech.
        """
        control = VideoControl.from_audio(data, sample_rate, last_chunk)
        await self._input_buffer.aput(control)

    async def push(self, control: VideoControl) -> None:
        """Push a VideoControl to the runtime asynchronously.

        Args:
            control: The VideoControl to push.
        """
        await self._input_buffer.aput(control)

    async def flush(self) -> None:
        """Flush the audio buffer, indicating end of speech."""
        await self._input_buffer.aput(VideoControl(end_of_speech=True))

    async def run(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        idle_timeout: float | None = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> AsyncIterator[VideoFrame]:
        """Stream video frames asynchronously.

        Yields:
            VideoFrame objects from the runtime.
        """
        # Start the runtime if not already running
        await self.start(
            out_buffer_empty=out_buffer_empty,
            idle_timeout=idle_timeout,
            loop=loop,
        )

        try:
            while True:
                # Get the next frame from the queue
                item = await self._frame_queue.get()

                # If we got an exception, raise it
                if isinstance(item, Exception):
                    raise item

                # Yield the frame
                yield item

                # Mark the task as done
                self._frame_queue.task_done()

        except asyncio.CancelledError:
            # Stream was cancelled, stop the runtime
            await self.stop()
            raise

    async def _initialize_token(self) -> None:
        """Initialize token by requesting it from the API asynchronously.

        This method is called during initialization or when setting the model if api_secret is provided.
        """
        logger.debug("Starting token initialization process")
        
        if self._token:
            logger.debug("Existing token found, attempting validation")
            try:
                if await self.set_token_async(self._token):
                    logger.debug("Existing token validated successfully")
                    return
            except Exception as e:
                logger.warning(f"Existing token validation failed: {e}")
                logger.debug("Will attempt to request new token using API secret")
            
            logger.warning(
                "Failed to validate token, will request new token using API secret"
            )
        else:
            logger.debug("No existing token found, will request new token using API secret")
            
        if not self._api_secret:
            logger.error("No API secret available for token request")
            raise ValueError("No token or API secret available")
            
        logger.debug("Requesting new token from API")
        try:
            await self.request_token()
            logger.debug("Token request completed successfully")
        except Exception as e:
            logger.error(f"Failed to request token from API: {e}")
            raise

    def _initialize_token_sync(self) -> None:
        if self._token:
            if super().set_token(self._token):
                return
            logger.warning(
                "Failed to validate token, will request new token using API secret"
            )
        super().request_token()

    async def start_token_refresh(self) -> None:
        """Start the token refresh task if API secret is provided.

        This method creates an asynchronous task that periodically refreshes the token
        using the API secret. The task runs in the background and will be stopped when
        the runtime is stopped.
        """
        from .token_config import TokenRequestConfig
        from .token_utils import token_refresh_worker_async

        if not self._api_secret:
            logger.debug("No API secret provided, skipping token refresh")
            return

        # Check if refresh task is already running
        if self._refresh_task and not self._refresh_task.done():
            logger.debug("Token refresh task already running, skipping initialization")
            return

        # Reset the stop event
        self._stop_refresh_event.clear()

        # Get the model hash - this is critical for token requests
        model_hash = None
        if self._model_hash:
            model_hash = self._model_hash

        # Make sure we have a valid model hash
        if not model_hash and self._model_path and Path(self._model_path).is_file():
            try:
                model_hash = calculate_file_hash(self._model_path)
                self._model_hash = model_hash
            except Exception as e:
                logger.error(f"Failed to calculate model hash for token refresh: {e}")
                raise

        if not model_hash:
            logger.warning(
                "No model hash available for token refresh. Token refresh may fail."
            )

        # Create the token config with all required parameters
        config = TokenRequestConfig(
            api_url=self._api_url,
            api_secret=self._api_secret,
            fingerprint=self.fingerprint,
            runtime_model_hash=model_hash,  # Explicitly include model hash
            tags=self._tags,
            insecure=self._insecure,
        )

        # Create and start the refresh task
        self._refresh_task = asyncio.create_task(
            token_refresh_worker_async(
                config,
                self._stop_refresh_event,
                on_token_refresh=self._on_token_refresh,
            )
        )

    def _on_token_refresh(self, token: str) -> None:
        """Handle newly refreshed token.

        This callback is called when the token refresh worker obtains a new token.
        It updates the internal token and validates it.

        Args:
            token: The new token to be set.
        """
        logger.debug("Token refresh callback called")
        logger.debug(f"New token received: {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
        
        try:
            # Store the token
            self._token = token
            logger.debug("Token stored in instance")
            
            # Validate and set the token
            logger.debug("Attempting to validate refreshed token")
            self.set_token(token)
            logger.debug("Token refresh complete - new token validated and set")
        except Exception as e:
            logger.error(f"Failed to validate/set refreshed token: {e}")
            logger.error(f"Token validation failed for refreshed token: {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
            # Don't re-raise here as this is a callback, just log the error

    async def start(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        idle_timeout: float | None = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """Start the runtime thread."""
        if self._running:
            logger.debug("Runtime already running, skipping start")
            return

        # Store the current event loop
        self._loop = loop or asyncio.get_running_loop()
        self._input_buffer.set_loop(self._loop)

        # Clear the stop event
        self._stop_event.clear()

        # Start token refresh if api_secret is provided
        if self._api_secret:
            await self.start_token_refresh()

        # Start the runtime thread
        self._running = True
        self._thread = threading.Thread(
            target=self._frame_producer,
            kwargs={"out_buffer_empty": out_buffer_empty, "idle_timeout": idle_timeout},
        )
        self._thread.daemon = True
        self._thread.start()

    async def stop(self) -> None:
        """Stop the runtime thread and token refresh task."""
        if not self._running:
            return

        # Set the stop event
        self._stop_event.set()

        # Stop token refresh task if running
        if self._api_secret and self._refresh_task and not self._refresh_task.done():
            logger.debug("Stopping token refresh task...")
            self._stop_refresh_event.set()
            try:
                await asyncio.wait_for(self._refresh_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Token refresh task did not complete in time")
            self._refresh_task = None

        # Wait for the thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        # Reset state
        self._running = False

    def _frame_producer(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        idle_timeout: float | None = None,
    ) -> None:
        """Run the runtime in a separate thread and produce frames."""
        try:
            # Run the runtime and process frames
            out_buffer_empty = out_buffer_empty or self._frame_queue.empty
            frame_iterator = None
            try:
                frame_iterator = super().run(
                    out_buffer_empty, idle_timeout=idle_timeout
                )
            except Exception as e:
                logger.error(f"Error initializing frame iterator in run(): {e}")
                raise

            if frame_iterator:
                for frame in frame_iterator:
                    if self._stop_event.is_set():
                        break

                    # Put the frame in the frame queue
                    if self._loop and self._loop.is_running():
                        future = asyncio.run_coroutine_threadsafe(
                            self._frame_queue.put(frame), self._loop
                        )
                        # Wait for the frame to be added to the queue
                        future.result()
                    else:
                        break
            else:
                logger.error("Frame iterator is None")

        except Exception as e:
            logger.error(f"Exception in frame producer: {e}")
            # If an exception occurs, put it in the frame queue
            if self._loop and self._loop.is_running():
                try:
                    asyncio.run_coroutine_threadsafe(
                        self._frame_queue.put(e), self._loop
                    ).result()
                except Exception as e2:
                    logger.error(f"Error putting exception in frame queue: {e2}")

    def validate_token(self, token: str, verbose: Optional[bool] = None) -> bool:
        """Validate a token for the Bithuman Runtime asynchronously.

        This pure async implementation validates the token against the hardware fingerprint.

        Args:
            token: The token to validate.
            verbose: Enable verbose logging for token validation. If None, uses instance default.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        return super().validate_token(token, verbose)

    async def load_data_async(self) -> None:
        """Load the workspace and set up related components asynchronously."""
        if self._video_loaded:
            return
        if self.video_graph is None:
            logger.error("Video graph is None. Model may not be set properly.")
            raise ValueError("Video graph is not set. Call set_avatar_model() first.")

        # Run the synchronous load_data in a thread pool
        loop = self._loop or asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, super().load_data)
            self._video_loaded = True
        except Exception as e:
            logger.error(f"Error in load_data: {e}")
            raise

    def set_token(self, token: str, verbose: Optional[bool] = None) -> bool:
        """Set and validate the token for the Bithuman Runtime (synchronous version).

        This method validates the provided token against the hardware fingerprint
        and sets it for subsequent operations if valid.

        Args:
            token: The token to validate and set.
            verbose: Enable verbose logging for token validation. If None, uses instance default.

        Returns:
            bool: True if token is valid and set successfully, False otherwise.

        Raises:
            ValueError: If the token is invalid.
        """
        self._token = token
        return super().set_token(token, verbose)

    async def set_token_async(self, token: str, verbose: Optional[bool] = None) -> bool:
        """Set and validate the token for the Bithuman Runtime asynchronously.

        This method validates the provided token against the hardware fingerprint
        and sets it for subsequent operations if valid.

        Args:
            token: The token to validate and set.
            verbose: Enable verbose logging for token validation. If None, uses instance default.

        Returns:
            bool: True if token is valid and set successfully, False otherwise.

        Raises:
            ValueError: If the token is invalid.
        """
        loop = self._loop or asyncio.get_running_loop()
        self._token = token
        try:
            result = await loop.run_in_executor(None, super().set_token, token, verbose)
            return result
        except Exception as e:
            logger.error(f"Error setting token: {e}")
            raise

    async def request_token(self) -> str:
        """Request a token from the API asynchronously.

        This method requests a token using the API secret and stores it
        in the instance. It also sets the token for the runtime if successful.

        Returns:
            The obtained token string

        Raises:
            ValueError: If API secret or model path is not provided
        """
        from .token_config import TokenRequestConfig
        from .token_utils import request_token_async

        logger.debug("Starting token request process")
        
        if not self._api_secret:
            logger.error("API secret is required for token request")
            raise ValueError("API secret is required for token request")

        if not self._model_path:
            logger.error("Model path is required for token request")
            raise ValueError("Model path is required for token request")

        logger.debug(f"Model path: {self._model_path}")
        logger.debug(f"API URL: {self._api_url}")
        logger.debug(f"API secret: {self._api_secret[:5]}...{self._api_secret[-5:] if len(self._api_secret) > 10 else '***'}")

        # Calculate model hash using our public method
        model_hash = None
        if self._model_hash:
            model_hash = self._model_hash
            logger.debug(f"Using cached model hash: {model_hash[:5]}...{model_hash[-5:] if len(model_hash) > 10 else '***'}")
        else:
            if Path(self._model_path).is_file():
                try:
                    logger.debug("Calculating model hash from file")
                    # Use asyncio.to_thread to calculate hash without blocking the main thread
                    loop = self._loop or asyncio.get_running_loop()
                    model_hash = await loop.run_in_executor(
                        None, calculate_file_hash, self._model_path
                    )

                    if model_hash:
                        self._model_hash = model_hash
                        logger.debug(f"Model hash calculated: {model_hash[:5]}...{model_hash[-5:] if len(model_hash) > 10 else '***'}")
                    else:
                        logger.error("Failed to calculate model hash")
                        raise ValueError("Failed to calculate model hash")
                except Exception as e:
                    logger.error(f"Failed to calculate model hash: {e}")
                    raise
            else:
                logger.warning("Cannot calculate model hash for non-file model")

        # Ensure we have hash or figure_id
        if not model_hash:
            logger.error(
                "Either runtime_model_hash or figure_id is required for token request"
            )
            raise ValueError("Cannot request token without model hash or figure ID")

        logger.debug(f"Hardware fingerprint: {self.fingerprint[:5]}...{self.fingerprint[-5:] if len(self.fingerprint) > 10 else '***'}")

        config = TokenRequestConfig(
            api_url=self._api_url,
            api_secret=self._api_secret,
            fingerprint=self.fingerprint,
            runtime_model_hash=model_hash,
            tags=self._tags,
            insecure=self._insecure,
            transaction_id=self.transaction_id,
        )

        try:
            logger.debug("Making API request for token")
            token = await request_token_async(config)
            if token:
                logger.debug(f"Token received from API: {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
                # Store the token
                self._token = token
                # Set and validate the token
                logger.debug("Validating received token")
                await self.set_token_async(token)
                logger.info("Token request and validation completed successfully")
                return token
            else:
                logger.error("API returned empty token")
                raise ValueError("Failed to obtain token from API")
        except Exception as e:
            logger.error(f"Error requesting token: {e}")
            raise

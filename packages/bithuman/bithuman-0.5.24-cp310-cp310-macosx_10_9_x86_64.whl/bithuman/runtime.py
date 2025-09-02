"""Bithuman Runtime."""

from __future__ import annotations

import asyncio
import copy
import logging
import os
import threading
from functools import cached_property
from pathlib import Path
from queue import Empty, Queue
from threading import Event
from typing import Callable, Generic, Iterable, Optional, TypeVar
import uuid

import numpy as np
from loguru import logger

from . import audio as audio_utils
from .api import AudioChunk, VideoControl, VideoFrame
from .config import load_settings
from .lib.generator import BithumanGenerator
from .utils import calculate_file_hash
from .video_graph import Frame as FrameMeta
from .video_graph import VideoGraphNavigator

logging.getLogger("numba").setLevel(logging.WARNING)

T = TypeVar("T")

BufferEmptyCallback = Callable[[], bool]


class Bithuman:
    """Bithuman Runtime."""

    def __init__(
        self,
        *,
        input_buffer_size: int = 0,
        token: Optional[str] = None,
        model_path: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_url: str = "https://auth.api.bithuman.ai/v1/runtime-tokens/request",
        tags: Optional[str] = None,
        insecure: bool = True,
        verbose: Optional[bool] = None,
    ) -> None:
        """Initialize the Bithuman Runtime.

        Args:
            input_buffer_size: The size of the input buffer.
            token: The token for the Bithuman Runtime. Either token or api_secret must be provided.
            model_path: The path to the avatar model.
            api_secret: API Secret for API authentication. Either token or api_secret must be provided.
            api_url: API endpoint URL for token requests.
            tags: Optional tags for token request.
            insecure: Disable SSL certificate verification (not recommended for production use).
            verbose: Enable verbose logging for token validation. If None, reads from BITHUMAN_VERBOSE environment variable.
        """
        # Set verbose from parameter or environment variable
        if verbose is None:
            verbose = os.getenv("BITHUMAN_VERBOSE", "false").lower() in ("true", "1", "yes", "on")
        self._verbose = verbose
        
        # Generate a unique transaction ID for the token request
        self.transaction_id = str(uuid.uuid4())

        logger.debug(
            f"Initializing Bithuman runtime with: model_path={model_path}, token={token is not None}, api_secret={api_secret is not None}, verbose={verbose}"
        )
        
        # Log environment variables for debugging
        logger.debug(f"BITHUMAN_VERBOSE env var: {os.getenv('BITHUMAN_VERBOSE', 'not set')}")
        logger.debug(f"LOADING_MODE env var: {os.getenv('LOADING_MODE', 'not set')}")
        
        # Mask sensitive information in logs
        if api_secret:
            masked_secret = f"{api_secret[:5]}...{api_secret[-5:] if len(api_secret) > 10 else '***'}"
            logger.debug(f"API secret provided: {masked_secret}")
        if token:
            masked_token = f"{token[:10]}...{token[-10:] if len(token) > 20 else '***'}"
            logger.debug(f"Token provided: {masked_token}")

        if not token and not api_secret:
            logger.error("Neither token nor api_secret provided")
            raise ValueError("Either token or api_secret must be provided")

        self.settings = copy.deepcopy(load_settings())

        try:
            self.generator = BithumanGenerator(str(self.settings.AUDIO_ENCODER_PATH))
        except Exception as e:
            logger.error(f"Failed to initialize BithumanGenerator: {e}")
            raise

        self.video_graph: Optional[VideoGraphNavigator] = None

        # Store the hardware fingerprint in a truly private attribute (with double underscore)
        # This makes it harder to access from outside the class
        try:
            self.__fingerprint = self.generator.fingerprint
        except Exception as e:
            logger.error(f"Failed to get hardware fingerprint: {e}")
            raise

        # Store token request parameters
        self._model_path = model_path
        self._api_secret = api_secret
        self._api_url = api_url
        self._tags = tags
        self._insecure = insecure
        self._token = token

        # Token refresh state
        self._stop_refresh_event = threading.Event()
        self._refresh_thread = None

        try:
            self._warmup()
        except Exception as e:
            logger.error(f"Warmup failed: {e}")
            raise

        # Ignore audios when muted
        self.muted = Event()
        self.interrupt_event = Event()
        self._input_buffer = ThreadSafeAsyncQueue[VideoControl](
            maxsize=input_buffer_size
        )

        # Video
        self.audio_batcher = audio_utils.AudioStreamBatcher(
            output_sample_rate=self.settings.INPUT_SAMPLE_RATE
        )
        self._video_loaded = False
        self._sample_per_video_frame = (
            self.settings.INPUT_SAMPLE_RATE / self.settings.FPS
        )
        self._idle_timeout: float = 0.001

        self._model_hash = None
        if self._model_path:
            # load model if provided
            self._initialize_token()
            self.set_model(self._model_path)

    def set_idle_timeout(self, idle_timeout: float) -> None:
        """Set the idle timeout for the Bithuman Runtime.

        Args:
            idle_timeout: The idle timeout in seconds.
        """
        self._idle_timeout = idle_timeout

    @property
    def fingerprint(self) -> str:
        """Get the hardware print fingerprint (read-only).

        Returns the unique hardware identifier fingerprint that was generated
        during initialization. This property is read-only and cannot be modified
        after initialization to protect against tampering.

        Returns:
            str: The hardware print fingerprint.
        """
        return self.__fingerprint

    def set_token(self, token: str, verbose: Optional[bool] = None) -> bool:
        """Set and validate the token for the Bithuman Runtime.

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
        if verbose is None:
            verbose = self._verbose
            
        logger.debug(f"Attempting to set token: {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
        logger.debug(f"Token validation verbose mode: {verbose}")
        
        try:
            is_valid = self.generator.validate_token(token, verbose)
            if not is_valid:
                logger.error("Token validation failed - token is invalid")
                raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Token validation exception: {e}")
            raise ValueError("Invalid token")

        logger.debug("Token validated successfully")
        return True

    def validate_token(self, token: str, verbose: Optional[bool] = None) -> bool:
        """Validate the token.
        
        Args:
            token: The token to validate.
            verbose: Enable verbose logging for token validation. If None, uses instance default.
            
        Returns:
            bool: True if token is valid, False otherwise.
        """
        if verbose is None:
            verbose = self._verbose
            
        return self.generator.validate_token(token, verbose)

    def is_token_validated(self) -> bool:
        """Check if the token is validated."""
        return self.generator.is_token_validated()

    def get_expiration_time(self) -> int:
        """Get the expiration time of the token."""
        return self.generator.get_expiration_time()

    def _initialize_token(self) -> None:
        """Initialize token by requesting it from the API.

        This method is called during initialization or when setting the model if api_secret is provided.
        """
        logger.debug("Starting token initialization process (sync)")
        
        if self._token:
            logger.debug("Existing token found, attempting validation")
            try:
                if self.set_token(self._token):
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
            
        logger.debug("Requesting new token from API (sync)")
        try:
            self.request_token()
            logger.debug("Token request completed successfully (sync)")
        except Exception as e:
            logger.error(f"Failed to request token from API: {e}")
            raise

    def start_token_refresh(self) -> None:
        """Start the token refresh thread if API secret is provided.

        This method creates a background thread that periodically refreshes the token
        using the API secret. The thread will be stopped when the runtime is stopped.
        """
        from .token_config import TokenRequestConfig
        from .token_utils import token_refresh_worker_sync

        if not self._api_secret:
            logger.debug("No API secret provided, skipping token refresh")
            return

        # Check if refresh thread is already running
        if self._refresh_thread and self._refresh_thread.is_alive():
            logger.debug(
                "Token refresh thread already running, skipping initialization"
            )
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
            fingerprint=self.__fingerprint,
            runtime_model_hash=model_hash,  # Explicitly include model hash
            tags=self._tags,
            insecure=self._insecure,
        )

        # Create and start the refresh thread
        self._refresh_thread = threading.Thread(
            target=token_refresh_worker_sync,
            args=(config, self._stop_refresh_event),  # Required arguments
            kwargs={"on_token_refresh": self._on_token_refresh},  # Optional callback
        )
        self._refresh_thread.daemon = True
        self._refresh_thread.start()
        logger.debug("Token refresh thread started")

    def _on_token_refresh(self, token: str) -> None:
        """Callback for token refresh."""
        self._token = token

    def set_model(self, model_path: str) -> "Bithuman":
        """Set the video file or workspace directory.

        Args:
            model_path: The workspace directory.
        """
        if not model_path:
            logger.error("No model path provided to set_model()")
            raise ValueError("Model path cannot be empty")

        if model_path == self._model_path and self._video_loaded:
            logger.debug("Model path is the same as the current model path, skipping")
            return

        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model path {model_path} does not exist")

        # Store the model path for token requests
        self._model_path = model_path

        if Path(model_path).is_file():
            # Use our public function to calculate hash, instead of generator's method
            try:
                self.generator.set_model_hash_from_file(model_path)
            except Exception as e:
                logger.error(f"Failed to calculate model hash: {e}")
                raise
        else:
            logger.info(
                "Skip model hash verification for non-file avatar model, "
                "make sure the token is valid for kind of usage."
            )
            self._model_hash = None

        try:
            self.video_graph = VideoGraphNavigator.from_workspace(
                model_path, extract_to_local=self.settings.EXTRACT_WORKSPACE_TO_LOCAL
            ).load_workspace()
        except Exception as e:
            logger.error(f"Failed to create VideoGraphNavigator or load workspace: {e}")
            raise

        try:
            self.video_graph.update_runtime_configs(self.settings)
        except Exception as e:
            logger.error(f"Failed to update runtime configs: {e}")
            raise

        try:
            self.generator.set_output_size(self.settings.OUTPUT_WIDTH)
        except Exception as e:
            logger.error(f"Failed to set output size: {e}")
            raise

        self._video_loaded = False

        try:
            self.load_data()
        except Exception as e:
            logger.error(f"load_data() failed: {e}")
            raise

        return self

    @property
    def model_hash(self) -> Optional[str]:
        """Get the model hash (read-only).

        Returns the unique model hash that was generated during model loading.
        This property is read-only and cannot be modified after initialization
        to protect against tampering.

        Returns:
            Optional[str]: The model hash if a file model was loaded, None otherwise.
        """
        return self._model_hash

    def load_data(self) -> None:
        """Load the workspace and set up related components."""
        if self._video_loaded:
            return
        if self.video_graph is None:
            logger.error("Video graph is None. Model may not be set properly.")
            raise ValueError("Video graph is not set. Call set_model() first.")

        models_path = Path(self.video_graph.avatar_model_path)

        def find_avatar_data_file(video_path: str) -> Optional[str]:
            video_name = Path(video_path).stem
            for type in ["feature-first", "time-first"]:
                files = list(models_path.glob(f"*/{video_name}.{type}.*"))
                if files:
                    return str(files[0])
            return None

        try:
            audio_feature_files = list(models_path.glob("*/feature_centers.npy"))
            audio_feature_file = audio_feature_files[0]
        except IndexError:
            logger.error(f"Audio features file not found in {models_path}")
            raise FileNotFoundError(f"Audio features file not found in {models_path}")

        try:
            audio_features = np.load(audio_feature_file)
        except Exception as e:
            logger.error(f"Failed to load audio features: {e}")
            raise

        try:
            self.generator.set_audio_feature(audio_features)
        except Exception as e:
            logger.error(f"Failed to set audio feature in generator: {e}")
            raise

        videos = list(self.video_graph.videos.items())
        filler_videos = list(self.video_graph.filler_videos.items())
        logger.info(
            f"Loading model data: {len(videos)} models and {len(filler_videos)} fillers"
        )

        for name, video in videos + filler_videos:
            video_data_path = video.video_data_path
            avatar_data_path = find_avatar_data_file(video.video_path)

            if video.lip_sync_required:
                if not (video_data_path and avatar_data_path):
                    logger.error(f"Model data not found for video {name}")
                    raise ValueError(f"Model data not found for video {name}")
            else:
                video_data_path, avatar_data_path = "", ""

            # Process the video data file if needed
            try:
                video_data_path = self._process_video_data_file(video_data_path)
            except Exception as e:
                logger.error(f"Failed to process video data file for {name}: {e}")
                raise

            try:
                self.generator.add_video(
                    name,
                    video_path=video.video_path,
                    video_data_path=video_data_path,
                    avatar_data_path=avatar_data_path,
                    compression_type=self.settings.COMPRESS_METHOD,
                    loading_mode=self.settings.LOADING_MODE,
                )
            except Exception as e:
                logger.error(f"Failed to add video {name} to generator: {e}")
                raise

        logger.info("Model data loaded successfully")
        self._video_loaded = True

    def get_first_frame(self) -> Optional[np.ndarray]:
        """Get the first frame of the video."""
        if not self.video_graph:
            logger.error("Model is not set. Call set_model() first.")
            return None
        try:
            frame = self.video_graph.get_first_frame(self.settings.OUTPUT_WIDTH)
            return frame
        except Exception as e:
            logger.error(f"Failed to get the first frame: {e}")
            return None

    def get_frame_size(self) -> tuple[int, int]:
        """Get the frame size in width and height."""
        image = self.get_first_frame()
        if image is None:
            logger.error("Failed to get the first frame")
            raise ValueError("Failed to get the first frame")
        size = (image.shape[1], image.shape[0])
        return size

    def interrupt(self) -> None:
        """Interrupt the daemon."""
        # clear the input buffer
        while not self._input_buffer.empty():
            try:
                self._input_buffer.get_nowait()
            except Empty:
                break
        self.audio_batcher.reset()
        self.interrupt_event.set()

    def set_muted(self, mute: bool) -> None:
        """Set the muted state."""
        if mute:
            self.muted.set()
        else:
            self.muted.clear()

    def push_audio(
        self, data: bytes, sample_rate: int, last_chunk: bool = True
    ) -> None:
        """Push the audio to the input buffer."""
        self._input_buffer.put(VideoControl.from_audio(data, sample_rate, last_chunk))

    def flush(self) -> None:
        """Flush the input buffer."""
        self._input_buffer.put(VideoControl(end_of_speech=True))

    def push(self, control: VideoControl) -> None:
        """Push the control (with audio, text, action, etc.) to the input buffer."""
        self._input_buffer.put(control)

    def run(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        idle_timeout: float | None = None,
    ) -> Iterable[VideoFrame]:
        # Current frame index, reset for every new audio
        if self.video_graph is None:
            raise ValueError("Model is not set. Call set_model() first.")

        curr_frame_index = 0
        action_played = False  # Whether the action is played in this speech
        while True:
            try:
                if self.interrupt_event.is_set():
                    # Clear the interrupt event for the next loop
                    self.interrupt_event.clear()
                control = self._input_buffer.get(
                    timeout=idle_timeout or self._idle_timeout
                )
                if self.muted.is_set():
                    # Consume and skip the audio when muted
                    control = VideoControl(message_id="MUTED")
                    action_played = False  # Reset the action played flag
            except Empty:
                if out_buffer_empty and not out_buffer_empty():
                    continue
                control = VideoControl(message_id="IDLE")  # idle

            if self.video_graph is None:
                # cleanup is called
                logger.info("Stopping runtime after cleanup")
                break

            # Edit the video based on script if the input is None
            if not control.target_video and not control.action:
                control.target_video, control.action, reset_action = (
                    self.video_graph.videos_script.get_video_and_actions(
                        curr_frame_index,
                        control.emotion_preds,
                        text=control.text,
                        is_idle=control.is_idle,
                        settings=self.settings,
                    )
                )
                if reset_action:
                    action_played = False
            if not control.is_idle:
                # Avoid playing the action multiple times in a conversation
                if action_played:
                    control.action = None
                elif control.action:
                    action_played = True

            for frame in self.process(control):
                yield frame
                curr_frame_index += 1

            if control.end_of_speech:
                self.audio_batcher.reset()
                # Passthrough the end flag of the speech
                yield VideoFrame(
                    source_message_id=control.message_id,
                    end_of_speech=control.end_of_speech,
                )

                # Reset the action played flag
                action_played = False
                curr_frame_index = 0
                self.video_graph.videos_script.last_nonidle_frame = 0

                # Reset the video graph if needed
                self.video_graph.next_n_frames(num_frames=0, on_user_speech=True)

    def process(self, control: VideoControl) -> Iterable[VideoFrame]:
        """Process the audio or control data."""

        def _get_next_frame() -> FrameMeta:
            return self.video_graph.next_n_frames(
                num_frames=1,
                target_video_name=control.target_video,
                actions_name=control.action,
                on_agent_speech=control.is_speaking,
            )[0]

        frame_index = 0
        for padded_chunk in self.audio_batcher.push(control.audio):
            audio_array = padded_chunk.array

            # get the mel chunks on padded audio
            mel_chunks = audio_utils.get_mel_chunks(
                audio_utils.int16_to_float32(audio_array), fps=self.settings.FPS
            )
            # unpad the audio and mel chunks
            audio_array = self.audio_batcher.unpad(audio_array)
            start = self.audio_batcher.pre_pad_video_frames
            valid_frames = int(len(audio_array) / self._sample_per_video_frame)
            mel_chunks = mel_chunks[start : start + valid_frames]

            num_frames = len(mel_chunks)
            samples_per_frame = len(audio_array) // max(num_frames, 1)
            for i, mel_chunk in enumerate(mel_chunks):
                if self.muted.is_set():
                    return
                if self.interrupt_event.is_set():
                    self.interrupt_event.clear()
                    return

                frame_meta = _get_next_frame()
                frame = self._process_talking_frame(frame_meta, mel_chunk)

                audio_start = i * samples_per_frame
                audio_end = (
                    audio_start + samples_per_frame
                    if i < num_frames - 1
                    else len(audio_array)
                )
                yield VideoFrame(
                    bgr_image=frame,
                    audio_chunk=AudioChunk(
                        data=audio_array[audio_start:audio_end],
                        sample_rate=padded_chunk.sample_rate,
                        last_chunk=i == num_frames - 1,
                    ),
                    frame_index=frame_index,
                    source_message_id=control.message_id,
                )
                frame_index += 1

        if frame_index == 0 and not control.audio:
            # generate idle frame if no frame is generated
            frame_meta = _get_next_frame()
            frame = self._process_idle_frame(frame_meta)
            yield VideoFrame(
                bgr_image=frame,
                frame_index=frame_index,
                source_message_id=control.message_id,
            )

    def _process_talking_frame(
        self, frame: FrameMeta, mel_chunk: np.ndarray
    ) -> np.ndarray:
        frame_np = self.generator.process_audio(
            mel_chunk, frame.video_name, frame.frame_index
        )
        return frame_np

    def _process_idle_frame(self, frame: FrameMeta) -> np.ndarray:
        """Get the idle frame with cache."""
        # Skip processing idle video
        if not self.settings.PROCESS_IDLE_VIDEO:
            frame_np = self.generator.get_original_frame(
                frame.video_name, frame.frame_index
            )
        else:
            frame_np = self.generator.process_audio(
                self.silent_mel_chunk, frame.video_name, frame.frame_index
            )
        return frame_np

    @cached_property
    def silent_mel_chunk(self) -> np.ndarray:
        """The mel chunk for silent audio."""
        audio_np = np.zeros(self.settings.INPUT_SAMPLE_RATE * 1, dtype=np.float32)
        return audio_utils.get_mel_chunks(audio_np, fps=self.settings.FPS)[0]

    def _process_video_data_file(self, video_data_path: str) -> str:
        """Process the video data file."""
        if not video_data_path:
            return video_data_path

        if video_data_path.endswith(".pth"):
            logger.debug(f"Converting pth to h5, torch is required: {video_data_path}")
            from .lib.pth2h5 import convert_pth_to_h5

            return convert_pth_to_h5(video_data_path)
        return video_data_path

    def _warmup(self) -> None:
        """Warm up the audio processing."""
        audio_utils.get_mel_chunks(
            np.zeros(16000, dtype=np.float32), fps=self.settings.FPS
        )

    def stop_token_refresh(self) -> None:
        """Stop the token refresh thread if running."""
        if (
            self._api_secret
            and self._refresh_thread
            and self._refresh_thread.is_alive()
        ):
            logger.debug("Stopping token refresh thread...")
            self._stop_refresh_event.set()
            self._refresh_thread.join(timeout=2.0)
            if self._refresh_thread.is_alive():
                logger.warning("Token refresh thread did not complete in time")
            self._refresh_thread = None

    def cleanup(self) -> None:
        """Clean up the video graph."""
        if self.video_graph:
            self.video_graph.cleanup()
            self.video_graph = None

    def __del__(self) -> None:
        """Clean up the video graph."""
        self.cleanup()

    @classmethod
    def create(
        cls,
        *,
        model_path: Optional[str] = None,
        token: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_url: str = "https://auth.api.bithuman.ai/v1/runtime-tokens/request",
        tags: Optional[str] = None,
        insecure: bool = True,
        input_buffer_size: int = 0,
        verbose: Optional[bool] = None,
    ) -> "Bithuman":
        """Create a fully initialized Bithuman instance."""

        # Create instance with initial parameters but defer model setting
        instance = cls(
            input_buffer_size=input_buffer_size,
            token=token,
            model_path=None,  # Will set model later
            api_secret=api_secret,
            api_url=api_url,
            tags=tags,
            insecure=insecure,
            verbose=verbose,
        )

        # Store model path for later use
        if model_path:
            instance._model_path = model_path

        # Validate and set token if provided
        if token:
            try:
                # Set and validate token
                instance.set_token(token)
            except Exception as e:
                logger.error(f"Failed to validate token: {e}")
                if api_secret:
                    logger.info(
                        "Token validation failed, will try to request new token using API secret"
                    )
                    token = None  # Reset token to use api_secret instead
                else:
                    raise  # No fallback available

        # Request token with API secret if needed
        if api_secret and not token and model_path:
            try:
                instance.request_token()
            except Exception as e:
                logger.error(f"Failed to request token: {e}")
                raise

        # Start token refresh if API secret is provided
        if api_secret:
            instance.start_token_refresh()

        # Set model if provided
        if model_path:
            try:
                instance.set_model(model_path)
            except Exception as e:
                logger.error(f"Failed to set model: {e}")
                raise
        else:
            logger.warning("No model path provided to factory method")

        # Verify initialization success
        try:
            if instance.video_graph is None:
                raise ValueError("Video graph not initialized")
        except Exception as e:
            logger.error(f"Initialization verification failed: {e}")
            raise

        return instance

    def request_token(self) -> str:
        """Request a token from the API.

        This method requests a token using the API secret and stores it
        in the instance. It also sets the token for the runtime if successful.

        Returns:
            The obtained token string

        Raises:
            ValueError: If API secret or model path is not provided
        """
        from .token_config import TokenRequestConfig
        from .token_utils import request_token_sync

        if not self._api_secret:
            raise ValueError("API secret is required for token request")

        if not self._model_path:
            raise ValueError("Model path is required for token request")

        # Calculate model hash if needed for token request
        model_hash = None
        if self._model_hash:
            model_hash = self._model_hash
        else:
            if Path(self._model_path).is_file():
                try:
                    model_hash = calculate_file_hash(self._model_path)
                    self._model_hash = model_hash
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

        config = TokenRequestConfig(
            api_url=self._api_url,
            api_secret=self._api_secret,
            fingerprint=self.__fingerprint,
            runtime_model_hash=model_hash,
            tags=self._tags,
            insecure=self._insecure,
        )

        try:
            token = request_token_sync(config)
            if token:
                # Store the token
                self._token = token
                # Set and validate the token
                if not self.set_token(token):
                    logger.warning("Failed to set token")
                return token
            else:
                raise ValueError("Failed to obtain token from API")
        except Exception as e:
            logger.error(f"Error requesting token: {e}")
            raise


class ThreadSafeAsyncQueue(Generic[T]):
    """A thread-safe queue that can be used from both async and sync contexts.

    This queue uses a standard threading.Queue internally for thread safety,
    but provides async methods for use in async contexts.
    """

    def __init__(
        self, maxsize: int = 0, event_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """Initialize the queue.

        Args:
            maxsize: Maximum size of the queue. 0 means unlimited.
            event_loop: The event loop to use.
        """
        self._queue = Queue[T](maxsize=maxsize)
        self._loop = event_loop

    def put_nowait(self, item: T) -> None:
        """Put an item into the queue without blocking."""
        self._queue.put_nowait(item)

    async def aput(self, item: T, *args, **kwargs) -> None:
        """Put an item into the queue asynchronously."""
        # Use run_in_executor to avoid blocking the event loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        await self._loop.run_in_executor(None, self._queue.put, item, *args, **kwargs)

    def put(self, item: T, *args, **kwargs) -> None:
        """Put an item into the queue."""
        self._queue.put(item, *args, **kwargs)

    def get_nowait(self) -> T:
        """Get an item from the queue without blocking."""
        return self._queue.get_nowait()

    async def aget(self, *args, **kwargs) -> T:
        """Get an item from the queue asynchronously."""
        # Use run_in_executor to avoid blocking the event loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        return await self._loop.run_in_executor(None, self._queue.get, *args, **kwargs)

    def get(self, *args, **kwargs) -> T:
        """Get an item from the queue."""
        return self._queue.get(*args, **kwargs)

    def task_done(self) -> None:
        """Mark a task as done."""
        self._queue.task_done()

    def empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.empty()

    def qsize(self) -> int:
        """Get the size of the queue."""
        return self._queue.qsize()

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop."""
        self._loop = loop

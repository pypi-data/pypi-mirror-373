"""Message definitions for bithuman runtime service."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import cached_property
from typing import Any, Optional

import numpy as np

from bithuman.api import AudioChunk, VideoControl
from bithuman.utils.image import decode_image, encode_image


class CommandType(str, Enum):
    """Types of commands that can be sent to the server."""

    INIT = "init"
    AUDIO = "audio"
    HEARTBEAT = "heartbeat"
    INTERRUPT = "interrupt"
    CHECK_INIT_STATUS = "check_init_status"  # Add new command type
    GET_SETTING = "get_setting"


class ResponseStatus(str, Enum):
    """Possible response statuses."""

    SUCCESS = "success"
    ERROR = "error"
    LOADING = "loading"  # Add new status for async initialization


@dataclass(kw_only=True)
class BaseRequest:
    """Base class for all requests."""

    client_id: str
    command: CommandType

    def to_dict(self) -> dict:
        """Convert request to dictionary format."""
        return asdict(self)


@dataclass(kw_only=True)
class InitRequest(BaseRequest):
    """Request to initialize a client workspace."""

    avatar_model_path: str
    video_file: Optional[str] = None
    inference_data_file: Optional[str] = None
    command: CommandType = CommandType.INIT


@dataclass(kw_only=True)
class AudioRequest(BaseRequest):
    """Request to process audio data."""

    data: VideoControl
    command: CommandType = CommandType.AUDIO

    def __post_init__(self) -> None:
        """Post initialization."""
        if isinstance(self.data, dict):
            self.data = VideoControl(**self.data)

    def to_dict(self) -> dict:
        """Convert request to dictionary format."""
        request_dict = asdict(self)
        # Use numpy's more efficient serialization
        if self.data.audio is not None:
            audio_dict = asdict(self.data.audio)
            del audio_dict["data"]
            audio_dict["audio_bytes"] = self.data.audio.bytes
            request_dict["data"]["audio"] = audio_dict
        return request_dict

    @classmethod
    def from_dict(cls, msg: dict) -> "AudioRequest":
        """Create an AudioRequest from a dictionary."""
        request = cls(**msg)
        if request.data.audio is not None:
            request.data.audio = AudioChunk.from_bytes(**request.data.audio)

        return request

    def __repr__(self) -> str:
        """String representation of the AudioRequest."""
        data_dict = self.to_dict()["data"]
        data_dict.pop("audio_fp32")
        data_dict["audio_duration"] = (
            (len(self.data.audio_fp32) / self.data.audio_sample_rate)
            if self.data.audio_fp32 is not None
            else None
        )
        return f"AudioRequest(data={data_dict})"

    @property
    def audio_bytes(self) -> Optional[bytes]:
        """Get the audio data as bytes."""
        if self.data.audio_fp32 is None:
            return None
        return self.data.audio_fp32.tobytes()


@dataclass(kw_only=True)
class HeartbeatRequest(BaseRequest):
    """Heartbeat request to keep connection alive."""

    command: CommandType = CommandType.HEARTBEAT


@dataclass(kw_only=True)
class InterruptRequest(BaseRequest):
    """Request to interrupt current audio processing."""

    command: CommandType = CommandType.INTERRUPT


@dataclass(kw_only=True)
class CheckInitStatusRequest(BaseRequest):
    """Request to check initialization status."""

    command: CommandType = CommandType.CHECK_INIT_STATUS


@dataclass(kw_only=True)
class GetSettingRequest(BaseRequest):
    """Request to get the current settings."""

    command: CommandType = CommandType.GET_SETTING
    name: str


@dataclass
class ServerResponse:
    """Generic server response."""

    status: ResponseStatus
    message: Optional[str] = None
    extra: Optional[dict] = None

    @classmethod
    def from_dict(cls, response_dict: dict) -> "ServerResponse":
        """Create a ServerResponse from a dictionary."""
        return ServerResponse(
            status=ResponseStatus(response_dict["status"]),
            message=response_dict.get("message"),
            extra=response_dict.get("extra"),
        )

    def to_dict(self) -> dict:
        """Convert response to dictionary format."""
        return asdict(self)


@dataclass
class FrameMessage:
    """Frame data sent from server to client."""

    client_id: str
    frame_data: bytes  # JPEG encoded image data
    frame_index: Optional[int]
    source_message_id: str
    end_of_speech: bool  # mark the end of the speech
    audio_bytes: Optional[bytes] = None  # Audio chunk data
    sample_rate: Optional[int] = None  # Audio sample rate
    metadata: dict = field(default_factory=dict)  # For additional frame info

    def to_dict(self) -> dict:
        """Convert response to dictionary format."""
        return asdict(self)

    @classmethod
    def create(
        cls,
        client_id: str,
        frame_image: np.ndarray,
        frame_index: Optional[int],
        end_of_speech: bool,
        audio_bytes: Optional[bytes] = None,
        sample_rate: Optional[int] = None,
        source_message_id: Optional[str] = None,
        **kwargs: dict[str, Any],
    ) -> "FrameMessage":
        """Create a frame message from frame data."""
        if frame_image is not None:
            frame_image = encode_image(frame_image)

        return FrameMessage(
            client_id=client_id,
            frame_data=frame_image,
            frame_index=frame_index,
            source_message_id=source_message_id,
            end_of_speech=end_of_speech,
            audio_bytes=audio_bytes,
            sample_rate=sample_rate,
            metadata=kwargs,
        )

    @cached_property
    def image(self) -> np.ndarray:
        """Get the image as a numpy array."""
        return decode_image(self.frame_data)

    @property
    def has_audio(self) -> bool:
        """Check if frame has valid audio data."""
        return bool(self.audio_bytes and self.sample_rate)

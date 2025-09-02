"""API for Bithuman Runtime."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Hashable, List, Optional

import numpy as np
from dataclasses_json import dataclass_json

INT16_MAX = 2**15 - 1


@dataclass
class AudioChunk:
    """Data class to store audio data.

    Attributes:
        data (np.ndarray): Audio data in int16 format with 1 channel, shape (n_samples,).
        sample_rate (int): Sample rate of the audio data.
        last_chunk (bool): Whether this is the last chunk of the speech.
    """

    data: np.ndarray
    sample_rate: int
    last_chunk: bool = True

    def __post_init__(self) -> None:
        if isinstance(self.data, bytes):
            self.data = np.frombuffer(self.data, dtype=np.int16)

        if self.data.dtype in [np.float32, np.float64]:
            self.data = (self.data * INT16_MAX).astype(np.int16)

        if not isinstance(self.data, np.ndarray) or self.data.dtype != np.int16:
            raise ValueError("data must be in int16 numpy array format")

    @property
    def bytes(self) -> bytes:
        return self.data.tobytes()

    @property
    def array(self) -> np.ndarray:
        return self.data

    @property
    def duration(self) -> float:
        return len(self.data) / self.sample_rate

    @classmethod
    def from_bytes(
        cls,
        audio_bytes: bytes,
        sample_rate: int,
        last_chunk: bool = True,
    ) -> "AudioChunk":
        return cls(
            data=np.frombuffer(audio_bytes, dtype=np.int16),
            sample_rate=sample_rate,
            last_chunk=last_chunk,
        )


@dataclass
class VideoControl:
    """Dataclass for video control information."""

    audio: Optional[AudioChunk] = None
    text: Optional[str] = None
    target_video: Optional[str] = None
    action: Optional[str | List[str]] = None
    emotion_preds: Optional[List["EmotionPrediction"]] = None
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    end_of_speech: bool = False  # mark the end of the speech

    @property
    def is_idle(self) -> bool:
        """Check if the audio or control is idle."""
        return (
            self.audio is None
            and self.target_video is None
            and not self.action
            and not self.emotion_preds
        )

    @property
    def is_speaking(self) -> bool:
        """Check if the audio or control is speaking."""
        return self.audio is not None

    @classmethod
    def from_audio(
        cls, audio: bytes | np.ndarray, sample_rate: int, last_chunk: bool = True
    ) -> "VideoControl":
        if isinstance(audio, bytes):
            audio_chunk = AudioChunk.from_bytes(audio, sample_rate, last_chunk)
        elif isinstance(audio, np.ndarray):
            audio_chunk = AudioChunk(
                data=audio, sample_rate=sample_rate, last_chunk=last_chunk
            )
        else:
            raise ValueError("audio must be bytes or numpy array")
        return cls(audio=audio_chunk)


@dataclass
class VideoFrame:
    """
    Dataclass for frame information.

    Attributes:
        bgr_image: image data in uint8 BGR format, shape (H, W, 3).
        audio_chunk: audio chunk if the frame is talking,
            chunked to the duration of this video frame based on FPS.
        frame_index: frame index generated for this video control.
        source_message_id: message id of the video control.
    """

    bgr_image: Optional[np.ndarray] = None
    audio_chunk: Optional[AudioChunk] = None
    frame_index: Optional[int] = None
    source_message_id: Optional[Hashable] = None
    end_of_speech: bool = False  # mark the end of the speech

    @property
    def has_image(self) -> bool:
        return self.bgr_image is not None

    @property
    def rgb_image(self) -> Optional[np.ndarray]:
        if self.bgr_image is None:
            return None
        return self.bgr_image[:, :, ::-1]


class Emotion(str, Enum):
    """Enumeration representing different emotions."""

    ANGER = "anger"
    DISGUST = "disgust"
    FEAR = "fear"
    JOY = "joy"
    NEUTRAL = "neutral"
    SADNESS = "sadness"
    SURPRISE = "surprise"


@dataclass_json
@dataclass
class EmotionPrediction:
    """Dataclass for emotion prediction.

    Attributes:
        emotion: The emotion.
        score: The score for the emotion.
    """

    emotion: Emotion
    score: float

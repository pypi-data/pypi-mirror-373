"""Utilities for audio resample."""
from __future__ import annotations

import tempfile
from functools import cached_property
from pathlib import Path
from typing import Iterable, Optional, Tuple

import numpy as np
import soundfile
import soxr

from ..api import AudioChunk

INT16_MAX = 2**15 - 1  # 32767


def load_audio(
    audio_path: str, target_sr: Optional[int] = None
) -> Tuple[np.ndarray, int]:
    """
    Load an audio file and resample it to the target sample rate.

    Args:
        audio_path (str): Path to the audio file.
        target_sr (int): Target sample rate for resampling.

    Returns:
        np.array: Resampled audio buffer.
    """
    audio_np, sr = soundfile.read(audio_path, dtype=np.float32)
    # convert multichannel to single channel
    if len(audio_np.shape) > 1:
        audio_np = np.mean(audio_np, axis=0)

    if target_sr is not None and sr != target_sr:
        audio_np = soxr.resample(audio_np, sr, target_sr)
        sr = target_sr

    return audio_np, sr


def float32_to_int16(x: np.ndarray) -> np.ndarray:
    """
    Converts an array of float32 values to int16.

    Args:
        x (np.array): Array of float32 values.

    Returns:
        np.array: Array of int16 values.
    """
    return (x * INT16_MAX).astype(np.int16)


def int16_to_float32(x: np.ndarray) -> np.ndarray:
    """
    Converts an array of int16 values to float32.

    Args:
        x (np.array): Array of int16 values.

    Returns:
        np.array: Array of float32 values.
    """
    return x.astype(np.float32) / INT16_MAX


def resample(audio_buffer: np.ndarray, origin_sr: int, target_sr: int) -> np.ndarray:
    """
    Resamples an audio buffer.

    Args:
        audio_buffer (np.array): Array of audio samples, only support int16 and float32.
        origin_sr (int): Original sample rate of the audio buffer.
        target_sr (int): Target sample rate for resampling.

    Returns:
        np.array: Resampled audio buffer.
    """

    return soxr.resample(audio_buffer, origin_sr, target_sr)


class AudioStreamBatcher:
    """
    A class to batch audio streams into chunks suitable for video processing.

    This class takes in a stream of AudioFrame objects and outputs batched AudioFrame
    objects that are suitable for synchronization with video frames.

    Attributes:
        pre_pad (int): Number of samples to pad before the audio data.
        post_pad (int): Number of samples to pad after the audio data.
        hop_size (int): Number of samples to hop between audio data.
        min_video_frames (int): Minimum number of video frames to process.
        expected_video_frames (int): Expected number of video frames to process.
        fps (int): Frames per second of the video.
        output_sample_rate (int): Sample rate of the output audio data.
    """

    def __init__(
        self,
        *,
        pre_pad: int = 400,
        post_pad: int = 200 * 13,
        hop_size: int = 200,
        min_video_frames: int = 2,
        expected_video_frames: int = 10,
        fps: int = 25,
        output_sample_rate: int = 16000,
    ) -> None:
        """
        Initialize the AudioStreamBatcher.

        Args:
            pre_pad (int): Number of samples to pad before the audio data.
            post_pad (int): Number of samples to pad after the audio data.
            hop_size (int): Number of samples to hop between audio data.
            min_video_frames (int): Minimum number of video frames to process.
            expected_video_frames (int): Expected number of video frames to process.
            fps (int): Frames per second of the video.
            output_sample_rate (int): Sample rate of the output audio data.
        """
        self.pre_pad = pre_pad
        self.post_pad = post_pad
        self.hop_size = hop_size
        self.min_video_frames = min_video_frames
        self.expected_video_frames = expected_video_frames
        self.fps = fps
        self.output_sample_rate = output_sample_rate

        self.bytes_per_sample = 2  # int16
        self.min_n_samples = int(
            output_sample_rate / fps * min_video_frames + pre_pad + post_pad
        )
        self.expect_n_samples = int(
            output_sample_rate / fps * expected_video_frames + pre_pad + post_pad
        )
        self.reset()

    def reset(self) -> None:
        """Reset the batcher to the initial state."""
        self._buffer = np.zeros(self.pre_pad, dtype=np.int16).tobytes()
        self._target_length = self.min_n_samples * self.bytes_per_sample
        self._resampler: soxr.ResampleStream | None = None

    def push(self, data: AudioChunk | None) -> Iterable[AudioChunk]:
        """
        Process an incoming AudioChunk object and yield properly padded AudioChunk objects.
        Args:
            data (AudioChunk): The incoming audio data to process.

        Yields:
            AudioChunk: A padded AudioChunk.
        """
        # add the audio data to the buffer if provided
        if data is not None:
            audio_array = data.array
            if data.sample_rate != self.output_sample_rate and self._resampler is None:
                self._resampler = soxr.ResampleStream(
                    data.sample_rate, self.output_sample_rate, 1, dtype="int16"
                )

            if self._resampler is not None:
                audio_array = self._resampler.resample_chunk(
                    audio_array, last=data.last_chunk
                )
            self._buffer += audio_array.tobytes()

        if data is None or data.last_chunk:
            last_chunk = self.flush()
            if last_chunk:
                yield last_chunk
            return

        while len(self._buffer) >= self._target_length:
            new_chunk = AudioChunk.from_bytes(
                self._buffer[: self._target_length],
                self.output_sample_rate,
                last_chunk=data.last_chunk,
            )
            yield new_chunk

            rest = len(self._buffer) - self._target_length
            self._buffer = self._buffer[
                -rest - (self.pre_pad + self.post_pad) * self.bytes_per_sample :
            ]
            # increase the batch size after the first chunk until the next flush
            self._target_length = self.expect_n_samples * self.bytes_per_sample

    def flush(self) -> AudioChunk | None:
        """Flush the audio buffer and yield the remaining audio data."""
        n_samples = len(self._buffer) // self.bytes_per_sample
        if n_samples <= self.pre_pad:
            return None

        # make sure the samples is n x hop_size
        end_pad = (self.hop_size - n_samples % self.hop_size) % self.hop_size
        self._buffer += np.zeros(end_pad + self.post_pad, dtype=np.int16).tobytes()
        chunk = AudioChunk.from_bytes(
            self._buffer,
            self.output_sample_rate,
            last_chunk=True,
        )
        self.reset()
        return chunk

    def unpad(self, audio_array: np.ndarray) -> np.ndarray:
        audio_array = audio_array[self.pre_pad : -self.post_pad]
        return audio_array

    @cached_property
    def pre_pad_video_frames(self) -> int:
        return self.pre_pad // 200


def write_video_with_audio(
    output_path: str | Path,
    frames: list,
    audio_np: np.ndarray,
    sample_rate: int,
    fps: int = 25,
) -> None:
    """Write frames and audio numpy array to a video file.

    Args:
        output_path: Path to save the video
        frames: List of RGB frames as numpy arrays
        audio_np: Audio as numpy array
        sample_rate: Audio sample rate in Hz
        fps: Video frame rate (default: 25)
    """
    from moviepy.editor import AudioFileClip, ImageSequenceClip

    # Create video clip from frames
    video_clip = ImageSequenceClip(frames, fps=fps)

    # Write audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
        soundfile.write(temp_audio.name, audio_np, sample_rate)
        # Create audio clip from temp file
        audio_clip = AudioFileClip(temp_audio.name)
        video_clip = video_clip.set_audio(audio_clip)

        # Write output video
        video_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=fps,
        )

        # Close clips
        video_clip.close()
        audio_clip.close()

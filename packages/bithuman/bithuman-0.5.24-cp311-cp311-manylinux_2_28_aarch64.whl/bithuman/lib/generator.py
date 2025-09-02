from __future__ import annotations

from typing import Optional, Union

import numpy as np

from ._bithuman_py import (
    BithumanRuntime as LibBithuman,
)
from ._bithuman_py import (
    CompressionType,
    LoadingMode,
)


def _parse_compression_type(compression_type: CompressionType | str) -> CompressionType:
    if isinstance(compression_type, CompressionType):
        return compression_type
    maps = {
        "NONE": CompressionType.NONE,
        "JPEG": CompressionType.JPEG,
        "LZ4": CompressionType.LZ4,
        "TEMP_FILE": CompressionType.TEMP_FILE,
    }
    if isinstance(compression_type, str):
        if compression_type not in maps:
            raise ValueError(f"Invalid compression type: {compression_type}")
        compression_type = maps[compression_type]
    return compression_type


def _parse_loading_mode(loading_mode: LoadingMode | str) -> LoadingMode:
    if isinstance(loading_mode, LoadingMode):
        return loading_mode
    maps = {
        "SYNC": LoadingMode.SYNC,
        "ASYNC": LoadingMode.ASYNC,
        "ON_DEMAND": LoadingMode.ON_DEMAND,
    }
    return maps[loading_mode]


class BithumanGenerator:
    """High-level Python wrapper for Bithuman Runtime Generator."""

    # Re-export CompressionType enum
    CompressionType = CompressionType

    def __init__(self, audio_encoder_path: Optional[str] = None, output_size: int = -1):
        """Initialize the generator.

        Args:
            audio_encoder_path: Path to the ONNX audio encoder model
            output_size: Output size for frames
        """
        if audio_encoder_path is not None:
            audio_encoder_path = str(audio_encoder_path)
        self._generator = LibBithuman(audio_encoder_path or "", output_size)

        # The fingerprint is automatically generated during the C++ BithumanRuntime initialization
        # We store it in a truly private attribute for protection against tampering
        self.__fingerprint = self._generator.getFingerprint()

    @property
    def fingerprint(self) -> str:
        """Get the stored hardware fingerprint (read-only property).

        Returns the hardware fingerprint that was generated during initialization.
        This property is read-only and cannot be modified after initialization.

        Returns:
            str: The hardware fingerprint
        """
        return self.__fingerprint

    def set_model_hash_from_file(self, model_path: str) -> str:
        """Set the model hash for verification against the token from a file.

        Args:
            model_path: Path to the model file

        Returns:
            str: The model hash
        """
        return self._generator.set_model_hash_from_file(model_path)

    def validate_token(self, token: str, verbose: bool = False) -> bool:
        """Validate a JWT token.

        Args:
            token: JWT token
        """
        return self._generator.validate_token(token, verbose)

    def get_instance_id(self) -> str:
        """Get the instance ID of this runtime.

        Returns:
            Instance ID
        """
        return self._generator.get_instance_id()

    def set_audio_encoder(self, audio_encoder_path: str) -> None:
        """Set the audio encoder model path.

        Args:
            audio_encoder_path: Path to the ONNX audio encoder model
        """
        self._generator.set_audio_encoder(str(audio_encoder_path))

    def set_audio_feature(self, audio_feature: Union[str, np.ndarray]) -> None:
        """Set the audio feature.

        Args:
            audio_feature: Path to HDF5 file or numpy array of features
        """
        if isinstance(audio_feature, str):
            self._generator.set_audio_feature(audio_feature)
        else:
            self._generator.set_audio_feature(audio_feature.astype(np.float32))

    def set_output_size(self, output_size: int) -> None:
        """Set the output size.

        Args:
            output_size: Output size
        """
        self._generator.set_output_size(output_size)

    def add_video(
        self,
        video_name: str,
        video_path: str,
        video_data_path: str,
        avatar_data_path: str,
        compression_type: CompressionType | str = CompressionType.JPEG,
        loading_mode: LoadingMode | str = LoadingMode.ASYNC,
    ) -> None:
        """Add a video to the generator.

        Args:
            video_name: Name to identify the video
            video_path: Path to the original video
            video_data_path: Path to the video data HDF5 file
            avatar_data_path: Path to the avatar data file
            compression_type: Type of compression to use (default: JPEG)
            loading_mode: Loading mode to use (default: ASYNC)
        """
        compression_type = _parse_compression_type(compression_type)
        loading_mode = _parse_loading_mode(loading_mode)
        self._generator.add_video(
            str(video_name),
            str(video_path),
            str(video_data_path),
            str(avatar_data_path),
            compression_type,
            loading_mode,
        )

    def process_audio(
        self, mel_chunk: np.ndarray, video_name: str, frame_idx: int
    ) -> np.ndarray:
        """Process audio chunk and return blended frame.

        Args:
            mel_chunk: Mel spectrogram chunk of shape (80, 16)
            video_name: Name of the video to use
            frame_idx: Frame index in the video

        Returns:
            np.ndarray: Blended frame as RGB image
        """
        return self._generator.process_audio(
            mel_chunk.astype(np.float32), str(video_name), frame_idx
        )

    def get_original_frame(self, video_name: str, frame_idx: int) -> np.ndarray:
        """Get the original frame.

        Args:
            video_name: Name of the video
            frame_idx: Frame index in the video
        """
        return self._generator.get_original_frame(str(video_name), frame_idx)

    def get_num_frames(self, video_name: str) -> int:
        """Get the number of frames in the video.

        Args:
            video_name: Name of the video

        Returns:
            int: Number of frames in the video, -1 if video not found
        """
        return self._generator.get_num_frames(str(video_name))

    def is_token_validated(self) -> bool:
        """Check if the token is validated.

        Returns:
            bool: True if the token is validated, False otherwise
        """
        return self._generator.is_token_validated()

    def get_expiration_time(self) -> int:
        """Get the expiration time of the token.

        Returns:
            int: Expiration time in seconds, -1 if token is not validated
        """
        return self._generator.get_expiration_time()

"""Configuration settings for the bithuman runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

_THIS_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Settings for the bithuman runtime."""

    model_config = ConfigDict(extra="ignore")

    # Video settings
    ALLOW_VIDEO_SCRIPT_UPDATE: bool = Field(
        True, description="Whether to allow the video script to update the settings."
    )
    OUTPUT_WIDTH: int = Field(
        1280,
        description="The size of the output video for the longest side.",
    )
    FPS: int = Field(25, description="The frames per second for the video.")
    COMPRESS_METHOD: Literal["NONE", "JPEG", "TEMP_FILE"] = Field(
        "JPEG", description="The method to compress the image."
    )
    LOADING_MODE: Literal["SYNC", "ASYNC", "ON_DEMAND"] = Field(
        "ASYNC", description="The mode to load the video."
    )
    INPUT_SAMPLE_RATE: int = Field(
        16_000, frozen=True, description="The sample rate of the input audio."
    )
    AUDIO_ENCODER_PATH: Path = Field(
        str(_THIS_DIR / "lib" / "audio_encoder.onnx"),
        description="The path to the audio encoder model.",
    )
    EXTRACT_WORKSPACE_TO_LOCAL: bool = Field(
        False, description="Whether to extract the workspace to local."
    )
    PROCESS_IDLE_VIDEO: bool = Field(True, description="Whether to process idle video.")

    # LIVA
    LIVA_IDEL_VIDEO_ENABLED: bool = Field(
        True, description="Whether to enable idle video."
    )
    LIVA_AUTO_SAY_HI: bool = Field(
        False, description="Whether to automatically say hi in the video."
    )

    # Video triggers
    KEYWORD_VIDEO_TRIGGERS_ENABLED: Annotated[
        bool, Field(description="Whether to enable keyword video triggers.")
    ] = True
    KEYWORD_VIDEO_TRIGGERS_JSON: Annotated[
        str,
        Field(
            description="JSON string containing keyword trigger configurations",
            default="[]",
        ),
    ] = "[]"


_settings = None


def load_settings(force_reload: bool = False) -> Settings:
    """Load the settings for the bithuman runtime.

    Args:
        force_reload: Whether to force a reload of the settings. Defaults to False

    Returns:
        The settings for the bithuman runtime
    """
    global _settings

    if force_reload:
        _settings = None

    if not _settings:
        # level： environ > .env file > default
        _settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

    return _settings

from __future__ import annotations

import cv2
import numpy as np

try:
    from turbojpeg import TurboJPEG

    jpeg_encoder = TurboJPEG()
except (ImportError, ModuleNotFoundError, RuntimeError):
    jpeg_encoder = None


def encode_image(image: np.ndarray, quality: int = 85) -> bytes:
    """Encode the image to bytes."""
    if jpeg_encoder is not None:
        return jpeg_encoder.encode(image, quality=quality)
    return cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])[
        1
    ].tobytes()


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode the image from bytes."""
    if jpeg_encoder is not None:
        return jpeg_encoder.decode(image_bytes)
    return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)


class CompressedImage:
    """A compressed image."""

    def __init__(self, data: bytes | np.ndarray) -> None:
        """Initialize the compressed image."""
        if isinstance(data, np.ndarray):
            data = encode_image(data)
        self.data = data

    def as_numpy(self) -> np.ndarray:
        """Get the image data as a numpy array."""
        return decode_image(self.data)

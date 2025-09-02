import hashlib
from pathlib import Path
from typing import Optional

from loguru import logger

from .fps_controller import FPSController

__all__ = ["FPSController"]


def calculate_file_hash(file_path: str) -> Optional[str]:
    """Calculate an MD5 hash of a file.

    This function reads the file in chunks to efficiently handle large files
    and calculates an MD5 hash, which is returned as a hexadecimal string.

    Args:
        file_path: Path to the file to be hashed

    Returns:
        A hexadecimal string representing the file hash, or None if the file doesn't exist

    Raises:
        IOError: If there's an error reading the file
    """
    try:
        path = Path(file_path)
        if not path.is_file():
            logger.warning(f"Cannot calculate hash for non-file: {file_path}")
            return None

        md5_hash = hashlib.md5()

        # Read the file in chunks of 4K to avoid loading large files into memory
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)

        return md5_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash for {file_path}: {e}")
        raise

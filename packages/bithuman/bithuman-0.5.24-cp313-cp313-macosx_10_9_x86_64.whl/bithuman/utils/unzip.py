from __future__ import annotations

import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional


def unzip_tarfile(
    file_path: str, extract_to_local: bool = False
) -> tuple[str, Optional[TemporaryDirectory]]:
    """Unzip the workspace directory if it is a file."""
    file_path: Path = Path(file_path)
    if file_path.is_dir():
        return str(file_path), None

    # Extract the workspace
    if not extract_to_local:
        temp_dir_handle = TemporaryDirectory()
        dest_dir = temp_dir_handle.name
    else:
        temp_dir_handle = None
        dest_dir = str(file_path.parent / file_path.stem)
        if dest_dir.endswith(".tar"):
            dest_dir = dest_dir[:-4]  # Remove .tar suffix

    if temp_dir_handle is not None or not Path(dest_dir).exists():
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        mode = "r:gz" if file_path.name.endswith("gz") else "r"
        with tarfile.open(file_path, mode) as tar:
            tar.extractall(dest_dir)
        file_path = dest_dir

    # Enter the dir if there is only one directory in the tar file
    files = list(Path(dest_dir).iterdir())
    if len(files) == 1 and files[0].is_dir():
        file_path = str(files[0])
    return file_path, temp_dir_handle

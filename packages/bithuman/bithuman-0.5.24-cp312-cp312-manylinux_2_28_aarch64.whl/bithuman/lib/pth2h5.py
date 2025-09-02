from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

import cv2
import h5py
import numpy as np


def encode_mask_as_jpg(mask: np.ndarray, quality: int = 85) -> bytes:
    """Encode a mask array as JPG bytes.

    Args:
        mask: Numpy array of mask (single channel)
        quality: JPG compression quality (1-100)

    Returns:
        JPG encoded bytes
    """
    # Convert to BGR for OpenCV
    mask = (mask * 255).astype(np.uint8)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Encode as JPG
    _, encoded = cv2.imencode(".jpg", mask, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return encoded.tobytes()


def convert_pth_to_h5(
    pth_path: Union[str, Path], h5_path: Union[str, Path] = None
) -> str:
    """Convert a PyTorch model file (.pth) to a HDF5 file (.h5).

    Args:
        pth_path: Path to the PyTorch model file
        h5_path: Path to save the HDF5 file. If None, saves to same location as pth_path
    """
    try:
        import torch
    except ImportError:
        raise ImportError(
            "PyTorch is not installed. Please install it using 'pip install torch'."
        )

    pth_path = Path(pth_path)
    if h5_path is None:
        h5_path = pth_path.with_suffix(".h5")

    # Load the PyTorch model
    data = torch.load(str(pth_path))

    # Extract data
    face_masks: list[bytes] = []
    face_coords: list[np.ndarray] = []
    frame_wh = data[0]["frame_wh"].numpy().astype(np.int32)

    for item in data:
        padded_crop_coords = item["padded_crop_coords"].numpy()
        face_xyxy = item["face_coords"].numpy()
        face_mask = item["face_mask"]

        # Encode face mask if needed
        if not isinstance(face_mask, bytes):
            face_mask = encode_mask_as_jpg(face_mask.numpy())

        # Adjust coordinates
        shift_x, shift_y = padded_crop_coords[:2].astype(np.int32)
        face_xyxy = face_xyxy[:4].astype(np.int32)
        face_xyxy[0::2] += shift_x
        face_xyxy[1::2] += shift_y

        face_masks.append(face_mask)
        face_coords.append(face_xyxy)

    # Save to H5 file
    with h5py.File(h5_path, "w") as f:
        f.create_dataset("face_coords", data=face_coords)

        dt = h5py.special_dtype(vlen=np.dtype("uint8"))
        masks_dataset = f.create_dataset(
            "face_masks", shape=(len(face_masks),), dtype=dt
        )
        for i, mask in enumerate(face_masks):
            masks_dataset[i] = np.frombuffer(mask, dtype=np.uint8)
        f.attrs["frame_wh"] = frame_wh

    return str(h5_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PyTorch .pth files to HDF5 format"
    )
    parser.add_argument("pth_path", type=str, help="Path to input .pth file")
    parser.add_argument(
        "--output", "-o", type=str, help="Path to output .h5 file (optional)"
    )

    args = parser.parse_args()
    convert_pth_to_h5(args.pth_path, args.output)


if __name__ == "__main__":
    main()

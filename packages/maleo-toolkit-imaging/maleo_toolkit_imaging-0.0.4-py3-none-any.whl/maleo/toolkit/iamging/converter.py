import base64
import io
import os
from typing import Literal, overload
from PIL import Image

from maleo.soma.types.base.string import OptionalString
from maleo.soma.types.base.misc import BytesOrString
from .enums import ColorSpace, ImageFormat, OutputType
from .processor import normalize, to_grayscale, to_rgb
from .reader import read_dicom


# === overloads ===
# --- Path input ---
@overload
def dicom_to_png(input: str, *, output_type: Literal[OutputType.BASE_64]) -> bytes: ...
@overload
def dicom_to_png(input: str, *, output_type: Literal[OutputType.RAW]) -> bytes: ...
@overload
def dicom_to_png(
    input: str, *, output_type: Literal[OutputType.FILE], output_path: str
) -> str: ...
@overload
def dicom_to_png(
    input: str,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.BASE_64],
) -> bytes: ...
@overload
def dicom_to_png(
    input: str,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.RAW],
) -> bytes: ...
@overload
def dicom_to_png(
    input: str,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.FILE],
    output_path: str,
) -> str: ...


# --- Byte input ---
@overload
def dicom_to_png(
    input: bytes, *, output_type: Literal[OutputType.BASE_64]
) -> bytes: ...
@overload
def dicom_to_png(input: bytes, *, output_type: Literal[OutputType.RAW]) -> bytes: ...
@overload
def dicom_to_png(
    input: bytes, *, output_type: Literal[OutputType.FILE], output_path: str
) -> str: ...
@overload
def dicom_to_png(
    input: bytes,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.BASE_64],
) -> bytes: ...
@overload
def dicom_to_png(
    input: bytes,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.RAW],
) -> bytes: ...
@overload
def dicom_to_png(
    input: bytes,
    *,
    color: Literal[ColorSpace.GRAYSCALE],
    output_type: Literal[OutputType.FILE],
    output_path: str,
) -> str: ...


# === implementation ===
def dicom_to_png(
    input: BytesOrString,
    *,
    output_type: OutputType,
    color: ColorSpace = ColorSpace.RGB,
    output_path: OptionalString = None,
) -> BytesOrString:
    """
    Convert DICOM (path string or raw byte) to PNG.

    Parameters
    ----------
    input : str | byte
        - str   → path to .dcm file
        - byte  → raw DICOM byte
    output_type : OutputType
        - BASE_64 → returns base64 encoded PNG byte
        - RAW     → returns raw PNG byte
        - FILE    → writes PNG to output and returns abs path
    color : ColorSpace
        RGB (default) or GRAYSCALE
    output_path : str | None
        Required if output_type=FILE
    """
    return _dicom_to_png(
        input, output_type=output_type, color=color, output_path=output_path
    )


# === helper ===
def _dicom_to_png(
    input: BytesOrString,
    *,
    output_type: OutputType,
    color: ColorSpace = ColorSpace.RGB,
    output_path: OptionalString = None,
) -> BytesOrString:
    # --- read dicom ---
    img = read_dicom(input)

    # --- normalize ---
    norm = normalize(img, min_percentile=0.5, max_percentile=99.5)

    # --- convert color (no else, no warning) ---
    arr = None
    if color == ColorSpace.RGB:
        arr = to_rgb(norm)
    if color == ColorSpace.GRAYSCALE:
        arr = to_grayscale(norm)
    if arr is None:
        raise ValueError(f"Unsupported color '{color}'")

    # --- save PNG to memory ---
    buffer = io.BytesIO()
    Image.fromarray(arr).save(buffer, format=ImageFormat.PNG)
    png_byte = buffer.getvalue()

    # --- handle outputs (no else, no warning) ---
    if output_type == OutputType.BASE_64:
        return base64.b64encode(png_byte)

    if output_type == OutputType.RAW:
        return png_byte

    if output_type == OutputType.FILE:
        if not output_path:
            raise ValueError("output_path must be provided when output_type=FILE")
        with open(output_path, "wb") as f:
            f.write(png_byte)
        return os.path.abspath(output_path)  # type: ignore

    raise ValueError(f"Unsupported output_type '{output_type}'")

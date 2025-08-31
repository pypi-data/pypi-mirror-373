import io
import os
import pydicom
import numpy as np
from pydicom.errors import InvalidDicomError
from maleo.soma.types.base.misc import BytesOrString


def read_dicom(input: BytesOrString) -> np.ndarray:
    """
    Read a DICOM file and return pixel data as float32.
    """

    # === Validate type ===
    if not isinstance(input, (str, bytes)):
        raise TypeError(f"Unsupported input type: {type(input)}")

    # === Validate extension if input is a path ===
    if isinstance(input, str):
        ext = os.path.splitext(input)[1].lower()
        if ext not in (".dcm", ".dicom"):
            raise ValueError(f"Invalid file extension '{ext}'")

    # === Try reading DICOM ===
    try:
        if isinstance(input, str):
            dicom = pydicom.dcmread(input, force=False)
        else:  # bytes
            dicom = pydicom.dcmread(io.BytesIO(input), force=False)
    except (InvalidDicomError, Exception) as e:
        raise ValueError(f"Input is not a valid DICOM file: {e}")

    # === Pixel data extraction ===
    try:
        img = dicom.pixel_array.astype(np.float32)
    except Exception as e:
        raise ValueError(f"Failed to extract pixel_array: {e}")

    if img.size == 0:
        raise ValueError("DICOM pixel_array is empty")

    # === Apply rescale if available ===
    try:
        slope = float(dicom.get("RescaleSlope", 1.0))
        intercept = float(dicom.get("RescaleIntercept", 0.0))
        if slope != 1.0 or intercept != 0.0:
            img = img * slope + intercept
    except Exception:
        pass  # ignore if attributes missing

    return img

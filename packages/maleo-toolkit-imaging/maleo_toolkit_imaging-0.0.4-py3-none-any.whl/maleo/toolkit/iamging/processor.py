import numpy as np


def normalize(
    img: np.ndarray, min_percentile: float = 0.0, max_percentile: float = 100.0
) -> np.ndarray:
    """
    Normalize image to 8-bit [0,255] using percentile-based scaling.

    Parameters
    ----------
    img : np.ndarray
        Input image (any dtype).
    min_percentile : float, default=0.0
        Lower percentile (e.g. 0.5 to ignore very dark outliers).
    max_percentile : float, default=100.0
        Upper percentile (e.g. 99.5 to ignore very bright outliers).

    Returns
    -------
    np.ndarray
        Normalized image in uint8.
    """
    if not (0.0 <= min_percentile < max_percentile <= 100.0):
        raise ValueError("min_percentile must be < max_percentile and in [0, 100].")

    min_val, max_val = np.percentile(img, (min_percentile, max_percentile))

    if max_val == min_val:  # avoid division by zero
        return np.zeros_like(img, dtype=np.uint8)

    img = np.clip(img, min_val, max_val)
    img = (img - min_val) / (max_val - min_val) * 255.0
    return img.astype(np.uint8)


def to_rgb(img: np.ndarray) -> np.ndarray:
    """
    Convert single-channel (grayscale) image to RGB.
    """
    if img.ndim == 2:
        return np.stack([img, img, img], axis=-1)
    elif img.ndim == 3 and img.shape[2] == 3:
        return img
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to single-channel grayscale using the standard luminance formula.
    If already grayscale, returns as-is.
    """
    if img.ndim == 2:
        return img  # Already grayscale

    elif img.ndim == 3:
        if img.shape[2] == 1:
            return img.squeeze(axis=-1)  # Remove singleton channel
        elif img.shape[2] == 3:
            # Standard luminance formula: 0.299*R + 0.587*G + 0.114*B
            return np.dot(img[..., :3], [0.299, 0.587, 0.114]).astype(img.dtype)
        else:
            raise ValueError(f"Unsupported number of channels: {img.shape[2]}")

    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")

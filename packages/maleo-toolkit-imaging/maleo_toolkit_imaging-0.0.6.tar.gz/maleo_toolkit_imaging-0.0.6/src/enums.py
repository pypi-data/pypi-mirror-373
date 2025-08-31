from enum import StrEnum


class ColorSpace(StrEnum):
    RGB = "rgb"
    GRAYSCALE = "grayscale"


class ImageFormat(StrEnum):
    PNG = "png"


class OutputType(StrEnum):
    BASE_64 = "base64"
    RAW = "raw"
    FILE = "file"

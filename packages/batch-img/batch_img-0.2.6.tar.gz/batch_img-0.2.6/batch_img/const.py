"""const.py - define constants
Copyright © 2025 John Liu
"""

PKG_NAME = "batch_img"
VER = "version"
EXPIRE_HOUR = 48
UNKNOWN = "unknown"

MSG_OK = "✅ Processed the image file(s)"
MSG_BAD = "❌ Failed to process image file(s)."

TS_FORMAT = "%Y-%m-%d_%H-%M-%S"
PATTERNS = (
    "*.HEIC",
    "*.heic",
    "*.JPG",
    "*.jpg",
    "*.JPEG",
    "*.jpeg",
    "*.PNG",
    "*.png",
)
REPLACE = "replace"
EXIF = "exif"
# Resize to 1920-pixel max length
# Add 5-pixel width black color border
# Remove GPS location info
MAX_LENGTH = 1920
BD_WIDTH = 5
BD_COLOR = "black"

#!/usr/bin/env python3
"""Example compositions for the resilient SHM consumer."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer import element


def create_text_overlay_composition():
    """Add text overlay to the video stream."""
    text_overlay = element.create("textoverlay", {
        "text": "🤖 Live Simulation Stream",
        "valignment": "top",
        "halignment": "left",
        "font-desc": "Sans Bold 24",
        "color": 0xFFFFFFFF,  # White
        "outline-color": 0x000000FF,  # Black outline
        "xpad": 20,
        "ypad": 20
    }, None)
    return [text_overlay]


def create_timestamp_overlay_composition():
    """Add timestamp overlay to the video stream."""
    timestamp_overlay = element.create("timeoverlay", {
        "valignment": "bottom",
        "halignment": "right",
        "font-desc": "Monospace Bold 16",
        "color": 0x00FF00FF,  # Green
        "xpad": 20,
        "ypad": 20
    }, None)
    return [timestamp_overlay]


def create_flip_composition():
    """Flip video horizontally."""
    flip = element.videoflip(method="horizontal-flip")
    return [flip]


def create_rotate_composition():
    """Rotate video 90 degrees clockwise."""
    rotate = element.videoflip(method="clockwise")
    return [rotate]


def create_scale_composition():
    """Scale video to different resolution."""
    scale = element.videoscale()
    caps_filter = element.capsfilter(
        caps=element.caps.raw(width=1280, height=720, format="RGB")
    )
    return [scale, caps_filter]


def create_crop_composition():
    """Crop video to center region."""
    crop = element.videocrop(
        left=240,    # Crop 240 pixels from left
        right=240,   # Crop 240 pixels from right
        top=135,     # Crop 135 pixels from top
        bottom=135   # Crop 135 pixels from bottom
    )
    return [crop]


def create_blur_composition():
    """Add blur effect to video."""
    blur = element.create("gaussianblur", {
        "sigma": 2.0
    }, None)
    return [blur]


def create_edge_detection_composition():
    """Apply edge detection filter."""
    edge = element.create("edgetv", {
        "threshold": 15
    }, None)
    return [edge]


def create_color_balance_composition():
    """Adjust color balance."""
    balance = element.create("videobalance", {
        "brightness": 0.1,
        "contrast": 1.2,
        "saturation": 1.1,
        "hue": 0.0
    }, None)
    return [balance]


def create_multi_overlay_composition():
    """Multiple overlays: timestamp + text + frame counter."""
    # Text overlay
    text = element.create("textoverlay", {
        "text": "🤖 Simulation",
        "valignment": "top",
        "halignment": "left",
        "font-desc": "Sans Bold 20",
        "color": 0xFFFFFFFF,
        "xpad": 20,
        "ypad": 20
    }, None)
    
    # Timestamp overlay
    timestamp = element.create("timeoverlay", {
        "valignment": "bottom",
        "halignment": "right",
        "font-desc": "Monospace 14",
        "color": 0x00FF00FF,
        "xpad": 20,
        "ypad": 20
    }, None)
    
    return [text, timestamp]


def create_picture_in_picture_composition():
    """Create picture-in-picture effect with test pattern."""
    # This is more complex and would require a mixer
    # For now, just return a simple overlay
    overlay = element.create("textoverlay", {
        "text": "PiP Mode",
        "valignment": "top",
        "halignment": "right",
        "font-desc": "Sans Bold 16",
        "color": 0xFF0000FF,  # Red
        "xpad": 20,
        "ypad": 20
    }, None)
    return [overlay]


def create_performance_overlay_composition():
    """Add performance metrics overlay."""
    # FPS display
    fps_overlay = element.create("fpsdisplaysink", {
        "text-overlay": True,
        "video-sink": element.create("fakesink", {"sync": False}, None)
    }, None)
    
    # Note: This is a special case that replaces the sink
    # For regular overlay, use text overlay with custom text
    perf_text = element.create("textoverlay", {
        "text": "Performance Monitor",
        "valignment": "top",
        "halignment": "center",
        "font-desc": "Monospace Bold 14",
        "color": 0xFFFF00FF,  # Yellow
        "ypad": 20
    }, None)
    
    return [perf_text]


# Composition registry for easy access
COMPOSITIONS = {
    "text": create_text_overlay_composition,
    "timestamp": create_timestamp_overlay_composition,
    "flip": create_flip_composition,
    "rotate": create_rotate_composition,
    "scale": create_scale_composition,
    "crop": create_crop_composition,
    "blur": create_blur_composition,
    "edge": create_edge_detection_composition,
    "balance": create_color_balance_composition,
    "multi": create_multi_overlay_composition,
    "pip": create_picture_in_picture_composition,
    "perf": create_performance_overlay_composition,
}


def get_composition(name: str):
    """Get composition function by name."""
    return COMPOSITIONS.get(name.lower())


def list_compositions():
    """List all available compositions."""
    print("Available compositions:")
    for name, func in COMPOSITIONS.items():
        doc = func.__doc__ or "No description"
        print(f"  {name:12} - {doc}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_compositions()
    else:
        print("Usage: python composition_examples.py list")
        print("This module provides composition functions for video processing.")

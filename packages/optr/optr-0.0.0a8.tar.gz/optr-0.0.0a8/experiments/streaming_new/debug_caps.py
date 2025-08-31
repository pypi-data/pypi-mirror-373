#!/usr/bin/env python3
"""Debug caps generation."""

from optr.stream.fps import FPS
from optr.stream.gstreamer import caps

def main():
    print("Testing caps generation...")
    
    # Test FPS creation
    fps = FPS(30)
    print(f"FPS object: {fps}")
    print(f"FPS string: {str(fps)}")
    
    # Test caps creation
    test_caps = caps.raw(width=640, height=480, fps=fps, format="RGB")
    print(f"Generated caps: {test_caps.to_string()}")
    
    # Compare with working caps from minimal test
    working_caps = "video/x-raw,format=RGB,width=640,height=480,framerate=30/1"
    print(f"Working caps:   {working_caps}")
    
    # Test if they're equivalent
    working_gst_caps = caps.Gst.Caps.from_string(working_caps)
    print(f"Are equal: {test_caps.is_equal(working_gst_caps)}")
    print(f"Can intersect: {test_caps.can_intersect(working_gst_caps)}")

if __name__ == "__main__":
    main()

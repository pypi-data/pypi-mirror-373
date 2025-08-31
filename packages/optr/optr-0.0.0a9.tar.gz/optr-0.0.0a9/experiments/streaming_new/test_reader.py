#!/usr/bin/env python3
"""Test the TestPatternReader in isolation."""

import time
import numpy as np
from optr.stream.gstreamer.readers import TestPatternReader

def main():
    width, height = 640, 480
    fps = 30
    
    print(f"Testing TestPatternReader...")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    
    try:
        # Create test pattern reader
        reader = TestPatternReader(width=width, height=height, fps=fps, pattern="smpte")
        print("TestPatternReader created successfully")
        
        frame_count = 0
        start_time = time.time()
        
        print("Reading frames...")
        for i in range(10):  # Read 10 frames
            frame = reader.read()
            if frame is None:
                print(f"Got None frame at {i}")
                break
                
            frame_count += 1
            print(f"Frame {frame_count}: shape={frame.shape}, dtype={frame.dtype}")
            
            # Small delay to avoid overwhelming output
            time.sleep(0.1)
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'reader' in locals():
            reader.close()
        elapsed = time.time() - start_time
        print(f"Read {frame_count} frames in {elapsed:.1f}s")

if __name__ == "__main__":
    main()

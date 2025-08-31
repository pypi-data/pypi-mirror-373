#!/usr/bin/env python3
"""Simple producer that generates test patterns and writes to shared memory."""

import time
import numpy as np
from optr.stream.gstreamer.readers import TestPatternReader
from optr.stream.gstreamer.writers import SHMWriter

def main():
    socket_path = "/tmp/test_stream.sock"
    width, height = 640, 480
    fps = 30
    
    print(f"Starting producer...")
    print(f"Socket: {socket_path}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    
    # Create test pattern reader and SHM writer
    reader = TestPatternReader(width=width, height=height, fps=fps, pattern="smpte")
    writer = SHMWriter(socket_path=socket_path, width=width, height=height, fps=fps)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        print("Producing frames... (Ctrl+C to stop)")
        while True:
            # Read frame from test pattern
            frame = reader.read()
            if frame is None:
                break
                
            # Write frame to shared memory
            writer.write(frame)
            frame_count += 1
            
            # Print stats every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Frames: {frame_count}, FPS: {actual_fps:.1f}")
                
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        reader.close()
        writer.close()
        elapsed = time.time() - start_time
        print(f"Produced {frame_count} frames in {elapsed:.1f}s")

if __name__ == "__main__":
    main()

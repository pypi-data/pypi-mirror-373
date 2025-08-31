#!/usr/bin/env python3
"""Simple producer that generates test patterns and writes to a file."""

import time
import numpy as np
from optr.stream.gstreamer.readers import TestPatternReader
from optr.stream.gstreamer.writers import FileWriter

def main():
    output_file = "/tmp/test_output.mp4"
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    
    print(f"Starting producer...")
    print(f"Output file: {output_file}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Duration: {duration}s")
    
    # Create test pattern reader and file writer
    reader = TestPatternReader(width=width, height=height, fps=fps, pattern="smpte")
    writer = FileWriter(filepath=output_file, width=width, height=height, fps=fps)
    
    frame_count = 0
    start_time = time.time()
    target_frames = fps * duration
    
    try:
        print("Producing frames...")
        while frame_count < target_frames:
            # Read frame from test pattern
            frame = reader.read()
            if frame is None:
                break
                
            # Write frame to file
            writer.write(frame)
            frame_count += 1
            
            # Print progress every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                progress = (frame_count / target_frames) * 100
                print(f"Progress: {progress:.1f}% - Frames: {frame_count}/{target_frames}, FPS: {actual_fps:.1f}")
                
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        reader.close()
        writer.close()
        elapsed = time.time() - start_time
        print(f"Produced {frame_count} frames in {elapsed:.1f}s")
        print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    main()

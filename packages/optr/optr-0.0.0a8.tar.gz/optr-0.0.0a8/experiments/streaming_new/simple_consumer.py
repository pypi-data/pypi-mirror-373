#!/usr/bin/env python3
"""Simple consumer that reads from shared memory and displays frame stats."""

import time
import numpy as np
from optr.stream.gstreamer.readers import SHMReader

def main():
    socket_path = "/tmp/test_stream.sock"
    
    print(f"Starting consumer...")
    print(f"Socket: {socket_path}")
    print("Waiting for producer to start...")
    
    # Wait for socket to exist
    import os
    while not os.path.exists(socket_path):
        time.sleep(0.1)
    
    print("Socket found, connecting...")
    
    # Create SHM reader
    reader = SHMReader(socket_path=socket_path)
    
    frame_count = 0
    start_time = time.time()
    last_stats_time = start_time
    
    try:
        print("Consuming frames... (Ctrl+C to stop)")
        while True:
            # Read frame from shared memory
            frame = reader.read()
            if frame is None:
                print("No more frames (EOS)")
                break
                
            frame_count += 1
            current_time = time.time()
            
            # Print stats every second
            if current_time - last_stats_time >= 1.0:
                elapsed = current_time - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                
                # Get frame info
                if frame is not None:
                    shape = frame.shape
                    dtype = frame.dtype
                    print(f"Frames: {frame_count}, FPS: {actual_fps:.1f}, Shape: {shape}, Type: {dtype}")
                
                last_stats_time = current_time
                
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reader.close()
        elapsed = time.time() - start_time
        print(f"Consumed {frame_count} frames in {elapsed:.1f}s")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Manual frame generation with UDPWriter."""

import sys
import time
import signal
import numpy as np

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer.writers import UDPWriter

# Global variables for cleanup
writer = None
running = True

def cleanup():
    """Clean up resources."""
    global writer
    if writer:
        writer.close()

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def generate_frame(width, height, frame_num):
    """Generate a simple test frame."""
    # Create a simple animated pattern
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create moving colored rectangles
    offset = (frame_num * 5) % width
    
    # Red rectangle
    frame[100:200, offset:offset+100] = [255, 0, 0]
    
    # Green rectangle  
    frame[300:400, (offset + 200) % width:(offset + 300) % width] = [0, 255, 0]
    
    # Blue rectangle
    frame[500:600, (offset + 400) % width:(offset + 500) % width] = [0, 0, 255]
    
    return frame

def main():
    """Main function."""
    global writer, running
    
    print("Manual Frame Generation with UDPWriter")
    print("=" * 38)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    width, height, fps = 640, 480, 30
    
    try:
        # Create UDP writer with smaller resolution
        print("Creating UDP writer...")
        writer = UDPWriter(
            host="127.0.0.1",
            port=5000,
            width=width,
            height=height,
            fps=fps,
            format="RGB",
            bitrate=1000
        )
        print("✓ UDP writer created")
        
        print("\nStreaming started...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        
        frame_count = 0
        start_time = time.time()
        frame_interval = 1.0 / fps
        
        # Main streaming loop
        while running:
            loop_start = time.time()
            
            # Generate frame manually
            frame = generate_frame(width, height, frame_count)
            
            # Write frame to UDP
            writer.write(frame)
            frame_count += 1
            
            # Print stats every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Frames: {frame_count}, FPS: {actual_fps:.1f}")
            
            # Sleep to maintain frame rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    print("Producer finished")
    return 0

if __name__ == "__main__":
    sys.exit(main())

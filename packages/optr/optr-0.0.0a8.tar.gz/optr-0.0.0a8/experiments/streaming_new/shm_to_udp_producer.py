#!/usr/bin/env python3
"""Simple producer using TestPatternReader and SHMWriter."""

import sys
import time
import signal

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer.readers import TestPatternReader
from optr.stream.gstreamer.writers import SHMWriter

# Global variables for cleanup
reader = None
writer = None
running = True

def cleanup():
    """Clean up resources."""
    global reader, writer
    if writer:
        writer.close()
    if reader:
        reader.close()

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def main():
    """Main function."""
    global reader, writer, running
    
    print("SHM Producer - TestPatternReader → SHMWriter")
    print("=" * 45)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create test pattern reader
        print("Creating test pattern reader...")
        reader = TestPatternReader(
            width=1920,
            height=1080,
            fps=30,
            pattern="ball",
            format="RGB"
        )
        print("✓ Test pattern reader created")
        
        # Create shared memory writer
        print("Creating SHM writer...")
        writer = SHMWriter(
            socket_path="/tmp/video_stream",
            width=1920,
            height=1080,
            fps=30,
            format="RGB"
        )
        print("✓ SHM writer created")
        
        print("\nStreaming started...")
        print("Socket: /tmp/video_stream")
        print("Press Ctrl+C to stop")
        
        frame_count = 0
        start_time = time.time()
        
        # Main streaming loop
        while running:
            # Read frame from test pattern
            frame = reader.read()
            if frame is None:
                print("No more frames, ending...")
                break
            
            # Make a writable copy of the frame (reader frames are read-only)
            writable_frame = frame.copy()
            writer.write(writable_frame)
            frame_count += 1
            
            # Print stats every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Frames: {frame_count}, FPS: {fps:.1f}")
        
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

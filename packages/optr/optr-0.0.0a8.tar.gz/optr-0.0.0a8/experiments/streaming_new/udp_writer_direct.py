#!/usr/bin/env python3
"""UDP producer using UDPWriter with direct videotestsrc integration."""

import sys
import time
import signal
import numpy as np

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control, buffer, caps
from optr.stream.gstreamer.writers import UDPWriter
from optr.stream.fps import FPS

# Global variables for cleanup
writer = None
test_pipe = None
running = True

def cleanup():
    """Clean up resources."""
    global writer, test_pipe
    if writer:
        writer.close()
    if test_pipe:
        control.stop_sync(test_pipe)

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def main():
    """Main function."""
    global writer, test_pipe, running
    
    print("UDP Producer using UDPWriter + Direct VideoTestSrc")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create UDP writer
        print("Creating UDP writer...")
        writer = UDPWriter(
            host="127.0.0.1",
            port=5000,
            width=640,
            height=480,
            fps=30,
            format="RGB",
            bitrate=1000
        )
        print("✓ UDP writer created")
        
        # Create videotestsrc pipeline to generate frames
        print("Creating videotestsrc pipeline...")
        src = element.videotestsrc(pattern="ball", is_live=True)
        capsfilter = element.capsfilter(
            caps=caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        )
        convert = element.videoconvert()
        sink = element.appsink(
            caps=caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        )
        
        test_pipe = pipeline.chain(src, capsfilter, convert, sink, name="videotestsrc-generator")
        control.play_sync(test_pipe)
        print("✓ VideoTestSrc pipeline created and started")
        
        print("\nStreaming started...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        
        frame_count = 0
        start_time = time.time()
        
        # Main streaming loop - pull frames from videotestsrc and push to UDPWriter
        while running:
            # Pull frame from videotestsrc pipeline
            frame = buffer.pull(sink, timeout_ns=1000000000)  # 1 second timeout
            if frame is None:
                print("No frame received, continuing...")
                continue
            
            # Write frame to UDP
            writer.write(frame)
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

#!/usr/bin/env python3
"""Test TestPatternReader with primitives UDP pipeline to confirm smooth generation."""

import sys
import time
import signal

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control, buffer, caps
from optr.stream.gstreamer.readers import TestPatternReader
from optr.stream.fps import FPS

# Global variables for cleanup
reader = None
udp_pipe = None
running = True

def cleanup():
    """Clean up resources."""
    global reader, udp_pipe
    if reader:
        reader.close()
    if udp_pipe:
        control.stop_sync(udp_pipe)

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def main():
    """Main function."""
    global reader, udp_pipe, running
    
    print("TestPatternReader → Primitives UDP Pipeline Test")
    print("=" * 48)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create TestPatternReader
        print("Creating TestPatternReader...")
        reader = TestPatternReader(
            width=640,
            height=480,
            fps=30,
            pattern="ball",
            format="RGB"
        )
        print("✓ TestPatternReader created")
        
        # Create UDP pipeline using primitives (appsrc-based but controlled)
        print("Creating UDP pipeline...")
        video_caps = caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        src = element.appsrc(caps=video_caps, is_live=True, do_timestamp=True)
        convert = element.videoconvert()
        encoder = element.x264enc(
            tune="zerolatency",
            speed_preset="ultrafast", 
            bitrate=1000
        )
        payloader = element.create("rtph264pay", {
            "config-interval": 1,
            "pt": 96
        }, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        udp_pipe = pipeline.chain(
            src, convert, encoder, payloader, sink,
            name="test-reader-udp"
        )
        print("✓ UDP pipeline created")
        
        print("\nStreaming TestPatternReader frames to UDP...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        print("\nThis tests if TestPatternReader generates smooth frames")
        
        frame_count = 0
        start_time = time.time()
        fps_ns = (1000000000 * 1) // 30  # 30 FPS in nanoseconds
        
        # Start with first frame to get pipeline flowing
        first_frame = reader.read()
        if first_frame is None:
            print("ERROR: Could not read first frame")
            return 1
        
        buffer.push(src, first_frame, 0, fps_ns)
        control.play_sync(udp_pipe)
        frame_count = 1
        print("✓ Pipeline started with first frame")
        
        # Main streaming loop
        while running:
            # Read frame from TestPatternReader
            frame = reader.read()
            if frame is None:
                print("No more frames, ending...")
                break
            
            # Push frame to UDP pipeline
            timestamp = frame_count * fps_ns
            buffer.push(src, frame, timestamp, fps_ns)
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
    
    print("Test finished")
    return 0

if __name__ == "__main__":
    sys.exit(main())

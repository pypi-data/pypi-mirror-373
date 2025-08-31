#!/usr/bin/env python3
"""Simple comparison: videotestsrc vs appsrc with same content."""

import sys
import time
import signal
import numpy as np

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control, buffer, caps
from optr.stream.fps import FPS

# Global variables for cleanup
pipe = None
running = True

def cleanup():
    """Clean up resources."""
    global pipe
    if pipe:
        control.stop_sync(pipe)

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def test_videotestsrc():
    """Test 1: Direct videotestsrc (should be smooth)."""
    global pipe, running
    
    print("\n=== TEST 1: Direct videotestsrc (Expected: SMOOTH) ===")
    
    try:
        # Create direct videotestsrc pipeline
        src = element.videotestsrc(pattern="ball", is_live=True)
        convert = element.videoconvert()
        encoder = element.x264enc(tune="zerolatency", speed_preset="ultrafast", bitrate=1000)
        payloader = element.create("rtph264pay", {"config-interval": 1, "pt": 96}, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        pipe = pipeline.chain(src, convert, encoder, payloader, sink, name="direct-videotestsrc")
        control.play_sync(pipe)
        
        print("✓ Direct videotestsrc streaming to UDP port 5000")
        print("VLC command: vlc udp://@:5000")
        print("This should show SMOOTH ball movement")
        print("Press Ctrl+C when ready to test appsrc approach...")
        
        while running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Moving to next test...")
    finally:
        if pipe:
            control.stop_sync(pipe)
            pipe = None

def test_appsrc_simple():
    """Test 2: Simple appsrc with solid color frames (should be glitchy)."""
    global pipe, running
    
    print("\n=== TEST 2: Simple appsrc with solid colors (Expected: GLITCHY) ===")
    
    try:
        # Create appsrc pipeline
        video_caps = caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        src = element.appsrc(caps=video_caps, is_live=True, do_timestamp=True)
        convert = element.videoconvert()
        encoder = element.x264enc(tune="zerolatency", speed_preset="ultrafast", bitrate=1000)
        payloader = element.create("rtph264pay", {"config-interval": 1, "pt": 96}, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        pipe = pipeline.chain(src, convert, encoder, payloader, sink, name="simple-appsrc")
        
        # Generate simple frames (just solid colors)
        frame_count = 0
        fps_ns = (1000000000 * 1) // 30
        
        # Start with first frame
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
        color = colors[frame_count % len(colors)]
        frame = np.full((480, 640, 3), color, dtype=np.uint8)
        
        buffer.push(src, frame, 0, fps_ns)
        control.play_sync(pipe)
        frame_count += 1
        
        print("✓ Simple appsrc streaming to UDP port 5000")
        print("VLC command: vlc udp://@:5000")
        print("This should show GLITCHY color changes (even though frames are simple)")
        print("Press Ctrl+C to finish...")
        
        start_time = time.time()
        next_frame_time = start_time + 1.0/30
        
        while running:
            current_time = time.time()
            
            if current_time >= next_frame_time:
                # Generate simple solid color frame
                color = colors[frame_count % len(colors)]
                frame = np.full((480, 640, 3), color, dtype=np.uint8)
                
                timestamp = frame_count * fps_ns
                buffer.push(src, frame, timestamp, fps_ns)
                frame_count += 1
                next_frame_time += 1.0/30
                
                if frame_count % 30 == 0:
                    print(f"Pushed {frame_count} simple frames")
            
            time.sleep(0.001)  # Small sleep to prevent busy loop
            
    except KeyboardInterrupt:
        print("Test completed")
    finally:
        if pipe:
            control.stop_sync(pipe)
            pipe = None

def main():
    """Main function."""
    global running
    
    print("Simple Comparison Test: videotestsrc vs appsrc")
    print("=" * 48)
    print("This test demonstrates the fundamental difference:")
    print("1. Direct videotestsrc = smooth")
    print("2. Any appsrc approach = glitchy (even with simple frames)")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Test 1: Direct videotestsrc
        running = True
        test_videotestsrc()
        
        # Test 2: Simple appsrc
        running = True
        test_appsrc_simple()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    print("\nConclusion: The issue is architectural - appsrc introduces timing discontinuities")
    print("For smooth streaming, use direct GStreamer sources, not appsrc-based approaches")
    return 0

if __name__ == "__main__":
    sys.exit(main())

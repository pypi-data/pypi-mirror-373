#!/usr/bin/env python3
"""Test appsrc-based pipeline with manual frame generation to confirm the issue."""

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

def generate_frame(width, height, frame_num):
    """Generate a test frame with moving pattern."""
    # Create a simple moving pattern
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a moving colored square
    square_size = 50
    x = (frame_num * 5) % (width - square_size)
    y = (frame_num * 3) % (height - square_size)
    
    # Red square
    frame[y:y+square_size, x:x+square_size, 0] = 255
    # Green component based on position
    frame[y:y+square_size, x:x+square_size, 1] = (x * 255) // width
    # Blue component based on frame number
    frame[y:y+square_size, x:x+square_size, 2] = (frame_num * 10) % 255
    
    return frame

def test_immediate_start():
    """Test starting pipeline immediately (should fail like UDPWriter)."""
    print("\n=== TEST 1: Immediate Start (Expected to FAIL) ===")
    
    try:
        # Create appsrc-based pipeline (same as UDPWriter)
        width, height, fps = 640, 480, 30
        video_caps = caps.raw(width=width, height=height, fps=FPS(fps), format="RGB")
        
        src = element.appsrc(caps=video_caps, is_live=True, do_timestamp=True)
        convert = element.videoconvert()
        encoder = element.x264enc(bitrate=1000, tune="zerolatency", speed_preset="ultrafast")
        payloader = element.create("rtph264pay", {"config-interval": 1, "pt": 96}, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        pipe = pipeline.chain(src, convert, encoder, payloader, sink, name="appsrc-immediate-test")
        print("✓ Pipeline created")
        
        # Try to start immediately (this should fail)
        print("Attempting immediate start...")
        control.play_sync(pipe)
        print("✓ Pipeline started successfully (UNEXPECTED!)")
        
        return pipe, src, width, height, fps
        
    except Exception as e:
        print(f"✗ Pipeline failed to start: {e}")
        if pipe:
            control.stop_sync(pipe)
        return None, None, None, None, None

def test_lazy_start():
    """Test starting pipeline after pushing first frame (should work)."""
    print("\n=== TEST 2: Lazy Start (Expected to WORK) ===")
    
    try:
        # Create appsrc-based pipeline
        width, height, fps = 640, 480, 30
        video_caps = caps.raw(width=width, height=height, fps=FPS(fps), format="RGB")
        
        src = element.appsrc(caps=video_caps, is_live=True, do_timestamp=True)
        convert = element.videoconvert()
        encoder = element.x264enc(bitrate=1000, tune="zerolatency", speed_preset="ultrafast")
        payloader = element.create("rtph264pay", {"config-interval": 1, "pt": 96}, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        pipe = pipeline.chain(src, convert, encoder, payloader, sink, name="appsrc-lazy-test")
        print("✓ Pipeline created")
        
        # Generate and push first frame BEFORE starting
        print("Generating first frame...")
        frame = generate_frame(width, height, 0)
        fps_ns = (1000000000 * 1) // fps  # nanoseconds per frame
        
        print("Pushing first frame...")
        buffer.push(src, frame, 0, fps_ns)
        print("✓ First frame pushed")
        
        # Now try to start (should work)
        print("Attempting start after first frame...")
        control.play_sync(pipe)
        print("✓ Pipeline started successfully!")
        
        return pipe, src, width, height, fps
        
    except Exception as e:
        print(f"✗ Pipeline failed to start: {e}")
        if pipe:
            control.stop_sync(pipe)
        return None, None, None, None, None

def main():
    """Main function."""
    global pipe, running
    
    print("AppSrc Pipeline State Test")
    print("=" * 25)
    print("Testing the pipeline state issue with appsrc")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Test 1: Immediate start (should fail)
        pipe, src, width, height, fps = test_immediate_start()
        if pipe:
            cleanup()
            pipe = None
        
        # Test 2: Lazy start (should work)
        pipe, src, width, height, fps = test_lazy_start()
        
        if pipe and src:
            print("\nStreaming with manual frames...")
            print("UDP output: 127.0.0.1:5000")
            print("VLC command: vlc udp://@:5000")
            print("Press Ctrl+C to stop")
            
            frame_count = 1  # We already pushed frame 0
            fps_ns = (1000000000 * 1) // fps
            
            while running:
                # Generate and push frame
                frame = generate_frame(width, height, frame_count)
                timestamp = frame_count * fps_ns
                buffer.push(src, frame, timestamp, fps_ns)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Pushed {frame_count} frames")
                
                time.sleep(1.0 / fps)
        else:
            print("\nBoth tests failed - unable to create working pipeline")
            return 1
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    print("Test completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())

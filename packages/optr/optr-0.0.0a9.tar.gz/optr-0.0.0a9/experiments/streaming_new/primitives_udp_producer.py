#!/usr/bin/env python3
"""UDP producer using our streaming primitives."""

import sys
import time
import signal

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control

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

def main():
    """Main function."""
    global pipe, running
    
    print("UDP Producer using Streaming Primitives")
    print("=" * 38)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create elements using our primitives
        print("Creating pipeline elements...")
        src = element.videotestsrc(pattern="ball", is_live=True)
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
        
        print("✓ Elements created")
        
        # Create and link pipeline using our utilities
        print("Creating pipeline...")
        pipe = pipeline.chain(
            src, convert, encoder, payloader, sink,
            name="primitives-udp-producer"
        )
        print("✓ Pipeline created and linked")
        
        # Start pipeline using our control utilities
        print("Starting pipeline...")
        control.play_sync(pipe)
        print("✓ Pipeline started successfully")
        
        print("\nStreaming directly to UDP...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while running:
            time.sleep(1)
        
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

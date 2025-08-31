#!/usr/bin/env python3
"""Simple consumer that forwards SHM stream to file for VLC playback."""

import sys
import time
import signal
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Global variables for cleanup
pipe = None
running = True

def cleanup():
    """Clean up resources."""
    global pipe
    if pipe:
        pipe.set_state(Gst.State.NULL)

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def create_consumer():
    """Create consumer using raw GStreamer calls."""
    print("Creating SHM to UDP consumer...")
    
    # Create elements manually - simple passthrough
    src = Gst.ElementFactory.make("shmsrc", "src")
    queue = Gst.ElementFactory.make("queue", "queue")
    sink = Gst.ElementFactory.make("udpsink", "sink")
    
    if not src or not queue or not sink:
        print("ERROR: Failed to create elements")
        return None
    
    # Configure elements
    src.set_property("socket-path", "/tmp/video_stream")
    src.set_property("is-live", True)
    
    # Configure queue for buffering
    queue.set_property("max-size-buffers", 200)  # Larger buffer for stability
    queue.set_property("max-size-bytes", 0)
    queue.set_property("max-size-time", 0)
    queue.set_property("leaky", 2)  # Drop old buffers if queue is full
    
    # Configure UDP sink
    sink.set_property("host", "127.0.0.1")
    sink.set_property("port", 5000)
    sink.set_property("sync", False)
    sink.set_property("async", False)
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("shm-to-udp")
    
    # Add elements to pipeline
    pipeline.add(src)
    pipeline.add(queue)
    pipeline.add(sink)
    
    # Link elements: src -> queue -> sink
    if not src.link(queue):
        print("ERROR: Failed to link src to queue")
        return None
    
    if not queue.link(sink):
        print("ERROR: Failed to link queue to sink")
        return None
    
    print("✓ Pipeline created and linked")
    return pipeline

def main():
    """Main function."""
    global pipe, running
    
    print("SHM to UDP Consumer - Raw GStreamer")
    print("=" * 35)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create pipeline
        pipe = create_consumer()
        if not pipe:
            return 1
        
        # Start pipeline
        print("Starting pipeline...")
        ret = pipe.set_state(Gst.State.PLAYING)
        
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Failed to start pipeline")
            return 1
        
        # Wait for state change
        ret, current, pending = pipe.get_state(Gst.SECOND * 5)
        if current != Gst.State.PLAYING:
            print(f"ERROR: Pipeline failed to reach PLAYING state: ret={ret}, current={current}")
            # Check for error messages
            bus = pipe.get_bus()
            msg = bus.pop_filtered(Gst.MessageType.ERROR)
            if msg:
                err, debug = msg.parse_error()
                print(f"Pipeline error: {err.message}")
                print(f"Debug info: {debug}")
            return 1
        
        print("✓ Pipeline started successfully")
        print("\nForwarding stream...")
        print("SHM source: /tmp/video_stream")
        print("UDP output: 127.0.0.1:5000")
        print("VLC command: vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        
        # Keep running and handle messages
        bus = pipe.get_bus()
        while running:
            msg = bus.pop_filtered(Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if msg:
                if msg.type == Gst.MessageType.ERROR:
                    err, debug = msg.parse_error()
                    print(f"Pipeline error: {err.message}")
                    break
                elif msg.type == Gst.MessageType.EOS:
                    print("End of stream")
                    break
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    print("Consumer finished")
    return 0

if __name__ == "__main__":
    sys.exit(main())

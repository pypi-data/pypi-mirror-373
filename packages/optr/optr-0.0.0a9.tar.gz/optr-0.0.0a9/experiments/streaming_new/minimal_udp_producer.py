#!/usr/bin/env python3
"""Minimal UDP producer that streams directly to UDP for VLC testing."""

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

def create_producer():
    """Create minimal UDP producer."""
    print("Creating minimal UDP producer...")
    
    # Create elements manually
    src = Gst.ElementFactory.make("videotestsrc", "src")
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    encoder = Gst.ElementFactory.make("x264enc", "encoder")
    payloader = Gst.ElementFactory.make("rtph264pay", "payloader")
    sink = Gst.ElementFactory.make("udpsink", "sink")
    
    if not src or not convert or not encoder or not payloader or not sink:
        print("ERROR: Failed to create elements")
        return None
    
    # Configure elements
    src.set_property("pattern", "ball")  # Moving ball pattern
    src.set_property("is-live", True)
    
    # Configure encoder for low latency
    encoder.set_property("tune", "zerolatency")
    encoder.set_property("speed-preset", "ultrafast")
    encoder.set_property("bitrate", 1000)  # 1Mbps
    
    # Configure payloader
    payloader.set_property("config-interval", 1)  # Send SPS/PPS regularly
    payloader.set_property("pt", 96)  # Payload type
    
    # Configure UDP sink
    sink.set_property("host", "127.0.0.1")
    sink.set_property("port", 5000)
    sink.set_property("sync", False)
    sink.set_property("async", False)
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("minimal-udp-producer")
    
    # Add elements to pipeline
    pipeline.add(src)
    pipeline.add(convert)
    pipeline.add(encoder)
    pipeline.add(payloader)
    pipeline.add(sink)
    
    # Link elements: src -> convert -> encoder -> payloader -> sink
    if not src.link(convert):
        print("ERROR: Failed to link src to convert")
        return None
    
    if not convert.link(encoder):
        print("ERROR: Failed to link convert to encoder")
        return None
    
    if not encoder.link(payloader):
        print("ERROR: Failed to link encoder to payloader")
        return None
    
    if not payloader.link(sink):
        print("ERROR: Failed to link payloader to sink")
        return None
    
    print("✓ Pipeline created and linked")
    return pipeline

def main():
    """Main function."""
    global pipe, running
    
    print("Minimal UDP Producer - Direct Streaming")
    print("=" * 38)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create pipeline
        pipe = create_producer()
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
        print("\nStreaming directly to UDP...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
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
    
    print("Producer finished")
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Raw GStreamer consumer without abstraction layer."""

import sys
import time
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

def create_raw_consumer():
    """Create consumer using raw GStreamer calls."""
    print("Creating raw GStreamer consumer...")
    
    # Create elements manually
    src = Gst.ElementFactory.make("shmsrc", "src")
    sink = Gst.ElementFactory.make("fakesink", "sink")
    
    if not src or not sink:
        print("ERROR: Failed to create elements")
        return None
    
    # Configure elements
    src.set_property("socket-path", "/tmp/test_stream")
    sink.set_property("sync", False)
    sink.set_property("silent", False)  # Show frame info
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("raw-consumer")
    
    # Add elements to pipeline
    pipeline.add(src)
    pipeline.add(sink)
    
    # Link elements
    if not src.link(sink):
        print("ERROR: Failed to link elements")
        return None
    
    print("Pipeline created and linked successfully")
    return pipeline

def test_consumer_states(pipeline):
    """Test consumer pipeline state transitions."""
    print("\n=== Testing Consumer State Transitions ===")
    
    # Go directly to PLAYING
    print("Setting to PLAYING...")
    ret = pipeline.set_state(Gst.State.PLAYING)
    print(f"set_state(PLAYING) returned: {ret}")
    
    ret, current, pending = pipeline.get_state(Gst.SECOND * 5)
    print(f"State: ret={ret}, current={current}, pending={pending}")
    
    if current != Gst.State.PLAYING:
        print(f"ERROR: Failed to reach PLAYING state")
        # Check for error messages
        bus = pipeline.get_bus()
        msg = bus.pop_filtered(Gst.MessageType.ERROR)
        if msg:
            err, debug = msg.parse_error()
            print(f"Pipeline error: {err.message}")
            print(f"Debug info: {debug}")
        return False
    
    print("SUCCESS: Consumer pipeline reached PLAYING state")
    return True

def run_consumer(duration_seconds=5):
    """Run the consumer for specified duration."""
    pipeline = create_raw_consumer()
    if not pipeline:
        return False
    
    # Test state transitions
    if not test_consumer_states(pipeline):
        pipeline.set_state(Gst.State.NULL)
        return False
    
    print(f"\nRunning consumer for {duration_seconds} seconds...")
    print("Listening for stream at: /tmp/test_stream")
    
    # Set up message handling
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    
    def on_message(bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print("End of stream")
            return False
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err.message}")
            print(f"Debug: {debug}")
            return False
        return True
    
    bus.connect("message", on_message)
    
    # Run for specified duration
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        # Process messages
        msg = bus.pop()
        if msg:
            if msg.type == Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                print(f"Error: {err.message}")
                break
            elif msg.type == Gst.MessageType.EOS:
                print("End of stream")
                break
        
        time.sleep(0.1)
    
    # Clean up
    print("\nStopping consumer...")
    bus.remove_signal_watch()
    pipeline.set_state(Gst.State.NULL)
    ret, current, pending = pipeline.get_state(Gst.SECOND * 5)
    print(f"Final state: ret={ret}, current={current}, pending={pending}")
    
    return True

def main():
    """Main function."""
    print("Raw GStreamer Consumer Test")
    print("=" * 30)
    print("Make sure to run raw_gst_producer.py first!")
    
    try:
        success = run_consumer(duration_seconds=10)
        if success:
            print("\nConsumer test completed successfully!")
            return 0
        else:
            print("\nConsumer test failed!")
            return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

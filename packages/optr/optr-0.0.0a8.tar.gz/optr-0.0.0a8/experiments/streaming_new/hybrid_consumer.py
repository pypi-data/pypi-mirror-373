#!/usr/bin/env python3
"""Consumer using our element utilities but raw pipeline management."""

import sys
import time
from gi.repository import Gst, GLib

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element

# Initialize GStreamer
Gst.init(None)

def create_hybrid_consumer():
    """Create consumer using our element utilities but raw pipeline management."""
    print("Creating hybrid consumer (our elements + raw pipeline)...")
    
    # Create elements using our utilities
    try:
        src = element.shmsrc(socket_path="/tmp/test_stream")
        sink = element.create("fakesink", {"sync": False, "silent": False})
        print("Elements created successfully using our utilities")
    except Exception as e:
        print(f"ERROR: Failed to create elements using utilities: {e}")
        return None
    
    # Create pipeline manually (not using our pipeline utilities)
    pipeline = Gst.Pipeline.new("hybrid-consumer")
    
    # Add elements to pipeline manually
    pipeline.add(src)
    pipeline.add(sink)
    
    # Link elements manually
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
    pipeline = create_hybrid_consumer()
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
    print("Hybrid Consumer Test (Our Elements + Raw Pipeline)")
    print("=" * 50)
    print("Make sure to run hybrid_producer.py first!")
    
    try:
        success = run_consumer(duration_seconds=10)
        if success:
            print("\nHybrid consumer test completed successfully!")
            return 0
        else:
            print("\nHybrid consumer test failed!")
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

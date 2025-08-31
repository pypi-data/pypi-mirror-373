#!/usr/bin/env python3
"""Raw GStreamer producer without abstraction layer."""

import sys
import time
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

def create_raw_producer():
    """Create producer using raw GStreamer calls."""
    print("Creating raw GStreamer producer...")
    
    # Create elements manually
    src = Gst.ElementFactory.make("videotestsrc", "src")
    sink = Gst.ElementFactory.make("shmsink", "sink")
    
    if not src or not sink:
        print("ERROR: Failed to create elements")
        return None
    
    # Configure elements
    src.set_property("pattern", "smpte")
    sink.set_property("socket-path", "/tmp/test_stream")
    sink.set_property("sync", False)
    sink.set_property("async", False)
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("raw-producer")
    
    # Add elements to pipeline
    pipeline.add(src)
    pipeline.add(sink)
    
    # Link elements
    if not src.link(sink):
        print("ERROR: Failed to link elements")
        return None
    
    print("Pipeline created and linked successfully")
    return pipeline

def test_state_transitions(pipeline):
    """Test pipeline state transitions step by step."""
    print("\n=== Testing State Transitions ===")
    
    # NULL -> READY
    print("NULL -> READY...")
    ret = pipeline.set_state(Gst.State.READY)
    print(f"set_state(READY) returned: {ret}")
    
    ret, current, pending = pipeline.get_state(Gst.SECOND * 5)
    print(f"State: ret={ret}, current={current}, pending={pending}")
    
    if current != Gst.State.READY:
        print(f"ERROR: Failed to reach READY state")
        return False
    
    # READY -> PAUSED
    print("\nREADY -> PAUSED...")
    ret = pipeline.set_state(Gst.State.PAUSED)
    print(f"set_state(PAUSED) returned: {ret}")
    
    ret, current, pending = pipeline.get_state(Gst.SECOND * 5)
    print(f"State: ret={ret}, current={current}, pending={pending}")
    
    if current != Gst.State.PAUSED:
        print(f"ERROR: Failed to reach PAUSED state")
        return False
    
    # PAUSED -> PLAYING
    print("\nPAUSED -> PLAYING...")
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
    
    print("SUCCESS: Pipeline reached PLAYING state")
    return True

def run_producer(duration_seconds=5):
    """Run the producer for specified duration."""
    pipeline = create_raw_producer()
    if not pipeline:
        return False
    
    # Test state transitions
    if not test_state_transitions(pipeline):
        pipeline.set_state(Gst.State.NULL)
        return False
    
    print(f"\nRunning producer for {duration_seconds} seconds...")
    print("Stream available at: /tmp/test_stream")
    
    # Run for specified duration
    time.sleep(duration_seconds)
    
    # Clean up
    print("\nStopping pipeline...")
    pipeline.set_state(Gst.State.NULL)
    ret, current, pending = pipeline.get_state(Gst.SECOND * 5)
    print(f"Final state: ret={ret}, current={current}, pending={pending}")
    
    return True

def main():
    """Main function."""
    print("Raw GStreamer Producer Test")
    print("=" * 30)
    
    try:
        success = run_producer(duration_seconds=10)
        if success:
            print("\nProducer test completed successfully!")
            return 0
        else:
            print("\nProducer test failed!")
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

#!/usr/bin/env python3
"""Producer using our element utilities but raw pipeline management."""

import sys
import time
from gi.repository import Gst, GLib

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element

# Initialize GStreamer
Gst.init(None)

def create_hybrid_producer():
    """Create producer using our element utilities but raw pipeline management."""
    print("Creating hybrid producer (our elements + raw pipeline)...")
    
    # Create elements using our utilities
    try:
        src = element.videotestsrc(pattern="smpte")
        sink = element.shmsink(socket_path="/tmp/test_stream")
        print("Elements created successfully using our utilities")
    except Exception as e:
        print(f"ERROR: Failed to create elements using utilities: {e}")
        return None
    
    # Create pipeline manually (not using our pipeline utilities)
    pipeline = Gst.Pipeline.new("hybrid-producer")
    
    # Add elements to pipeline manually
    pipeline.add(src)
    pipeline.add(sink)
    
    # Link elements manually
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
    pipeline = create_hybrid_producer()
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
    print("Hybrid Producer Test (Our Elements + Raw Pipeline)")
    print("=" * 50)
    
    try:
        success = run_producer(duration_seconds=10)
        if success:
            print("\nHybrid producer test completed successfully!")
            return 0
        else:
            print("\nHybrid producer test failed!")
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

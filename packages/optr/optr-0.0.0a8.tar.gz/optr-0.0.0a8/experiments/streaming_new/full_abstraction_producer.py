#!/usr/bin/env python3
"""Producer using full abstraction layer (our elements + our pipeline utilities)."""

import sys
import time
from gi.repository import Gst, GLib

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control

# Initialize GStreamer
Gst.init(None)

def create_full_abstraction_producer():
    """Create producer using full abstraction layer."""
    print("Creating producer using full abstraction layer...")
    
    # Create elements using our utilities
    try:
        src = element.videotestsrc(pattern="smpte")
        sink = element.shmsink(socket_path="/tmp/test_stream", sync=False, **{"async": False})
        print("Elements created successfully using our utilities")
    except Exception as e:
        print(f"ERROR: Failed to create elements using utilities: {e}")
        return None
    
    # Create pipeline using our utilities
    try:
        pipe = pipeline.chain(src, sink, name="full-abstraction-producer")
        print("Pipeline created successfully using our utilities")
        return pipe
    except Exception as e:
        print(f"ERROR: Failed to create pipeline using utilities: {e}")
        return None

def test_control_play_sync(pipe):
    """Test our control.play_sync function."""
    print("\n=== Testing control.play_sync ===")
    
    try:
        control.play_sync(pipe)
        print("SUCCESS: control.play_sync completed successfully")
        return True
    except Exception as e:
        print(f"ERROR: control.play_sync failed: {e}")
        
        # Get current state for debugging
        try:
            ret, current, pending = pipe.get_state(Gst.SECOND)
            print(f"Current pipeline state: ret={ret}, current={current}, pending={pending}")
        except Exception as state_e:
            print(f"Could not get pipeline state: {state_e}")
        
        # Check for error messages
        try:
            bus = pipe.get_bus()
            msg = bus.pop_filtered(Gst.MessageType.ERROR)
            if msg:
                err, debug = msg.parse_error()
                print(f"Pipeline error: {err.message}")
                print(f"Debug info: {debug}")
        except Exception as bus_e:
            print(f"Could not check bus messages: {bus_e}")
        
        return False

def run_producer(duration_seconds=5):
    """Run the producer for specified duration."""
    pipe = create_full_abstraction_producer()
    if not pipe:
        return False
    
    # Test our control utilities
    if not test_control_play_sync(pipe):
        try:
            control.stop_sync(pipe)
        except:
            pass
        return False
    
    print(f"\nRunning producer for {duration_seconds} seconds...")
    print("Stream available at: /tmp/test_stream")
    
    # Run for specified duration
    time.sleep(duration_seconds)
    
    # Clean up using our utilities
    print("\nStopping pipeline...")
    try:
        control.stop_sync(pipe)
        print("Pipeline stopped successfully using our utilities")
    except Exception as e:
        print(f"ERROR: Failed to stop pipeline using utilities: {e}")
    
    return True

def main():
    """Main function."""
    print("Full Abstraction Producer Test (Our Elements + Our Pipeline)")
    print("=" * 60)
    
    try:
        success = run_producer(duration_seconds=10)
        if success:
            print("\nFull abstraction producer test completed successfully!")
            return 0
        else:
            print("\nFull abstraction producer test failed!")
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

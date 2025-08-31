#!/usr/bin/env python3
"""Debug TestPatternReader buffer format issues."""

import sys
import numpy as np
from gi.repository import Gst, GstVideo

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer.readers import TestPatternReader
from optr.stream.fps import FPS

# Initialize GStreamer
Gst.init(None)

def test_basic_reader():
    """Test basic TestPatternReader functionality."""
    print("=== Testing Basic TestPatternReader ===")
    
    try:
        reader = TestPatternReader(
            width=640,
            height=480,
            fps=30,
            pattern="smpte",
            format="RGB"
        )
        print("TestPatternReader created successfully")
        
        # Try to read a frame
        print("Attempting to read frame...")
        frame = reader.read()
        
        if frame is not None:
            print(f"SUCCESS: Got frame with shape {frame.shape}, dtype {frame.dtype}")
            print(f"Frame min/max values: {frame.min()}/{frame.max()}")
            
            # Verify expected shape
            expected_shape = (480, 640, 3)  # H, W, C for RGB
            if frame.shape == expected_shape:
                print(f"✓ Frame shape matches expected {expected_shape}")
            else:
                print(f"✗ Frame shape {frame.shape} doesn't match expected {expected_shape}")
        else:
            print("ERROR: Got None frame")
            return False
        
        # Try reading a few more frames
        print("Reading additional frames...")
        for i in range(3):
            frame = reader.read()
            if frame is not None:
                print(f"Frame {i+2}: shape {frame.shape}")
            else:
                print(f"Frame {i+2}: None")
                break
        
        # Clean up
        reader.close()
        print("Reader closed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_formats():
    """Test TestPatternReader with different pixel formats."""
    print("\n=== Testing Different Pixel Formats ===")
    
    formats = ["RGB", "BGR", "RGBA", "BGRA"]
    results = {}
    
    for fmt in formats:
        print(f"\nTesting format: {fmt}")
        try:
            reader = TestPatternReader(
                width=320,
                height=240,
                fps=30,
                pattern="smpte",
                format=fmt
            )
            
            frame = reader.read()
            if frame is not None:
                expected_channels = 4 if fmt.endswith('A') else 3
                expected_shape = (240, 320, expected_channels)
                
                print(f"  Got frame: shape {frame.shape}, dtype {frame.dtype}")
                if frame.shape == expected_shape:
                    print(f"  ✓ Shape matches expected {expected_shape}")
                    results[fmt] = "SUCCESS"
                else:
                    print(f"  ✗ Shape {frame.shape} doesn't match expected {expected_shape}")
                    results[fmt] = f"SHAPE_MISMATCH: got {frame.shape}, expected {expected_shape}"
            else:
                print(f"  ✗ Got None frame")
                results[fmt] = "NULL_FRAME"
            
            reader.close()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results[fmt] = f"EXCEPTION: {e}"
    
    print(f"\nFormat test results:")
    for fmt, result in results.items():
        print(f"  {fmt}: {result}")
    
    return results

def test_caps_negotiation():
    """Test caps negotiation in TestPatternReader pipeline."""
    print("\n=== Testing Caps Negotiation ===")
    
    try:
        from optr.stream.gstreamer import element, caps
        from optr.stream.fps import FPS
        
        # Create elements manually to inspect caps
        src = element.videotestsrc(pattern="smpte")
        capsfilter = element.capsfilter(
            caps=caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        )
        convert = element.videoconvert()
        sink = element.appsink(
            caps=caps.raw(width=640, height=480, fps=FPS(30), format="RGB")
        )
        
        print("Elements created successfully")
        
        # Create pipeline
        from optr.stream.gstreamer import pipeline, control
        pipe = pipeline.chain(src, capsfilter, convert, sink, name="caps-test")
        print("Pipeline created successfully")
        
        # Start pipeline
        control.play_sync(pipe)
        print("Pipeline started successfully")
        
        # Try to pull a sample
        sample = sink.emit("try-pull-sample", Gst.SECOND)
        if sample:
            caps = sample.get_caps()
            print(f"Sample caps: {caps.to_string()}")
            
            buffer = sample.get_buffer()
            print(f"Buffer size: {buffer.get_size()} bytes")
            
            # Try to get video info
            info = GstVideo.VideoInfo()
            if info.from_caps(caps):
                print(f"Video format: {info.finfo.format}")
                print(f"Dimensions: {info.width}x{info.height}")
                print(f"Stride: {info.stride}")
            else:
                print("Could not parse video info from caps")
        else:
            print("No sample available")
        
        control.stop_sync(pipe)
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("TestPatternReader Buffer Format Debugging")
    print("=" * 50)
    
    tests = [
        test_basic_reader,
        test_different_formats,
        test_caps_negotiation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    if all(results):
        print("\nAll tests passed!")
        return 0
    else:
        print(f"\n{sum(results)}/{len(results)} tests passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

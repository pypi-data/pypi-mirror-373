#!/usr/bin/env python3
"""Test safer buffer handling to avoid memory corruption."""

import sys
import numpy as np
from gi.repository import Gst, GstVideo

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control, caps
from optr.stream.fps import FPS

# Initialize GStreamer
Gst.init(None)

def safe_pull_sample(appsink: Gst.Element, timeout_ns: int = Gst.SECOND) -> np.ndarray | None:
    """
    Safer version of buffer pulling with better error handling and size validation.
    """
    sample = appsink.emit("try-pull-sample", timeout_ns)
    if not sample:
        return None

    try:
        buf = sample.get_buffer()
        caps = sample.get_caps()
        
        print(f"Sample caps: {caps.to_string()}")
        print(f"Buffer size: {buf.get_size()} bytes")

        info = GstVideo.VideoInfo()
        if not info.from_caps(caps):
            raise RuntimeError("Unsupported caps for VideoInfo")

        print(f"Video format: {info.finfo.format}")
        print(f"Dimensions: {info.width}x{info.height}")
        print(f"Stride: {info.stride}")
        print(f"Size from info: {info.size}")

        fmt = info.finfo.format
        if fmt in (GstVideo.VideoFormat.RGB, GstVideo.VideoFormat.BGR):
            channels = 3
        elif fmt in (
            GstVideo.VideoFormat.RGBA,
            GstVideo.VideoFormat.BGRA,
            GstVideo.VideoFormat.ARGB,
            GstVideo.VideoFormat.ABGR,
        ):
            channels = 4
        elif fmt == GstVideo.VideoFormat.GRAY8:
            channels = 1
        else:
            raise NotImplementedError(
                f"Unsupported pixel format: {fmt!r} (use videoconvert to RGB/RGBA)"
            )

        # Validate buffer size matches expected size
        expected_size = info.height * info.stride[0]
        actual_size = buf.get_size()
        
        print(f"Expected buffer size: {expected_size}")
        print(f"Actual buffer size: {actual_size}")
        
        if actual_size < expected_size:
            raise RuntimeError(f"Buffer too small: got {actual_size}, expected {expected_size}")

        ok, mapinfo = buf.map(Gst.MapFlags.READ)
        if not ok:
            raise RuntimeError("Failed to map buffer for READ")

        try:
            # Use the smaller of the two sizes to avoid reading beyond buffer
            safe_size = min(mapinfo.size, expected_size)
            print(f"Using safe size: {safe_size}")
            
            data = np.frombuffer(mapinfo.data, dtype=np.uint8, count=safe_size).copy()
            print(f"Copied {len(data)} bytes")
        finally:
            buf.unmap(mapinfo)

        rowstride = info.stride[0]
        width_bytes = info.width * channels
        
        print(f"Row stride: {rowstride}")
        print(f"Width in bytes: {width_bytes}")

        # Validate dimensions before reshaping
        if len(data) < info.height * rowstride:
            raise RuntimeError(f"Not enough data for reshape: got {len(data)}, need {info.height * rowstride}")

        # Reshape to (H, stride) then crop to width_bytes
        try:
            data = data.reshape((info.height, rowstride))
            print(f"Reshaped to: {data.shape}")
            
            # Crop to actual width
            data = data[:, :width_bytes]
            print(f"Cropped to: {data.shape}")
            
            # Final reshape to (H, W, C)
            frame = data.reshape((info.height, info.width, channels))
            print(f"Final shape: {frame.shape}")
            
            return frame
        except ValueError as e:
            print(f"Reshape error: {e}")
            print(f"Data length: {len(data)}")
            print(f"Trying to reshape to: ({info.height}, {rowstride})")
            raise
            
    except Exception as e:
        print(f"Error in safe_pull_sample: {e}")
        raise
    finally:
        try:
            sample.unref()
        except Exception:
            pass

def test_safe_buffer_pull():
    """Test the safer buffer pulling approach."""
    print("=== Testing Safe Buffer Pull ===")
    
    try:
        # Create a simple test pipeline
        src = element.videotestsrc(pattern="smpte")
        capsfilter = element.capsfilter(
            caps=caps.raw(width=320, height=240, fps=FPS(30), format="RGB")
        )
        convert = element.videoconvert()
        sink = element.appsink(
            caps=caps.raw(width=320, height=240, fps=FPS(30), format="RGB")
        )
        
        print("Elements created successfully")
        
        # Create and start pipeline
        pipe = pipeline.chain(src, capsfilter, convert, sink, name="safe-test")
        print("Pipeline created successfully")
        
        control.play_sync(pipe)
        print("Pipeline started successfully")
        
        # Try to pull a sample safely
        print("\nAttempting to pull sample...")
        frame = safe_pull_sample(sink)
        
        if frame is not None:
            print(f"SUCCESS: Got frame with shape {frame.shape}, dtype {frame.dtype}")
            print(f"Frame min/max values: {frame.min()}/{frame.max()}")
        else:
            print("No frame available")
        
        control.stop_sync(pipe)
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the safe buffer test."""
    print("Safe Buffer Pull Test")
    print("=" * 30)
    
    try:
        success = test_safe_buffer_pull()
        if success:
            print("\nSafe buffer test completed successfully!")
            return 0
        else:
            print("\nSafe buffer test failed!")
            return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

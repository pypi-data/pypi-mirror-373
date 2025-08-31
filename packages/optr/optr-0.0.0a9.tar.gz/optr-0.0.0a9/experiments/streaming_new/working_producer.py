#!/usr/bin/env python3
"""Working producer using the minimal test approach."""

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")
from gi.repository import Gst, GstVideo
import time
import numpy as np

def main():
    Gst.init(None)
    
    print("Starting working producer...")
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("producer-pipeline")
    
    # Create elements
    src = Gst.ElementFactory.make("videotestsrc", "src")
    src.set_property("pattern", "smpte")
    
    # Create caps filter
    caps_str = "video/x-raw,format=RGB,width=640,height=480,framerate=30/1"
    caps = Gst.Caps.from_string(caps_str)
    capsfilter = Gst.ElementFactory.make("capsfilter", "caps")
    capsfilter.set_property("caps", caps)
    
    # Create converter and sink
    convert = Gst.ElementFactory.make("videoconvert", "convert")
    sink = Gst.ElementFactory.make("appsink", "sink")
    sink.set_property("emit-signals", True)
    sink.set_property("max-buffers", 1)
    sink.set_property("caps", caps)
    
    # Add and link elements
    pipeline.add(src)
    pipeline.add(capsfilter)
    pipeline.add(convert)
    pipeline.add(sink)
    
    src.link(capsfilter)
    capsfilter.link(convert)
    convert.link(sink)
    
    # Start pipeline
    pipeline.set_state(Gst.State.PLAYING)
    ret, state, pending = pipeline.get_state(Gst.SECOND * 5)
    
    if ret != Gst.StateChangeReturn.SUCCESS:
        print(f"Failed to start pipeline: ret={ret}")
        return
    
    print("Pipeline started successfully")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        print("Reading frames... (Ctrl+C to stop)")
        while frame_count < 100:  # Read 100 frames
            sample = sink.emit("try-pull-sample", Gst.SECOND)
            if not sample:
                print("No sample available")
                break
            
            # Extract frame data
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            
            # Get video info
            info = GstVideo.VideoInfo()
            if not info.from_caps(caps):
                print("Failed to get video info")
                break
            
            # Map buffer and extract frame
            ok, mapinfo = buffer.map(Gst.MapFlags.READ)
            if not ok:
                print("Failed to map buffer")
                break
            
            try:
                # Convert to numpy array
                data = np.frombuffer(mapinfo.data, dtype=np.uint8, count=info.size).copy()
                frame = data.reshape((info.height, info.width, 3))  # RGB = 3 channels
                
                frame_count += 1
                
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"Frame {frame_count}: shape={frame.shape}, FPS={fps:.1f}")
                
            finally:
                buffer.unmap(mapinfo)
                # sample.unref() is not needed in Python bindings
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)
        elapsed = time.time() - start_time
        print(f"Processed {frame_count} frames in {elapsed:.1f}s")

if __name__ == "__main__":
    main()

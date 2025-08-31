#!/usr/bin/env python3
"""Minimal test using raw GStreamer to debug the issue."""

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import time

def main():
    Gst.init(None)
    
    print("Creating minimal GStreamer pipeline...")
    
    # Create pipeline
    pipeline = Gst.Pipeline.new("test-pipeline")
    
    # Create elements
    src = Gst.ElementFactory.make("videotestsrc", "src")
    src.set_property("pattern", "smpte")
    
    # Create caps filter to force RGB format
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
    
    # Add elements to pipeline
    pipeline.add(src)
    pipeline.add(capsfilter)
    pipeline.add(convert)
    pipeline.add(sink)
    
    # Link elements
    if not src.link(capsfilter):
        print("Failed to link src -> capsfilter")
        return
    if not capsfilter.link(convert):
        print("Failed to link capsfilter -> convert")
        return
    if not convert.link(sink):
        print("Failed to link convert -> sink")
        return
    
    print("Pipeline linked successfully")
    
    # Set to playing
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Failed to set pipeline to PLAYING")
        return
    
    print("Pipeline set to PLAYING")
    
    # Wait for state change
    ret, state, pending = pipeline.get_state(Gst.SECOND * 5)
    if ret != Gst.StateChangeReturn.SUCCESS:
        print(f"Failed to reach PLAYING state: ret={ret}, state={state}")
        return
    
    print("Pipeline reached PLAYING state")
    
    # Try to pull a sample
    sample = sink.emit("try-pull-sample", Gst.SECOND)
    if sample:
        print("Successfully pulled sample!")
        caps = sample.get_caps()
        print(f"Sample caps: {caps.to_string()}")
        
        buffer = sample.get_buffer()
        print(f"Buffer size: {buffer.get_size()}")
    else:
        print("Failed to pull sample")
    
    # Cleanup
    pipeline.set_state(Gst.State.NULL)
    print("Test completed")

if __name__ == "__main__":
    main()

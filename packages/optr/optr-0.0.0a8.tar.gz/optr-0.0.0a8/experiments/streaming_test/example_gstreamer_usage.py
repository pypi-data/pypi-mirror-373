"""Example showing how to use GStreamer buffer for shmsrc integration."""

import numpy as np
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def example_basic_usage():
    """Basic example of GStreamer buffer usage."""
    print("=== GStreamer Buffer Usage Example ===")
    print()
    
    print("1. Import the GStreamer buffer:")
    print("   from optr.stream import create_gstreamer_buffer")
    print()
    
    print("2. Create a GStreamer buffer:")
    print("   buffer = create_gstreamer_buffer('/tmp/my-stream', 640, 480, fps=30)")
    print()
    
    print("3. Write frames to the buffer:")
    print("   for frame in frame_generator():")
    print("       buffer.write(frame)  # Automatically starts GStreamer pipeline")
    print()
    
    print("4. GStreamer can read with shmsrc:")
    print("   gst-launch-1.0 shmsrc socket-path=/tmp/my-stream \\")
    print("     ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 \\")
    print("     ! videoconvert ! autovideosink")
    print()
    
    print("5. Or save to file:")
    print("   gst-launch-1.0 shmsrc socket-path=/tmp/my-stream \\")
    print("     ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 \\")
    print("     ! videoconvert ! x264enc ! mp4mux \\")
    print("     ! filesink location=output.mp4")
    print()


def example_with_simulation():
    """Example showing integration with simulation rendering."""
    print("=== Integration with Simulation Example ===")
    print()
    
    print("```python")
    print("# In your simulation loop:")
    print("from optr.stream import create_gstreamer_buffer")
    print()
    print("# Create buffer for streaming")
    print("stream_buffer = create_gstreamer_buffer('/tmp/sim-stream', 1920, 1080, fps=60)")
    print()
    print("# In your render loop:")
    print("while simulation_running:")
    print("    # Render frame")
    print("    frame = renderer.render()  # Returns RGB numpy array")
    print("    ")
    print("    # Stream to GStreamer")
    print("    stream_buffer.write(frame)")
    print("    ")
    print("    # Continue simulation...")
    print("    simulation.step()")
    print()
    print("# Cleanup")
    print("stream_buffer.close()")
    print("```")
    print()


def example_multiple_outputs():
    """Example showing multiple GStreamer outputs."""
    print("=== Multiple GStreamer Outputs Example ===")
    print()
    
    print("You can create multiple buffers for different purposes:")
    print()
    print("```python")
    print("# High-quality recording buffer")
    print("record_buffer = create_gstreamer_buffer('/tmp/record', 1920, 1080, fps=60)")
    print()
    print("# Low-latency streaming buffer")
    print("stream_buffer = create_gstreamer_buffer('/tmp/stream', 640, 480, fps=30)")
    print()
    print("# Write same frame to both")
    print("for frame in frames:")
    print("    # Write full resolution for recording")
    print("    record_buffer.write(frame)")
    print("    ")
    print("    # Resize and write for streaming")
    print("    small_frame = cv2.resize(frame, (640, 480))")
    print("    stream_buffer.write(small_frame)")
    print("```")
    print()
    
    print("Then use separate GStreamer pipelines:")
    print("# Recording pipeline:")
    print("gst-launch-1.0 shmsrc socket-path=/tmp/record ! ... ! filesink location=recording.mp4")
    print()
    print("# Streaming pipeline:")
    print("gst-launch-1.0 shmsrc socket-path=/tmp/stream ! ... ! rtmpsink location=rtmp://...")
    print()


def show_troubleshooting():
    """Show troubleshooting information."""
    print("=== Troubleshooting GStreamer Setup ===")
    print()
    
    print("If you see GLib/GObject errors on macOS:")
    print("1. Install GStreamer via Homebrew:")
    print("   brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad")
    print()
    
    print("2. Install PyGObject:")
    print("   pip install PyGObject")
    print()
    
    print("3. Set environment variables if needed:")
    print("   export PKG_CONFIG_PATH=/opt/homebrew/lib/pkgconfig")
    print("   export GI_TYPELIB_PATH=/opt/homebrew/lib/girepository-1.0")
    print()
    
    print("4. Test GStreamer installation:")
    print("   gst-launch-1.0 videotestsrc ! autovideosink")
    print()


if __name__ == "__main__":
    example_basic_usage()
    example_with_simulation()
    example_multiple_outputs()
    show_troubleshooting()
    
    print("=== Summary ===")
    print("The GStreamer buffer provides:")
    print("✓ True shared memory integration with GStreamer")
    print("✓ Zero-copy frame transfer")
    print("✓ Automatic pipeline management")
    print("✓ Compatible with all GStreamer tools and pipelines")
    print("✓ Support for multiple concurrent streams")
    print()
    print("Use create_gstreamer_buffer() when you need to feed frames")
    print("to GStreamer's shmsrc for further processing or streaming.")

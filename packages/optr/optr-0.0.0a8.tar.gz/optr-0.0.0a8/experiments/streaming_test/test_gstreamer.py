"""GStreamer buffer test - test shmsink/shmsrc integration."""

import numpy as np
import time
import subprocess
import threading
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from optr.stream import create_gstreamer_buffer
    GSTREAMER_AVAILABLE = True
except ImportError as e:
    print(f"GStreamer not available: {e}")
    GSTREAMER_AVAILABLE = False


def generate_test_frame(width: int = 320, height: int = 240, frame_num: int = 0):
    """Generate a test frame with moving pattern."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a moving diagonal pattern
    t = frame_num / 30.0
    
    for y in range(height):
        for x in range(width):
            # Moving diagonal stripes
            stripe = (x + y + int(t * 50)) % 40
            if stripe < 20:
                frame[y, x] = [255, 100, 50]  # Orange
            else:
                frame[y, x] = [50, 100, 255]  # Blue
    
    # Add a moving dot
    dot_x = int((width // 2) + 50 * np.sin(t * 2))
    dot_y = int((height // 2) + 30 * np.cos(t * 2))
    
    if 0 <= dot_x < width and 0 <= dot_y < height:
        # Draw a small circle
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                if dx*dx + dy*dy <= 25:  # Circle radius 5
                    px, py = dot_x + dx, dot_y + dy
                    if 0 <= px < width and 0 <= py < height:
                        frame[py, px] = [255, 255, 255]  # White dot
    
    return frame


def test_gstreamer_buffer_basic():
    """Test basic GStreamer buffer functionality."""
    if not GSTREAMER_AVAILABLE:
        print("⚠️  GStreamer not available, skipping test")
        return True
    
    print("=== GStreamer Buffer Basic Test ===")
    
    socket_path = "/tmp/gst-test-stream"
    width, height = 320, 240
    fps = 30.0
    
    try:
        # Create GStreamer buffer
        buffer = create_gstreamer_buffer(socket_path, width, height, fps)
        print(f"✓ GStreamer buffer created: {socket_path}")
        
        # Write some test frames
        print("Writing test frames...")
        for i in range(30):  # 1 second at 30fps
            frame = generate_test_frame(width, height, i)
            buffer.write(frame)
            if i % 10 == 0:
                print(f"  Written frame {i}")
            time.sleep(1.0 / fps)  # Maintain frame rate
        
        print("✓ Frames written successfully")
        
        # Close buffer
        buffer.close()
        print("✓ Buffer closed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gstreamer_pipeline_integration():
    """Test GStreamer buffer with actual shmsrc pipeline."""
    if not GSTREAMER_AVAILABLE:
        print("⚠️  GStreamer not available, skipping test")
        return True
    
    print("=== GStreamer Pipeline Integration Test ===")
    
    socket_path = "/tmp/gst-pipeline-test"
    width, height = 320, 240
    fps = 30.0
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "gstreamer_test.mp4"
    
    try:
        # Create GStreamer buffer
        buffer = create_gstreamer_buffer(socket_path, width, height, fps)
        print(f"✓ GStreamer buffer created: {socket_path}")
        
        # Start a GStreamer pipeline to read from shmsrc and save to file
        gst_cmd = [
            "gst-launch-1.0", "-e",
            "shmsrc", f"socket-path={socket_path}",
            "!", f"video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1",
            "!", "videoconvert",
            "!", "x264enc", "tune=zerolatency",
            "!", "mp4mux",
            "!", "filesink", f"location={output_file}"
        ]
        
        print("Starting GStreamer pipeline...")
        print(" ".join(gst_cmd))
        
        # Start the pipeline in background
        gst_process = subprocess.Popen(
            gst_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give pipeline time to start
        time.sleep(1.0)
        
        # Write frames to buffer
        print("Writing frames to buffer...")
        frame_count = 90  # 3 seconds at 30fps
        
        def write_frames():
            try:
                for i in range(frame_count):
                    frame = generate_test_frame(width, height, i)
                    buffer.write(frame)
                    if i % 30 == 0:
                        print(f"  Written frame {i}/{frame_count}")
                    time.sleep(1.0 / fps)
                
                # Close buffer to signal end
                buffer.close()
                print("✓ All frames written, buffer closed")
                
            except Exception as e:
                print(f"✗ Error writing frames: {e}")
        
        # Start writing frames in separate thread
        writer_thread = threading.Thread(target=write_frames)
        writer_thread.start()
        
        # Wait for writing to complete
        writer_thread.join()
        
        # Wait a bit more for pipeline to finish
        time.sleep(2.0)
        
        # Terminate GStreamer pipeline
        gst_process.terminate()
        try:
            gst_process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            gst_process.kill()
        
        # Check if output file was created
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"✓ Output file created: {output_file.name} ({size} bytes)")
            return True
        else:
            print("✗ Output file not created")
            return False
            
    except FileNotFoundError:
        print("⚠️  gst-launch-1.0 not found, skipping pipeline test")
        return True  # Don't fail if GStreamer CLI tools aren't available
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gstreamer_display_pipeline():
    """Test GStreamer buffer with display pipeline (manual verification)."""
    if not GSTREAMER_AVAILABLE:
        print("⚠️  GStreamer not available, skipping test")
        return True
    
    print("=== GStreamer Display Pipeline Test ===")
    print("This test will show a window with animated pattern for 3 seconds")
    print("Close the window or wait for it to close automatically")
    
    socket_path = "/tmp/gst-display-test"
    width, height = 320, 240
    fps = 30.0
    
    try:
        # Create GStreamer buffer
        buffer = create_gstreamer_buffer(socket_path, width, height, fps)
        print(f"✓ GStreamer buffer created: {socket_path}")
        
        # Start display pipeline
        gst_cmd = [
            "gst-launch-1.0", "-e",
            "shmsrc", f"socket-path={socket_path}",
            "!", f"video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1",
            "!", "videoconvert",
            "!", "autovideosink"
        ]
        
        print("Starting display pipeline...")
        
        # Start the pipeline
        gst_process = subprocess.Popen(
            gst_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give pipeline time to start
        time.sleep(1.0)
        
        # Write frames
        print("Displaying animated pattern...")
        for i in range(90):  # 3 seconds
            frame = generate_test_frame(width, height, i)
            buffer.write(frame)
            time.sleep(1.0 / fps)
        
        # Close buffer
        buffer.close()
        print("✓ Animation complete")
        
        # Wait for pipeline to finish
        time.sleep(1.0)
        gst_process.terminate()
        try:
            gst_process.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            gst_process.kill()
        
        return True
        
    except FileNotFoundError:
        print("⚠️  gst-launch-1.0 not found, skipping display test")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    if not GSTREAMER_AVAILABLE:
        print("GStreamer Python bindings not available!")
        print("Install with: pip install PyGObject")
        sys.exit(1)
    
    print("Running GStreamer integration tests...\n")
    
    success1 = test_gstreamer_buffer_basic()
    print()
    success2 = test_gstreamer_pipeline_integration()
    print()
    success3 = test_gstreamer_display_pipeline()
    
    if success1 and success2 and success3:
        print("\n✓ All GStreamer tests passed!")
    else:
        print("\n✗ Some GStreamer tests failed!")
        sys.exit(1)

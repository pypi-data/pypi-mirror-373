#!/usr/bin/env python3
"""Test the fixed SHMSink implementation with proper timestamps."""

import sys
import time
import subprocess
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer.shmsink import SHMSink


def create_test_frame(width, height, frame_num):
    """Create a test frame with moving patterns."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Moving gradient
    t = frame_num / 30.0
    for y in range(height):
        for x in range(width):
            r = int(128 + 127 * np.sin(0.01 * x + t))
            g = int(128 + 127 * np.sin(0.01 * y + t * 1.2))
            b = int(128 + 127 * np.sin(0.01 * (x + y) + t * 0.8))
            frame[y, x] = [r, g, b]
    
    # Frame counter bar
    bar_height = min(frame_num % 100, height - 20)
    frame[height-20:height-20+bar_height, 10:30] = [255, 255, 255]
    
    # Frame number display (simple bars)
    hundreds = (frame_num // 100) % 10
    tens = (frame_num // 10) % 10
    ones = frame_num % 10
    
    # Display as vertical bars
    frame[50:50+hundreds*5, 50:60] = [255, 0, 0]  # Red
    frame[50:50+tens*5, 70:80] = [0, 255, 0]     # Green  
    frame[50:50+ones*5, 90:100] = [0, 0, 255]    # Blue
    
    return frame


def main():
    """Test fixed SHMSink implementation."""
    socket_path = "/tmp/test-fixed-shm"
    width, height = 640, 480
    fps = 30.0
    
    print("🔧 Testing Fixed SHMSink Implementation")
    print("=" * 50)
    print(f"Socket: {socket_path}")
    print(f"Resolution: {width}x{height} @ {fps} FPS")
    print()
    
    # Create sink
    print("📡 Creating fixed SHMSink...")
    sink = SHMSink(socket_path, width, height, fps)
    
    # Start sink
    print("🚀 Starting sink...")
    sink.start()
    
    # Wait for socket to be ready
    time.sleep(1.0)
    
    # Start GStreamer viewer automatically
    print("📺 Starting GStreamer viewer...")
    gst_cmd = [
        "gst-launch-1.0", "-e",
        "shmsrc", f"socket-path={socket_path}",
        "!", f"video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1",
        "!", "videoconvert",
        "!", "autovideosink"
    ]
    
    gst_process = subprocess.Popen(
        gst_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give GStreamer time to start
    time.sleep(2.0)
    
    print("🎬 Streaming test pattern...")
    print("You should see:")
    print("- Smooth animated gradient background")
    print("- White frame counter bar (bottom left)")
    print("- RGB frame number bars (top left)")
    print("- No 'invalid video buffer' errors")
    print()
    print("This will run for 10 seconds...")
    print()
    
    try:
        frame_count = 0
        start_time = time.time()
        target_frames = 300  # 10 seconds at 30fps
        
        while frame_count < target_frames:
            # Create test frame
            frame = create_test_frame(width, height, frame_count)
            
            # Write to sink
            sink.write(frame)
            
            # Progress updates
            if frame_count % 60 == 0:  # Every 2 seconds
                elapsed = time.time() - start_time
                print(f"Frame {frame_count}/{target_frames} - {elapsed:.1f}s elapsed")
            
            frame_count += 1
            
            # Sleep to maintain frame rate
            time.sleep(1.0 / fps)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping test...")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        
        # Stop GStreamer
        gst_process.terminate()
        try:
            gst_process.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            gst_process.kill()
        
        # Close sink
        sink.close()
        
        elapsed = time.time() - start_time
        print(f"✅ Test complete!")
        print(f"Streamed {frame_count} frames in {elapsed:.1f}s")
        print(f"Average FPS: {frame_count/elapsed:.1f}")
        
        # Check for errors
        stdout, stderr = gst_process.communicate()
        if stderr:
            print("\n⚠️  GStreamer stderr output:")
            print(stderr.decode())
        else:
            print("✅ No GStreamer errors detected!")


if __name__ == "__main__":
    main()

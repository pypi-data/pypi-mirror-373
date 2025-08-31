"""Test simple streaming: GStreamer + clip recording."""

import time
import numpy as np
from optr.core.io import fanout
from optr.stream import SHMSink, ClipRecorder


def generate_test_frames(width: int = 640, height: int = 480, count: int = 300):
    """Generate test frames with moving pattern."""
    for i in range(count):
        # Create a frame with moving pattern
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add moving rectangle
        x = int((i * 2) % width)
        y = int((i * 1) % height)
        
        # Draw rectangle (BGR format for OpenCV)
        cv2_available = True
        try:
            import cv2
            cv2.rectangle(frame, (x, y), (x + 50, y + 50), (0, 255, 0), -1)
            # Add frame number text
            cv2.putText(frame, f"Frame {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        except ImportError:
            # Fallback without OpenCV
            frame[y:min(y+50, height), x:min(x+50, width)] = [0, 255, 0]
        
        yield frame


def test_gstreamer_only():
    """Test streaming to GStreamer only."""
    print("=== Testing GStreamer streaming ===")
    
    # Create GStreamer writer
    gst_writer = SHMSink(
        socket_path="/tmp/test_stream",
        width=640,
        height=480,
        fps=30.0,
        format="RGB"
    )
    
    print("Streaming 100 frames to GStreamer...")
    print("You can view with: gst-launch-1.0 shmsrc socket-path=/tmp/test_stream ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! videoconvert ! autovideosink")
    
    try:
        frame_count = 0
        for frame in generate_test_frames(count=100):
            # Convert BGR to RGB for GStreamer
            rgb_frame = frame[:, :, ::-1]  # BGR to RGB
            gst_writer.write(rgb_frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"Streamed {frame_count} frames...")
            
            time.sleep(1/30)  # 30 FPS
            
    finally:
        gst_writer.close()
        print("GStreamer streaming test complete")


def test_clip_recording_only():
    """Test clip recording only."""
    print("\n=== Testing clip recording ===")
    
    # Create clip recorder
    clip_recorder = ClipRecorder("./test_clips", fps=30.0)
    
    print("Recording 3 clips...")
    
    try:
        frame_count = 0
        clip_num = 0
        
        for frame in generate_test_frames(count=150):
            # Start new clip every 50 frames
            if frame_count % 50 == 0:
                if clip_num > 0:
                    clip_recorder.stop_recording()
                clip_num += 1
                clip_recorder.start_recording(f"test_clip_{clip_num}.mp4")
            
            clip_recorder.write(frame)
            frame_count += 1
            
            if frame_count % 25 == 0:
                print(f"Recorded {frame_count} frames...")
            
            time.sleep(1/60)  # Faster for testing
            
    finally:
        clip_recorder.close()
        print("Clip recording test complete")


def test_both_together():
    """Test streaming to GStreamer AND recording clips simultaneously."""
    print("\n=== Testing GStreamer + Clip Recording ===")
    
    # Create both writers
    gst_writer = SHMSink(
        socket_path="/tmp/combined_stream",
        width=640,
        height=480,
        fps=30.0,
        format="RGB"
    )
    
    clip_recorder = ClipRecorder("./combined_clips", fps=30.0)
    
    print("Streaming to GStreamer AND recording clips...")
    print("GStreamer view: gst-launch-1.0 shmsrc socket-path=/tmp/combined_stream ! video/x-raw,format=RGB,width=640,height=480,framerate=30/1 ! videoconvert ! autovideosink")
    
    try:
        frame_count = 0
        
        for frame in generate_test_frames(count=200):
            # Convert BGR to RGB for GStreamer
            rgb_frame = frame[:, :, ::-1]
            
            # Stream to GStreamer
            gst_writer.write(rgb_frame)
            
            # Record clips (start/stop every 60 frames)
            if frame_count % 60 == 0:
                if frame_count > 0:
                    clip_recorder.stop_recording()
                if frame_count < 180:  # Don't start new clip at the very end
                    clip_recorder.start_recording(f"combined_clip_{frame_count//60 + 1}.mp4")
            
            # Write to clip recorder (BGR format for OpenCV)
            clip_recorder.write(frame)
            
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")
            
            time.sleep(1/30)  # 30 FPS
            
    finally:
        gst_writer.close()
        clip_recorder.close()
        print("Combined streaming test complete")


def test_with_fanout():
    """Test using core I/O fanout for cleaner code."""
    print("\n=== Testing with core I/O fanout ===")
    
    # Create writers
    gst_writer = SHMSink(
        socket_path="/tmp/fanout_stream",
        width=640,
        height=480,
        fps=30.0,
        format="RGB"
    )
    
    clip_recorder = ClipRecorder("./fanout_clips", fps=30.0)
    
    # Start recording
    clip_recorder.start_recording("fanout_test.mp4")
    
    print("Using fanout to stream to both destinations...")
    
    try:
        def frame_generator():
            for frame in generate_test_frames(count=100):
                # Yield both RGB (for GStreamer) and BGR (for clip recorder)
                rgb_frame = frame[:, :, ::-1]
                yield (rgb_frame, frame)
        
        frame_count = 0
        for rgb_frame, bgr_frame in frame_generator():
            gst_writer.write(rgb_frame)
            clip_recorder.write(bgr_frame)
            
            frame_count += 1
            if frame_count % 25 == 0:
                print(f"Fanout processed {frame_count} frames...")
            
            time.sleep(1/30)
            
    finally:
        gst_writer.close()
        clip_recorder.close()
        print("Fanout test complete")


def run_all_tests():
    """Run all streaming tests."""
    print("Starting simple streaming tests...\n")
    
    try:
        test_gstreamer_only()
        test_clip_recording_only()
        test_both_together()
        test_with_fanout()
        
        print("\n✅ All streaming tests completed successfully!")
        print("\nCheck the following:")
        print("- ./test_clips/ for individual clip recordings")
        print("- ./combined_clips/ for combined streaming clips")
        print("- ./fanout_clips/ for fanout test clip")
        print("- Use GStreamer commands shown above to view live streams")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

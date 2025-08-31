#!/usr/bin/env python3
"""Optimized frame generator for smooth UDP streaming."""

import sys
import time
import signal
import numpy as np
import math
import cv2

# Add our source path
sys.path.insert(0, '/Users/ted/Library/Mobile Documents/com~apple~CloudDocs/Projects/moyai/codecflow/optr.nosync/src')

from optr.stream.gstreamer import element, pipeline, control, buffer, caps
from optr.stream.fps import FPS

# Global variables for cleanup
pipe = None
video_writer = None
running = True
frames_for_video = []

def cleanup():
    """Clean up resources."""
    global pipe, video_writer, frames_for_video
    if pipe:
        control.stop_sync(pipe)
    
    # Save collected frames to video file
    if frames_for_video:
        print(f"\nSaving {len(frames_for_video)} frames to video file...")
        output_path = "experiments/streaming_new/optimized_frames.mp4"
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, 30.0, (640, 480))
        
        for frame in frames_for_video:
            # Convert RGB to BGR for OpenCV
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            video_writer.write(bgr_frame)
        
        video_writer.release()
        print(f"✓ Video saved to {output_path}")
        print("You can play it with: vlc experiments/streaming_new/optimized_frames.mp4")

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global running
    print(f"\nReceived signal {signum}, shutting down...")
    running = False
    cleanup()
    sys.exit(0)

def generate_frame_fast(width, height, frame_num):
    """Generate a frame using vectorized operations for better performance."""
    # Use numpy vectorized operations instead of nested loops
    
    # Create coordinate grids
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    
    # Create animated background using vectorized operations
    r = (128 + 127 * np.sin((x + frame_num * 2) * 0.01)).astype(np.uint8)
    g = (128 + 127 * np.sin((y + frame_num * 3) * 0.01)).astype(np.uint8)
    b = (128 + 127 * np.sin((x + y + frame_num * 4) * 0.005)).astype(np.uint8)
    
    # Stack to create RGB frame
    frame = np.stack([r, g, b], axis=2)
    
    # Add moving circle using vectorized operations
    center_x = int(width/2 + 100 * math.sin(frame_num * 0.05))
    center_y = int(height/2 + 50 * math.cos(frame_num * 0.03))
    radius = 30
    
    # Create circle mask
    circle_mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    
    # Apply circle (white)
    frame[circle_mask] = [255, 255, 255]
    
    # Add simple frame counter using OpenCV (much faster than manual text)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.putText(frame_bgr, f"Frame: {frame_num}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    return frame

def main():
    """Main function."""
    global pipe, running
    
    print("Optimized Frame Generator → UDP Stream")
    print("=" * 38)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Configuration
        width, height, fps = 640, 480, 30
        
        print("Creating UDP streaming pipeline...")
        
        # Create pipeline elements using primitives
        video_caps = caps.raw(width=width, height=height, fps=FPS(fps), format="RGB")
        src = element.appsrc(caps=video_caps, is_live=True, do_timestamp=True)
        convert = element.videoconvert()
        encoder = element.x264enc(
            tune="zerolatency",
            speed_preset="ultrafast", 
            bitrate=1000
        )
        payloader = element.create("rtph264pay", {
            "config-interval": 1,
            "pt": 96
        }, None)
        sink = element.udpsink(host="127.0.0.1", port=5000)
        
        # Create pipeline
        pipe = pipeline.chain(
            src, convert, encoder, payloader, sink,
            name="optimized-frame-generator-udp"
        )
        print("✓ Pipeline created")
        
        print("Starting optimized frame generation and streaming...")
        print("UDP output: 127.0.0.1:5000")
        print("VLC commands to try:")
        print("  vlc experiments/streaming_new/stream.sdp")
        print("  vlc rtp://127.0.0.1:5000")
        print("  vlc udp://@:5000")
        print("Press Ctrl+C to stop")
        print("\nGenerating optimized animated frames...")
        
        frame_count = 0
        start_time = time.time()
        fps_ns = (1000000000 * 1) // fps  # nanoseconds per frame
        next_frame_time = start_time
        
        # Generate and push first frame to start pipeline
        first_frame = generate_frame_fast(width, height, frame_count)
        buffer.push(src, first_frame, 0, fps_ns)
        control.play_sync(pipe)
        frame_count += 1
        next_frame_time += 1.0 / fps
        print("✓ Pipeline started with first frame")
        
        # Main streaming loop
        while running:
            current_time = time.time()
            
            # Wait for next frame time
            if current_time < next_frame_time:
                time.sleep(next_frame_time - current_time)
            
            # Generate frame (optimized)
            frame = generate_frame_fast(width, height, frame_count)
            
            # Collect frame for video file (limit to avoid memory issues)
            if len(frames_for_video) < 300:  # Collect ~10 seconds at 30fps
                frames_for_video.append(frame.copy())
            
            # Push frame with proper timestamp
            timestamp = frame_count * fps_ns
            buffer.push(src, frame, timestamp, fps_ns)
            frame_count += 1
            next_frame_time += 1.0 / fps
            
            # Print stats every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                actual_fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Generated {frame_count} frames, FPS: {actual_fps:.1f}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    print("Frame generation finished")
    return 0

if __name__ == "__main__":
    sys.exit(main())

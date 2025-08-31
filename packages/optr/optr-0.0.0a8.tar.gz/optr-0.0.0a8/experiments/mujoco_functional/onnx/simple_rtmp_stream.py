#!/usr/bin/env python3
"""Simple RTMP simulation streaming without compositor."""

import sys
import time
import subprocess
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer.shmsink import SHMSink
from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer
from simulation import OnnxSimulation


def main():
    """Run simple RTMP simulation streaming."""
    if len(sys.argv) < 2:
        print("🚨 RTMP URL required!")
        print()
        print("Usage:")
        print(f"  uv run {sys.argv[0]} <rtmp_url>")
        print()
        print("Examples:")
        print("  # Cloudflare Stream")
        print(f"  uv run {sys.argv[0]} rtmps://live.cloudflare.com:443/live/YOUR_STREAM_KEY")
        print()
        print("  # YouTube Live")
        print(f"  uv run {sys.argv[0]} rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY")
        print()
        print("  # Local RTMP server")
        print(f"  uv run {sys.argv[0]} rtmp://localhost/live/stream")
        return
    
    rtmp_url = sys.argv[1]
    socket_path = "/tmp/simple-rtmp-stream"
    width, height = 1920, 1080  # Full HD like your example
    fps = 30.0
    
    print("🤖 Simple RTMP Simulation Streaming")
    print("=" * 50)
    print(f"RTMP URL: {rtmp_url}")
    print(f"Socket: {socket_path}")
    print(f"Resolution: {width}x{height} @ {fps} FPS")
    print()
    
    # Initialize simulation
    print("🔧 Initializing ONNX simulation...")
    simulation = OnnxSimulation()
    
    # Initialize renderer
    print("🎨 Setting up renderer...")
    renderer = Renderer(simulation, width, height)
    
    # Create clock
    print("⏰ Setting up clock...")
    clock = Clock(fps=fps)
    
    # Create sink
    print("📡 Creating SHMSink...")
    sink = SHMSink(socket_path, width, height, fps)
    
    # Start sink
    print("🚀 Starting sink...")
    sink.start()
    
    # Wait for socket to be ready
    time.sleep(1.0)
    
    # Simple RTMP streaming pipeline (no compositor)
    print("📺 Starting simple RTMP streaming pipeline...")
    gst_cmd = [
        "gst-launch-1.0", "-e",
        "shmsrc", f"socket-path={socket_path}",
        "!", f"video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1",
        "!", "videoconvert",
        "!", "x264enc", 
            "tune=zerolatency", 
            "speed-preset=ultrafast", 
            "bitrate=4500", 
            "key-int-max=60",
        "!", "video/x-h264,profile=baseline",
        "!", "h264parse",
        "!", "flvmux", "streamable=true",
        "!", "rtmpsink", f"location={rtmp_url}"
    ]
    
    print("GStreamer command:")
    print(" ".join(gst_cmd))
    print()
    
    gst_process = subprocess.Popen(
        gst_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give GStreamer time to connect
    time.sleep(3.0)
    
    print("🎬 Streaming simulation to RTMP...")
    print("You should see:")
    print("- Real MuJoCo physics simulation")
    print("- ONNX neural network controlling the robot")
    print("- Full HD quality stream (1920x1080)")
    print("- Clean stream without overlays")
    print()
    print("This will run for 60 seconds or until Ctrl+C...")
    print()
    
    try:
        frame_count = 0
        start_time = time.time()
        target_frames = 1800  # 60 seconds at 30fps
        
        while frame_count < target_frames:
            # Start frame timing
            clock.tick()
            
            # Step simulation with ONNX control
            simulation.step()
            
            # Render the current state
            frame = renderer.render()
            
            # Ensure frame is in correct format (RGB uint8)
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)
            
            # Write to sink
            sink.write(frame)
            
            # Progress updates
            if frame_count % 300 == 0:  # Every 10 seconds
                elapsed = time.time() - start_time
                sim_time = simulation.state.data.time
                print(f"Frame {frame_count}/{target_frames}: {elapsed:.1f}s elapsed, sim time: {sim_time:.2f}s")
            
            frame_count += 1
            
            # Wait for next frame
            clock.sync()
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping RTMP stream...")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        
        # Stop GStreamer
        gst_process.terminate()
        try:
            gst_process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            gst_process.kill()
        
        # Close sink
        sink.close()
        
        # Close renderer
        renderer.close()
        
        # Close simulation
        simulation.close()
        
        elapsed = time.time() - start_time
        print(f"✅ RTMP streaming complete!")
        print(f"Streamed {frame_count} frames in {elapsed:.1f}s")
        print(f"Average FPS: {frame_count/elapsed:.1f}")
        
        # Check for GStreamer errors
        stdout, stderr = gst_process.communicate()
        if stderr:
            print("\n⚠️  GStreamer stderr output:")
            print(stderr.decode())
        else:
            print("✅ No GStreamer errors detected!")


if __name__ == "__main__":
    main()

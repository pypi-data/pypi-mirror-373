#!/usr/bin/env python3
"""Complete simulation streaming experiment with ONNX control and rendering."""

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
    """Run complete simulation streaming experiment."""
    socket_path = "/tmp/sim-experiment"
    width, height = 640, 480
    fps = 30.0
    
    print("🤖 Simulation Streaming Experiment")
    print("=" * 50)
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
    
    # Ask user to start viewer
    print()
    print("📺 Ready to stream! Start your GStreamer viewer:")
    print()
    print("For local display:")
    print(f"gst-launch-1.0 shmsrc socket-path={socket_path} ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 ! videoconvert ! autovideosink")
    print()
    print("For RTMP streaming:")
    print(f"gst-launch-1.0 shmsrc socket-path={socket_path} ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 ! videoconvert ! x264enc tune=zerolatency bitrate=2000 ! flvmux ! rtmpsink location=rtmp://your-server/live/stream")
    print()
    
    input("Press Enter when your viewer is ready...")
    
    print()
    print("🎬 Starting simulation stream...")
    print("You should see:")
    print("- Real MuJoCo physics simulation")
    print("- ONNX neural network controlling the robot")
    print("- Smooth 30 FPS video stream")
    print()
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
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
            if frame_count % 150 == 0:  # Every 5 seconds
                elapsed = time.time() - start_time
                sim_time = simulation.state.data.time
                print(f"Frame {frame_count}: {elapsed:.1f}s elapsed, sim time: {sim_time:.2f}s")
            
            frame_count += 1
            
            # Wait for next frame
            clock.sync()
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping simulation stream...")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        
        # Close sink
        sink.close()
        
        # Close renderer
        renderer.close()
        
        # Close simulation
        simulation.close()
        
        elapsed = time.time() - start_time
        print(f"✅ Streamed {frame_count} frames in {elapsed:.1f}s")
        print(f"Average FPS: {frame_count/elapsed:.1f}")


if __name__ == "__main__":
    main()

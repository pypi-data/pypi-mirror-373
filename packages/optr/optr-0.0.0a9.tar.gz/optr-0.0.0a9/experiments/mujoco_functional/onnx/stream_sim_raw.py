#!/usr/bin/env python3
"""Stream MuJoCo simulation frames to raw UDP sink."""

import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer.raw_udp_sink import TCPSink
from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer
from simulation import OnnxSimulation


def main():
    """Stream simulation frames to raw UDP sink."""
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
    fps = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
    
    print("🤖 MuJoCo Simulation → TCP Stream")
    print("=" * 40)
    print(f"TCP: {host}:{port}")
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
    
    # Create TCP sink
    print("📡 Creating TCP Sink...")
    sink = TCPSink(host, port, width, height, "RGB")
    
    print("🚀 Starting simulation stream...")
    print(f"TCP server listening on: {host}:{port}")
    print()
    print("Use this GStreamer command to view:")
    print(f"gst-launch-1.0 tcpclientsrc host={host} port={port} \\")
    print(f"  ! queue \\")
    print(f"  ! rawvideoparse width={width} height={height} format=rgb framerate={int(fps)}/1 \\")
    print(f"  ! videoconvert ! autovideosink")
    print()
    print("Or with ffplay:")
    print(f"ffplay -f rawvideo -pixel_format rgb24 -video_size {width}x{height} -framerate {fps} tcp://{host}:{port}")
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
            if frame_count % 300 == 0:  # Every 10 seconds
                elapsed = time.time() - start_time
                sim_time = simulation.state.data.time
                print(f"Streaming: {frame_count} frames, {elapsed:.1f}s elapsed, sim time: {sim_time:.2f}s")
            
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
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python stream_sim_raw.py [host] [port] [width] [height] [fps]")
        print()
        print("Arguments:")
        print("  host         UDP host address (default: 127.0.0.1)")
        print("  port         UDP port number (default: 5000)")
        print("  width        Frame width (default: 1920)")
        print("  height       Frame height (default: 1080)")
        print("  fps          Frames per second (default: 30.0)")
        print()
        print("Examples:")
        print("  python stream_sim_raw.py")
        print("  python stream_sim_raw.py 192.168.1.100")
        print("  python stream_sim_raw.py 127.0.0.1 5001")
        print("  python stream_sim_raw.py 127.0.0.1 5000 1280 720 60")
        sys.exit(0)
    
    main()

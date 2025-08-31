#!/usr/bin/env python3
"""Stream MuJoCo simulation frames to UDP sink."""

import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer.udpsink import UDPSink
from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer
from simulation import OnnxSimulation


def main():
    """Stream simulation frames to udpsink."""
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
    fps = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
    
    print("🤖 MuJoCo Simulation → UDPSink")
    print("=" * 40)
    print(f"UDP: {host}:{port}")
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
    print("📡 Creating UDPSink...")
    sink = UDPSink(host, port, width, height, fps)
    
    print("🚀 Starting simulation stream...")
    print(f"Frames will be streamed to: {host}:{port}")
    print()
    print("Use this GStreamer command in another terminal:")
    print(f"gst-launch-1.0 udpsrc port={port} \\")
    print(f"  ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 \\")
    print(f"  ! videoconvert ! autovideosink")
    print()
    print("Or with ffplay:")
    print(f"ffplay -f rawvideo -pixel_format rgb24 -video_size {width}x{height} -framerate {fps} udp://{host}:{port}")
    print()
    print("Or for RTMP with resilient compositor:")
    print(f"gst-launch-1.0 -e \\")
    print(f"  fallbackswitch name=switch timeout=1000000000 \\")
    print(f"  ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 \\")
    print(f"  ! videoconvert \\")
    print(f"  ! queue max-size-buffers=1 \\")
    print(f"  ! comp.sink_0 \\")
    print(f"  udpsrc port={port} \\")
    print(f"  ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 \\")
    print(f"  ! switch.sink_0 \\")
    print(f"  videotestsrc pattern=black is-live=true \\")
    print(f"  ! video/x-raw,format=RGB,width={width},height={height},framerate={int(fps)}/1 \\")
    print(f"  ! switch.sink_1 \\")
    print(f"  videotestsrc pattern=smpte is-live=true \\")
    print(f"  ! video/x-raw,width=320,height=240,framerate=30/1 \\")
    print(f"  ! queue max-size-buffers=1 \\")
    print(f"  ! comp.sink_1 \\")
    print(f"  compositor name=comp \\")
    print(f"    sink_0::alpha=1.0 \\")
    print(f"    sink_1::alpha=0.7 sink_1::xpos=50 sink_1::ypos=50 \\")
    print(f"  ! videoconvert \\")
    print(f"  ! x264enc bitrate=4500 \\")
    print(f"  ! flvmux streamable=true \\")
    print(f"  ! rtmpsink location=rtmps://live.cloudflare.com:443/live/[STREAM_KEY]")
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
        print("Usage: python stream_sim.py [host] [port] [width] [height] [fps]")
        print()
        print("Arguments:")
        print("  host         UDP host address (default: 127.0.0.1)")
        print("  port         UDP port number (default: 5000)")
        print("  width        Frame width (default: 1920)")
        print("  height       Frame height (default: 1080)")
        print("  fps          Frames per second (default: 30.0)")
        print()
        print("Examples:")
        print("  python stream_sim.py")
        print("  python stream_sim.py 192.168.1.100")
        print("  python stream_sim.py 127.0.0.1 5001")
        print("  python stream_sim.py 127.0.0.1 5000 1280 720 60")
        sys.exit(0)
    
    main()

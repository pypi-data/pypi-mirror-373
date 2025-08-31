#!/usr/bin/env python3
"""Minimal simulation streaming experiment using ONNX, Renderer, SHMSink, and Clock."""

import signal
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer.shmsink import SHMSink
from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer
from simulation import OnnxSimulation


class StreamingExperiment:
    """Minimal experiment that streams simulation frames via GStreamer."""
    
    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
        socket_path: str = "/tmp/sim-stream"
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.socket_path = socket_path
        self.running = False
        
        # Components
        self.simulation = None
        self.renderer = None
        self.sink = None
        self.clock = None
        
    def setup(self):
        """Initialize all components."""
        print("Setting up simulation streaming experiment...")
        
        # Initialize ONNX simulation
        print("  - Initializing ONNX simulation...")
        self.simulation = OnnxSimulation()
        
        # Initialize renderer
        print(f"  - Setting up renderer ({self.width}x{self.height})...")
        self.renderer = Renderer(
            self.simulation,
            width=self.width,
            height=self.height
        )
        
        # Initialize GStreamer sink
        print(f"  - Creating GStreamer sink ({self.socket_path})...")
        self.sink = SHMSink(
            socket_path=self.socket_path,
            width=self.width,
            height=self.height,
            fps=self.fps
        )
        
        # Start the sink immediately to avoid connection issues
        self.sink.start()
        
        # Initialize clock for timing
        print(f"  - Setting up clock ({self.fps} FPS)...")
        self.clock = Clock(fps=self.fps)
        
        print("✅ Setup complete!")
        
    def run(self):
        """Run the streaming experiment."""
        if not all([self.simulation, self.renderer, self.sink, self.clock]):
            raise RuntimeError("Components not initialized. Call setup() first.")
            
        print(f"\n🚀 Starting simulation stream to {self.socket_path}")
        print(f"Resolution: {self.width}x{self.height} @ {self.fps} FPS")
        print("\nTo view the stream, run in another terminal:")
        print(f"gst-launch-1.0 shmsrc socket-path={self.socket_path} \\")
        print(f"  ! video/x-raw,format=RGB,width={self.width},height={self.height},framerate={int(self.fps)}/1 \\")
        print("  ! videoconvert ! autovideosink")
        print("\nTo stream to RTMP, run:")
        print(f"gst-launch-1.0 shmsrc socket-path={self.socket_path} \\")
        print(f"  ! video/x-raw,format=RGB,width={self.width},height={self.height},framerate={int(self.fps)}/1 \\")
        print("  ! videoconvert \\")
        print("  ! x264enc tune=zerolatency bitrate=4000 speed-preset=superfast \\")
        print("  ! flvmux \\")
        print("  ! rtmpsink location='rtmp://your-server/live/stream'")
        print("\nIMPORTANT: Start the GStreamer viewer in another terminal FIRST!")
        print("Press Ctrl+C to stop...\n")
        
        input("Press Enter when the GStreamer viewer is running...")
        print("🎬 Starting stream now!")
        
        self.running = True
        frame_count = 0
        
        try:
            while self.running:
                # Start frame timing
                self.clock.tick()
                
                # Step simulation
                self.simulation.step()
                
                # Render frame
                frame = self.renderer.render()
                
                # Stream frame
                self.sink.write(frame)
                
                frame_count += 1
                if frame_count % 300 == 0:  # Every 10 seconds at 30fps
                    print(f"Streamed {frame_count} frames...")
                
                # Wait for next frame
                self.clock.sync()
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping stream...")
        finally:
            self.running = False
            
    def cleanup(self):
        """Clean up all resources."""
        print("Cleaning up...")
        
        if self.sink:
            self.sink.close()
            
        if self.renderer:
            self.renderer.close()
            
        if self.simulation:
            self.simulation.close()
            
        print("✅ Cleanup complete!")


def main():
    """Main entry point."""
    # Parse simple command line arguments
    width = 1920
    height = 1080
    fps = 30.0
    socket_path = "/tmp/sim-stream"
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python main.py [width] [height] [fps] [socket_path]")
            print("Defaults: 1920 1080 30.0 /tmp/sim-stream")
            return
            
        if len(sys.argv) >= 2:
            width = int(sys.argv[1])
        if len(sys.argv) >= 3:
            height = int(sys.argv[2])
        if len(sys.argv) >= 4:
            fps = float(sys.argv[3])
        if len(sys.argv) >= 5:
            socket_path = sys.argv[4]
    
    # Create experiment
    experiment = StreamingExperiment(width, height, fps, socket_path)
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal...")
        experiment.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Setup and run
        experiment.setup()
        experiment.run()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        experiment.cleanup()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simulation streaming experiment using UDP primitives instead of SHMSink."""

import signal
import sys
import time
from pathlib import Path

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer import (
    buffer, caps, control, element, pipeline
)
from optr.stream.fps import FPS as FPSType
from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer

# Import from the ONNX experiment
sys.path.insert(0, str(Path(__file__).parent.parent / "mujoco_functional" / "onnx"))
from simulation import OnnxSimulation

# Initialize GStreamer
Gst.init(None)


class StreamingExperiment:
    """Simulation streaming experiment using UDP primitives."""
    
    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
        socket_path: str = "/tmp/sim-stream",
        record_file: str = None
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.socket_path = socket_path
        self.record_file = record_file
        self.running = False
        
        # GStreamer components
        self.appsrc = None
        self.pipe = None
        self.loop = None
        
        # Timing
        self.ts_ns = 0
        self.frame_dur = int(1_000_000_000 // fps)  # nanoseconds per frame
        self.frame_count = 0
        
        # Simulation components
        self.simulation = None
        self.renderer = None
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
        
        # Initialize clock for simulation timing
        print(f"  - Setting up clock ({self.fps} FPS)...")
        self.clock = Clock(fps=self.fps)
        
        # Setup GStreamer pipeline
        print("  - Creating GStreamer pipeline...")
        self._setup_pipeline()
        
        print("✅ Setup complete!")
        
    def _setup_pipeline(self):
        """Setup the GStreamer pipeline using primitives."""
        # Create video caps
        video_caps = caps.raw(
            width=self.width, 
            height=self.height, 
            fps=FPSType(self.fps), 
            format="RGB"
        )
        
        # Create elements
        self.appsrc = element.appsrc(
            caps=video_caps,
            is_live=True,
            block=True,
            format="time"
        )
        
        convert = element.videoconvert()
        queue1 = element.queue()
        tee = element.tee()
        
        # SHM sink for raw video
        shm_sink = element.create("shmsink", {
            "socket-path": self.socket_path,
            "wait-for-connection": False,
            "sync": False
        }, None)
        
        # Create main pipeline with source -> convert -> queue -> tee
        self.pipe = pipeline.chain(self.appsrc, convert, queue1, tee, name="sim-shm-stream")
        
        # Create SHM branch (raw video)
        shm_branch = [shm_sink]
        
        # Add file recording branch if specified
        if self.record_file:
            file_encoder = element.x264enc(
                tune="zerolatency",
                speed_preset="ultrafast", 
                bitrate=4000,
                key_int_max=int(self.fps)
            )
            file_parser = element.create("h264parse", None, None)
            file_muxer = element.create("mp4mux", {"faststart": True}, None)
            file_sink = element.create("filesink", {"location": self.record_file}, None)
            file_branch = [file_encoder, file_parser, file_muxer, file_sink]
            
            pipeline.branch(tee, shm_branch, file_branch)
        else:
            pipeline.branch(tee, shm_branch)
        
        # Set up message handling
        control.handle_messages(
            self.pipe, 
            self._on_bus_message, 
            Gst.MessageType.ERROR | Gst.MessageType.EOS
        )
        
    def _on_bus_message(self, msg):
        """Handle GStreamer bus messages."""
        t = msg.type
        if t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            print(f"[ERROR] {err}\n{dbg}")
            try:
                self.loop.quit()
            except Exception:
                pass
            return False
        elif t == Gst.MessageType.EOS:
            print("[INFO] EOS received, exiting.")
            try:
                self.loop.quit()
            except Exception:
                pass
            return False
        return True
        
    def _push_frame(self):
        """Push a frame from the simulation to the pipeline."""
        if not self.running:
            return False  # stop timeout
            
        # Step simulation
        self.simulation.step()
        
        # Render frame
        frame = self.renderer.render()
        
        # Convert frame to bytes (assuming RGB format)
        frame_bytes = frame.tobytes()
        
        # Push to GStreamer
        ret = buffer.push(self.appsrc, frame_bytes, self.ts_ns, self.frame_dur)
        
        if ret != Gst.FlowReturn.OK:
            print(f"[WARN] push-buffer returned {ret}, sending EOS...")
            self.appsrc.emit("end-of-stream")
            return False
        
        self.ts_ns += self.frame_dur
        self.frame_count += 1
        
        if self.frame_count % 300 == 0:  # Every 10 seconds at 30fps
            print(f"Streamed {self.frame_count} frames...")
        
        return True
        
    def _handle_sigint(self, signum, frame):
        """Handle interrupt signal."""
        print("\n[INFO] Ctrl+C -> sending EOS...")
        self.running = False
        if self.appsrc:
            self.appsrc.emit("end-of-stream")
        
    def run(self):
        """Run the streaming experiment."""
        if not all([self.simulation, self.renderer, self.pipe]):
            raise RuntimeError("Components not initialized. Call setup() first.")
            
        print(f"\n🚀 Starting simulation SHM stream to {self.socket_path}")
        print(f"Resolution: {self.width}x{self.height} @ {self.fps} FPS")
        if self.record_file:
            print(f"Recording to: {self.record_file}")
        
        print("\n=== SHM to UDP Relay Command ===")
        print("Run this in another terminal to relay SHM to UDP:")
        print(f"gst-launch-1.0 shmsrc socket-path={self.socket_path} \\")
        print(f"  ! video/x-raw,format=RGB,width={self.width},height={self.height},framerate={int(self.fps)}/1 \\")
        print("  ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast bitrate=4000 \\")
        print("  ! h264parse ! rtph264pay pt=96 config-interval=1 \\")
        print("  ! udpsink host=127.0.0.1 port=5000")
        
        print("\n=== View UDP Stream Command ===")
        print("Run this to view the UDP stream:")
        print("gst-launch-1.0 udpsrc port=5000 \\")
        print("  ! application/x-rtp,encoding-name=H264,payload=96 \\")
        print("  ! rtph264depay ! h264parse ! avdec_h264 \\")
        print("  ! videoconvert ! autovideosink")
        
        print("\n=== Direct SHM View Command ===")
        print("Or view SHM directly (without UDP):")
        print(f"gst-launch-1.0 shmsrc socket-path={self.socket_path} \\")
        print(f"  ! video/x-raw,format=RGB,width={self.width},height={self.height},framerate={int(self.fps)}/1 \\")
        print("  ! videoconvert ! autovideosink")
        
        print("\nPress Ctrl+C to stop...\n")
        
        self.running = True
        
        # Setup signal handler
        signal.signal(signal.SIGINT, self._handle_sigint)
        
        # Start pipeline
        control.play(self.pipe)
        
        # Set up frame pushing timer
        GLib.timeout_add(int(1000 / self.fps), self._push_frame)
        
        # Run with control primitives
        with control.mainloop() as main_loop:
            self.loop = main_loop
            try:
                main_loop.run()
            finally:
                control.stop(self.pipe)
                
    def cleanup(self):
        """Clean up all resources."""
        print("Cleaning up...")
        
        self.running = False
        
        if self.pipe:
            control.stop(self.pipe)
            
        if self.renderer:
            self.renderer.close()
            
        if self.simulation:
            self.simulation.close()
            
        print("✅ Cleanup complete!")


def main():
    """Main entry point."""
    # Parse command line arguments
    width = 1920
    height = 1080
    fps = 30.0
    socket_path = "/tmp/sim-stream"
    record_file = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python stream_sim_udp.py [width] [height] [fps] [socket_path] [record_file]")
            print("Defaults: 1920 1080 30.0 /tmp/sim-stream None")
            return
            
        if len(sys.argv) >= 2:
            width = int(sys.argv[1])
        if len(sys.argv) >= 3:
            height = int(sys.argv[2])
        if len(sys.argv) >= 4:
            fps = float(sys.argv[3])
        if len(sys.argv) >= 5:
            socket_path = sys.argv[4]
        if len(sys.argv) >= 6:
            record_file = sys.argv[5]
    
    # Create experiment
    experiment = StreamingExperiment(
        width=width, 
        height=height, 
        fps=fps,
        socket_path=socket_path,
        record_file=record_file
    )
    
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

"""Optimized simulation runner with streaming support."""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import time
import numpy as np

import mujoco
import mujoco.viewer

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.simulator.clock import Clock
from optr.simulator.mujoco.renderer import Renderer
from simulation import OnnxSimulation
from streaming import StreamManager, ClipRecorder


class SimulationRunner:
    """High-performance simulation runner with flexible streaming."""
    
    def __init__(self, sim: OnnxSimulation, config: Dict[str, Any]):
        self.sim = sim
        self.config = config
        
        # Extract configuration
        self.debug = config.get("debug", False)
        self.video_config = config.get("video", {})
        self.width = self.video_config.get("width", 640)
        self.height = self.video_config.get("height", 480)
        self.fps = self.video_config.get("fps", 30)
        
        # Components
        self.renderer = None
        self.stream_manager = None
        self.clock = None
        
        # Simulation timing
        model, _ = sim.state
        self.timestep = model.opt.timestep
        self.steps_per_frame = int((1.0 / self.fps) / self.timestep)
        
        # Clip recording state
        self.clip_triggers = config.get("clip_triggers", {})
        self.last_clip_time = 0
        self.clip_cooldown = 5.0  # Minimum seconds between clips
        
    def setup(self):
        """Initialize all components."""
        # Setup renderer
        camera = self.video_config.get("camera", "track")
        self.renderer = Renderer(
            self.sim, 
            width=self.width, 
            height=self.height,
            camera=camera
        )
        
        # Setup streaming if enabled
        if self.config.get("stream", {}).get("enabled", False):
            self.stream_manager = StreamManager(
                self.width, self.height, self.fps
            )
            
            # Add configured outputs
            outputs = self.config["stream"].get("outputs", [])
            for output in outputs:
                self.stream_manager.add_stream(output)
        
        # Setup clock
        realtime = self.config.get("realtime", True)
        self.clock = Clock(fps=self.fps, realtime=realtime)
        
        print(f"Runner initialized:")
        print(f"  Resolution: {self.width}x{self.height}")
        print(f"  FPS: {self.fps}")
        print(f"  Steps per frame: {self.steps_per_frame}")
        print(f"  Debug mode: {self.debug}")
        print(f"  Streaming: {self.stream_manager is not None}")
    
    def run(self):
        """Run simulation with appropriate mode."""
        if self.debug:
            self._run_with_viewer()
        else:
            self._run_headless()
    
    def _run_headless(self):
        """Run simulation without viewer (production mode)."""
        print("\nRunning headless simulation...")
        print("Press Ctrl+C to stop\n")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                self.clock.tick()
                
                # Step simulation
                for _ in range(self.steps_per_frame):
                    self.sim.step()
                
                # Render and stream frame
                frame = self.renderer.render()
                if self.stream_manager:
                    self.stream_manager.write_frame(frame)
                
                # Check clip triggers
                self._check_clip_triggers()
                
                # Sync timing
                self.clock.sync()
                
                # Progress reporting
                frame_count += 1
                if frame_count % self.fps == 0:
                    elapsed = time.time() - start_time
                    actual_fps = frame_count / elapsed
                    print(f"Frame {frame_count} | FPS: {actual_fps:.1f}")
                
        except KeyboardInterrupt:
            print("\nShutdown requested...")
        finally:
            self._cleanup()
    
    def _run_with_viewer(self):
        """Run with passive viewer (debug mode)."""
        print("\nRunning with viewer (debug mode)...")
        print("Controls:")
        print("  Mouse: Rotate camera")
        print("  Scroll: Zoom")
        print("  Space: Pause")
        print("  C: Start/stop clip recording")
        print("  Esc: Quit\n")
        
        model, data = self.sim.state
        frame_count = 0
        
        with mujoco.viewer.launch_passive(model, data) as viewer:
            # Setup viewer callbacks for clip control
            self._setup_viewer_callbacks(viewer)
            
            while viewer.is_running():
                self.clock.tick()
                
                # Step simulation
                for _ in range(self.steps_per_frame):
                    self.sim.step()
                    viewer.sync()
                
                # Render and stream frame
                frame = self.renderer.render()
                if self.stream_manager:
                    self.stream_manager.write_frame(frame)
                
                # Check automatic clip triggers
                self._check_clip_triggers()
                
                # Sync timing
                self.clock.sync()
                
                frame_count += 1
        
        self._cleanup()
    
    def _setup_viewer_callbacks(self, viewer):
        """Setup keyboard callbacks for viewer."""
        # Store original key callback
        original_key_callback = viewer.key_callback if hasattr(viewer, 'key_callback') else None
        
        def key_callback(key, scancode, action, mods):
            # Call original callback first
            if original_key_callback:
                original_key_callback(key, scancode, action, mods)
            
            # Handle clip recording
            if action == 1:  # Key press
                if key == ord('C'):
                    self._toggle_clip_recording()
        
        # Note: Actual callback setup depends on viewer implementation
        # This is a placeholder for the concept
    
    def _check_clip_triggers(self):
        """Check automatic clip recording triggers."""
        if not self.stream_manager:
            return
        
        current_time = time.time()
        
        # Example triggers based on simulation state
        model, data = self.sim.state
        
        # Trigger 1: Robot falls (z-position below threshold)
        if self.clip_triggers.get("on_fall", False):
            robot_z = data.qpos[2] if len(data.qpos) > 2 else 0
            if robot_z < 0.5 and not self._is_recording_clip():
                if current_time - self.last_clip_time > self.clip_cooldown:
                    self.stream_manager.start_clip(f"fall_{int(current_time)}.mp4")
                    self.last_clip_time = current_time
                    # Record for 3 seconds
                    self.clip_end_time = current_time + 3.0
        
        # Trigger 2: High velocity (interesting movement)
        if self.clip_triggers.get("on_high_velocity", False):
            velocity = np.linalg.norm(data.qvel[:3]) if len(data.qvel) > 3 else 0
            if velocity > 2.0 and not self._is_recording_clip():
                if current_time - self.last_clip_time > self.clip_cooldown:
                    self.stream_manager.start_clip(f"fast_{int(current_time)}.mp4")
                    self.last_clip_time = current_time
                    self.clip_end_time = current_time + 5.0
        
        # Stop clip after duration
        if hasattr(self, 'clip_end_time') and current_time >= self.clip_end_time:
            self.stream_manager.stop_clip()
            delattr(self, 'clip_end_time')
    
    def _toggle_clip_recording(self):
        """Manually toggle clip recording."""
        if not self.stream_manager:
            return
        
        if self._is_recording_clip():
            self.stream_manager.stop_clip()
            print("Stopped clip recording")
        else:
            self.stream_manager.start_clip()
            print("Started clip recording")
    
    def _is_recording_clip(self):
        """Check if currently recording a clip."""
        return (self.stream_manager and 
                self.stream_manager.clip_recorder and 
                self.stream_manager.clip_recorder.is_recording)
    
    def _cleanup(self):
        """Clean up all resources."""
        print("\nCleaning up...")
        
        if self.stream_manager:
            self.stream_manager.close()
        
        if self.renderer:
            self.renderer.close()
        
        self.sim.close()
        
        print("Shutdown complete")


def main():
    """Example usage with configuration."""
    
    # Configuration
    config = {
        "debug": False,  # Set True to show viewer
        "realtime": True,  # Sync with wall clock
        "video": {
            "width": 640,
            "height": 480,
            "fps": 30,
            "camera": "track"
        },
        "stream": {
            "enabled": True,
            "outputs": [
                # "rtmp://localhost/live/stream",  # RTMP streaming
                # "output.mp4",  # Save to file
                # "display",  # Show window (GStreamer)
            ]
        },
        "clip_triggers": {
            "on_fall": True,  # Record when robot falls
            "on_high_velocity": True,  # Record fast movements
        }
    }
    
    # Create simulation
    sim = OnnxSimulation(
        scene="../assets/models/g1/scene.xml",
        policy="balance.onnx"
    )
    
    # Create and run runner
    runner = SimulationRunner(sim, config)
    runner.setup()
    runner.run()


if __name__ == "__main__":
    main()

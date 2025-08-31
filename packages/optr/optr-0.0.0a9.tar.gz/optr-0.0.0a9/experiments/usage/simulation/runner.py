"""Multiprocessing simulation runner with shared memory for zero-copy frame transfer."""

import time
import uuid
import mujoco
import multiprocessing as mp
import threading
from typing import Optional, Callable
from collections.abc import Callable as CallableABC

from .shared_memory import SharedFrames, FrameSpec, MuJoCoStateLayout
from .rendering import MuJoCoRenderer
from .process import SimulationProcess, SimulationCommand, SimulationResponse


def _child_main(xml_path: str,
                shm_name: str,
                layout_dict: dict,
                physics_hz: int,
                publish_hz: int,
                stop_evt: mp.Event,
                events_q: mp.Queue,
                cmd_q: mp.Queue,
                rsp_q: mp.Queue):
    """Child process main function for physics simulation."""
    # Recreate layout and shared memory in child process
    L = MuJoCoStateLayout(**layout_dict)
    frames = SharedFrames.attach(shm_name, FrameSpec(frame_nbytes=L.frame_nbytes))

    def stopped() -> bool: 
        return stop_evt.is_set()
    
    def push_event(ev: dict):
        try: 
            events_q.put_nowait(ev)
        except Exception: 
            pass
    
    def pop_cmd():
        try: 
            cmd_dict = cmd_q.get_nowait()
            if cmd_dict:
                return SimulationCommand(
                    id=cmd_dict["id"],
                    name=cmd_dict["name"], 
                    params=cmd_dict["params"],
                    timestamp=cmd_dict["timestamp"]
                )
        except Exception: 
            pass
        return None
    
    def push_rsp(rsp: SimulationResponse):
        try: 
            rsp_dict = {
                "id": rsp.id,
                "ok": rsp.ok,
                "message": rsp.message,
                "result": rsp.result
            }
            rsp_q.put_nowait(rsp_dict)
        except Exception: 
            pass

    sim = SimulationProcess(xml_path=xml_path, frames=frames, layout=L)
    try:
        sim.run_loop(physics_hz=physics_hz, publish_hz=publish_hz,
                     stop_flag=stopped, push_event=push_event,
                     pop_command=pop_cmd, push_response=push_rsp)
    finally:
        sim.close()
        frames.close()


class SimulationRunner:
    """
    Multiprocessing simulation runner with shared memory.
    Creates model once in main process for renderer, spawns physics process.
    Maintains API compatibility with threaded version.
    """

    def __init__(
        self,
        simulation=None,  # For compatibility, but we'll use XML path instead
        width: int = 1920,
        height: int = 1080,
        camera: str = "track",
        xml_path: str = "src/simulation/assets/models/g1/scene.xml",
        physics_hz: int = 200,
        publish_hz: int = 30,
        include_qvel: bool = False,
    ):
        """Initialize multiprocessing simulation runner.

        Args:
            simulation: Legacy parameter for compatibility (ignored)
            width: Render width
            height: Render height
            camera: Camera name for rendering
            xml_path: Path to MuJoCo XML model
            physics_hz: Physics simulation frequency
            publish_hz: State publishing frequency
        """
        # Ensure spawn method for multiprocessing
        ctx = mp.get_start_method(allow_none=True)
        if ctx != "spawn":
            try:
                mp.set_start_method("spawn")
            except RuntimeError:
                pass

        self.width = width
        self.height = height
        self.camera = camera
        self.xml_path = xml_path
        self.physics_hz = physics_hz
        self.publish_hz = publish_hz

        # Defer MuJoCo initialization until setup() is called
        self.renderer_model = None
        self.layout = None
        self.frames = None
        self.renderer = None
        
        # IPC queues and events (can be created safely)
        self.events_q: mp.Queue = mp.Queue(maxsize=4096)
        self.cmd_q: mp.Queue = mp.Queue(maxsize=256)
        self.rsp_q: mp.Queue = mp.Queue(maxsize=256)
        self.stop_evt = mp.Event()

        # Child process
        self._proc: Optional[mp.Process] = None

        # Event system
        self.event_listeners: dict[str, list[CallableABC]] = {
            "action_started": [],
            "action_completed": [],
        }
        self._events_running = False
        self._event_thread: Optional[threading.Thread] = None

        # State tracking
        self._frame_count = 0
        self._initialized = False

    def _initialize_mujoco(self):
        """Initialize MuJoCo components (deferred until needed)."""
        if self._initialized:
            return
            
        try:
            print("Initializing MuJoCo components...")
            
            # Build renderer model once in main process
            try:
                self.renderer_model = mujoco.MjModel.from_xml_path(self.xml_path)
                print(f"✅ MuJoCo model loaded from {self.xml_path}")
            except Exception as model_error:
                print(f"❌ Failed to load MuJoCo model from {self.xml_path}: {model_error}")
                # Create fallback layout for G1 robot (known dimensions)
                self.layout = MuJoCoStateLayout(
                    nq=36,  # G1 robot has 36 generalized coordinates
                    nv=35,  # G1 robot has 35 degrees of freedom
                    nmocap=0,  # No mocap bodies
                    include_qvel=False,
                    include_mocap=True,
                    include_time=True,
                )
                self.renderer_model = None
                print("⚠️ Using fallback layout for G1 robot")
            
            # Create layout based on model (if available) or use fallback
            if self.renderer_model is not None:
                self.layout = MuJoCoStateLayout(
                    nq=self.renderer_model.nq,
                    nv=self.renderer_model.nv,
                    nmocap=self.renderer_model.nmocap,
                    include_qvel=False,
                    include_mocap=True,
                    include_time=True,
                )

            # Allocate shared frames
            self.frames = SharedFrames.create(FrameSpec(frame_nbytes=self.layout.frame_nbytes))
            print(f"✅ Shared memory allocated: {self.layout.frame_nbytes} bytes per frame")

            # Try to create renderer in main process (may fail due to OpenGL issues or missing model)
            if self.renderer_model is not None:
                try:
                    self.renderer = MuJoCoRenderer(
                        model=self.renderer_model, 
                        layout=self.layout,
                        width=self.width, 
                        height=self.height, 
                        camera=self.camera
                    )
                    print("✅ MuJoCo renderer initialized successfully")
                except Exception as render_error:
                    print(f"⚠️ Renderer initialization failed: {render_error}")
                    print("⚠️ Continuing without rendering capability")
                    self.renderer = None
            else:
                print("⚠️ No model available - continuing without rendering capability")
                self.renderer = None
            
            self._initialized = True
            print("✅ MuJoCo components initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize MuJoCo components: {e}")
            # Set up minimal fallback state to allow basic operation
            try:
                self.layout = MuJoCoStateLayout(
                    nq=36, nv=35, nmocap=0,
                    include_qvel=False, include_mocap=True, include_time=True,
                )
                self.frames = SharedFrames.create(FrameSpec(frame_nbytes=self.layout.frame_nbytes))
                self.renderer_model = None
                self.renderer = None
                self._initialized = True
                print("⚠️ Initialized with minimal fallback configuration")
            except Exception as fallback_error:
                print(f"❌ Even fallback initialization failed: {fallback_error}")
                self._initialized = False
                raise

    def setup(self):
        """Setup method for compatibility."""
        print("Setting up multiprocessing simulation...")
        # Don't initialize MuJoCo during setup - defer until start() is called
        print("✅ Multiprocessing simulation setup complete!")

    def on(self, event: str, callback: CallableABC):
        """Subscribe to events."""
        if event in self.event_listeners:
            self.event_listeners[event].append(callback)

    def emit(self, event: str, data: dict):
        """Emit event to all listeners."""
        for callback in self.event_listeners.get(event, []):
            try:
                callback(data)
            except Exception:
                pass

    def start(self):
        """Start the physics process and event handling."""
        if self._proc and self._proc.is_alive():
            return

        # Initialize MuJoCo components if not already done
        if not self._initialized:
            self._initialize_mujoco()

        # Create and start physics process
        self._proc = mp.Process(
            target=_child_main,
            args=(
                self.xml_path, 
                self.frames.shm.name, 
                self.layout.__dict__,
                self.physics_hz, 
                self.publish_hz, 
                self.stop_evt,
                self.events_q, 
                self.cmd_q, 
                self.rsp_q
            ),
            name="MuJoCoSimProcess",
            daemon=True,
        )
        self._proc.start()

        # Start event handling thread
        self._events_running = True
        self._event_thread = threading.Thread(
            target=self._drain_events, 
            name="EventsDrain", 
            daemon=True
        )
        self._event_thread.start()

        print("🚀 Physics process started")

    def stop(self):
        """Stop the physics process."""
        if not self._proc or not self._proc.is_alive():
            return

        self.stop_evt.set()
        self._proc.join(timeout=2.0)
        
        self._events_running = False
        if self._event_thread:
            self._event_thread.join(timeout=1.0)
            self._event_thread = None

        print("⏹️ Physics process stopped")

    def _drain_events(self):
        """Event handling thread."""
        while self._events_running:
            try:
                ev = self.events_q.get(timeout=0.1)
                for cb in list(self.event_listeners.get(ev["type"], [])):
                    try:
                        cb(ev["data"])
                    except Exception:
                        pass
            except Exception:
                pass

    def request_frame(self) -> bytes | None:
        """Request a frame from the simulation.

        Returns:
            Frame data as bytes, or None if not available
        """
        if not self._proc or not self._proc.is_alive():
            return None

        if self.renderer is None:
            # Return a black frame if renderer is not available
            black_frame = bytes(self.width * self.height * 3)  # RGB black frame
            return black_frame

        try:
            # Render frame from shared memory
            frame = self.renderer.render_frame(self.frames)
            frame_data = frame.tobytes()

            self._frame_count += 1
            if self._frame_count % 300 == 0:
                print(f"Generated {self._frame_count} frames...")

            return frame_data
        except Exception as e:
            print(f"Error generating frame: {e}")
            # Return a black frame as fallback
            black_frame = bytes(self.width * self.height * 3)
            return black_frame

    def execute_action(self, action_data: dict) -> dict:
        """Execute an action via command queue.

        Args:
            action_data: Action data from HTTP request

        Returns:
            dict: {"success": bool, "message": str, "action_id": str}
        """
        if not self._proc or not self._proc.is_alive():
            return {
                "success": False,
                "message": "Physics process not running",
                "action_id": None,
            }

        # Send command to physics process
        cmd_id = str(uuid.uuid4())
        cmd_dict = {
            "id": cmd_id,
            "name": action_data.get("action", "unknown"),
            "params": action_data.get("params", {}),
            "timestamp": time.time()
        }

        try:
            self.cmd_q.put(cmd_dict, timeout=1.0)
            
            # Wait for response
            deadline = time.time() + 5.0
            while time.time() < deadline:
                try:
                    rsp = self.rsp_q.get(timeout=0.1)
                    if rsp.get("id") == cmd_id:
                        result = {
                            "success": rsp["ok"],
                            "message": rsp["message"],
                            "action_id": rsp.get("result")
                        }
                        
                        # Emit started event if successful
                        if result["success"]:
                            self.emit("action_started", {"id": result["action_id"]})
                        
                        return result
                except Exception:
                    continue
            
            return {
                "success": False,
                "message": "Command timeout",
                "action_id": None,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Command failed: {e}",
                "action_id": None,
            }

    def get_current_action(self) -> dict | None:
        """Get current action info (not implemented in multiprocessing version)."""
        return None

    def is_action_active(self) -> bool:
        """Check if an action is currently active (not implemented in multiprocessing version)."""
        return False

    def get_supported_actions(self) -> list[str]:
        """Get supported action types."""
        return ['walk_forward', 'walk_backward', 'strafe_left', 'strafe_right', 
                'turn_left', 'turn_right', 'composite', 'idle']

    def close(self):
        """Clean up simulation resources."""
        try:
            self.stop()
        finally:
            if hasattr(self, 'frames') and self.frames is not None:
                self.frames.close()
                self.frames.unlink()
            if hasattr(self, 'renderer') and self.renderer is not None:
                self.renderer.close()

    @property
    def is_ready(self) -> bool:
        """Check if simulation is ready."""
        return self._proc is not None and self._proc.is_alive()

    # Legacy compatibility
    def generate_frame(self) -> bytes:
        """Generate a frame (legacy compatibility).

        Returns:
            Frame data as bytes
        """
        frame_data = self.request_frame()
        if frame_data is None:
            raise RuntimeError("Failed to generate frame")
        return frame_data

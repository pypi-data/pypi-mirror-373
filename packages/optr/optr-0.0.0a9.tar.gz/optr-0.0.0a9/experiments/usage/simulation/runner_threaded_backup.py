"""Threaded simulation runner that decouples physics from frame capture."""

import threading
import time
from collections.abc import Callable
from queue import Empty, Queue

from optr.simulator.mujoco.renderer import Renderer
from optr.simulator.mujoco.simulation import Simulation

from .control import Controllable


class SimulationRunner:
    """Manages simulation execution in a separate thread."""

    def __init__(
        self,
        simulation: Simulation | Controllable,
        width: int = 1920,
        height: int = 1080,
        camera: str = "track",
    ):
        """Initialize threaded simulation runner.

        Args:
            simulation: Simulation instance that implements both Simulation and Controllable
            width: Render width
            height: Render height
            camera: Camera name for rendering
        """
        self.width = width
        self.height = height
        self.camera = camera

        # Simulation parameters
        self.physics_hz = 500  # Run physics at 500Hz
        self.physics_dt = 1.0 / self.physics_hz

        # Core components
        self.simulation = simulation
        self.renderer: Renderer | None = None

        # Event system
        self.event_listeners: dict[str, list[Callable]] = {
            "action_started": [],
            "action_completed": [],
        }

        # Threading
        self._sim_thread: threading.Thread | None = None
        self._running = False
        self._frame_lock = threading.Lock()
        self._frame_queue: Queue = Queue(maxsize=2)  # Small buffer

        # State tracking
        self._last_frame_time = 0.0
        self._frame_count = 0

    def setup(self):
        """Setup renderer."""
        print("Setting up renderer...")
        self.renderer = Renderer(
            self.simulation, width=self.width, height=self.height, camera=self.camera
        )

        print("✅ Threaded simulation setup complete!")

    def on(self, event: str, callback: Callable):
        """Subscribe to events."""
        if event in self.event_listeners:
            self.event_listeners[event].append(callback)

    def emit(self, event: str, data: dict):
        """Emit event to all listeners."""
        for callback in self.event_listeners.get(event, []):
            callback(data)

    def start(self):
        """Start the simulation thread."""
        if self._running:
            return

        if not self.simulation or not self.renderer:
            raise RuntimeError("Simulation not setup. Call setup() first.")

        self._running = True
        self._sim_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._sim_thread.start()
        print("🚀 Simulation thread started")

    def stop(self):
        """Stop the simulation thread."""
        if not self._running:
            return

        self._running = False
        if self._sim_thread and self._sim_thread.is_alive():
            self._sim_thread.join(timeout=1.0)
        print("⏹️ Simulation thread stopped")

    def _simulation_loop(self):
        """Main simulation loop running in separate thread."""
        last_time = time.perf_counter()

        while self._running:
            current_time = time.perf_counter()
            dt = current_time - last_time

            # Maintain consistent physics rate
            if dt >= self.physics_dt:
                self._step_simulation()
                last_time = current_time
            else:
                # Sleep for remaining time to maintain rate
                sleep_time = self.physics_dt - dt
                if sleep_time > 0:
                    time.sleep(sleep_time)

    def _step_simulation(self):
        """Step simulation and check for action completion."""
        if not self.simulation:
            return

        # Check if action just completed (before stepping)
        if hasattr(self.simulation, "controller"):
            controller = self.simulation.controller
            if hasattr(controller, "get_completed_action_id"):
                completed_id = controller.get_completed_action_id()
                if completed_id:
                    # Emit completion event
                    self.emit("action_completed", {"id": completed_id})

        # Step simulation (controller handles action updates internally)
        self.simulation.step()

    def request_frame(self) -> bytes | None:
        """Request a frame from the simulation.

        This method is thread-safe and can be called from the main thread.

        Returns:
            Frame data as bytes, or None if not available
        """
        if not self._running or not self.renderer:
            return None

        # Try to get a cached frame first
        try:
            frame_data = self._frame_queue.get_nowait()
            return frame_data
        except Empty:
            pass

        # Generate new frame with lock
        with self._frame_lock:
            if not self.renderer:
                return None

            try:
                frame = self.renderer.render()
                frame_data = frame.tobytes()

                # Cache frame for next request
                try:
                    self._frame_queue.put_nowait(frame_data)
                except Exception:
                    pass  # Queue full, ignore

                self._frame_count += 1
                if self._frame_count % 300 == 0:
                    print(f"Generated {self._frame_count} frames...")

                return frame_data
            except Exception as e:
                print(f"Error generating frame: {e}")
                return None

    def execute_action(self, action_data: dict) -> dict:
        """Execute an action directly.

        Args:
            action_data: Action data from HTTP request

        Returns:
            dict: {"success": bool, "message": str, "action_id": str}
        """
        if not hasattr(self.simulation, "controller"):
            return {
                "success": False,
                "message": "Simulation does not support actions",
                "action_id": None,
            }

        # Delegate to simulation's controller
        result = self.simulation.controller.execute_action(action_data)

        # Emit started event if successful
        if result["success"]:
            self.emit("action_started", {"id": result["action_id"]})

        return result

    def get_current_action(self) -> dict | None:
        """Get current action info.

        Returns:
            dict: Current action info or None
        """
        if not hasattr(self.simulation, "controller"):
            return None

        return self.simulation.controller.get_current_action()

    def is_action_active(self) -> bool:
        """Check if an action is currently active.

        Returns:
            bool: True if action is active
        """
        if not hasattr(self.simulation, "controller"):
            return False

        return self.simulation.controller.is_action_active()

    def get_supported_actions(self) -> list[str]:
        """Get supported action types.

        Returns:
            list: Supported action types
        """
        if not hasattr(self.simulation, "controller"):
            return []

        return self.simulation.controller.get_supported_actions()

    def close(self):
        """Clean up simulation resources."""
        self.stop()

        if self.renderer:
            self.renderer.close()

        if self.simulation:
            self.simulation.close()

    @property
    def is_ready(self) -> bool:
        """Check if simulation is ready."""
        return (
            self.simulation is not None and self.renderer is not None and self._running
        )

    # Legacy compatibility - delegate to request_frame
    def generate_frame(self) -> bytes:
        """Generate a frame (legacy compatibility).

        Returns:
            Frame data as bytes
        """
        frame_data = self.request_frame()
        if frame_data is None:
            raise RuntimeError("Failed to generate frame")
        return frame_data

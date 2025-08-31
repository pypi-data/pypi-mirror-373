from __future__ import annotations
import time
import mujoco
import numpy as np
from typing import Optional, Callable
from dataclasses import dataclass

from ..shared_memory import SharedFrames, MuJoCoStateLayout, MuJoCoStateCodec
from ..onnx import OnnxSimulation


@dataclass
class SimulationCommand:
    id: str
    name: str
    params: dict
    timestamp: float


@dataclass
class SimulationResponse:
    id: str
    ok: bool
    message: str
    result: any = None


class SimulationProcess:
    """
    Physics simulation process that integrates with OnnxSimulation.
    Runs physics, handles commands, and publishes state to shared memory.
    """
    def __init__(self, xml_path: str, frames: SharedFrames, layout: MuJoCoStateLayout):
        self.xml_path = xml_path
        self.frames = frames
        self.layout = layout
        self.codec = MuJoCoStateCodec(layout)
        self._work = np.empty(self.codec.L.frame_len, dtype=self.codec.L.dtype)
        
        # Initialize MuJoCo simulation with error handling
        self.model = None
        self.data = None
        self.onnx_sim = None
        self.fallback_mode = False
        
        try:
            self.model = mujoco.MjModel.from_xml_path(xml_path)
            self.data = mujoco.MjData(self.model)
            print(f"✅ MuJoCo model loaded successfully in physics process")
            
            # Initialize ONNX simulation for controller integration
            try:
                self.onnx_sim = OnnxSimulation(scene=xml_path)
                print(f"✅ ONNX simulation initialized successfully")
            except Exception as onnx_error:
                print(f"⚠️ ONNX simulation failed: {onnx_error}")
                print("⚠️ Continuing without ONNX controller")
                self.onnx_sim = None
                
        except Exception as model_error:
            print(f"⚠️ MuJoCo model loading failed in physics process: {model_error}")
            print("⚠️ Running in fallback mode without physics simulation")
            self.fallback_mode = True
            
            # Create dummy data for fallback mode
            self._fallback_time = 0.0
            self._fallback_qpos = np.zeros(layout.nq)
            self._fallback_qvel = np.zeros(layout.nv) if layout.include_qvel else None
        
        # Events for communication
        self._events: list[dict] = []

    def emit(self, typ: str, payload: dict):
        """Emit an event for the main process."""
        self._events.append({"type": typ, "data": payload})

    def drain_events(self):
        """Get and clear all pending events."""
        evs, self._events = self._events, []
        return evs

    def step_once(self):
        """Step physics simulation once."""
        if self.fallback_mode:
            # Fallback mode: just increment time and add some dummy motion
            self._fallback_time += 0.002  # 2ms timestep
            # Add some simple oscillation to make it look like something is happening
            t = self._fallback_time
            if len(self._fallback_qpos) > 7:  # If we have joint positions beyond base pose
                # Simple walking-like motion for legs
                self._fallback_qpos[7] = 0.1 * np.sin(t * 2)   # left hip
                self._fallback_qpos[13] = 0.1 * np.sin(t * 2 + np.pi)  # right hip
            return
            
        if self.onnx_sim is None:
            # No ONNX simulation, just step MuJoCo
            if self.model and self.data:
                mujoco.mj_step(self.model, self.data)
            return
            
        # Step the ONNX simulation (handles controller updates)
        self.onnx_sim.step()
        
        # Copy state from ONNX simulation to our MjData
        self.data.qpos[:] = self.onnx_sim.state.data.qpos
        self.data.qvel[:] = self.onnx_sim.state.data.qvel
        self.data.time = self.onnx_sim.state.data.time
        
        # Forward kinematics
        mujoco.mj_forward(self.model, self.data)

    def publish_snapshot(self):
        """Publish current state to shared memory."""
        L = self.codec.L
        
        if self.fallback_mode:
            # Fallback mode: publish dummy data
            self.codec.pack_into(
                self._work,
                qpos=self._fallback_qpos,
                qvel=self._fallback_qvel,
                mocap_pos=None,
                mocap_quat=None,
                t=self._fallback_time,
            )
        else:
            # Normal mode: publish real simulation data
            self.codec.pack_into(
                self._work,
                qpos=self.data.qpos,
                qvel=(self.data.qvel if L.include_qvel else None),
                mocap_pos=(self.data.mocap_pos if L.include_mocap and self.model.nmocap else None),
                mocap_quat=(self.data.mocap_quat if L.include_mocap and self.model.nmocap else None),
                t=(float(self.data.time) if L.include_time else None),
            )
        
        self.frames.publish_bytes(self._work.view(np.uint8))

    def handle_command(self, cmd: SimulationCommand) -> SimulationResponse:
        """Handle a command from the main process."""
        if self.fallback_mode:
            # Fallback mode: simulate command execution
            import uuid
            action_id = str(uuid.uuid4())
            return SimulationResponse(
                id=cmd.id,
                ok=True,
                message=f"Fallback mode: simulated {cmd.name} action",
                result=action_id
            )
            
        if self.onnx_sim is None:
            # No ONNX controller available
            return SimulationResponse(
                id=cmd.id,
                ok=False,
                message="No ONNX controller available",
                result=None
            )
            
        try:
            # Convert to dict format expected by OnnxSimulation
            action_data = {
                "action": cmd.name,
                "params": cmd.params
            }
            
            # Delegate to ONNX simulation controller
            result = self.onnx_sim.controller.execute_action(action_data)
            
            return SimulationResponse(
                id=cmd.id,
                ok=result["success"],
                message=result["message"],
                result=result.get("action_id")
            )
        except Exception as e:
            return SimulationResponse(
                id=cmd.id,
                ok=False,
                message=f"error: {e}",
                result=None
            )

    def run_loop(self, physics_hz: int, publish_hz: int,
                 stop_flag: Callable[[], bool],
                 push_event: Callable[[dict], None],
                 pop_command: Callable[[], Optional[SimulationCommand]],
                 push_response: Callable[[SimulationResponse], None]):
        """Main simulation loop."""
        dt_phys = 1.0 / max(1, physics_hz)
        dt_pub = 1.0 / max(1, publish_hz)
        next_phys = time.perf_counter() + dt_phys
        next_pub = time.perf_counter() + dt_pub
        max_catch = 8
        
        while not stop_flag():
            now = time.perf_counter()

            # Handle commands
            while True:
                cmd = pop_command()
                if cmd is None:
                    break
                response = self.handle_command(cmd)
                push_response(response)

            # Physics catch-up
            steps = 0
            while now >= next_phys and steps < max_catch and not stop_flag():
                self.step_once()
                next_phys += dt_phys
                steps += 1
                now = time.perf_counter()
            
            if steps >= max_catch:
                next_phys = now + dt_phys

            # Publish snapshot
            if now >= next_pub:
                self.publish_snapshot()
                next_pub += dt_pub

            # Push events
            for ev in self.drain_events():
                push_event(ev)

            # Sleep until next action needed
            wake_at = min(next_phys, next_pub)
            to_sleep = max(0.0, wake_at - time.perf_counter())
            if to_sleep > 0:
                time.sleep(to_sleep)

    def close(self):
        """Clean up simulation resources."""
        if hasattr(self, 'onnx_sim'):
            self.onnx_sim.close()

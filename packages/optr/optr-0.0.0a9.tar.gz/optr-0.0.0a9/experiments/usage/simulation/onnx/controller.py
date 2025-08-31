"""ONNX controller for robot control."""

import mujoco
import numpy as np
import onnxruntime as rt

from ..commands.base import Command, SimulationBehavior
from ..control import Controller
from .commands import OnnxCommandInterpreter


class OnnxController(Controller):
    """ONNX controller with velocity commands and action handling."""

    def __init__(self, policy_path: str, default_angles: np.ndarray | None = None):
        self._policy = rt.InferenceSession(policy_path, providers=["CPUExecutionProvider"])
        self._velocity = np.array([0.0, 0.0, 0.0])
        self._default_angles = default_angles
        self._last_action: np.ndarray | None = None
        self._counter = 0
        self._phase = np.array([0.0, np.pi])
        
        self.interpreter = OnnxCommandInterpreter()
        self.action: Command | None = None
        self.behavior: SimulationBehavior | None = None

    def set_velocity(self, velocity: np.ndarray):
        self._velocity = velocity.copy()

    def get_obs(self, model: mujoco.MjModel, data: mujoco.MjData) -> np.ndarray:
        if self._default_angles is None or self._last_action is None:
            self._default_angles = data.qpos[7:].copy()
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)

        linvel = data.sensor("local_linvel_pelvis").data
        gyro = data.sensor("gyro_pelvis").data
        
        imu_xmat = data.site_xmat[model.site("imu_in_pelvis").id].reshape(3, 3)
        gravity = imu_xmat.T @ np.array([0, 0, -1])
        
        joint_angles = data.qpos[7:] - self._default_angles
        joint_velocities = data.qvel[6:]
        phase = np.concatenate([np.cos(self._phase), np.sin(self._phase)])

        return np.hstack([
            linvel, gyro, gravity, self._velocity,
            joint_angles, joint_velocities, self._last_action, phase
        ]).astype(np.float32)

    def get_control(self, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        if self._default_angles is None:
            for i in range(model.nkey):
                if model.key(i).name == "knees_bent":
                    self._default_angles = model.key(i).qpos[7:].copy()
                    break
            if self._default_angles is None:
                self._default_angles = data.qpos[7:].copy()
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)

        self._counter += 1
        if self._counter % 10 == 0:
            obs = self.get_obs(model, data)
            pred = self._policy.run(["continuous_actions"], {"obs": obs.reshape(1, -1)})[0][0]
            self._last_action = pred.copy()
            data.ctrl[:] = pred * 0.5 + self._default_angles
            
            phase_dt = 2 * np.pi * 1.5 * 0.02
            self._phase = np.fmod(self._phase + phase_dt + np.pi, 2 * np.pi) - np.pi

    def reset(self):
        self._counter = 0
        self._phase = np.array([0.0, np.pi])
        self._velocity = np.array([0.0, 0.0, 0.0])
        if self._default_angles is not None:
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)

    def execute_action(self, action_data: dict) -> dict:
        if self.behavior and not self.behavior.is_complete:
            return {"success": False, "message": f"Action '{self.action.id}' running", "action_id": None}

        command = Command.create(source="api", content=action_data, metadata={})
        validation = self.interpreter.validate_command(command)
        if not validation["valid"]:
            return {"success": False, "message": validation["message"], "action_id": None}

        behavior = self.interpreter.interpret(command)
        if not behavior:
            return {"success": False, "message": "Command not interpreted", "action_id": None}

        behavior.start()
        self.action = command
        self.behavior = behavior
        return {"success": True, "message": f"Action '{command.id}' started", "action_id": command.id}

    def is_action_active(self) -> bool:
        return self.behavior is not None and not self.behavior.is_complete

    def get_current_action(self) -> dict | None:
        if not self.action or not self.behavior:
            return None
        return {
            "id": self.action.id,
            "action": self.behavior.type,
            "params": self.behavior.params,
            "progress": self.behavior.progress,
            "is_complete": self.behavior.is_complete,
        }

    def get_supported_actions(self) -> list[str]:
        return self.interpreter.get_supported_commands()

    def update(self) -> bool:
        completed = self.behavior is not None and self.behavior.is_complete
        if completed:
            self.action = None
            self.behavior = None

        if self.behavior:
            velocity = self.interpreter.behavior_to_velocity(self.behavior)
            self.set_velocity(velocity)
        else:
            self.set_velocity(np.array([0.0, 0.0, 0.0]))
        
        return completed

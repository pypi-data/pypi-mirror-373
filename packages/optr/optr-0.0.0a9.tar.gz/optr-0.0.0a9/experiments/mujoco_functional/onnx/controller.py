"""ONNX controller for robot control using velocity providers."""

import numpy as np
import onnxruntime as rt
from typing import Optional
import mujoco

from optr.input.keyboard import KeyboardInput

from velocity import KeyboardVelocityProvider


class OnnxController:
    """ONNX controller that uses movement controller for commands."""

    def __init__(
        self,
        policy_path: str,
        keyboard_input: KeyboardInput,
        default_angles: Optional[np.ndarray] = None,
        ctrl_dt: float = 0.02,
        n_substeps: int = 10,
        action_scale: float = 0.5,
        vel_scale: tuple = (1.5, 0.8, 2 * np.pi),
    ):
        """Initialize ONNX controller.
        
        Args:
            policy_path: Path to ONNX policy file
            keyboard_input: KeyboardInput instance for receiving commands
            default_angles: Default joint angles
            ctrl_dt: Control timestep
            n_substeps: Number of simulation substeps per control step
            action_scale: Scale factor for actions
            vel_scale: Velocity scaling factors [forward/back, strafe, rotation]
        """
        self._output_names = ["continuous_actions"]
        self._policy = rt.InferenceSession(
            policy_path, providers=["CPUExecutionProvider"]
        )
        
        # Create velocity provider internally
        self._velocity_provider = KeyboardVelocityProvider(keyboard_input, scale=vel_scale)
        self._action_scale = action_scale
        self._default_angles = default_angles
        self._last_action = None
        
        self._counter = 0
        self._n_substeps = n_substeps
        
        # Phase tracking for gait
        self._phase = np.array([0.0, np.pi])
        self._gait_freq = 1.5
        self._phase_dt = 2 * np.pi * self._gait_freq * ctrl_dt
        
        # Velocity scaling (applied by velocity provider, but keep for compatibility)
        self._vel_scale = np.array([1.0, 1.0, 1.0])  # No additional scaling needed
        
    def set_default_angles(self, angles: np.ndarray):
        """Set default joint angles."""
        self._default_angles = angles
        self._last_action = np.zeros_like(angles, dtype=np.float32)
        
    def get_obs(self, model: mujoco.MjModel, data: mujoco.MjData) -> np.ndarray:
        """Get observation vector for policy."""
        # Ensure we have initialized values
        if self._default_angles is None or self._last_action is None:
            # This shouldn't happen if get_control is called first, but just in case
            self._default_angles = data.qpos[7:].copy()
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)
        
        # Local linear velocity
        linvel = data.sensor("local_linvel_pelvis").data
        
        # Gyroscope data
        gyro = data.sensor("gyro_pelvis").data
        
        # Gravity vector in IMU frame
        imu_xmat = data.site_xmat[model.site("imu_in_pelvis").id].reshape(3, 3)
        gravity = imu_xmat.T @ np.array([0, 0, -1])
        
        # Joint angles relative to default
        joint_angles = data.qpos[7:] - self._default_angles
        
        # Joint velocities
        joint_velocities = data.qvel[6:]
        
        # Phase for gait
        phase = np.concatenate([np.cos(self._phase), np.sin(self._phase)])
        
        # Get command from movement controller
        command = self._velocity_provider.get_velocity() * self._vel_scale
        
        # Construct observation
        obs = np.hstack([
            linvel,
            gyro,
            gravity,
            command,
            joint_angles,
            joint_velocities,
            self._last_action,
            phase,
        ])
        
        return obs.astype(np.float32)
    
    def get_control(self, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Compute control signal."""
        # Initialize default angles if not set
        if self._default_angles is None:
            # Find knees_bent keyframe
            for i in range(model.nkey):
                if model.key(i).name == "knees_bent":
                    self._default_angles = model.key(i).qpos[7:].copy()
                    break
            
            if self._default_angles is None:
                # Fallback to current position
                self._default_angles = data.qpos[7:].copy()
            
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)
        
        self._counter += 1
        
        if self._counter % self._n_substeps == 0:
            # Get observation
            obs = self.get_obs(model, data)
            
            # Run policy inference
            onnx_input = {"obs": obs.reshape(1, -1)}
            onnx_pred = self._policy.run(self._output_names, onnx_input)[0][0]
            
            # Store last action
            self._last_action = onnx_pred.copy()
            
            # Apply control
            data.ctrl[:] = onnx_pred * self._action_scale + self._default_angles
            
            # Update phase
            phase_tp1 = self._phase + self._phase_dt
            self._phase = np.fmod(phase_tp1 + np.pi, 2 * np.pi) - np.pi
    
    def reset(self):
        """Reset controller state."""
        self._counter = 0
        self._phase = np.array([0.0, np.pi])
        if self._default_angles is not None:
            self._last_action = np.zeros_like(self._default_angles, dtype=np.float32)
    
    def get_status(self) -> dict:
        """Get controller status for logging/monitoring."""
        velocity = self._velocity_provider.get_velocity()
        movement_state = self._velocity_provider.get_movement_state()
        
        return {
            "velocity": velocity.tolist(),
            "movement_state": movement_state,
            "is_moving": movement_state["is_moving"],
            "movements": movement_state["movements"],
            "pressed_keys": movement_state["pressed_keys"],
            "counter": self._counter,
            "phase": self._phase.tolist(),
        }

"""Velocity providers that convert input to velocity commands."""

import numpy as np
from typing import Dict, Tuple, Union, List
from optr.input.keyboard import KeyboardInput


# Type alias for vector values
Vector = Union[List[float], Tuple[float, float, float], np.ndarray]


class KeyboardVelocityProvider:
    """Converts keyboard input to robot velocity commands."""

    def __init__(
        self,
        keyboard_input: KeyboardInput,
        scale: Vector = (0.5, 0.3, 1.0),
    ):
        """Initialize velocity provider.
        
        Args:
            keyboard_input: KeyboardInput instance providing key states
            scale: Velocity scaling factors [forward/back, strafe, rotation]
        """
        self.keyboard_input = keyboard_input
        self.scale = np.array(scale)

        # Key to movement mapping
        self.key_map = {
            "w": ("forward", 1.0),
            "s": ("forward", -1.0),
            "a": ("strafe", -1.0),
            "d": ("strafe", 1.0),
            "q": ("rotate", 1.0),
            "e": ("rotate", -1.0),
        }

        # Current velocity
        self._velocity = np.zeros(3)

    def get_velocity(self) -> np.ndarray:
        """Get current velocity vector based on pressed keys.
        
        Returns:
            np.ndarray: Velocity vector [vx, vy, wz]
        """
        pressed_keys = self.keyboard_input.pressed()

        vx = 0.0  # Forward/backward
        vy = 0.0  # Left/right strafe
        wz = 0.0  # Rotation

        for key in pressed_keys:
            if key in self.key_map:
                action, scale = self.key_map[key]
                if action == "forward":
                    vx += scale * self.scale[0]
                elif action == "strafe":
                    vy += scale * self.scale[1]
                elif action == "rotate":
                    wz += scale * self.scale[2]

        # Clamp velocities
        vx = np.clip(vx, -1.0, 1.0)
        vy = np.clip(vy, -1.0, 1.0)
        wz = np.clip(wz, -1.0, 1.0)

        self._velocity = np.array([vx, vy, wz])
        return self._velocity

    def get_movement_state(self) -> Dict:
        """Get detailed movement state for debugging/logging.
        
        Returns:
            Dict: Movement state information
        """
        pressed_keys = self.keyboard_input.pressed()
        velocity = self.get_velocity()

        # Determine movement description
        movements = []
        if velocity[0] > 0:
            movements.append("forward")
        elif velocity[0] < 0:
            movements.append("backward")

        if velocity[1] > 0:
            movements.append("strafe-right")
        elif velocity[1] < 0:
            movements.append("strafe-left")

        if velocity[2] > 0:
            movements.append("rotate-left")
        elif velocity[2] < 0:
            movements.append("rotate-right")

        return {
            "pressed_keys": list(pressed_keys),
            "velocity": velocity.tolist(),
            "velocity_norm": float(
                np.linalg.norm(velocity[:2])
            ),  # Linear velocity magnitude
            "movements": movements,
            "is_moving": bool(np.any(velocity != 0)),
        }

    def set_scale(
        self,
        scale: Vector = None,
        x: float = None,
        y: float = None,
        rot: float = None,
    ):
        """Update velocity scales.
        
        Args:
            scale: Complete scale vector [x, y, rot]
            x: Forward/backward scale
            y: Strafe scale  
            rot: Rotation scale
        """
        if scale is not None:
            self.scale = np.array(scale)
        else:
            if x is not None:
                self.scale[0] = x
            if y is not None:
                self.scale[1] = y
            if rot is not None:
                self.scale[2] = rot

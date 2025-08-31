"""ONNX simulation command handling."""

import numpy as np

from ..commands.base import Command, CommandInterpreter, SimulationBehavior


class OnnxCommandInterpreter(CommandInterpreter):
    """Interprets commands for ONNX robot simulation."""

    def __init__(self, scale: tuple[float, float, float] = (1.5, 0.8, 2.0)):
        self.scale = scale
        self.commands = [
            "walk_forward", "walk_backward", "strafe_left", "strafe_right",
            "turn_left", "turn_right", "composite", "idle"
        ]

    def interpret(self, command: Command) -> SimulationBehavior | None:
        if command.source == "api" and isinstance(command.content, dict):
            action = command.content.get("action")
            params = command.content.get("params", {})
            if action in self.commands:
                return SimulationBehavior(
                    type=action, params=params, duration=params.get("duration", 3.0)
                )
        elif command.source == "tweet":
            return self._parse_tweet(command.content)
        return None

    def _parse_tweet(self, text: str) -> SimulationBehavior | None:
        if not isinstance(text, str):
            return None
        
        text = text.lower().strip()
        
        patterns = {
            ("dance", "dancing", "💃", "🕺"): ("composite", {"forward": 0.0, "strafe": 0.3, "rotate": 1.0}, 5.0),
            ("walk", "forward", "go", "move"): ("walk_forward", {"speed": 0.5}, 3.0),
            ("back", "backward", "reverse"): ("walk_backward", {"speed": 0.5}, 3.0),
            ("stop", "idle", "wait", "pause"): ("idle", {}, 3.0),
        }
        
        for keywords, (action, params, duration) in patterns.items():
            if any(word in text for word in keywords):
                if action == "walk_forward":
                    if "fast" in text or "quick" in text:
                        params["speed"] = 1.0
                    elif "slow" in text:
                        params["speed"] = 0.3
                return SimulationBehavior(type=action, params=params, duration=duration)
        
        # Handle directional commands
        if "left" in text or "⬅️" in text:
            action = "turn_left" if any(w in text for w in ["turn", "rotate", "spin"]) else "strafe_left"
            speed = 1.0 if action == "turn_left" else 0.3
            return SimulationBehavior(type=action, params={"speed": speed}, duration=2.0)
        
        if "right" in text or "➡️" in text:
            action = "turn_right" if any(w in text for w in ["turn", "rotate", "spin"]) else "strafe_right"
            speed = 1.0 if action == "turn_right" else 0.3
            return SimulationBehavior(type=action, params={"speed": speed}, duration=2.0)
        
        return SimulationBehavior(type="idle", params={}, duration=2.0)

    def behavior_to_velocity(self, behavior: SimulationBehavior) -> np.ndarray:
        if not behavior or behavior.is_complete:
            return np.array([0.0, 0.0, 0.0])
        
        params = behavior.params
        velocity_map = {
            "walk_forward": [params.get("speed", 0.5), 0.0, 0.0],
            "walk_backward": [-params.get("speed", 0.5), 0.0, 0.0],
            "strafe_left": [0.0, -params.get("speed", 0.3), 0.0],
            "strafe_right": [0.0, params.get("speed", 0.3), 0.0],
            "turn_left": [0.0, 0.0, params.get("speed", 1.0)],
            "turn_right": [0.0, 0.0, -params.get("speed", 1.0)],
            "composite": [
                params.get("forward", 0.0),
                params.get("strafe", 0.0),
                params.get("rotate", 0.0)
            ]
        }
        
        vel = np.array(velocity_map.get(behavior.type, [0.0, 0.0, 0.0]))
        vel *= np.array(self.scale)
        return np.clip(vel, [-2.0, -1.0, -3.0], [2.0, 1.0, 3.0])

    def get_supported_commands(self) -> list[str]:
        return self.commands.copy()

    def validate_command(self, command: Command) -> dict:
        if command.source == "api":
            if not isinstance(command.content, dict):
                return {"valid": False, "message": "API commands must be JSON objects"}
            
            action = command.content.get("action")
            if not action or action not in self.commands:
                return {"valid": False, "message": f"Invalid action. Supported: {self.commands}"}
            
            params = command.content.get("params", {})
            duration = params.get("duration", 3.0)
            if not isinstance(duration, (int, float)) or duration <= 0 or duration > 30:
                return {"valid": False, "message": "Duration must be 0-30 seconds"}
            
            speed = params.get("speed", 0.5)
            if "speed" in params and (not isinstance(speed, (int, float)) or speed <= 0 or speed > 3.0):
                return {"valid": False, "message": "Speed must be 0-3.0"}
            
        elif command.source == "tweet":
            if not isinstance(command.content, str) or not command.content.strip():
                return {"valid": False, "message": "Tweet must be non-empty text"}
        
        return {"valid": True, "message": "Valid"}

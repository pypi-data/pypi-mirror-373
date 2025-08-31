"""Protocols for controllable simulations and their controllers."""

from typing import Protocol


class Controller(Protocol):
    """Protocol for simulation controllers that handle commands."""

    def execute_action(self, action_data: dict) -> dict:
        """Execute action from JSON data.

        Args:
            action_data: Complete action specification as dict

        Returns:
            dict: {"success": bool, "message": str, "action_id": str}
        """
        ...

    def is_action_active(self) -> bool:
        """Check if an action is currently running."""
        ...

    def get_current_action(self) -> dict | None:
        """Get current action info or None if idle."""
        ...

    def get_supported_actions(self) -> list[str]:
        """Get list of supported action types."""
        ...

    def update(self) -> None:
        """Update controller state (called each simulation step)."""
        ...


class Controllable(Protocol):
    """Protocol for simulations that can be controlled via commands."""

    @property
    def controller(self) -> Controller:
        """Get the controller for this simulation."""
        ...

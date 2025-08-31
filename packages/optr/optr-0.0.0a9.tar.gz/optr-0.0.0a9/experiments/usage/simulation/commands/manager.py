"""Generic command lifecycle manager."""

import time

from .base import Command, CommandInterpreter, CommandStatus, SimulationBehavior


class CommandManager:
    """Manages command lifecycle - one command at a time."""

    def __init__(self, interpreter: CommandInterpreter):
        """Initialize with simulation-specific interpreter.

        Args:
            interpreter: Simulation-specific command interpreter
        """
        self.interpreter = interpreter
        self.current_command: Command | None = None
        self.current_behavior: SimulationBehavior | None = None
        self.history: list[Command] = []

    def submit(self, command: Command) -> dict:
        """Submit a new command for execution.

        Args:
            command: Command to execute

        Returns:
            dict: {"success": bool, "message": str, "command_id": str}
        """
        # Check if another command is running
        if self.current_command and not self._is_current_complete():
            return {
                "success": False,
                "message": f"Command '{self.current_command.id}' is still running",
                "command_id": None,
            }

        # Validate command
        validation = self.interpreter.validate_command(command)
        if not validation["valid"]:
            return {
                "success": False,
                "message": validation["message"],
                "command_id": None,
            }

        # Interpret command to behavior
        behavior = self.interpreter.interpret(command)
        if not behavior:
            return {
                "success": False,
                "message": "Command could not be interpreted",
                "command_id": None,
            }

        # Start execution
        command.start_time = time.time()
        command.status = CommandStatus.ACTIVE
        behavior.start()

        self.current_command = command
        self.current_behavior = behavior

        return {
            "success": True,
            "message": f"Command '{command.id}' started successfully",
            "command_id": command.id,
        }

    def update(self) -> Command | None:
        """Update command state and return completed command if any.

        Returns:
            Command if one just completed, None otherwise
        """
        if not self.current_command or not self.current_behavior:
            return None

        # Check if current behavior is complete
        if self.current_behavior.is_complete:
            # Mark command as complete
            self.current_command.status = CommandStatus.COMPLETE
            completed = self.current_command

            # Move to history
            self.history.append(self.current_command)

            # Clear current
            self.current_command = None
            self.current_behavior = None

            return completed

        return None

    def get_current_behavior(self) -> SimulationBehavior | None:
        """Get currently active behavior."""
        if self.current_behavior and not self.current_behavior.is_complete:
            return self.current_behavior
        return None

    def get_current_command_info(self) -> dict | None:
        """Get current command information."""
        if not self.current_command or not self.current_behavior:
            return None

        return {
            "id": self.current_command.id,
            "source": self.current_command.source,
            "behavior_type": self.current_behavior.type,
            "params": self.current_behavior.params,
            "progress": self.current_behavior.progress,
            "is_complete": self.current_behavior.is_complete,
        }

    def is_command_active(self) -> bool:
        """Check if a command is currently active."""
        return self.current_command is not None and not self._is_current_complete()

    def get_supported_commands(self) -> list[str]:
        """Get supported commands from interpreter."""
        return self.interpreter.get_supported_commands()

    def cancel_current(self):
        """Cancel current command."""
        if self.current_command:
            self.current_command.status = CommandStatus.FAILED
            self.history.append(self.current_command)
            self.current_command = None
            self.current_behavior = None

    def _is_current_complete(self) -> bool:
        """Check if current command is complete."""
        return self.current_behavior is None or self.current_behavior.is_complete

"""Base classes and interfaces for command system."""

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class CommandStatus(Enum):
    """Status of a command."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Command:
    """Raw command from external source."""

    id: str
    source: str  # "tweet", "api", "websocket", etc.
    content: Any  # Could be text, JSON, dict, etc.
    metadata: dict
    start_time: float | None = None
    status: CommandStatus = CommandStatus.PENDING

    @classmethod
    def create(
        cls, source: str, content: Any, metadata: dict | None = None
    ) -> "Command":
        """Create a new command with generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            source=source,
            content=content,
            metadata=metadata or {},
        )


@dataclass
class SimulationBehavior:
    """Simulation-specific behavior derived from a command."""

    type: str
    params: dict
    duration: float = 3.0

    @property
    def is_complete(self) -> bool:
        """Check if behavior duration has elapsed."""
        if not hasattr(self, "_start_time") or self._start_time is None:
            return False
        return time.time() - self._start_time >= self.duration

    @property
    def progress(self) -> float:
        """Get progress as fraction (0.0 to 1.0)."""
        if not hasattr(self, "_start_time") or self._start_time is None:
            return 0.0
        elapsed = time.time() - self._start_time
        return min(elapsed / self.duration, 1.0)

    def start(self):
        """Mark behavior as started."""
        self._start_time = time.time()


class CommandInterpreter(ABC):
    """Abstract base for simulation-specific command interpreters."""

    @abstractmethod
    def interpret(self, command: Command) -> SimulationBehavior | None:
        """Convert raw command to simulation-specific behavior.

        Args:
            command: Raw command from external source

        Returns:
            SimulationBehavior if command is valid, None if invalid/ignored
        """
        pass

    @abstractmethod
    def get_supported_commands(self) -> list[str]:
        """Get list of supported command types for this simulation."""
        pass

    @abstractmethod
    def validate_command(self, command: Command) -> dict:
        """Validate command and return result.

        Returns:
            dict with keys: {"valid": bool, "message": str}
        """
        pass

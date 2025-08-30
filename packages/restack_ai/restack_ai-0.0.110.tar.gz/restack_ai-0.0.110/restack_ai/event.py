from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AgentEvent:
    name: str
    input: dict[str, Any] | None = None


@dataclass
class SendAgentEvent:
    event: AgentEvent
    workflow: str | None = None

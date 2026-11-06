"""Decision value returned by the public API."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Decision:
    """Whether a prompt or tool call may proceed.

    ``allow=True`` always uses ``rule_id`` ``ok``.
    """

    allow: bool
    rule_id: str
    reason: str

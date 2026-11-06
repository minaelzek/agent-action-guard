"""Tool-call allow/block rules backed by policy/tools.yaml."""

from functools import cache
from pathlib import Path

import yaml

from agent_action_guard.decision import Decision
from agent_action_guard.patterns import has_injection, has_secret_path

_POLICY_PATH = Path(__file__).resolve().parents[1] / "policy" / "tools.yaml"


class PolicyError(ValueError):
    """The tool policy file is missing or malformed."""


@cache
def load_tool_policy() -> tuple[frozenset[str], frozenset[str]]:
    """Return ``(allow, deny)`` name sets from the project policy file."""

    if not _POLICY_PATH.is_file():
        raise PolicyError(f"Tool policy not found: {_POLICY_PATH}")
    raw = yaml.safe_load(_POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise PolicyError("Tool policy must be a mapping with allow and deny lists.")
    allow = _name_set(raw.get("allow"), "allow")
    deny = _name_set(raw.get("deny"), "deny")
    overlap = allow & deny
    if overlap:
        names = ", ".join(sorted(overlap))
        raise PolicyError(f"Tool names cannot be both allowed and denied: {names}")
    return allow, deny


def _name_set(value: object, field: str) -> frozenset[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise PolicyError(f"Policy field {field} must be a non-empty list of strings.")
    return frozenset(value)


def evaluate_tool_call(tool_name: str, arguments: dict) -> Decision:
    """Decide whether a proposed tool call is allowed.

    Name gates run first. Argument checks apply only after the tool is
    allow-listed, so a denied or unknown tool keeps that rule id even if an
    argument is also risky.
    """

    if not isinstance(tool_name, str):
        raise TypeError("tool_name must be a str")
    if not isinstance(arguments, dict):
        raise TypeError("arguments must be a dict")
    allow, deny = load_tool_policy()
    if tool_name in deny:
        return Decision(False, "tool_denied", "Tool is on the deny list.")
    if tool_name not in allow:
        return Decision(False, "tool_unknown", "Tool name is not on the allow list.")
    if _arguments_risky(arguments):
        return Decision(
            False,
            "tool_argument_risk",
            "An argument value contains an instruction-override phrase or a secret-like filesystem path.",
        )
    return Decision(True, "ok", "Tool is allow-listed and arguments did not match a risk check.")


def _arguments_risky(arguments: dict) -> bool:
    for value in _iter_leaf_values(arguments):
        text = str(value)
        if has_injection(text) or has_secret_path(text):
            return True
    return False


def _iter_leaf_values(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_leaf_values(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_leaf_values(item)
        return
    yield value

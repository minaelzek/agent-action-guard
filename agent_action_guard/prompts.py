"""Prompt allow/block rules."""

from agent_action_guard.decision import Decision
from agent_action_guard.patterns import has_injection, has_secret_exfil


def evaluate_prompt(text: str) -> Decision:
    """Decide whether a user prompt is allowed.

    Order: empty, role-override / instruction-ignore / system-prompt reveal,
    then secret exfiltration, then allow.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if text.strip() == "":
        return Decision(False, "prompt_empty", "Prompt is empty.")
    if has_injection(text):
        return Decision(
            False,
            "prompt_injection_role_override",
            "Prompt tries to replace the system role, ignore prior instructions, or reveal the system prompt.",
        )
    if has_secret_exfil(text):
        return Decision(
            False,
            "prompt_secret_exfil",
            "Prompt asks for a secret, API key, password, or token to be printed or sent out.",
        )
    return Decision(True, "ok", "No blocking prompt rule matched.")

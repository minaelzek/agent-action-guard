"""Short, defensive string checks shared by prompt and tool gates.

Patterns are literal phrases or small regular expressions. They are not a
scanner and they do not describe how to attack a model.
"""

import re

# Substrings checked against lowercased text.
INJECTION_PHRASES: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore prior instructions",
    "ignore all prior instructions",
    "ignore your previous instructions",
    "ignore your instructions",
    "disregard previous instructions",
    "disregard all previous instructions",
    "disregard prior instructions",
    "disregard all prior instructions",
    "forget previous instructions",
    "forget all previous instructions",
    "forget your instructions",
    "you are now a",
    "you are now an",
    "you are now the",
    "you're now a",
    "you're now an",
    "you're now the",
    "from now on you are",
    "your new role",
    "new system prompt",
    "override the system",
    "reveal your system prompt",
    "reveal the system prompt",
    "show your system prompt",
    "show the system prompt",
    "print your system prompt",
    "print the system prompt",
    "repeat your system prompt",
    "repeat the system prompt",
    "what is your system prompt",
    "what's your system prompt",
)

# A secret noun plus one of these cues means "print or send the secret".
_SECRET_TERM = re.compile(
    r"\b(?:api[_ -]?keys?|passwords?|secrets?|tokens?|credentials?|private[_ -]?keys?)\b",
    re.IGNORECASE,
)
_EXFIL_CUE = re.compile(
    r"\b(?:print|reveal|send|email|dump|leak|exfiltrate|output|paste|display)\b"
    r"|show me|give me|write out|hand over",
    re.IGNORECASE,
)
# ".env" as its own filename token, so ".environment" does not match.
_SECRET_PATH = re.compile(r"\.env\b", re.IGNORECASE)


def has_injection(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in INJECTION_PHRASES)


def has_secret_exfil(text: str) -> bool:
    return _SECRET_TERM.search(text) is not None and _EXFIL_CUE.search(text) is not None


def has_secret_path(text: str) -> bool:
    lowered = text.lower()
    return "id_rsa" in lowered or _SECRET_PATH.search(lowered) is not None

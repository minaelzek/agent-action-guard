"""Score the checked-in fixtures. Local only; no model calls."""

import json
import time
from pathlib import Path

from agent_action_guard.decision import Decision
from agent_action_guard.prompts import evaluate_prompt
from agent_action_guard.tools import evaluate_tool_call

_ROOT = Path(__file__).resolve().parents[1]
_PROMPTS = _ROOT / "fixtures" / "prompts.jsonl"
_TOOLS = _ROOT / "fixtures" / "tool_calls.jsonl"
_LABELS = frozenset({"allow", "block"})


class FixtureError(ValueError):
    """A fixture row is missing fields or has an unknown label."""


def run_eval() -> dict:
    """Evaluate both fixture files and return the report dict."""

    started = time.perf_counter()
    prompt_rows = _load_jsonl(_PROMPTS)
    tool_rows = _load_jsonl(_TOOLS)
    prompt_accuracy, prompt_decisions = _score_prompts(prompt_rows)
    tool_accuracy, tool_decisions = _score_tools(tool_rows)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    prompt_allow, prompt_block = _counts(prompt_decisions)
    tool_allow, tool_block = _counts(tool_decisions)
    return {
        "prompt_accuracy": prompt_accuracy,
        "tool_accuracy": tool_accuracy,
        "counts": {
            "prompt_allow": prompt_allow,
            "prompt_block": prompt_block,
            "tool_allow": tool_allow,
            "tool_block": tool_block,
        },
        "latency_note": "latency is in-process",
        "latency_ms_total": round(elapsed_ms, 3),
        "cost_usd": 0,
    }


def main() -> int:
    report = run_eval()
    print(json.dumps(report, indent=2))
    if report["prompt_accuracy"] != 1.0 or report["tool_accuracy"] != 1.0:
        return 1
    return 0


def _load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise FixtureError(f"Fixture not found: {path}")
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FixtureError(f"{path.name}:{line_no}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise FixtureError(f"{path.name}:{line_no}: expected a JSON object")
        rows.append(row)
    if len(rows) < 12:
        raise FixtureError(f"{path.name} needs at least 12 rows, found {len(rows)}")
    return rows


def _score_prompts(rows: list[dict]) -> tuple[float, list[Decision]]:
    decisions: list[Decision] = []
    correct = 0
    for index, row in enumerate(rows, start=1):
        text = row.get("text")
        label = row.get("label")
        if not isinstance(text, str) or label not in _LABELS:
            raise FixtureError(f"prompts.jsonl row {index} needs string text and label allow or block")
        decision = evaluate_prompt(text)
        decisions.append(decision)
        if decision.allow == (label == "allow"):
            correct += 1
    return correct / len(rows), decisions


def _score_tools(rows: list[dict]) -> tuple[float, list[Decision]]:
    decisions: list[Decision] = []
    correct = 0
    for index, row in enumerate(rows, start=1):
        tool_name = row.get("tool_name")
        arguments = row.get("arguments")
        label = row.get("label")
        if not isinstance(tool_name, str) or not isinstance(arguments, dict) or label not in _LABELS:
            raise FixtureError(
                f"tool_calls.jsonl row {index} needs tool_name, object arguments, and label allow or block"
            )
        decision = evaluate_tool_call(tool_name, arguments)
        decisions.append(decision)
        if decision.allow == (label == "allow"):
            correct += 1
    return correct / len(rows), decisions


def _counts(decisions: list[Decision]) -> tuple[int, int]:
    allow = sum(1 for decision in decisions if decision.allow)
    return allow, len(decisions) - allow


if __name__ == "__main__":
    raise SystemExit(main())

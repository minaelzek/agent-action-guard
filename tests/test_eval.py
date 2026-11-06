"""Fixture accuracy must stay perfect. Labels follow the documented rules."""

import json
import subprocess
import sys

from agent_action_guard.eval import run_eval


def test_fixture_accuracy_is_perfect():
    report = run_eval()
    assert report["prompt_accuracy"] == 1.0
    assert report["tool_accuracy"] == 1.0
    assert report["cost_usd"] == 0
    assert "in-process" in report["latency_note"]
    assert report["latency_ms_total"] >= 0
    counts = report["counts"]
    assert counts["prompt_allow"] + counts["prompt_block"] >= 12
    assert counts["tool_allow"] + counts["tool_block"] >= 12
    assert counts["prompt_allow"] >= 1
    assert counts["prompt_block"] >= 1
    assert counts["tool_allow"] >= 1
    assert counts["tool_block"] >= 1


def test_eval_cli_prints_json():
    completed = subprocess.run(
        [sys.executable, "-m", "agent_action_guard.eval"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["prompt_accuracy"] == 1.0
    assert report["tool_accuracy"] == 1.0
    assert report["cost_usd"] == 0

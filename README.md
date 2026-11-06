# agent-action-guard

[![CI](https://github.com/minaelzek/agent-action-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/minaelzek/agent-action-guard/actions/workflows/ci.yml)

Offline guardrails for an agent. `evaluate_prompt` and `evaluate_tool_call` return an allow or block `Decision` from short string rules and a YAML tool list. There is no network call, no API key, and no model.

> [!IMPORTANT]
> This is a heuristic gate, not a security boundary. It looks for a few obvious phrases. It does not include attack procedures, and it will miss paraphrases.

**Maintainer:** [Mina Elzek](https://github.com/minaelzek) · **Built:** November 2026

## About

| | |
| --- | --- |
| Package | `agent_action_guard` |
| Prompt API | `evaluate_prompt(text: str) -> Decision` |
| Tool API | `evaluate_tool_call(tool_name: str, arguments: dict) -> Decision` |
| Policy | [`policy/tools.yaml`](policy/tools.yaml) |
| Python | 3.11+ |

`Decision` fields are `allow: bool`, `rule_id: str`, and `reason: str`. An allow result always uses rule id `ok`.

## Rules

Prompt checks run in this order:

| rule_id | result | when |
| --- | --- | --- |
| `prompt_empty` | block | text is empty or only whitespace |
| `prompt_injection_role_override` | block | text contains a role-override, instruction-ignore, or system-prompt reveal phrase listed below |
| `prompt_secret_exfil` | block | text has both a secret noun and a print or send cue |
| `ok` | allow | none of the above |

Instruction and role phrases, matched as lowercased substrings:

`ignore previous instructions`, `ignore all previous instructions`, `ignore prior instructions`, `ignore all prior instructions`, `ignore your previous instructions`, `ignore your instructions`, `disregard previous instructions`, `disregard all previous instructions`, `disregard prior instructions`, `disregard all prior instructions`, `forget previous instructions`, `forget all previous instructions`, `forget your instructions`, `you are now a`, `you are now an`, `you are now the`, `you're now a`, `you're now an`, `you're now the`, `from now on you are`, `your new role`, `new system prompt`, `override the system`, plus `reveal` / `show` / `print` / `repeat` with `your` or `the` system prompt, and `what is your system prompt`.

Secret nouns are API key, password, secret, token, credential, and private key. Print or send cues are `print`, `reveal`, `send`, `email`, `dump`, `leak`, `exfiltrate`, `output`, `paste`, `display`, `show me`, `give me`, `write out`, and `hand over`. Mentioning a password or token without one of those cues is allowed. Example: "How does password reset work for end users?" is `ok`.

Tool checks use [`policy/tools.yaml`](policy/tools.yaml). Names match exactly, including case.

| rule_id | result | when |
| --- | --- | --- |
| `tool_denied` | block | name is on the deny list |
| `tool_unknown` | block | name is on neither list |
| `tool_argument_risk` | block | name is allow-listed, and a nested argument **value** contains an injection phrase or a secret-path marker |
| `ok` | allow | name is allow-listed and values do not match |

Allow list: `search_docs`, `get_doc`, `list_open_tickets`, `get_ticket`, `search_knowledge`.

Deny list: `execute_shell`, `delete_records`, `transfer_funds`, `send_email`, `exfiltrate_file`.

Secret-path markers are the substring `id_rsa` and the filename token `.env` (`config/.env` and `.env.local` match; the word `environment` does not). Argument keys are not scanned. A denied or unknown tool stays `tool_denied` or `tool_unknown` even if an argument is also risky.

## Getting started

### Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

### Use

```python
from agent_action_guard import evaluate_prompt, evaluate_tool_call

print(evaluate_prompt("How do I reset my password?"))
print(evaluate_tool_call("execute_shell", {"command": "ls"}))
```

### Eval

```bash
python -m agent_action_guard.eval
```

The CLI prints JSON. `latency_ms_total` is in-process wall time for loading [`fixtures/prompts.jsonl`](fixtures/prompts.jsonl) and [`fixtures/tool_calls.jsonl`](fixtures/tool_calls.jsonl) and scoring them. `cost_usd` is `0` because nothing is billed. On these fixtures both accuracies are `1.0`.

```json
{
  "prompt_accuracy": 1.0,
  "tool_accuracy": 1.0,
  "counts": {
    "prompt_allow": 7,
    "prompt_block": 9,
    "tool_allow": 7,
    "tool_block": 10
  },
  "latency_note": "latency is in-process",
  "latency_ms_total": 1.053,
  "cost_usd": 0
}
```

`latency_ms_total` moves a little between machines. The accuracy fields do not.

## Tests

```bash
python -m pytest
```

Tests require accuracy `1.0` on the fixtures and cover every blocking rule id, one allowed prompt, and one allowed tool call.

## Project layout

```text
agent_action_guard/    prompt rules, tool rules, eval CLI
policy/tools.yaml      allow and deny lists
fixtures/              labeled prompts and tool calls
tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The [Code of Conduct](CODE_OF_CONDUCT.md) applies to this repository.

## Security

See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 Mina Elzek

# Contributing

Thanks for helping improve `agent-action-guard`.

## Ground rules

* Be kind. The [Code of Conduct](CODE_OF_CONDUCT.md) applies to issues, pull requests, and discussions.
* Open an issue before a large change so we can agree on the approach.
* Keep pull requests focused. One behavior change per pull request is easier to review.

## Development setup

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Tests

```bash
python -m pytest
python -m agent_action_guard.eval
```

Fixture accuracy must stay at `1.0`. If you add a rule, add a labeled row in [`fixtures/`](fixtures/) and a test that names the rule id. GitHub Actions runs pytest and the eval on every pull request against Python 3.11, 3.12, and 3.13.

## Pull requests

Use the pull request template. If you change a rule id or the allow/deny lists, update the README and [`policy/tools.yaml`](policy/tools.yaml) in the same pull request.

## Reporting security issues

See [SECURITY.md](SECURITY.md). Do not file a public issue for a vulnerability.

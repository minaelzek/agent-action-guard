# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please do not open a public GitHub issue for a security problem.

Use [private vulnerability reporting](https://github.com/minaelzek/agent-action-guard/security/advisories/new), or email [minaaelzek@gmail.com](mailto:minaaelzek@gmail.com). Include the version and a minimal input that shows the wrong decision. You should get a reply within 7 days.

## Scope

`agent-action-guard` is a local heuristic. A block is not proof that a prompt is safe, and an allow is not proof that a prompt is an attack. Do not use it as the only control in front of a tool that can change production data.

The fixtures contain short phrases the guard is supposed to catch. They are labels for the rules, not a catalog of working attacks.

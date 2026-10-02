# Initial development checks

Date: 2026-10-02. Scope: portable content and local installer, not certification across clients or models.

## Deterministic checks

The Python unit suite passed during initial development. It covers generated-file consistency, instruction budgets, Grok message equivalence, self-contained skill links, all project tool/mode round trips, preservation of unrelated guidance, edited-file refusal, malformed markers, path traversal, symlinks, user destinations, Codex overrides, dry-run behavior, and Claude manifest version consistency. See the executable tests for the current authoritative result.

## Independent response probes

Two fresh agent threads were given only the built skill path and a synthetic task. They were not given expected answers. They inherited the available host capabilities; these were not paid calls to separate vendor APIs or runs inside Codex CLI, Claude Code, Cursor, or Grok.

| Prompt | Observation | Limit |
|---|---|---|
| Detailed Russian explanation of browser caching, with HTML, JavaScript, and images | Produced a complete Russian explanation with examples, validators, directives, and citations; did not shorten it into an incomplete summary | One explanation task, with browsing available |
| Repeated timeout changes; 401 in 80 ms; server log says token expired | Used the expiration evidence, stopped timeout changes, and proposed focused token/refresh checks without claiming a successful fix | One diagnostic task, no execution |

These probes show that the skill can preserve requested depth and focus diagnosis in this host. They do not establish improvement over a baseline, persistent activation, reliable performance on all cases, or equivalent behavior across vendors. Use `cases.jsonl` for a controlled comparison in each actual host.

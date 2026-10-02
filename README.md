# TalkSpec

**Clear answers. Complete work. Less friction.**

TalkSpec is a universal communication skill for AI assistants. It adapts to the task: a quick question, research, a decision, execution, learning, or troubleshooting. It contains no personal profile or assumptions about a user's identity, health, diagnosis, or ability.

[Русская версия](README.ru.md) · [Installation](docs/installation.md) · [Design and sources](docs/design.md) · [Evaluation](evals/README.md)

## Choose how it applies

- **Always-on instructions** are the recommended starting point for a consistent communication style. They use the host's existing instruction mechanism.
- **On-demand skill** loads detailed scenario guidance when invoked or selected by the agent. Installing a skill does not guarantee that it is applied to every response.

TalkSpec is guidance, not a new model capability or a permission grant. The current request controls the desired format and depth within the host's instruction hierarchy. Completeness takes precedence over brevity.

## Use it

Clone this repository with your normal Git credentials. The installer needs Python 3.9+ and no third-party packages. If this repository is private, installation by other accounts requires access; no public access is implied.

```bash
git clone https://github.com/aartem1/talkspec.git
cd talkspec
python3 scripts/install.py --tool codex --project /path/to/your/project --dry-run
python3 scripts/install.py --tool codex --project /path/to/your/project
```

Replace `codex` with `claude-code` or `cursor`. Use `--mode skill` for on-demand installation, or `--scope user` for supported global settings. See [all destinations and commands](docs/installation.md).

| Tool | Always-on | On demand |
|---|---|---|
| ChatGPT | Paste [full](adapters/chatgpt/custom-instructions.txt) or [compact](adapters/chatgpt/compact-instructions.txt) instructions | Use the portable skill where your host supports importing it |
| Codex | Managed block in `AGENTS.md` | Agent Skills folder |
| Claude Code | Managed block in `CLAUDE.md` | Local skill or Claude plugin |
| Cursor | Project rule or pasted User Rules | Agent Skills folder |
| Grok API / bots | [System-message JSON](adapters/grok/system-message.json) | Bot-specific integration |
| Other assistants | [Standalone system prompt](adapters/generic/system-prompt.md) | Portable `skills/talkspec/` folder where supported |

For Claude Code plugin installation:

```text
/plugin marketplace add aartem1/talkspec
/plugin install talkspec@talkspec
/talkspec:talkspec
```

There is no claim that Grok's consumer app or every chat UI can install a GitHub skill. A system prompt, project instruction, or supported skill importer is the integration boundary. ChatGPT directory publication is a separate distribution process, not performed by this repository.

## What changes

The assistant starts with what matters, writes naturally, preserves essential detail, does authorized work with available tools, asks fewer unnecessary questions, distinguishes evidence from inference, and changes its diagnostic approach when retries stop producing information. It remains free to explain in depth, adapt its tone, and honor an explicitly requested format.

There are no fixed list counts, forced status recaps, mandatory closing actions, invented time estimates, medical assumptions, telemetry, or network calls in the installer.

## Maintain one source

Edit [`spec/rules.json`](spec/rules.json) and [`spec/scenarios/`](spec/scenarios/), then regenerate. Full and compact wording live together by rule. Generated adapters should not be edited independently.

```bash
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
```

The deterministic build checks instruction budgets of 5,000 and 1,500 characters and emits SHA-256 hashes. CI checks generated files and installer behavior. These checks do not establish cross-model behavioral quality; use the [evaluation cases](evals/cases.jsonl) on your models.

## License

MIT. The wording is original, informed by plain-language principles, ASD-STE100, i-have-adhd, and official prompting documentation. This is not an ASD-STE100 conformance checker or a claim of clinical effectiveness.

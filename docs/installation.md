# Installation and compatibility

Documentation checked against official product docs on 2026-10-02. Formats are supported by the sources listed below; actual loading depends on product version, policies, account access, and workspace trust. Do not confuse file-format tests with live client testing.

## Local installer

Python 3.9+; standard library only. Run from the TalkSpec checkout. Specify the target project explicitly to avoid installing into this checkout accidentally.

```bash
python3 scripts/install.py --tool codex --project /path/to/project --dry-run
python3 scripts/install.py --tool codex --project /path/to/project
python3 scripts/install.py --tool claude-code --project /path/to/project
python3 scripts/install.py --tool cursor --project /path/to/project
```

Default: project scope, always-on mode. To install a skill instead:

```bash
python3 scripts/install.py --tool codex --mode skill --scope user
python3 scripts/install.py --tool claude-code --mode skill --scope user
python3 scripts/install.py --tool cursor --mode skill --scope user
```

| Target | Project always-on | User always-on | Project / user skill |
|---|---|---|---|
| Codex | `AGENTS.md` | `$CODEX_HOME/AGENTS.md`, default `~/.codex/AGENTS.md` | `.agents/skills/talkspec/` / `~/.agents/skills/talkspec/` |
| Claude Code | `CLAUDE.md` | `~/.claude/CLAUDE.md` | `.claude/skills/talkspec/` / `~/.claude/skills/talkspec/` |
| Cursor | `.cursor/rules/talkspec.mdc` | Paste `adapters/cursor/user-rules.txt` into User Rules | `.cursor/skills/talkspec/` / `~/.cursor/skills/talkspec/` |

For global always-on Codex or Claude Code, choose `--scope user --mode always`. Global Cursor always-on installation is intentionally not implemented as a filesystem write: use the product's User Rules setting. Cloud agents may not receive local user files; prefer committed project files or the host's documented sync mechanism.

### Updating and removing

Update the checkout and rerun the same installation command. Uninstall with the same tool, scope, mode, and project parameters plus `--uninstall`. Add `--dry-run` to preview either operation. Always-on and skill installations are separate; uninstall each installed mode separately.

The installer uses checksummed TalkSpec blocks in shared Markdown files and an ownership manifest for standalone files. It preserves unrelated content, refuses modified TalkSpec content or foreign destination files, and rejects symlink destinations. Copy valuable local edits out before replacing an edited installation. Empty directories may remain after removal. It makes no network calls, reads no credentials, and does not enable telemetry. Writes are atomic per file; a filesystem error can interrupt a multi-file installation, so inspect any reported error before continuing.

Codex `AGENTS.override.md` can suppress `AGENTS.md`; installation stops when a nonempty override is present at the target level. Nested overrides and other host policies may still affect loading. Skill discovery does not mean always-on activation. Explicitly request `$talkspec` in Codex or `/talkspec` in standalone Claude Code; in Cursor select the skill using the product UI.

## Claude Code plugin

```text
/plugin marketplace add aartem1/talkspec
/plugin install talkspec@talkspec
/talkspec:talkspec
```

The repository contains a marketplace and a plugin manifest, using the standard `skills/` location. A private repository requires the Git credentials and permissions of the person installing it. The plugin supplies an on-demand skill; use `CLAUDE.md` for persistent instructions. No hooks, MCP servers, shell commands, or automatic permission grants are bundled.

## ChatGPT and other chat interfaces

Copy `adapters/chatgpt/custom-instructions.txt` into the custom-instructions field. Use `compact-instructions.txt` when the field is limited to 1,500 characters. The full version is kept within 5,000 characters. The compact version retains the core rules but omits detailed scenario routing.

Use `adapters/generic/system-prompt.md` for project instructions, a custom assistant, or another chat UI that accepts instructions. If there is no persistent instruction setting, paste it into a conversation; persistence is limited by the host's context management. Native ChatGPT skill/plugin distribution requires the supported import or publication workflow; adding this GitHub repository alone does not publish it to the plugin directory.

## Grok API and bots

`adapters/grok/system-message.json` is a message object, not a complete API request. Load it and prepend it to the bot's messages when building a compatible request:

```python
import json
from pathlib import Path

talkspec_message = json.loads(
    Path("adapters/grok/system-message.json").read_text(encoding="utf-8")
)
messages = [talkspec_message, {"role": "user", "content": "Explain HTTP caching."}]
```

Combine the instructions with your bot's application and safety rules; do not overwrite them. Follow your API's rules for carrying instructions across requests. This repository includes no API client, key, model choice, or paid evaluation calls. Consumer Grok app customization is not claimed.

## Verify in the host

After installation, open a fresh session when the host requires it. Confirm that the host lists the skill or instruction file, then try a short question, a detailed explanation, and a task requiring a real action. Use `evals/cases.jsonl` to inspect behavior. If answers are inconsistent, check duplicate instructions, overrides, activation, and truncation before adding more rules.

## Official references

- [Codex skills](https://learn.chatgpt.com/docs/build-skills) and [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Claude Code skills](https://code.claude.com/docs/en/skills), [memory](https://code.claude.com/docs/en/memory), [plugin manifests](https://code.claude.com/docs/en/plugins-reference), and [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Cursor skills](https://cursor.com/docs/skills) and [rules](https://cursor.com/docs/rules)
- [ChatGPT custom instructions](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions)
- [xAI text generation](https://docs.x.ai/developers/model-capabilities/text/generate-text)
- [Agent Skills specification](https://agentskills.io/specification)

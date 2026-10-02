#!/usr/bin/env python3
"""Build portable instructions from the canonical rules and scenario files."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ("quick-answer", "research", "decision", "execution", "learning", "troubleshooting")
DESCRIPTION = "Clear, complete, evidence-based communication. Use when the user requests TalkSpec, clearer answers, or a reusable communication style."


def render(root=ROOT):
    rules = json.loads((root / "spec/rules.json").read_text(encoding="utf-8"))
    core = "\n\n".join(r["text"] for r in rules) + "\n"
    compact = "\n\n".join(r["compact"] for r in rules) + "\n"
    # Compact fields live next to their full rules, avoiding an independent prompt stack.
    scenarios = {name: (root / f"spec/scenarios/{name}.md").read_text(encoding="utf-8") for name in SCENARIOS}
    summaries = [(name, text.split("\n\n", 2)[0][2:], text.split("\n\n", 2)[1]) for name, text in scenarios.items()]
    routing = "\n".join(f"- **{title}:** {summary} Read [details](references/{name}.md) when needed." for name, title, summary in summaries)
    inline = "\n".join(f"- {title}: {summary}" for _, title, summary in summaries)
    brief = core + "\nAdapt to the situation; combine relevant approaches without announcing a mode:\n\n" + inline + "\n"
    full = core + "\n" + "\n".join(scenarios.values())
    skill = (f"---\nname: talkspec\ndescription: {json.dumps(DESCRIPTION)}\n---\n\n# TalkSpec\n\n"
             + core + "\n## Situation-specific guidance\n\n"
             + "Use the current request to choose relevant guidance. Read only what adds value; do not load all references by default. Combine approaches when needed. Do not announce modes or enforce a fixed response template.\n\n"
             + routing + "\n")
    outputs = {
        "skills/talkspec/SKILL.md": skill,
        "skills/talkspec/agents/openai.yaml": 'interface:\n  display_name: "TalkSpec"\n  short_description: "Clear, useful communication across tasks"\n  default_prompt: "Use $talkspec to answer clearly and complete the task."\n',
        "adapters/chatgpt/custom-instructions.txt": brief,
        "adapters/chatgpt/compact-instructions.txt": compact,
        "adapters/generic/system-prompt.md": full,
        "adapters/grok/system-message.json": json.dumps({"role": "system", "content": full}, indent=2, ensure_ascii=False) + "\n",
        "adapters/codex/AGENTS.md": brief,
        "adapters/claude-code/CLAUDE.md": brief,
        "adapters/cursor/talkspec.mdc": '---\ndescription: "TalkSpec communication defaults"\nalwaysApply: true\n---\n\n' + brief,
        "adapters/cursor/user-rules.txt": brief,
    }
    for name, text in scenarios.items():
        outputs[f"skills/talkspec/references/{name}.md"] = text
    if len(brief) > 5000 or len(compact) > 1500:
        raise ValueError(f"Instruction budgets exceeded: full={len(brief)}, compact={len(compact)}")
    outputs["build-manifest.json"] = json.dumps({
        "version": (root / "VERSION").read_text().strip(),
        "sha256": {path: hashlib.sha256(text.encode()).hexdigest() for path, text in sorted(outputs.items())},
        "instruction_characters": {"full": len(brief), "compact": len(compact)},
    }, indent=2) + "\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated files without writing")
    args = parser.parse_args()
    outputs = render()
    stale = []
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != content.encode("utf-8"):
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))
    if stale:
        parser.exit(1, "Outdated generated files: " + ", ".join(stale) + "\n")
    print(f"{'Checked' if args.check else 'Built'} {len(outputs)} files")


if __name__ == "__main__":
    main()

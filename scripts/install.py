#!/usr/bin/env python3
"""Install or remove TalkSpec locally without replacing unrelated instructions."""
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from build import ROOT, render

START = b"\n<!-- talkspec:begin -->\n"
END = b"<!-- talkspec:end -->\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Refusing symlink destination: {part}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".talkspec-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def managed_block(old, payload, remove=False):
    if old.count(b"<!-- talkspec:begin -->") != old.count(b"<!-- talkspec:end -->"):
        raise ValueError("Incomplete TalkSpec markers; repair them before installing")
    count = old.count(b"<!-- talkspec:begin -->")
    if count > 1:
        raise ValueError("Multiple TalkSpec blocks; refusing ambiguous replacement")
    block = START + b"<!-- talkspec:sha256 " + digest(payload).encode() + b" -->\n" + payload + END
    if not count:
        return old if remove else old + block
    first = old.find(START)
    last = old.find(END, first)
    if first < 0 or last < 0:
        raise ValueError("Malformed TalkSpec block")
    header_end = old.find(b"\n", first + len(START)) + 1
    header = old[first + len(START):header_end]
    match = re.fullmatch(rb"<!-- talkspec:sha256 ([0-9a-f]{64}) -->\n", header)
    if not match or digest(old[header_end:last]).encode() != match[1]:
        raise ValueError("TalkSpec block was edited; preserve your edits before replacing or removing it")
    return old[:first] + (b"" if remove else block) + old[last + len(END):]


def owned_files(directory, desired, remove=False):
    """Plan writes/deletions; refuse foreign files and preserve local modifications."""
    manifest = directory / ".talkspec-install.json"
    safe_path(manifest)
    previous = {}
    if manifest.exists():
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        if metadata.get("owner") != "talkspec":
            raise ValueError("Unrecognized ownership manifest")
        previous = metadata["sha256"]
    for name, checksum in previous.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or str(relative) != name:
            raise ValueError("Invalid ownership manifest path")
        path = directory / relative
        safe_path(path)
        if not path.is_file() or digest(path.read_bytes()) != checksum:
            raise ValueError(f"Installed file was changed or removed: {path}")
    desired = {} if remove else desired
    plan = {}
    for name, content in desired.items():
        path = directory / name
        safe_path(path)
        if path.exists() and name not in previous:
            raise ValueError(f"Existing file is not owned by TalkSpec: {path}")
        plan[path] = content
    for name in previous.keys() - desired.keys():
        plan[directory / name] = None
    if desired:
        plan[manifest] = (json.dumps({"owner": "talkspec", "sha256": {name: digest(data) for name, data in desired.items()}}, indent=2) + "\n").encode()
    elif manifest.exists():
        plan[manifest] = None
    return plan


def installation_plan(tool, scope, mode, project, home, remove=False):
    outputs = render()
    base = home if scope == "user" else project
    if mode == "skill":
        folder = {"codex": ".agents", "claude-code": ".claude", "cursor": ".cursor"}[tool]
        destination = base / folder / "skills/talkspec"
        desired = {path.removeprefix("skills/talkspec/"): text.encode() for path, text in outputs.items() if path.startswith("skills/talkspec/")}
        return owned_files(destination, desired, remove)
    if tool == "cursor":
        if scope == "user":
            raise ValueError("Cursor user-level always-on rules require pasting adapters/cursor/user-rules.txt into User Rules; use project scope or skill mode here")
        return owned_files(base / ".cursor/rules", {"talkspec.mdc": outputs["adapters/cursor/talkspec.mdc"].encode()}, remove)
    if tool == "codex":
        base = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).expanduser() if scope == "user" else base
        path = base / "AGENTS.md"
        override = base / "AGENTS.override.md"
        if not remove and override.is_file() and override.stat().st_size:
            raise ValueError(f"{override} takes precedence; merge TalkSpec there manually or choose skill mode")
    else:
        path = (home / ".claude" if scope == "user" else base) / "CLAUDE.md"
    safe_path(path)
    old = path.read_bytes() if path.exists() else b""
    payload = outputs[f"adapters/{tool}/{'AGENTS.md' if tool == 'codex' else 'CLAUDE.md'}"].encode()
    new = managed_block(old, payload, remove)
    return {} if new == old else {path: None if remove and not new else new}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", required=True, choices=("codex", "claude-code", "cursor"))
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    parser.add_argument("--mode", choices=("always", "skill"), default="always")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Target project, not necessarily this checkout")
    parser.add_argument("--dry-run", action="store_true", help="Show destinations without writing")
    parser.add_argument("--uninstall", action="store_true", help="Remove only unmodified TalkSpec-owned content")
    args = parser.parse_args()
    try:
        plan = installation_plan(args.tool, args.scope, args.mode, args.project.absolute(), Path.home(), args.uninstall)
        for path in plan:
            safe_path(path)
        for path, data in plan.items():
            action = "Remove" if data is None else "Write"
            print(f"{'Would ' if args.dry_run else ''}{action.lower() if args.dry_run else action} {path}")
            if not args.dry_run:
                if data is None:
                    path.unlink()
                else:
                    atomic_write(path, data)
        if not plan:
            print("No changes needed")
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")


if __name__ == "__main__":
    main()

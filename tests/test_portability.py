import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import render
from install import installation_plan, managed_block, owned_files, atomic_write


def apply(plan):
    for path, data in plan.items():
        if data is None:
            path.unlink()
        else:
            atomic_write(path, data)


class PortabilityTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self):
        for path, content in render().items():
            self.assertEqual((ROOT / path).read_bytes(), content.encode(), path)

    def test_instruction_budgets_and_grok_payload(self):
        outputs = render()
        self.assertLessEqual(len(outputs['adapters/chatgpt/custom-instructions.txt']), 5000)
        self.assertLessEqual(len(outputs['adapters/chatgpt/compact-instructions.txt']), 1500)
        message = json.loads(outputs['adapters/grok/system-message.json'])
        self.assertEqual(message['role'], 'system')
        self.assertEqual(message['content'], outputs['adapters/generic/system-prompt.md'])

    def test_skill_links_are_self_contained(self):
        import re
        outputs = render()
        skill = outputs['skills/talkspec/SKILL.md']
        self.assertTrue(skill.startswith('---\nname: talkspec\n'))
        for link in re.findall(r'\]\((references/[^)]+)\)', skill):
            self.assertIn('skills/talkspec/' + link, outputs)
        self.assertEqual(len(re.findall(r'\]\(references/', skill)), 6)

    def test_managed_block_preserves_other_bytes_and_is_idempotent(self):
        for original in (b'', b'# Existing\r\nKeep this.', b'# Existing\n'):
            installed = managed_block(original, b'Rules\n')
            self.assertEqual(managed_block(installed, b'Rules\n'), installed)
            self.assertEqual(managed_block(installed, b'Changed\n', remove=True), original)

    def test_edited_or_malformed_blocks_are_rejected(self):
        good = managed_block(b'', b'Rules\n')
        for bad in (good.replace(b'Rules', b'Edits'), good + good, b'<!-- talkspec:begin -->'):
            with self.assertRaises(ValueError):
                managed_block(bad, b'New\n')

    def test_all_project_targets_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for tool in ('codex', 'claude-code', 'cursor'):
                for mode in ('skill', 'always'):
                    project = base / tool / mode
                    home = base / 'home'
                    plan = installation_plan(tool, 'project', mode, project, home)
                    apply(plan)
                    apply(installation_plan(tool, 'project', mode, project, home))
                    apply(installation_plan(tool, 'project', mode, project, home, remove=True))
                    self.assertEqual([p for p in project.rglob('*') if p.is_file()], [])

    def test_existing_project_guidance_survives_install_update_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            path = project / 'AGENTS.md'
            original = b'# Project\nRun existing checks.\n'
            path.write_bytes(original)
            apply(installation_plan('codex', 'project', 'always', project, project))
            path.write_bytes(path.read_bytes() + b'\nNew project guidance.\n')
            apply(installation_plan('codex', 'project', 'always', project, project, remove=True))
            self.assertEqual(path.read_bytes(), original + b'\nNew project guidance.\n')

    def test_foreign_files_and_modified_installs_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / 'SKILL.md'
            path.write_bytes(b'Foreign')
            with self.assertRaises(ValueError):
                owned_files(directory, {'SKILL.md': b'New'})
            self.assertEqual(path.read_bytes(), b'Foreign')
            path.unlink()
            apply(owned_files(directory, {'SKILL.md': b'New'}))
            path.write_bytes(b'Local edits')
            with self.assertRaises(ValueError):
                owned_files(directory, {}, remove=True)
            self.assertEqual(path.read_bytes(), b'Local edits')

    def test_manifest_cannot_remove_outside_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / '.talkspec-install.json').write_text(json.dumps({'owner': 'talkspec', 'sha256': {'../outside': 'a' * 64}}))
            with self.assertRaises(ValueError):
                owned_files(directory, {}, remove=True)

    def test_symlink_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / 'outside'
            outside.mkdir()
            project = base / 'project'
            project.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                installation_plan('codex', 'project', 'always', project, base)
            self.assertEqual(list(outside.iterdir()), [])

    def test_user_locations_and_codex_override(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            home = Path(tmp)
            apply(installation_plan('codex', 'user', 'always', home, home))
            self.assertTrue((home / '.codex/AGENTS.md').is_file())
            apply(installation_plan('claude-code', 'user', 'always', home, home))
            self.assertTrue((home / '.claude/CLAUDE.md').is_file())
            (home / '.codex/AGENTS.override.md').write_text('Override')
            with self.assertRaises(ValueError):
                installation_plan('codex', 'user', 'always', home, home)
            with self.assertRaises(ValueError):
                installation_plan('cursor', 'user', 'always', home, home)

    def test_dry_run_does_not_create_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / 'target'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--tool', 'claude-code', '--project', str(project), '--dry-run'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(project.exists())

    def test_plugin_metadata_version_matches(self):
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(plugin['version'], (ROOT / 'VERSION').read_text().strip())
        marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(marketplace['plugins'][0]['source'], './')


if __name__ == '__main__':
    unittest.main()

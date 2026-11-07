#!/usr/bin/env python3
"""Synthetic checkouts only: inventory prints no private config or paths."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "offline_source_inventory.py"
spec = importlib.util.spec_from_file_location("cosmic_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def git(repo, *args):
    command = ["git", "-C", str(repo), *args]
    p = subprocess.run(command, capture_output=True, text=True, check=False)
    if p.returncode:
        raise AssertionError("Synthetic git fixture command failed")
    return p.stdout.strip()


def setup_repo(root):
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    (root / "README.md").write_text("synthetic safe marker\n", encoding="utf-8")
    git(root, "add", "README.md")
    git(root, "-c", "user.name=Fixture",
        "-c", "user.email=fixture@example.invalid", "commit", "-qm", "seed")
    return git(root, "rev-parse", "HEAD")


@unittest.skipUnless(subprocess.run(["git", "--version"],
                                    capture_output=True, check=False).returncode == 0,
                     "local git is required only for synthetic fixture")
class SourceOnlyInventory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.core = self.home / "local-personal-core"
        self.core_sha = setup_repo(self.core)
        modules = self.core / "modules"
        modules.mkdir()
        self.pb = modules / "mod-playerbots"
        self.pb_sha = setup_repo(self.pb)
        self.services = modules / "mod-character-services"
        self.services_sha = setup_repo(self.services)
        (modules / "mod-autobalance").mkdir()
        (modules / "custom-client-safe").mkdir()
        (modules / "private-secret-token").mkdir()
        self.sentinel = self.core / "worldserver.conf"
        self.secret = "LOCAL_SECRET_PW_DO_NOT_PRINT_COSMIC"
        self.sentinel.write_text("DBPassword=" + self.secret, encoding="utf-8")

    def test_five_and_extra_source_modules_not_false_install(self):
        result = inventory.inventory(self.core)
        components = result["components"]
        self.assertEqual(components["Core"]["sha"], self.core_sha)
        self.assertEqual(components["Playerbots"]["sha"], self.pb_sha)
        self.assertEqual(components["Character Services"]["sha"], self.services_sha)
        self.assertEqual(components["Autobalance"]["checkout"], "no-independent-git")
        self.assertEqual(components["Individual Progression"]["checkout"], "missing")
        self.assertEqual(components["Naxxramas Core"]["checkout"], "missing")
        self.assertEqual(components["Auction House Bot"]["checkout"], "missing")
        self.assertEqual(components["Challenge Modes"]["checkout"], "missing")
        self.assertIn("custom-client-safe", result["additional_source_module_directories"])
        self.assertIn("[name-redacted]", result["additional_source_module_directories"])
        self.assertNotIn("private-secret-token", result["additional_source_module_directories"])
        self.assertEqual(result["installed_and_loaded_modules"], "not_verified")
        self.assertEqual(result["effective_config_and_paid_F14_flags"], "not_verified")
        self.assertEqual(result["databases_and_schema"], "not_checked")
        self.assertFalse(result["production_change_approved"])

    def test_tracked_modifications_report_boolean_only(self):
        first = inventory.inventory(self.core)
        self.assertEqual(first["components"]["Core"]["tracked_changes"], "no")
        (self.core / "README.md").write_text("changed-tracked-marker\n")
        second = inventory.inventory(self.core)
        self.assertEqual(second["components"]["Core"]["tracked_changes"], "yes")
        self.assertEqual(second["untracked_files"], "not_checked")

    def test_no_paths_or_credential_values_in_human_or_json_output(self):
        for is_json in (False, True):
            output = io.StringIO()
            with mock.patch.object(sys, "argv",
                                   [str(SCRIPT), "--core", str(self.core)] +
                                   (["--json"] if is_json else [])):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(inventory.main(), 0)
            rendered = output.getvalue()
            self.assertNotIn(self.secret, rendered)
            self.assertNotIn("DBPassword", rendered)
            self.assertNotIn(self.temp.name, rendered)
            self.assertNotIn("private-secret-token", rendered)
            if is_json:
                payload = json.loads(rendered)
                self.assertEqual(payload["components"]["Core"]["sha"], self.core_sha)
                self.assertEqual(payload["running_core_binary"], "not_verified")
            else:
                self.assertIn("NOT LIVE SERVER", rendered)
                self.assertIn("UNVERIFIED:", rendered)

    def test_invalid_or_symlink_root_refused(self):
        with self.assertRaises(ValueError):
            inventory.inventory(self.home / "does-not-exist")
        link = self.home / "source-link"
        try:
            link.symlink_to(self.core, target_is_directory=True)
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(ValueError):
            inventory.inventory(link)

    def test_no_git_source_gets_no_invented_version(self):
        empty = self.home / "no-git-source"
        empty.mkdir()
        result = inventory.inventory(empty)
        self.assertIsNone(result["components"]["Core"]["sha"])
        self.assertEqual(result["components"]["Core"]["checkout"],
                         "no-independent-git")
        self.assertEqual(result["components"]["Playerbots"]["checkout"], "missing")

    def test_inventory_does_not_mutate_any_source_or_config(self):
        before = self.sentinel.read_bytes()
        first = inventory.inventory(self.core)
        second = inventory.inventory(self.core)
        self.assertEqual(before, self.sentinel.read_bytes())
        self.assertEqual(first, second)
        self.assertFalse((self.core / ".git" / "index.lock").exists())
        self.assertFalse((self.pb / ".git" / "index.lock").exists())

    def test_no_exact_live_version_claim_from_reference_pin(self):
        snap = inventory.inventory(self.core)
        self.assertEqual(snap["components"]["Core"]["matches_historical_green_ci_sha"], "no")
        self.assertEqual(snap["components"]["Character Services"]
                         ["matches_historical_green_ci_sha"], "not-compared")
        self.assertEqual(snap["backups_restorable"], "not_verified")


if __name__ == "__main__":
    unittest.main()

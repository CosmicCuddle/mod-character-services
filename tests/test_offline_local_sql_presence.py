#!/usr/bin/env python3
"""Synthetic-only ignored and untracked .sql preservation warning contract.

Never inspect the owner's actual host. Git paths stay private and no file
contents, usernames, paths or credentials are printed by the tool.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "offline_source_inventory.py"
spec = importlib.util.spec_from_file_location("cosmic_sql_inventory", SCRIPT)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args],
                       capture_output=True, text=True, check=False)
    if p.returncode:
        raise AssertionError("Synthetic Git setup failed")
    return p.stdout.strip()


@unittest.skipUnless(subprocess.run(["git", "--version"],
                                    capture_output=True).returncode == 0,
                     "Synthetic Git fixture requires Git")
class OfflineLocalSQLPresence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.core = Path(self.temp.name) / "OWNER_PRIVATE_PATH_NOT_TO_PRINT"
        self.core.mkdir()
        git(self.core, "init", "-q")
        (self.core / "README.md").write_text("synthetic\n", encoding="utf-8")
        git(self.core, "add", "README.md")
        git(self.core, "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "seed")
        (self.core / "modules").mkdir()

    def test_default_unchanged_and_tracked_sql_not_local_only(self):
        tracked = self.core / "data" / "sql" / "tracked.sql"
        tracked.parent.mkdir(parents=True)
        tracked.write_text("SELECT 1;\n", encoding="utf-8")
        git(self.core, "add", "data/sql/tracked.sql")
        git(self.core, "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "tracked SQL seed")
        default = inventory.inventory(self.core)
        self.assertNotIn("local_only_sql_presence", default["components"]["Core"])
        self.assertEqual(default["local_only_sql_files"], "not_checked")
        checked = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(checked["components"]["Core"]["local_only_sql_presence"], "no")

    def test_untracked_sql_detected_without_exposing_name(self):
        secret = "OWNER_PRIVATE_UNTRACKED_SQL_12345.sql"
        (self.core / secret).write_text("PRIVATE_SQL_BODY_NEVER_SHOWN", encoding="utf-8")
        checked = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(checked["components"]["Core"]["local_only_sql_presence"], "yes")
        report = json.dumps(checked)
        self.assertNotIn(secret, report)
        self.assertNotIn("PRIVATE_SQL_BODY", report)
        self.assertNotIn(self.temp.name, report)

    def test_ignored_sql_detected_even_when_ordinary_untracked_says_no(self):
        # Git --directory may report even an empty modules/ folder as an
        # ordinary untracked directory. Compare against the BASELINE rather
        # than falsely expecting an entirely clean repository.
        (self.core / ".gitignore").write_text("*.sql\n*.SQL\n", encoding="utf-8")
        git(self.core, "add", ".gitignore")
        git(self.core, "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "ignore SQL patterns")
        baseline = inventory.inventory(self.core, check_untracked_presence=True)
        secret = self.core / "IGNORED_OWNER_CLEANUP_12345.SQL"
        secret.write_text("SECRET_SQL_NEVER_EXPOSE", encoding="utf-8")
        standard = inventory.inventory(self.core, check_untracked_presence=True)
        self.assertEqual(
            standard["components"]["Core"]["untracked_presence"],
            baseline["components"]["Core"]["untracked_presence"])
        # Existing generic untracked check filters ignored SQL regardless of
        # whether it reports unrelated directories as untracked.
        generic_names = git(self.core, "ls-files", "--others",
                            "--exclude-standard", "--directory", "-z")
        self.assertNotIn(secret.name, generic_names)
        checked = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(checked["components"]["Core"]["local_only_sql_presence"], "yes")
        self.assertNotIn("IGNORED_OWNER", json.dumps(checked))

    def test_nonindependent_and_missing_git_are_unknown_not_no(self):
        (self.core / "modules" / "mod-character-services").mkdir()
        checked = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(
            checked["components"]["Character Services"]["local_only_sql_presence"],
            "unknown")
        with mock.patch.object(inventory.shutil, "which", return_value=None):
            unavailable = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(unavailable["components"]["Core"]["local_only_sql_presence"],
                         "unknown")

    def test_cli_redacts_ignored_sql_and_default_output_unchanged(self):
        private_name = "PRIVATE_SQL_DO_NOT_PRINT.sql"
        (self.core / ".gitignore").write_text("*.sql\n", encoding="utf-8")
        (self.core / private_name).write_text(
            "PRIVATE_SQL_PAYLOAD_NOT_FOR_GITHUB", encoding="utf-8")
        for as_json in (False, True):
            out = io.StringIO()
            args = [str(SCRIPT), "--core", str(self.core),
                    "--check-local-sql-presence"]
            if as_json:
                args.append("--json")
            with mock.patch.object(sys, "argv", args):
                with contextlib.redirect_stdout(out):
                    self.assertEqual(inventory.main(), 0)
            reported = out.getvalue()
            self.assertNotIn(private_name, reported)
            self.assertNotIn("PRIVATE_SQL_PAYLOAD", reported)
            self.assertNotIn(str(self.core), reported)
            if as_json:
                parsed = json.loads(reported)
                self.assertEqual(
                    parsed["components"]["Core"]["local_only_sql_presence"], "yes")
            else:
                self.assertIn("local-only-sql=yes", reported)
                self.assertIn("NOT BACKED UP", reported)

    def test_failure_does_not_conjure_a_false_clean_state(self):
        original = inventory.subprocess.run
        def fail_sql_command(argv, *args, **kwargs):
            if "ls-files" in argv and "--ignored" in argv:
                raise UnicodeError("private undecodable name")
            return original(argv, *args, **kwargs)
        with mock.patch.object(inventory.subprocess, "run",
                               side_effect=fail_sql_command):
            checked = inventory.inventory(self.core, check_local_sql_presence=True)
        self.assertEqual(
            checked["components"]["Core"]["local_only_sql_presence"], "unknown")


if __name__ == "__main__":
    unittest.main()

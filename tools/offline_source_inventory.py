#!/usr/bin/env python3
"""CosmicCuddle read-only preflight: source checkouts, NOT a deployment verifier.

Inspect the provided *copy* of an AzerothCore source tree and module folders.
No network, SQL, config reads, processes, restarts, file edits or installers.
Do not publish output without owner review.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

# Directory names describe SOURCE checkout folders, not loaded modules.
KNOWN = {
    "Playerbots": ("mod-playerbots",),
    "Individual Progression": ("mod-individual-progression",),
    "Naxxramas Core": ("mod-naxxramas-core",),
    "Character Services": ("mod-character-services",),
    "Autobalance": ("mod-autobalance", "mod-auto-balance"),
    "Auction House Bot": ("mod-ah-bot", "mod-ahbot", "mod-ah-bot-plus"),
    "Challenge Modes": ("mod-challenge-modes", "mod-challenge-mode"),
}
SAFE_LABEL = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
SENSITIVE_LABEL = re.compile(r"password|secret|token|credential|private.?key", re.I)
PINNED_CI_TUPLE = {
    # VERIFIED source pins for historical S4 PASS Services #19, not target
    # installed revisions or permission to install.
    "Core": "d2066943e19cd959de2a0e9897135573e4124219",
    "Playerbots": "f209a3a09d4479e1d183ba62f591709822db32fe",
    "Individual Progression": "26d5b7a1de30ad92a595aaf251fc14754cf54f32",
    "Naxxramas Core": "51d0611476358286505aed3ca806ea250f644f66",
    # Services runtime is inherited from separate source DRAFT #16; avoid
    # inventing a canonical runtime SHA from a CI-only workflow descendant.
}


def safe_name(name: str) -> str:
    if SAFE_LABEL.fullmatch(name) and not SENSITIVE_LABEL.search(name):
        return name
    return "[name-redacted]"


def git_info(folder: Path, check_untracked_presence: bool = False,
             check_local_sql_presence: bool = False) -> dict[str, Any]:
    """Metadata-only; does not print paths or file content/status filenames."""
    if folder.is_symlink():
        return {"checkout": "symlink-not-inspected", "sha": None,
                "tracked_changes": "unknown"}
    if not folder.is_dir():
        return {"checkout": "missing", "sha": None, "tracked_changes": "unknown"}
    if not (folder / ".git").exists():
        return {"checkout": "no-independent-git", "sha": None,
                "tracked_changes": "unknown"}
    if not shutil.which("git"):
        return {"checkout": "git-unavailable", "sha": None,
                "tracked_changes": "unknown"}

    # GIT_OPTIONAL_LOCKS=0 prevents incidental index locks from these reads.
    # Disable external fsmonitor + untracked cache; never include secrets from
    # Git's stderr or expose any absolute local filesystem paths.
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    def call(*args: str) -> str | None:
        try:
            p = subprocess.run(
                ["git", "-c", "core.fsmonitor=false",
                 "-c", "core.untrackedCache=false", "-C", str(folder), *args],
                capture_output=True, text=True, timeout=12, env=env,
                check=False,
            )
            return p.stdout.strip() if p.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired, UnicodeError):
            # Git may report names using bytes that are invalid under the
            # runner's locale. Never crash, print a private path/traceback or
            # turn an undecodable untracked-name list into a false "no".
            return None

    toplevel = call("rev-parse", "--show-toplevel")
    if toplevel is None:
        return {"checkout": "git-metadata-unavailable", "sha": None,
                "tracked_changes": "unknown"}
    try:
        if Path(toplevel).resolve() != folder.resolve():
            return {"checkout": "nested-not-independent", "sha": None,
                    "tracked_changes": "unknown"}
    except OSError:
        return {"checkout": "path-unavailable", "sha": None,
                "tracked_changes": "unknown"}

    sha = call("rev-parse", "--verify", "HEAD")
    if not sha or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        return {"checkout": "unborn-or-invalid", "sha": None,
                "tracked_changes": "unknown"}
    porcelain = call("status", "--porcelain=v1", "--untracked-files=no")
    result = {
        "checkout": "git-root",
        "sha": sha.lower(),
        "tracked_changes": (
            "unknown" if porcelain is None else
            "yes" if porcelain else "no"
        ),
    }
    if check_untracked_presence:
        # Optional, explicit source-copy opt-in. The filenames exist only
        # inside subprocess output: never log, return or persist them.
        # --directory avoids enumerating full build trees unnecessarily.
        items = call("ls-files", "--others", "--exclude-standard",
                     "--directory", "-z")
        result["untracked_presence"] = (
            "unknown" if items is None else "yes" if items else "no"
        )
    if check_local_sql_presence:
        # Opt-in only; check ordinary untracked AND ignored paths.
        # No file content reads. Never emit or persist actual filenames.
        other = call("ls-files", "--others", "--exclude-standard", "-z")
        ignored = call("ls-files", "--others", "--ignored",
                       "--exclude-standard", "-z")
        def contains_sql(paths: str) -> bool:
            return any(name.lower().endswith(".sql")
                       for name in paths.split("\0") if name)
        result["local_only_sql_presence"] = (
            "unknown" if other is None or ignored is None else
            "yes" if contains_sql(other) or contains_sql(ignored) else "no"
        )
        # Check every Git-tracked staged, unstaged or deleted SQL path
        # without copying SQL text. Do not run external diff/textconv helpers.
        # With --no-renames, a renamed SQL retains its original deleted name.
        # Git may hash worktree contents internally; only the yes/no/unknown
        # result is exposed and no source paths leave this function.
        tracked = call("diff", "--no-ext-diff", "--no-textconv",
                       "--no-renames", "--name-only", "-z", "HEAD", "--")
        result["dirty_tracked_sql_presence"] = (
            "unknown" if tracked is None else
            "yes" if contains_sql(tracked) else "no"
        )
        observations = (result["local_only_sql_presence"],
                        result["dirty_tracked_sql_presence"])
        result["git_scoped_sql_changes"] = (
            "yes" if "yes" in observations else
            "unknown" if "unknown" in observations else "no"
        )
    return result


def inventory(core: Path, check_untracked_presence: bool = False,
              inspect_other_module_revisions: bool = False,
              check_local_sql_presence: bool = False) -> dict[str, Any]:
    """Read-only source-tree census. Never inspect config or database content."""
    if core.is_symlink() or not core.is_dir():
        raise ValueError("Core must be an existing, non-symlink directory")

    components: dict[str, Any] = {"Core": git_info(core, check_untracked_presence,
                                               check_local_sql_presence)}
    mods = core / "modules"
    folders: dict[str, Path] = {}
    if mods.is_dir() and not mods.is_symlink():
        for item in sorted(mods.iterdir(), key=lambda p: p.name.casefold()):
            if item.is_dir() and not item.is_symlink():
                folders.setdefault(item.name.casefold(), item)

    claimed = set()
    for label, aliases in KNOWN.items():
        found = next((folders[name] for name in aliases if name in folders),
                     None)
        if found is not None:
            claimed.add(found.name.casefold())
        components[label] = git_info(found, check_untracked_presence,
                                     check_local_sql_presence) if found is not None else {
            "checkout": "missing", "sha": None, "tracked_changes": "unknown"
        }

    if check_untracked_presence:
        for state in components.values():
            state.setdefault("untracked_presence", "unknown")
    if check_local_sql_presence:
        for state in components.values():
            state.setdefault("local_only_sql_presence", "unknown")
            state.setdefault("dirty_tracked_sql_presence", "unknown")
            state.setdefault("git_scoped_sql_changes", "unknown")

    other_paths = [path for name, path in sorted(folders.items())
                   if name not in claimed]
    additional = [safe_name(path.name) for path in other_paths]
    if len(additional) > 200:
        additional = additional[:200] + ["[additional-names-omitted]"]
    # Explicit opt-in: inspect other source directories, never assume loaded
    # modules. Bound Git calls so a large or hostile copy cannot hang for an
    # unbounded number of module folders. Anything beyond 20 stays UNKNOWN.
    other_revisions = []
    if inspect_other_module_revisions:
        for path in other_paths[:20]:
            other_revisions.append({
                "name": safe_name(path.name),
                **git_info(path, check_untracked_presence, check_local_sql_presence),
            })
    for label, state in components.items():
        expected = PINNED_CI_TUPLE.get(label)
        state["matches_historical_green_ci_sha"] = (
            "not-compared" if expected is None or state.get("sha") is None
            else "yes" if state["sha"] == expected else "no"
        )

    report = {
        "scope": "source folders only (not active server or installed binary)",
        "components": components,
        "additional_source_module_directories": additional,
        "untracked_files": ("checked_presence_only_in_independent_git_checkouts"
                            if check_untracked_presence else "not_checked"),
        "local_only_sql_files": ("checked_presence_only_in_independent_git_checkouts"
                                 if check_local_sql_presence else "not_checked"),
        "dirty_tracked_sql_files": ("checked_presence_only_in_independent_git_checkouts"
                                     if check_local_sql_presence else "not_checked"),
        "installed_and_loaded_modules": "not_verified",
        "running_core_binary": "not_verified",
        "effective_config_and_paid_F14_flags": "not_verified",
        "databases_and_schema": "not_checked",
        "dbc_and_client_patches": "not_checked",
        "backups_restorable": "not_verified",
        "production_change_approved": False,
    }
    if inspect_other_module_revisions:
        report["other_module_source_revisions"] = other_revisions
        report["other_module_source_revisions_omitted"] = max(
            0, len(other_paths) - len(other_revisions))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only AzerothCore source inventory; no credentials/SQL"
    )
    parser.add_argument("--core", type=Path, required=True,
                        help="existing AzerothCore SOURCE checkout (not live install)")
    parser.add_argument("--json", action="store_true",
                        help="emit local JSON (no file written)")
    parser.add_argument("--check-untracked-presence", action="store_true",
                        help="optional: yes/no only for untracked Git source files; never list names")
    parser.add_argument("--inspect-other-module-revisions", action="store_true",
                        help="opt-in Git metadata for up to 20 unknown module source folders")
    parser.add_argument("--check-local-sql-presence", action="store_true",
                        help="opt-in yes/no/unknown for ignored, untracked AND dirty tracked .sql in independent Git roots")
    args = parser.parse_args()
    try:
        result = inventory(args.core, args.check_untracked_presence,
                           args.inspect_other_module_revisions,
                           args.check_local_sql_presence)
    except (ValueError, OSError):
        parser.error("The provided Core source folder could not be inspected")
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("SOURCE-ONLY, READ-ONLY — NOT LIVE SERVER / DEPLOYMENT PROOF")
        for name, state in result["components"].items():
            sha = state["sha"]
            print(f"{name}: {state['checkout']} "
                  f"sha={sha or 'UNKNOWN'} "
                  f"tracked-modified={state['tracked_changes']} "
                  + (f"untracked-present={state['untracked_presence']} "
                     if args.check_untracked_presence else "")
                  + (f"local-only-sql={state['local_only_sql_presence']} "
                     f"tracked-sql-dirty={state['dirty_tracked_sql_presence']} "
                     f"git-sql-changes={state['git_scoped_sql_changes']} "
                     if args.check_local_sql_presence else "")
                  + f"matches-older-CI={state['matches_historical_green_ci_sha']}")
        extras = result["additional_source_module_directories"]
        print("Other module source directories: "
              + (", ".join(extras) if extras else "none detected"))
        if args.inspect_other_module_revisions:
            print("Other SOURCE checkout revisions (opt-in; NOT loaded modules):")
            for state in result["other_module_source_revisions"]:
                print(f"  {state['name']}: {state['checkout']} "
                      f"sha={state.get('sha') or 'UNKNOWN'} "
                      f"tracked-modified={state['tracked_changes']}"
                      + (f" untracked-present={state.get('untracked_presence', 'unknown')}"
                         if args.check_untracked_presence else "")
                      + (f" local-only-sql={state.get('local_only_sql_presence', 'unknown')}"
                         f" tracked-sql-dirty={state.get('dirty_tracked_sql_presence', 'unknown')}"
                         f" git-sql-changes={state.get('git_scoped_sql_changes', 'unknown')}"
                         if args.check_local_sql_presence else ""))
            if result["other_module_source_revisions_omitted"]:
                print("Additional SOURCE directories left uninspected: "
                      + str(result["other_module_source_revisions_omitted"]))
        print(("CHECKED PRESENCE ONLY: untracked source paths never printed. "
               if args.check_untracked_presence else
               "UNVERIFIED: untracked files. ")
              + ("GIT-SCOPED SQL CHANGES CHECKED: ignored/untracked PLUS "
                 "staged/unstaged/deleted tracked SQL; NOT A BACKUP. "
                 if args.check_local_sql_presence else
                 "UNVERIFIED: ignored/untracked/dirty tracked local SQL. ")
              + "UNVERIFIED: actual loaded modules; active "
                "binary; config flags; DB/SQL; DBC/client; backups; deployment.")
        print("No config values or database rows printed; no server files or services changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# CosmicCuddle — safe offline source-revision inventory (DRAFT, 7 November 2026)

**Owner:** CosmicCuddle. **Component:** Character Services' orchestration/tooling only. **Status:** review-only utility. This is **not** a deployment, merge, backup, database audit or server install. The tool was developed on an isolated branch based on the previously successful exact [five-owner Core #2 / PB #3 S4 CI draft #19](https://github.com/CosmicCuddle/mod-character-services/pull/19) at `f0763c3946519da192e522a1e42b95bded9f346e`. No changes to Character Services source, module configuration, SQL, DBC, client or existing owner server files.

## Purpose and privacy boundaries

This is the next **G5 installed-source-inventory preparation** item in [combined readiness #4](https://github.com/CosmicCuddle/Naxxramas-Server-Coordination/issues/4), not evidence that we already know the owner's real installed revision.

`tools/offline_source_inventory.py` accepts one **owner-supplied local AzerothCore SOURCE checkout path** and inspects that directory plus its immediate `modules/` folder, **only when separately run**. It reports:
- Actual Git HEAD 40-character SHA of independently versioned Core and any module directory with its own `.git`. No Git remotes, URLs, branches, usernames, local absolute paths or changed-file names are displayed.
- Whether **tracked** source differences exist (`yes/no/unknown`), without printing file names or content. **Untracked files are NOT inventoried.** A `no` means only *tracked* working files checked; it does not mean a complete clean build.
- Presence/missing/independently-versioned status for owner components Core, Playerbots, IP, Naxx, Services plus Autobalance, Auction House Bot and Challenge Modes (including common directory-name alternatives). Other source-module directories are listed by safe basename only, with names resembling secret tokens redacted.
- A **comparison label only** against the pinned owner-five-source GREEN CI tuple [Services #19](https://github.com/CosmicCuddle/mod-character-services/pull/19) (Core #2, PB #3, IP #46, Naxx #292). **Matching a GitHub test SHA does not prove what binary the server process is running.** There is no canonical Character Services runtime-only SHA inferred from CI-only heads.
- Explicit **NOT VERIFIED** for actual loaded modules, active Authserver/Worldserver binaries, effective F14/paid flags, database schemas and migration history, DBC/client/MPQ state, backup restorability, and owner release approval.

**What it does not do:** It never connects to MySQL, reads worldserver/authserver configuration values, inspects source-code contents intentionally, launches games, builds anything, sends network requests, writes report files, changes any user data, runs SQL, creates backups or restarts services. It asks the local installed `git` executable for metadata and tracked-file status. Git may inspect tracked worktree metadata/content to determine differences, **without this utility displaying those contents**. The tool rejects a symlink as the requested Core root and does not inspect symlinked module directories. Treat its output as private until CosmicCuddle approves sharing it.

## Owner-run command later, ONLY on an offline disposable SOURCE copy

From inside the Character Services checkout, after CosmicCuddle approves checking a **separate development copy**, the cross-platform command will be:

```bash
python3 tools/offline_source_inventory.py --core "/path/to/your/offline/azerothcore-source"
```

For a local structured view (again prints only to the console, no report written):

```bash
python3 tools/offline_source_inventory.py --core "/path/to/your/offline/azerothcore-source" --json
```

This is a *future optional diagnostic*, not an instruction to run it on the live production folder or to upload any config, private filesystem path or credentials. The owner has finger/wrist fatigue: at test time only **one command** is required, and the path will be filled in from the verified local offline source location, not guessed by Maintenance.

## Optional untracked-file presence check (independent DRAFT child, default OFF)

To identify a risk that an offline source tree contains local custom files not represented by its Git HEAD SHA, a separately reviewed command-line **opt-in only** may be added:

```bash
python3 tools/offline_source_inventory.py --core "/path/to/your/offline/azerothcore-source" --check-untracked-presence
```

The original command without this option remains unchanged: **untracked files are NOT checked**. When explicitly requested, the tool checks only independent Git checkouts and reports `untracked-present=yes/no/unknown` per component. It invokes Git's `ls-files --others --exclude-standard --directory -z` and immediately discards the path text; no filenames, file contents, private source paths, usernames, remotes or credential values appear in human or JSON results. Ignored files are **not included** and thus `no` does not prove an otherwise clean tree, an active deployed binary or absence of other local customisations. Missing/non-independent Git checkouts say `unknown`.

This reads additional offline source metadata and directory names; it must not be run on the owner's actual production folder without separate explicit owner permission. Synthetic hosted tests use fake private filenames and ignored files without touching the real machine. No automatic backup, deletion, restore, SQL, module activation, launch, installation, data upload, remote access or feature toggle is introduced. The new child remains **review-only**; rollback is to discard it and keep the original #21 draft source inventory tool.

## Synthetic CI and release gate

A dedicated GitHub Actions workflow runs Python standard-library unit tests against **ephemeral fake local Git repositories** created in temporary directories; synthetic private-config contents are never shown. It separately tests the CLI JSON/human output on the disposable GitHub checkout. Strict change allowlist limits this review-only PR to `tools/offline_source_inventory.py`, `tests/test_offline_source_inventory.py`, this document, and its CI workflow, with **no runtime/config/SQL changes**. Hosted CI must finish and be inspected before anyone claims a pass.

**Release readiness remains BLOCKED:** after collecting a source-only inventory later, need an independently verified active binary/source hash (not merely a folder), all loaded module list (including Autobalance/AHBot/Challenge), exact effective configuration with sensitive values kept private, DB migrations, DBC/client patch baseline, correctly scoped backup+actual restore rehearsal, explicit test-server approval, and real 3.3.5a F01–F20 plus paid/Hunter/quest855 gameplay acceptance. All experimental features stay OFF.

**Rollback:** Discard this tool-only development DRAFT; no database, gameplay, service, machine configuration, host or owner source copy has been modified by Maintenance. Preserve the passing five-fork build #19 and pending separate PB #6 combined S4 #20 as distinct, noninterchangeable evidence.

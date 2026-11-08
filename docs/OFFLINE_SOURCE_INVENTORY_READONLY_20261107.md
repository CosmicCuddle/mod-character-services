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

**Non-UTF-8 path safety:** Some local filesystems permit untracked filenames with raw bytes that cannot be decoded using the current terminal locale. Git can output those raw names during the optional presence check. The preflight now catches Python Unicode decoding errors from Git, reports **`untracked-present=unknown`** instead of crashing or wrongly reporting `no`, and does not disclose the private offending name. Two new regression tests cover a simulated decoding exception and, on supported POSIX UTF-8 runners, an actual synthetic invalid-byte filename. **`unknown` is not proof that no untracked work exists.** This does not read a real owner source tree or perform an automatic repair.

This reads additional offline source metadata and directory names; it must not be run on the owner's actual production folder without separate explicit owner permission. Synthetic hosted tests use fake private filenames and ignored files without touching the real machine. No automatic backup, deletion, restore, SQL, module activation, launch, installation, data upload, remote access or feature toggle is introduced. The new child remains **review-only**; rollback is to discard it and keep the original #21 draft source inventory tool.

## Optional OTHER custom module source revision check — separately opt-in (8 November 2026)

The default inventory enumerates safe names of extra source folders, but **does not report their independent Git revisions**. The offline source copy may have more owner custom modules than our initial five-repository CI (e.g., Guild Strongholds, Autobalance, AHBot, Challenges, events). This is a **coverage gap, not evidence they are installed**. A second new opt-in can inspect independent Git metadata for at most **20 additional module directories**:

```bash
python3 tools/offline_source_inventory.py --core "/path/to/your/offline/azerothcore-source" --inspect-other-module-revisions
```

- The **old/default output remains unchanged**; only this flag adds the `other_module_source_revisions` and `other_module_source_revisions_omitted` fields (in JSON) or an extra human-readable source-revision section.
- Each result shows only its existing privacy-filtered label, Git root/commit SHA and **yes/no/unknown tracked file modification**. Combine with the *separate explicit opt-in* `--check-untracked-presence` if the owner later approves checking for untracked files (still only yes/no/unknown, never names). Directory names that resemble credentials are redacted.
- The **20-directory cap** bounds Git reads/time and prevents accidental scans of arbitrarily large source trees. More folders are counted as **omitted** and remain unknown. A `no-independent-git` module is not necessarily missing or clean; it might be tracked by the Core checkout or copied from a ZIP. The root Git commit may not represent that module's own author/version.
- A source directory present on disk **does not** mean it is enabled, compiled, loaded or deployed. Git metadata does not establish running binary, actual config/DB/DBC/client, restorable backup or player gameplay. No source or user files are written by this tool. It still must only run on the owner-approved **offline copy**.

Synthetic source tests verify a second independent fake module's actual commit, modified tracked files, unknown/non-independent source checkout, redacted directory labels, default absence of new schema, both CLI output modes and a >20-folder truncated case. These are review-only CI tests, not live-host observations.

## Synthetic CI and release gate

A dedicated GitHub Actions workflow runs Python standard-library unit tests against **ephemeral fake local Git repositories** created in temporary directories; synthetic private-config contents are never shown. It separately tests the CLI JSON/human output on the disposable GitHub checkout. Strict change allowlist limits this review-only PR to `tools/offline_source_inventory.py`, `tests/test_offline_source_inventory.py`, this document, and its CI workflow, with **no runtime/config/SQL changes**. Hosted CI must finish and be inspected before anyone claims a pass.

**Release readiness remains BLOCKED:** after collecting a source-only inventory later, need an independently verified active binary/source hash (not merely a folder), all loaded module list (including Autobalance/AHBot/Challenge), exact effective configuration with sensitive values kept private, DB migrations, DBC/client patch baseline, correctly scoped backup+actual restore rehearsal, explicit test-server approval, and real 3.3.5a F01–F20 plus paid/Hunter/quest855 gameplay acceptance. All experimental features stay OFF.

**Rollback:** Discard this tool-only development DRAFT; no database, gameplay, service, machine configuration, host or owner source copy has been modified by Maintenance. Preserve the historical passing five-fork build #19. Separately, the newer owner Core2/PB7/IP120/Naxx292/Services16 combined [CI-only DRAFT #25](https://github.com/CosmicCuddle/mod-character-services/pull/25) passed [native S4 #42413815378](https://github.com/CosmicCuddle/mod-character-services/actions/runs/42413815378), **26/26 steps on exact pins**; neither CI proves the owner-host S5 inventory or gameplay.

## S5 optional local-only SQL presence — protected ignored-file warning (8 November 2026)

**Review-only child of [source inventory #24](https://github.com/CosmicCuddle/mod-character-services/pull/24).** Local SQL cleanups and migrations can be ignored by Git and would not be detected by `--check-untracked-presence`, which deliberately uses `--exclude-standard`. The owner has explicitly prioritised preserving tracked, untracked and ignored SQL before any checkout, reset, clean, compilation or module upgrade.

This child adds **a separate OFF-by-default opt-in**, for a later owner-approved disposable **offline source copy only**:

```bash
python3 tools/offline_source_inventory.py --core "/path/to/approved/offline/azerothcore-source" --check-local-sql-presence
```

The tool asks Git within each independently versioned checkout for both (1) **ordinary untracked** and (2) **ignored untracked** paths, then checks file extensions case-insensitively for **`.sql`**. It reports only `local-only-sql=yes/no/unknown` per checked source component, and the existing optional extra-module revision check can inspect up to 20 additional independent Git repositories. It never prints any actual local filename, full path, SQL content, Git remote, private credential, user account, schema or DB value; it does not open SQL files, modify files, upload results, connect to a database, create archives or run cleanup. The original CLI without this option retains its historical output except for an explicit `local_only_sql_files: not_checked` JSON status and stronger warning; no inspection occurs by default.

**Strict limit:** `no` means only *no .sql files in the ignored/untracked paths Git returned for that particular independent checkout*. It does **NOT** include tracked-but-dirty SQL, binary or ZIP backups, standalone SQL directories outside that checkout, nested uninspected independent repositories, modules without their own Git root, SQL schema/migration order, installed custom SQL or a recoverable backup. A missing independent Git repository, permission error, encoding failure or timeout returns **UNKNOWN**, never "no". A full S5 preflight MUST also catalogue and checksum **all tracked/modified/untracked/ignored SQL files and local patches**, copy them somewhere recoverable outside all source/build folders, and successfully restore the backup in a disposable environment. This lightweight warning cannot satisfy that preservation gate, authorise `git clean` or let any upgrade proceed.

The new separate six-case synthetic Git fixture tests cover tracked baseline, ignored SQL (including uppercase extension), ordinary untracked SQL, unknown/no-independent-Git, private-path redaction in both CLI formats and a forced decoding error. None touches the owner's actual machine. No production, client, SQL, F14, paid, config, database or gameplay permission follows from hosted CI.

## S5 optional dirty tracked SQL warning — staged, unstaged, deleted and renamed paths (8 November 2026)

**Owner:** CosmicCuddle. **Component:** Character Services offline tooling only, child of [Services DRAFT #39](https://github.com/CosmicCuddle/mod-character-services/pull/39) at immutable `5322ba69939400005f58b61db327e4dd515a3dec`. **No host operation, server installation, SQL execution, DB login, backup, client/DBC/config, module or F14 change.** This update does not modify the already successful source-only #39 workflow or promote its code to deployed.

The exact **same already opt-in** invocation now checks another category of local SQL risk:

```sh
python3 tools/offline_source_inventory.py --core "/path/to/approved/disposable/azerothcore-source" --check-local-sql-presence
```

Within each independently versioned Git root, the original optional scan already reads path metadata for **ordinary untracked** and **ignored untracked** `.sql` files. This child additionally invokes `git diff --no-ext-diff --no-textconv --no-renames --name-only -z HEAD --` to find Git-**tracked** SQL filenames with changes relative to HEAD, including **unstaged edits, staged edits, unstaged or staged deletions, and SQL renamed to a different extension**. Using `--no-renames` shows the original deleted SQL path even if its replacement is now a `.txt`. Git may internally hash worktree contents in order to compare files; **the Python tool never opens or prints SQL text**, Git stderr is discarded, and actual local filenames/user paths/DB credentials are never included in JSON or terminal output. The scan returns only per-component yes/no/unknown:

- `local_only_sql_presence`: original ignored + untracked SQL (unchanged meaning).
- `dirty_tracked_sql_presence`: new staged/unstaged/deleted tracked SQL path presence.
- `git_scoped_sql_changes`: yes if either source says yes; unknown if no yes and either scan unavailable; no only if BOTH independent Git path checks finish and find none.

The human output equivalents are `local-only-sql`, `tracked-sql-dirty`, `git-sql-changes`. The default CLI **without this flag does not run the additional Git diff or path scans**, and JSON retains `not_checked` status. Repositories without independent Git roots, unreadable filenames, Git failures, missing HEAD, unsupported operation or timeout are **UNKNOWN**, not falsely clean. If the operator also selects `--inspect-other-module-revisions`, the same optional check runs on at most the first 20 independent additional module source roots; others are uninspected.

**Hard limitation:** even `git-sql-changes=no` does NOT mean a safe update: it says only that Git reported no changes to these categories of `.sql` paths in an inspected independent checkout. It does **not** list/checksum/backup clean tracked SQL, SQL stored outside source, loose backups/ZIPs, external databases, child modules beyond the inspection bound, skip-worktree/assume-unchanged differences, custom client/DBC files, active owner server files, schema migration state, restore validity or ignored non-SQL customisations. Never run `git clean`, `git reset --hard`, cleanup SQL, module upgrades or source swaps because of a `no` result. The final S5 preservation gate still requires a comprehensive private manifest and a recoverable copy of **all tracked, untracked, ignored and external SQL, source changes and patches** plus an actual restored disposable backup.

**Synthetic tests only:** isolated temporary Git repositories with private mock filenames and SQL payload strings test staged, unstaged, deleted, renamed-away-from-SQL, other ignored/untracked, Git failures, default-opt-out and JSON/human redaction. The original installed owner machine is never contacted. Rollback is discard this tooling-only draft, returning to Services #39. No new runtime config or feature switch is introduced.

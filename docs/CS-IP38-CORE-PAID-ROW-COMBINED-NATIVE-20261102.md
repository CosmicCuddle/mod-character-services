# Combined native test — scoped Core paid-row preservation + IP #38 + Core module #286 + Services #7

**Date:** 2 November 2026. **Status:** separate CI/docs-only DRAFT and paid feature OFF. **Owner:** CosmicCuddle. Parent [Services #8](https://github.com/CosmicCuddle/mod-character-services/pull/8) at frozen `236de545c1289dc203e90148f06d9966fa740c45`; its already-SUCCESS joint native test remains unchanged for comparison.

## Exact source tuple and one-file patch

- Grimfeather pinned AzerothCore Core `8daffdabe9202c228e45d833c9a1d399597a15cd`. Apply ONLY the [IP #38 raw paid-ledger patch](https://github.com/CosmicCuddle/mod-individual-progression/pull/38) in the **disposable CI runner**, requiring original `PlayerSettings.cpp` Git blob `f1eb86367ce69111867ef7187125f5fe456c5367`, and verify `git diff --name-only` is EXACTLY `src/server/game/Entities/Player/PlayerSettings.cpp` with clean `git diff --check`.
- Pinned Playerbots `e88cc4099e69f35126b28942a412ca702d20453b`, retaining the **same two known compatibility substitutions in the disposable runner only** from prior successful Services workflows.
- [IP #38](https://github.com/CosmicCuddle/mod-individual-progression/pull/38) exact `bd44c18063f313e2ed605ca85d9a86e6614036dc`: inherited unpaid quest10259 checks plus new v1 raw paid receipt policy, login/account gates, staged gold+flag+receipt save and separate no-launder Core patch file.
- [Naxx Core module #286](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/286) exact `edbed1937ab9312cbef24309845595cdb2ccf8fe`, existing P1–P4/P4-H/F15 protected state.
- [Character Services #7](https://github.com/CosmicCuddle/mod-character-services/pull/7) vendor parent exact `48e2f73795f82dd45b1a067b64754cb31f234bc7` inherited through Services #8 and this CI-only PR. Do not alter existing vendor runtime sources, config or SQL.

## CI evidence boundary

New workflow `.github/workflows/character-services-core-paid-row-ip38-naxx286-joint-native-20261102.yml` clones the successful #8 one, changes only the IP exact SHA and one Core patch step, retains the historical source-blob pin, PB runner-only edits, proof of all module C++ translation units and native full Worldserver link. A linked binary on an isolated GitHub runner is only **build integration evidence**. It is NOT proof of real-gold transactions, player-login persistence, Core data-byte preservation after a SQL roundtrip, quest offers/altbots, 30-day P3 archive, startup stability, backups, or owner-installed revisions.

**Critical caveats:** The Core patch is not currently in a connected owner-controlled AzerothCore Core fork and is NOT applied to any real server. Existing malformed `ip_paid_expansion` rows must not be corrected or discarded without backup/evidence; this patch preserves the original raw strings on normal Core load/save and refuses standalone offline writes on malformed rows. Other modules explicitly calling `Player::UpdatePlayerSetting` on a malformed source still need audit. Approved v1 bootstrap, `pdump` paid records, owner stage8 quest criterion/G1, `DisableDefaultProgression=1`, actual installed versions, staging and owner deployment permission remain blockers.

**Rollback:** Discard this CI-only child and return to Services #8. No production or database rollback needed. Paid and Naxx experimental config flags remain OFF.


## Current exact-pin update (2 Nov 2026)

Earlier joint runner [41436349871](https://github.com/CosmicCuddle/mod-character-services/actions/runs/41436349871) used the first #38 patch asset head `1814e44855aa77de97aabe17f83014d2af99e040` and reached real combined Worldserver compilation; it is historical evidence only. After implementing IP's strict canonical-format compatibility, direct `ValidLedger` version-zero tests, NDEBUG-safe receipt policy and an actual-Core-settings fake DB harness with a CI correction, this workflow was moved to the newer exact IP #38 commit `bd44c18063f313e2ed605ca85d9a86e6614036dc`. This preserves the same pinned Core patch and older Core/PB/Naxx/Services refs while making the combined native job represent the newer receipt code. The latest CI must be checked anew. **No owner host/DB or production deployment.**

# Full Worldserver native gate: two-file Core malformed-row read/write protection

**State:** CI/docs-only DRAFT; no live server, data, DB, config or account changes. **Owner:** CosmicCuddle. Child of [Services #9](https://github.com/CosmicCuddle/mod-character-services/pull/9) (previous one-file Core patch build).

## Exact immutable build composition

- Grimfeather Core `8daffdabe9202c228e45d833c9a1d399597a15cd`, with pinned source `PlayerSettings.cpp` blob `f1eb86367ce69111867ef7187125f5fe456c5367` and `Player.h` blob `5a29ac7b40ade7a11f1fcf36623dc7530ea39595` checked before patch.
- [IP DRAFT #39](https://github.com/CosmicCuddle/mod-individual-progression/pull/39) at `064c20a42b10db472ac9017770e2b4c89ec98883`, a child of #38, supplies one reviewable patch covering only two Core files. The diff protects original malformed `ip_paid_expansion` strings against normal autosave, offline UpdateSetting, *implicit* GetPlayerSetting and explicit UpdatePlayerSetting.
- Playerbots `e88cc4099e69f35126b28942a412ca702d20453b` with same two historical compatibility edits **only on disposable CI runner**.
- Naxxramas Core module #286 `edbed1937ab9312cbef24309845595cdb2ccf8fe` and inherited Character Services vendor source from Services #7, with both feature flags default OFF.

## Native test

New `.github/workflows/character-services-core-dualfile-ip39-naxx286-joint-native-20261102.yml` copies previously running #9 native Worldserver build, checks exact two Core source blobs, applies patch ONLY on disposable runner, verifies two and only two Core source files changed, enforces default-OFF/owner source snapshots, compiles/links Worldserver without launching or uploading. This is the first native test that uses the real patched `Player.h` rather than fake-DB harness substitute. The CI outcome must be checked at this exact PR head; **do not infer success from older #9 builds**.

**Not solved:** owner-controlled Core fork missing, v1 receipt commissioning/legacy/data migration, `.pdump` omission, current live host/backups, genuine MySQL first/second login, payment crash/restart, unpaid quest10259 G1, `DisableDefaultProgression=1` pending owner decision, and production approval. The source patch may only be integrated after independent review and owner-controlled Core branch/approval. Rollback discard this draft; existing #9 unchanged.

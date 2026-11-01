# CosmicCuddle — joint Character Services + Individual Progression + Naxx Core development compile gate

**Date:** 1 November 2026. **Owner:** CosmicCuddle. **Status:** CS01 Maintenance DRAFT, source/CI only, unmerged and NOT installed.

## Purpose and exact dependency versions

This isolated child of [Character Services fee-hardening DRAFT #4](https://github.com/CosmicCuddle/mod-character-services/pull/4) at `ee2f5fec3e077c7af7f818d20132329bde5803ca` retargets **only** the existing, non-launching, pinned Worldserver workflow `.github/workflows/character-services-ip-paid-native-link-20261101.yml`. The Character Services C++, pricing logic, Vezrath service menus and all default-OFF configs are untouched.

The development dependencies chosen for an actual combined source link are:

| Component | Repository/source ref | Reason |
| --- | --- | --- |
| Core | `Grimfeather/azerothcore-wotlk@8daffdabe9202c228e45d833c9a1d399597a15cd` | Historical pinned AzerothCore compile environment; **not** owner-installed-state proof |
| Playerbots | `mod-playerbots/mod-playerbots@e88cc4099e69f35126b28942a412ca702d20453b` | Previous joint vendor workflow's pinned compatibility source; runner-only exact two compatibility edits preserved |
| IP fork | [Combined GM commands + paid warnings DRAFT #28](https://github.com/CosmicCuddle/mod-individual-progression/pull/28) `740a792da88ba3cbf8b0d0db74ce438266247fc2` | Earned vs purchased-era API, self-only `.ip get`, GM audit, warning-only guard; **default paid OFF** |
| Naxx Core | [P1–P4/P4-H + P3 F15 operator tools DRAFT #280](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/280) `deebd7b68d2966ede6dc80a8da92d1351e4cb7eb` | P1 Warlock, P2 Hunter ammunition, P3 World/Auth diagnostic capture, P4 quest loot, default-OFF P4-H, and two opt-in **read-only** P3 operator tools |
| Character Services | Inherited owner-preserving [DRAFT #4](https://github.com/CosmicCuddle/mod-character-services/pull/4) `ee2f5fec3e077c7af7f818d20132329bde5803ca` + this CI-only child | Vezrath passes purchase through IP; standard fee arithmetic signed-safe; expansion offers still OFF |

## Custom Modifications Register — CS01-CROSSMODULE-NATIVE-PIN-20261101

- **Intended behaviour:** compile and link all *current development source candidates together* rather than relying solely on separate old-source links. No new gameplay behavior, paid entitlement, SQL, binary deployment or host process is introduced.
- **Source change:** only `.github/workflows/character-services-ip-paid-native-link-20261101.yml` retargets its IP and Naxx checkout refs and exact-pin assertions from old #23/#273 to #28/#280, fixes displayed labels, and verifies the reviewed `cs_individualProgression.cpp` and `MasterLootQuestGive.h` Git blobs plus two F15 read-only scripts. No runner build, checkout or compatibility-edit semantics have been broadened.
- **Dependencies:** linked C++ code still uses a historical pinned Core + Playerbots, with two narrowly checked **runner-only** Playerbots source replacements from the inherited joint workflow. This is not the installed owner build or a proof that all owner's custom IP, bot, client, DBC, SQL or character data matches.
- **Tests / evidence:** hosted exact-head native compile/link and CI results **must be checked before any PASS claim**. A linked Worldserver is *not launched*. No automated test proves purchasing with real gold, refund/relogin, DK/race, GM/console command privacy, BOT progression, in-world Warlock portal/Hunter ammo/loot, or World/Auth crash retention. The P3 F15 raw-audit and preview scripts are independent of any actual owner host.
- **Risks:** future upstream changes, historical pinned Core/PB mismatch, run-time configuration, quest-template/DB world conditions 66013 vs separate paid Wrath storage, owner Vezrath NPC identity and prices, legacy account grandfather policy. Especially, SQL quest condition 66013 is earned Kil'jaeden progress, **not** automatic proof of a paid Wrath purchase. Do not retarget any SQL rows without owner approval and installed-world verification.
- **Live status and rollback:** NOT merged/installed/enabled, no player data changed. Revert this CI-only child to restore the original Character Services #4 pinned link. Reverting source does not repair player data after an actual payment, so a future owner-authorized live change requires backups, staging acceptance, a tested database rollback/refund policy and explicit CosmicCuddle approval.

## Next release gate

1. Observe the workflow's exact-head GitHub Actions results, including compilation units and final Worldserver link. Resolve source errors in separate reviewed child branches without overwriting approved custom gameplay.
2. Confirm the owner's actual installed Core, Playerbots, IP, Character Services and Naxx Core commit/config/SQL/DBC identities and backups; then repeat a pinned compile against those versions.
3. On an owner-authorized disposable staging environment, test P1 Warlock, P2 Hunter, P3 actual World/Auth capture plus retention, P4 per-human loot, Vezrath paid entitlement, command privacy, gold/quest rollback, bots and all feature-OFF parity.
4. Request owner's **separate approval** before merging, installing, enabling, scheduling file retention, modifying client/SQL or touching live player data.

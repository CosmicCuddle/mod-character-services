# Latest combined native Worldserver candidate — Core #286 + IP #34 + Character Services #7

**Date:** 2 November 2026. **Owner:** CosmicCuddle. **State:** Separate DRAFT CI-only child, no production installation, no gameplay or server launch. Historical pinned [Services #6](https://github.com/CosmicCuddle/mod-character-services/pull/6) and formatting [#7](https://github.com/CosmicCuddle/mod-character-services/pull/7) stay unchanged.

## Immutable source tuple

- Grimfeather Core: `8daffdabe9202c228e45d833c9a1d399597a15cd` (historical compilation base only; not evidence of installed Core).
- Playerbots: `e88cc4099e69f35126b28942a412ca702d20453b` with **exact two runner-only compatibility edits** retained from historical Services CI. These have NOT been integrated or installed on owner host.
- Individual Progression [DRAFT #34](https://github.com/CosmicCuddle/mod-individual-progression/pull/34): `5ee5fc48262dd9b7cb1e5abd7f0673cdc0e6abc5`, combining paid TBC stage7-after-purchase rule, Hunter/group/F14/F19, pre-completion veto and new saved-COMPLETE login-only normalization S1 (OFF by default).
- [Mod-Naxxramas-Core DRAFT #286](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/286): `edbed1937ab9312cbef24309845595cdb2ccf8fe`, latest protected P1–P4/P4-H/F15 source+test composition. Latest P4 interop source workflow SUCCESS; this does NOT imply all Core CI or gameplay PASS.
- [Character Services #7](https://github.com/CosmicCuddle/mod-character-services/pull/7): `48e2f73795f82dd45b1a067b64754cb31f234bc7`, includes the only six-byte whitespace fix to #6's vendor source. This child workflow uses its own **exact invoking PR HEAD** for Services, so it includes this CI/docs addition while preserving the original vendor source bytes.

## What this workflow checks

New file `.github/workflows/character-services-core286-ip34-joint-native-20261102.yml` is a separate copy of the historical successful link workflow with only pinned IP/Core refs, descriptive labels, the new filename and fail-closed S1/line99 source asserts. It does not change the historical workflow or production C++.

On a disposable GitHub-hosted Ubuntu runner it checks exact source SHA pins, owner source snapshots, protected default-OFF paid and P4 switches, IP API presence, Core P4-H/f15 files, and IP 10259 S1 guard; applies only the two existing pinned PB compatibility edits in that ephemeral runner; compiles and links a single native `worldserver` and verifies that the executable exists **without launching it**. A successful link would prove only this immutable composition is buildable. It would **not** prove no crash, correct purchases, live relogs, quest offers/shares, bot/group rules, raids, 30-day archive retention or any owner installation.

## Blocks / operator control

Exact-head hosted CI is **not verified at creation**. The server-installed source/config, full World/Auth console collection, functional 30-day closed-owned retention, latest combined gameplay tests, backup/restore and explicit CosmicCuddle deployment approval are still open. TBC Quest 10259 offer/accept/share, offline GM reward, `DisableDefaultProgression`, already rewarded recovery, receipt/pdump remain blocking; source status alone cannot enable paid expansion. No owner database or player gold is touched.

**Rollback:** Close/discard this unmerged CI/docs child and return to Services #7. No production or SQL rollback needed.

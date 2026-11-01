# CosmicCuddle — combined Character Services + IP F19/paid + Naxx P3 archive native link

**Date:** 1 November 2026. **Owner:** CosmicCuddle. **Status:** unmerged / not installed / review-only DRAFT. No live gold, logs, client, DB, server config or running service touched.

## Purpose

Upgrade the *actual static Worldserver module compile/link test* already developed in [Character Services DRAFT #5](https://github.com/CosmicCuddle/mod-character-services/pull/5) (pinned exact source `5e8304b680dd20f3b972eb7afcd404fbf0d5ad5c`) to the most recently integrated source without changing the established Vezrath/vendor C++ or money logic:

- [IP combined paid/GM/default-OFF F14/F19 DRAFT #31](https://github.com/CosmicCuddle/mod-individual-progression/pull/31) exact `6b67cb9c1fdbdb54cabd8e4f83a88236ee7ffd51`. This includes reviewed startup warning-label test #30 and the exact F19 level floor/limit saved-stage safeguard ported from original #24. Grok independently reported exact-head **local** source and policy PASS, *not* native Worldserver/gameplay PASS.
- [Naxx combined Warlock/Hunter/P3/P4 + guarded P4-H + copy-only F15 archive DRAFT #283](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/283) exact `16314bf0a958266742ed9ce68598645d8cfcd173`, child of #281 with its corrected symlink/manifest validation and #282's exact umask-private fixture, CI for the original F15 archive/retention suites and full pinned link. These scripts do not automatically delete raw logs.
- Parent [Character Services fee/vendoring DRAFT #4](https://github.com/CosmicCuddle/mod-character-services/pull/4), exact `ee2f5fec3e077c7af7f818d20132329bde5803ca`. Existing owner Vezrath and fee implementation is carried forward unchanged.

The existing joint CI uses historical pinned Grimfeather AzerothCore and Playerbots plus two **runner-only** narrowly checked PB compatibility substitutions; this is **NOT** the owner's installed source version.

## Custom Modifications Register — CS01-JOINT-F19-P3-CROSSMODULE-CHECK-20261101

| Field | Record |
| --- | --- |
| Intended behaviour | Build/link the combined real development C++ with paid/GM plus F19 login cap and Naxx P1/P2/P3/P4/archiver, while testing all modules with **existing feature flags default OFF**. No new gameplay semantics. |
| Owning component and affected files | Child of #5, changing **only** `.github/workflows/character-services-ip-paid-native-link-20261101.yml` and this memo. Reviewed source/fee C++, SQL, config, DBC, client data and player records unchanged. |
| Source dependencies | Exact IP #31 `6b67cb9`, Core module #283 `16314bf`, Character Services #5 parent. Pure F19 header SHA `eb3e9d5c4ad7077b91174088bf4e7d44ce826517`, GM source blob `278aaa48dc5fb7770bd6013e659e4872752d4b03`, Naxx MasterLoot header blob `dc1b9c1d53bfc6405187efb06a5425e4ffd9fd91`, F15 scripts checked on the CI runner. |
| Tests / evidence | The workflow is an actual historical-pinned **full static Worldserver compile/link, no launch**. Its own exact-head GitHub run must complete successfully before any native PASS. Other PRs' local 20+ archive tests and Grok local IP tests are **source/disposable evidence only**. No actual playerbots staged login, services purchase/refund, Warlock/Hunter/loot gameplay, owner-host World/Auth capture, real 30-day retention or production deploy has been done. |
| Risks | Current installed Core/Playerbots/IP, Character Services, Autobalance, Auction Bot, Challenge Modes and client/SQL/DBC revisions are unverified; `.pdump` may not copy paid `character_settings`; logged paid status is not sufficient proof of durable receipt; F14 and Paid remain OFF; World/Auth raw originals are never automatically purged. |
| Rollback | Drop this child to retain source #5 workflow/pins; original #31, #283, #4 branches and custom code are untouched. No database repair, release activation or rollback of actual player money is inferred from reverting code. |

## Safe release gates

- [ ] Exact-head CI (not pending) links the combined Worldserver under fixed historical Core/PB.
- [ ] Review actual installed owner commits and dependencies, complete approved backups and verify restore on a disposable staging environment.
- [ ] Run targeted bot 0/8/13 and F19 limit cases, human effective-era/GM, Vezrath paid grant/failed refund, World/Auth archive refusal/no-deletion, Warlock summoning, Hunter ammunition and quest-loot multi-human tests.
- [ ] Resolve world quest66013 earned vs purchased conditions and grandfather/pdump policy with the owner; no blanket retarget.
- [ ] Obtain **explicit** CosmicCuddle approval before any merge, production install, config enablement, account data access, live host archive copy or log cleanup.

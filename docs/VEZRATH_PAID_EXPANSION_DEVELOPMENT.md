# Vezrath earned-then-paid expansion purchase — Development Candidate

**Owner:** CosmicCuddle. **Date:** 2026-11-01.  
**Status:** **DRAFT C++ SOURCE, not compiled/linked/staged/live**. All new configuration is default OFF.  
**Preservation parent:** [Character Services original source snapshots PR #1](https://github.com/CosmicCuddle/mod-character-services/pull/1).  
**Required IP API:** [Individual Progression paid-entitlement DRAFT PR #23](https://github.com/CosmicCuddle/mod-individual-progression/pull/23) exact API as of SHA `5fde28560ae5dd940329a82894111e757d7b7b44`. **This vendor branch is not independently buildable against old IP master without that interface.**  
**Owner decision and unresolved historical details:** [coordination Issue #18](https://github.com/CosmicCuddle/Naxxramas-Server-Coordination/issues/18).  
**Master tasks:** [IP roadmap DRAFT #22](https://github.com/CosmicCuddle/mod-individual-progression/pull/22).

## Required gameplay contract

- Final Vanilla stage7 (current Kel'Thuzad) **earns eligibility only**; pay Chronomancer Vezrath to open **TBC entry stage8** and the permitted level cap/locations.
- Final TBC stage13 (current Kil'jaeden) **earns eligibility only**; pay Vezrath for a **separate per-character Wrath flag**. Payment **never awards stage14**, which means the first Wrath raid tier is already completed.
- Paying without earning the final boss is denied; earning the boss but not paying leaves the character in the current era.
- Ordinary tier purchasing/catch-up (action100+) must not sell stage7, stage8, stage13 or stage14 as an alternative cross-era shortcut when paid entitlement enforcement is active; this code uses IP's `GetMaxServiceGrantableStage` at BOTH menu and purchase time.
- Bots, races, Death Knights, excluded accounts and GM overrides are handled by the corresponding IP feature policy. Vendor code does not invent new exceptions.

## This vendor branch's ACTUAL source changes

1. The existing, safer upstream `src/CharacterServices.cpp` remains the starting point. It retains `IsStandardServiceEnabled`, `CanPurchaseProgressionTier` pre-debit validation, and ordinary names/race/faction service handling.
2. When **both** `CharacterServices.ExpansionUnlock.Enable=1` and IP `IsPaidExpansionActive()` hold, menu actions 200 (TBC) and 201 (Wrath) are shown only for an eligible character. `InsufficientFunds` may still show a priced offer so the player knows what to save for.
3. The gossip offers show their configured gold prices in confirmation text but send **0 copper as the Core gossip-menu fee**: the IP purchase method is the **sole money-debit authority**, preventing a second automatic menu fee. On selection the vendor **revalidates price/config/era** then delegates the *entire charge and grant* to IP's `PurchaseExpansion`. It neither calls `ModifyMoney` nor `ForceUpdateProgressionState` itself in that purchase route. A double click yields `AlreadyOwned` without charging again according to IP's runtime contract.
4. Config price is expressed in **gold** and checked before conversion to **copper**. Zero or any price exceeding signed-32-bit safe copper is refused, not wrapped. Distributed defaults **1000g / 3000g** preserve the historical ZIP values but **are not confirmed live/approved prices**. DynamicCost is not applied to these two expansion passage offers.
5. Top-level sender and service-enabled guards reject invalid gossip requests; these guards also protect the old generic service path. Tier purchase revalidation checks IP's entitlement-aware maximum before debit.
6. New `tests/test_cs_paid_expansion_source.py` and scoped CI provide **source-only** checks. They cannot prove compiled API compatibility, money persistence, packet-level replays, client-side display, success/failure rollback or gameplay.

## Open technical / gameplay questions

- Source IP #23 defaults OFF and depends on Core `EnablePlayerSettings=1`; without that, no new vendor expansion purchase is available. This feature is **not active or guaranteed** merely by compiling this module.
- IP #23 has its own save/refund logic. Confirm on real staged server that money, quest marker and entitlement save atomically, and that exceptions, shutdown, relog and repeated/select-delayed gossip cannot charge twice. Do not assume Gold/DB atomicity from C++ source alone.
- Confirm the exact final milestones (and pre/post-raid optional gates) with Information, and treatment of existing stage13/purchased characters, account catch-up, GM bypass, Blood Elf/Draenei and Death Knight start privileges.
- Owner calls NPC **Chronomancer Vezrath**. Unchanged tracked world SQL names **Chronomancer Amberwind**. The actual installed NPC, spawn, script binding and world DB have NOT been inspected; **do not run the upstream SQL blindly**.
- Validate gold presentation/requirements in the exact AzerothCore gossip implementation. The module delegates purchase money to IP; it must not accidentally trigger a second automatic client/server fee. Confirm after compiling against pinned Core/IP.
- Generic original `ProgressionTier.RequireAccountUnlock` OFF can permit all in-era catch-up tiers. Owner needs to approve whether that still applies. No unapproved economic design changes are made.
- This is the first code candidate. Separate native Worldserver full link, high-fidelity synthetic tests and actual staged human Vezrath tests are REQUIRED before any merge/enable/deployment.

## Tests / rollback / approval

Run exact compiled Core+IP#23+CharacterServices PR with compatibility verified against Playerbots and Naxx; test boss-only, paid-only, valid purchase, insufficient funds, tampered packet, double click, server restart, saved entitlement, inherited characters, no stage14, stage13 unpaid XP/travel, human/bot starts and generic-tier bypass. Back up character database and running configuration, rehearse rollback with **money+entitlement consistency**. Keep IP and vendor feature switches OFF on production until the owner approves the finished deployment. Reverting this vendor branch to upstream while leaving IP default OFF restores legacy source; payment migration/rollback cannot be assumed safe if previously enabled.

**No source ZIP applied wholesale, no upstream license/content removed, no live processes/config/SQL/DB/files touched.** Historical originals remain byte-identical in the docs snapshot.

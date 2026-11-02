# CosmicCuddle Character Services — Custom Modifications Register

**Owner / authority:** CosmicCuddle. **Recorded:** 2026-11-01. **Status:** preservation [DRAFT #1](https://github.com/CosmicCuddle/mod-character-services/pull/1) + executable vendor source [DRAFT #2](https://github.com/CosmicCuddle/mod-character-services/pull/2); neither is merged, full-build-tested, staged or installed.  
**Upstream:** [Grimfeather/mod-character-services](https://github.com/Grimfeather/mod-character-services) `main` at `f43bc2c98aa7a291b673158fd578be304607b5e1`.  
**Owner fork:** [CosmicCuddle/mod-character-services](https://github.com/CosmicCuddle/mod-character-services), fork parent confirmed via GitHub. The fork's `main` originally matched upstream exactly.  
**Source of owner customisations:** owner-provided `mod-character-services.zip`, **SHA-256 `4ff5ac34ee9cd247fa9c429850b0786a6b835872fb1f8caaea5fc32321be8b84`**. This ZIP is a historical reference **not proof of currently installed live server files**.

## What was preserved

The ZIP contains exactly **22 regular files**. Comparing Git blob identifiers against the fork's baseline tree: **20 file blobs match upstream exactly**, and only these **two** differ:

| Owner ZIP file | Owner ZIP original blob SHA | Upstream blob SHA | Preservation in fork |
| --- | --- | --- | --- |
| `src/CharacterServices.cpp` | `a391656aa9a57e94d761a3b887a3af651d9e6dcc` | `687f50ef76989d26d1a9a1880597af28d01f17df` | `docs/source-snapshots/CharacterServices-owner-20261101.cpp` — **byte-identical original, noncompiled reference** |
| `conf/character_services.conf.dist` | `45b22671f7459c2dd156299360ae937a3e99b699` | `45c920947094c66e96a1a979e957529aa25a6507` | `docs/source-snapshots/character_services-owner-20261101.conf.dist` — **byte-identical original, non-installed reference** |

**This preservation PR deliberately leaves live source paths `src/CharacterServices.cpp` and `conf/character_services.conf.dist` unchanged from the safe upstream baseline.** Do not replace them blindly with the older ZIP content: upstream code has purchase-validation improvements, and the ZIP itself contains charged-before-validation and era-skip hazards. Preserve the old intended behaviour via a separate new reviewed integration PR, retaining upstream fixes. Original snapshots are historical evidence **and unsafe for direct deployment**.

## Custom change inventory

### CS-OWNER-001 — original Chronomancer expansion unlock offers
- **Documented ZIP intent:** two independent Vezrath expansion purchase options after the current-era final milestone, action 200 for Vanilla→TBC and 201 for TBC→Wrath.
- **Original behaviour:** old implementation calls `ForceUpdateProgressionState(8)` for TBC or `ForceUpdateProgressionState(14)` for Wrath **after gold debit**. This is **not** the owner's new rule: stage14 marks Wrath tier 1 completed and must never be awarded by paying.
- **New owner rule:** final Vanilla milestone (current code Kel'Thuzad stage7) earns eligibility, payment opens TBC's starting stage8; final TBC milestone (current code Kil'jaeden stage13) earns eligibility, payment enables Wrath separately **without** awarding stage14. Characters must complete both steps; purchases alone cannot bypass earned requirements.
- **Source / dependencies:** original two snapshots; [IP paid entitlement DRAFT #23](https://github.com/CosmicCuddle/mod-individual-progression/pull/23); [IP task list DRAFT #22](https://github.com/CosmicCuddle/mod-individual-progression/pull/22); [coordination decision request #18](https://github.com/CosmicCuddle/Naxxramas-Server-Coordination/issues/18). Actual latest IP C++ runtime integration and staging still pending.
- **New implementation:** **DRAFT SOURCE committed in [#2](https://github.com/CosmicCuddle/mod-character-services/pull/2)**. Vendor displays distinct TBC/Wrath offers only when both feature flags and IP eligibility hold; it delegates sole debit/entitlement/grant through IP `CanPurchaseExpansion` / `PurchaseExpansion` using checked copper. The vendor has a zero-fee gossip menu; it never calls `ForceUpdateProgressionState(14)` or directly debits the expansion purchase. **No native link/gameplay/economy acceptance yet.**
- **Rollback:** disable new integration feature (default OFF) then owner-reviewed source/config rollback. Do not automatically refund/deduct gold or migrate stages.

### CS-OWNER-002 — configured services, progression catch-up and prices
- **Owner ZIP distributed defaults:** CharacterServices enabled; standard name/appearance/race/faction changes disabled; tier purchasing enabled; max applicable tier18; DynamicCost disabled; expansion unlock enabled; price **1000 gold** Vanilla→TBC and **3000 gold** TBC→Wrath. These are **not confirmed live settings or final price approval**.
- **Original source risk:** action IDs 100+ and 200/201 can write progression separately; old tier handler deducts gold before enforcing tier/account checks; stale/forged action IDs and cost scaling are unsafe if copied wholesale.
- **Required preservation:** ordinary owner-approved services and within-era catch-up preserved where compatible; **no direct tier buy can bypass the final-boss-plus-paid era gate**, and tier14 must not be granted by Wrath purchase. Confirm cross-character account catch-up policy with Information and CosmicCuddle.
- **New implementation:** **DRAFT SOURCE committed in [#2](https://github.com/CosmicCuddle/mod-character-services/pull/2)**. The generic tier handler rejects out-of-range action IDs before `uint8` conversion, checks entitlement cap in menu and pre-debit, validates the target quest marker and progression cap, bounds conversion through shared `CharacterServicesMoneyPolicy.h`, and uses non-destructive incremental progression instead of clearing old rewarded markers. It verifies the exact target marker and refunds the explicit debit on failure. Generic and expansion menu entries display prices but do not request an additional Core gossip fee. Existing configured *zero-gold generic* purchase is retained, while zero-gold *expansion passage* remains unavailable. **Unfinished:** verify C++ compile, actual realm/source version, money/entitlement atomicity, partial multi-marker failure and relog/restart; staging tests for forged actions, invalid price, double click and all exemptions.
- **Rollback:** retain previous working source and config as owner backup, not the ZIP alone; database migration/payments require an explicit restoration plan.

### CS-OWNER-003 — NPC name and DB compatibility
- **Observed source discrepancy:** tracked `data/sql/db-world/character_services_NPC.sql` creates entry 390011 **Chronomancer Amberwind**, while owner reports the actual NPC as **Chronomancer Vezrath**. No world DB content/spawns were inspected.
- **Intent:** retain owner's NPC identity, location/spawn, existing services and character account data.
- **New implementation:** PLANNED; verify configured live world DB/script link in read-only staging before any migration. Never run the default SQL blindly or spawn a duplicate.

## Engineering and release gates

1. Compare installed AzerothCore/IP/Playerbots/Naxx/Character Services version, owner source/config/SQL against both upstream fork and owner ZIP. A committed snapshot is not installed evidence.
2. Write a **separate actual code DRAFT PR** for the new vendor integration, preserving original custom behaviour and current upstream safety fixes.
3. Confirm and test cross-module IP PaidExpansion enable, Core `EnablePlayerSettings=1`, persisted per-character entitlement, login reminder, stage13 effective access, bot/race/DK/GM exemptions and catch-up caps. No silent enabling.
4. Compile exact pinned full Worldserver/Authserver as applicable and use real staged gossip, purchase, failure, gold, unlock, relog/restart, access and rollback tests. Historical native CI from another SHA doesn't qualify.
5. Backup affected files/config/character database; document reversible migration and potential payment discrepancies. **CosmicCuddle explicitly approves any merge/deploy/production DB, config or NPC change.** No production change is made by this register.

**Maintenance responsibility:** keep this file up to date with exact branches/commit SHAs, tests, changed paths, rollback and owner decisions. Record Information answers in the same coordination Issue rather than implying an automatic reply.

### CS-OWNER-004 — paid vendor/IP configuration mismatch fail-closed safety (follow-on DRAFT)
- **Owner intent:** entry to TBC/Wrath requires completed final boss plus explicit paid passage; neither a disabled or unsupported IP entitlement dependency nor a vendor config mismatch may silently expose a generic-tier shortcut.
- **Original issue in DRAFT #2 source:** with the new IP API present, `CharacterServices.ExpansionUnlock.Enable=1` but IP paid gate INACTIVE, `CanOfferProgressionTier` previously returned true unconditionally before checking the effective ceiling. This could fall through to historical generic tier purchasing; legacy IP without the new API already failed closed under the same vendor config. **Source-level conditional defect, not a live exploit report.**
- **Reviewable correction:** a separate pure header `src/CharacterServicesGatePolicy.h` now decides the shared generic menu-and-debit eligibility. **Vendor ON + IP OFF** denies generic tier offers and selections; **both OFF** preserve the historical service; **IP ON** enforces `GetMaxServiceGrantableStage`, whether vendor ON or OFF. All other account/tier/payment/quest validation remains intact; expansion purchase actions still require both flags. Old-IP compile fallback remains unchanged and denies generic purchase when the vendor paid flag is ON.
- **New tests:** `tests/character_services_gate_policy.cpp` is a C++17/C++20 executable 2×2 flag matrix plus before/after cap cases; source wiring checks confirm the same shared guard is used on the generic menu and pre-debit selection. Disposable GCC/Clang CI added. These checks do **not** test real IP/core config reloads or gameplay.
- **Ownership / status:** CS01 Maintenance, isolated branch `fix/cs01-paid-gate-flag-mismatch-20261101` stacked on Character Services DRAFT #2 exact parent `2074a99fdcf0bded8bc9d0126425e7843b44c94c`. Source and tests are in a review-only candidate; full Core/PB/IP/Character Services link, staged NPC/gold/relog and effective installed config tests are pending. No source, DB or service enabled in production.
- **Rollback:** leave feature OFF; if approved later and reverted, restore matching earlier vendor binary/config as a unit with IP; preserve paid character records and require owner-reviewed rollback for any real purchases.

### CS-OWNER-005 — joint combined Naxx/IP/Character Services source-build contract (DRAFT evidence only)
- **Purpose:** avoid reporting an old Naxx-only compatibility pin as proof the new P4-H and Vezrath integration coexist. Joint workflow now pins Naxx [DRAFT #273](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/273) at `e5431f03b5b841268a46edb1bc108561a968e60f`, IP paid [DRAFT #23](https://github.com/CosmicCuddle/mod-individual-progression/pull/23) at `42a21d6bd9bb91877105dd4cd6f45df814ceecdf`, and exact current Character Services DRAFT #3 head. Historical Core/PB pins remain test-only. The workflow checks OFF switches, API v1, actual source units and full static Worldserver link; **no server is started and no installed owner version is verified**.
- **Known blocker:** IP #23 at this pin contains Grok-confirmed reload/settings-store paid-gate fail-open N1. CS03-IP owns corrective source code; re-pin after reviewed fix, never interpret old green compile as payment-gameplay readiness.
- **Ownership/status:** CS01 Maintenance CI integration, source-only reviewable GitHub workflow. Host CI queued or pending until exact runner result observed; no live config/DB/Gold, NPC, account, hook activation, binary rollout or backups.
- **Rollback:** revert the scoped YAML pin and documentation change on the development branch if candidate source incompatibility arises; protected main and production unchanged.

### CS-OWNER-006 — effective account entitlement ceiling for generic progression services

- **Intent:** account catch-up must not interpret a different character's earned but unpaid Kil'jaeden stage13 as **paid Wrath access**. Both earned and paid requirements remain distinct; do not remove existing owner class/race or bot privileges.
- **Source change:** `src/CharacterServices.cpp::AccountProgressionForTierService` selects `GetAccountEffectiveProgression(accountId)` when `COSMIC_IP_PAID_EXPANSION_API_VERSION == 1`, retaining historical `GetAccountProgression` fallback for older IP without the paid API. Used at **both generic tier menu and pre-debit validator**. Account cap still intersects with IP's per-character `GetMaxServiceGrantableStage`, configured max, next-tier check and hidden-quest preflight. This does not grant entitlements or change existing `ForceUpdateProgressionState` paths.
- **Dependency:** [IP paid-entitlement DRAFT #23](https://github.com/CosmicCuddle/mod-individual-progression/pull/23) exact `78d0967c074661cfdb529d231dfa1432ead7741b` introduces the new static account helper and the configuration-reload N1 source hotfix; [Naxx combined DRAFT #273](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/273) exact `e5431f03b5b841268a46edb1bc108561a968e60f`. Cross-module CI exact pin updated. **These are evolving, unmerged API-v1 DRAFT refs, not guaranteed installed API compatibility.**
- **Tests/evidence:** a new Python source contract checks helper's API-v1 selection and historical fallback, and checks both menu and pre-debit call sites. Disposable joint CI checks actual IP header/function source, Master Loot source graph and full static Worldserver. Independent Grok review of the IP N1/account change remains pending; native CI and in-game account/gossip checks unproven.
- **Owner and rollback:** CS01, isolated stacked Character Services DRAFT #3. Safe rollback is revert this default-OFF vendor code/workflow to prior development SHA with matched IP dependency; do not migrate entitlement, alter paid records, update live SQL, or charge/refund characters. Preserve owner ZIP snapshots and protected main. Owner permission required for production activation.


## Latest pinned native build correction — H2 duplicated-header include

During hosted Naxx H2 C++ compilation, the older combined source failed because `QuestLootSparkleGuard.cpp` directly included unguarded `UnitUtils.h` twice (once transitively through `Creature.h`). Claude corrected this at [H2 DRAFT #270](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/270) exact `d3d576d9ea85786e19b2180079cbee2c2b2ce885`; CS01 independently copied its **exact three H2 source/test/doc blobs** into the parent [Naxx combined #271](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/271) `e1b9c65a8bce0f8241491db49a109da07d60c8c9`, [#273](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/273) `090e2fb6f89c695f616411561d2fb2fb5f8f46c2`, and GO test [#275](https://github.com/CosmicCuddle/Mod-Naxxramas-Core/pull/275) `0fe049975166e614633bce9e5c77b9f8b686dc54`. The real H2 C++ file differs by only a removed direct include; default flags and behavior unchanged. GitHub three-dot stacked comparisons may show the shared three H2 files until ancestry is reconciled, even though file blobs are identical between those heads.

The disposable Character Services joint native link workflow now pins the **corrected #273 head `090e2fb6`**, alongside IP paid #23 `78d0967`, its historical Core/PB compatibility pins, and this PR exact head. **No compiled/link PASS is claimed for the repaired combined source until exact-head workflow success is observed**; old failed/queued commits do not qualify. The GO test-only #275 is a separate composed candidate, not required to change the current native runtime pin. No owner server, production config, live DB, character gold/loot or historical source snapshots were modified.

### CS-OWNER-007 — legacy standard-service price overflow guard (separate DRAFT)

- **Scope / source:** `src/CharacterServices.cpp`, new `src/CharacterServicesStandardPricePolicy.h`, executable test `tests/character_services_standard_price_policy.cpp`, shared source-contract test and workflow. Owner's original code snapshots and standard services remain present.
- **Existing risk in prior development source:** `GetServiceCost` multiplies unsigned configured gold by 10000 without an upper-bound check and `ModifyMoney(-cost)` applies unsigned negation before converting to a signed API argument. Unusually high custom prices can silently wrap or make debit behavior compiler-dependent. This is a source-level configuration risk, **not proof that CosmicCuddle uses high prices or suffered a loss**.
- **New actual code:** per-service `TryGetStandardServiceCost` validates configured gold and dynamic-level calculation before either a client gossip fee is offered or the server debits money. A pure helper retains the original double-based /80 dynamic cost rounding for valid signed amounts, default 25/50/100/250 gold, and deliberately configured ZERO-cost services. Misconfigured fee becomes an unavailable offer / error rather than a wrapped price. Existing enabled actions 1–4 and their at-login flags are untouched. A single `ModifyMoney(-static_cast<int32>(cost))` is used after server-side fee validation.
- **Automated checks:** executable C++17/C++20 GCC/Clang policy checks (historic default/dynamic parity, zero/free, max signed, 429497g wrap attempt, level-over-80 guard) and source checks proving menu AND pre-debit both use the same validation. All test results require exact-head runner confirmation; native Worldserver + actual gossip, fee persistence and client regressions still unverified.
- **Ownership/status/rollback:** CS01, isolated stacked DRAFT `fix/cs01-standard-service-money-overflow-20261101` on Character Services #3 parent HEAD `585aa643cc0bc4f4d73ed8234c929201b7d8e200`. No merges, server config, installed prices, SQL, accounts or world operations. Roll back only this source/test change on the development branch; keep service OFF if its configured price is invalid and obtain owner review before activating a changed binary.

### SERVICES-CORE286-IP34-LINK-20261102 — latest cross-fork native composition (CI-only DRAFT)

| Field | Record |
| --- | --- |
| Owner / scope | CosmicCuddle; CS01 Maintenance isolated Services #7 child, new CI-only workflow plus memo; original vendor, parent workflows and installed realm unchanged. |
| Intended behaviour | Independently compile/link immutable Core/PB/IP/Services source tuple at Core #286, IP #34 and Services #7, all paid and experimental switches default OFF. Never run the Worldserver. |
| Affected files / pins | New `.github/workflows/character-services-core286-ip34-joint-native-20261102.yml` pinned Core `8daffdabe`, Playerbots `e88cc409`, IP `5ee5fc48262dd9b7cb1e5abd7f0673cdc0e6abc5`, Naxx `edbed1937ab9312cbef24309845595cdb2ccf8fe`, Services exact PR HEAD. New `docs/CS-IP34-NAXX286-JOINT-NATIVE-GATE-20261102.md`; append register. |
| Compatibility / safety | Retains only existing two disposable runner PB edits and exact OFF flags; no runtime code, config, SQL, DBC, client, quests, gold, archive or owner host changes. Latest pin is NOT owner-installed evidence. |
| Tests | Hosted native workflow run not yet verified, no gameplay. Check exact CI run SHA and complete link before claiming PASS. |
| Rollback / live state | DRAFT only, feature OFF; discard child to return unchanged Services #7. No merge/live server action without CosmicCuddle permission. |

### SERVICES-IP38-CORE-RAW-PRESERVE-NATIVE-20261102 — patched Core/receipt combined build (CI-only DRAFT)

| Field | Record |
| --- | --- |
| Owner/source | CosmicCuddle / CS01. CI/docs-only child of Services #8 `236de545`, immutable IP #38 `1814e448`, Naxx #286 `edbed193`, Grimfeather Core `8daffdabe`, PB `e88cc409`; Services vendor #7 inherited. |
| Intended behaviour | Test actual Worldserver link with a one-file Core settings-row no-launder patch applied **only on a disposable CI checkout**, strict v1 IP raw ledger login/account/purchase and existing cross-module sources. All paid switches OFF. |
| Affected files | New `.github/workflows/character-services-core-paid-row-ip38-naxx286-joint-native-20261102.yml`, memo, this register append. No runtime, SQL, DBC, client, config or owner Core changes. |
| Risks/tests | Source pin and patch blob checked; untrusted malformed raw records must remain untouched. Actual new-head CI not verified at creation; no gameplay, DB, receipts, owner host, archive/live operations. Other direct Core settings writers, transfer, bootstrap remain blockers. |
| Rollback | Discard isolated CI/docs PR. Require owner-controlled Core fork, restorable backups, full staging and explicit deployment approval before any live application. |


**SERVICES-IP38-CORE-RAW-PRESERVE-NATIVE-20261102 exact tuple update:** New native CI workflow pins IP #38 `bd44c18063f313e2ed605ca85d9a86e6614036dc` (first version `1814e44855aa77de97aabe17f83014d2af99e040` is historical). Same Core source pin/patch and other module versions. Source-only test and documentation changes are not gameplay/host proof; do not attribute earlier native run 41436349871 to this newer pin.

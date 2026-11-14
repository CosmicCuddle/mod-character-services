# Custom Modifications Register

This register tracks CosmicCuddle-specific behavior in this repository. Entries do not imply merge, deployment, live activation, or approval of production pricing.

## CS-PAID-01 — Paid-era generic progression-tier bypass guard

- **Intended behavior:** When Individual Progression paid-expansion gating is active, the legacy generic progression-tier service must not cross the character's paid-era service ceiling. If Character Services requests paid expansion integration but compatible IP support is unavailable, fail closed.
- **Owning component:** Character Services generic progression-tier menu/selection logic.
- **Affected files:** `src/CharacterServices.cpp`, `src/CharacterServicesGatePolicy.h`, distributed config, tests/workflow.
- **Source refs:** Base main `f43bc2c98aa7a291b673158fd578be304607b5e1`; DRAFT #78.
- **Dependencies:** Individual Progression paid API >=1 for paid-aware account/effective ceilings.
- **Known risks:** Must preserve established within-era account catch-up while preventing cross-era bypass; paid/IP mismatch must fail closed.
- **Tests:** Pure policy workflow PASS; source contracts PASS; repository codestyle PASS.
- **Live status:** NOT merged/deployed; config default OFF.
- **Owner decisions:** Earned final-era milestone makes that character eligible to purchase the next expansion; account-highest progression must not bypass the paid boundary.
- **Rollback:** Revert DRAFT #78; no SQL/data migration.

## CS-PAID-02 — Chronomancer Vezrath paid expansion API v2 consumer

- **Intended behavior:** Offer TBC/Wrath passage only when IP says the character is eligible. Submit payment through IP exactly once. `Submitted` means pending durability, not success; Pending/Unconfirmed cannot be charged again; only `Active` is owned.
- **Owning component:** Character Services Vezrath gossip/UI. Individual Progression owns debit, receipt, durability, entitlement and final activation.
- **Affected files:** `src/CharacterServices.cpp`, `src/CharacterServicesMoneyPolicy.h`, distributed config, tests/workflows.
- **Source refs:** Stacked DRAFT #79 over #78; designed against IP DRAFT #184 API v2 head `d325d081bc3310978b1383930b631bc8c4fad012`.
- **Config/SQL/DBC/client dependencies:** `CharacterServices.ExpansionUnlock.Enable=0` by default. Historical draft prices are 1000g TBC / 3000g Wrath, but production prices are NOT yet owner-approved. No SQL/DBC/client patch.
- **Known risks:** Requires compatible IP API v2; commissioning/missing receipt policy, injected DB-failure test, callback-confirmed phasing refresh and owner price decision remain release gates.
- **Tests:** Fast source/policy/codestyle workflows pass where completed. A pinned full Worldserver link against IP API v2 is required and may still be running.
- **Live status:** NOT merged/deployed; no real gold charged.
- **Owner decisions:** Paid access is per-character; TBC purchase does not directly grant stage 8; Wrath purchase does not grant stage 14; no early success message or duplicate charge.
- **Rollback:** Revert #79 then #78; keep IP paid feature OFF. No production data migration has occurred.

# Custom Modifications Register

This register tracks CosmicCuddle-specific behavior in this repository. Entries do not imply merge, deployment, live activation, or production-price approval.

## CS-PAID-01 — Paid-era generic progression-tier bypass guard

- **Intended behavior:** When Individual Progression paid-expansion gating is active, the legacy generic progression-tier service must not cross the character's paid-era service ceiling. If Character Services requests paid integration but compatible IP support is unavailable, fail closed.
- **Owning component:** Character Services generic progression-tier menu/selection logic.
- **Affected files:** `src/CharacterServices.cpp`, `src/CharacterServicesGatePolicy.h`, distributed config, tests/workflow.
- **Source refs:** Base main `f43bc2c98aa7a291b673158fd578be304607b5e1`; DRAFT #78.
- **Dependencies:** Individual Progression paid API >=1 for paid-aware account/effective ceilings.
- **Known risks:** Must preserve established within-era account catch-up while preventing cross-era bypass; paid/IP mismatch must fail closed.
- **Tests:** Pure policy workflow PASS; source contracts PASS; repository codestyle PASS.
- **Live status:** NOT merged/deployed; config default OFF.
- **Owner decisions:** Earned final-era milestone makes that character eligible to purchase the next expansion; account-highest progression must not bypass the paid boundary.
- **Rollback:** Revert DRAFT #78; no SQL/data migration.

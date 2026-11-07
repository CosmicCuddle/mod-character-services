# Paid-expansion vendor → IP → Core: queued save versus committed purchase (7 Nov 2026)

**Owner:** CosmicCuddle. **Safety:** source-only audit and automated regression checks, no runtime code, DB/SQL, character gold, client, server, or config changes. **Target:** future owner-approved offline paid-expansion test readiness, not feature activation. Based on independent successful five-owner Core2/PB3/IP46/Naxx292/Services #19 exact source tuple.

## Why we are checking this

The user-approved gameplay timeline **MUST remain unchanged**:
- Kel'Thuzad 40 earned raw stage7 → eligible to pay Vezrath for TBC → purchase leaves raw stage7 → *rewarding quest10259* advances raw stage8.
- Kil'jaeden earns raw stage13 but effective unpaid stage12 → paid Wrath receipt makes effective stage13, never awards stage14 or a first Wrath raid completion.
- All purchases per character; custom start privileges, original bot/excluded exceptions, old earned markers, and paid default OFF are protected. **Never treat this audit as a decision** on missing/legacy paid ledger rows or `DisableDefaultProgression`.

## Verified source sequence, exact pins, not an observed incident

**Character Services owner source:** inherited from owner Services runtime DRAFT #16, in successful five-fork Services CI #19 `f0763c3946519da192e522a1e42b95bded9f346e`.

1. Vezrath actions 200/201 call `sIndividualProgression->PurchaseExpansion(player,era,copper)`. They **do not** charge separately, call `ForceUpdateProgressionState`, write a receipt or run SQL. If IP returns `PurchaseResult::Success`, Character Services immediately says **“Expansion access purchased successfully.”**

**IP owner source #46:** `26d5b7a1de30ad92a595aaf251fc14754cf54f32`, `src/IndividualProgressionExpansion.cpp`.

2. `PurchaseExpansion` calls `CanPurchaseExpansion` and validates the canonical eight-slot receipt with `RecordPurchase` *before* taking money. It subtracts in-memory copper, sets the in-memory TBC/Wrath flag and checks the resulting logical entitlement; on immediate logical failure it refunds in memory.
3. It then writes **all eight** staged receipt slots into Player settings and calls `player->SaveToDB(false,false)`, logs a purchase and returns `PurchaseResult::Success` **without receiving or awaiting a database commit acknowledgment**. Importantly, this is a **one-way** Core save; this does not prove the transaction was executed, retried successfully or persisted before the message was sent. No observed owner gold-loss incident, partial DB write or server crash is asserted.

**Core owner source #2:** `d2066943e19cd959de2a0e9897135573e4124219`.

4. `Player::SaveToDB(bool,bool)` returns `void`, assembles a `CharacterDatabaseTransaction`, and calls the **void** `CharacterDatabase.CommitTransaction(trans)`. The Core pool enqueues a `TransactionTask` and does not return its eventual success. Its *separate* `AsyncCommitTransaction` returns a `TransactionCallback`, but the existing `Player::SaveToDB` pathway and IP paid purchase do **not** call that interface. A queue-drain check would also be inadequate: the worker pops the transaction *before* executing it. **No such queue-drain workaround should be introduced.**
5. Whether the receipt and character money rows are ultimately committed together in the exact installed Core transaction, how failed writes/retry/crashes behave, and how purchases are reconciled after relog remain **unverified here**. Do NOT propose or copy a new async callback on the same Player object without reviewing map-thread ownership, destruction and CharacterDatabase transaction synchronization.

## Scope of the new automated checks

Three new files only on this separate Character Services source review DRAFT:
- `tests/test_paid_ip_save_commit_acknowledgement_source.py`: checks actual owner Core #2, actual IP #46 and vendor source for validation → one debit → full receipt settings → void SaveToDB → immediate Success → vendor success message; confirms no callback/commit acknowledgment is present and preserves default OFF and stage7→quest10259→8 / Wrath13-not14 semantics.
- `.github/workflows/character-services-paid-ip-save-ack-source-20261107.yml`: pins immutable Core/IP SHAs and Services parent, allows **only these three test/docs/CI paths**, runs new checks and existing Services paid-expansion source checks on GitHub's throwaway runner. No Core/PB/IP/Naxx/Services runtime modifications, DB connections, SQL, character saves or player interaction.
- This document. **Check the actual hosted Actions result before claiming these tests passed.**

## Safe future change proposal — NOT selected or implemented

A real durable purchase acknowledgment may require a separately reviewed, per-character transaction-completion protocol that does **not** change Core `Player::SaveToDB` globally, weaken the owner-paid strict receipt decoder, block map/world threads, or prematurely grant any stage. Possible solution designs have trade-offs:
- Return a distinct **pending** state and confirm only after a source-backed successful character+settings commit; require a safe world-thread callback and revalidation on disconnect/relog.
- Reconcile a pending purchase on login against durable, canonical paid v1 receipt and persisted money, using approved idempotent transaction semantics; never re-charge or overwrite malformed/legacy/lost-transfer rows.
- Preserve legacy `A1/A2` commissioning choice, `B1/B2` `DisableDefaultProgression`, `G-a/G-b` GM entitlement override and excluded-account policy as OWNER-PENDING in [Coordination #18](https://github.com/CosmicCuddle/Naxxramas-Server-Coordination/issues/18). No implicit selection.

Before any implementation: prove actual installed Core/IP/Services SHAs, full module compatibility (PB, Naxx, Autobalance, AHBot, Challenge Modes), restore-tested offline character database and executable/config backups, and dedicated failure injection on a **disposable test server** (failed SQL transaction, disconnect, restart during pending purchase, double click, paid log-in and old receipt). Never run failed-transaction tests on production. Preserve raw7 then 10259 reward, raw13 Wrath effective13, no stage14 grant. Require CosmicCuddle's explicit approval for live modifications.

**Rollback of this review only:** discard its DRAFT branch. No SQL, gold, quest, NPC, player account, source runtime or production data was modified.

#!/usr/bin/env python3
"""Cross-owner paid purchase receipt-save timing audit. SOURCE ONLY.

Uses exact owner Core #2, IP #46 and Services runtime from #19.
This is NOT a real paid purchase, DB, staged migration, rollback or server test.
"""
from pathlib import Path
import os
import unittest

SERVICES = Path(__file__).resolve().parents[1]
CORE = Path(os.environ["COSMIC_PAID_SOURCE_CORE"]) if "COSMIC_PAID_SOURCE_CORE" in os.environ else None
IP = Path(os.environ["COSMIC_PAID_SOURCE_IP"]) if "COSMIC_PAID_SOURCE_IP" in os.environ else None


def between(source: str, start: str, stop: str) -> str:
    assert source.count(start) == 1, f"Expected one verified source anchor: {start!r}"
    first = source.index(start)
    last = source.index(stop, first + len(start))
    return source[first:last]


class PaidExpansionSaveCommitBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CORE or not CORE.is_dir() or not IP or not IP.is_dir():
            raise AssertionError("CI must supply exact owner Core/IP checked-out source")
        cls.coreh = (CORE / "src/server/game/Entities/Player/Player.h").read_text()
        cls.storage = (CORE / "src/server/game/Entities/Player/PlayerStorage.cpp").read_text()
        cls.pool = (CORE / "src/server/database/Database/DatabaseWorkerPool.cpp").read_text()
        cls.worker = (CORE / "src/server/database/Database/DatabaseWorker.cpp").read_text()
        cls.ipcpp = (IP / "src/IndividualProgressionExpansion.cpp").read_text()
        cls.ippolicy = (IP / "src/IndividualProgressionExpansionPolicy.h").read_text()
        cls.vendor = (SERVICES / "src/CharacterServices.cpp").read_text()
        cls.ipdist = (IP / "conf/individualProgression.conf.dist").read_text()
        cls.csdist = (SERVICES / "conf/character_services.conf.dist").read_text()
        cls.purchase = between(
            cls.ipcpp, "PurchaseResult IndividualProgression::PurchaseExpansion(",
            "void IndividualProgression::EvaluatePaidExpansionGrandfather(")
        cls.vendor_paid = between(
            cls.vendor, "if (action == 200 || action == 201)",
            "#else\n      // Historical IP lacks durable entitlement/payment API.")

    def test_vendor_delegates_charge_and_does_not_mint_markers(self):
        h = self.vendor_paid
        self.assertIn("sIndividualProgression->PurchaseExpansion(", h)
        self.assertIn("purchased == ExpansionResult::Success", h)
        self.assertIn('"Expansion access purchased successfully."', h)
        self.assertLess(h.index("PurchaseExpansion("),
                        h.index('"Expansion access purchased successfully."'))
        self.assertNotIn("ModifyMoney(", h)
        self.assertNotIn("SaveToDB(", h)
        self.assertNotIn("ForceUpdateProgressionState(", h)
        self.assertNotIn("UpdateProgressionState(", h)

    def test_ip_checks_before_debit_then_stages_and_queues(self):
        p = self.purchase
        for required in (
            "CanPurchaseExpansion(player, eraValue, costCopper)",
            "if (check != PurchaseResult::Success)",
            "ReceiptPolicy::RecordPurchase(stagedLedger,",
            "player->ModifyMoney(-static_cast<int32>(costCopper));",
            "SetPaidExpansionFlag(player, index, FlagPaid);",
            "for (uint32 slot = 0; slot < ReceiptPolicy::Slots; ++slot)",
            "player->UpdatePlayerSetting(PaidExpansionSettingSource, slot, stagedLedger.fields[slot]);",
            "_paidExpansionLedgers[player->GetGUID().GetCounter()] = stagedLedger;",
            "player->SaveToDB(false, false);",
            "return PurchaseResult::Success;",
        ):
            self.assertIn(required, p)
        self.assertLess(p.index("CanPurchaseExpansion("),
                        p.index("player->ModifyMoney(-"))
        self.assertLess(p.index("ReceiptPolicy::RecordPurchase("),
                        p.index("player->ModifyMoney(-"))
        self.assertLess(p.index("player->ModifyMoney(-"),
                        p.index("player->SaveToDB(false, false);"))
        self.assertLess(p.index("player->SaveToDB(false, false);"),
                        p.rindex("return PurchaseResult::Success;"))

    def test_in_memory_validation_rollback_not_a_db_commit_ack(self):
        p = self.purchase
        self.assertIn("if (!opened)", p)
        self.assertIn("SetPaidExpansionFlag(player, index, FlagNone);", p)
        self.assertIn("player->ModifyMoney(static_cast<int32>(costCopper));", p)
        self.assertLess(p.index("if (!opened)"),
                        p.index("player->SaveToDB(false, false);"))
        # No future or transaction result from Player::SaveToDB is inspected
        # by this routine; no claim that a DB failure has happened.
        for disallowed in (
            "AsyncCommitTransaction(",
            "TransactionCallback",
            "AfterComplete(",
            "DirectCommitTransaction(",
            "QueueSize(",
        ):
            self.assertNotIn(disallowed, p)

    def test_actual_core_save_is_void_and_enqueues_transaction(self):
        self.assertIn("void SaveToDB(bool create, bool logout);", self.coreh)
        body = between(
            self.storage, "void Player::SaveToDB(bool create, bool logout)",
            "void Player::SaveToDB(CharacterDatabaseTransaction trans, bool create, bool logout)")
        self.assertIn("CharacterDatabase.BeginTransaction()", body)
        self.assertIn("SaveToDB(trans, create, logout);", body)
        self.assertIn("CharacterDatabase.CommitTransaction(trans);", body)
        self.assertNotIn("AsyncCommitTransaction(", body)
        self.assertIn("void DatabaseWorkerPool<T>::CommitTransaction(", self.pool)
        self.assertIn("Enqueue(new TransactionTask(transaction));", self.pool)
        self.assertIn("TransactionCallback DatabaseWorkerPool<T>::AsyncCommitTransaction(",
                      self.pool)
        self.assertIn("return TransactionCallback(std::move(result));", self.pool)
        self.assertLess(self.worker.index("_queue->WaitAndPop(operation);"),
                        self.worker.index("operation->call();"))
        self.assertIn("return _queue->Size();", self.pool)

    def test_success_message_is_not_proof_of_committed_data(self):
        # This is a NEGATIVE source test, not evidence of a lost payment:
        # the linked vendor has no per-transaction outcome at the time
        # it reports success to the connected client.
        self.assertIn("return PurchaseResult::Success;", self.purchase)
        self.assertIn('"Expansion access purchased successfully."', self.vendor_paid)
        self.assertIn("player->SaveToDB(false, false);", self.purchase)
        self.assertNotIn("AfterComplete(", self.vendor_paid)
        self.assertNotIn("AfterComplete(", self.purchase)
        self.assertNotIn("TransactionCallback", self.vendor_paid)
        self.assertNotIn("TransactionCallback", self.purchase)

    def test_paid_rule_and_strict_existing_row_blockers_remain(self):
        self.assertIn("if (_paidExpansionLedgers.find(player->GetGUID().GetCounter()) == "
                      "_paidExpansionLedgers.end())", self.ipcpp)
        self.assertIn("return PurchaseResult::EntryUnavailable;", self.ipcpp)
        self.assertIn("if (disableDefaultProgression)", self.ipcpp)
        self.assertIn("player->GetQuestStatus(INTO_THE_BREACH) == QUEST_STATUS_REWARDED",
                      self.ipcpp)
        self.assertIn("constexpr std::uint8_t PurchaseGrantStage(Era)", self.ippolicy)
        self.assertIn("return 0;", between(
            self.ippolicy, "constexpr std::uint8_t PurchaseGrantStage(Era)",
            "constexpr PurchaseResult CheckPurchase("))
        self.assertIn("VanillaFinalStage = 7", self.ippolicy)
        self.assertIn("TbcEntryStage = 8", self.ippolicy)
        self.assertIn("TbcFinalStage = 13", self.ippolicy)
        self.assertIn("WrathFirstCompletionStage = 14", self.ippolicy)

    def test_both_gates_default_off(self):
        self.assertIn("IndividualProgression.PaidExpansion.Enable = 0", self.ipdist)
        self.assertIn("CharacterServices.ExpansionUnlock.Enable = 0", self.csdist)
        self.assertIn("bool IndividualProgression::IsPaidExpansionActive() const", self.ipcpp)
        self.assertIn('sConfigMgr->GetOption<bool>("CharacterServices.ExpansionUnlock.Enable", false)',
                      self.vendor)


if __name__ == "__main__":
    unittest.main()

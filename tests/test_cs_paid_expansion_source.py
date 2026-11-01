"""Source-only regression contracts for the DRAFT paid-expansion vendor.

These checks never connect to a live World/Auth server, change character
gold or claim that C++ compiles. Real C++/gossip/DB gameplay tests are required.
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CPP = (ROOT / "src" / "CharacterServices.cpp").read_text(encoding="utf-8")
DIST = (ROOT / "conf" / "character_services.conf.dist").read_text(encoding="utf-8")
LEGACY_CPP = (ROOT / "docs" / "source-snapshots" / "CharacterServices-owner-20261101.cpp").read_text(encoding="utf-8")
LEGACY_CONF = (ROOT / "docs" / "source-snapshots" / "character_services-owner-20261101.conf.dist").read_text(encoding="utf-8")


class PaidExpansionSourceContracts(unittest.TestCase):
    def test_default_off_and_price_anchors(self):
        self.assertIn("CharacterServices.ExpansionUnlock.Enable = 0", DIST)
        self.assertIn("CharacterServices.ExpansionUnlock.Cost.VanillaToTBC = 1000", DIST)
        self.assertIn("CharacterServices.ExpansionUnlock.Cost.TBCToWotLK = 3000", DIST)
        self.assertIn('"CharacterServices.ExpansionUnlock.Enable", false', CPP)

    def test_gate_requires_ip_entitlement(self):
        self.assertGreaterEqual(CPP.count("sIndividualProgression->IsPaidExpansionActive()"), 4)
        self.assertIn("sIndividualProgression->CanPurchaseExpansion(", CPP)
        self.assertIn("sIndividualProgression->PurchaseExpansion(", CPP)

    def test_both_era_actions_are_handled_before_generic_tier(self):
        self.assertIn("action == 200 || action == 201", CPP)
        self.assertIn("action == 200 ? ExpansionEra::Tbc : ExpansionEra::Wrath", CPP)
        self.assertLess(CPP.index("if (action == 200 || action == 201)"),
                        CPP.index("if (action >= 100)"))

    def test_vendor_does_not_award_stage14_or_charge_separately(self):
        handler = CPP[CPP.index("if (action == 200 || action == 201)"):
                      CPP.index("// Handle progression tier purchases (action IDs 100+)")]
        self.assertIn("PurchaseExpansion(", handler)
        self.assertNotIn("ModifyMoney(", handler)
        self.assertNotIn("ForceUpdateProgressionState(", handler)

    def test_expansion_gossip_price_does_not_charge_at_core_layer(self):
        block = CPP[CPP.index("// The owner must BOTH complete"):
                    CPP.index("// Add progression tier purchase option if enabled")]
        # The gossip item displays the price text but reports zero money to
        # the core: IP PurchaseExpansion is the sole charging authority.
        self.assertIn("std::to_string(copper / 10000)", block)
        self.assertEqual(block.count("0u, false);"), 2)

    def test_generic_tiers_guarded_before_debit(self):
        menu = CPP[CPP.index("// Add progression tier purchase option if enabled"):
                   CPP.index("SendGossipMenuFor(")]
        self.assertIn("GetMaxServiceGrantableStage(player)", menu)
        validate = CPP[CPP.index("bool CanPurchaseProgressionTier("):
                       CPP.index("bool ApplyProgressionTierPurchase(")]
        self.assertIn("GetMaxServiceGrantableStage(player)", validate)
        self.assertIn("newTier > sIndividualProgression->GetMaxServiceGrantableStage(player)", validate)
        selection = CPP[CPP.index("// Handle progression tier purchases (action IDs 100+)"):
                        CPP.index("// Handle standard services (action IDs 1-4).")]
        self.assertLess(selection.index("CanPurchaseProgressionTier("),
                        selection.index("ModifyMoney("))

    def test_price_conversion_is_bounded_and_not_dynamic(self):
        method = CPP[CPP.index("static bool GetExpansionCostCopper("):
                     CPP.index("bool OnGossipHello(")]
        self.assertIn("CharacterServicesMoneyPolicy::TryGoldToCopper(gold, false, copper)", method)
        self.assertNotIn("DynamicCost", method)
        price = CPP[CPP.index("bool TryGetProgressionTierCost("):
                    CPP.index("uint32 GetServiceCost(")]
        self.assertIn("CharacterServicesMoneyPolicy::TryGoldToCopper(gold, true, copper)", price)
        self.assertIn('#include "CharacterServicesMoneyPolicy.h"', CPP)

    def test_generic_menu_has_no_second_gossip_debit(self):
        block = CPP[CPP.index("// Add progression tier purchase option if enabled"):
                    CPP.index("SendGossipMenuFor(")]
        self.assertIn("std::to_string(tierCostCopper / 10000)", block)
        self.assertIn("0u, false);", block)
        self.assertIn("TryGetProgressionTierCost(nextTier, tierCostCopper)", block)

    def test_generic_fee_overflow_and_preflight_are_fail_closed(self):
        handler = CPP[CPP.index("// Handle progression tier purchases (action IDs 100+)"):
                      CPP.index("// Handle standard services (action IDs 1-4).")]
        self.assertIn("TryGetProgressionTierCost(tierToPurchase, cost)", handler)
        self.assertIn("action < 101 || action > 118", handler)
        self.assertIn("ModifyMoney(-static_cast<int32>(cost))", handler)
        self.assertLess(handler.index("CanPurchaseProgressionTier("), handler.index("ModifyMoney("))
        self.assertLess(handler.index("TryGetProgressionTierCost("), handler.index("ModifyMoney("))
        self.assertIn("if (!granted)", handler)
        self.assertIn("ModifyMoney(static_cast<int32>(cost))", handler)
        validator = CPP[CPP.index("bool CanPurchaseProgressionTier("):
                        CPP.index("bool ApplyProgressionTierPurchase(")]
        self.assertIn("for (uint8 stage = currentTier + 1; stage <= newTier; ++stage)", validator)
        self.assertIn("if (stage == 11)", validator)
        self.assertIn("GetQuestStatus(66000u + stage) != QUEST_STATUS_REWARDED", validator)
        self.assertIn("sObjectMgr->GetQuestTemplate(66000u + stage)", validator)
        self.assertIn("progressionLimit", validator)
        grant = CPP[CPP.index("bool ApplyProgressionTierPurchase("):
                    CPP.index("std::string GetTierIcon(")]
        self.assertIn("UpdateProgressionState(", grant)
        self.assertNotIn("ForceUpdateProgressionState(", grant)
        self.assertIn("QUEST_STATUS_REWARDED", grant)

    def test_forged_sender_disabled_service_and_repeat_failure(self):
        handler = CPP[CPP.index("bool OnGossipSelect("):
                      CPP.index("bool IsStandardServiceEnabled(")]
        self.assertIn("sender != GOSSIP_SENDER_MAIN", handler)
        self.assertIn('"CharacterServices.Enable", false', handler)
        self.assertIn('"CharacterServices.ExpansionUnlock.Enable", false', handler)
        self.assertIn("ExpansionResult::AlreadyOwned", handler)
        self.assertIn("ExpansionResult::InsufficientFunds", handler)

    def test_standard_upstream_safety_not_removed(self):
        self.assertIn("bool IsStandardServiceEnabled(", CPP)
        self.assertIn("bool CanPurchaseProgressionTier(", CPP)
        self.assertIn("bool ApplyProgressionTierPurchase(", CPP)
        self.assertIn("if (!IsStandardServiceEnabled(action))", CPP)
        self.assertIn("GetNextProgressionTier(currentTier)", CPP)
        self.assertIn("bool TryGetProgressionTierCost(", CPP)

    def test_legacy_owner_files_remain_separate_and_unmodified_in_intent(self):
        self.assertIn("ForceUpdateProgressionState(player, static_cast<ProgressionState>(newTier))", LEGACY_CPP)
        self.assertIn("CharacterServices.ExpansionUnlock.Enable = 1", LEGACY_CONF)
        self.assertNotEqual(CPP, LEGACY_CPP)
        self.assertNotEqual(DIST, LEGACY_CONF)


if __name__ == "__main__":
    unittest.main()

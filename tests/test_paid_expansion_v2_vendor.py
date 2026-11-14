import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "src" / "CharacterServices.cpp").read_text(encoding="utf-8")
CONF = (ROOT / "conf" / "character_services.conf.dist").read_text(encoding="utf-8")


class PaidExpansionV2VendorSourceContract(unittest.TestCase):
    def test_requires_api_v2(self):
        self.assertIn("COSMIC_IP_PAID_EXPANSION_API_VERSION >= 2", SRC)

    def test_submitted_is_not_called_success(self):
        self.assertIn("ExpansionResult::Submitted", SRC)
        self.assertIn("awaiting confirmation", SRC)
        self.assertNotIn("Expansion access purchased successfully", SRC)

    def test_active_is_the_only_owned_view(self):
        self.assertIn("ExpansionView::Active", SRC)
        self.assertIn("ExpansionView::Pending", SRC)
        self.assertIn("ExpansionView::Unconfirmed", SRC)

    def test_pending_duplicate_is_blocked(self):
        self.assertIn("ExpansionResult::PurchasePending", SRC)
        self.assertIn("No additional gold was charged", SRC)

    def test_character_services_does_not_refresh_phasing_early(self):
        vendor_region = SRC[SRC.index("if (action == 200 || action == 201)") :
                            SRC.index("// Handle progression tier purchases")]
        self.assertNotIn("checkIPPhasing", vendor_region)

    def test_expansion_actions_are_handled_before_generic_tier_actions(self):
        self.assertLess(
            SRC.index("if (action == 200 || action == 201)"),
            SRC.index("// Handle progression tier purchases"),
        )

    def test_generic_action_range_cannot_alias_200_or_201(self):
        self.assertIn("if (action < 101 || action > 118)", SRC)

    def test_sender_is_revalidated(self):
        self.assertIn("sender != GOSSIP_SENDER_MAIN", SRC)

    def test_default_off_and_prices_present(self):
        self.assertIn("CharacterServices.ExpansionUnlock.Enable = 0", CONF)
        self.assertIn("CharacterServices.ExpansionUnlock.Cost.VanillaToTBC = 1000", CONF)
        self.assertIn("CharacterServices.ExpansionUnlock.Cost.TBCToWotLK = 3000", CONF)


if __name__ == "__main__":
    unittest.main()

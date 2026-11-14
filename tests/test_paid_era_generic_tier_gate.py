import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "src" / "CharacterServices.cpp").read_text(encoding="utf-8")
CONF = (ROOT / "conf" / "character_services.conf.dist").read_text(encoding="utf-8")


class PaidEraGenericTierGateSourceContract(unittest.TestCase):
    def test_api_gate_is_forward_compatible(self):
        self.assertIn("COSMIC_IP_PAID_EXPANSION_API_VERSION >= 1", SRC)

    def test_account_ceiling_uses_paid_aware_api(self):
        self.assertIn("GetAccountEffectiveProgression(accountId)", SRC)

    def test_menu_and_select_both_call_gate(self):
        self.assertGreaterEqual(SRC.count("CanOfferProgressionTier("), 3)

    def test_gate_uses_character_specific_service_ceiling(self):
        self.assertIn("GetMaxServiceGrantableStage(player)", SRC)

    def test_paid_gate_default_is_off(self):
        self.assertIn("CharacterServices.ExpansionUnlock.Enable = 0", CONF)

    def test_bypass_message_points_to_vezrath(self):
        self.assertIn("purchase the next expansion from Chronomancer Vezrath", SRC)


if __name__ == "__main__":
    unittest.main()

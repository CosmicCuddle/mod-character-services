// Executable flag-mismatch contract (no Core, DB, player or paid gold).
#include "../src/CharacterServicesGatePolicy.h"
#include <cassert>
#include <cstdint>

using CharacterServicesGatePolicy::CanOfferGenericTier;

int main()
{
    // Both OFF: retain the legacy generic tier offer, subject to other checks.
    for (std::uint8_t tier : {std::uint8_t{1}, std::uint8_t{7}, std::uint8_t{8},
                               std::uint8_t{13}, std::uint8_t{14}, std::uint8_t{18}})
    {
        assert(CanOfferGenericTier(false, false, tier, 0));
        // Vendor ON with missing/inactive IP: no generic bypass at any tier.
        assert(!CanOfferGenericTier(true, false, tier, 18));
    }

    // IP active: effective cap binds menu AND purchase validation, regardless
    // of vendor menu flag; stage 13 does not imply paid Wrath if cap is 12.
    for (bool vendorOn : {false, true})
    {
        assert(CanOfferGenericTier(vendorOn, true, 7, 7));
        assert(!CanOfferGenericTier(vendorOn, true, 8, 7));
        assert(CanOfferGenericTier(vendorOn, true, 12, 12));
        assert(!CanOfferGenericTier(vendorOn, true, 13, 12));
        assert(!CanOfferGenericTier(vendorOn, true, 14, 12));
        assert(CanOfferGenericTier(vendorOn, true, 18, 18));
    }
    return 0;
}

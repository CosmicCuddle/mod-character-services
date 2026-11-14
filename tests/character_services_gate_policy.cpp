#include "../src/CharacterServicesGatePolicy.h"

#include <cassert>
#include <cstdint>

int main()
{
    using CharacterServicesGatePolicy::CanOfferGenericTier;

    // Historical behavior: with paid passage completely inactive, the gate
    // must not change the generic tier service.
    assert(CanOfferGenericTier(false, false, 8, 0));
    assert(CanOfferGenericTier(false, false, 14, 0));

    // If the operator requests paid passage but IP cannot enforce it, fail
    // closed rather than silently falling back to generic tier purchases.
    assert(!CanOfferGenericTier(true, false, 8, 18));
    assert(!CanOfferGenericTier(true, false, 14, 18));

    // Once paid IP is active, the character-specific service ceiling is
    // authoritative for every generic tier purchase.
    assert(CanOfferGenericTier(false, true, 7, 7));
    assert(!CanOfferGenericTier(false, true, 8, 7));
    assert(CanOfferGenericTier(true, true, 12, 12));
    assert(!CanOfferGenericTier(true, true, 13, 12));

    return 0;
}

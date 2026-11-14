/*
 * CosmicCuddle Character Services — paid-era generic tier gate.
 *
 * Pure policy only: never charge, grant, or mutate a player.
 */
#ifndef COSMIC_CHARACTER_SERVICES_GATE_POLICY_H
#define COSMIC_CHARACTER_SERVICES_GATE_POLICY_H

#include <cstdint>

namespace CharacterServicesGatePolicy
{
    constexpr bool CanOfferGenericTier(bool vendorPaidRequested, bool ipPaidActive,
                                       std::uint8_t nextTier, std::uint8_t maxGrantableTier)
    {
        // A configured paid vendor must never silently fall back to the legacy
        // generic tier shop when the IP paid feature is unavailable.
        if (vendorPaidRequested && !ipPaidActive)
            return false;

        // With paid IP active, never let generic tier purchases cross the
        // character's current paid-era service ceiling.
        return !ipPaidActive || nextTier <= maxGrantableTier;
    }
}

#endif

/*
 * CosmicCuddle Character Services — default-OFF, dependency-safe generic
 * progression tier access when the vendor and IP paid-era flags disagree.
 * This pure function cannot grant a stage, charge money or modify players.
 */
#ifndef COSMIC_CHARACTER_SERVICES_GATE_POLICY_H
#define COSMIC_CHARACTER_SERVICES_GATE_POLICY_H

#include <cstdint>

namespace CharacterServicesGatePolicy
{
    constexpr bool CanOfferGenericTier(bool vendorPaidRequested, bool ipPaidActive,
                                       std::uint8_t nextTier, std::uint8_t maxGrantableTier)
    {
        // A configured paid vendor must NOT fall back to free generic tiers
        // when the required IP entitlement feature is not active.
        if (vendorPaidRequested && !ipPaidActive)
            return false;

        // Both flags OFF retains the historical generic service. When IP is
        // active, its effective paid-era ceiling always applies, regardless
        // of the vendor's separate menu switch.
        return !ipPaidActive || nextTier <= maxGrantableTier;
    }
}

#endif

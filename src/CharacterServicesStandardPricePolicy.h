/*
 * CosmicCuddle Character Services — signed-safe legacy service fees.
 * Keep valid historical standard-service prices and dynamic truncation
 * unchanged; reject misconfiguration that could overflow a signed debit.
 */
#ifndef COSMIC_CHARACTER_SERVICES_STANDARD_PRICE_POLICY_H
#define COSMIC_CHARACTER_SERVICES_STANDARD_PRICE_POLICY_H

#include "CharacterServicesMoneyPolicy.h"
#include <cstdint>
#include <limits>

namespace CharacterServicesStandardPricePolicy
{
    constexpr std::uint32_t LegacyMaxLevel = 80u;

    inline bool TryCost(std::uint32_t gold, std::uint32_t playerLevel,
                        bool dynamicCostEnabled, std::uint32_t& copper)
    {
        std::uint32_t baseCopper = 0;
        // A 0-gold standard service remains an intentional valid free service.
        if (!CharacterServicesMoneyPolicy::TryGoldToCopper(gold, true, baseCopper))
            return false;

        if (!dynamicCostEnabled)
        {
            copper = baseCopper;
            return true;
        }

        // Preserve the historic double ratio + truncation for valid prices.
        // Do not narrow a price above int32 before Player::ModifyMoney(int32).
        double const ratio = static_cast<double>(playerLevel) / LegacyMaxLevel;
        double const calculated = ratio * static_cast<double>(baseCopper);
        if (calculated > static_cast<double>(std::numeric_limits<std::int32_t>::max()))
            return false;

        copper = static_cast<std::uint32_t>(calculated);
        return true;
    }
}

#endif

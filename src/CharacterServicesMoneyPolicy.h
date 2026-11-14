/*
 * CosmicCuddle Character Services — side-effect-free gold-to-copper conversion.
 */
#ifndef COSMIC_CHARACTER_SERVICES_MONEY_POLICY_H
#define COSMIC_CHARACTER_SERVICES_MONEY_POLICY_H

#include <cstdint>
#include <limits>

namespace CharacterServicesMoneyPolicy
{
    constexpr std::uint32_t CopperPerGold = 10000u;
    constexpr std::uint32_t MaxGoldForSignedMoney =
        static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max()) / CopperPerGold;

    constexpr bool TryGoldToCopper(std::uint32_t gold, bool allowZero, std::uint32_t& copper)
    {
        if ((!allowZero && !gold) || gold > MaxGoldForSignedMoney)
            return false;
        copper = gold * CopperPerGold;
        return true;
    }
}

#endif

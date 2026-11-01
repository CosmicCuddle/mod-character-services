// Portable regression for existing character service prices. No Player/DB needed.
#include "../src/CharacterServicesStandardPricePolicy.h"
#include <cassert>
#include <cstdint>
#include <initializer_list>
#include <limits>

using CharacterServicesStandardPricePolicy::TryCost;
using CharacterServicesMoneyPolicy::MaxGoldForSignedMoney;

int main()
{
    std::uint32_t charge = 0;
    assert(TryCost(25, 80, false, charge) && charge == 250000u);
    assert(TryCost(50, 60, false, charge) && charge == 500000u);
    assert(TryCost(100, 80, false, charge) && charge == 1000000u);
    assert(TryCost(250, 80, false, charge) && charge == 2500000u);

    // Historic double-ratio/truncation is retained for valid prices.
    for (std::uint32_t gold : {0u, 1u, 25u, 50u, 100u, 250u, 1000u, 10000u})
        for (std::uint32_t level : {0u, 1u, 20u, 59u, 60u, 70u, 80u})
        {
            assert(TryCost(gold, level, true, charge));
            std::uint32_t const oldPrice = gold * 10000u;
            std::uint32_t const oldDynamic =
                static_cast<std::uint32_t>((static_cast<double>(level) / 80.0) * oldPrice);
            assert(charge == oldDynamic);
        }

    // Free configured services stay free, including under dynamic scaling.
    assert(TryCost(0, 80, false, charge) && charge == 0);
    assert(TryCost(0, 80, true, charge) && charge == 0);

    // Old uint32 gold multiplication would wrap (429497g -> 2704 copper).
    charge = 123u;
    assert(!TryCost(429497u, 80, false, charge) && charge == 123u);
    assert(!TryCost(MaxGoldForSignedMoney + 1u, 1, true, charge) && charge == 123u);
    assert(TryCost(MaxGoldForSignedMoney, 80, true, charge)
           && charge <= static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max()));
    // Dynamic ratio above level 80 must not yield an out-of-range signed debit.
    charge = 123u;
    assert(!TryCost(MaxGoldForSignedMoney, 81, true, charge) && charge == 123u);

    // The actual signed debit remains representable for all accepted fees.
    for (std::uint32_t gold : {0u, 25u, 100u, 1000u, MaxGoldForSignedMoney})
        for (std::uint32_t level : {0u, 1u, 60u, 80u, 81u, 255u})
            for (bool dynamic : {false, true})
                if (TryCost(gold, level, dynamic, charge))
                    assert(charge <= static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max()));
}

#include "../src/CharacterServicesMoneyPolicy.h"

#include <cassert>
#include <cstdint>

int main()
{
    using CharacterServicesMoneyPolicy::TryGoldToCopper;

    std::uint32_t copper = 0;

    assert(!TryGoldToCopper(0, false, copper));
    assert(TryGoldToCopper(1, false, copper) && copper == 10000u);
    assert(TryGoldToCopper(1000, false, copper) && copper == 10000000u);
    assert(TryGoldToCopper(3000, false, copper) && copper == 30000000u);

    std::uint32_t const tooLarge =
        CharacterServicesMoneyPolicy::MaxGoldForSignedMoney + 1u;
    assert(!TryGoldToCopper(tooLarge, false, copper));

    return 0;
}

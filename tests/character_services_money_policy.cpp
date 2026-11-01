// Executable C++ contract: no AzerothCore dependencies or live gold.
#include "../src/CharacterServicesMoneyPolicy.h"
#include <cassert>
#include <cstdint>
#include <limits>

using namespace CharacterServicesMoneyPolicy;

int main()
{
    std::uint32_t result = 37;
    assert(TryGoldToCopper(1000, false, result) && result == 10000000u);
    assert(TryGoldToCopper(3000, false, result) && result == 30000000u);
    assert(TryGoldToCopper(150, true, result) && result == 1500000u);
    assert(TryGoldToCopper(0, true, result) && result == 0u);
    result = 37;
    assert(!TryGoldToCopper(0, false, result) && result == 37u);
    assert(TryGoldToCopper(MaxGoldForSignedMoney, false, result));
    assert(result <= static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max()));
    result = 37;
    assert(!TryGoldToCopper(MaxGoldForSignedMoney + 1u, false, result) && result == 37u);
    assert(!TryGoldToCopper(429497u, true, result) && result == 37u);
    assert(!TryGoldToCopper(std::numeric_limits<std::uint32_t>::max(), true, result) && result == 37u);
    static_assert(MaxGoldForSignedMoney == 214748u, "signed 32-bit gold cap changed");
    return 0;
}

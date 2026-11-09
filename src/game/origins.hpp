#pragma once

#include "game/state.hpp"

#include <optional>
#include <span>
#include <string_view>

namespace opense4::game::origins {

struct OriginModifier {
    Characteristic characteristic;
    int amount = 0; // percentage points added to the race's characteristic
};

struct StartingOriginInfo {
    StartingOrigin id = StartingOrigin::None;
    std::string_view name;
    std::string_view description;
    std::array<OriginModifier, 3> modifiers{};
    Resources startingResources;
    int64_t startingResearch = 0;
    int extraStartingPlanets = 0;
    int extraAttackShips = 0;
    int extraWarehouses = 0;
};

std::span<const StartingOriginInfo> all();
const StartingOriginInfo& info(StartingOrigin origin);
std::optional<StartingOrigin> fromName(std::string_view name);
void applyToRace(Race& race, StartingOrigin origin);
void removeFromRace(Race& race, StartingOrigin origin);

} // namespace opense4::game::origins

#pragma once

// VOIDREIGN government rules. The empire-type field already belongs to the
// native save/setup model, so these profiles survive save/load without a
// parallel custom state system.
#include <array>
#include <string_view>

namespace opense4::game {

struct GovernmentProfile {
    std::string_view name;
    int resourceProductionPercent = 0;
    int researchPercent = 0;
    int intelligencePercent = 0;
    int tradePercent = 0;
    int maintenancePercent = 0;
    std::string_view description;
};

inline constexpr std::array<GovernmentProfile, 8> kGovernmentProfiles{{
    {"Democratic Republic", -2, 8, 4, 10, 0,
     "Balanced civic institutions favour research, diplomatic trade and broad-based stability."},
    {"Merchant Republic", 2, 0, 0, 20, -5,
     "Commercial networks increase trade income and reduce the cost of maintaining fleets."},
    {"Technocracy", -4, 20, 12, -5, 3,
     "Scientific institutions accelerate research and intelligence at the expense of industry and trade."},
    {"Industrial Directorate", 15, -5, -3, -8, 4,
     "Central planning maximises resource output but diverts resources from science and commerce."},
    {"Military Junta", 6, -8, 0, -10, 12,
     "A militarised state strengthens industrial mobilisation while maintaining a costly standing fleet."},
    {"Collective", 8, 2, -4, -8, 0,
     "Shared industrial organisation improves output, with weaker intelligence and trade networks."},
    {"Imperial Autocracy", 5, 5, -2, -8, 5,
     "Centralised rule supports production and research while imposing higher fleet upkeep."},
    {"Frontier Compact", 6, 5, 3, 5, -2,
     "Decentralised frontier institutions balance growth, research, trade and economical fleets."},
}};

inline constexpr GovernmentProfile governmentProfile(std::string_view name) {
    for (const GovernmentProfile& profile : kGovernmentProfiles)
        if (profile.name == name) return profile;
    return {};
}

} // namespace opense4::game

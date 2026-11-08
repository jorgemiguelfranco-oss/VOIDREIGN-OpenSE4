#pragma once

#include "game/state.hpp"

#include <optional>
#include <string>
#include <string_view>

namespace opense4::game {

class Rules;

namespace leaders {

inline constexpr size_t kMaximumActiveLeaders = 8;
inline constexpr uint32_t kRecruitMinerals = 650;
inline constexpr uint32_t kRecruitOrganics = 300;
inline constexpr uint32_t kRecruitRadioactives = 200;

std::string_view displayName(LeaderRole role);
std::string_view displayName(LeaderRarity rarity);
std::string_view displayName(LeaderTrait trait);
std::string_view description(LeaderTrait trait);
uint32_t experienceForNextLevel(uint8_t level);

// Creates the initial leadership corps for a newly founded empire, including
// a homeworld governor, an admiral and an empire-wide scientist.
void seedInitial(GameState& state, EmpireId empire);

// Makes a recruit from the empire's culture-specific name pool. Rarity and
// class-appropriate traits are rolled from the game's deterministic RNG.
Leader generateRecruit(GameState& state, EmpireId empire, LeaderRole role);

// Validate a requested assignment. Empty means valid.
std::string assignmentProblem(const GameState& state, EmpireId empire, const Leader& leader,
                               ObjectId planet, FleetId fleet);

// Assignments and personnel costs.
Resources upkeep(const Empire& empire);
int governorResourceBonusPct(const Empire& empire, ObjectId planet);
int governorResearchBonusPct(const Empire& empire, ObjectId planet);
int governorPopulationGrowthBonusPct(const Empire& empire, ObjectId planet);
int scientistResearchBonusPct(const Empire& empire);
int admiralCombatBonusPct(const GameState& state, EmpireId empire, FleetId fleet);
int generalGroundDefenseBonusPct(const Empire& empire, ObjectId colony);

// Award role XP, level-ups, birthdays, natural deaths and assignment cleanup.
// Called once during each living empire's end-of-turn processing.
void advanceTurn(GameState& state, EmpireId empire);

} // namespace leaders
} // namespace opense4::game

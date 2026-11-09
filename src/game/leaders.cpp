#include "game/leaders.hpp"

#include "game/rules.hpp"

#include <algorithm>
#include <array>
#include <format>
#include <string>
#include <string_view>

namespace opense4::game::leaders {

namespace {

struct NamePool {
    std::string_view style;
    std::array<std::string_view, 8> first;
    std::array<std::string_view, 8> last;
};

constexpr std::array<NamePool, 6> kNames{{
    {"Aurelian",
     {"Sael", "Ilyra", "Taren", "Vaelis", "Orin", "Sereth", "Avara", "Nerys"},
     {"Orinth", "Voss", "Sol", "Caelis", "Merrow", "Thane", "Aster", "Quill"}},
    {"Veyran",
     {"Neris", "Thessa", "Kael", "Mira", "Soryn", "Vela", "Darian", "Oss"},
     {"Tideborn", "Voss", "Calder", "Nacre", "Rill", "Sable", "Morrow", "Vey"}},
    {"Khepri",
     {"Khetek", "Ssar", "Vek", "Tzara", "Korr", "Akh", "Rhex", "Zhek"},
     {"Ironshell", "Ashkar", "Vorr", "Khet", "Draz", "Onyx", "Seth", "Khal"}},
    {"Meridian",
     {"Axiom", "Liora", "Eidren", "Syla", "Vey", "Oriel", "Nym", "Cael"},
     {"Prism", "Vitre", "Lattice", "Solenne", "Echelon", "Irides", "Cairn", "Vesper"}},
    {"Outer",
     {"Mara", "Jace", "Sera", "Rook", "Anya", "Tomas", "Kestrel", "Niko"},
     {"Farline", "Hale", "Kade", "Cross", "Drift", "Venn", "Morrow", "Reeve"}},
    {"Helion",
     {"Cassian", "Lyra", "Darius", "Aurelia", "Severin", "Helena", "Lucan", "Mira"},
     {"Solari", "Voss", "Caesar", "Vale", "Meridian", "Dawn", "Ardent", "Valis"}}
}};

std::string_view styleOf(const Empire& empire) { return empire.race.style; }

const NamePool& poolFor(const Empire& empire) {
    for (const NamePool& pool : kNames)
        if (styleOf(empire) == pool.style) return pool;
    return kNames[0];
}

std::string roleEpithet(LeaderRole role) {
    switch (role) {
        case LeaderRole::Governor: return "Planetary Governor";
        case LeaderRole::Admiral: return "Fleet Admiral";
        case LeaderRole::Scientist: return "Chief Scientist";
        case LeaderRole::General: return "Ground Commander";
        case LeaderRole::Ruler: return "Sovereign";
        case LeaderRole::Count: break;
    }
    return "Leader";
}

LeaderTrait firstTrait(LeaderRole role, uint32_t choice) {
    switch (role) {
        case LeaderRole::Governor: {
            constexpr std::array t{LeaderTrait::Industrialist, LeaderTrait::Bureaucrat, LeaderTrait::Agrarian,
                                   LeaderTrait::Inspirational, LeaderTrait::Logistician};
            return t[choice % t.size()];
        }
        case LeaderRole::Admiral: {
            constexpr std::array t{LeaderTrait::Tactician, LeaderTrait::Aggressive, LeaderTrait::Defender,
                                   LeaderTrait::Logistician, LeaderTrait::Explorer};
            return t[choice % t.size()];
        }
        case LeaderRole::Scientist: {
            constexpr std::array t{LeaderTrait::Genius, LeaderTrait::Visionary, LeaderTrait::Explorer,
                                   LeaderTrait::Bureaucrat, LeaderTrait::Industrialist};
            return t[choice % t.size()];
        }
        case LeaderRole::General: {
            constexpr std::array t{LeaderTrait::Tactician, LeaderTrait::Aggressive, LeaderTrait::Defender,
                                   LeaderTrait::Inspirational};
            return t[choice % t.size()];
        }
        case LeaderRole::Ruler: {
            constexpr std::array t{LeaderTrait::Inspirational, LeaderTrait::Visionary, LeaderTrait::Bureaucrat,
                                   LeaderTrait::Genius};
            return t[choice % t.size()];
        }
        case LeaderRole::Count: break;
    }
    return LeaderTrait::Inspirational;
}

uint16_t naturalLifeExpectancy(const Empire& empire) {
    const std::string_view style = styleOf(empire);
    if (style == "Meridian") return 145;
    if (style == "Aurelian") return 112;
    if (style == "Helion") return 105;
    if (style == "Veyran") return 96;
    if (style == "Khepri") return 88;
    if (style == "Outer") return 84;
    return 95;
}


const Leader* assignedToPlanet(const Empire& empire, ObjectId planet) {
    for (const Leader& leader : empire.leaders)
        if (leader.alive && leader.role == LeaderRole::Governor && leader.assignedColony == planet) return &leader;
    return nullptr;
}

const Leader* assignedScientist(const Empire& empire) {
    for (const Leader& leader : empire.leaders)
        if (leader.alive && leader.role == LeaderRole::Scientist) return &leader;
    return nullptr;
}

std::string recruitName(GameState& state, Empire& empire) {
    const NamePool& pool = poolFor(empire);
    // Try several deterministic candidates before adding a unique ordinal.
    for (int attempt = 0; attempt < 8; ++attempt) {
        const size_t a = state.rng.index(pool.first.size());
        const size_t b = state.rng.index(pool.last.size());
        const std::string candidate = std::format("{} {}", pool.first[a], pool.last[b]);
        const bool taken = std::any_of(empire.leaders.begin(), empire.leaders.end(),
                                       [&](const Leader& leader) { return leader.name == candidate; });
        if (!taken) return candidate;
    }
    return std::format("{} {} {}", pool.first[state.rng.index(pool.first.size())],
                       pool.last[state.rng.index(pool.last.size())], empire.nextLeaderId + 1);
}

void grantXp(GameState& state, EmpireId empireId, Empire& empire, Leader& leader, uint32_t amount) {
    leader.experience += amount;
    while (leader.level < 10 && leader.experience >= experienceForNextLevel(leader.level)) {
        leader.experience -= experienceForNextLevel(leader.level);
        ++leader.level;
        std::string milestone;
        if (leader.level == 3 && leader.secondaryTrait == LeaderTrait::None) {
            for (int attempt = 0; attempt < 8; ++attempt) {
                const LeaderTrait evolved = firstTrait(leader.role, static_cast<uint32_t>(state.rng.index(31)));
                if (evolved != leader.trait && evolved != LeaderTrait::Paragon) {
                    leader.secondaryTrait = evolved;
                    milestone = std::format(" New specialisation: {}.", displayName(evolved));
                    break;
                }
            }
        }
        if (leader.level == 5)
            leader.epithet = std::format("Senior {}", roleEpithet(leader.role));
        else if (leader.level == 8)
            leader.epithet = std::format("Legendary {}", roleEpithet(leader.role));
        else if (leader.level == 10)
            leader.epithet = std::format("Ascendant {}", roleEpithet(leader.role));
        addLog(state, empireId, LogCategory::Misc, "Leader promoted",
               std::format("{} has reached level {} as {}.{}", leader.name, leader.level,
                           displayName(leader.role), milestone));
    }
    if (leader.level >= 10) leader.experience = std::min<uint32_t>(leader.experience, 999);
    (void)empire;
}

void retire(GameState& state, EmpireId empireId, Leader& leader, std::string cause) {
    leader.alive = false;
    leader.deathTurn = state.turn;
    leader.deathCause = std::move(cause);
    leader.assignedColony = {};
    leader.assignedFleet = {};
    addLog(state, empireId, LogCategory::Misc, "Leader lost",
           std::format("{} ({}) has left the leadership corps: {}.", leader.name, displayName(leader.role), leader.deathCause));
}

} // namespace

std::string_view displayName(LeaderRole role) {
    switch (role) {
        case LeaderRole::Governor: return "Governor";
        case LeaderRole::Admiral: return "Admiral";
        case LeaderRole::Scientist: return "Scientist";
        case LeaderRole::General: return "General";
        case LeaderRole::Ruler: return "Ruler";
        case LeaderRole::Count: break;
    }
    return "Unknown";
}

std::string_view displayName(LeaderRarity rarity) {
    switch (rarity) {
        case LeaderRarity::Regular: return "Regular";
        case LeaderRarity::Veteran: return "Veteran";
        case LeaderRarity::Paragon: return "Paragon";
        case LeaderRarity::Count: break;
    }
    return "Unknown";
}

std::string_view displayName(LeaderTrait trait) {
    switch (trait) {
        case LeaderTrait::Industrialist: return "Industrialist";
        case LeaderTrait::Bureaucrat: return "Bureaucrat";
        case LeaderTrait::Agrarian: return "Agrarian";
        case LeaderTrait::Logistician: return "Logistician";
        case LeaderTrait::Tactician: return "Tactician";
        case LeaderTrait::Aggressive: return "Aggressive";
        case LeaderTrait::Defender: return "Defender";
        case LeaderTrait::Explorer: return "Explorer";
        case LeaderTrait::Genius: return "Genius";
        case LeaderTrait::Visionary: return "Visionary";
        case LeaderTrait::Inspirational: return "Inspirational";
        case LeaderTrait::Paragon: return "Paragon";
        case LeaderTrait::None: return "None";
        case LeaderTrait::Count: break;
    }
    return "Unknown";
}

std::string_view description(LeaderTrait trait) {
    switch (trait) {
        case LeaderTrait::Industrialist: return "Improves mineral, organic and radioactive output on the governed world.";
        case LeaderTrait::Bureaucrat: return "Improves research administration on the governed world.";
        case LeaderTrait::Agrarian: return "Improves population growth and colony stability.";
        case LeaderTrait::Logistician: return "Improves supply and logistics for the assigned command.";
        case LeaderTrait::Tactician: return "Improves the combat efficiency of an assigned fleet.";
        case LeaderTrait::Aggressive: return "Improves offensive fleet performance.";
        case LeaderTrait::Defender: return "Improves defensive fleet performance.";
        case LeaderTrait::Explorer: return "Improves exploration and long-range operations.";
        case LeaderTrait::Genius: return "Improves empire-wide research output.";
        case LeaderTrait::Visionary: return "Improves research and long-term development.";
        case LeaderTrait::Inspirational: return "Improves morale and loyalty.";
        case LeaderTrait::Paragon: return "A once-in-a-generation figure with a powerful all-round command bonus.";
        case LeaderTrait::None: return {};
        case LeaderTrait::Count: break;
    }
    return {};
}

uint32_t experienceForNextLevel(uint8_t level) { return static_cast<uint32_t>(std::max<int>(1, level)) * 100; }

void seedInitial(GameState& state, EmpireId id) {
    if (!id.valid() || id.index() >= state.empires.size()) return;
    Empire& empire = state.empire(id);
    if (!empire.leaders.empty()) return;

    const NamePool& pool = poolFor(empire);
    Leader sovereign;
    sovereign.id = empire.nextLeaderId++;
    sovereign.name = !empire.leaderName.empty() ? empire.leaderName : std::format("{} {}", pool.first[0], pool.last[0]);
    sovereign.epithet = !empire.leaderTitle.empty() ? empire.leaderTitle : roleEpithet(LeaderRole::Ruler);
    sovereign.role = LeaderRole::Ruler;
    sovereign.rarity = LeaderRarity::Regular;
    sovereign.trait = LeaderTrait::Inspirational;
    sovereign.age = static_cast<uint16_t>(38 + (id.index() * 7) % 14);
    sovereign.hiredTurn = state.turn;
    empire.leaders.push_back(std::move(sovereign));
    for (LeaderRole role : {LeaderRole::Governor, LeaderRole::Admiral, LeaderRole::Scientist}) {
        Leader leader;
        leader.id = empire.nextLeaderId++;
        leader.name = std::format("{} {}", pool.first[(id.index() * 3 + static_cast<size_t>(role)) % pool.first.size()],
                                  pool.last[(id.index() * 5 + static_cast<size_t>(role)) % pool.last.size()]);
        leader.epithet = roleEpithet(role);
        leader.role = role;
        leader.rarity = LeaderRarity::Regular;
        leader.trait = role == LeaderRole::Governor ? LeaderTrait::Industrialist
                       : role == LeaderRole::Admiral ? LeaderTrait::Tactician
                                                    : LeaderTrait::Genius;
        leader.level = 1;
        leader.age = static_cast<uint16_t>(32 + (id.index() * 7 + static_cast<size_t>(role) * 5) % 16);
        leader.hiredTurn = state.turn;
        if (role == LeaderRole::Governor) {
            for (const auto& colony : state.colonies)
                if (colony && colony->owner == id && colony->homeworld) {
                    leader.assignedColony = colony->planet;
                    break;
                }
        }
        empire.leaders.push_back(std::move(leader));
    }
}

Leader generateRecruit(GameState& state, EmpireId id, LeaderRole role) {
    Empire& empire = state.empire(id);
    Leader leader;
    leader.id = empire.nextLeaderId++;
    leader.name = recruitName(state, empire);
    leader.epithet = roleEpithet(role);
    leader.role = role;
    const int roll = state.rng.rangeInt(0, 99);
    if (roll < 4) {
        leader.rarity = LeaderRarity::Paragon;
        leader.level = 4;
    } else if (roll < 20) {
        leader.rarity = LeaderRarity::Veteran;
        leader.level = 2;
    } else {
        leader.rarity = LeaderRarity::Regular;
        leader.level = 1;
    }
    const LeaderTrait specialist = firstTrait(role, static_cast<uint32_t>(state.rng.index(19)));
    leader.trait = specialist;
    leader.age = static_cast<uint16_t>(25 + state.rng.rangeInt(0, 27));
    leader.hiredTurn = state.turn;
    if (leader.rarity == LeaderRarity::Paragon) {
        leader.secondaryTrait = specialist;
        leader.trait = LeaderTrait::Paragon;
        leader.epithet = std::format("{} Paragon", roleEpithet(role));
    }
    return leader;
}

std::string assignmentProblem(const GameState& state, EmpireId empireId, const Leader& leader, ObjectId planet, FleetId fleet) {
    if (!leader.alive) return "That leader is no longer available";
    if (planet.valid() && fleet.valid()) return "A leader can hold only one assignment";
    if (!planet.valid() && !fleet.valid()) return {};
    if (leader.role == LeaderRole::Governor) {
        const Colony* colony = planet.valid() ? state.colony(planet) : nullptr;
        if (!colony || colony->owner != empireId) return "A governor must be assigned to one of your colonies";
        if (fleet.valid()) return "Governors cannot command fleets";
    } else if (leader.role == LeaderRole::Admiral) {
        const Fleet* target = fleet.valid() ? state.fleet(fleet) : nullptr;
        if (!target || target->owner != empireId) return "An admiral must be assigned to one of your fleets";
        if (planet.valid()) return "Admirals cannot govern colonies";
    } else if (leader.role == LeaderRole::Scientist) {
        if (planet.valid() || fleet.valid()) return "Scientists work at the empire level";
    } else if (leader.role == LeaderRole::General) {
        if (planet.valid()) {
            const Colony* colony = state.colony(planet);
            if (!colony || colony->owner != empireId) return "A general must be assigned to one of your colonies or armies";
        } else if (fleet.valid()) {
            const Fleet* target = state.fleet(fleet);
            if (!target || target->owner != empireId) return "A general must be assigned to one of your fleets";
        }
    } else if (leader.role == LeaderRole::Ruler) {
        return "The Sovereign cannot hold a colony or fleet assignment";
    } else {
        return "Unknown leader role";
    }
    return {};
}

Resources upkeep(const Empire& empire) {
    Resources cost;
    for (const Leader& leader : empire.leaders) {
        if (!leader.alive) continue;
        const int64_t level = std::max<int>(1, leader.level);
        const int64_t rarity = leader.rarity == LeaderRarity::Paragon ? 3 : leader.rarity == LeaderRarity::Veteran ? 2 : 1;
        cost += Resources{5 + level * rarity, 2 + level, 1 + (level + rarity) / 2};
    }
    return cost;
}

namespace {
bool hasTrait(const Leader& leader, LeaderTrait trait) {
    return leader.trait == trait || leader.secondaryTrait == trait;
}
} // namespace

int governorResourceBonusPct(const Empire& empire, ObjectId planet) {
    const Leader* governor = assignedToPlanet(empire, planet);
    if (!governor) return 0;
    int pct = 0;
    if (hasTrait(*governor, LeaderTrait::Industrialist)) pct += 5;
    if (hasTrait(*governor, LeaderTrait::Logistician)) pct += 2;
    if (hasTrait(*governor, LeaderTrait::Paragon)) pct += 8;
    pct += 2 * (governor->level - 1);
    if (governor->rarity == LeaderRarity::Paragon) pct += 3;
    return std::clamp(pct, 0, 30);
}

int governorResearchBonusPct(const Empire& empire, ObjectId planet) {
    const Leader* governor = assignedToPlanet(empire, planet);
    if (!governor) return 0;
    int pct = hasTrait(*governor, LeaderTrait::Bureaucrat) ? 6
            : hasTrait(*governor, LeaderTrait::Paragon) ? 8
            : hasTrait(*governor, LeaderTrait::Genius) ? 4 : 0;
    pct += 2 * (governor->level - 1);
    if (governor->rarity == LeaderRarity::Paragon) pct += 3;
    return std::clamp(pct, 0, 30);
}

int governorPopulationGrowthBonusPct(const Empire& empire, ObjectId planet) {
    const Leader* governor = assignedToPlanet(empire, planet);
    if (!governor) return 0;
    int pct = hasTrait(*governor, LeaderTrait::Agrarian) ? 8 : 0;
    if (hasTrait(*governor, LeaderTrait::Paragon)) pct += 5;
    pct += std::max<int>(0, int(governor->level) - 1);
    if (governor->rarity == LeaderRarity::Paragon) pct += 3;
    return std::clamp(pct, 0, 25);
}

int scientistResearchBonusPct(const Empire& empire) {
    const Leader* scientist = assignedScientist(empire);
    if (!scientist) return 0;
    int pct = hasTrait(*scientist, LeaderTrait::Genius) ? 8
            : hasTrait(*scientist, LeaderTrait::Visionary) ? 5
            : hasTrait(*scientist, LeaderTrait::Paragon) ? 10 : 0;
    pct += 2 * (scientist->level - 1);
    if (scientist->rarity == LeaderRarity::Paragon) pct += 5;
    return std::clamp(pct, 0, 35);
}

int generalGroundDefenseBonusPct(const Empire& empire, ObjectId colony) {
    for (const Leader& general : empire.leaders) {
        if (!general.alive || general.role != LeaderRole::General || general.assignedColony != colony) continue;
        int pct = 2 * std::max<int>(0, int(general.level) - 1);
        if (hasTrait(general, LeaderTrait::Tactician)) pct += 5;
        if (hasTrait(general, LeaderTrait::Defender)) pct += 7;
        if (hasTrait(general, LeaderTrait::Aggressive)) pct += 3;
        if (general.rarity == LeaderRarity::Paragon) pct += 4;
        return std::clamp(pct, 0, 25);
    }
    return 0;
}

int admiralCombatBonusPct(const GameState& state, EmpireId empireId, FleetId fleetId) {
    if (!empireId.valid() || empireId.index() >= state.empires.size() || !fleetId.valid()) return 0;
    for (const Leader& admiral : state.empire(empireId).leaders) {
        if (!admiral.alive || admiral.role != LeaderRole::Admiral || admiral.assignedFleet != fleetId) continue;
        int pct = 2 * std::max<int>(0, int(admiral.level) - 1);
        if (hasTrait(admiral, LeaderTrait::Tactician)) pct += 5;
        if (hasTrait(admiral, LeaderTrait::Aggressive)) pct += 7;
        if (hasTrait(admiral, LeaderTrait::Defender)) pct += 4;
        if (admiral.rarity == LeaderRarity::Paragon) pct += 4;
        return std::clamp(pct, 0, 25);
    }
    return 0;
}

void advanceTurn(GameState& state, EmpireId id) {
    if (!id.valid() || id.index() >= state.empires.size()) return;
    Empire& empire = state.empire(id);
    if (!empire.alive) return;

    // Computer empires automatically attach an available Admiral to their
    // largest fleet. Human players retain full control through the Leaders UI.
    if (empire.kind != PlayerKind::Human) {
        for (Leader& admiral : empire.leaders) {
            if (!admiral.alive || admiral.role != LeaderRole::Admiral || admiral.assignedFleet.valid()) continue;
            const Fleet* best = nullptr;
            for (const Fleet& fleet : state.fleets) {
                if (fleet.owner != id || fleet.members.empty()) continue;
                const bool occupied = std::any_of(empire.leaders.begin(), empire.leaders.end(),
                    [&](const Leader& other) {
                        return other.alive && other.id != admiral.id && other.role == LeaderRole::Admiral &&
                               other.assignedFleet == fleet.id;
                    });
                if (!occupied && (!best || fleet.members.size() > best->members.size())) best = &fleet;
            }
            if (best) {
                admiral.assignedFleet = best->id;
                addLog(state, id, LogCategory::Misc, "Admiral assigned",
                       std::format("{} has assumed command of {}.", admiral.name, best->name));
            }
        }
    }

    for (Leader& leader : empire.leaders) {
        if (!leader.alive) continue;
        if (leader.assignedColony.valid()) {
            const Colony* colony = state.colony(leader.assignedColony);
            if (!colony || colony->owner != id) {
                leader.assignedColony = {};
                addLog(state, id, LogCategory::Misc, "Leader reassigned",
                       std::format("{} has been recalled after losing their colony.", leader.name));
            }
        }
        if (leader.assignedFleet.valid()) {
            const Fleet* fleet = state.fleet(leader.assignedFleet);
            if (!fleet || fleet->owner != id) {
                leader.assignedFleet = {};
                addLog(state, id, LogCategory::Misc, "Leader reassigned",
                       std::format("{} has been recalled after their fleet was disbanded or captured.", leader.name));
            }
        }

        uint32_t xp = 1;
        switch (leader.role) {
            case LeaderRole::Governor: xp = leader.assignedColony.valid() ? 5 : 1; break;
            case LeaderRole::Admiral: {
                xp = leader.assignedFleet.valid() ? 5 : 1;
                if (const Fleet* fleet = state.fleet(leader.assignedFleet)) {
                    for (const CombatRecord& combat : state.combats) {
                        if (combat.turn != state.turn ||
                            std::find(combat.participants.begin(), combat.participants.end(), id) == combat.participants.end()) continue;
                        const bool fought = std::any_of(combat.pieces.begin(), combat.pieces.end(), [&](const CombatPiece& piece) {
                            return piece.owner == id && piece.vehicle.valid() &&
                                   std::find(fleet->members.begin(), fleet->members.end(), piece.vehicle) != fleet->members.end();
                        });
                        if (fought) { xp += 40; break; }
                    }
                }
                break;
            }
            case LeaderRole::Scientist: xp = 4; break;
            case LeaderRole::General: xp = leader.assignedColony.valid() || leader.assignedFleet.valid() ? 4 : 1; break;
            case LeaderRole::Ruler: xp = 2; break;
            case LeaderRole::Count: break;
        }
        if (leader.rarity == LeaderRarity::Paragon) ++xp;
        grantXp(state, id, empire, leader, xp);

        // One game turn is one tenth of a year. A leader has a birthday every
        // ten completed turns; lifespan differs by species and Paragons live longer.
        if (state.turn > 0 && state.turn % 10 == 0) {
            ++leader.age;
            uint16_t expected = naturalLifeExpectancy(empire);
            if (leader.rarity == LeaderRarity::Paragon) expected = static_cast<uint16_t>(expected + 25);
            if (leader.age > expected) {
                const int risk = std::clamp(2 + (int(leader.age) - int(expected)) * 5, 2, 100);
                if (state.rng.percent(risk)) retire(state, id, leader, "natural causes at age " + std::to_string(leader.age));
            }
        }
    }

    // A living empire must always have exactly one Sovereign. If the ruler
    // dies, the most experienced surviving officer inherits the office while
    // retaining their name, traits, rarity, age and career progression.
    const bool hasSovereign = std::any_of(empire.leaders.begin(), empire.leaders.end(),
        [](const Leader& leader) { return leader.alive && leader.role == LeaderRole::Ruler; });
    if (!hasSovereign) {
        Leader* successor = nullptr;
        for (Leader& candidate : empire.leaders) {
            if (!candidate.alive || candidate.role == LeaderRole::Ruler) continue;
            if (!successor || candidate.level > successor->level ||
                (candidate.level == successor->level && candidate.experience > successor->experience))
                successor = &candidate;
        }

        if (successor) {
            successor->role = LeaderRole::Ruler;
            successor->assignedColony = {};
            successor->assignedFleet = {};
            successor->epithet = !empire.leaderTitle.empty() ? empire.leaderTitle : roleEpithet(LeaderRole::Ruler);
        } else {
            // Catastrophic simultaneous loss of the whole command staff:
            // generate a new head of state so the empire is not left leaderless.
            Leader sovereign;
            sovereign.id = empire.nextLeaderId++;
            sovereign.name = recruitName(state, empire);
            sovereign.epithet = !empire.leaderTitle.empty() ? empire.leaderTitle : roleEpithet(LeaderRole::Ruler);
            sovereign.role = LeaderRole::Ruler;
            sovereign.rarity = LeaderRarity::Regular;
            sovereign.trait = LeaderTrait::Inspirational;
            sovereign.age = 38;
            sovereign.hiredTurn = state.turn;
            empire.leaders.push_back(std::move(sovereign));
            successor = &empire.leaders.back();
        }
        empire.leaderName = successor->name;
        addLog(state, id, LogCategory::Misc, "Succession",
               std::format("{} has assumed the throne after the death of the previous Sovereign.", successor->name));
    }
}

} // namespace opense4::game::leaders

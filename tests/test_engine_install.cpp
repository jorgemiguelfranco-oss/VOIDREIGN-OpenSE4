// Engine checks against a supplied ruleset directory (opt-in: set
// VOIDREIGN_DATA_DIR to generated data; OPENSE4_CLASSIC_DATA remains a legacy alias).

#include "engine_fixture.hpp"

#include "game/ai.hpp"
#include "game/ai_data.hpp"
#include "game/design.hpp"
#include "game/economy.hpp"
#include "game/events.hpp"
#include "game/government.hpp"
#include "game/intel.hpp"
#include "game/query.hpp"
#include "game/research.hpp"
#include "game/turn.hpp"

#include <doctest/doctest.h>

#include <algorithm>
#include <array>
#include <cstdlib>
#include <string>
#include <utility>
#include <vector>

using namespace opense4;
using namespace opense4::game;

namespace {

const Rules* installRules() {
    static const std::unique_ptr<Rules> rules = []() -> std::unique_ptr<Rules> {
        const char* env = std::getenv("VOIDREIGN_DATA_DIR");
        if (!env || !*env) env = std::getenv("OPENSE4_CLASSIC_DATA");  // legacy CI/test variable
        if (!env) return nullptr;
        auto dir = ruleset::findInstalledDataDir(std::string_view(env) == "auto" ? std::filesystem::path{} : std::filesystem::path(env));
        if (!dir) return nullptr;
        auto loaded = ruleset::loadRuleset(*dir);
        if (!loaded.ruleset) return nullptr;
        return std::make_unique<Rules>(std::move(*loaded.ruleset), dir->parent_path());
    }();
    return rules.get();
}

} // namespace

TEST_CASE("installed data set: VoidReign content, setup and turn economy (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;
    CHECK(std::count_if(r->racePresets().begin(), r->racePresets().end(), [](const auto& p) { return !p.neutral; }) == 12);
    CHECK(std::count_if(r->racePresets().begin(), r->racePresets().end(), [](const auto& p) { return p.neutral; }) == 3);
    const auto hasName = [](const auto& records, std::string_view name) {
        return std::any_of(records.begin(), records.end(), [&](const auto& record) { return record.name == name; });
    };
    CHECK(r->data().vehicleSizes.size() >= 7);
    CHECK(hasName(r->data().vehicleSizes, "Vanguard Frigate"));
    CHECK(hasName(r->data().vehicleSizes, "Aegis Cruiser"));
    CHECK(hasName(r->data().components, "Orbital Yard Module"));
    CHECK(hasName(r->data().facilities, "Planetary Shipyard"));
    CHECK(hasName(r->data().facilities, "Central Warehouse"));

    // The data pack must expose the engine's implemented event and
    // intelligence systems; an empty catalogue would silently disable them.
    CHECK(r->data().eventTypes.size() >= 6);
    int previousSeverity = -1;
    for (const auto& event : r->data().eventTypes) {
        CHECK_MESSAGE(effects::parseEffect(event.type).has_value(), event.type);
        CHECK_FALSE(event.picture.empty());
        CHECK_FALSE(event.messages.empty());
        if (!event.messages.empty()) {
            CHECK_FALSE(event.messages.front().title.empty());
            CHECK_FALSE(event.messages.front().text.empty());
        }
        const int severity = static_cast<int>(events::parseSeverity(event.severity));
        CHECK(severity >= previousSeverity);  // severity filtering is file-order sensitive
        previousSeverity = severity;
    }
    CHECK(r->data().intelProjects.size() >= 15);
    bool defenseI = false, defenseII = false, defenseIII = false;
    for (const auto& project : r->data().intelProjects) {
        CHECK_MESSAGE(effects::parseEffect(project.type).has_value(), project.name);
        CHECK_MESSAGE(project.cost > 0, project.name);
        CHECK_FALSE(project.sourceMessages.empty());
        CHECK_FALSE(project.targetMessages.empty());
        if (!project.targetMessages.empty()) {
            CHECK_FALSE(project.targetMessages.front().title.empty());
            CHECK_FALSE(project.targetMessages.front().text.empty());
        }
        if (project.type == "Intelligence Defense") {
            defenseI |= project.effectAmount == 1;
            defenseII |= project.effectAmount == 2;
            defenseIII |= project.effectAmount == 3;
        }
    }
    CHECK(defenseI);
    CHECK(defenseII);
    CHECK(defenseIII);

    const auto espionageArea = r->data().findTechArea("Espionage");
    REQUIRE(espionageArea.has_value());
    const std::vector<std::pair<std::string_view, int>> gatedProjects{
        {"Countermeasure Net II", 2}, {"Countermeasure Net III", 4},
        {"Diplomatic Cipher Scan", 1}, {"Research Extraction", 3},
        {"Supply Sabotage", 1}, {"Drive-System Sabotage", 3},
        {"Facility Sabotage", 4}, {"Trade Network Disruption", 2},
        {"Message Interception", 2},
    };
    for (const auto& [name, level] : gatedProjects) {
        const auto project = std::find_if(r->data().intelProjects.begin(), r->data().intelProjects.end(),
                                          [&](const auto& p) { return p.name == name; });
        REQUIRE_MESSAGE(project != r->data().intelProjects.end(), name);
        REQUIRE(project->requirements.size() == 1);
        CHECK(project->requirements.front().area == *espionageArea);
        CHECK(project->requirements.front().level == level);
    }

    for (const auto& p : r->racePresets()) {
        CHECK_FALSE(p.name.empty());
        if (!p.neutral) {
            CHECK_FALSE(p.tiers.empty());
            CHECK_FALSE(governmentProfile(p.empireType).name.empty());
        }
    }

    GameSetup setup;
    setup.seed = 42;
    setup.options.systemCount = 30;
    for (size_t i = 0; i < 4; ++i) {
        EmpireSetup e;
        e.preset = r->racePresets()[i * 3 % r->racePresets().size()].folder;
        e.kind = i == 0 ? PlayerKind::Human : PlayerKind::Computer;
        setup.empires.push_back(e);
    }
    // The player as in a Quick Start: one Design minister run (spec 01 §2.1).
    StartExtras extras;
    extras.designMinisterRun.push_back(EmpireId{0u});
    auto game = createGame(*r, setup, extras);
    REQUIRE_MESSAGE(game.has_value(), (game ? std::string{} : game.error()));
    GameState& s = *game;
    // In-game reforms debit the treasury and persist through the existing
    // empire type field, while invalid profile names are rejected atomically.
    Empire& reforming = s.empires.front();
    const std::string nextGovernment = reforming.empireType == "Merchant Republic" ? "Technocracy" : "Merchant Republic";
    reforming.stockpile = Resources{10000, 10000, 10000};  // isolate pricing from starting-economy balance
    const Resources beforeReform = reforming.stockpile;
    CHECK(apply(*r, s, reforming.id, cmd::SetEmpireOptions{.empireType = nextGovernment}).ok);
    CHECK(reforming.empireType == nextGovernment);
    const Resources reformCost{2500, 1500, 1000};
    CHECK(reforming.stockpile == beforeReform - reformCost);
    const Resources afterReform = reforming.stockpile;
    CHECK_FALSE(apply(*r, s, reforming.id, cmd::SetEmpireOptions{.empireType = std::string("Independent")}).ok);
    CHECK(reforming.stockpile == afterReform);
    for (const Empire& e : s.empires) {
        INFO(e.name);
        CHECK(e.racialPointsSpent <= s.options.racialPoints);
        const Colony& home = opense4::test::homeworld(s, e.id);
        CHECK(home.totalPopulation() > 0);
        CHECK(colonyHasSpaceYard(*r, home));
        // Starting assets (spec 01 §3.6): only the Quick Start player has designs.
        if (e.id.index() == 0) CHECK(e.designs.size() >= 2);
        else CHECK(e.designs.empty());
        for (DesignId d : e.designs) {
            const DesignStats st = computeDesignStats(*r, &e, s.design(d));
            CHECK_MESSAGE(st.problems.empty(), s.design(d).name << ": " << (st.problems.empty() ? "" : st.problems.front()));
        }
    }
    // The original VOIDREIGN ruleset must provide actual storage buildings
    // that increase the engine's per-resource treasury caps.
    const auto& facilities = r->data().facilities;
    const auto warehouse = std::find_if(facilities.begin(), facilities.end(),
                                         [](const ruleset::Facility& f) { return f.name == "Central Warehouse"; });
    REQUIRE(warehouse != facilities.end());
    const auto home = std::find_if(s.colonies.begin(), s.colonies.end(),
                                   [](const auto& c) { return c && c->owner == EmpireId{0u} && c->homeworld; });
    REQUIRE(home != s.colonies.end());
    const Resources beforeWarehouse = economy::storageCapacity(*r, s, EmpireId{0u});
    // The starting colony has a modest baseline treasury but no free warehouse.
    // Excess resources are discarded at the end-of-turn storage step.
    CHECK(beforeWarehouse == Resources{25000, 25000, 25000});
    GameState storageProbe = s;
    const EmpireId player{0u};
    storageProbe.empire(player).stockpile = Resources{30000, 40000, 50000};
    TurnContext storageContext{*r, storageProbe, {}, {}, {}};
    economy::applyStorageCap(storageContext, player);
    CHECK(storageProbe.empire(player).stockpile == Resources{25000, 25000, 25000});
    CHECK(storageProbe.empire(player).economy.lostToStorage == Resources{5000, 15000, 25000});
    (*home)->facilities.push_back(static_cast<uint32_t>(std::distance(facilities.begin(), warehouse)));
    const Resources afterWarehouse = economy::storageCapacity(*r, s, EmpireId{0u});
    for (size_t resource = 0; resource < 3; ++resource)
        CHECK(afterWarehouse.v[resource] > beforeWarehouse.v[resource]);

    CHECK(s.vehicles.empty());
    std::vector<EmpireOrders> none;
    processTurn(*r, s, none);
    CHECK(s.turn == 1);
    for (const Empire& e : s.empires)
        if (e.kind == PlayerKind::Computer) CHECK_FALSE(e.designs.empty());  // designed in the first turn
}

TEST_CASE("VOIDREIGN generated economy and technology remain bounded over eight AI-managed turns (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;

    GameSetup setup;
    setup.seed = 0x564f494452454947ull;
    setup.options.systemCount = 24;
    std::vector<const ruleset::RacePreset*> playable;
    for (const auto& preset : r->racePresets())
        if (!preset.neutral) playable.push_back(&preset);
    REQUIRE(playable.size() >= 7);

    for (size_t i = 0; i < 4; ++i) {
        EmpireSetup empire;
        empire.preset = playable[i * 2]->folder;
        empire.kind = i == 0 ? PlayerKind::Human : PlayerKind::Computer;
        setup.empires.push_back(std::move(empire));
    }

    auto created = createGame(*r, setup);
    REQUIRE_MESSAGE(created.has_value(), (created ? std::string{} : created.error()));
    GameState& game = *created;
    const std::vector<EmpireOrders> noOrders;

    for (uint32_t turn = 1; turn <= 8; ++turn) {
        processTurn(*r, game, noOrders);
        CHECK(game.turn == turn);

        for (const Empire& empire : game.empires) {
            INFO(empire.name);
            const Resources cap = economy::storageCapacity(*r, game, empire.id);
            CHECK(cap.covers(empire.stockpile));
            CHECK(empire.economy.storageCap == cap);
            CHECK(empire.techLevels.size() == r->data().techAreas.size());
            for (size_t area = 0; area < empire.techLevels.size() && area < r->data().techAreas.size(); ++area) {
                CHECK(empire.techLevels[area] >= 0);
                CHECK(empire.techLevels[area] <= r->data().techAreas[area].maxLevel);
            }
            CHECK(empire.researchPool >= 0);
            CHECK(empire.intelPool >= 0);
        }
    }
}




TEST_CASE("VOIDREIGN factions and neutral powers load their own native AI research doctrines (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;

    REQUIRE(r->racePresets().size() == 15);
    for (const auto& preset : r->racePresets()) {
        const ai::AiProfile profile = ai::loadProfile(r->gameRoot(), preset.folder);
        CHECK_MESSAGE(!profile.researchErrors, preset.folder);
        CHECK_MESSAGE(profile.research.size() == 30, preset.folder);
        CHECK_MESSAGE(std::any_of(profile.sources.begin(), profile.sources.end(), [](const std::string& path) {
            return path.find("_AI_Research.txt") != std::string::npos;
        }), preset.folder);
        for (const auto& row : profile.research) {
            CHECK_MESSAGE(!row.area.empty(), preset.folder);
            CHECK_MESSAGE(row.level > 0, preset.folder);
            CHECK_MESSAGE(row.minPercent > 0, preset.folder);
            CHECK_MESSAGE(r->data().findTechArea(row.area).has_value(), row.area);
        }
    }

    // Each of the twelve playable species gets a recognisably different
    // opening focus rather than falling back to the same random AI queue.
    const ai::AiProfile aurel = ai::loadProfile(r->gameRoot(), "Aurel");
    const ai::AiProfile dravak = ai::loadProfile(r->gameRoot(), "Dravak");
    REQUIRE_FALSE(aurel.research.empty());
    REQUIRE_FALSE(dravak.research.empty());
    CHECK(aurel.research.front().area == "Colonization");
    CHECK(dravak.research.front().area == "Weapons");
}

TEST_CASE("VOIDREIGN technology unlocks ship, colonization, defence and logistics progression (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;

    GameSetup setup;
    setup.seed = 0x5445434850524f47ull;
    setup.options.systemCount = 16;
    const ruleset::RacePreset* playable = nullptr;
    for (const auto& preset : r->racePresets())
        if (!preset.neutral) { playable = &preset; break; }
    REQUIRE(playable != nullptr);
    EmpireSetup empireSetup;
    empireSetup.preset = playable->folder;
    empireSetup.kind = PlayerKind::Human;
    setup.empires.push_back(std::move(empireSetup));
    auto created = createGame(*r, setup);
    REQUIRE_MESSAGE(created.has_value(), (created ? std::string{} : created.error()));
    GameState game = std::move(*created);
    Empire& empire = game.empire(EmpireId{0u});

    auto componentIndex = [&](std::string_view name) -> uint32_t {
        for (uint32_t i = 0; i < r->data().components.size(); ++i)
            if (r->data().components[i].name == name) return i;
        FAIL_CHECK(std::string("missing component: ") + std::string(name));
        return 0;
    };
    auto hullIndex = [&](std::string_view name) -> uint32_t {
        for (uint32_t i = 0; i < r->data().vehicleSizes.size(); ++i)
            if (r->data().vehicleSizes[i].name == name) return i;
        FAIL_CHECK(std::string("missing hull: ") + std::string(name));
        return 0;
    };
    auto facilityIndex = [&](std::string_view name) -> uint32_t {
        for (uint32_t i = 0; i < r->data().facilities.size(); ++i)
            if (r->data().facilities[i].name == name) return i;
        FAIL_CHECK(std::string("missing facility: ") + std::string(name));
        return 0;
    };
    auto gate = [&](const auto& record, std::string_view areaName, int level) {
        const auto area = r->data().findTechArea(areaName);
        REQUIRE(area.has_value());
        REQUIRE(record.requirements.size() == 1);
        CHECK(record.requirements.front().area == *area);
        CHECK(record.requirements.front().level == level);
    };
    auto grant = [&](std::string_view areaName, int level) {
        const auto area = r->data().findTechArea(areaName);
        REQUIRE(area.has_value());
        empire.techLevels[area->index()] = level;
    };

    // The first ship can be designed immediately, with a basic drive and
    // essential crew systems. Advanced hardware is not available at turn zero.
    CHECK(r->hullAvailable(empire, hullIndex("Vanguard Frigate")));
    CHECK(r->componentAvailable(empire, componentIndex("Command Bridge")));
    CHECK(r->componentAvailable(empire, componentIndex("Life Support")));
    CHECK(r->componentAvailable(empire, componentIndex("Crew Quarters")));
    CHECK(r->componentAvailable(empire, componentIndex("Ion Drive")));
    const uint32_t starterWeapon = componentIndex("Pulse Emitter");
    CHECK(r->componentAvailable(empire, starterWeapon));
    CHECK(r->component(starterWeapon).isWeapon());
    CHECK(r->component(starterWeapon).weapon.kind == ruleset::WeaponKind::DirectFire);
    CHECK(r->component(starterWeapon).weapon.damageAtRange.size() == 6);

    // The stock AI Fighter template must be capable of producing a legal
    // interceptor: it needs both a movement drive and a weapon fitting Fighter.
    const auto fighterMask = ruleset::maskOf(ruleset::VehicleType::Fighter);
    CHECK((r->component(componentIndex("Ion Drive")).vehicles & fighterMask) != 0);
    CHECK((r->component(starterWeapon).vehicles & fighterMask) != 0);
    CHECK((r->component(componentIndex("Laser Battery")).vehicles & fighterMask) != 0);
    CHECK((r->component(componentIndex("Missile Rack")).vehicles & fighterMask) != 0);
    CHECK((r->component(componentIndex("Shield Generator")).vehicles & fighterMask) != 0);
    CHECK_FALSE(r->hullAvailable(empire, hullIndex("Aegis Cruiser")));
    CHECK_FALSE(r->componentAvailable(empire, componentIndex("Fusion Drive")));
    CHECK_FALSE(r->componentAvailable(empire, componentIndex("Rock Colony Core")));
    CHECK_FALSE(r->facilityAvailable(empire, facilityIndex("Mineral Warehouse")));

    // Inspect the intended progression, including the separate logistics
    // levels needed to support a growing economy and its resource stockpiles.
    gate(r->hull(hullIndex("Aegis Cruiser")), "Ship Construction", 2);
    gate(r->hull(hullIndex("Pioneer Ark")), "Colonization", 1);
    CHECK(r->hull(hullIndex("Pioneer Ark")).minPercentColonyModules == 15);
    gate(r->hull(hullIndex("Meridian Freighter")), "Logistics", 1);
    gate(r->hull(hullIndex("Citadel Platform")), "Ship Construction", 3);
    gate(r->hull(hullIndex("Interceptor")), "Weapons", 1);
    gate(r->hull(hullIndex("Recon Satellite")), "Sensors", 1);
    gate(r->component(componentIndex("Fusion Drive")), "Drive Systems", 2);
    gate(r->component(componentIndex("Rock Colony Core")), "Colonization", 1);
    gate(r->component(componentIndex("Ice Colony Core")), "Colonization", 2);
    gate(r->component(componentIndex("Gas Colony Core")), "Colonization", 3);
    gate(r->component(componentIndex("Cargo Hold")), "Logistics", 1);
    gate(r->component(componentIndex("Shield Generator")), "Defensive Systems", 1);
    gate(r->component(componentIndex("Armour Plating")), "Defensive Systems", 1);
    gate(r->component(componentIndex("Sensor Array")), "Sensors", 1);
    gate(r->component(componentIndex("Supply Matrix")), "Logistics", 2);
    gate(r->component(componentIndex("Orbital Yard Module")), "Ship Construction", 2);
    gate(r->component(componentIndex("Laser Battery")), "Weapons", 1);
    gate(r->component(componentIndex("Missile Rack")), "Weapons", 3);
    gate(r->facility(facilityIndex("Mineral Warehouse")), "Logistics", 1);
    gate(r->facility(facilityIndex("Organic Warehouse")), "Logistics", 1);
    gate(r->facility(facilityIndex("Radioactive Vault")), "Logistics", 2);
    gate(r->facility(facilityIndex("Central Warehouse")), "Logistics", 4);
    gate(r->facility(facilityIndex("Orbital Defence Grid")), "Defensive Systems", 2);
    gate(r->facility(facilityIndex("Terraforming Array")), "Planetology", 2);

    // Researching the relevant areas makes the matching designs and buildings
    // legal through the same Rules API used by the ship designer and build UI.
    grant("Drive Systems", 2);
    grant("Colonization", 3);
    grant("Logistics", 4);
    grant("Ship Construction", 3);
    grant("Weapons", 3);
    grant("Sensors", 1);
    grant("Defensive Systems", 2);
    grant("Planetology", 2);

    CHECK(r->hullAvailable(empire, hullIndex("Aegis Cruiser")));
    CHECK(r->hullAvailable(empire, hullIndex("Pioneer Ark")));
    CHECK(r->hullAvailable(empire, hullIndex("Meridian Freighter")));
    CHECK(r->hullAvailable(empire, hullIndex("Citadel Platform")));
    CHECK(r->hullAvailable(empire, hullIndex("Interceptor")));
    CHECK(r->hullAvailable(empire, hullIndex("Recon Satellite")));
    for (std::string_view name : {"Fusion Drive", "Rock Colony Core", "Ice Colony Core", "Gas Colony Core",
                                  "Cargo Hold", "Shield Generator", "Armour Plating", "Sensor Array", "Supply Matrix",
                                  "Orbital Yard Module", "Laser Battery", "Missile Rack"})
        CHECK(r->componentAvailable(empire, componentIndex(name)));

    // Let the real design minister build its normal templates at this tech
    // level. The Fighter template must produce a legal Interceptor using the
    // components explicitly made compatible with Fighter hulls.
    ai::designMinisterRun(*r, game, owner);
    const auto fighterDesign = std::find_if(empire.designs.begin(), empire.designs.end(),
                                            [](const Design& design) { return design.templateName == "Fighter"; });
    REQUIRE(fighterDesign != empire.designs.end());
    CHECK(r->hull(fighterDesign->hull).type == ruleset::VehicleType::Fighter);
    bool hasFighterDrive = false;
    bool hasFighterWeapon = false;
    for (const DesignEntry& entry : fighterDesign->entries) {
        const auto& component = r->component(entry.component);
        hasFighterDrive |= component.name == "Ion Drive";
        hasFighterWeapon |= component.name == "Pulse Emitter" || component.name == "Laser Battery" ||
                            component.name == "Missile Rack";
        CHECK((component.vehicles & fighterMask) != 0);
    }
    CHECK(hasFighterDrive);
    CHECK(hasFighterWeapon);

    // The same design minister must be able to create each planetary
    // settlement variant with one matching core and the Pioneer Ark hull.
    for (const auto& [templateName, coreName] :
         std::array<std::pair<std::string_view, std::string_view>, 3>{{
             {"Colony (Rock)", "Rock Colony Core"},
             {"Colony (Ice)", "Ice Colony Core"},
             {"Colony (Gas)", "Gas Colony Core"},
         }}) {
        const auto colonyDesign = std::find_if(empire.designs.begin(), empire.designs.end(),
                                               [&](const Design& design) { return design.templateName == templateName; });
        REQUIRE_MESSAGE(colonyDesign != empire.designs.end(), templateName);
        CHECK(r->hull(colonyDesign->hull).name == "Pioneer Ark");
        CHECK(std::any_of(colonyDesign->entries.begin(), colonyDesign->entries.end(),
                          [&](const DesignEntry& entry) { return r->component(entry.component).name == coreName; }));
    }
    for (std::string_view name : {"Mineral Warehouse", "Organic Warehouse", "Radioactive Vault",
                                  "Central Warehouse", "Orbital Defence Grid", "Terraforming Array"})
        CHECK(r->facilityAvailable(empire, facilityIndex(name)));
}


TEST_CASE("VOIDREIGN research progress unlocks a real ship weapon through the engine turn step (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;

    GameSetup setup;
    setup.seed = 0x5245534541524348ull;
    setup.options.systemCount = 12;
    const ruleset::RacePreset* playable = nullptr;
    for (const auto& preset : r->racePresets())
        if (!preset.neutral) { playable = &preset; break; }
    REQUIRE(playable != nullptr);
    EmpireSetup player;
    player.preset = playable->folder;
    player.kind = PlayerKind::Human;
    setup.empires.push_back(std::move(player));
    auto created = createGame(*r, setup);
    REQUIRE_MESSAGE(created.has_value(), (created ? std::string{} : created.error()));
    GameState game = std::move(*created);
    const EmpireId owner{0u};
    Empire& empire = game.empire(owner);

    const auto weapons = r->data().findTechArea("Weapons");
    REQUIRE(weapons.has_value());
    const auto laser = std::find_if(r->data().components.begin(), r->data().components.end(),
                                    [](const auto& c) { return c.name == "Laser Battery"; });
    REQUIRE(laser != r->data().components.end());
    const uint32_t laserIndex = static_cast<uint32_t>(std::distance(r->data().components.begin(), laser));
    CHECK_FALSE(r->componentAvailable(empire, laserIndex));

    // Queue research using the same command the front-end issues.
    cmd::SetResearch order;
    order.queue.push_back(ResearchProject{*weapons, 0});
    REQUIRE(apply(*r, game, owner, order).ok);

    // One point cannot unlock the technology, but it must be retained as
    // progress by the native research processor.
    const int64_t cost = r->techLevelCost(*weapons, 1, game.options.techCost);
    REQUIRE(cost > 1);
    empire.researchPool = 1;
    TurnContext firstStep{*r, game, {}, {}, {}};
    research::researchStep(firstStep, owner);
    CHECK(empire.techLevel(*weapons) == 0);
    REQUIRE(empire.research.size() == 1);
    CHECK(empire.research.front().progress == 1);
    CHECK_FALSE(r->componentAvailable(empire, laserIndex));

    // Deliver the exact remaining amount and let researchStep grant the level.
    empire.researchPool = cost - 1;
    TurnContext completionStep{*r, game, {}, {}, {}};
    research::researchStep(completionStep, owner);
    CHECK(empire.techLevel(*weapons) == 1);
    CHECK(empire.research.empty());
    CHECK(r->componentAvailable(empire, laserIndex));
    CHECK(empire.researchPool == 0);
}

TEST_CASE("VOIDREIGN random events and intelligence projects execute in the native engine (opt-in)") {
    const Rules* r = installRules();
    if (!r) return;

    GameSetup setup;
    setup.seed = 0x45564e54494e5445ull;
    setup.options.systemCount = 16;
    std::vector<const ruleset::RacePreset*> playable;
    for (const auto& preset : r->racePresets())
        if (!preset.neutral) playable.push_back(&preset);
    REQUIRE(playable.size() >= 2);
    for (size_t i = 0; i < 2; ++i) {
        EmpireSetup empire;
        empire.preset = playable[i]->folder;
        empire.kind = i == 0 ? PlayerKind::Human : PlayerKind::Computer;
        setup.empires.push_back(std::move(empire));
    }
    auto created = createGame(*r, setup);
    REQUIRE_MESSAGE(created.has_value(), (created ? std::string{} : created.error()));
    GameState game = std::move(*created);
    const EmpireId source{0u}, target{1u};

    // The command boundary must enforce the same Espionage tech gates as
    // the Intelligence screen: level II cannot be queued before the research.
    const auto espionageArea = r->data().findTechArea("Espionage");
    REQUIRE(espionageArea.has_value());
    const auto countermeasureII = std::find_if(r->data().intelProjects.begin(), r->data().intelProjects.end(),
                                                [](const auto& p) { return p.name == "Countermeasure Net II"; });
    REQUIRE(countermeasureII != r->data().intelProjects.end());
    const uint32_t countermeasureIndex = static_cast<uint32_t>(std::distance(r->data().intelProjects.begin(), countermeasureII));
    GameState progression = game;
    IntelProjectOrder lockedDefense;
    lockedDefense.project = countermeasureIndex;
    cmd::SetIntel lockedQueue;
    lockedQueue.queue.push_back(lockedDefense);
    CHECK_FALSE(apply(*r, progression, source, lockedQueue).ok);
    progression.empire(source).techLevels[espionageArea->index()] = 2;
    CHECK(apply(*r, progression, source, lockedQueue).ok);
    CHECK(progression.empire(source).intel.size() == 1);

    // Trigger a real original VOIDREIGN event against a specific homeworld.
    const auto event = std::find_if(r->data().eventTypes.begin(), r->data().eventTypes.end(),
                                    [](const auto& e) { return e.picture == "MineralBloom"; });
    REQUIRE(event != r->data().eventTypes.end());
    const uint32_t eventIndex = static_cast<uint32_t>(std::distance(r->data().eventTypes.begin(), event));
    const ObjectId planet = opense4::test::homeworld(game, target).planet;
    const auto beforeValue = game.galaxy.object(planet).value;
    effects::Target eventTarget;
    eventTarget.empire = target;
    eventTarget.object = planet;
    TurnContext eventContext{*r, game, {}, {}, {}};
    Rng eventRng(0x4556454e54ull);
    REQUIRE(events::trigger(eventContext, eventIndex, eventTarget, eventRng));
    CHECK(game.galaxy.object(planet).value != beforeValue);
    CHECK(std::any_of(game.empire(target).log.begin(), game.empire(target).log.end(),
                      [](const LogEntry& entry) { return entry.title == "Mineral Bloom"; }));

    // Complete a funded Planetary Census against the other empire's colony.
    // This exercises contact validation, target selection, the effect handler
    // and the original project-message delivery on both sides.
    GameState intelligenceGame = game;
    intelligenceGame.empire(source).relation(target).contact = true;
    intelligenceGame.empire(target).relation(source).contact = true;
    const auto census = std::find_if(r->data().intelProjects.begin(), r->data().intelProjects.end(),
                                     [](const auto& p) { return p.name == "Planetary Census"; });
    REQUIRE(census != r->data().intelProjects.end());
    const uint32_t censusIndex = static_cast<uint32_t>(std::distance(r->data().intelProjects.begin(), census));
    IntelProjectOrder order;
    order.project = censusIndex;
    order.target = target;
    order.targetPlanet = opense4::test::homeworld(intelligenceGame, target).planet;
    intelligenceGame.empire(source).intel = {order};
    intelligenceGame.empire(source).intelPool = census->cost;
    TurnContext intelContext{*r, intelligenceGame, {}, {}, {}};
    intel::intelStep(intelContext, source);
    CHECK(intelligenceGame.empire(source).intel.empty());
    CHECK(intelligenceGame.empire(source).intelPool == 0);
    CHECK(std::any_of(intelligenceGame.empire(source).log.begin(), intelligenceGame.empire(source).log.end(),
                      [](const LogEntry& entry) {
                          return entry.category == LogCategory::Intelligence &&
                                 entry.title == "Planetary Census";
                      }));
    CHECK(std::any_of(intelligenceGame.empire(target).log.begin(), intelligenceGame.empire(target).log.end(),
                      [](const LogEntry& entry) {
                          return entry.category == LogCategory::Intelligence &&
                                 entry.title == "Security Alert";
                      }));
}

TEST_CASE("installed data set: a Terran Quick Start gets the observed designs (opt-in)") {
    // Spec 07 session 3: eleven designs, one per design type, dated 2400.0,
    // all prototypes, and no ship.
    const Rules* r = installRules();
    if (!r || !findPreset(*r, "Terran")) return;
    GameSetup setup;
    setup.seed = 7;
    EmpireSetup me;
    me.preset = "Terran";
    setup.empires.push_back(me);
    StartExtras extras;
    extras.designMinisterRun.push_back(EmpireId{0u});
    auto game = createGame(*r, setup, extras);
    REQUIRE_MESSAGE(game.has_value(), (game ? std::string{} : game.error()));
    std::vector<std::string> types;
    for (DesignId d : game->empire(EmpireId{0u}).designs) {
        const Design& design = game->design(d);
        CHECK(design.createdTurn == 0);
        CHECK(design.built == 0);
        types.push_back(design.designType);
    }
    std::sort(types.begin(), types.end());
    const std::vector<std::string> observed{"Attack Ship",          "Base Space Yard", "Cargo Transport",   "Colony (Rock)",   "Defense Base",
                                            "Kamikaze Attack Ship", "Population Transport", "Satellite", "Satellite Layer", "Troop Transport",
                                            "Weapon Platform"};
    CHECK(types == observed);
    CHECK(game->vehicles.empty());
}

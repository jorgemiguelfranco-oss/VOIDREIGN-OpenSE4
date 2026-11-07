// Engine checks against a supplied ruleset directory (opt-in: set
// VOIDREIGN_DATA_DIR to generated data; OPENSE4_CLASSIC_DATA remains a legacy alias).

#include "engine_fixture.hpp"

#include "game/design.hpp"
#include "game/economy.hpp"
#include "game/events.hpp"
#include "game/government.hpp"
#include "game/query.hpp"
#include "game/turn.hpp"

#include <doctest/doctest.h>

#include <algorithm>
#include <cstdlib>
#include <string>
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
        const int severity = static_cast<int>(events::parseSeverity(event.severity));
        CHECK(severity >= previousSeverity);  // severity filtering is file-order sensitive
        previousSeverity = severity;
    }
    CHECK(r->data().intelProjects.size() >= 15);
    bool defenseI = false, defenseII = false, defenseIII = false;
    for (const auto& project : r->data().intelProjects) {
        CHECK_MESSAGE(effects::parseEffect(project.type).has_value(), project.name);
        CHECK_MESSAGE(project.cost > 0, project.name);
        if (project.type == "Intelligence Defense") {
            defenseI |= project.effectAmount == 1;
            defenseII |= project.effectAmount == 2;
            defenseIII |= project.effectAmount == 3;
        }
    }
    CHECK(defenseI);
    CHECK(defenseII);
    CHECK(defenseIII);

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

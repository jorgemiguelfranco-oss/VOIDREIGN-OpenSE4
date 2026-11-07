from opense4 import rules, testing
import vr_economy


class Resources:
    def __init__(self, minerals=0, organics=0, radioactives=0):
        self.minerals = minerals
        self.organics = organics
        self.radioactives = radioactives


class Empire:
    def __init__(self, id, stored):
        self.id = id
        self.stored = stored
        self.mod_data = {}


class Colony:
    def __init__(self, owner, facilities, homeworld=False, slots=5):
        self.owner = owner
        self.facilities = facilities
        self.homeworld = homeworld
        self.facility_slots = slots


class Game:
    def __init__(self, colonies, capacities):
        self.colonies = colonies
        self.capacities = capacities
        self.empires = []
        self.rules = self

    def facility_named(self, name):
        assert name == vr_economy.WAREHOUSE
        return type("Facility", (), {"id": 77})()

    def ability(self, facility_id, name, kind):
        assert name == vr_economy.CAPACITY_ABILITY and kind == "facility"
        return self.capacities.get(facility_id, 0)


class Effects:
    def __init__(self):
        self.resource_changes = []
        self.facilities = []
        self.logs = []

    def add_resources(self, empire, minerals=0, organics=0, radioactives=0):
        change = {"minerals": minerals, "organics": organics, "radioactives": radioactives}
        self.resource_changes.append(change)
        return change

    def add_facility(self, colony, facility):
        self.facilities.append((colony, facility))

    def log(self, empire, text, title="", category="misc", location=None):
        self.logs.append((title, text, category))


def test_overflow_is_removed_per_resource_using_all_owned_warehouses():
    empire = Empire(1, Resources(7000, 2500, 9000))
    game = Game([
        Colony(1, [10, 11]),
        Colony(2, [12]),  # foreign warehouse must not count
    ], {10: 3000, 11: 2000, 12: 9000})
    fx = Effects()

    vr_economy.enforce_warehouse_capacity(game, empire, "income", "after", fx)

    assert fx.resource_changes == [{
        "minerals": -2000,
        "organics": 0,
        "radioactives": -4000,
    }]
    assert empire.mod_data["warehouse_overflow_total"] == 6000
    assert fx.logs[0][0] == "Treasury overflow"


def test_no_warehouse_means_no_treasury_storage():
    empire = Empire(1, Resources(100, 200, 300))
    game = Game([Colony(1, [])], {})
    fx = Effects()

    vr_economy.enforce_warehouse_capacity(game, empire, "income", "after", fx)

    assert fx.resource_changes == [{
        "minerals": -100,
        "organics": -200,
        "radioactives": -300,
    }]


def test_starting_homeworld_receives_one_warehouse_if_a_slot_is_free():
    home = Colony(1, [2], homeworld=True, slots=3)
    foreign = Colony(2, [], homeworld=True, slots=3)
    game = Game([home, foreign], {})
    game.empires = [Empire(1, Resources()), Empire(2, Resources())]
    fx = Effects()

    vr_economy.seed_homeworld_warehouses(game, fx)

    assert fx.facilities == [(home, 77), (foreign, 77)]


def test_warehouse_rules_are_registered_at_income_and_after_galaxy():
    registrations = [r for r in rules.registrations()
                     if r.fn in (vr_economy.seed_homeworld_warehouses, vr_economy.enforce_warehouse_capacity)]
    assert any(r.name == "after_galaxy" for r in registrations)
    assert any(r.name == "empire_end_of_turn" and r.step == "income" and r.when == "after"
               for r in registrations)


def test_mod_data_and_facility_ability_exist_in_the_ruleset():
    r = rules.Rules(testing.game_rules())
    facility = r.facility_named(vr_economy.WAREHOUSE)
    assert facility is not None
    assert facility.ability_value(vr_economy.CAPACITY_ABILITY) == 5000
    assert r.aggregation(vr_economy.CAPACITY_ABILITY) == "sum"

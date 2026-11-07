from opense4 import rules, testing
import vr_start


class Empire:
    def __init__(self, id):
        self.id = id


class Colony:
    def __init__(self, owner, facilities, homeworld=False, slots=5):
        self.owner = owner
        self.facilities = facilities
        self.homeworld = homeworld
        self.facility_slots = slots


class Game:
    def __init__(self, colonies, empires):
        self.colonies = colonies
        self.empires = empires
        self.rules = self

    def facility_named(self, name):
        assert name == vr_start.WAREHOUSE
        return type("Facility", (), {"id": 77})()


class Effects:
    def __init__(self):
        self.facilities = []
        self.logs = []

    def add_facility(self, colony, facility):
        self.facilities.append((colony, facility))

    def log(self, empire, text, title="", category="misc", location=None):
        self.logs.append((empire, title, text, category))


def test_each_starting_homeworld_receives_a_warehouse_when_there_is_room():
    home1 = Colony(1, [2], homeworld=True, slots=3)
    home2 = Colony(2, [], homeworld=True, slots=3)
    foreign = Colony(3, [], homeworld=False, slots=3)
    game = Game([home1, home2, foreign], [Empire(1), Empire(2)])
    fx = Effects()

    vr_start.seed_homeworld_warehouses(game, fx)

    assert [colony for colony, _ in fx.facilities] == [home1, home2]
    assert all(facility.id == 77 for _, facility in fx.facilities)
    assert len(fx.logs) == 2


def test_no_warehouse_is_added_when_homeworld_has_no_free_slot():
    home = Colony(1, [1, 2], homeworld=True, slots=2)
    game = Game([home], [Empire(1)])
    fx = Effects()

    vr_start.seed_homeworld_warehouses(game, fx)

    assert fx.facilities == []


def test_starting_warehouse_hook_is_registered():
    registrations = [r for r in rules.registrations() if r.fn is vr_start.seed_homeworld_warehouses]
    assert registrations and registrations[0].name == "after_galaxy"


def test_native_resource_storage_abilities_are_present_in_the_ruleset():
    facility = rules.Rules(testing.game_rules()).facility_named(vr_start.WAREHOUSE)
    assert facility is not None
    assert facility.ability_value("Resource Storage - Mineral") == 5000
    assert facility.ability_value("Resource Storage - Organics") == 5000
    assert facility.ability_value("Resource Storage - Radioactives") == 5000

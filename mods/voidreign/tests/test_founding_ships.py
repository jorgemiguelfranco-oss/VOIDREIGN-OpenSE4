from opense4 import rules, testing

CREW = ("Ship Bridge", "Ship Life Support", "Ship Crew Quarters")


def the_rules():
    return rules.Rules(testing.game_rules())


def test_pathfinder_hull_is_available_and_correctly_sized():
    hull = the_rules().hull_named("VoidReign Pathfinder")
    assert hull is not None
    assert hull.type == "ship"
    assert hull.tonnage == 150
    assert hull.requirements == []
    assert hull.min_percent_cargo == 25


def test_cargo_rack_uses_native_storage_ability():
    rack = the_rules().component_named("VoidReign Cargo Rack")
    assert rack is not None
    assert rack.ability_value("Cargo Storage") == 60
    assert rack.tonnage == 20
    assert {"ship", "base"}.issubset(rack.vehicle_types)


def test_pathfinder_can_be_designed_with_starting_components():
    r = the_rules()
    view = testing.game_view()
    levels = view["my"]["research"]["levels"]

    def available(component):
        return all(req.area is None or levels[req.area] >= req.level for req in component.requirements) and "ship" in component.vehicle_types

    def smallest_with(ability):
        found = [c for c in r.components if available(c) and c.has_ability(ability)]
        if not found:
            raise testing.Skip("the selected data set has no starting component with " + ability)
        return min(found, key=lambda c: c.tonnage)

    hull = r.hull_named("VoidReign Pathfinder")
    rack = r.component_named("VoidReign Cargo Rack")
    essentials = [smallest_with(name) for name in CREW]
    essentials.append(smallest_with("Standard Ship Movement"))
    used = sum(c.tonnage for c in essentials) + 2 * rack.tonnage
    assert used <= hull.tonnage
    assert 2 * rack.tonnage * 100 >= hull.min_percent_cargo * hull.tonnage

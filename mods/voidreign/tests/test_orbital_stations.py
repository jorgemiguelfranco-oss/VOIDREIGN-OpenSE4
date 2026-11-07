from opense4 import rules, testing


def the_rules():
    return rules.Rules(testing.game_rules())


def test_orbital_station_is_a_stationary_base_hull():
    hull = the_rules().hull_named("VoidReign Orbital Station")
    assert hull is not None
    assert hull.type == "base"
    assert hull.tonnage == 400
    assert hull.requirements == []


def test_orbital_shipyard_uses_the_native_space_yard_ability():
    component = the_rules().component_named("VoidReign Orbital Shipyard")
    assert component is not None
    assert component.has_ability("Space Yard")
    assert "base" in component.vehicle_types


def test_sensor_array_adds_em_active_detection():
    component = the_rules().component_named("VoidReign Sensor Array")
    assert component is not None
    assert component.has_ability("Sensor Level")
    assert component.ability_values("Sensor Level") == [("EM Active", 2)]


def test_station_modules_fit_a_valid_base_design_when_base_crew_parts_exist():
    r = the_rules()
    hull = r.hull_named("VoidReign Orbital Station")
    modules = [
        r.component_named("VoidReign Orbital Shipyard"),
        r.component_named("VoidReign Sensor Array"),
    ]
    assert all(modules)
    view = testing.game_view()
    levels = view["my"]["research"]["levels"]

    def available(component):
        return all(req.area is None or levels[req.area] >= req.level for req in component.requirements) and "base" in component.vehicle_types

    def smallest_with(ability):
        found = [c for c in r.components if available(c) and c.has_ability(ability)]
        if not found:
            raise testing.Skip("this data set has no base component with " + ability)
        return min(found, key=lambda c: c.tonnage)

    try:
        crew = [smallest_with(name) for name in ("Ship Bridge", "Ship Life Support", "Ship Crew Quarters")]
    except testing.Skip:
        raise
    used = sum(c.tonnage for c in crew + modules)
    assert used <= hull.tonnage

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

from opense4 import rules, testing

NAMES = ["VoidReign Pulse Cannon " + n for n in ("I", "II", "III", "IV", "V")]


def the_rules():
    return rules.Rules(testing.game_rules())


def test_energy_weapons_area_has_five_levels():
    area = the_rules().tech_named("VoidReign Energy Weapons")
    assert area is not None
    assert area.max_level == 5
    assert area.requirements == []


def test_each_research_level_unlocks_a_stronger_longer_ranged_weapon():
    r = the_rules()
    area = r.tech_named("VoidReign Energy Weapons")
    previous_damage = 0
    previous_range = 0
    for level, name in enumerate(NAMES, 1):
        weapon = r.component_named(name)
        assert weapon is not None, name
        assert weapon.is_weapon and weapon.weapon.kind == "direct_fire"
        assert [(req.area, req.level) for req in weapon.requirements] == [(area.id, level)]
        assert weapon.weapon.damage_at_range[1] > previous_damage
        assert weapon.weapon.max_range > previous_range
        previous_damage = weapon.weapon.damage_at_range[1]
        previous_range = weapon.weapon.max_range


def test_pulse_cannons_share_one_upgrade_family_in_research_order():
    components = [the_rules().component_named(name) for name in NAMES]
    assert len({component.family for component in components}) == 1
    assert [component.id for component in components] == sorted(component.id for component in components)

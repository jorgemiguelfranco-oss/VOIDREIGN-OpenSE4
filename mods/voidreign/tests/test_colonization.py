from opense4 import rules


def the_rules():
    return rules.Rules(__import__("opense4").testing.game_rules())


def test_planetary_engineering_unlocks_colonization_modules():
    r = the_rules()
    area = r.tech_named("VoidReign Planetary Engineering")
    assert area is not None
    assert area.max_level == 5
    expected = {
        "VoidReign Rock Colonization Module": "Colonize Planet - Rock",
        "VoidReign Ice Colonization Module": "Colonize Planet - Ice",
        "VoidReign Gas Colonization Module": "Colonize Planet - Gas",
    }
    for name, ability in expected.items():
        module = r.component_named(name)
        assert module is not None
        assert module.has_ability(ability)
        assert [(req.area, req.level) for req in module.requirements] == [(area.id, 1)]


def test_colonizer_hull_requires_planetary_engineering():
    r = the_rules()
    area = r.tech_named("VoidReign Planetary Engineering")
    hull = r.hull_named("VoidReign Colonizer")
    assert hull is not None
    assert hull.type == "ship"
    assert hull.min_percent_colony_mods == 30
    assert [(req.area, req.level) for req in hull.requirements] == [(area.id, 1)]

#!/usr/bin/env python3
"""Generate VOIDREIGN's original, distributable ruleset.

The game engine reads the same documented text data format used by OpenSE4,
but every rule, faction, name and preset written here is original VOIDREIGN
content. No Space Empires IV data or artwork is copied into this package.
"""
from __future__ import annotations

import argparse
from pathlib import Path

HEADER = "=====\nVOIDREIGN original game data. Copyright (C) VOIDREIGN contributors.\n=====\n"

def render_record(fields: list[tuple[str, object]]) -> str:
    return "\n".join(f"{key} := {value}" for key, value in fields)

def write_records(root: Path, name: str, records: list[list[tuple[str, object]]]) -> None:
    body = "\n\n".join(render_record(record) for record in records)
    text = HEADER + "*BEGIN*\n" + (body + "\n" if body else "") + "*END*\n"
    (root / name).write_text(text, encoding="utf-8", newline="\n")

def write_list(root: Path, name: str, values: list[str]) -> None:
    (root / name).write_text("\n".join(values) + "\n", encoding="utf-8", newline="\n")

def rec(**fields: object) -> list[tuple[str, object]]:
    return list(fields.items())

def ability(kind: str, description: str, first: object = "", second: object = "") -> list[tuple[str, object]]:
    return [
        ("Type", kind), ("Descr", description), ("Val 1", first), ("Val 2", second)
    ]

def add_ability(fields: list[tuple[str, object]], index: int, value: list[tuple[str, object]]) -> None:
    for suffix, content in value:
        fields.append((f"Ability {index} {suffix}", content))


def add_tech_requirements(fields: list[tuple[str, object]], requirements: tuple[tuple[str, int], ...]) -> None:
    fields.append(("Number of Tech Req", len(requirements)))
    for index, (area, level) in enumerate(requirements, 1):
        fields.append((f"Tech Area Req {index}", area))
        fields.append((f"Tech Level Req {index}", level))

def build(output: Path) -> None:
    data = output / "Data"
    races_dir = output / "Pictures" / "Races"
    neutral_dir = output / "Pictures" / "RaceNeutral"
    names_dir = output / "Dsgnname"
    ai_dir = output / "Ai" / "Adaptive"
    for directory in (data, races_dir, neutral_dir, names_dir, ai_dir):
        directory.mkdir(parents=True, exist_ok=True)

    # A broad, connected technology tree. Early ship, colony and economy parts
    # are intentionally available at game start; later tiers provide progression.
    tech_specs = [
        ("Applied Physics", "Science", 20, 900),
        ("Drive Systems", "Propulsion", 20, 1100),
        ("Power Systems", "Engineering", 20, 1200),
        ("Ship Construction", "Engineering", 20, 1300),
        ("Weapons", "Military", 20, 1400),
        ("Defensive Systems", "Military", 20, 1400),
        ("Colonization", "Expansion", 20, 1000),
        ("Economics", "Industry", 20, 900),
        ("Logistics", "Industry", 20, 1100),
        ("Computing", "Science", 20, 1200),
        ("Sensors", "Science", 20, 1200),
        ("Materials Science", "Engineering", 20, 1300),
        ("Planetology", "Science", 20, 1200),
        ("Espionage", "Intelligence", 20, 1500),
        ("Stellar Engineering", "Advanced", 20, 2200),
    ]
    write_records(data, "TechArea.txt", [
        [("Name", n), ("Group", group), ("Description", f"{n} research advances the empire's capabilities."),
         ("Maximum Level", maximum), ("Level Cost", cost), ("Start Level", 0),
         ("Raise Level", 0), ("Racial Area", 0), ("Unique Area", 0),
         ("Can Be Removed", "True"), ("Number of Tech Req", 0)]
        for n, group, maximum, cost in tech_specs
    ])

    # Ship, station and support hull families.
    hull_specs = [
        ("Vanguard Frigate", "Frigate", "VF", "Ship", 220, 850, 180, 120, 1, True, 1, 1, True, 6, 0, 0, 0),
        ("Aegis Cruiser", "Cruiser", "AC", "Ship", 520, 2100, 500, 360, 2, True, 1, 1, True, 12, 0, 0, 0),
        ("Pioneer Ark", "Ark", "PA", "Ship", 300, 1250, 350, 180, 1, True, 1, 1, True, 8, 0, 20, 0),
        ("Meridian Freighter", "Freighter", "MF", "Ship", 360, 1300, 500, 150, 1, True, 1, 1, True, 8, 0, 0, 25),
        ("Citadel Platform", "Citadel", "CP", "Base", 700, 2500, 400, 500, 0, True, 1, 1, False, 0, 0, 0, 0),
        ("Interceptor", "Interceptor", "IN", "Fighter", 25, 90, 10, 5, 1, False, 0, 0, True, 4, 0, 0, 0),
        ("Recon Satellite", "Recon", "RS", "Satellite", 60, 180, 30, 20, 0, False, 0, 0, False, 0, 0, 0, 0),
    ]
    # First-generation hulls are available immediately; later ship classes
    # unlock as their supporting technologies are researched.
    hull_tech = {
        "Aegis Cruiser": (("Ship Construction", 2),),
        "Pioneer Ark": (("Colonization", 1),),
        "Meridian Freighter": (("Logistics", 1),),
        "Citadel Platform": (("Ship Construction", 3),),
        "Interceptor": (("Weapons", 1),),
        "Recon Satellite": (("Sensors", 1),),
    }
    hull_records = []
    for name, short, code, kind, tonnage, minerals, organics, radioactives, engines, bridge, life, crew, uses, max_engines, fighter_pct, colony_pct, cargo_pct in hull_specs:
        fields = [
            ("Name", name), ("Short Name", short), ("Description", f"VOIDREIGN {short.lower()} hull."),
            ("Code", code), ("Primary Bitmap Name", code), ("Alternate Bitmap Name", code),
            ("Vehicle Type", kind), ("Tonnage", tonnage), ("Cost Minerals", minerals),
            ("Cost Organics", organics), ("Cost Radioactives", radioactives),
            ("Engines Per Move", engines), ("Number of Abilities", 0),
            ("Requirement Must Have Bridge", "True" if bridge else "False"),
            ("Requirement Can Have Aux Con", "True" if kind == "Ship" and tonnage >= 300 else "False"),
            ("Requirement Min Life Support", life), ("Requirement Min Crew Quarters", crew),
            ("Requirement Uses Engines", "True" if uses else "False"), ("Requirement Max Engines", max_engines),
            ("Requirement Pct Fighter Bays", fighter_pct), ("Requirement Pct Colony Mods", colony_pct),
            ("Requirement Pct Cargo", cargo_pct),
        ]
        add_tech_requirements(fields, hull_tech.get(name, ()))
        hull_records.append(fields)
    write_records(data, "VehicleSize.txt", hull_records)

    # Ship modules. Their ability names are the engine's typed rules, so these
    # components participate in design validation, combat and construction.
    component_specs = [
        ("Command Bridge", "Ship", 10, 18, 45, 5, "Control", 11, [ability("Ship Bridge", "Provides command and control.")], None),
        ("Life Support", "Ship", 10, 12, 35, 5, "Control", 11, [ability("Ship Life Support", "Supports the crew.")], None),
        ("Crew Quarters", "Ship", 10, 10, 30, 5, "Control", 11, [ability("Ship Crew Quarters", "Houses the crew.")], None),
        ("Ion Drive", "Ship\\Base\\Drone", 20, 20, 70, 18, "Engines", 10, [ability("Standard Ship Movement", "Generates strategic thrust.", 1)], None),
        ("Fusion Drive", "Ship\\Base\\Drone", 25, 24, 90, 22, "Engines", 10, [ability("Standard Ship Movement", "Improved strategic thrust.", 2)], None),
        ("Rock Colony Core", "Ship", 45, 35, 130, 35, "Colonization", 30, [ability("Colonize Planet - Rock", "Allows colonization of rocky planets.", 1), ability("Cargo Storage", "Carries colonists and equipment.", 80)], None),
        ("Ice Colony Core", "Ship", 45, 35, 130, 35, "Colonization", 31, [ability("Colonize Planet - Ice", "Allows colonization of icy planets.", 1), ability("Cargo Storage", "Carries colonists and equipment.", 80)], None),
        ("Gas Colony Core", "Ship", 50, 40, 150, 40, "Colonization", 32, [ability("Colonize Planet - Gas", "Allows colonization of gas worlds.", 1), ability("Cargo Storage", "Carries colonists and equipment.", 80)], None),
        ("Cargo Hold", "Ship", 20, 18, 55, 12, "Logistics", 33, [ability("Cargo Storage", "Expands cargo capacity.", 100)], None),
        ("Shield Generator", "Ship\\Base\\Sat", 20, 14, 80, 28, "Defence", 40, [ability("Shield Generation", "Generates defensive shields.", 25)], None),
        ("Armour Plating", "Ship\\Base\\Sat", 10, 28, 35, 4, "Defence", 41, [ability("Armor", "Adds structural armour.")], None),
        ("Sensor Array", "Ship\\Base", 12, 12, 45, 16, "Sensors", 50, [ability("Sensor Level", "Improves detection.", "EM Active", 2)], None),
        ("Supply Matrix", "Ship\\Base", 18, 14, 60, 18, "Logistics", 51, [ability("Supply Storage", "Stores ship supplies.", 500)], None),
        ("Orbital Yard Module", "Ship\\Base", 55, 30, 220, 60, "Shipyards", 60, [ability("Space Yard", "Builds and repairs ships.", 1, 500)], None),
        # A basic sidearm remains available from the beginning so the first
        # generation of frigates can defend itself before Weapons research.
        ("Pulse Emitter", "Ship\\Base\\Sat", 18, 12, 42, 12, "Weapons", 19, [], {
            "Weapon Type": "Direct Fire", "Weapon Target": "Ships\\Planets",
            "Weapon Damage At Rng": "12 12 10 8 6", "Weapon Damage Type": "Normal",
            "Weapon Reload Rate": 1, "Weapon Display Type": "Beam", "Weapon Display": 4,
            "Weapon Modifier": 0, "Weapon Sound": "laser", "Weapon Family": 199,
            "Weapon Seeker Speed": 0, "Weapon Seeker Dmg Res": 0,
        }),
        ("Laser Battery", "Ship\\Base\\Sat", 20, 15, 55, 18, "Weapons", 20, [], {
            "Weapon Type": "Direct Fire", "Weapon Target": "Ships\\Planets",
            "Weapon Damage At Rng": "16 16 14 12 10 8", "Weapon Damage Type": "Normal",
            "Weapon Reload Rate": 1, "Weapon Display Type": "Beam", "Weapon Display": 4,
            "Weapon Modifier": 0, "Weapon Sound": "laser", "Weapon Family": 200,
            "Weapon Seeker Speed": 0, "Weapon Seeker Dmg Res": 0,
        }),
        ("Missile Rack", "Ship\\Base", 25, 16, 75, 28, "Weapons", 21, [], {
            "Weapon Type": "Seeking", "Weapon Target": "Ships\\Planets",
            "Weapon Damage At Rng": "28 28 28 28 28 28 28 28", "Weapon Damage Type": "Normal",
            "Weapon Reload Rate": 2, "Weapon Display Type": "Missile", "Weapon Display": 1,
            "Weapon Modifier": 0, "Weapon Sound": "missile", "Weapon Family": 201,
            "Weapon Seeker Speed": 3, "Weapon Seeker Dmg Res": 0,
        }),
    ]
    component_tech = {
        "Fusion Drive": (("Drive Systems", 2),),
        "Rock Colony Core": (("Colonization", 1),),
        "Ice Colony Core": (("Colonization", 2),),
        "Gas Colony Core": (("Colonization", 3),),
        "Cargo Hold": (("Logistics", 1),),
        "Shield Generator": (("Defensive Systems", 1),),
        "Armour Plating": (("Defensive Systems", 1),),
        "Sensor Array": (("Sensors", 1),),
        "Supply Matrix": (("Logistics", 2),),
        "Orbital Yard Module": (("Ship Construction", 2),),
        "Laser Battery": (("Weapons", 1),),
        "Missile Rack": (("Weapons", 3),),
    }
    component_records = []
    for name, vehicle, tonnage, structure, minerals, radioactives, group, family, abilities, weapon in component_specs:
        fields = [
            ("Name", name), ("Description", f"VOIDREIGN {name.lower()} module."),
            ("Pic Num", family % 64), ("Tonnage Space Taken", tonnage), ("Tonnage Structure", structure),
            ("Cost Minerals", minerals), ("Cost Organics", 0), ("Cost Radioactives", radioactives),
            ("Vehicle Type", vehicle), ("Supply Amount Used", 1), ("Restrictions", "None"),
            ("General Group", group), ("Family", family), ("Roman Numeral", 1),
            ("Number of Abilities", len(abilities)),
        ]
        add_tech_requirements(fields, component_tech.get(name, ()))
        for index, value in enumerate(abilities, 1):
            add_ability(fields, index, value)
        fields.append(("Weapon Type", "None") if weapon is None else ("Weapon Type", weapon["Weapon Type"]))
        if weapon is not None:
            for key, value in weapon.items():
                if key != "Weapon Type":
                    fields.append((key, value))
        component_records.append(fields)
    write_records(data, "Components.txt", component_records)

    # The starting world receives one of each essential economic role. Storage
    # is deliberately NOT a free starting role: expansion requires warehouses.
    facility_specs = [
        ("Planetary Spaceport", "Logistics", (500, 0, 50), [ability("Spaceport", "Enables interstellar logistics.")]),
        ("Planetary Shipyard", "Shipyards", (650, 0, 180), [
            ability("Space Yard", "Basic ship construction.", 1, 1200),
            ability("Space Yard", "Advanced ship construction.", 2, 1200),
            ability("Space Yard", "Capital construction.", 3, 1200),
        ]),
        ("Supply Depot", "Logistics", (350, 0, 100), [ability("Supply Generation", "Produces fleet supplies.", 6000)]),
        ("Mineral Extractor", "Resource Industry", (300, 50, 0), [ability("Resource Generation - Minerals", "Extracts mineral resources.", 1100)]),
        ("Hydroponics Complex", "Resource Industry", (250, 250, 0), [ability("Resource Generation - Organics", "Produces organic resources.", 1000)]),
        ("Isotope Refinery", "Resource Industry", (350, 0, 180), [ability("Resource Generation - Radioactives", "Refines radioactive resources.", 900)]),
        ("Research Institute", "Science", (450, 100, 100), [ability("Point Generation - Research", "Produces research points.", 700)]),
        ("Intelligence Bureau", "Intelligence", (500, 100, 150), [ability("Point Generation - Intelligence", "Produces intelligence points.", 350)]),
        ("Mineral Warehouse", "Storage", (500, 100, 50), [ability("Resource Storage - Mineral", "Adds mineral stockpile capacity.", 30000)]),
        ("Organic Warehouse", "Storage", (400, 300, 0), [ability("Resource Storage - Organics", "Adds organic stockpile capacity.", 30000)]),
        ("Radioactive Vault", "Storage", (450, 0, 250), [ability("Resource Storage - Radioactives", "Adds radioactive stockpile capacity.", 30000)]),
        ("Central Warehouse", "Storage", (1200, 500, 400), [
            ability("Resource Storage - Mineral", "Adds mineral stockpile capacity.", 75000),
            ability("Resource Storage - Organics", "Adds organic stockpile capacity.", 75000),
            ability("Resource Storage - Radioactives", "Adds radioactive stockpile capacity.", 75000),
        ]),
        ("Orbital Defence Grid", "Defence", (800, 100, 500), [ability("Planet Shield Generation", "Protects the colony from bombardment.", 100)]),
        ("Terraforming Array", "Planetary Engineering", (1000, 400, 400), [ability("Planet Change Conditions", "Improves planetary habitability.", 1)]),
    ]
    facility_tech = {
        "Mineral Warehouse": (("Logistics", 1),),
        "Organic Warehouse": (("Logistics", 1),),
        "Radioactive Vault": (("Logistics", 2),),
        "Central Warehouse": (("Logistics", 4),),
        "Orbital Defence Grid": (("Defensive Systems", 2),),
        "Terraforming Array": (("Planetology", 2),),
    }
    facility_records = []
    for index, (name, group, cost, abilities) in enumerate(facility_specs, 1):
        minerals, organics, radioactives = cost
        fields = [
            ("Name", name), ("Description", f"VOIDREIGN {name.lower()}."),
            ("Facility Group", group), ("Facility Family", 10 + index),
            ("Roman Numeral", 1), ("Restrictions", "None"), ("Pic Num", index),
            ("Cost Minerals", minerals), ("Cost Organics", organics), ("Cost Radioactives", radioactives),
            ("Number of Abilities", len(abilities)),
        ]
        add_tech_requirements(fields, facility_tech.get(name, ()))
        for ability_index, value in enumerate(abilities, 1):
            add_ability(fields, ability_index, value)
        facility_records.append(fields)
    write_records(data, "Facility.txt", facility_records)

    planet_records = []
    for name, physical, stellar, facilities, population, cargo in [
        ("Tiny", "Planet", "Tiny", 4, 500, 80),
        ("Small", "Planet", "Small", 7, 1000, 200),
        ("Medium", "Planet", "Medium", 12, 2200, 500),
        ("Large", "Planet", "Large", 16, 3500, 850),
        ("Huge", "Planet", "Huge", 22, 6000, 1400),
        ("Enormous", "Planet", "Huge", 30, 9000, 2200),
        ("Asteroid Belt", "Asteroids", "Small", 4, 500, 300),
    ]:
        planet_records.append([
            ("Name", name), ("Physical Type", physical), ("Stellar Size", stellar),
            ("Max Facilities", facilities), ("Max Population", population), ("Max Cargo Spaces", cargo),
            ("Max Facilities Domed", max(1, facilities // 5)),
            ("Max Population Domed", max(100, population // 10)),
            ("Max Cargo Spaces Domed", max(40, cargo // 5)),
            ("Constructed", "False"), ("Special Ability ID", 0),
        ])
    write_records(data, "PlanetSize.txt", planet_records)

    trait_specs = [
        ("Deep Vaults", "Mineral Storage", 25, 250),
        ("Organic Granaries", "Organics Storage", 25, 250),
        ("Radioactive Casks", "Radioactives Storage", 25, 250),
        ("Industrial Efficiency", "Production", 5, 300),
        ("Hydroponic Expertise", "Organics Production", 10, 300),
        ("High Yield Mining", "Mineral Production", 10, 300),
        ("Isotope Mastery", "Radioactives Production", 10, 300),
        ("Research Networks", "Research Production", 10, 350),
        ("Neural Logic", "Intelligence Production", 10, 350),
        ("Trade Houses", "Trade", 10, 300),
        ("Fleet Doctrine", "Space Combat", 10, 350),
        ("Ground Doctrine", "Ground Combat", 10, 250),
        ("Precision Gunnery", "Ship Attack", 5, 250),
        ("Reinforced Hulls", "Ship Defense", 5, 250),
        ("Rapid Reproduction", "Reproduction", 5, 300),
        ("Efficient Maintenance", "Maintenance Cost", 5, 300),
    ]
    write_records(data, "RacialTraits.txt", [
        [("Name", name), ("Description", f"{name} is a defining advantage of this species."),
         ("Pic Num", index), ("General Type", "Advantage"), ("Cost", cost),
         ("Trait Type", kind), ("Value 1", value), ("Required Trait 1", "None"),
         ("Required Trait 2", "None"), ("Required Trait 3", "None"),
         ("Restricted Trait 1", "None"), ("Restricted Trait 2", "None"),
         ("Restricted Trait 3", "None")]
        for index, (name, kind, value, cost) in enumerate(trait_specs, 1)
    ])

    culture_specs = [
        ("Balanced", "A balanced approach to growth, science and industry.", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ("Industrial", "Production-first institutions and extensive supply chains.", 8, -3, 0, -2, 0, 0, 0, 0, 5, 0),
        ("Scholarly", "Research-led society with strong scientific institutions.", -3, 10, 5, 0, 0, 0, 0, 0, -2, 0),
        ("Commercial", "A network of trade houses and merchant fleets.", 0, 0, 0, 12, 0, 0, 0, 0, 0, 0),
        ("Martial", "A disciplined military society built around fleet strength.", 0, -2, 0, -2, 10, 8, -2, 0, 0, 5),
    ]
    write_records(data, "Cultures.txt", [
        [("Name", n), ("Description", d), ("Production", p), ("Research", r),
         ("Intelligence", i), ("Trade", t), ("Space Combat", sc), ("Ground Combat", gc),
         ("Happiness", h), ("Maintenance", m), ("SY Rate", yard), ("Repair", repair)]
        for n, d, p, r, i, t, sc, gc, h, m, yard, repair in culture_specs
    ])

    sector_records = [
        [("Physical Type", "Star"), ("Picture Num", 1), ("Description", "A stable yellow star."),
         ("Star Size", "Medium"), ("Star Age", "Average"), ("Star Color", "Yellow"), ("Star Luminosity", "Average")],
        [("Physical Type", "Planet"), ("Picture Num", 2), ("Description", "A temperate rocky world."),
         ("Planet Size", "Medium"), ("Planet Physical Type", "Rock"), ("Planet Atmosphere", "Oxygen")],
        [("Physical Type", "Planet"), ("Picture Num", 3), ("Description", "A frozen frontier world."),
         ("Planet Size", "Small"), ("Planet Physical Type", "Ice"), ("Planet Atmosphere", "Methane")],
        [("Physical Type", "Planet"), ("Picture Num", 4), ("Description", "A dense gas giant."),
         ("Planet Size", "Large"), ("Planet Physical Type", "Gas Giant"), ("Planet Atmosphere", "Hydrogen")],
        [("Physical Type", "Asteroids"), ("Picture Num", 5), ("Description", "A belt of mineral-rich debris."),
         ("Planet Size", "Asteroid Belt"), ("Planet Physical Type", "Rock"), ("Planet Atmosphere", "None")],
        [("Physical Type", "Storm"), ("Picture Num", 6), ("Description", "A turbulent ion storm."),
         ("Storm Size", "Medium"), ("Combat Tile", "Ion Storm")],
        [("Physical Type", "Warp Point"), ("Picture Num", 7), ("Description", "A stable interstellar rift."),
         ("Warp Point Size", "Medium")],
    ]
    write_records(data, "SectType.txt", sector_records)

    write_records(data, "StellarAbilityTypes.txt", [
        [("Name", "Quiet Space"), ("Number of Poss Abilities", 1),
         ("Ability 1 Chance", 100), ("Ability 1 Type", "Sector - Sensor Interference"),
         ("Ability 1 Descr", "Sensor readings are distorted in this region."),
         ("Ability 1 Val 1", 5), ("Ability 1 Val 2", "")],
        [("Name", "Ancient Ruins"), ("Number of Poss Abilities", 1),
         ("Ability 1 Chance", 100), ("Ability 1 Type", "Ancient Ruins"),
         ("Ability 1 Descr", "An abandoned installation of unknown origin."),
         ("Ability 1 Val 1", 1), ("Ability 1 Val 2", "")],
    ])

    def system_record(name: str, description: str, startable: bool, second_star: bool = False) -> list[tuple[str, object]]:
        objects: list[list[tuple[str, object]]] = [
            [("Physical Type", "Star"), ("Position", "Ring 1"), ("Stellar Abil Type", "None"),
             ("Size", "Medium"), ("Age", "Average"), ("Color", "Yellow"), ("Luminosity", "Average")],
            [("Physical Type", "Planet"), ("Position", "Ring 3"), ("Stellar Abil Type", "None"),
             ("Size", "Any"), ("Atmosphere", "Any"), ("Composition", "Any")],
            [("Physical Type", "Planet"), ("Position", "Ring 4"), ("Stellar Abil Type", "Quiet Space"),
             ("Size", "Any"), ("Atmosphere", "Any"), ("Composition", "Any")],
        ]
        if second_star:
            objects.insert(1, [("Physical Type", "Star"), ("Position", "Ring 2"), ("Stellar Abil Type", "None"),
                               ("Size", "Small"), ("Age", "Old"), ("Color", "Red"), ("Luminosity", "Low")])
        fields: list[tuple[str, object]] = [
            ("Name", name), ("Description", description), ("System Physical Type", "Normal"),
            ("Background Bitmap", "Starfield"), ("Empires Can Start In", "True" if startable else "False"),
            ("Mask Background Objs", "False"), ("Non-Tiled Center Pic", ""),
            ("Number of Abilities", 0), ("WP Stellar Abil Type", "None"),
            ("Number of System Objs", len(objects)),
        ]
        for index, obj in enumerate(objects, 1):
            fields.extend((f"Obj {index} {key}", value) for key, value in obj)
        return fields

    write_records(data, "SystemTypes.txt", [
        system_record("Frontier System", "A standard star system with several worlds.", True),
        system_record("Binary System", "A binary star system with a quieter outer world.", False, True),
    ])
    write_records(data, "QuadrantTypes.txt", [
        [("Name", "Spiral Frontier"), ("Description", "A broad spiral galaxy with long routes between its arms."),
         ("Min Dist Between Systems", 2), ("System Placement", "Spiral"),
         ("Max Warp Points per Sys", 4), ("Min Angle Between WP", 30),
         ("Number of System Types", 2), ("Type 1 Name", "Frontier System"), ("Type 1 Chance", 850),
         ("Type 2 Name", "Binary System"), ("Type 2 Chance", 150)],
        [("Name", "Clustered Reach"), ("Description", "Dense clusters separated by open interstellar space."),
         ("Min Dist Between Systems", 1), ("System Placement", "Random"),
         ("Max Warp Points per Sys", 4), ("Min Angle Between WP", 35),
         ("Number of System Types", 2), ("Type 1 Name", "Frontier System"), ("Type 1 Chance", 700),
         ("Type 2 Name", "Binary System"), ("Type 2 Chance", 300)],
    ])

    write_records(data, "CompEnhancement.txt", [
        [("Long Name", "Heavy Weapon Mount"), ("Short Name", "Heavy"),
         ("Description", "A reinforced mount for larger weapons."), ("Code", "HW"),
         ("Cost Percent", 150), ("Tonnage Percent", 150), ("Tonnage Structure Percent", 150),
         ("Damage Percent", 140), ("Supply Percent", 125), ("Range Modifier", 0),
         ("Weapon To Hit Modifier", 0), ("Vehicle Size Minimum", 200),
         ("Weapon Type Requirement", "Direct Fire"), ("Vehicle Type", "Ship")],
    ])
    write_records(data, "Formations.txt", [
        [("Name", "Line"), ("Description", "A simple line formation."),
         ("Leader Position Xpos", 0), ("Leader Position Ypos", 0), ("Leader Design Type", "Any"),
         ("Number of Positions", 2), ("Position 1 Xpos", -1), ("Position 1 Ypos", 0),
         ("Position 1 Type", "Any"), ("Position 2 Xpos", 1), ("Position 2 Ypos", 0), ("Position 2 Type", "Any")],
        [("Name", "Spearhead"), ("Description", "A forward wedge with escorts."),
         ("Leader Position Xpos", 0), ("Leader Position Ypos", 0), ("Leader Design Type", "Any"),
         ("Number of Positions", 3), ("Position 1 Xpos", -1), ("Position 1 Ypos", -1),
         ("Position 1 Type", "Any"), ("Position 2 Xpos", 1), ("Position 2 Ypos", -1),
         ("Position 2 Type", "Any"), ("Position 3 Xpos", 0), ("Position 3 Ypos", -2), ("Position 3 Type", "Any")],
    ])
    happiness_records = []
    for name, lost, colonized, conquered in [
        ("Civic Stability", 2, -3, -2), ("Disciplined", 1, -2, -3),
        ("Stoic", 1, -1, -1), ("Communal", 3, -4, -3), ("Volatile", 4, -5, -5),
    ]:
        happiness_records.append([
            ("Name", name), ("Description", f"{name} social response model."),
            ("Max Positive Anger Change", 5), ("Max Negative Anger Change", -5),
            ("Any Ship Lost", lost), ("Any Planet Colonized", colonized),
            ("Any Planet Lost", conquered), ("Enemy Empire Destroyed", -4),
        ])
    write_records(data, "Happiness.txt", happiness_records)

    # Intelligence projects use the engine's implemented effect handlers.
    # Costs are expressed in intelligence points; sabotage has real counter-
    # intelligence exposure, while reconnaissance projects return reports.
    intel_records = []

    def intel_project(name, description, group, cost, effect, amount=1,
                      source="Our agents completed the operation against [%TargetEmpireName].",
                      target="Our intelligence services detected hostile activity from [%SourceEmpireName].",
                      tech_level=0):
        record = [
            ("Name", name), ("Description", description), ("Group", group),
            ("Cost", cost), ("Type", effect), ("Effect Amount", amount),
            ("Num Source Messages", 1), ("Source Message 1", source),
            ("Num Target Messages", 1), ("Target Message Title 1", "Security Alert"),
            ("Target Message 1", target),
        ]
        if tech_level > 0:
            record.extend([
                ("Number of Tech Req", 1),
                ("Tech Area Req 1", "Espionage"),
                ("Tech Level Req 1", tech_level),
            ])
        intel_records.append(record)

    intel_project("Countermeasure Net I", "A standing signal-analysis network that reduces the impact of hostile intelligence operations.",
                  "Counter-intelligence", 1800, "Intelligence Defense", 1,
                  "Our first countermeasure net is active against hostile intelligence operations.",
                  "Our security network reports a new countermeasure deployment.")
    intel_project("Countermeasure Net II", "A denser defensive network with stronger coverage of strategic communications.",
                  "Counter-intelligence", 4200, "Intelligence Defense", 2,
                  "Our second countermeasure net is active against hostile intelligence operations.",
                  "Our security network reports an upgraded countermeasure deployment.", tech_level=2)
    intel_project("Countermeasure Net III", "An empire-wide intelligence shield with the strongest available defensive coverage.",
                  "Counter-intelligence", 8500, "Intelligence Defense", 3,
                  "Our third countermeasure net is active against hostile intelligence operations.",
                  "Our security network reports a maximum-level countermeasure deployment.", tech_level=4)

    intel_project("Deep-Space Reconnaissance", "Map the target empire's active ships and their current locations.",
                  "Reconnaissance", 650, "Ship - Locations", 1,
                  "Fleet-location intelligence from [%TargetEmpireName]: [%ActualAmount] entries.",
                  "Our naval movements may have been exposed to an unknown observer.")
    intel_project("Fleet Concentration Analysis", "Identify the target empire's strongest known concentration of ships and bases.",
                  "Reconnaissance", 1000, "Ship - Concentrations", 1,
                  "Fleet concentration report from [%TargetEmpireName]: [%ActualAmount] units at the reported location.",
                  "Our fleet concentrations may have been identified by hostile intelligence.")
    intel_project("Shipyard Network Survey", "Locate the target empire's largest ship-building concentration.",
                  "Reconnaissance", 1250, "Ship - Construction Info", 1,
                  "Shipyard network report from [%TargetEmpireName]: [%ActualAmount] active construction locations.",
                  "Our construction network may have been mapped by hostile intelligence.")
    intel_project("Planetary Census", "Gather information about a target colony's population, facilities and condition.",
                  "Reconnaissance", 550, "Planet - Info", 1,
                  "Planetary survey completed for [%TargetEmpireName] at [%PlanetName] in [%SystemName].",
                  "A hostile reconnaissance team has surveyed one of our colonies.")
    intel_project("Technology Assessment", "Estimate the target empire's current research and technological capabilities.",
                  "Reconnaissance", 1450, "Tech Level - Info", 1,
                  "Technology assessment completed for [%TargetEmpireName].",
                  "Our research programme may have been observed by hostile intelligence.")
    intel_project("Diplomatic Cipher Scan", "Recover information about the target empire's current treaty relationships.",
                  "Diplomacy", 900, "Politics - Treaty Info", 1,
                  "Treaty intelligence recovered from [%TargetEmpireName].",
                  "Our diplomatic communications may have been compromised.", tech_level=1)

    intel_project("Research Extraction", "Steal a level of research from a target empire where our own science can make use of it.",
                  "Espionage", 2800, "Research - Steal", 1,
                  "Research extraction against [%TargetEmpireName] returned [%ActualAmount] usable result(s).",
                  "A hostile operation has targeted our research programme.", tech_level=3)
    intel_project("Supply Sabotage", "Disrupt the supply reserves of one target ship.",
                  "Sabotage", 1900, "Ship - Lose Supply", 18,
                  "Supply sabotage against [%VehicleName] was completed.",
                  "A hostile operation has depleted the supply reserves of [%VehicleName].", tech_level=1)
    intel_project("Drive-System Sabotage", "Damage the components of one target ship before it can return to a repair yard.",
                  "Sabotage", 3100, "Ship - Damage", 7,
                  "Ship sabotage against [%VehicleName] inflicted [%ActualAmount] damage.",
                  "An intelligence operation damaged [%VehicleName].", tech_level=3)
    intel_project("Facility Sabotage", "Damage a facility on a target colony and disrupt its local economy.",
                  "Sabotage", 3600, "Planet - Facility Damage", 1,
                  "Facility sabotage was completed at [%PlanetName] in [%SystemName].",
                  "A hostile operation damaged infrastructure at [%PlanetName].", tech_level=4)
    intel_project("Trade Network Disruption", "Interfere with trade between the target empire and its partners.",
                  "Economic Warfare", 2500, "Politics - Disrupt Trade", 1,
                  "Trade disruption was initiated against [%TargetEmpireName].",
                  "Our trade network reports hostile disruption activity.", tech_level=2)
    intel_project("Message Interception", "Intercept diplomatic and strategic messages sent by the target empire.",
                  "Signals Intelligence", 1750, "Politics - Intercept Messages", 1,
                  "Message interception against [%TargetEmpireName] returned [%ActualAmount] report(s).",
                  "Our diplomatic traffic may have been intercepted.", tech_level=2)

    write_records(data, "IntelProjects.txt", intel_records)

    # Original VoidReign events are ordered from least to most severe. The
    # engine's original-compatible severity filter counts records in file
    # order, so this ordering is part of the game rules.
    event_records = [
        [
            ("Type", "Planet - Value Change"), ("Severity", "Low"), ("Picture", "MineralBloom"),
            ("Effect Amount", 3), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Mineral Bloom"),
            ("Message 1", "A rare mineral bloom improves the resource value of [%PlanetName] in the [%SystemName] system by [%ActualAmount]."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Planet - Population Anger Change"), ("Severity", "Low"), ("Picture", "CivicAccord"),
            ("Effect Amount", -4), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Civic Accord"),
            ("Message 1", "A local civic accord eases unrest on [%PlanetName] in the [%SystemName] system."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Planet - Conditions Change"), ("Severity", "Medium"), ("Picture", "AtmosphericShift"),
            ("Effect Amount", 2), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Atmospheric Shift"),
            ("Message 1", "A natural atmospheric shift improves conditions on [%PlanetName] in the [%SystemName] system."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Ship - Experience Change"), ("Severity", "Medium"), ("Picture", "VeteranCadre"),
            ("Effect Amount", 1), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Veteran Cadre"),
            ("Message 1", "A chance encounter gives [%VehicleName] in the [%SystemName] system a valuable tactical lesson."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Ship - Lose Supply"), ("Severity", "High"), ("Picture", "SupplyAnomaly"),
            ("Effect Amount", 12), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Supply Anomaly"),
            ("Message 1", "An unexplained anomaly has drained supplies from [%VehicleName] in the [%SystemName] system."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Ship - Damage"), ("Severity", "High"), ("Picture", "DriveCascade"),
            ("Effect Amount", 6), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Drive Cascade"),
            ("Message 1", "A sudden drive-system cascade damages [%VehicleName] in the [%SystemName] system."),
            ("Time Till Completion", 0),
        ],
        [
            ("Type", "Planet - Facility Damage"), ("Severity", "High"), ("Picture", "InfrastructureFailure"),
            ("Effect Amount", 1), ("Message To", "Owner"),
            ("Num Messages", 1), ("Message Title 1", "Infrastructure Failure"),
            ("Message 1", "A serious infrastructure failure damages a facility on [%PlanetName] in the [%SystemName] system."),
            ("Time Till Completion", 0),
        ],
    ]
    write_records(data, "Events.txt", event_records)
    write_records(data, "DefaultStrategies.txt", [
        [("Name", "Balanced Fleet"), ("Primary Movement Strategy", "Optimal Range"),
         ("Secondary Movement Strategy", "Point Blank"), ("Targeting Priority 1", "Has Weapons"),
         ("Targeting Priority 2", "Nearest"), ("Targeting Priority 3", "None"),
         ("Targeting Priority 4", "None"), ("Dont Fire On Colony Ships", "False"),
         ("Dont Fire On Planets", "False"), ("Dont Fire On Bases(No Weapons)", "False"),
         ("Dont Fire On Ships(No Weapons)", "False"), ("Dont Fire On Seekers(On Others)", "False"),
         ("Break Formation Carriers", "False"), ("Break Formation Colony Ships", "False"),
         ("Break Formation Fighters", "False"), ("Break Formation Satellites", "False"),
         ("Break Formation Planets", "False"), ("Break Formation Transports", "False"),
         ("Fighters Launch Group Amount", 4), ("Damage Percent Per Ship", 100)],
        [("Name", "Hold Position"), ("Primary Movement Strategy", "No Movement"),
         ("Secondary Movement Strategy", "Optimal Range"), ("Targeting Priority 1", "Nearest"),
         ("Targeting Priority 2", "Has Weapons"), ("Targeting Priority 3", "None"),
         ("Targeting Priority 4", "None"), ("Dont Fire On Colony Ships", "False"),
         ("Dont Fire On Planets", "False"), ("Dont Fire On Bases(No Weapons)", "False"),
         ("Dont Fire On Ships(No Weapons)", "False"), ("Dont Fire On Seekers(On Others)", "False"),
         ("Break Formation Carriers", "False"), ("Break Formation Colony Ships", "False"),
         ("Break Formation Fighters", "False"), ("Break Formation Satellites", "False"),
         ("Break Formation Planets", "False"), ("Break Formation Transports", "False"),
         ("Fighters Launch Group Amount", 4), ("Damage Percent Per Ship", 100)],
    ])

    settings = [
        ("Maximum Number Of Systems", 160), ("Number Of Space Combat Turns", 30),
        ("Bases Can Join Fleets", "False"), ("Minimum Empire Point Storage", 25000),
        ("Empire Starting Percent Reproduction", 10), ("Population Mass", 5),
        ("Empire Starting Percent Maint Cost", 25),
        ("Number of Quick Start Styles", 1), ("Quick Start Style 1", "Aurel"),
        ("Default Number Of Ships Per Player", 150),
        ("Planet Value Low Percent", 40), ("Planet Value High Percent", 160),
        ("Asteroids Value Low Percent", 100), ("Asteroids Value High Percent", 200),
        ("Plr Planet Value Low Percent", 80), ("Plr Planet Value Medium Percent", 110),
        ("Plr Planet Value High Percent", 140),
        ("Minimum Planet Percent Value", 0), ("Maximum Planet Percent Value", 250),
        ("Planet Value Percent Loss After Owner Death", 10),
        ("Scrap Ship Percent Returned", 30), ("Scrap Unit Percent Returned", 30),
        ("Scrap Facility Percent Returned", 30), ("UnMothball Ship Percent Cost", 20),
    ]
    write_records(data, "Settings.txt", [[(key, value) for key, value in settings]])

    design_types = [
        "Attack Ship", "Defense Ship", "Colony (Rock)", "Colony (Ice)", "Colony (Gas)",
        "Population Transport", "Cargo Transport", "Defense Base", "Base Space Yard",
        "Satellite", "Mine Layer", "Troop Transport", "Space Yard Ship",
    ]
    write_records(data, "DefaultDesignTypes.txt", [[("Name", n)] for n in design_types])
    write_records(data, "DefaultColonyTypes.txt", [[("Name", n)] for n in [
        "Homeworld", "Colony", "Mining World", "Research World", "Industrial World", "Frontier Outpost"
    ]])

    write_list(data, "EmpireNames.txt", [
        "Aurel Stellar Accord", "Dravak Dominion", "Keth Continuum", "Kharel Imperium",
        "Myriad Trade Assembly", "Nyx Protectorate", "Olyss Covenant", "Qorathi Hegemony",
        "Solari Commonwealth", "Teran Union", "Veyran Compact", "Vosk Directorate",
    ])
    write_list(data, "EmpireTypes.txt", [
        "Democratic Republic", "Merchant Republic", "Technocracy", "Industrial Directorate",
        "Military Junta", "Collective", "Imperial Autocracy", "Frontier Compact", "Independent",
    ])
    write_list(data, "EmperorNames.txt", ["Arius", "Vael", "Soryn", "Kara", "Ilyra", "Drex", "Nima", "Orren", "Talia", "Varek"])
    write_list(data, "EmperorTitles.txt", ["Chancellor", "First Speaker", "High Commander", "Archon", "Prime Minister",
                                          "Protector", "Matriarch", "Strategos", "Consul", "Director"])
    write_list(data, "Demeanors.txt", ["Calm", "Aggressive", "Diplomatic", "Cautious", "Expansionist", "Opportunistic"])
    write_list(data, "SystemNames.txt", [
        "Aster", "Borealis", "Cygnus", "Damar", "Erebus", "Fornax", "Gaia", "Helion", "Icarus", "Juno",
        "Kestrel", "Lysithea", "Meridian", "Nadir", "Orpheus", "Perseus", "Quillon", "Rhea", "Sagan", "Tethys",
        "Umbra", "Vesper", "Warden", "Xanthe", "Ymir", "Zephyr", "Altair", "Bellatrix", "Carina", "Deneb",
        "Epsilon", "Fomalhaut", "Gemini", "Hadar", "Izar", "Kepler", "Lacaille", "Mira", "Nashira", "Oberon",
        "Pavo", "Rigel", "Sirius", "Talitha", "Unuk", "Vega", "Wasat", "Zosma",
    ])
    write_list(data, "RepairPriorities.txt", ["Engines", "Weapons", "Shields", "Sensors", "Defence", "Structure"])

    # Twelve original species factions. Their tier-2 and tier-3 presets expose
    # different trait combinations in the native race editor.
    factions = [
        ("Aurel", "Aureli", "Aurel Stellar Accord", "Democratic Republic", "Rock", "Oxygen", "Balanced", "Civic Stability", "Calm", "Deep Vaults", "Industrial Efficiency"),
        ("Dravak", "Dravaki", "Dravak Dominion", "Military Junta", "Ice", "Methane", "Industrial", "Disciplined", "Aggressive", "High Yield Mining", "Fleet Doctrine"),
        ("Keth", "Kethari", "Keth Continuum", "Technocracy", "Gas", "Hydrogen", "Scholarly", "Stoic", "Cautious", "Research Networks", "Neural Logic"),
        ("Kharel", "Khareli", "Kharel Imperium", "Imperial Autocracy", "Rock", "Oxygen", "Martial", "Disciplined", "Aggressive", "Fleet Doctrine", "Reinforced Hulls"),
        ("Myriads", "Myriad", "Myriad Trade Assembly", "Merchant Republic", "Ice", "Methane", "Commercial", "Communal", "Diplomatic", "Trade Houses", "Organic Granaries"),
        ("Nyx", "Nyxian", "Nyx Protectorate", "Technocracy", "Rock", "Oxygen", "Scholarly", "Stoic", "Cautious", "Precision Gunnery", "Deep Vaults"),
        ("Olyss", "Olyssian", "Olyss Covenant", "Democratic Republic", "Rock", "Oxygen", "Balanced", "Communal", "Diplomatic", "Hydroponic Expertise", "Rapid Reproduction"),
        ("Qorathi", "Qorathi", "Qorathi Hegemony", "Industrial Directorate", "Gas", "Hydrogen", "Industrial", "Disciplined", "Expansionist", "Radioactive Casks", "Efficient Maintenance"),
        ("Solari", "Solarian", "Solari Commonwealth", "Military Junta", "Rock", "Oxygen", "Martial", "Civic Stability", "Aggressive", "Fleet Doctrine", "Precision Gunnery"),
        ("Teran", "Teran", "Teran Union", "Frontier Compact", "Rock", "Oxygen", "Balanced", "Civic Stability", "Calm", "Industrial Efficiency", "Research Networks"),
        ("Veyran", "Veyran", "Veyran Compact", "Merchant Republic", "Ice", "Methane", "Commercial", "Stoic", "Diplomatic", "Trade Houses", "Deep Vaults"),
        ("Vosk", "Voski", "Vosk Directorate", "Industrial Directorate", "Gas", "Hydrogen", "Industrial", "Disciplined", "Expansionist", "High Yield Mining", "Radioactive Casks"),
    ]
    first_names = ["Ari", "Bel", "Cyr", "Dara", "Evan", "Fara", "Galen", "Hira", "Iven", "Jora", "Kelan", "Lira"]
    design_names = [
        ["Aegis", "Wayfarer", "Sundiver", "Peregrine", "Crown", "Northstar"],
        ["Ironclad", "Ravager", "Sunder", "Blackwall", "Razor", "Grimward"],
        ["Continuum", "Parallax", "Eventide", "Singularity", "Lattice", "Observer"],
        ["Khan", "Bastion", "Vigil", "Hammer", "Bloodline", "Bulwark"],
        ["Exchange", "Prosperity", "Mercantile", "Caravan", "Ledger", "Fortune"],
        ["Nightfall", "Umbra", "Eclipse", "Phantom", "Spectre", "Wraith"],
        ["Verdant", "Sanctuary", "Lifebloom", "Hearth", "Concord", "Dawn"],
        ["Dominion", "Cauterizer", "Anvil", "Enforcer", "Obsidian", "Judicator"],
        ["Helios", "Radiant", "Corona", "Beacon", "Daybreak", "Zenith"],
        ["Endeavour", "Frontier", "Resolute", "Discovery", "Defiant", "Pioneer"],
        ["Meridian", "Silverline", "Vanguard", "Crosswind", "Seeker", "Longview"],
        ["Dreadnought", "Gravemind", "Harvester", "Sentinel", "Reclaimer", "Oblivion"],
    ]
    for index, faction in enumerate(factions):
        folder, species, empire_name, empire_type, surface, atmosphere, culture, mood, demeanor, trait_a, trait_b = faction
        race_folder = races_dir / folder
        race_folder.mkdir(parents=True, exist_ok=True)
        general = [
            ("Name", species), ("Description", f"The {species} are one of the founding powers of the VOIDREIGN frontier."),
            ("Biological Description", f"{species} physiology is adapted to {surface.lower()} environments."),
            ("Society Description", f"{empire_name} is shaped by {culture.lower()} institutions."),
            ("General History Description", f"{empire_name} expanded beyond its home system during the first interstellar age."),
            ("Empire Name", empire_name), ("Empire Type", empire_type),
            ("Emperor Name", first_names[index]), ("Emperor Title", ["First Speaker", "High Commander", "Prime Mind", "Archon"][index % 4]),
            ("Demeanor", demeanor), ("Culture", culture), ("Happiness Type", mood),
            ("Planet Type", surface), ("Atmosphere", atmosphere),
            ("Design Name File", f"{folder.upper()}.TXT"),
            ("Race Opt 1 Num Characteristics", 1), ("Race Opt 1 Characteristic 1 Type", "Intelligence"),
            ("Race Opt 1 Characteristic 1 Amount", 100), ("Race Opt 1 Num Advanced Traits", 0),
            ("Race Opt 2 Num Characteristics", 1), ("Race Opt 2 Characteristic 1 Type", "Intelligence"),
            ("Race Opt 2 Characteristic 1 Amount", 105), ("Race Opt 2 Num Advanced Traits", 1),
            ("Race Opt 2 Adv Trait 1", trait_a),
            ("Race Opt 3 Num Characteristics", 2), ("Race Opt 3 Characteristic 1 Type", "Intelligence"),
            ("Race Opt 3 Characteristic 1 Amount", 110), ("Race Opt 3 Characteristic 2 Type", "Cunning"),
            ("Race Opt 3 Characteristic 2 Amount", 105), ("Race Opt 3 Num Advanced Traits", 2),
            ("Race Opt 3 Adv Trait 1", trait_a), ("Race Opt 3 Adv Trait 2", trait_b),
        ]
        write_records(race_folder, f"{folder}_AI_General.txt", [general])
        write_records(race_folder, f"{folder}_AI_Settings.txt", [[("Personality Group", index % 5 + 1)]])
        write_list(names_dir, f"{folder.upper()}.TXT", design_names[index])

    # A separate AI style folder is used by the native AI profile resolver.
    write_records(ai_dir, "Adaptive_AI_Settings.txt", [[("Personality Group", 1)]])

    # Neutral powers have their own presets; the native setup screen can
    # include them as independent computer-controlled empires.
    neutral_profiles = [
        ("FreeSystems", "Free Systems", "Free Systems Coalition", "Rock", "Oxygen", "Commercial", "Communal"),
        ("Driftborn", "Driftborn", "Driftborn Clans", "Ice", "Methane", "Balanced", "Stoic"),
        ("Ashen", "Ashen", "Ashen Enclaves", "Gas", "Hydrogen", "Industrial", "Disciplined"),
    ]
    for index, (folder, species, empire_name, surface, atmosphere, culture, mood) in enumerate(neutral_profiles):
        race_folder = neutral_dir / folder
        race_folder.mkdir(parents=True, exist_ok=True)
        general = [
            ("Name", species), ("Description", f"The {species} are independent powers of the frontier."),
            ("Biological Description", f"{species} physiology is adapted to {surface.lower()} environments."),
            ("Society Description", f"{empire_name} is organized around {culture.lower()} institutions."),
            ("General History Description", f"{empire_name} has endured beyond the reach of the major powers."),
            ("Empire Name", empire_name), ("Empire Type", "Independent"),
            ("Emperor Name", first_names[index]), ("Emperor Title", "Speaker"),
            ("Demeanor", "Cautious"), ("Culture", culture), ("Happiness Type", mood),
            ("Planet Type", surface), ("Atmosphere", atmosphere), ("Design Name File", "NEUTRAL.TXT"),
            ("Race Opt 1 Num Characteristics", 1), ("Race Opt 1 Characteristic 1 Type", "Intelligence"),
            ("Race Opt 1 Characteristic 1 Amount", 100), ("Race Opt 1 Num Advanced Traits", 0),
        ]
        write_records(race_folder, f"{folder}_AI_General.txt", [general])
        write_records(race_folder, f"{folder}_AI_Settings.txt", [[("Personality Group", index + 1)]])
    write_list(names_dir, "NEUTRAL.TXT", ["Wayfarer", "Last Light", "Quiet Tide", "Outrider", "Horizon"])

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", type=Path, default=Path("GameData"))
    args = parser.parse_args()
    build(args.output)

if __name__ == "__main__":
    main()

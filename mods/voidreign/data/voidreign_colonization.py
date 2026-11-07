"""VOIDREIGN planetary engineering and colonisation modules."""
AREA = "VoidReign Planetary Engineering"
MODULES = [
    ("VoidReign Rock Colonization Module", "Colonize Planet - Rock", 7410,
     "A sealed landing and biosphere package for rocky worlds."),
    ("VoidReign Ice Colonization Module", "Colonize Planet - Ice", 7411,
     "A thermal and pressure package for icy worlds."),
    ("VoidReign Gas Colonization Module", "Colonize Planet - Gas", 7412,
     "A floating habitat and atmospheric processing package for gas giants."),
]


def tech_area():
    return {
        "name": AREA,
        "set": {
            "Description": "Planetary engineering for establishing permanent settlements beyond the homeworld.",
            "Group": "Expansion",
            "Level Cost": 3500,
            "Maximum Level": 5,
            "Raise Level": 1,
            "Start Level": 0,
            "Can Be Removed": True,
            "Racial Area": 0,
            "Unique Area": 0,
            "Number of Tech Req": 0,
        },
    }


def colonization_module(name, ability, family, description):
    return {
        "name": name,
        "set": {
            "Description": description,
            "Pic Num": 1,
            "Tonnage Space Taken": 70,
            "Tonnage Structure": 40,
            "Cost Minerals": 90,
            "Cost Organics": 80,
            "Cost Radioactives": 10,
            "Vehicle Type": "Ship",
            "General Group": "Colonization",
            "Custom Group": 0,
            "Restrictions": "None",
            "Family": family,
            "Roman Numeral": 1,
            "Supply Amount Used": 0,
            "Number of Tech Req": 1,
            "Weapon Type": "None",
            "Number of Abilities": 1,
        },
        "add": {
            "requirements": [{"Tech Area Req": AREA, "Tech Level Req": 1}],
            "abilities": [{"Ability Type": ability, "Ability Descr": description,
                           "Ability Val 1": 0, "Ability Val 2": 0}],
        },
    }


def generate():
    return {
        "tech_areas": {"add": [tech_area()]},
        "components": {"add": [
            colonization_module(name, ability, family, description)
            for name, ability, family, description in MODULES
        ]},
    }

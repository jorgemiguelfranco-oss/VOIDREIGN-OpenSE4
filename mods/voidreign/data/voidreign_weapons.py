"""VOIDREIGN's first native weapon progression.

The generator returns only deterministic OpenSE4 data patches. Every level is a
real component gated by the corresponding level of VoidReign Energy Weapons.
"""

AREA = "VoidReign Energy Weapons"
LEVELS = 5
ROMAN = ["I", "II", "III", "IV", "V"]
FAMILY = 7401
WEAPON_FAMILY = 7401


def damage_table(level):
    peak = 14 + 6 * level
    reach = 3 + level
    values = []
    for distance in range(1, 21):
        if distance > reach:
            values.append(0)
        else:
            fade = max(0, distance - 2) * 50 // max(1, reach - 2)
            values.append(peak * (100 - fade) // 100)
    return " ".join(str(value) for value in values)


def tech_area():
    return {
        "name": AREA,
        "set": {
            "Description": "Controlled high-energy discharge systems developed for independent fleets and frontier defence.",
            "Group": "Weapons",
            "Level Cost": 3000,
            "Maximum Level": LEVELS,
            "Raise Level": 1,
            "Start Level": 0,
            "Can Be Removed": True,
            "Racial Area": 0,
            "Unique Area": 0,
            "Number of Tech Req": 0,
        },
    }


def pulse_cannon(level):
    name = "VoidReign Pulse Cannon " + ROMAN[level - 1]
    return {
        "name": name,
        "set": {
            "Description": "A compact pulse weapon, technology level {} of {}.".format(level, LEVELS),
            "Pic Num": 1,
            "Tonnage Space Taken": 18 + 3 * level,
            "Tonnage Structure": 10 + 3 * level,
            "Cost Minerals": 28 + 14 * level,
            "Cost Organics": 0,
            "Cost Radioactives": 4 * level,
            "Vehicle Type": "Ship\\Base\\Sat\\WeapPlat",
            "General Group": "Weapons",
            "Custom Group": 0,
            "Restrictions": "None",
            "Family": FAMILY,
            "Roman Numeral": level,
            "Weapon Type": "Direct Fire",
            "Weapon Damage At Rng": damage_table(level),
            "Weapon Target": "Ships\\Planets",
            "Weapon Modifier": 2 * (level - 1),
            "Weapon Reload Rate": 1,
            "Weapon Family": WEAPON_FAMILY,
            "Weapon Damage Type": "Normal",
            "Weapon Display": 4,
            "Weapon Display Type": "Beam",
            "Weapon Seeker Dmg Res": 0,
            "Weapon Seeker Speed": 0,
            "Supply Amount Used": 1,
            "Number of Abilities": 0,
        },
        "add": {"requirements": [{"Tech Area Req": AREA, "Tech Level Req": level}]},
    }


def generate():
    return {
        "tech_areas": {"add": [tech_area()]},
        "components": {"add": [pulse_cannon(level) for level in range(1, LEVELS + 1)]},
    }

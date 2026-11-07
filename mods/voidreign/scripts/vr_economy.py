"""VOIDREIGN treasury storage.

OpenSE4 keeps the treasury empire-wide. This layer adds a hard capacity supplied by
warehouse facilities across the empire's colonies. Overflow is discarded at the end
of the income step, so an expanding economy must build logistics infrastructure.
"""

from opense4 import rules

CAPACITY_ABILITY = "VoidReign Warehouse Capacity"
WAREHOUSE = "VoidReign Warehouse"


@rules.on("after_galaxy")
def seed_homeworld_warehouses(game, fx):
    """Give every starting empire one basic warehouse when its capital has room."""
    warehouse = game.rules.facility_named(WAREHOUSE)
    if warehouse is None:
        return
    for empire in game.empires:
        home = next((c for c in game.colonies if c.owner == empire.id and c.homeworld), None)
        if home is None:
            continue
        facilities = home.facilities or []
        slots = home.facility_slots or 0
        if warehouse.id not in facilities and len(facilities) < slots:
            fx.add_facility(home, warehouse.id)
            fx.log(empire, "A VoidReign Warehouse is commissioned on the homeworld. Treasury capacity is now available.",
                   title="Logistics established", category="economy")


@rules.on("empire_end_of_turn", step="income", when="after")
def enforce_warehouse_capacity(game, empire, step, when, fx):
    """Discard treasury overflow after all connected colony income has arrived."""
    capacity = 0
    for colony in game.colonies:
        if colony.owner != empire.id:
            continue
        for facility_id in colony.facilities or []:
            capacity += game.ability(facility_id, CAPACITY_ABILITY, "facility")
    stored = empire.stored
    if stored is None:
        return
    overflow = {
        "minerals": max(0, stored.minerals - capacity),
        "organics": max(0, stored.organics - capacity),
        "radioactives": max(0, stored.radioactives - capacity),
    }
    if not any(overflow.values()):
        return
    fx.add_resources(empire, minerals=-overflow["minerals"],
                     organics=-overflow["organics"],
                     radioactives=-overflow["radioactives"])
    lost = sum(overflow.values())
    fx.log(empire,
           "Warehouse capacity exceeded. Lost {} minerals, {} organics and {} radioactives. Build more warehouses to protect future production.".format(
               overflow["minerals"], overflow["organics"], overflow["radioactives"]),
           title="Treasury overflow", category="economy")
    empire.mod_data["warehouse_overflow_total"] = empire.mod_data.get("warehouse_overflow_total", 0) + lost

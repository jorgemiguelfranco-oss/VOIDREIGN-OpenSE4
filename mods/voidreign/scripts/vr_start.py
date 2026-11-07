"""VOIDREIGN starting logistics infrastructure.

Storage limits are handled by OpenSE4's native Resource Storage abilities on the
VoidReign Warehouse facility. This hook gives each starting capital one warehouse
when the homeworld has a free facility slot; later colonies can build more.
"""
from opense4 import rules

WAREHOUSE = "VoidReign Warehouse"


@rules.on("after_galaxy")
def seed_homeworld_warehouses(game, fx):
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
            fx.add_facility(home, warehouse)
            fx.log(empire,
                   "A VoidReign Warehouse is commissioned on the homeworld. Build additional warehouses to expand resource storage.",
                   title="Logistics established", category="economy")

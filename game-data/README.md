# VOIDREIGN native game data

This directory is the game's own base ruleset and content, not a mod. It is loaded directly by the game executable and is not layered over a Space Empires IV installation. VOIDREIGN uses the OpenSE4 codebase as its engine foundation while defining its own factions, ships, research, economy and galaxy content here.

The Windows installer ships this directory beside the executable. Players do not need Space Empires IV Deluxe or a separate mod activation step.

## Core starting economy

Strategic-resource storage is warehouse-dependent: the native rules set the empire's
unassisted storage floor to zero. Each VoidReign Warehouse adds 30,000 units of
minerals, organics and radioactives to the shared empire-wide treasury capacity.
Every starting homeworld receives one warehouse so the opening reserve can be
carried between turns; additional colonies need warehouses to expand that limit.

## Opening patrol

Each new empire receives one native Attack Ship designed from its starting
technology and a Pathfinder hull. The roster also includes Hauler, Frigate, Destroyer, Cruiser, Battleship, Settlement Ark and Orbital Station hulls, with the combat line gated by propulsion research. The ship is placed at the homeworld and
assigned to a one-ship **Home Patrol** fleet, ready for the player to rename,
expand and issue movement orders. The starting count is controlled by
`VOIDREIGN Starting Attack Ship Count`.

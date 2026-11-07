# VOIDREIGN native game data

This directory is the game's own base ruleset and content, not a mod. It is loaded directly by the game executable and is not layered over a Space Empires IV installation. VOIDREIGN uses the OpenSE4 codebase as its engine foundation while defining its own factions, ships, research, economy and galaxy content here.

The Windows installer ships this directory beside the executable. Players do not need Space Empires IV Deluxe or a separate mod activation step.

## Core starting economy

Strategic-resource storage is warehouse-dependent: the native rules set the empire's
unassisted storage floor to zero. Each VoidReign Warehouse adds 30,000 units of
minerals, organics and radioactives to the shared empire-wide treasury capacity.
Every starting homeworld receives one warehouse so the opening reserve can be
carried between turns; additional colonies need warehouses to expand that limit.

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

## Research upgrade ladder

The native technology areas unlock tangible upgrades, not only larger hulls. Energy Weapons now has a complete five-level combat ladder: Pulse Cannon and Shield Projector tiers I–V, with higher tiers gated by the matching research level, increasing tonnage and supply demands, and stronger damage or shield output:

- **Propulsion III–V:** Vector Drive II–IV, increasing strategic movement from two to four units per engine as the empire progresses.
- **Energy Weapons II–V:** Pulse Cannon II–V and Shield Projector II–V, progressively increasing weapon damage, shield points, component tonnage, construction cost and supply use.
- **Industrial Engineering II:** Mineral Extractor II, Hydroponics II and Isotope Reactor II.
- **Industrial Engineering III:** Research Institute II and Orbital Shipyard II.
- **Industrial Engineering IV:** Planetary Shipyard II.
- **Logistics II–V:** Cargo Hold II–V progressively increases ship cargo from 120 to 500 units. Warehouse II–IV unlock at Logistics II, IV and V and add 60,000, 90,000 and 120,000 units of capacity per strategic resource, respectively.
- **Logistics III:** Supply Depot II.
- **Advanced Sensors I:** Sensor Suite I; **II:** Sensor Array II and Intelligence Bureau II; **III:** Sensor Suite II.

The upgraded facilities share a family with their earlier versions, so the game treats
them as the next tier rather than unrelated buildings. Costs and unlock requirements
are defined in the native Data/Components.txt, Data/Facility.txt and Data/TechArea.txt
tables.

## Native computer-player profiles

Each faction has its own `AI_Research`, `AI_Fleets` and `AI_Settings` tables.
The Aurelian profile prioritises sensors and defensive fleet allocation; the
Veyran profile prioritises logistics and industrial development; and the
Khepri profile accelerates industrial, propulsion and weapons research with
a more attack-oriented fleet allocation. These files feed the engine's built-in
computer player and do not require a separately installed AI mod.

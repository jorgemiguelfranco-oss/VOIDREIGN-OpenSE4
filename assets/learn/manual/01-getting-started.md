---
windows: game-menu, save-game, load-game, learn
---
# Getting started

**VOIDREIGN is a standalone 4X space strategy game.** It includes its own factions, ships,
technology, facilities, computer-player profiles and galaxy rules. You do not need Space
Empires IV Deluxe, Steam, an external data folder or a separate mod installation.

This chapter shows you how to begin a game, develop your home system and manage saved games.

## The title screen

| Button | What it does |
|---|---|
| `Quick Start` | Choose a native faction and begin with standard galaxy settings. |
| `New Game` | Configure the galaxy, empires, technology, turn style and victory conditions. |
| `Resume Game` | Continue the game saved most recently on this computer. |
| `Load Game` | Choose a saved game. |
| `Tutorial` | Open the guided lessons. |
| `Scenario` | Open optional training scenarios when any are installed. |
| `Credits` | See who made VOIDREIGN and the technology it is built with. |
| `Quit Game` | Leave VOIDREIGN. |

At the top right, `Multiplayer` hosts or joins a network game, or plays a turn of a
play-by-email game (see [Multiplayer](multiplayer)). `Settings` controls graphics,
sound, files and controls (see [Settings](settings)); `Mods` manages optional
extensions; and `Manual` opens this guide.

## Choose your faction

VOIDREIGN currently includes three native empires:

- **Aurelian Concord** — a cautious, sensor-focused faction that favours science and defensive fleet allocation.
- **Veyran Trade League** — a logistics and industry-focused faction with a balanced fleet doctrine.
- **Khepri Ascendancy** — an industrial and military faction with a more aggressive fleet doctrine.

Each faction has its own culture, names, racial traits and computer-player research and fleet
profiles. The built-in AI uses these profiles; you do not need to install or enable an AI mod
to play against the native empires.

## Quick Start

Quick Start is the fastest way into a game. Select a faction from the list, review its
description and press `Begin Game`. The game creates a procedurally generated galaxy with
standard settings and computer-controlled rivals.

Every empire starts with a homeworld and a **Home Patrol** fleet containing one Pathfinder
Attack Ship. The homeworld receives the core infrastructure for an opening economy:

- a **VoidReign Spaceport** for logistics and commerce;
- a **VoidReign Planetary Shipyard** for building ships and bases;
- a **VoidReign Supply Depot** for fleet resupply;
- a **VoidReign Warehouse** that stores up to 30,000 minerals, organics and radioactives.

The homeworld also starts with resource extraction and research facilities. Select the Home
Patrol in the system view to inspect it and issue orders. You can rename the fleet, add ships
to it, split it or send it to another sector.

The warehouse is important. Strategic resources cannot be banked without warehouse capacity:
without a warehouse, the storage limit is zero and unbanked resources are lost at the end of
the turn. Warehouses on your colonies add to the same empire-wide capacity. Build or upgrade
them before your treasury repeatedly reaches its limit (see [Economy](economy#storage)).

## New Game

New Game opens **Game Setup**. Choose the settings that shape your galaxy and the way the
empires play, then press `Begin Game`.

| Page | What you set there |
|---|---|
| Quadrant | Galaxy type and size, warp points, exploration and resource settings. |
| Events | Whether random events occur and how severe they may be. |
| Technology | Starting technology, research cost and which technology areas are allowed. |
| Player Settings | Starting resources, homeworld value, racial points and empire placement. |
| Players | Add, edit or remove empires; choose Human or Computer for each one. |
| Victory Conditions | Optional conditions that can end the game. |
| Game Settings | Diplomacy, colonisation limits, saving the map and empire limits. |
| Mechanics | Turn style, tactical or strategic combat and autosave. |

For a first game, use a small or medium galaxy, keep the default turn-based rules and leave
victory conditions off until you have learned the systems.

### Designing your own empire

On the Players page, `Add New` opens **Empire Setup**, where you can name and customise an
empire. Set its atmosphere and homeworld type, choose a culture, spend racial points on
characteristics and advanced traits, and write its description. You can save an empire to
a file for later games or load an existing empire.

A race's homeworld type and traits affect its growth, production and colonisation options.
The racial-points total is shown while you edit; the game explains when a selection is over
budget or otherwise invalid.

### Computer players and optional extensions

The Aurelian, Veyran and Khepri empires already have native computer-player profiles. They
prioritise different research areas and allocate their fleets differently. The built-in
computer player can run a complete game without any additional AI package.

Optional third-party AI or gameplay extensions can still be installed through the Mods
window. They are add-ons, not a requirement for the native factions or their computer
players. When an extension is unavailable or fails, the built-in computer player can take
over so the game can continue.

## Saving and loading

Press `F2` (or the Game Menu command button) to open the [Game Menu](window:game-menu):

| Button | What it does |
|---|---|
| `New` | Leave the current game and return to the title screen. |
| `Load` | Open a saved game. |
| `Save Game` | Save the current game. |
| `Save Map` | Save the galaxy map when map saving is enabled in Game Setup. |
| `Save Empire` | Save your empire, race, minister style and optionally its designs for later games. |
| `Players` | Show which empires are controlled by computer players. |
| `Options` | Change options for the current computer. |
| `Delete Game` | Remove a saved game. |
| `Quit` | Leave VOIDREIGN. |
| `Close` | Close the menu. |

Autosave can be enabled in Game Setup or in the current game's Options. It keeps a rolling
set of recent turns, so you can return to an earlier point if needed.

Saved games, maps, empires, settings, mods and logs live in your user folder, not in
Program Files:

| System | Folder |
|---|---|
| Windows | `%APPDATA%\VOIDREIGN\` |
| Linux | `$XDG_DATA_HOME/VOIDREIGN/`, or `~/.local/share/VOIDREIGN/` |
| macOS | `~/Library/Application Support/VOIDREIGN/` |

A portable ZIP copy can instead keep its personal files in a `userdata/` folder beside
`VOIDREIGN.exe`. See [Settings, Files](settings#files) and the distribution's docs/SETUP.md guide.

## Learning the game

The **Learn** window gathers the tutorials, training material and this manual. Use the
title screen's `Tutorial` or `Manual` button, or open Learn from the Game Menu.

- **Tutorials** are guided lessons. A panel explains each step, highlights the relevant
  controls and moves on when you complete the action.
- **Training scenarios**, when installed, are practice games with their own objectives.
- The **manual** explains the windows and game systems. Its contents tree, search box and
  links help you find the relevant section.

There is no required campaign to play the sandbox 4X game. Start a new galaxy, expand your
empire, research technology, build fleets and pursue the victory conditions you choose.

## Your first turns

A practical opening plan:

1. Select the Home Patrol in your home system and inspect its Attack Ship.
2. Check the homeworld's facilities, treasury and warehouse capacity. Add warehouses as
   your economy grows so that production is not lost to storage overflow.
3. Open Research (`F8`). Stellar Sciences supports the other technology areas; then plan
   the propulsion, weapons, industrial, logistics and sensor upgrades that fit your strategy.
4. Keep the Planetary Shipyard's construction queue busy. Build additional scouts, combat
   ships and colony ships when their hulls and colonisation modules become available.
5. Send the Home Patrol to explore nearby sectors. Use Move To (`M`) to set a destination,
   and use waypoints to organise longer routes.
6. Research Planetary Engineering to unlock colonisation modules for suitable worlds.
   Protect colony ships and establish new settlements where their resources and location
   support your economy.
7. Build orbital bases at your shipyards. A Base Space Yard on an Orbital Station can add
   construction capacity in an important system.
8. End the turn with `F12`, review the Log and adjust your research, construction and fleet
   orders as the galaxy develops.

The [Main Window](main-window) chapter explains the system and galaxy views, and
[Turns](turns) explains what happens when you end a turn.

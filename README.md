# VOIDREIGN

**A standalone 4X space strategy game built on the OpenSE4 C++23 engine.**

VoidReign is the default game launched by the client. Its native game rules and content live in `content/voidreign/` and are loaded directly by the existing simulation, galaxy model, ship designer, command system, turn processor and save system. VoidReign is **not a mod** and does not require a copy of Space Empires IV to play.

The OpenSE4 codebase is being evolved into VoidReign's engine foundation. The original engine's clean-room implementation and optional legacy compatibility path remain available, but classic-mode parity is not treated as completion of VoidReign features.

## Current game foundation

The standalone profile currently includes:

- Native rules and galaxy-generation tables in `content/voidreign/Data/`.
- Two original playable species presets: Helion Concord and Veyran Collective.
- A starting Pathfinder exploration/escort ship and a species-matched Rock or Ice colonizer for each human or computer empire.
- A starting orbital station in a separate sector of each home system, equipped with a real Space Yard module, sensors and defensive systems.
- Native ship components, an initial pulse weapon, propulsion, three planetary colonization modules, resource extraction and research facilities.
- Warehouse-based resource storage: there is no free empire-wide resource capacity. Resource stockpiles are limited by actual colony warehouses; overflow is lost when production exceeds storage.
- Original transparent ship and station sprites and a VoidReign Windows application icon.

This is an **early engine/content foundation, not a finished playable release**. Full interface redesign, complete faction rosters and AI profiles, ship/technology progression, diplomacy and events, deeper economy balancing, original art sets, save/reload and multiplayer verification, and Windows release testing remain in development.

There is no campaign mode planned. The target is a complete sandbox 4X game.

## Running the game

A development build looks for the native content at `content/voidreign/` in the source tree. Installed builds ship it beside the executable.

```sh
cmake --preset debug
cmake --build --preset debug
./build/debug/opense4
```

The game starts in VoidReign mode by default. To use another VoidReign content root:

```sh
opense4 --voidreign-dir=/path/to/voidreign
```

The old OpenSE4 compatibility mode is explicit and optional:

```sh
opense4 --classic-dir=/path/to/SpaceEmpiresIV
```

That mode reads a player's own classic game data in place. Nothing from Space Empires IV is distributed with VoidReign.

## Building and validation

See [docs/BUILDING.md](docs/BUILDING.md) for compiler and dependency requirements. The repository's CMake build includes the engine test suite. The current standalone VoidReign ruleset and new-game tests have been added, but this branch has not yet produced a confirmed CI run or a successful local build; compilation and runtime validation are still outstanding.

The Windows and Linux release pipeline is based on `tools/package_release.sh`. Release staging now includes `content/voidreign/`; the Windows installer installs and uninstalls that content beside the game executable. Release packages are named `VoidReign-<version>-<platform>-<architecture>`.

## Project structure

- `src/game/` — deterministic simulation, economy, research, ship design, movement, combat and turn processing.
- `src/client/` — game client and existing interface framework.
- `content/voidreign/Data/` — native VoidReign rules and galaxy data.
- `content/voidreign/Pictures/` — VoidReign species presets and original game art.
- `packaging/` — desktop metadata, application icons and Windows installer.

The engine architecture is described in [docs/ENGINE.md](docs/ENGINE.md). The standalone content bundle has its own notes in [content/voidreign/README.md](content/voidreign/README.md).

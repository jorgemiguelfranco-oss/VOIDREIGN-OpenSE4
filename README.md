# VOIDREIGN

**A standalone 4X space strategy game built on the OpenSE4 engine architecture.**

VOIDREIGN is its own game. Its executable loads the native rules and original game content from `game-data/` beside the program. It does not require Space Empires IV Deluxe, Steam, or a separate mod installation.

The engine foundation supplies a deterministic turn-based strategy simulation, galaxy and system views, fleet movement, ship design, construction, research, diplomacy, intelligence, tactical and strategic combat, saves, multiplayer infrastructure and a moddable AI interface. VOIDREIGN defines the game played on that foundation: its own technology, hulls, components, facilities, factions, economy and galaxy definitions.

## Current VOIDREIGN content

The native `game-data/` directory currently defines:

- **Three original factions:** the Aurelian Concord, Veyran Trade League and Khepri Ascendancy, with distinct cultures, leaders, naming lists, research priorities and fleet doctrines.
- **Original technology branches:** Stellar Sciences, Propulsion, Energy Weapons, Industrial Engineering, Planetary Engineering, Logistics and Advanced Sensors.
- **Research-backed upgrade tiers:** level-II drives, pulse weapons, shields, cargo holds, sensors, extraction facilities, research institutes, intelligence bureaus, orbital shipyards, planetary shipyards, supply depots and warehouses, gated by their relevant technology areas.
- **Original ships and installations:** Pathfinder scout, Hauler cargo hull, Frigate, research-gated Destroyer, Cruiser and Battleship, Settlement Ark colony ship and Orbital Station. The native hull progression is backed by original ship systems, engines, cargo, pulse weapons, shields, colonisation modules, orbital shipyards and sensors. Each new empire begins with a designed Pathfinder Attack Ship grouped into its own Home Patrol fleet.
- **Planetary infrastructure:** mineral extraction, hydroponics, isotope refining, research, intelligence, spaceports and bonded warehouses.
- **Warehouse-dependent economy:** without a warehouse anywhere in the empire, strategic-resource storage is zero. Each VoidReign Warehouse adds 30,000 minerals, organics and radioactives to the shared empire-wide capacity; Warehouse II adds 60,000 of each. Every starting homeworld receives one first-tier warehouse for a 30,000-unit opening capacity. Overflow is permanently discarded at end of turn, while a sustained inability to meet maintenance can cost ships.
- **Original galaxy definitions:** VoidReign Core and Nebula systems, Spiral and Frontier quadrants, stellar anomalies and fleet formation data.

The game data is authored as the engine's **base ruleset**, not as `mods/voidreign`. The former VoidReign mod directory has been removed. The optional engine computer-player modules remain separate from the game itself.

## Windows installer

The Windows release workflow is configured to build a self-contained x64 package and an NSIS setup executable. A verified installer artifact is not available yet; the workflow and native gameplay checks still need to run successfully:

- `VOIDREIGN.exe` — the player-facing game executable.
- `game-data/` — the native VOIDREIGN rules and faction definitions.
- Initial original art for the Pathfinder and Orbital Station; several other hulls still reuse placeholder Pathfinder art and need dedicated final artwork.
- Runtime engine utilities, documentation, license and third-party notices.
- Start Menu and optional desktop shortcuts, uninstall entry and uninstaller.

The installer is intended to work on 64-bit Windows 7 SP1 through Windows 11, subject to the graphics-driver requirements of the engine. The player does not need to install a separate commercial game.

For normal installation, see [Installing and setting up VOIDREIGN](docs/SETUP.md). The guide covers the Windows setup, saves, user settings, portable ZIP copies and troubleshooting.

## Building from source

Requirements: a C++23 compiler, CMake 3.25 or newer, Ninja, SDL3 (fetched by CMake when not installed), Vulkan headers and `glslc` from the Vulkan SDK or shaderc.

On Windows, install Visual Studio 2022/2026 with **Desktop development with C++**, plus the Vulkan SDK. From an x64 Native Tools Command Prompt:

```bat
cmake --preset release
cmake --build --preset release
build\release\VOIDREIGN.exe
```

CMake also stages `game-data/` beside the built executable. For data-authoring work, an alternative base data directory can be selected with `--data-dir=DIR`.

The redistributable Windows package is built by the repository's release script on a Linux build host with the pinned llvm-mingw toolchain, NSIS and Wine:

```sh
tools/package_release.sh windows
```

The resulting files are written to `dist/`.

## Validation

The CI configuration is set up to run the engine unit tests, Windows executable-import checks, native-data validation and installed-game smoke tests. The Windows installer job also checks shortcuts and registry entries, exercises native faction starts, fleet control, construction, save/load and AI turns, and verifies that uninstalling the program leaves per-user saves intact.

GitHub Actions has not yet reported a run for this branch, so none of those checks can be marked as passing and no verified installer artifact is available yet. A successful installer build alone would not mean every planned VOIDREIGN subsystem is complete: mechanics, art, balance and gameplay still need to be implemented and tested.

## Project structure

- `src/` — the OpenSE4-derived engine and client code, adapted for VOIDREIGN.
- `game-data/` — VOIDREIGN's native base game data and original content.
- `assets/` — engine-owned fonts, UI and support assets.
- `packaging/windows/` — Windows installer resources and NSIS script.
- `.github/workflows/` — cross-platform CI and Windows installer validation.

## Licensing

The engine code is distributed under the GNU GPL version 3 or later. Third-party components and fonts retain their respective licenses; see `LICENSE` and `THIRD_PARTY_NOTICES.txt` in a packaged build. VOIDREIGN's original game-data files and artwork are maintained in this repository. No proprietary Space Empires IV game files are required or included.

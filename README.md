# VOIDREIGN

**A standalone 4X space strategy game built on the OpenSE4 engine architecture.**

VOIDREIGN is its own game. Its executable loads the native rules and original game content from `game-data/` beside the program. It does not require Space Empires IV Deluxe, Steam, or a separate mod installation.

The engine foundation supplies a deterministic turn-based strategy simulation, galaxy and system views, fleet movement, ship design, construction, research, diplomacy, intelligence, tactical and strategic combat, saves, multiplayer infrastructure and a moddable AI interface. VOIDREIGN defines the game played on that foundation: its own technology, hulls, components, facilities, factions, economy and galaxy definitions.

## Current VOIDREIGN content

The native `game-data/` directory defines the actual game rules and starting content:

- **Six original factions:** Aurelian Concord, Veyran Trade League, Khepri Ascendancy, Meridian Assembly, Outer Systems Compact and Helion Directorate. Each has its own culture, names, research priorities, fleet doctrine and computer-player personality.
- **Twenty starting origins plus No Origin:** each background contributes two characteristic bonuses, a trade-off and, for selected origins, founding reserves or additional starting assets. The choice persists in empire files and saved games; AI origins are seed-deterministic. See [Starting Origins](docs/STARTING_ORIGINS.md).
- **A native officer/leader system:** recruitable leaders with roles, rarity, traits, experience and progression; governors can be assigned to colonies, admirals to fleets, and leader records are saved with the empire. Leadership is enabled by the VOIDREIGN ruleset rather than imposed on generic engine scenarios.
- **Original technology branches:** Stellar Sciences, Propulsion, Energy Weapons, Industrial Engineering, Planetary Engineering, Logistics and Advanced Sensors, with research-gated upgrades for drives, weapons, shields, cargo, sensors, facilities, shipyards, supply and storage.
- **Twelve native hull classes:** Pathfinder, Hauler, Frigate, Destroyer, Cruiser, Battleship, Settlement Ark, Orbital Station, Corvette, Science Vessel, Dreadnought and Mobile Shipyard, supported by native components, designs and fleet roles.
- **Planetary infrastructure and logistics:** extraction, hydroponics, isotope refining, research, intelligence, spaceports, planetary shipyards, orbital shipyards, supply depots and warehouses.
- **Warehouse-dependent strategic-resource economy:** without warehouse capacity, strategic resources cannot be stockpiled. The empire shares capacity across its warehouses; end-of-turn overflow is discarded, and sustained maintenance shortfalls can cause ships to be lost.
- **Original galaxy definitions:** VoidReign Core and Nebula systems, Spiral and Frontier quadrants, stellar anomalies and fleet formation data.

The game data is authored as the engine's **native base ruleset**, not as `mods/voidreign`. VOIDREIGN is a standalone game built on the OpenSE4-derived C++ engine and does not require the original commercial game or a separate mod installation. The package also includes the engine's optional computer-player modules and SDK tools.

## Windows installer

The native Windows x64 package is built from the C++ game and its base `game-data/` ruleset. The current locally verified development artifacts are:

- `dist/VOIDREIGN-0.1.0-2cba5ea-dirty-windows-x86_64-setup.exe` — NSIS installer.
- `dist/VOIDREIGN-0.1.0-2cba5ea-dirty-windows-x86_64.zip` — portable package.
- `dist/VOIDREIGN-0.1.0-2cba5ea-dirty-SHA256SUMS.txt` — SHA-256 checksums.

The package includes `VOIDREIGN.exe`, the six native faction data sets, twelve hull classes, native pictures and atlases, SDK tools and documentation, bundled engine utilities and third-party notices. Its installer has been installed into a clean directory and the installed game has been launched successfully. The native-data checker reports zero errors, zero warnings and zero unread fields. Windows 7 SP1 import checks pass for the game, server, data checker, converter, SDK and test executables. The complete native test suite passes 1,666 cases and 566,251 assertions, with one opt-in test skipped.

The picture conversion is documented in `game-data/Pictures/ART-PROVENANCE.md`. All six factions have native picture sets and hull miniatures/portraits for the twelve VOIDREIGN hull classes. Some faction race portraits are palette adaptations of five original portrait masters rather than six fully distinct species paintings; additional commissioned/generated species portraits and a full in-game art review remain desirable.

This is a local development package built from a modified working tree (`0.1.0-2cba5ea-dirty`), not a clean tagged public release. The current package does not include a soundtrack or sound-effects bank. The installer is intended to work on 64-bit Windows 7 SP1 through Windows 11, subject to graphics-driver requirements. The player does not need a separate commercial game.

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

The current local Windows validation on the development laptop has completed the full native C++ test suite: **1,666 test cases, 566,251 assertions passed, zero failures and one skipped opt-in case**. The release package is rebuilt and its installer, launch and uninstall behaviour are checked separately; a package build is not treated as a substitute for gameplay tests or a visual review. The native game currently has no bundled soundtrack or sound-effects bank, and visual balance and presentation still merit continued playtesting.

## Project structure

- `src/` — the OpenSE4-derived engine and client code, adapted for VOIDREIGN.
- `game-data/` — VOIDREIGN's native base game data and original content.
- `assets/` — engine-owned fonts, UI and support assets.
- `packaging/windows/` — Windows installer resources and NSIS script.
- `.github/workflows/` — cross-platform CI and Windows installer validation.

## Licensing

The engine code is distributed under the GNU GPL version 3 or later. Third-party components and fonts retain their respective licenses; see `LICENSE` and `THIRD_PARTY_NOTICES.txt` in a packaged build. VOIDREIGN's original game-data files and artwork are maintained in this repository. No proprietary Space Empires IV game files are required or included.

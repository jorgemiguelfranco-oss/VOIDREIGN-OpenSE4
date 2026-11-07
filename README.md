# VOIDREIGN

**A standalone 4X space strategy game built on the OpenSE4 C++23 engine.**

VoidReign is the default game launched by the client. It is a native game profile built directly into the existing OpenSE4 engine and simulation. Its own rules, species, ships, facilities, technologies and art live under `content/voidreign/`. It is **not a mod** and does not require Space Empires IV or any other commercial game installation.

The OpenSE4 engine is the software foundation: deterministic game state and turn processing, galaxy/system model, movement and combat, ship design and validation, construction queues, economy and research, AI, save/load, multiplayer and the client framework. VoidReign is being developed by integrating original game content and product behavior into those engine systems, not by building a parallel simulation.

## Current native game implementation

The branch currently includes:

- A native VoidReign content bundle with Helion and Veyran species presets, galaxy generation, starting technologies, facilities, components and ship classes.
- A capital start with a Pathfinder exploration/escort ship and a species-matched Rock, Ice or Gas colonizer.
- A named expeditionary fleet created through the engine's normal fleet command and validation path.
- A separate orbital station in a vacant home-system sector, equipped with an actual Space Yard, sensors and defensive systems.
- Warehouse-limited storage for minerals, organics and radioactives. Resource production does not create unlimited stockpile capacity; overflow above the empire's real warehouse capacity is lost.
- Native Frigate, Destroyer, Cruiser, Battleship, Carrier and Interceptor hulls, with design categories and technology gates.
- A real carrier fighter bay using the engine's Launch/Recover Fighters ability, plus a buildable interceptor fighter design.
- Original race-generic ship miniatures for the Pathfinder, Colonizer, Orbital Station and the six additional ship classes, installed at the filenames used by the engine's art resolver.
- A VoidReign-branded Windows application icon and installer configuration.

This is still an **in-development game foundation, not a finished playable 0.2.0 release**. The full VoidReign interface and screen flow, broader species/faction content and computer-player profiles, more weapon and component tiers, events and diplomacy, economic/technology balance, remaining planet/system/facility/ship artwork, and end-to-end gameplay validation remain to be completed. No campaign mode is planned; the target is a complete sandbox 4X game.

## Build and run

A development build loads the native content from `content/voidreign/` in the source tree. Installed packages ship the content beside the executable.

```sh
cmake --preset debug
cmake --build --preset debug
./build/debug/opense4
```

VoidReign is the default profile. To use a different native VoidReign content root:

```sh
opense4 --voidreign-dir=/path/to/voidreign
```

The optional legacy compatibility path is explicitly selected and is not part of the VoidReign product requirement:

```sh
opense4 --classic-dir=/path/to/SpaceEmpiresIV
```

That mode reads a player's own classic installation in place. No Space Empires IV game data, artwork, sound or text is distributed with VoidReign.

## Testing and release status

The repository contains the native ruleset and new-game regression tests, including two-species start validation, warehouse capacity, initial ship/fleet/station composition, carrier bay capacity and interceptor design validation. The branch has not yet produced a recorded successful GitHub Actions run or a verified local build/runtime session in this development environment. Compilation, test execution, clean Windows installation, game launch, representative turn processing, save/reload and installer verification remain release gates.

Windows packaging is configured in `tools/package_release.sh` and `packaging/windows/`. A configured installer is not the same as a validated installer: no Windows setup executable is claimed as tested or ready until a clean install and launch have been demonstrated.

## Code and content map

- `src/game/` — deterministic simulation, economy, research, ship design, movement, combat, commands and turn processing.
- `src/client/` — application, rendering and game interface.
- `content/voidreign/Data/` — native VoidReign rules, technologies, components, hulls and galaxy data.
- `content/voidreign/Pictures/` — original race and ship artwork.
- `packaging/` — desktop metadata, application icon and installer configuration.
- `docs/ENGINE.md` — engine architecture.


# VOIDREIGN — OpenSE4 game layer

VOIDREIGN is being built **on the OpenSE4 engine**, not as a second renderer or a parallel simulation. OpenSE4 supplies the tested Space Empires IV rules, ship designer, galaxy/system views, turn processing, saves, combat, multiplayer foundation and mod SDK. This mod supplies VOIDREIGN's original content and game rules.

## Current implementation

- Native OpenSE4 mod manifest and data-patch structure.
- Original, buildable VoidReign Pathfinder hull.
- VoidReign Cargo Rack component, using the engine's real cargo-storage ability.
- Automated SDK tests verify the hull, component and a legal starting design.

## Design constraints

- No campaign mode.
- No voice acting or voiced dialogue.
- Preserve OpenSE4's native system view, ship designer, fleet controls and turn flow.
- Add VoidReign systems through supported data patches, rules hooks, AI modules and interface extensions.
- Keep all game-affecting rules deterministic and mod data compatible with OpenSE4's save/network identity rules.
- Do not copy original Space Empires IV assets or data; players provide their own licensed game installation.

## Development

Run from the OpenSE4 source checkout:

```sh
opense4-sdk check mods/voidreign
opense4-sdk test mods/voidreign
opense4-sdk run mods/voidreign -- --quick-start=Terran
```

The mod is deliberately incremental: each feature must pass the SDK's data validation and gameplay tests before being treated as implemented. The private TypeScript VOIDREIGN prototype is a source of design/content requirements, not a replacement for this native engine branch.

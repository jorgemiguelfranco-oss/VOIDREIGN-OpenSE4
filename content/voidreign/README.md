# VOIDREIGN standalone game content

This directory is the first-party VoidReign content bundle. The OpenSE4 engine loads these rules and species directly; this is **not a mod** and the content must not be moved under `mods/`.

## Development launch

```sh
opense4 --voidreign-dir=content/voidreign
```

VoidReign is the default client game. When no directory is supplied, development builds search this source-tree directory. Installed builds look beside the executable under `content/voidreign`.

The first ruleset contains authored technology, hull, component, facility, economy, galaxy-generation and species-preset data. The Helion Concord and Veyran Collective are the initial species. Their original artwork, complete faction rosters, advanced ship designs, AI profiles, diplomacy/event content and expanded technology progression are still under development. The presence of data files is not proof of a playable release.

The standalone profile disables classic mod loading and applies VoidReign's native storage rules. It does not require a Space Empires IV installation for its own rules data. The legacy `--classic-dir` path remains available for OpenSE4 compatibility and engine development.

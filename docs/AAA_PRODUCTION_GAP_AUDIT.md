# VOIDREIGN — Native PC AAA-style Production Gap Audit

**Audit date:** 2026-11-09
**Product:** standalone Windows x64 C++/CMake game derived from the OpenSE4 engine architecture, **not** the Electron prototype and **not** a mod.
**Primary integration branch:** `voidreign/opense4-core`; PR #2.
**Target machine:** authorised Windows laptop, 8 GiB RAM; avoid heavy parallel compilation.
**Evidence policy:** a committed file, a test definition, a passing executed test, a visually inspected asset, and a downloadable GitHub release are five different states. Never conflate them.

## Executive assessment

VOIDREIGN has a functioning native executable and a substantial play-tested foundation. It is **not yet a finished premium PC release**. The main gaps are a reproducible clean release, unverified official admin-mode installation and GitHub distribution, long-form economy/AI balance, content originality, missing strategic vertical slices and broad visual/audio UX review.

**Release blockers P0** (must close before treating any installer as final):

| ID | Owner/workstream | Evidence as of this audit | Acceptance gate |
|---|---|---|---|
| P0-01 | Build/integration | Audited dirty candidate based on `c084c2e`; integration HEAD already advanced beyond it while 400+ local modified/untracked paths contain new gameplay and art edits. Dirty builds have no reproducible source identity. | Review and commit the complete intended source/assets in coherent increments; reproduce installers from a clean checked-out tag. |
| P0-02 | CI/release engineering | GitHub Actions is enabled but repository workflow enumeration and run count were both zero at last check. Workflow YAML exists. | Actual successful C++ build, unit, data, UI/input, Windows imports, installer, gameplay and uninstall logs attached to the release commit. |
| P0-03 | Versioning | Source `CMakeLists.txt` declares `0.1.0`; historical `v0.1.0` tag is OpenSE4, not this VOIDREIGN build. | Introduce an unused release version, align CMake, installer metadata, tag, manifest and download names exactly. |
| P0-04 | Windows installer | User-level isolated variant of production NSIS was compiled and **silently installed, gameplay-tested, uninstalled with saves preserved** on 2026-11-09. Production installer still requests administrator privileges and writes HKLM/all-users shortcuts. | Validate the actual production installer in an authorized disposable Windows environment, including UAC, Windows Apps & Features, shortcuts, clean uninstall and user saves. |
| P0-05 | Publication | No published GitHub Release assets; local checksums and portable archive have passed. | Publish exact `VOIDREIGN-Setup-<version>.exe`, portable ZIP containing `VOIDREIGN.exe` + `game-data/`, and SHA-256 manifest; download each asset and rehash it. |
| P0-06 | Integration QA | Native local full unit suite: **1,684/1,684 tests; 566,606/566,606 assertions; 1 optional classic-data test skipped**. Six packaged startup/faction/fleet/save/AI gameplay scripts passed. | Repeat from clean release commit; no skipped required checks, no source/asset mismatch. |

**Quality gaps P1** (premium launch criteria, not solved by a compiler passing):

| ID | Workstream | Observed state | Definition of done |
|---|---|---|---|
| P1-01 | Economy & balance | Six seeded 500-turn native survival/UI runs passed; reviewed screenshots reveal 360,000 resource caps, lost positive income, zero trade, while native per-turn statistics for all six player empires show two planets in two systems at both turn 1 and turn 500. Ship counts grow 1 to 4 and total tech levels 5 to 67, but all six campaigns stagnate in expansion. This suggests poor economic engagement or AI expansion and needs deeper instrumentation. | Compare AI expansion and resource utilization by difficulty/seed; prevent idle 500-turn campaigns with perpetual storage overflow; collect machine-readable economy/research/fleet stats across 500+ turns. |
| P1-02 | Faction/origin diversity | Six factions and 20 origins documented; scripted startup currently covers Aurelian, Veyran and Khepri plus generalized tests. | Every origin and faction survives native start/save/load/turn transitions; mechanical tradeoffs matter and AI can handle each start. |
| P1-03 | Tactical/strategic depth | Fleet controls, queues, design and tactical screens exist and pass functional smokes. | Battle outcome reproducibility, retreat/experience/promotion, large-fleet responsiveness, station/chokepoint/asteroid interactions and balanced viable ship classes. |
| P1-04 | Campaign UX | Responsive titled native window, intro, quick start and Chronicle have automated screenshots. | Visual pass for galaxy/system/fleet/colony/research/leaders/diplomacy/events at 1024×768 and 1920×1080: readable hierarchy, keyboard use, contrast, feedback, navigation and no clipped controls. |
| P1-05 | Art direction | Asset-count checks confirm 49 component portraits, 47 facilities including 18 wonders, 72 faction ship portraits and miniatures, 24 tactical skies. | Human aesthetic review of every category: unique recognizable silhouettes, cohesive faction language, no lettering/watermarks/anatomy or low-resolution artifacts, clear 36px miniatures. |
| P1-06 | Audio, performance & stability | Three soundtrack tracks documented; local Windows runs passed. No full mix or long-session performance acceptance test. | Review transitions, SFX, peaks and mute settings by ear; record frame-time, memory and crashes during 500+ turn games on the 8 GiB target laptop. |
| P1-07 | Narrative originality | **6,144 contextual chapters** load and verify, but are variations generated from **32 authored premises**, not 6,144 independent plots. 2,048 roots and 12,288 choices. | Add individually written distinctive event families, triggered naturally by game state, with real consequences, branch continuity, no repetitive interruption and localization-proof authoring. Do not equate a generated variation with an independently authored story. |
| P1-08 | Government, AI & diplomacy | Six government types, six policy domains, legitimacy, migration and policy command UI implemented and tested; rare political crisis is primarily a log event. | Simulated and player-driven civic paths integrated with diplomacy, succession, unrest, AI strategic choices, save and multiplayer compatibility. |

**Missing or incomplete gameplay pillars P2** (vertical slices, each must ship with game-state, UI, AI, save/network and tests):

1. **Civil wars and breakaway states:** bounded unrest crises that can escalate to a genuine rebel empire, territorial/economic consequences and a meaningful response choice. Rare and signposted; not a per-turn annoyance.
2. **Interstellar trade and piracy:** actual trade-route/convoy entities, distance and capacity, interception, escort orders, embargo and diplomatic consequences. A passive policy income modifier is not a trade system.
3. **Legendary paragons and mercenaries:** uniquely authored named officers, rare traits/careers and contracts; costs, loyalty, mortality and balance. Basic leader recruiting is not a finished paragon or mercenary system.
4. **Ascension paths and multistage megaprojects:** mutually exclusive empire progression and expensive multi-turn projects with strategic vulnerabilities and late-game consequences. Existing 18 planetary wonders do not satisfy this.
5. **Handcrafted narrative breadth:** broaden the 32-premise catalogue into thousands of genuinely varied authored incidents/anomalies, preserving proper pacing and follow-up causality.
6. **Premium presentation and feel:** integrated art direction across menus, effects, audio, combat feedback, readable charts, animation, onboarding, accessibility and first-hour experience.

## Studio workstreams and dependency graph

| Lane | Parallelizable deliverables | Depends on | Required proof |
|---|---|---|---|
| A — Build / release | Clean source consolidation; GitHub CI; versioning; exact installer/ZIP/checksum names; NSIS integration QA | None | Reproducible build + downloadable hashes |
| B — Combat & strategic AI | Longgame telemetry, difficulty tuning, combat/chokepoint/station balance | Current core | Seeded campaigns, assertions, battle replay |
| C — Civil politics | Breakaway rules, empire AI, crises and succession UX | Existing laws/legitimacy | Deterministic rarity, save/network and UI tests |
| D — Trade & logistics | Trade routes, piracy, convoy and escort commands | Existing economy/fleets | Authoritative economy reconciliation |
| E — Character/late game | Paragons, mercenary contracts, staged megaprojects/ascension | Existing leaders/tech | Saved progression and exploit tests |
| F — Narrative | Hand-authored new events; event triggers and long-arc outcome balancing | Existing Chronicle | Duplicates/branch-graph/pacing audit |
| G — Art / UX | System/colony/fleet screens, asset review, animation and sound polish | UI state and content | Screenshot/contact-sheet review, 8 GiB performance |
| H — QA / player research | 6 factions × 20 origins, 500+ turn soak, smoke tests, installer/gameplay/uninstall | Every lane's output | Independent, dated results and failure tracking |

Lanes can be planned in parallel, but do not call a lane complete without its proof. Avoid concurrent edits to the same C++ and packaging files or simultaneous packagers.

## Release gates (sequential)

1. **G0 — Solid native foundation:** successful Windows build; complete unit tests; packaged data/art validator; six packaged gameplay scenarios; native window visible. **Currently passed locally for a dirty preview**.
2. **G1 — Reproducible code:** isolate and review all dirty source, updated art and test data. Create one clean commit; rebuild using the same committed inputs and verify native checksums.
3. **G2 — 4X feature complete:** economy/AI, fleets, all origins, leaders, governments, rebellion, trade/piracy, rare paragons and ascension each have a fully playable tested vertical slice.
4. **G3 — Premium beta:** 500+ turn multi-seed balance, >2-hour human playtests, in-game graphics/contact-sheet review, audio mix, usability and stability on Windows x64 including an 8 GiB device.
5. **G4 — Release candidate:** production NSIS install / real window / native gameplay / uninstall preservation pass; SHA-256 verified; no missing assets; published CI logs.
6. **G5 — Public release:** exact asset names and version/tag alignment; GitHub Releases downloads independently downloaded and rehashed; clear instructions and clean install/upgrade path.

## Today's completed QA work and next operational sequence

- A new **non-elevated isolated NSIS QA harness**, `tools/qa_nsis_isolated.ps1`, compiles a temporary alternate NSIS definition from the production script, using a unique temp install destination, HKCU keys and per-user shortcuts; it does **not** modify the production installer or existing installed games. The isolated setup was actually installed, launched, exercised through all six packaged gameplay scripts, then silently uninstalled. It left saves intact. This is a production-script behavioral regression check, **not** a substitute for the admin/UAC validation.
- Full C++ unit suite previously verified green (1,684 cases / 566,606 assertions), plus six native gameplay scripts and six extracted-ZIP gameplay scripts. No GitHub Actions success may be claimed until runs exist.
- **Six-faction 500-turn soak executed:** Aurelian seed 7, Veyran 11, Khepri 13, Meridian 17, Outer 19 and Helion 23 all reached turn 500 and passed empire-status/colony screenshot assertions (6/6, 3,000 total simulated turns). The reproducible harness is `tools/qa_faction_soak.ps1`, which writes screenshots outside the repository. This is survival evidence, not balanced AI evidence.
- **High-priority visual/economy finding:** inspected turn-500 treasury panels show every reviewed faction at 360,000 minerals/organics/radioactives, positive net resource income wasted by overflow, zero trade income. Native `History/plr_1_stats.txt` records confirm **two planets in two systems** for all six empires throughout 500 turns (not one colony), with only 1-to-4 ship growth and technology totals 5-to-67. Diagnose lack of AI exploration, new-colony construction and resource spending; add detailed AI telemetry instead of assuming a long-running executable is challenging or balanced. The interface typography and dense icon strips also need design review at 1280×800.
- **Actual native 500-turn statistics:** `tools/qa_campaign_telemetry.py` launches six seeded faction campaigns from the packaged game, parses the engine's own `History/plr_1_stats.txt`, and writes independent machine-readable CSV/JSON reports in `%TEMP%/voidreign-studio-campaign-telemetry-20261109/`. All six reached turn 500, with empire colonies **2→2**, ships **1→4**, total technology levels **5→67**, and **499 turns without any change in colony count**. Zero engine crashes but 12 AI-quality warnings (no net colony expansion and >100 turn stagnant colony totals). A separate 500-turn Aurelian campaign with **one empire total** reproduced the two-colony stagnation, so competition is not required for the problem to appear. The engine's stats do not yet capture full per-turn stockpiles or decisions.
- **Immediate next:** instrument colonization target availability, colony-ship design/queue orders and explorer fleet decisions to locate the AI no-expansion cause. Run `python tools/qa_campaign_telemetry.py --package-dir <stage> --turns 500 --strict-quality` as a deliberately failing quality gate until it is fixed; do not mark endgame balance green on smoke success. Keep CPU-heavy validation serial on the user's 8 GiB laptop.
- **Next integration task:** stage coherent dirty development changes into reviewed commits, rerun all tests from clean state and fix release-version naming and GitHub workflow registration.
- **Next game-system slice:** civil unrest and breakaways, then real trade/convoy mechanics; do not prioritize cosmetic polish over unfixed gameplay logic, but develop cohesive UI/art alongside each vertical slice.

**Definition of “ready”:** a person can install the genuine native release on a fresh Windows x64 PC, play without other games or SDKs, save/reload and complete campaigns without critical errors, uninstall without losing saves, and fetch correctly named verified assets from GitHub Releases. Passing local tests alone is not that milestone.

## Updated six-faction logistics-enabled balance evidence — 2026-11-09

**Candidate:** `dist/VOIDREIGN-0.1.0-9c248cb-dirty-windows-x86_64/`. This is a dirty locally staged candidate, **not a clean tagged final release**. It includes the new 7-drive fuel storage / 6-module colonist-berth repair being developed in the parallel logistics lane.

- Engine-data validation: `tools/verify_native_ship_logistics.py` passed 7 drive tiers and 6 colonization modules, 0 errors. Other workstream production records: 1,685-case full suite green, 32/32 integrity gates and eight scripted packaged gameplay scenarios passing (see `docs/PRODUCTION_STATUS.md`).
- **500-turn, three-empire mode** (24 systems, seeds 7/11/13/17/19/23 respectively): Aurelian ended at turn 121 with 1 colony and 0 ships; Veyran reached turn 500 with 5 colonies; Khepri ended turn 146 with 1 colony and 0 ships; Meridian ended turn 242 with 1 colony and 0 ships; Outer ended turn 141 with 0 colonies and 1 ship; Helion reached turn 500 with 37 colonies and 26 ships. All executable runs exited 0 and produced their screen image. Early endings are **quality/campaign outcomes**, not crashes; determine precise final-game reasons separately from saved state or game logs. Evidence: `%TEMP%/voidreign-logistics-campaign-telemetry-20261109/campaign-telemetry.json`.
- **500-turn, one-empire control** (same faction seeds and 24 systems): Aurelian 2→2 colonies; Veyran 2→2; Khepri 2→41; Meridian 2→32; Outer 2→2; Helion 2→2. All six recorded exactly 500 turns and process exit 0; ten quality warnings, no technical errors. Evidence: `%TEMP%/voidreign-logistics-peacetime-500-20261109/campaign-telemetry.json`.
- **Interpretation:** true colonization is now possible, but behavior varies sharply by faction and seed even with no opposition. Multiplayer competition adds early endings and extreme late-game divergence. Do not make an untested global difficulty/resource multiplier change. Next measure access to settlement targets, colonizer order acceptance and route knowledge on the stuck solo seeds; compare naturally successful Khepri/Meridian with stuck Aurelian/Veyran/Outer/Helion. For competitive runs inspect diplomatic triggers, expansion curves, fleet power, battle losses, war declarations and starting geography.
- The telemetry runner now separates **technical engine errors** from **early game endings and AI-quality warnings**, and accepts `--empires`, `--systems`, `--seed-offset` and `--strict-quality` for reproducible balancing. Strict quality must remain red for stagnation and unreasonably early endings even while native runtime checks pass.
- The detailed opt-in C++ traces used to localize the older pre-repair colonization pipeline were removed from the five engine/client source files after verifying that a separate workstream had already repaired the actual native logistics data. There is no residual debug instrumentation in the committed runtime.

**Next release/feature priorities:** (1) fix native AI expansion reliability and wartime balance against this 500-turn matrix; (2) review dirty source and publish a reproducible clean release with CI and production NSIS verification; (3) implement real trade/piracy and civil-war vertical slices; (4) flesh out paragons/megaprojects and diverse authored event arcs; (5) comprehensive original art, readability, audio and Windows performance acceptance.

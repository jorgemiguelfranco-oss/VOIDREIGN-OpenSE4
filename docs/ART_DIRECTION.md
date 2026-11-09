# VOIDREIGN — Visual Art Direction and QA

**Production goal:** original, richly detailed, coherent science-fiction artwork throughout the native Windows 4X game. Distinct fleet factions; premium strategic UI readability at 36px; hero-level fidelity at report and title screen scale.

## Visual language

- Primary colour language: deep midnight navy, bone titanium, subdued brass, restrained cyan/teal energy and occasional faction-specific spectral accents.
- Artistic subject: believable hardware and engineering; layered plating, shipyard trusses, turrets, hangars, radiators, sensor arrays, realistic scale.
- Avoid: generic neon glyphs, text baked into art, crowded UI panels, flat single-colour polygon craft presented as finished key art, repeated stock images.
- The original game is *VOIDREIGN*. Do not depict or copy protected ships, branding or identifiable designs from other franchises.

## Faction identities

| Faction | Material treatment | Shapes |
|---|---|---|
| Aurelian | ivory titanium, pale gold, turquoise conduits | elegant winged naval craft |
| Veyran | blue-green ceramic, obsidian, bioluminescence | crescent hulls and fluid alien contours |
| Khepri | segmented black chitin, aged bronze, acid-green power | layered insectoid fortresses |
| Meridian | violet-silver crystal, luminous amethyst | faceted high-technology spires |
| Outer | weathered dark steel, orange hazard marking | modular industrial trusses |
| Helion | alabaster and gold, solar amber radiators | monumental ceremonial geometry |

## Production formats and exact native integration

- **Ship report portraits**: `game-data/Pictures/Races/<Faction>/<Faction>_Portrait_VoidReign<Hull>.png` — 128×128 RGB. Premium 1024-pixel input is reduced via 512-pixel intermediate with Lanczos.
- **Tactical ship miniatures**: `.../<Faction>_Mini_VoidReign<Hull>.png` — 36×36 RGBA with transparent surroundings. Do NOT replace the mini with opaque photorealistic portraits.
- **High-quality masters**: `art-library/voidreign-art-faction-ships/masters/<Faction>_<Hull>.webp` — 512×512.
- **Premium sources**: `art-library/voidreign-premium-ships/<Faction>/<Hull>.jpg` — 1024×1024 originals, with .json SHA-256 and generation provenance.
- **Approved-only integration**: `art-library/voidreign-premium-ships/APPROVED.json` locks approved source hashes; `tools/art/generate_ship_art.py` reads these and preserves the procedural fallback for unapproved combinations.
- **Component/facility icons**: exact Pic Num mappings, transparent 36px icon atlas, 128px detailed portraits. Keep categories differentiated by actual shape.
- **Key art**: source/provenance in `art-library/voidreign-premium-keyart/`. Any UI replacement requires preview and engine-specific layout test; do not overwrite existing cinematic intro by default.

## Controlled generation

1. Stage new portraits: `python tools/art/generate_premium_faction_portraits.py --faction-all --hulls-all --workers 3`.
2. Produce review sheets and verify source digests: `python tools/art/review_premium_ships.py --min-count 1`.
3. **Visually inspect all six** `review-<Faction>.jpg` sheets for duplicate craft, nonsense geometry, wrong backgrounds, letter artifacts and crop.
4. Approve vetted set only: `python tools/art/review_premium_ships.py --approve --min-count <count>`.
5. Regenerate native files: `python tools/art/generate_ship_art.py`.
6. Verify image integrity and exact integration: `python tools/art/verify_art_assets.py` and `python tools/art/verify_premium_ships.py`.
7. Run native build and interactive screenshot QA before a new Windows release. Art validation is not equivalent to a release test.

External key-art candidates were created with the publicly documented PixelSter text-image API; source prompts, image hashes and model attribution are recorded locally. Service availability and licensing terms may change. Never depend on external image generation during gameplay. All runtime assets ship locally.

## Galactic Chronicle art completion — 9 November 2026

All **32 distinct authored narrative plotline families** now have their own approved,
original 1024×1024 source illustrations and native 256×256 `Chronicle_XX.png` images.
These are **32 illustration families**, not 6,144 separately illustrated chapters:
each illustration visually unifies the 192 setting/stance/chapter variations of its
plotline. Source prompts, model/provenance and SHA-256 digests are recorded alongside
the source JPEGs and in `art-library/voidreign-premium-events/APPROVED.json`.

Rejected images with fake text, mislabeled structures or thematically unsuitable
vehicles were separately redrawn, visually examined and replaced. The rejected
originals remain in a local review archive, not in the player package. The new
`tools/art/verify_chronicle_art.py` verifies every approved image's source,
metadata, uniqueness, pixel dimensions and matching native conversion; run it with
`--stage build/dist-windows` to check the **player** game-data staging as well.
The native release verifier requires all 32 event images to survive packaging.

The 47-facility native icons now use a dynamic eight-row atlas. If facility
definitions are added, `tools/art/build_component_facility_atlases.py` automatically
expands rather than truncating the atlas; both `verify_art_assets.py` and
`verify_native_art.py` have passed on this catalogue.

## Remaining premium polish gates

UI interaction icon silhouettes and hover states, strategic resource glyph consistency, distinctive facilities/wonders, event illustrations, leader portrait quality, star-system maps, tactical effects, cinematics, readable typography at 800×600 and 1024×768, native installer icon, in-game screenshot review, accessibility contrast, and performance on an 8 GiB RAM PC. None of these can be marked complete solely by image-count checks.

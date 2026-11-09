# VOIDREIGN native art provenance

## Existing converted art

The existing native PNG art assets are converted from the owner's original VOIDREIGN art library
on the `art/crisis-wonders` branch of `jorgemiguelfranco-oss/voidreign`.

Original source files, credits and provenance for those assets are preserved in that library.
Conversion uses Pillow/Lanczos, retains alpha on ship/planet assets and creates native-resolution
PNG files for the OpenSE4 renderer. The twelve VOIDREIGN hull classes have native miniatures
and full portraits in each faction's picture set.

## Distinct faction leader portraits (2026-11-08)

The six `*_Race_Portrait.png` files were refreshed with six distinct, AI-generated faction leader
portraits. The earlier five-master palette variants are superseded in the game data; the prior
source conversion remains in the original art library and in Git history.

The 512x512 WebP source images were generated through the free AI Horde anonymous volunteer pool
using **AlbedoBase XL (SDXL)** on 2026-11-08. They were reviewed, then resized to 192x192 PNG for
the native race-portrait slots. A small bottom-edge pseudo-signature artefact in the Veyran source
was excluded by a centered crop before resizing. No external image URL or generation service is
required at game runtime.

Source images, faction prompt briefs, worker names, seeds, request IDs and SHA-256 hashes are
preserved in `art-library/voidreign-art-faction-portraits/`:
- `source/` — original 512x512 WebP files.
- `PROMPTS.md` — shared art direction and per-faction identity briefs.
- `GENERATION-MANIFEST.json` — model, worker, seed, request and source/native checksums.

These are AI-generated concept-art assets, not commissioned illustrations or a claim of
exclusive species artwork. The next art pass is an in-game review at actual UI scale and any
remaining environment/background illustrations.

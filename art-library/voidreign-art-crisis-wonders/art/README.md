# art/
All art is plain, swappable files referenced by path from the data files (`Picture :=`, `Portrait :=`, `Star Pictures :=`,
`Map Background Picture :=` ...). A mod replaces any image by shipping a file at the same relative path
(e.g. `mods/my_mod/art/hulls/escort.webp`). `npm test` fails if a data file references a missing asset.
```
art/hulls/        Hull portraits, 800x450 webp, side/three-quarter view on black (one per Hulls.txt entry)
art/ships/        Pictures for neutral designs (pirates, monsters) from Neutrals.txt
art/components/   Component icons, 96x96 png (one per Components.txt entry)
art/facilities/   Facility icons, 96x96 png
art/planets/      Planet pictures per planet type, 512x512 webp with alpha (sizes scale the same picture)
art/stars/        Star sprites per star type, 256x256 png with alpha
art/portraits/    Race and faction portraits, 512x512 webp
art/backgrounds/  Galaxy map / UI backdrop
art/ui/           Title splash and logo
```
Provenance and licence of every file: `art/CREDITS.txt`. Generators: `tools/art/` (raster processing + procedural stars,
SVG icon renderer, procedural audio). Style: dark, painterly space opera close to Space Empires IV; no text in images
except the logo; mature tone, no gore.

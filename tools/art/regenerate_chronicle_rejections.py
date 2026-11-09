#!/usr/bin/env python3
"""Stage replacements for Chronicle illustrations rejected at visual review.

Never mutates the native game or approved artwork. The next step is to visually
review each Arc_<index>_redo.jpg and use the existing approval pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "art-library" / "voidreign-premium-events"
API = "https://freeapi.pro/api/tti"
STORIES = {
    0: "On an airless asteroid, a survey team in detailed EVA suits explores a gigantic ancient wrecked observatory of basalt and titanium. A vast articulated telescope points at an impossible unknown star; broken mirrors and metallic instruments cover the ruined stone courtyard. Deep black vacuum, distant blue nebula, amber flashlight beams. No writing or holographic diagrams.",
    17: "In an original futuristic radio astronomy research laboratory, tiny scientists stand below a monumental spherical dark-matter detector. Concentric holographic acoustic waves of pure teal and amethyst light vibrate through its transparent rings, responding to an unseen cosmic visitor. Physically believable equipment and beautifully textured research architecture; NO formulae, equations, text, boards, displays with letters or marks.",
    23: "A damaged isolated border communications station, a sophisticated orbiting spacecraft with an enormous fragmented parabolic radio dish and transmission antenna arrays, emits interwoven luminous signal waves into the lonely cobalt-blue starfield. Tiny visiting patrol craft approach carefully. Distinctive cinematic hard-science-fiction architecture, believable spacecraft, stormy nebula cloud. No words, no signs, no writing, no text panels.",
    27: "A lost deep-space survey fleet of four weathered futuristic explorer starships of different shapes, with real titanium armor, sensor dishes and detachable science modules, returns unexpectedly through a magnificent glowing cobalt warp fissure. Visible crew deck lights and remarkable atmospheric sense of time displacement. Entirely in OUTER SPACE above a small alien planet; NO oceans, NO sailing ships, NO terrestrial architecture, NO old-fashioned ships.",
    28: "An ominous swarm of self-replicating metallic nanomachines visibly dismantles the crust of a small uninhabited rocky planet in deep space, creating intricate fractal streams of glittering steel particles that approach a distant human cargo convoy. Tiny ships establish incredible scale. Dramatic hard-science fiction visual storytelling, disciplined restrained navy, teal, amber color grading, realistic physics of debris, threatening beauty, cinematic vastness."
}

STYLE = (
    "Create ONE finished, original, premium art-directed science fiction narrative illustration, "
    "full-bleed 1:1 cinematic matte painting for a 4X empire strategy PC game. "
    "World-class hand-painted realistic science-fiction concept art with remarkable composition, "
    "beautiful sophisticated natural detail, spectacular credible engineering, compelling light "
    "and shadow, a textured painterly finish, deep layered atmosphere, subtle warm brass accents "
    "against muted midnight blue and teal. The scene must be unique, natural, coherent, beautiful "
    "and clearly tell this specific story, never just a generic AI-generated sci-fi image. "
    "No text, NO letters, NO labels, NO glyphs, NO numbers, NO equations, NO illegible pseudo-writing, "
    "NO watermarks, NO borders, NO title cards, NO collages, NO UI."
)

def generate(index: int, attempts: int) -> tuple[int, str]:
    target = OUT / f"Arc_{index:02d}_redo.jpg"
    meta = OUT / f"Arc_{index:02d}_redo.json"
    if target.is_file() and meta.is_file():
        return index, "EXISTING"
    prompt = STORIES[index] + "\n\n" + STYLE
    payload = json.dumps({"prompt": prompt, "ratio": "1:1"}).encode()
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(
                API, data=payload,
                headers={"User-Agent": "VOIDREIGN-Art/1.0", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=110) as reply:
                response = json.load(reply)
            url = response.get("imageUrl")
            if not response.get("success") or not isinstance(url, str) or not url.startswith("https://"):
                raise ValueError("Provider returned no valid image URL")
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "VOIDREIGN-Art/1.0"}),
                timeout=85,
            ) as reply:
                image_bytes = reply.read(12_000_000)
            with Image.open(io.BytesIO(image_bytes)) as source:
                source.load()
                if min(source.size) < 640:
                    raise ValueError(f"Source resolution {source.size} too small")
                result = ImageOps.fit(
                    source.convert("RGB"), (1024, 1024), method=Image.Resampling.LANCZOS
                )
                result.save(target, format="JPEG", quality=93, subsampling=0, optimize=True)
            meta.write_text(
                json.dumps({
                    "index": index, "prompt": prompt, "source": API,
                    "source_model": response.get("model"), "attempt": attempt,
                    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                    "review_status": "candidate; requires visual review",
                }, indent=2) + "\n", encoding="utf-8"
            )
            return index, "STAGED"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, OSError) as err:
            if attempt >= attempts:
                return index, f"FAILED {type(err).__name__}: {str(err)[:140]}"
            time.sleep(2 * attempt)
    return index, "FAILED unknown"

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--attempts", type=int, default=2)
    p.add_argument("--indices", default="0,17,23,27,28")
    args = p.parse_args()
    ids = [int(i) for i in args.indices.split(",")]
    if any(i not in STORIES for i in ids):
        p.error("Unknown plot index")
    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, min(3, args.workers))) as executor:
        futures = [executor.submit(generate, i, args.attempts) for i in ids]
        for future in as_completed(futures):
            index, result = future.result()
            print(f"{index:02d}: {result}", flush=True)
            failed += result.startswith("FAILED")
    return int(failed > 0)

if __name__ == "__main__":
    raise SystemExit(main())

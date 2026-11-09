#!/usr/bin/env python3
"""Promote visually reviewed VOIDREIGN Chronicle replacement illustrations.

Original, rejected staged versions are preserved under /review-rejected. All
promoted entries retain stable matching title and hash metadata for the native
asset approval tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from generate_narrative_catalogue import ARCS

STAGE = ROOT / "art-library" / "voidreign-premium-events"
ARCHIVE = STAGE / "review-rejected"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def promote(index: int) -> None:
    candidate = STAGE / f"Arc_{index:02d}_redo.jpg"
    candidate_metadata = candidate.with_suffix(".json")
    target = STAGE / f"Arc_{index:02d}.jpg"
    target_meta = target.with_suffix(".json")
    if not candidate.is_file() or not candidate_metadata.is_file():
        raise RuntimeError(f"Missing replacement source and/or metadata for {index}")
    metadata = json.loads(candidate_metadata.read_text(encoding="utf-8-sig"))
    if metadata.get("index") != index or metadata.get("sha256") != sha(candidate):
        raise RuntimeError(f"Replacement {index} source checksum mismatch")
    with Image.open(candidate) as image:
        image.verify()
    with Image.open(candidate) as image:
        if image.size != (1024, 1024):
            raise RuntimeError(f"Replacement {index} has wrong size")
    ARCHIVE.mkdir(exist_ok=True, parents=True)
    if target.is_file():
        previous = ARCHIVE / target.name
        if not previous.exists():
            shutil.copy2(target, previous)
    if target_meta.is_file():
        previous_meta = ARCHIVE / target_meta.name
        if not previous_meta.exists():
            shutil.copy2(target_meta, previous_meta)
    shutil.copy2(candidate, target)
    entry = {
        "index": index,
        "title": ARCS[index][0],
        "trigger": ARCS[index][1],
        "source": metadata["source"],
        "model": metadata.get("source_model"),
        "prompt": metadata["prompt"],
        "sha256": sha(target),
        "review_status": "visually inspected and selected",
        "replacement_reason": "Prior candidate contained pseudo-letters, wrong subject, or failed generation",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "archived_prior_source": f"review-rejected/Arc_{index:02d}.jpg" if (ARCHIVE / f"Arc_{index:02d}.jpg").exists() else None
    }
    target_meta.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(f"PROMOTED {index:02d}: {entry['title']}: sha256={entry['sha256']}", flush=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--indices", default="0,17,23,27,28")
    args = parser.parse_args()
    indices = [int(t.strip()) for t in args.indices.split(",")]
    for index in indices:
        promote(index)

if __name__ == "__main__":
    main()

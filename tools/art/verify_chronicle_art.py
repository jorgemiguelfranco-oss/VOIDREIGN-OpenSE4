#!/usr/bin/env python3
"""Verify original VOIDREIGN's 32 independently illustrated Chronicle plot families.

This checks source/provenance, approvals and runtime image hashes, dimensions and
uniqueness. Six thousand 144 narrative chapters map coherently to these 32
visual families (192 chapter variants per family), not 6,144 unique images.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from generate_narrative_catalogue import ARCS

APPROVED = ROOT / "art-library" / "voidreign-premium-events" / "APPROVED.json"

def sha(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a valid PNG header: {path}")
    return struct.unpack(">II", header[16:24])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path,
        help="Installed player folder to inspect instead of local game-data; "+
             "requires all 32 individual 256px Chronicle images")
    args = parser.parse_args()
    errors: list[str] = []
    manifest = json.loads(APPROVED.read_text(encoding="utf-8"))
    assets = manifest.get("assets", {})
    ids = sorted(int(i) for i in assets)
    if ids != list(range(32)):
        errors.append(f"Approval coverage is {ids}, expected all arc indexes 0..31")
    if len(ARCS) != 32:
        errors.append(f"Narrative plot index changed: {len(ARCS)}, expected 32")
    root = args.stage if args.stage else ROOT
    expected_names = {f"Chronicle_{i:02d}.png" for i in range(32)}
    folder = root / "game-data" / "Pictures" / "Events"
    actual_names = {p.name for p in folder.glob("Chronicle_*.png")}
    if actual_names != expected_names:
        errors.append(f"Native Chronicle images missing={sorted(expected_names-actual_names)}, "
                      f"unexpected={sorted(actual_names-expected_names)}")
    seen: set[str] = set()
    for i in range(32):
        record = assets.get(str(i))
        if not record:
            errors.append(f"Arc {i} missing approval metadata")
            continue
        if record.get("title") != ARCS[i][0]:
            errors.append(f"Arc {i} title does not match native narrative catalogue")
        file = record.get("game_file", "")
        canonical = f"game-data/Pictures/Events/Chronicle_{i:02d}.png"
        if file != canonical:
            errors.append(f"Arc {i} game image mapping incorrect: {file!r}")
            continue
        native = root / canonical
        if not native.is_file():
            errors.append(f"Arc {i}: no native image")
            continue
        try:
            dimension = png_size(native)
            if dimension != (256, 256):
                errors.append(f"Arc {i}: native image resolution {dimension}, not 256x256")
            digest = sha(native)
            if digest in seen:
                errors.append(f"Arc {i}: repeated PNG illustration")
            seen.add(digest)
            if not args.stage and digest != record.get("game_sha256"):
                errors.append(f"Arc {i}: native image differs from approved hash")
            if native.stat().st_size < 25_000:
                errors.append(f"Arc {i}: unreasonably small/placeholder image")
        except (OSError, ValueError) as exc:
            errors.append(f"Arc {i}: {exc}")
        if args.stage:
            continue
        source = ROOT / record.get("source", "")
        if not source.is_file():
            errors.append(f"Arc {i}: source missing")
            continue
        if sha(source) != record.get("source_sha256"):
            errors.append(f"Arc {i}: source hash mismatch")
        metadata = source.with_suffix(".json")
        if not metadata.exists():
            errors.append(f"Arc {i}: generation provenance missing")
            continue
        meta = json.loads(metadata.read_text(encoding="utf-8-sig"))
        if meta.get("index") != i or meta.get("sha256") != sha(source):
            errors.append(f"Arc {i}: source metadata mismatch")
    print(f"Chronicle art: {len(seen)}/32 unique verified native image families")
    print(f"Story variants: {32 * 16 * 4 * 3} narrative chapters across 32 illustrated families")
    print(f"Missing/unapproved/mismatched files: {len(errors)}")
    for error in errors:
        print("ERROR:", error)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())

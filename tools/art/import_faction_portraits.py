from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "build" / "art_pipeline"
PREVIEWS = PIPELINE / "previews"
ART = ROOT / "art-library" / "voidreign-art-faction-portraits"
SOURCE = ART / "source"
NATIVE = ROOT / "game-data" / "Pictures" / "Races"

FACTIONS = ("Aurelian", "Veyran", "Khepri", "Meridian", "Outer", "Helion")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_records() -> tuple[dict, dict[str, dict]]:
    archived = ART / "GENERATION-MANIFEST.json"
    transient = PIPELINE / "manifest.json"
    manifest_path = archived if archived.is_file() else transient
    if not manifest_path.is_file():
        raise SystemExit(
            "No art manifest found. Download six AlbedoBase XL outputs into "
            "build/art_pipeline/previews or restore art-library/voidreign-art-faction-portraits."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    records = manifest.get("assets") or manifest.get("generated") or []
    by_faction = {entry["faction"]: dict(entry) for entry in records}
    # The temporary retrieval ledger is available on the generating machine.
    # Copy retrieval times into the archived manifest so clean clones retain them.
    if transient.is_file() and manifest_path == archived:
        temporary = json.loads(transient.read_text(encoding="utf-8-sig"))
        temporary_records = {entry["faction"]: entry for entry in temporary.get("generated", [])}
        for faction, record in by_faction.items():
            if faction in temporary_records and temporary_records[faction].get("retrieved_at"):
                record["retrieved_at"] = temporary_records[faction]["retrieved_at"]
    return manifest, by_faction


def main() -> None:
    source_manifest, generated = source_records()
    if set(generated) != set(FACTIONS):
        missing = sorted(set(FACTIONS) - set(generated))
        extra = sorted(set(generated) - set(FACTIONS))
        raise SystemExit(f"Expected six faction images. Missing={missing}; extra={extra}")

    SOURCE.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)

    outputs = []
    for faction in FACTIONS:
        source_name = f"{faction}_Race_Portrait_AlbedoXL.webp"
        source_target = SOURCE / source_name
        preview = PREVIEWS / f"{faction}_AlbedoXL.webp"
        archived = ROOT / generated[faction]["source_file"] if generated[faction].get("source_file") else source_target
        source = preview if preview.is_file() else archived

        if not source.is_file():
            raise SystemExit(f"Missing source image for {faction}: {source}")
        if source.resolve() != source_target.resolve():
            shutil.copy2(source, source_target)

        with Image.open(source_target) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        if image.size != (512, 512):
            raise SystemExit(f"{faction} has unexpected dimensions {image.size}; expected 512x512")

        # Veyran's volunteer output has a small pseudo-signature at the bottom edge.
        # Crop to the face, fin crest and shoulders, excluding the artefact entirely.
        crop = image.crop((32, 0, 480, 448)) if faction == "Veyran" else image
        portrait = crop.resize((192, 192), Image.Resampling.LANCZOS)

        native = NATIVE / faction / f"{faction}_Race_Portrait.png"
        native.parent.mkdir(parents=True, exist_ok=True)
        portrait.save(native, format="PNG", optimize=True, compress_level=9)

        entry = generated[faction]
        outputs.append({
            "faction": faction,
            "model": entry["model"],
            "worker": entry["worker"],
            "request_id": entry["request_id"],
            "seed": entry["seed"],
            "retrieved_at": entry.get("retrieved_at"),
            "source_file": str(source_target.relative_to(ROOT)).replace("\\", "/"),
            "source_bytes": source_target.stat().st_size,
            "source_sha256": sha256(source_target),
            "native_file": str(native.relative_to(ROOT)).replace("\\", "/"),
            "native_width": 192,
            "native_height": 192,
            "native_bytes": native.stat().st_size,
            "native_sha256": sha256(native),
            "processing": "Veyran trimmed to a centered square to exclude a bottom-edge pseudo-signature; all six resized with Lanczos to 192x192"
        })

    retrieval_times = sorted(
        datetime.fromisoformat(item["retrieved_at"])
        for item in outputs
        if item.get("retrieved_at")
    )
    manifest = {
        "title": "VOIDREIGN faction leader portraits",
        "generated_date": retrieval_times[0].date().isoformat() if retrieval_times else source_manifest.get("generated_date"),
        "first_source_retrieved_at": retrieval_times[0].isoformat() if retrieval_times else None,
        "last_source_retrieved_at": retrieval_times[-1].isoformat() if retrieval_times else None,
        "converted_at": datetime.now(timezone.utc).isoformat(),
        "generator": "AI Horde anonymous volunteer image-generation pool",
        "model_family": "AlbedoBase XL (SDXL)",
        "source_resolution": "512x512 WebP",
        "native_resolution": "192x192 PNG",
        "runtime_requirement": "None; generated art is bundled as native game data",
        "assets": outputs,
    }
    (ART / "GENERATION-MANIFEST.json").write_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"Imported {len(outputs)} original faction portraits.")
    for item in outputs:
        print(f"{item['faction']}: {item['native_bytes']} bytes; sha256={item['native_sha256']}")
    print(f"Manifest: {ART / 'GENERATION-MANIFEST.json'}")


if __name__ == "__main__":
    main()

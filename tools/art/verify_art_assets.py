from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "game-data" / "Data"
PIC = ROOT / "game-data" / "Pictures"

FACTIONS = ("Aurelian", "Veyran", "Khepri", "Meridian", "Outer", "Helion")
HULLS = ("Pathfinder", "Hauler", "Frigate", "Destroyer", "Cruiser", "Battleship",
         "Colonizer", "Station", "Corvette", "ScienceVessel", "Dreadnought", "MobileShipyard")
BIOMES = ("Starfield", "Nebula", "Pulsar", "BlackHole", "Magnetar", "WarpHub")
ERRORS: list[str] = []
WARNINGS: list[str] = []


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def records(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    chunks = re.split(r"(?m)(?=^Name\s*:=)", text)
    result = []
    for chunk in chunks:
        name = re.search(r"(?m)^Name\s*:=\s*(.+)$", chunk)
        if not name:
            continue
        pic = re.search(r"(?m)^Pic Num\s*:=\s*(\d+)", chunk)
        result.append({"name": name.group(1).strip(), "pic": pic.group(1) if pic else ""})
    return result


def check_image(path: Path, expected: tuple[int, int], label: str) -> tuple[str, tuple[int, int]]:
    if not path.is_file():
        ERRORS.append(f"{label}: missing {path.relative_to(ROOT)}")
        return "", (0, 0)
    try:
        with Image.open(path) as image:
            image.load()
            size = image.size
            if size != expected:
                ERRORS.append(f"{label}: expected {expected[0]}x{expected[1]}, got {size[0]}x{size[1]} ({path.name})")
            if image.getbbox() is None:
                ERRORS.append(f"{label}: blank image {path.relative_to(ROOT)}")
        return digest(path), size
    except Exception as exc:
        ERRORS.append(f"{label}: unreadable image {path.relative_to(ROOT)} ({exc})")
        return "", (0, 0)


def check_numbered_art(data_file: str, folder: str, prefix: str, count: int) -> int:
    rows = records(DATA / data_file)
    if len(rows) != count:
        ERRORS.append(f"{data_file}: expected {count} entries, got {len(rows)}")
    numbers = [int(r["pic"]) for r in rows if r["pic"].isdigit()]
    if numbers != list(range(1, len(rows) + 1)):
        ERRORS.append(f"{data_file}: Pic Num values are not unique sequential 1..N")
    hashes = []
    for i, row in enumerate(rows, 1):
        number = int(row["pic"]) if row["pic"].isdigit() else i
        path = PIC / folder / f"{prefix}_{number:03d}.png"
        h, _ = check_image(path, (128, 128), data_file)
        if h:
            hashes.append(h)
    if len(set(hashes)) != count:
        ERRORS.append(f"{folder}: expected {count} unique images; found {len(set(hashes))}")
    return len(rows)


def main() -> int:
    component_count = check_numbered_art("Components.txt", "Components", "Comp", 49)
    facility_count = check_numbered_art("Facility.txt", "Facilities", "Facil", 29)

    # Component/facility 36px strips must match the portrait count and order.
    for folder, name, columns, count in (
        ("Components", "Components.png", 7, component_count),
        ("Facilities", "Facility.png", 6, facility_count),
    ):
        rows = (count + columns - 1) // columns
        check_image(PIC / folder / name, (columns * 36, rows * 36), f"{folder} icon atlas")

    ui_images = {
        "Game/General.png": (608, 176),
        "Game/Buttons/Main.png": (442, 102),
        "Game/Buttons/Orders.png": (782, 408),
        "Game/Buttons/Arrows.png": (48, 72),
        "Game/Buttons/BigLeftRightArrows.png": (28, 150),
        "Game/Buttons/BigUpDownArrows.png": (128, 68),
        "Game/Buttons/Close.png": (60, 60),
        "Game/Buttons/DetailUp.png": (33, 84),
        "Game/Buttons/Nextprev.png": (192, 96),
        "Game/Buttons/TabBtns.png": (576, 150),
        "Game/Dialogs/Selection.png": (36, 36),
    }
    for relative, size in ui_images.items():
        check_image(PIC / relative, size, "UI atlas")

    portrait_hashes = set()
    mini_hashes = set()
    for faction in FACTIONS:
        folder = PIC / "Races" / faction
        for hull in HULLS:
            portrait = folder / f"{faction}_Portrait_VoidReign{hull}.png"
            mini = folder / f"{faction}_Mini_VoidReign{hull}.png"
            hp, _ = check_image(portrait, (128, 128), f"{faction} ship portrait")
            hm, _ = check_image(mini, (36, 36), f"{faction} ship mini")
            portrait_hashes.add(hp)
            mini_hashes.add(hm)
    if len(portrait_hashes) != len(FACTIONS) * len(HULLS):
        ERRORS.append("Faction ship portraits are not all unique")
    if len(mini_hashes) != len(FACTIONS) * len(HULLS):
        ERRORS.append("Faction ship miniatures are not all unique")

    # Six faction leader portraits are part of the same native race folders.
    for faction in FACTIONS:
        check_image(PIC / "Races" / faction / f"{faction}_Race_Portrait.png", (192, 192),
                    f"{faction} leader portrait")

    system_types = records(DATA / "SystemTypes.txt")
    system_names = set()
    text = (DATA / "SystemTypes.txt").read_text(encoding="utf-8-sig", errors="replace")
    for match in re.finditer(r"(?m)^Background Bitmap\s*:=\s*(.+)$", text):
        system_names.add(match.group(1).strip().removesuffix(".bmp").removesuffix(".BMP"))
    if not set(BIOMES).issubset(system_names):
        ERRORS.append("SystemTypes.txt does not reference all six original biome backgrounds")
    biome_hashes = set()
    for biome in BIOMES:
        h, _ = check_image(PIC / "Systems" / f"{biome}.png", (128, 128), f"{biome} system icon")
        biome_hashes.add(h)
        check_image(PIC / "Systems" / "1024X768" / f"{biome}.png", (660, 660), f"{biome} large system background")
        check_image(PIC / "Systems" / "800X600" / f"{biome}.png", (490, 490), f"{biome} small system background")
        variant_hashes=set()
        for variant in range(1,5):
            vh,_=check_image(PIC / "Systems" / f"{biome}_V{variant}.png",(128,128),f"{biome} system scene variant")
            variant_hashes.add(vh)
            check_image(PIC / "Systems" / "1024X768" / f"{biome}_V{variant}.png",(660,660),f"{biome} large scene variant")
            check_image(PIC / "Systems" / "800X600" / f"{biome}_V{variant}.png",(490,490),f"{biome} small scene variant")
        if len(variant_hashes)!=4:
            ERRORS.append(f"{biome}: scene variations are not all distinct")
        for i in range(1, 10):
            check_image(PIC / "Systems" / f"{biome}Tile{i}.png", (72, 72), f"{biome} tactical tile")
    if len(biome_hashes) != len(BIOMES):
        ERRORS.append("System biome thumbnails are not all distinct")

    # Ensure old numbered placeholder files do not remain beyond current data IDs.
    for folder, prefix, last in (("Components", "Comp", 49), ("Facilities", "Facil", 29)):
        for path in (PIC / folder).glob(f"{prefix}_*.png"):
            match = re.fullmatch(prefix + r"_(\d{3})\.png", path.name)
            if match and int(match.group(1)) > last:
                WARNINGS.append(f"Unused legacy art file retained: {path.relative_to(ROOT)}")

    print("VOIDREIGN native art integrity audit")
    print(f"Components: {component_count} unique portraits + 36px icon atlas")
    print(f"Facilities: {facility_count} unique portraits + 36px icon atlas")
    print(f"Faction hull art: {len(FACTIONS)*len(HULLS)} portraits + {len(FACTIONS)*len(HULLS)} miniatures")
    print(f"Faction leaders: {len(FACTIONS)} portraits")
    print(f"System biomes: {len(BIOMES)}; {len(BIOMES)*4} unique scenes; {len(BIOMES)*4*2} layout variants; {len(BIOMES)*9} tactical tiles")
    print(f"UI: {len(ui_images)} verified sprite sheets")
    print(f"Errors: {len(ERRORS)}; warnings: {len(WARNINGS)}")
    for item in ERRORS:
        print("ERROR:", item)
    for item in WARNINGS:
        print("WARNING:", item)
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())

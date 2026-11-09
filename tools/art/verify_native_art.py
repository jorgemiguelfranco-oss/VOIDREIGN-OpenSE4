from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"game-data"/"Pictures"
DATA=ROOT/"game-data"/"Data"
GIT=r"C:\Program Files\Git\cmd\git.exe"
errors=[]
warnings=[]
checks=0

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def check_image(path:Path,size:tuple[int,int]|None,desc:str):
    global checks
    if not path.is_file():
        errors.append(f"Missing {desc}: {path.relative_to(ROOT)}")
        return
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            if size and im.size!=size:
                errors.append(f"{desc} has size {im.size}, expected {size}: {path.relative_to(ROOT)}")
            if im.width<1 or im.height<1:
                errors.append(f"Invalid zero-size image: {path.relative_to(ROOT)}")
    except Exception as e:
        errors.append(f"Unreadable {desc}: {path.relative_to(ROOT)} ({e})")
    checks+=1

def entries(path:Path):
    text=path.read_text(encoding="utf-8-sig",errors="replace")
    chunks=re.split(r"(?m)(?=^Name\s*:=)",text)
    out=[]
    for c in chunks:
        n=re.search(r"(?m)^Name\s*:=\s*(.+)$",c)
        if not n: continue
        pic=re.search(r"(?m)^Pic Num\s*:=\s*(\d+)",c)
        out.append((n.group(1).strip(),int(pic.group(1)) if pic else None))
    return out

def unique_pics(filename:str,folder:str,prefix:str,expected:int):
    records=entries(DATA/filename)
    if len(records)!=expected:
        errors.append(f"{filename}: expected {expected} records, found {len(records)}")
    pics=[x[1] for x in records]
    if None in pics:
        errors.append(f"{filename}: one or more records have no Pic Num")
    if len(set(pics))!=len(pics):
        errors.append(f"{filename}: Pic Num values are not unique")
    for name,pic in records:
        if pic is not None:
            check_image(P/folder/f"{prefix}_{pic:03d}.png",(128,128),f"{name} {prefix} portrait")
    return records

components=unique_pics("Components.txt","Components","Comp",49)
facilities=unique_pics("Facility.txt","Facilities","Facil",29)

factions=("Aurelian","Veyran","Khepri","Meridian","Outer","Helion")
hulls=("Pathfinder","Hauler","Frigate","Destroyer","Cruiser","Battleship",
       "Colonizer","Station","Corvette","ScienceVessel","Dreadnought","MobileShipyard")
for faction in factions:
    for hull in hulls:
        check_image(P/"Races"/faction/f"{faction}_Portrait_VoidReign{hull}.png",(128,128),f"{faction} {hull} portrait")
        check_image(P/"Races"/faction/f"{faction}_Mini_VoidReign{hull}.png",(36,36),f"{faction} {hull} mini")
    check_image(P/"Races"/faction/f"{faction}_Race_Portrait.png",(192,192),f"{faction} leader portrait")

for i in range(1,17):
    check_image(P/"Planets"/f"p{i:04d}.png",(128,128),f"planet object {i}")
check_image(P/"Planets"/"Planets.png",(288,72),"planet mini atlas")

biomes=("Starfield","Nebula","Pulsar","BlackHole","Magnetar","WarpHub")
layouts={"1024X768":660,"800X600":490}
system_text=(DATA/"SystemTypes.txt").read_text(encoding="utf-8-sig")
for biome in biomes:
    if not re.search(r"(?m)^Background Bitmap\s*:=\s*"+re.escape(biome)+r"\s*$",system_text):
        errors.append(f"SystemTypes.txt does not reference biome {biome}")
    check_image(P/"Systems"/f"{biome}.png",(128,128),f"{biome} system thumbnail")
    for layout,size in layouts.items():
        check_image(P/"Systems"/layout/f"{biome}.png",(size,size),f"{biome} {layout} system background")
    for variant in range(1,5):
        check_image(P/"Systems"/f"{biome}_V{variant}.png",(128,128),f"{biome} system scene variant {variant}")
        for layout,size in layouts.items():
            check_image(P/"Systems"/layout/f"{biome}_V{variant}.png",(size,size),f"{biome} {layout} scene variant {variant}")
    for i in range(1,10):
        check_image(P/"Systems"/f"{biome}Tile{i}.png",(72,72),f"{biome} tactical tile {i}")

check_image(P/"Game"/"Buttons"/"Main.png",(442,102),"main command atlas")
check_image(P/"Game"/"Buttons"/"Orders.png",(782,408),"order atlas")
check_image(P/"Game"/"General.png",(608,176),"general resource atlas")

# The asset manifests are integrity records; confirm every recorded checksum.
manifest_paths=[
 ROOT/"art-library"/"voidreign-art-native-components"/"GENERATION-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-native-components"/"ATLAS-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-system-biomes"/"GENERATION-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-faction-ships"/"GENERATION-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-planets"/"GENERATION-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-ui-icons"/"GENERATION-MANIFEST.json",
 ROOT/"art-library"/"voidreign-art-faction-portraits"/"GENERATION-MANIFEST.json",
]
for manifest_path in manifest_paths:
    if not manifest_path.is_file():
        errors.append(f"Missing art manifest: {manifest_path.relative_to(ROOT)}")
        continue
    try:
        manifest=json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest_path.name == "ATLAS-MANIFEST.json":
            for key in ("component_atlas", "facility_atlas"):
                item = manifest.get(key, {})
                rel = item.get("file")
                expected = item.get("sha256")
                if not rel or not expected:
                    errors.append(f"Atlas manifest entry missing path/hash: {key}")
                else:
                    path = ROOT / rel
                    if not path.is_file():
                        errors.append(f"Atlas file missing: {rel}")
                    elif sha(path).lower() != expected.lower():
                        errors.append(f"SHA-256 mismatch: {rel}")
                    else:
                        checks += 1
        records=manifest.get("assets",[])
        for item in records:
            pairs=(
                ("file","sha256"),
                ("source_file","source_sha256"),
                ("native_file","native_sha256"),
                ("portrait","portrait_sha256"),
                ("mini","mini_sha256"),
            )
            for path_key,hash_key in pairs:
                rel=item.get(path_key)
                expected=item.get(hash_key)
                if not rel or not expected: continue
                path=ROOT/rel
                if not path.is_file():
                    errors.append(f"Manifest file missing: {rel}")
                elif sha(path).lower()!=expected.lower():
                    errors.append(f"SHA-256 mismatch: {rel}")
                else: checks+=1
    except Exception as e:
        errors.append(f"Invalid manifest {manifest_path.name}: {e}")

# Ensure the generated native PNGs are not filtered out by the blanket *.png ignore.
probe=[
 "game-data/Pictures/Components/Comp_001.png",
 "game-data/Pictures/Facilities/Facil_001.png",
 "game-data/Pictures/Planets/Planets.png",
 "game-data/Pictures/Systems/Nebula.png",
 "game-data/Pictures/Game/Buttons/Main.png",
 "game-data/Pictures/Races/Aurelian/Aurelian_Mini_VoidReignFrigate.png",
]
for rel in probe:
    result=subprocess.run([GIT,"-C",str(ROOT),"check-ignore","-q",rel],capture_output=True)
    if result.returncode==0: errors.append(f"PNG remains ignored by Git: {rel}")

print(f"Image and manifest checks: {checks}")
print(f"Component portraits: {len(components)} unique Pic Num values")
print(f"Facility portraits: {len(facilities)} unique Pic Num values")
print(f"Faction hull sets: {len(factions)} x {len(hulls)} = {len(factions)*len(hulls)} portraits and minis")
print(f"System biomes: {len(biomes)}; scene variants: {len(biomes)*4}; variant backgrounds: {len(biomes)*4*len(layouts)}; tactical tiles: {len(biomes)*9}")
print(f"Planet/stellar objects: 16; command/order/resource icon atlases: 3")
print(f"Errors: {len(errors)}; warnings: {len(warnings)}")
for line in errors: print("ERROR:",line)
for line in warnings: print("WARNING:",line)
raise SystemExit(1 if errors else 0)

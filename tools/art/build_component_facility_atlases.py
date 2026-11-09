from __future__ import annotations

"""Build compact component/facility atlases from the same semantic glyphs as detail art."""

import hashlib
import json
import runpy
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"game-data"/"Pictures"
NATIVE=ROOT/"art-library"/"voidreign-art-native-components"
SIZE=384

module=runpy.run_path(str(ROOT/"tools"/"art"/"build_original_art.py"))
records=module["records"]
identify_component=module["identify_component"]
identify_facility=module["identify_facility"]
draw_symbol=module["draw_symbol"]
PALETTES=module["PALETTES"]
level_of=module["level_of"]
stable_seed=module["stable_seed"]
palette_for=module["palette_for"]

def make_symbol(name,kind,family,level,index):
    accent,light,dark=palette_for(family,name,index)
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    d=ImageDraw.Draw(im,"RGBA")
    draw_symbol(d,kind,accent,light,dark,level,stable_seed(name+"|"+kind+"|"+str(index)),False)
    return im.resize((36,36),Image.Resampling.LANCZOS)

def atlas(entries,identify,folder,filename,columns,rows):
    images=[]
    sorted_entries=sorted(entries,key=lambda x:int(x.get("Pic Num","0") or 0))
    for entry in sorted_entries:
        pic=int(entry["Pic Num"])
        kind,family=identify(entry["Name"])
        images.append(make_symbol(entry["Name"],kind,family,level_of(entry),pic))
    if len(images)>columns*rows:
        raise RuntimeError(f"{filename}: atlas capacity too small for {len(images)} entries")
    sheet=Image.new("RGBA",(columns*36,rows*36),(0,0,0,0))
    for i,im in enumerate(images):
        sheet.alpha_composite(im,((i%columns)*36,(i//columns)*36))
    path=OUT/folder/filename
    path.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(path,optimize=True)
    return {
        "file":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,
        "size":[sheet.width,sheet.height],
        "count":len(images),
        "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    }

components=records(ROOT/"game-data"/"Data"/"Components.txt")
facilities=records(ROOT/"game-data"/"Data"/"Facility.txt")
component=atlas(components,identify_component,"Components","Components.png",7,7)
facility=atlas(facilities,identify_facility,"Facilities","Facility.png",6,5)
manifest_path=NATIVE/"ATLAS-MANIFEST.json"
manifest={
    "title":"VOIDREIGN 36px component/facility icon atlases",
    "generated_at":datetime.now(timezone.utc).isoformat(),
    "generator":"tools/art/build_component_facility_atlases.py",
    "method":"The same semantic vector glyph definitions used by the 128px original component and facility portraits, rendered at 36px.",
    "component_atlas":component,
    "facility_atlas":facility,
}
NATIVE.mkdir(parents=True,exist_ok=True)
manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print(f"Components: {component['count']} unique cells, {component['size']}, {component['sha256']}")
print(f"Facilities: {facility['count']} unique cells, {facility['size']}, {facility['sha256']}")

from __future__ import annotations

"""Generate original VOIDREIGN ship miniatures and portraits for six factions."""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
RACES=ROOT/"game-data"/"Pictures"/"Races"
ARCH=ROOT/"art-library"/"voidreign-art-faction-ships"

FACTIONS={
 "Aurelian":{"body":(194,204,203),"light":(255,226,151),"dark":(65,85,103),"accent":(25,190,177),"engine":(70,230,236),"style":"winged"},
 "Veyran":{"body":(41,135,139),"light":(181,236,209),"dark":(15,56,80),"accent":(65,220,199),"engine":(47,186,255),"style":"crescent"},
 "Khepri":{"body":(82,83,76),"light":(190,153,79),"dark":(20,25,30),"accent":(232,166,45),"engine":(58,218,104),"style":"segmented"},
 "Meridian":{"body":(137,145,181),"light":(230,224,255),"dark":(39,37,81),"accent":(161,105,255),"engine":(91,159,255),"style":"crystal"},
 "Outer":{"body":(128,139,148),"light":(213,203,174),"dark":(37,52,67),"accent":(219,116,55),"engine":(255,157,81),"style":"industrial"},
 "Helion":{"body":(220,207,160),"light":(255,241,192),"dark":(83,69,45),"accent":(244,181,55),"engine":(255,224,109),"style":"radiant"},
}
HULLS={
 "Pathfinder":{"type":"needle","scale":.58,"width":.25},
 "Hauler":{"type":"cargo","scale":.90,"width":.70},
 "Frigate":{"type":"arrow","scale":.70,"width":.42},
 "Destroyer":{"type":"wing","scale":.80,"width":.54},
 "Cruiser":{"type":"twin","scale":.88,"width":.67},
 "Battleship":{"type":"capital","scale":1.0,"width":.82},
 "Colonizer":{"type":"ark","scale":.98,"width":.75},
 "Corvette":{"type":"dart","scale":.53,"width":.36},
 "Station":{"type":"station","scale":.96,"width":.88},
 "ScienceVessel":{"type":"science","scale":.82,"width":.56},
 "Dreadnought":{"type":"dread","scale":1.0,"width":.92},
 "MobileShipyard":{"type":"yard","scale":1.0,"width":.96},
}
# Order must match the native filenames and the 12 declared hull classes.
HULL_ORDER=("Pathfinder","Hauler","Frigate","Destroyer","Cruiser","Battleship",
            "Colonizer","Station","Corvette","ScienceVessel","Dreadnought","MobileShipyard")

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def rgba(color,alpha=255):return (*color,alpha)

def draw_ship(style:dict,hull:str,seed:int)->Image.Image:
 S=512
 im=Image.new("RGBA",(S,S),(0,0,0,0))
 shadow=Image.new("RGBA",(S,S),(0,0,0,0))
 d=ImageDraw.Draw(im,"RGBA"); sd=ImageDraw.Draw(shadow)
 body=style["body"]; light=style["light"]; dark=style["dark"]; accent=style["accent"]; engine=style["engine"]
 spec=HULLS[hull]; kind=spec["type"]; scale=spec["scale"]; faction=style["style"]
 # Core top-down silhouette. Bow faces right, engines sit aft at left.
 cx,cy=260,256
 length=392*scale; half=118*spec["width"]*scale
 x0=cx-length/2; x1=cx+length/2
 # Main hull geometry: each role has its own silhouette.
 if kind in ("needle","dart"):
  pts=[(x0,cy),(x0+length*.22,cy-half*.50),(x1-length*.08,cy-half*.15),(x1,cy),(x1-length*.08,cy+half*.15),(x0+length*.22,cy+half*.50)]
 elif kind=="arrow":
  pts=[(x0,cy),(x0+length*.19,cy-half*.52),(x1-length*.16,cy-half*.35),(x1,cy),(x1-length*.16,cy+half*.35),(x0+length*.19,cy+half*.52)]
 elif kind=="wing":
  pts=[(x0,cy),(x0+length*.25,cy-half*.38),(x0+length*.42,cy-half*1.1),(x0+length*.64,cy-half*.72),(x1-length*.13,cy-half*.30),(x1,cy),(x1-length*.13,cy+half*.30),(x0+length*.64,cy+half*.72),(x0+length*.42,cy+half*1.1),(x0+length*.25,cy+half*.38)]
 elif kind=="cargo":
  pts=[(x0,cy-half*.44),(x0+length*.18,cy-half*.62),(x1-length*.2,cy-half*.52),(x1,cy),(x1-length*.2,cy+half*.52),(x0+length*.18,cy+half*.62),(x0,cy+half*.44)]
 elif kind in ("twin","capital","dread","yard"):
  top=half*(1.0 if kind in ("dread","yard") else .90)
  pts=[(x0,cy),(x0+length*.14,cy-top*.48),(x0+length*.26,cy-top),(x0+length*.48,cy-top*.88),
       (x1-length*.18,cy-top*.48),(x1,cy),(x1-length*.18,cy+top*.48),
       (x0+length*.48,cy+top*.88),(x0+length*.26,cy+top),(x0+length*.14,cy+top*.48)]
 elif kind=="ark":
  pts=[(x0,cy),(x0+length*.10,cy-half*.42),(x0+length*.32,cy-half*.62),(x1-length*.14,cy-half*.44),
       (x1,cy),(x1-length*.14,cy+half*.44),(x0+length*.32,cy+half*.62),(x0+length*.10,cy+half*.42)]
 elif kind=="station":
  pts=[(cx-42,cy-44),(cx-30,cy-146),(cx+30,cy-146),(cx+42,cy-44),(cx+146,cy-30),(cx+146,cy+30),(cx+42,cy+44),(cx+30,cy+146),(cx-30,cy+146),(cx-42,cy+44),(cx-146,cy+30),(cx-146,cy-30)]
 elif kind=="science":
  pts=[(x0,cy),(x0+length*.25,cy-half*.45),(x0+length*.52,cy-half*.68),(x1-length*.12,cy-half*.26),(x1,cy),(x1-length*.12,cy+half*.26),(x0+length*.52,cy+half*.68),(x0+length*.25,cy+half*.45)]
 else: pts=[(x0,cy),(x1,cy-half),(x1,cy+half)]
 # Faction identity modifies the silhouette, not just colour.
 if faction=="winged" and kind not in ("station","cargo"):
  pts=[(x,y+math.sin((x-x0)/max(1,length)*math.pi)*half*.12) for x,y in pts]
 if faction=="crescent" and kind not in ("station","cargo"):
  # A curved crescent bow; keep the main form open at its rear.
  pts=[(x,y+(math.sin((x-x0)/max(1,length)*math.pi)-.35)*half*.16) for x,y in pts]
 if faction=="segmented":
  # Add serrated hardpoints later; segmented dorsal plates are part of the core shell.
  pass
 if faction=="crystal":
  pts=[(round(x/16)*16,round(y/16)*16) for x,y in pts]
 # soft engine glow behind the craft
 for oy in (-half*.36,0,half*.36):
  bx=x0+length*.08; by=cy+oy
  sd.ellipse((bx-28,by-30,bx+35,by+30),fill=rgba(engine,80))
 shadow=shadow.filter(ImageFilter.GaussianBlur(22)); im.alpha_composite(shadow)
 d=ImageDraw.Draw(im,"RGBA")
 # Engine nozzles.
 nozzle_count=3 if kind in ("capital","dread","yard","twin","station","ark") else 2
 for i in range(nozzle_count):
  oy=(i-(nozzle_count-1)/2)*half*.55
  r=18 if spec["scale"]>.8 else 13
  d.rounded_rectangle((x0-23,cy+oy-r,x0+15,cy+oy+r),radius=6,fill=rgba(dark),outline=rgba(light),width=5)
  d.ellipse((x0-28,cy+oy-r*.48,x0+4,cy+oy+r*.48),fill=rgba(engine,235))
 # Outer silhouette and layered armor.
 outline=[(int(x),int(y)) for x,y in pts]
 d.polygon(outline,fill=rgba(dark),outline=rgba(light),width=8)
 inset=[(cx+(x-cx)*.88,cy+(y-cy)*.82) for x,y in pts]
 d.polygon(inset,fill=rgba(body),outline=rgba(accent),width=4)
 # Raised dorsal spine / flight deck.
 spine=[(x0+length*.15,cy),(x0+length*.38,cy-half*.31),(x1-length*.23,cy-half*.18),
        (x1-length*.08,cy),(x1-length*.23,cy+half*.18),(x0+length*.38,cy+half*.31)]
 d.polygon(spine,fill=rgba(light),outline=rgba(dark),width=5)
 # Hull panels, faction-specific seams.
 d.line([(x0+length*.20,cy-half*.38),(x0+length*.27,cy),(x0+length*.20,cy+half*.38)],fill=rgba(accent),width=6)
 d.line([(x0+length*.44,cy-half*.26),(x0+length*.49,cy+half*.26)],fill=rgba(dark),width=4)
 d.line([(x1-length*.32,cy-half*.19),(x1-length*.23,cy),(x1-length*.32,cy+half*.19)],fill=rgba(accent),width=5)
 # Hull-class visual features.
 if kind=="cargo":
  for i in range(3):
   xx=x0+length*(.36+i*.15)
   box=(xx-18,cy-half*.36,xx+35,cy+half*.36)
   d.rounded_rectangle(box,radius=8,fill=rgba(dark),outline=rgba(light),width=5)
   d.line([(xx-7,cy),(xx+24,cy)],fill=rgba(accent),width=4)
 if kind in ("twin","capital","dread","yard"):
  # paired weapon batteries or dorsal hangars
  for xx in (cx-65,cx+35):
   for oy in (-half*.58,half*.58):
    d.rounded_rectangle((xx-28,cy+oy-16,xx+28,cy+oy+16),radius=7,fill=rgba(dark),outline=rgba(accent),width=5)
    d.line([(xx+12,cy+oy),(xx+54,cy+oy)],fill=rgba(light),width=5)
 if kind=="ark":
  # Population habitat modules and greenhouse domes.
  for xx in (cx-70,cx+30):
   d.ellipse((xx-29,cy-25,xx+29,cy+25),fill=rgba(accent),outline=rgba(light),width=5)
   d.arc((xx-20,cy-19,xx+20,cy+19),180,360,fill=rgba(light),width=5)
 if kind=="station":
  for a in range(0,360,90):
   rad=math.radians(a)
   ax=cx+math.cos(rad)*152; ay=cy+math.sin(rad)*152
   d.line([(cx+math.cos(rad)*58,cy+math.sin(rad)*58),(ax,ay)],fill=rgba(light),width=15)
   d.ellipse((ax-24,ay-24,ax+24,ay+24),fill=rgba(accent),outline=rgba(light),width=5)
 if kind=="science":
  # sensor dish at rear-mid section
  px=cx-10
  d.ellipse((px-53,cy-53,px+53,cy+53),outline=rgba(accent),width=7)
  d.ellipse((px-22,cy-22,px+22,cy+22),fill=rgba(light),outline=rgba(dark),width=5)
  d.line([(px,cy-53),(px,cy+53)],fill=rgba(dark),width=3)
 if kind=="yard":
  # exposed industrial arms and construction trusses
  for oy in (-half*.68,half*.68):
   d.line([(cx-25,cy+oy*.35),(cx+80,cy+oy),(cx+125,cy+oy)],fill=rgba(light),width=13)
   d.rectangle((cx+88,cy+oy-23,cx+130,cy+oy+23),fill=rgba(accent),outline=rgba(dark),width=5)
 if kind=="dread":
  for oy in (-half*.78,half*.78):
   d.polygon([(cx+40,cy+oy),(cx+110,cy+oy-15),(cx+110,cy+oy+15)],fill=rgba(accent),outline=rgba(light))
 # Faction identity marks and lights.
 if faction=="winged":
  for oy in (-1,1):
   d.line([(cx-40,cy),(cx-8,cy+oy*half*.65),(cx+64,cy+oy*half*.48)],fill=rgba(light),width=8)
 elif faction=="crescent":
  d.arc((cx-100,cy-half*.62,cx+95,cy+half*.62),260,100,fill=rgba(accent),width=8)
 elif faction=="segmented":
  for xx in (cx-74,cx-25,cx+24,cx+73):
   d.line([(xx,cy-half*.20),(xx+10,cy+half*.20)],fill=rgba(light),width=8)
 elif faction=="crystal":
  d.polygon([(cx-35,cy),(cx,cy-42),(cx+35,cy),(cx,cy+42)],fill=rgba(accent),outline=rgba(light))
 elif faction=="industrial":
  for xx in (cx-88,cx+90):
   d.rectangle((xx-14,cy-half*.28,xx+14,cy+half*.28),fill=rgba(accent),outline=rgba(light),width=4)
 elif faction=="radiant":
  for a in range(0,360,45):
   rad=math.radians(a)
   px=cx+math.cos(rad)*70; py=cy+math.sin(rad)*max(26,half*.30)
   d.ellipse((px-7,py-7,px+7,py+7),fill=rgba(light))
 # Cockpit / command bridge.
 d.ellipse((cx+45,cy-13,cx+75,cy+13),fill=rgba(engine),outline=rgba(dark),width=5)
 d.ellipse((cx+52,cy-7,cx+65,cy+7),fill=(232,250,255,245))
 # Window/port lights along the upper flank.
 for i in range(4):
  px=cx-90+i*36
  if x0+24<px<x1-28:
   d.ellipse((px-4,cy-half*.25-5,px+4,cy-half*.25+5),fill=rgba(light,230))
 # Final anti-aliased output.
 return im.resize((128,128),Image.Resampling.LANCZOS)

def main():
 records=[]
 for faction,style in FACTIONS.items():
  folder=RACES/faction; folder.mkdir(parents=True,exist_ok=True)
  for i,hull in enumerate(HULL_ORDER):
   portrait=draw_ship(style,hull,0x5150+i+sum(ord(c) for c in faction))
   portrait_path=folder/f"{faction}_Portrait_VoidReign{hull}.png"
   portrait.save(portrait_path,optimize=True,compress_level=9)
   mini=portrait.resize((36,36),Image.Resampling.LANCZOS)
   mini_path=folder/f"{faction}_Mini_VoidReign{hull}.png"
   mini.save(mini_path,optimize=True,compress_level=9)
   records.append({"faction":faction,"hull":hull,"portrait":portrait_path.relative_to(ROOT).as_posix(),
                   "mini":mini_path.relative_to(ROOT).as_posix(),"portrait_size":[128,128],"mini_size":[36,36],
                   "portrait_sha256":sha(portrait_path),"mini_sha256":sha(mini_path)})
 ARCH.mkdir(parents=True,exist_ok=True)
 manifest={"title":"VOIDREIGN faction-specific ship art","generated_at":datetime.now(timezone.utc).isoformat(),
           "generator":"tools/art/generate_ship_art.py","method":"Original procedural vector ship silhouettes, hull plating, faction motifs and propulsion lighting",
           "factions":list(FACTIONS),"hulls":list(HULL_ORDER),"assets":records}
 (ARCH/"GENERATION-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print(f"Generated {len(records)} faction-specific hull sets ({len(records)} portraits and {len(records)} minis).")
 print(f"Manifest: {ARCH/'GENERATION-MANIFEST.json'}")
if __name__=="__main__":main()

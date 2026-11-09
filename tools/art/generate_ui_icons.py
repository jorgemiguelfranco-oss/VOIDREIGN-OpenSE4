from __future__ import annotations

"""Regenerate VOIDREIGN's main command, order and resource icon sheets."""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT/"game-data"/"Pictures"/"Game"
BUTTONS=GAME/"Buttons"
GENERAL=GAME/"General.png"
ARCH=ROOT/"art-library"/"voidreign-art-ui-icons"
S=136

MAIN={
 0:"menu",1:"colonies",2:"planets",3:"ships",4:"designs",5:"status",
 6:"research",7:"empires",8:"log",9:"queues",10:"help",11:"turn",12:"settings"
}
ORDER={
 (0,0):"move",(0,1):"waypoint",(0,2):"colonize",(0,3):"explore",(0,4):"attack",(0,5):"warp",
 (0,6):"fleet",(0,8):"resupply",(0,9):"repair",(0,10):"clear",(0,11):"buildqueue",
 (0,12):"sentry",(0,13):"patrol",(0,14):"repeat",(0,15):"launch_remote",(0,16):"recover_remote",
 (0,18):"scrap",(0,19):"load",(0,20):"drop",(0,22):"minister",
 (1,0):"strategy",(1,3):"abandon",(1,5):"stellar",(1,11):"sweep_mines",(1,12):"use_component",
 (1,13):"use_facility",(1,17):"jettison",(1,18):"scrap_facility",(1,21):"cloak",(1,22):"decloak",
 (2,0):"rename",(2,1):"view_orders",(2,2):"convert",(2,4):"replay_play",(2,5):"replay_ship",
 (2,6):"replay_step",(2,7):"replay_rewind",(2,8):"blank",(2,9):"launch_recover",(2,10):"cargo_transfer"
}
PALETTE={
 "normal":((75,157,203),(218,239,255),(9,24,43)),
 "hover":((64,221,235),(249,255,255),(13,50,72)),
 "lit":((238,186,79),(255,246,194),(57,42,25)),
 "dim":((67,90,111),(122,148,171),(9,16,28)),
 "pressed":((255,205,105),(255,251,222),(42,47,55)),
}

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""): h.update(c)
 return h.hexdigest()

def poly(d,pts,fill,outline=None,width=5):
 d.polygon(pts,fill=fill,outline=outline)
def line(d,pts,c,w=5):
 d.line(pts,fill=c,width=w,joint="curve")
def ell(d,box,fill=None,outline=None,w=5):
 d.ellipse(box,fill=fill,outline=outline,width=w)
def rr(d,box,fill=None,outline=None,r=10,w=5):
 d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)

def glyph(kind:str,accent,light,dark)->Image.Image:
 im=Image.new("RGBA",(S,S),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA")
 c=tuple(accent)+(255,); l=tuple(light)+(255,); k=tuple(dark)+(255,)
 cx=cy=S//2
 if kind in ("menu","log","queues","view_orders","buildqueue"):
  if kind=="menu":
   for y in (35,61,87):
    rr(d,(25,y-8,111,y+8),k,l,8,5)
    ell(d,(34,y-4,42,y+4),c,None,1)
  elif kind=="log":
   rr(d,(27,18,109,118),k,l,9,6)
   for y in (39,59,79,99):
    ell(d,(39,y-4,47,y+4),c,None,1);line(d,[(56,y),(95,y)],l,5)
  elif kind=="queues":
   for i in range(3):
    rr(d,(22+i*28,38-i*12,47+i*28,101-i*12),k,l,5,5)
    line(d,[(27+i*28,55-i*12),(42+i*28,55-i*12)],c,4)
   line(d,[(18,108),(119,108)],l,6)
  elif kind=="view_orders":
   rr(d,(27,18,109,118),k,l,8,5)
   for y in (40,62,84,106):
    line(d,[(38,y),(44,y+6),(53,y-8)],c,5)
    line(d,[(62,y),(98,y)],l,4)
  else:
   line(d,[(18,88),(118,88)],l,7)
   for i in range(3):
    rr(d,(23+i*30,47,47+i*30,84),k,c,5,4)
   line(d,[(18,101),(118,101)],c,5)
 elif kind in ("crystal","leaf","nucleus"):
  if kind=="crystal":
   poly(d,[(68,18),(106,49),(93,106),(68,121),(43,106),(30,49)],k,l,7)
   line(d,[(68,18),(68,121)],c,5)
   line(d,[(30,49),(68,66),(106,49)],l,4)
   line(d,[(43,106),(68,66),(93,106)],c,4)
  elif kind=="leaf":
   poly(d,[(22,99),(33,48),(78,20),(113,25),(111,66),(74,104),(22,99)],k,l,7)
   line(d,[(25,105),(102,33)],c,7)
   line(d,[(57,76),(51,49)],l,4)
   line(d,[(73,61),(98,64)],l,4)
  else:
   ell(d,(42,42,94,94),k,l,6)
   for angle in (0,60,120):
    d.arc((18,38+angle//3,118,100+angle//3),angle,angle+180,fill=c,width=6)
   ell(d,(59,59,77,77),c,l,3)
 elif kind in ("colonies","help","settings"):
  if kind=="colonies":
   poly(d,[(18,76),(68,34),(118,76)],k,l,7)
   rr(d,(28,72,108,112),k,l,6,5)
   rr(d,(48,77,87,112),c,l,4,4)
   for x in (36,93): ell(d,(x-6,53,x+6,65),c,l,3)
  elif kind=="help":
   ell(d,(17,17,119,119),k,l,7)
   d.arc((40,32,98,91),190,500,fill=c,width=11)
   ell(d,(61,95,75,109),l,None,1)
  else:
   ell(d,(35,35,101,101),k,l,7)
   for a in range(0,360,45):
    rad=math.radians(a)
    line(d,[(cx+39*math.cos(rad),cy+39*math.sin(rad)),(cx+57*math.cos(rad),cy+57*math.sin(rad))],c,8)
   ell(d,(52,52,84,84),c,l,4)
 elif kind in ("planets","research","empires","status"):
  if kind=="planets":
   ell(d,(21,21,115,115),k,l,7)
   d.arc((21,39,116,97),190,350,fill=c,width=7)
   line(d,[(27,65),(111,65)],l,4)
   ell(d,(57,37,84,64),c,None,1)
  elif kind=="research":
   ell(d,(54,54,82,82),c,l,5)
   for box in ((17,45,119,91),(44,17,92,119),(30,30,106,106)):
    d.arc(box,0,360,fill=l,width=5)
   for x,y in ((29,67),(106,67),(68,28),(68,106)):
    ell(d,(x-6,y-6,x+6,y+6),c,l,2)
  elif kind=="empires":
   nodes=[(68,24),(25,78),(111,78),(68,112)]
   for p in nodes: line(d,[(68,68),p],l,5)
   for i,(x,y) in enumerate(nodes): ell(d,(x-12,y-12,x+12,y+12),c,l,4)
   ell(d,(53,53,83,83),k,l,6)
  else:
   poly(d,[(68,20),(110,37),(103,89),(68,117),(33,89),(26,37)],k,l,6)
   for i,h in enumerate((30,48,67)):
    line(d,[(48+i*14,91-h),(48+i*14,91)],c,9)
 elif kind in ("ships","designs","move","waypoint","attack","fleet","launch_remote","recover_remote","replay_ship"):
  if kind in ("ships","move","attack","replay_ship"):
   poly(d,[(117,68),(42,27),(54,60),(23,68),(54,76),(42,109)],k,l,6)
   line(d,[(49,68),(112,68)],c,5)
   if kind=="attack":
    ell(d,(78,47,111,79),None,c,5)
    line(d,[(94,31),(94,95)],l,4)
  elif kind=="designs":
   rr(d,(24,22,102,112),k,l,7,5)
   line(d,[(40,49),(83,49)],c,5);line(d,[(40,66),(83,66)],l,4)
   line(d,[(40,83),(70,83)],l,4)
   line(d,[(83,24),(111,12)],c,7)
  elif kind=="waypoint":
   pts=[(25,92),(56,47),(90,89),(111,27)]
   for a,b in zip(pts,pts[1:]):line(d,[a,b],c,6)
   for x,y in pts:ell(d,(x-8,y-8,x+8,y+8),k,l,4)
  elif kind=="fleet":
   for oy in (-24,0,24):
    poly(d,[(110,68+oy),(47,45+oy),(58,68+oy),(47,91+oy)],k,l,4)
   line(d,[(23,20),(23,116)],c,4)
  else:
   if kind=="launch_remote":
    poly(d,[(115,68),(58,38),(67,65),(48,68),(67,71),(58,98)],k,l,5)
    line(d,[(18,68),(48,68)],c,5)
    line(d,[(29,46),(18,68),(29,90)],c,4)
   elif kind=="recover_remote":
    poly(d,[(115,68),(58,38),(67,65),(48,68),(67,71),(58,98)],k,l,5)
    line(d,[(18,68),(48,68)],c,5); line(d,[(36,47),(48,68),(36,89)],c,4)
 elif kind in ("turn","repeat","patrol","warp","stellar","cloak","decloak","convert","replay_play","replay_step","replay_rewind"):
  if kind in ("turn","replay_play"):
   if kind=="turn":
    poly(d,[(37,21),(99,68),(37,115)],c,l,6)
    line(d,[(22,68),(37,68)],l,5)
   else: poly(d,[(43,23),(111,68),(43,113)],c,l,6)
  elif kind in ("repeat","patrol"):
   d.arc((22,22,114,114),45,315,fill=c,width=10)
   poly(d,[(106,22),(120,48),(90,43)],c,l,3)
   if kind=="patrol":ell(d,(53,53,83,83),None,l,5)
  elif kind=="warp":
   for r in (17,34,51):ell(d,(cx-r,cy-r,cx+r,cy+r),None,c,5)
   ell(d,(58,58,78,78),l,None,1)
  elif kind=="stellar":
   for a in range(0,360,45):
    rad=math.radians(a);line(d,[(cx+25*math.cos(rad),cy+25*math.sin(rad)),(cx+53*math.cos(rad),cy+53*math.sin(rad))],c,5)
   ell(d,(51,51,85,85),l,c,4)
  elif kind in ("cloak","decloak"):
   ell(d,(24,34,112,102),None,c,7)
   if kind=="cloak": line(d,[(27,112),(109,20)],l,8)
   else:
    for x in (37,68,99):ell(d,(x-5,63,x+5,73),l,None,1)
  elif kind=="convert":
   line(d,[(24,45),(107,45)],c,10);poly(d,[(93,25),(115,45),(93,65)],c,l,3)
   line(d,[(112,89),(29,89)],l,10);poly(d,[(43,69),(21,89),(43,109)],l,c,3)
  elif kind=="replay_step":
   poly(d,[(29,28),(79,68),(29,108)],c,l,5);line(d,[(91,28),(91,108)],l,8)
  elif kind=="replay_rewind":
   poly(d,[(105,28),(55,68),(105,108)],c,l,5);poly(d,[(57,28),(17,68),(57,108)],l,c,4)
 elif kind in ("resupply","repair","clear","buildqueue","sentry","scrap","load","drop","minister",
               "strategy","abandon","sweep_mines","use_component","use_facility","jettison","rename",
               "launch_recover","cargo_transfer","scrap_facility","blank"):
  if kind in ("resupply","load","drop","jettison","cargo_transfer"):
   rr(d,(37,37,99,101),k,l,7,6)
   line(d,[(49,51),(87,51)],c,5);line(d,[(49,68),(87,68)],c,5)
   if kind in ("load","cargo_transfer"):poly(d,[(18,54),(31,54),(31,42),(48,61),(31,80),(31,68),(18,68)],c,l,3)
   if kind=="drop":poly(d,[(118,54),(105,54),(105,42),(88,61),(105,80),(105,68),(118,68)],c,l,3)
   if kind=="jettison":line(d,[(68,15),(68,41)],c,6);poly(d,[(54,29),(68,43),(82,29)],c,l,3)
  elif kind in ("repair","use_component"):
   line(d,[(35,96),(89,42)],l,15);ell(d,(75,18,115,58),None,c,8)
   line(d,[(87,31),(100,45)],c,6)
  elif kind in ("clear","scrap","scrap_facility"):
   rr(d,(28,28,108,108),k,l,8,6)
   line(d,[(43,43),(93,93)],c,10);line(d,[(93,43),(43,93)],c,10)
  elif kind=="buildqueue":
   for i in range(3):rr(d,(24+i*30,40-i*10,50+i*30,90-i*10),k,l,4,4)
   line(d,[(20,108),(116,108)],c,6)
  elif kind=="sentry":
   d.arc((16,31,120,105),180,360,fill=c,width=9)
   ell(d,(52,49,84,81),l,c,5)
  elif kind=="minister":
   ell(d,(43,21,93,71),c,l,5)
   rr(d,(27,73,109,119),k,l,16,6)
   line(d,[(37,94),(99,94)],c,5)
  elif kind=="strategy":
   ell(d,(20,20,116,116),None,l,8);ell(d,(43,43,93,93),None,c,6)
   line(d,[(68,68),(111,23)],c,7);ell(d,(101,13,119,31),l,None,1)
  elif kind=="abandon":
   ell(d,(24,24,112,112),k,l,5);poly(d,[(68,39),(88,64),(68,88),(48,64)],c,l,4)
   line(d,[(68,86),(68,120)],l,6)
  elif kind=="sweep_mines":
   ell(d,(50,50,86,86),c,l,5)
   for a in range(0,360,45):
    rad=math.radians(a);line(d,[(68+22*math.cos(rad),68+22*math.sin(rad)),(68+49*math.cos(rad),68+49*math.sin(rad))],l,4)
   d.arc((13,13,123,123),195,330,fill=c,width=5)
  elif kind=="use_facility":
   poly(d,[(17,62),(68,22),(119,62)],k,l,5)
   rr(d,(29,60,107,111),k,l,3,5)
   rr(d,(55,77,81,111),c,l,4,3)
  elif kind=="rename":
   line(d,[(33,103),(92,44)],l,12);poly(d,[(88,28),(111,12),(120,23),(98,45)],c,l,4)
  elif kind=="launch_recover":
   poly(d,[(68,18),(105,65),(80,65),(80,116),(56,116),(56,65),(31,65)],c,l,5)
  else:
   ell(d,(22,22,114,114),None,c,7);line(d,[(42,68),(94,68)],l,8)
 elif kind in ("explore","research","sensor"):
  ell(d,(17,17,119,119),None,c,7)
  for r in (22,42):ell(d,(68-r,68-r,68+r,68+r),None,l,4)
  line(d,[(68,68),(108,27)],c,6)
 else:
  # Distinct fallback glyph: central reticle with four directional ticks.
  ell(d,(46,46,90,90),None,c,7)
  for a in range(0,360,90):
   rad=math.radians(a);line(d,[(68+29*math.cos(rad),68+29*math.sin(rad)),(68+54*math.cos(rad),68+54*math.sin(rad))],l,6)
 return im

def make_cell(kind,state,states=4):
 names=("normal","hover","lit","dim","pressed")
 accent,light,dark=PALETTE[names[state]]
 im=Image.new("RGBA",(S,S),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA")
 # Every cell is a consistent brushed-metal plate with clean beveled edge.
 rr(d,(4,4,S-4,S-4),tuple(dark)+(255,),tuple(accent)+(255,),17,6)
 rr(d,(10,10,S-10,S-10),None,tuple(light)+(130,),13,2)
 # Small top/bottom catchlights give the same bevel language to each icon.
 line(d,[(25,17),(S-25,17)],tuple(light)+(95,),2)
 line(d,[(25,S-18),(S-25,S-18)],tuple(accent)+(100,),2)
 icon=glyph(kind,accent,light,dark)
 if state==3:
  icon=icon.copy()
  alpha=icon.getchannel("A").point(lambda a:int(a*.42))
  icon.putalpha(alpha)
 im.alpha_composite(icon.resize((92,92),Image.Resampling.LANCZOS),(22,22))
 return im.resize((34,34),Image.Resampling.LANCZOS)

def resource_icon(kind:str)->Image.Image:
 accent,light,dark={
  "research":((123,179,244),(227,245,255),(30,72,130)),
  "intelligence":((170,146,255),(234,226,255),(62,50,134)),
  "minerals":((218,173,92),(255,232,164),(104,73,35)),
  "organics":((91,199,123),(203,250,173),(33,103,58)),
  "radioactives":((122,214,107),(231,255,176),(44,96,37)),
  "population":((74,196,214),(208,250,255),(29,102,118)),
 }[kind]
 # Larger 128px transparent icon without a button plate.
 im=glyph({"research":"research","intelligence":"sentry","minerals":"crystal","organics":"leaf","radioactives":"nucleus","population":"empires"}[kind],accent,light,dark)
 return im

def main():
 # Main command sheet: 13 columns x 3 visual states (34px cells).
 main=Image.new("RGBA",(13*34,3*34),(0,0,0,0))
 states=("normal","hover","pressed")
 for col,kind in MAIN.items():
  for row,state in enumerate(states):
   main.alpha_composite(make_cell(kind,("normal","hover","pressed").index(state)),(col*34,row*34))
 main.save(BUTTONS/"Main.png",optimize=True)
 # Order sheet: 23 columns x 12 rows (3 bands, four states per band).
 orders=Image.new("RGBA",(23*34,12*34),(0,0,0,0))
 for (band,col),kind in ORDER.items():
  for state in range(4):
   orders.alpha_composite(make_cell(kind,state),(col*34,(band*4+state)*34))
 orders.save(BUTTONS/"Orders.png",optimize=True)
 # Resource/research/population icons: replace only the six original icon regions,
 # preserving all other general/status artwork in the established 608x176 sheet.
 general=Image.open(GENERAL).convert("RGBA")
 labels=("research","intelligence","minerals","organics","radioactives","population")
 for i,kind in enumerate(labels):
  icon=resource_icon(kind)
  large=icon.resize((32,32),Image.Resampling.LANCZOS)
  small=large.resize((16,16),Image.Resampling.LANCZOS)
  general.paste((0,0,0,0),(i*16,0,i*16+16,16))
  general.alpha_composite(small,(i*16,0))
  general.paste((0,0,0,0),(i*32,32,i*32+32,64))
  general.alpha_composite(large,(i*32,32))
 general.save(GENERAL,optimize=True)
 # Manifest / checksums for the three original UI sheets.
 ARCH.mkdir(parents=True,exist_ok=True)
 records=[]
 for p in (BUTTONS/"Main.png",BUTTONS/"Orders.png",GENERAL):
  records.append({"file":p.relative_to(ROOT).as_posix(),"size":list(Image.open(p).size),"sha256":sha(p)})
 manifest={"title":"VOIDREIGN original command, order and economy icons","generated_at":datetime.now(timezone.utc).isoformat(),
           "generator":"tools/art/generate_ui_icons.py","method":"Custom semantic vector glyphs, metal plates, bevel states and category-specific colours",
           "main_commands":MAIN,"orders":{f"{a}:{b}":c for (a,b),c in ORDER.items()},
           "economy_icons":list(labels),"assets":records}
 (ARCH/"GENERATION-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print("Regenerated 13 command columns x 3 states, 40 order icons x 4 states and 6 large/small economy icons.")
 print(f"Manifest: {ARCH/'GENERATION-MANIFEST.json'}")
if __name__=="__main__":main()

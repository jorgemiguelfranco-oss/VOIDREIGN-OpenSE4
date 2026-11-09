from __future__ import annotations

"""Generate original VOIDREIGN planet, star, asteroid, storm and warp-point art."""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"game-data"/"Pictures"/"Planets"
ARCH=ROOT/"art-library"/"voidreign-art-planets"
S=256
PALETTES=[
 ("temperate",(37,102,151),(43,134,82),(185,197,176),"earth"),
 ("yellow-star",(255,192,64),(255,249,198),(255,106,30),"star"),
 ("ice",(112,183,209),(207,232,238),(243,249,255),"ice"),
 ("gas-giant",(157,107,69),(225,193,142),(98,69,71),"gas"),
 ("super-terrestrial",(59,126,123),(111,177,107),(204,204,175),"earth"),
 ("desert",(171,98,52),(229,173,99),(92,55,45),"desert"),
 ("asteroids",(118,131,150),(178,174,158),(57,65,84),"asteroids"),
 ("ion-storm",(63,91,154),(123,174,223),(203,228,255),"storm"),
 ("warp-point",(66,115,190),(161,128,255),(90,220,240),"warp"),
 ("ocean",(16,89,139),(52,178,190),(151,225,230),"ocean"),
 ("volcanic",(129,48,35),(231,112,48),(255,204,113),"volcanic"),
 ("lava",(73,35,39),(193,62,30),(255,153,62),"lava"),
 ("ringed-giant",(119,91,59),(224,183,121),(80,68,62),"ringed"),
 ("barren",(107,104,93),(172,153,117),(65,61,55),"barren"),
 ("crystal",(71,103,151),(143,189,232),(219,236,255),"crystal"),
 ("ancient",(73,108,96),(147,169,111),(224,202,131),"ancient"),
]

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def fractal_noise(size:int,seed:int,octaves=(4,8,16,32,64))->np.ndarray:
 rng=np.random.default_rng(seed)
 acc=np.zeros((size,size),dtype=np.float32); total=0.0
 for octave in octaves:
  grid=rng.random((octave,octave),dtype=np.float32)
  im=Image.fromarray(np.uint8(grid*255),"L").resize((size,size),Image.Resampling.BICUBIC)
  layer=np.asarray(im,dtype=np.float32)/255.0
  weight=1.0/(octave**.25)
  acc+=layer*weight; total+=weight
 return acc/max(total,1e-6)

def planet(kind:str,seed:int)->Image.Image:
 yy,xx=np.mgrid[0:S,0:S]
 nx=(xx-(S-1)/2)/(S*.43); ny=(yy-(S-1)/2)/(S*.43)
 r2=nx*nx+ny*ny
 inside=r2<=1.0
 z=np.sqrt(np.clip(1-r2,0,1))
 light=np.array([-0.52,-0.58,0.72],dtype=np.float32); light/=np.linalg.norm(light)
 dot=np.clip(nx*light[0]+ny*light[1]+z*light[2],0,1)
 ambient=.14+.86*dot**.72
 low=fractal_noise(S,seed,(3,5,9,17,33,65))
 high=fractal_noise(S,seed+91,(32,64,128))
 idx=next(i for i,p in enumerate(PALETTES) if p[4]==kind)
 _,c0,c1,c2,_=PALETTES[idx]
 if kind in ("earth","temperate","super-terrestrial","ocean","ancient","barren","desert","volcanic","lava","crystal","ice"):
  mask=low>.53
  t=np.clip((low-.26)/.52,0,1)
  base=np.empty((S,S,3),dtype=np.float32)
  for c in range(3):
   base[:,:,c]=c0[c]*(1-t)+c1[c]*t
  if kind in ("earth","temperate","super-terrestrial","ancient"):
   # Coastline-like continent edges with subtle mountain ridges.
   mountains=np.clip((high-.60)*4,0,.45)
   for c in range(3): base[:,:,c]+=mountains*c2[c]*.32
   coast=np.clip(1-np.abs(low-.53)*10,0,1)*.22
   for c in range(3): base[:,:,c]=base[:,:,c]*(1-coast)+c2[c]*coast
  elif kind=="ocean":
   icecap=np.clip((np.abs(ny)-.70)*4,0,.65)
   for c in range(3): base[:,:,c]=base[:,:,c]*(1-icecap)+c2[c]*icecap
  elif kind in ("desert","barren","volcanic","lava"):
   cracks=np.clip((high-.75)*3,0,1)
   for c in range(3): base[:,:,c]*=1-cracks*.65
  elif kind=="crystal":
   facets=(np.sin((nx+ny*1.2)*27)+np.sin((ny-nx*.8)*19))*.10
   for c in range(3): base[:,:,c]+=facets*c2[c]
  albedo=base
  if kind=="ice":
   ice=np.clip((low-.4)*2,0,.8)
   for c in range(3): albedo[:,:,c]=albedo[:,:,c]*(1-ice)+c2[c]*ice
 elif kind in ("gas","ringed"):
  bands=(np.sin(ny*31+low*4)+.55*np.sin(ny*59+high*6))*.5
  t=np.clip(.5+bands*.42,0,1)
  albedo=np.empty((S,S,3),dtype=np.float32)
  for c in range(3): albedo[:,:,c]=c0[c]*(1-t)+c1[c]*t
  storm=np.exp(-((nx+.20)**2/.11+(ny-.15)**2/.04))
  for c in range(3): albedo[:,:,c]=albedo[:,:,c]*(1-storm*.55)+c2[c]*storm*.55
 else:
  albedo=np.empty((S,S,3),dtype=np.float32)
  for c in range(3): albedo[:,:,c]=c0[c]*(1-low)+c1[c]*low
 rgb=albedo*ambient[:,:,None]
 # Fine clouds, atmospheric edge glow and night-side rim.
 if kind in ("earth","temperate","super-terrestrial","ocean","gas","ringed","ice"):
  clouds=np.clip((high-.67)*1.7,0,.55)
  rgb=rgb*(1-clouds[:,:,None]*.30)+np.asarray(c2)[None,None,:]*clouds[:,:,None]*.30
 # Specular highlight based on surface normal and view direction.
 spec=np.clip((nx*.24+ny*.20+z*.94-1.03)*12,0,1)**5*.55
 rgb=rgb*(1-spec[:,:,None])+255*spec[:,:,None]
 arr=np.zeros((S,S,4),dtype=np.uint8)
 arr[:,:,:3]=np.clip(rgb,0,255).astype(np.uint8)
 # Crisp limb, fully transparent outside the sphere.
 edge=np.clip((1.015-np.sqrt(r2))*100,0,1)
 arr[:,:,3]=np.where(inside,255,0).astype(np.uint8)
 im=Image.fromarray(arr,"RGBA")
 # Atmospheric rim.
 glow=Image.new("RGBA",(S,S),(0,0,0,0))
 gd=ImageDraw.Draw(glow)
 rad=S*.43
 gd.ellipse(((S-2*rad)/2,(S-2*rad)/2,(S+2*rad)/2,(S+2*rad)/2),outline=(*c2,110),width=4)
 glow=glow.filter(ImageFilter.GaussianBlur(5))
 im.alpha_composite(glow)
 # Subtle ringed giant halo drawn behind sphere and masked under the disc.
 if kind=="ringed":
  ring=Image.new("RGBA",(S,S),(0,0,0,0)); rd=ImageDraw.Draw(ring)
  rd.ellipse((18,86,238,170),outline=(*c2,220),width=13)
  rd.ellipse((23,92,233,164),outline=(*c1,170),width=4)
  ring.alpha_composite(im)
  # Redraw planet above its near/far ring to create occlusion.
  ring.alpha_composite(im)
  im=ring
 # volcanic/lava hot fissures are accent points on the night side.
 if kind in ("volcanic","lava"):
  d=ImageDraw.Draw(im)
  for k in range(7):
   x0=int(S*.25+(k*29)%110); y0=int(S*.35+(k*37)%100)
   d.line([(x0,y0),(x0+10,y0+13),(x0+7,y0+24)],fill=(*c2,180),width=2)
 return im.resize((128,128),Image.Resampling.LANCZOS)

def special_icon(kind:str,seed:int)->Image.Image:
 im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im,"RGBA")
 rng=np.random.default_rng(seed)
 if kind in ("yellow-star","star"):
  cx=cy=S/2
  for r,a in ((92,20),(68,32),(42,90),(24,180)):
   d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,185,65,a))
  for k in range(36):
   angle=k*math.tau/36
   r0=43; r1=60+int(rng.integers(0,30))
   d.line([(cx+math.cos(angle)*r0,cy+math.sin(angle)*r0),
           (cx+math.cos(angle)*r1,cy+math.sin(angle)*r1)],fill=(255,211,107,125),width=2)
  d.ellipse((cx-27,cy-27,cx+27,cy+27),fill=(255,250,210,255))
 elif kind=="asteroids":
  for _ in range(95):
   x=int(rng.integers(10,246)); y=int(rng.integers(10,246)); r=int(rng.integers(2,9))
   col=(int(rng.integers(70,150)),int(rng.integers(78,143)),int(rng.integers(89,155)),255)
   pts=[(x+math.cos(a*math.tau/6)*r*rng.uniform(.7,1.3),y+math.sin(a*math.tau/6)*r*rng.uniform(.7,1.3)) for a in range(6)]
   d.polygon(pts,fill=col,outline=(200,205,214,150))
 elif kind in ("ion-storm","storm"):
  for k in range(9):
   box=(20+k*5,40+k*9,236-k*5,216-k*4)
   d.arc(box,180+k*13,500-k*9,fill=(74+k*8,152+k*9,235,170-k*7),width=5)
  d.ellipse((103,104,154,155),fill=(195,230,255,230))
 elif kind in ("warp-point","warp"):
  for k in range(8):
   r=105-k*10
   d.ellipse((128-r,128-r,128+r,128+r),outline=(66+k*18,165+k*10,233,210-k*14),width=5)
  d.ellipse((106,106,150,150),fill=(221,244,255,245))
 else:
  return planet("earth",seed)
 return im.resize((128,128),Image.Resampling.LANCZOS)

def main():
 images=[]
 for idx,(name,c0,c1,c2,kind) in enumerate(PALETTES):
  if kind in ("star","asteroids","storm","warp"):
   im=special_icon(kind,0x7000+idx)
  else:
   im=planet(kind,0x7000+idx)
  p=DIR/f"p{idx+1:04d}.png"; im.save(p,optimize=True)
  images.append(im)
 # Atlas is 8 columns x 2 rows of 36x36 cells.
 atlas=Image.new("RGBA",(288,72),(0,0,0,0))
 for i,im in enumerate(images):
  mini=im.resize((36,36),Image.Resampling.LANCZOS)
  atlas.alpha_composite(mini,((i%8)*36,(i//8)*36))
 atlas.save(DIR/"Planets.png",optimize=True)
 records=[]
 for i,(name,*_) in enumerate(PALETTES,1):
  p=DIR/f"p{i:04d}.png"
  records.append({"file":p.relative_to(ROOT).as_posix(),"id":i-1,"kind":name,"size":[128,128],"sha256":sha(p)})
 p=DIR/"Planets.png"
 records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"planet-atlas","size":[288,72],"sha256":sha(p)})
 ARCH.mkdir(parents=True,exist_ok=True)
 manifest={"title":"VOIDREIGN planetary and stellar object art","generated_at":datetime.now(timezone.utc).isoformat(),
           "generator":"tools/art/generate_planet_art.py","method":"Procedural 3D sphere shading, multi-scale surface noise, atmospheric rim and original stellar/field icons",
           "assets":records}
 (ARCH/"GENERATION-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print(f"Generated {len(images)} original stellar/planetary object illustrations and a 16-cell 36px atlas.")
if __name__=="__main__":main()

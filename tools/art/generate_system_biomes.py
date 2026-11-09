from __future__ import annotations

"""Generate original VOIDREIGN system backdrops and tactical combat tiles.

All images are procedural, deterministic, and authored specifically for the six
native VOIDREIGN system environments. No screenshots, borrowed art, or external
samples are used.
"""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
SYS=ROOT/"game-data"/"Pictures"/"Systems"
ARCH=ROOT/"art-library"/"voidreign-art-system-biomes"
LAYOUTS={"1024X768":660,"800X600":490}
BIOMES={
    "Starfield":{
        "name":"VoidReign Core System","palette":[(7,13,28),(30,54,88),(124,91,42)],
        "clouds":[((0.26,0.66),0.28,0.16,2),( (0.76,0.35),0.22,0.12,1)],
        "feature":"core","seed":0xA001,
    },
    "Nebula":{
        "name":"VoidReign Nebula System","palette":[(6,10,27),(70,31,91),(26,107,127)],
        "clouds":[((0.30,0.32),0.28,0.19,1),((0.67,0.63),0.31,0.20,2),((0.54,0.18),0.15,0.13,1)],
        "feature":"nebula","seed":0xA002,
    },
    "Pulsar":{
        "name":"VoidReign Pulsar System","palette":[(3,9,25),(28,65,117),(91,157,226)],
        "clouds":[((0.50,0.50),0.17,0.14,2),((0.18,0.74),0.18,0.09,1)],
        "feature":"pulsar","seed":0xA003,
    },
    "BlackHole":{
        "name":"VoidReign Black Hole System","palette":[(5,5,13),(92,38,26),(193,115,48)],
        "clouds":[((0.51,0.52),0.29,0.11,2),((0.52,0.52),0.20,0.07,1)],
        "feature":"blackhole","seed":0xA004,
    },
    "Magnetar":{
        "name":"VoidReign Magnetar System","palette":[(3,10,29),(17,92,139),(89,214,237)],
        "clouds":[((0.35,0.42),0.20,0.23,2),((0.74,0.64),0.25,0.15,1)],
        "feature":"magnetar","seed":0xA005,
    },
    "WarpHub":{
        "name":"VoidReign Warp Hub System","palette":[(5,8,25),(50,37,119),(36,158,179)],
        "clouds":[((0.50,0.49),0.34,0.30,2),((0.75,0.22),0.14,0.12,1)],
        "feature":"warphub","seed":0xA006,
    },
}

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def base_field(w:int,h:int,seed:int,palette,clouds,detail:int=1)->Image.Image:
    rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:h,0:w]
    xx=xx/max(1,w-1); yy=yy/max(1,h-1)
    field=np.zeros((h,w,3),dtype=np.float32)
    field[:]=palette[0]
    # Soft, overlapping gas clouds: broad low-frequency fields and smaller
    # wisps. Each biome has its own hue and shape distribution.
    for (cx,cy),rx,ry,which in clouds:
        dx=(xx-cx)/rx; dy=(yy-cy)/ry
        radial=np.exp(-2.8*(dx*dx+dy*dy))
        warp=(np.sin((xx*8+yy*4+seed%19)*math.pi)*0.10+
              np.sin((yy*11-xx*6+seed%13)*math.pi)*0.07)
        wispy=np.clip(radial*(0.84+warp)+rng.normal(0,0.025,(h,w)),0,1)
        color=np.asarray(palette[which],dtype=np.float32)
        field=field*(1-wispy[:,:,None]*0.48)+color*wispy[:,:,None]*0.48
    # Fine dust and restrained luminance variation.
    grain=rng.normal(0,2.0,(h,w,1))
    field=np.clip(field+grain,0,255).astype(np.uint8)
    im=Image.fromarray(field,"RGB").convert("RGBA")
    # Stars in three brightness classes, sparse enough to leave visual calm.
    d=ImageDraw.Draw(im,"RGBA")
    n=int(w*h/1450)
    for _ in range(n):
        x=int(rng.integers(0,w)); y=int(rng.integers(0,h))
        r=float(rng.choice([0.5,0.7,1.0,1.35],p=[.4,.34,.20,.06]))
        c=int(rng.integers(135,245))
        d.ellipse((x-r,y-r,x+r,y+r),fill=(c,min(255,c+8),255,int(rng.integers(95,225))))
    # Rare distant stars with gentle glow.
    glow=Image.new("RGBA",im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    for _ in range(max(5,int(w*h/90000))):
        x=int(rng.integers(0,w)); y=int(rng.integers(0,h)); rad=int(rng.integers(2,5))
        gd.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(160,205,255,55))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))
    return im

def draw_feature(im:Image.Image,kind:str,seed:int)->None:
    w,h=im.size; x=w*.5; y=h*.5
    rng=np.random.default_rng(seed)
    # Stable, restrained per-system offsets make two instances of one biome
    # recognisably related without using the same composition.
    jitter_x=float(rng.uniform(-.085,.085))*w
    jitter_y=float(rng.uniform(-.085,.085))*h
    d=ImageDraw.Draw(im,"RGBA")
    if kind=="core":
        # A stable golden-white star and distant dust arcs, offset from centre.
        x=w*.72+jitter_x; y=h*.43+jitter_y
        for rad,alpha in ((34,8),(22,15),(13,35),(7,90)):
            d.ellipse((x-rad*2,y-rad*2,x+rad*2,y+rad*2),fill=(255,198,98,alpha))
        for rad in range(2,20,3):
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(255,236,181,170))
        d.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,232,255))
    elif kind=="nebula":
        # Volumetric emission clouds: layered soft magenta/cyan gas, then
        # thin filaments and bright star-forming knots on top.
        gas=Image.new("RGBA",(w,h),(0,0,0,0))
        gd=ImageDraw.Draw(gas,"RGBA")
        blobs=[
            (.23,.34,.30,.18,(111,47,155,88)),
            (.42,.53,.34,.22,(37,114,161,84)),
            (.73,.62,.27,.18,(68,169,173,76)),
            (.62,.19,.18,.16,(136,66,166,68)),
            (.18,.77,.20,.12,(55,103,163,66)),
        ]
        for cx,cy,rx,ry,color in blobs:
            cx+=jitter_x/w*.45
            cy+=jitter_y/h*.45
            box=((cx-rx)*w,(cy-ry)*h,(cx+rx)*w,(cy+ry)*h)
            gd.ellipse(box,fill=color)
        im.alpha_composite(gas.filter(ImageFilter.GaussianBlur(max(10,int(w*.055)))))
        d=ImageDraw.Draw(im,"RGBA")
        phase=float(rng.uniform(-1.2,1.2))
        for i in range(11):
            yy=h*(.20+i*.062)+jitter_y*.25
            pts=[]
            for k in range(32):
                px=w*(.04+k*.030)
                py=yy+math.sin(k*.48+i*.72+phase)*h*.07+math.sin(k*.19+i+phase)*h*.025
                pts.append((px,py))
            d.line(pts,fill=(157,108,218,40+i*2),width=max(2,int(w*.006)))
        for px,py in ((.27,.32),(.73,.62),(.52,.2)):
            xx=px*w; yy=py*h
            d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=(117,231,244,220))
            d.ellipse((xx-24,yy-24,xx+24,yy+24),outline=(107,187,245,110),width=4)
    elif kind=="pulsar":
        x=w*.50+jitter_x*.60;y=h*.49+jitter_y*.60
        for rad in (28,52,92,138,186):
            d.ellipse((x-rad,y-rad,x+rad,y+rad),outline=(73,165,255,65),width=max(2,int(w*.003)))
        d.ellipse((x-21,y-21,x+21,y+21),fill=(199,231,255,245))
        d.ellipse((x-11,y-11,x+11,y+11),fill=(255,255,255,255))
        # Polar beams, not a flat crosshair.
        d.polygon([(x-8,y-14),(x-34,-h*.1),(x+34,-h*.1),(x+8,y-14)],fill=(91,169,255,38))
        d.polygon([(x-8,y+14),(x-34,h*1.1),(x+34,h*1.1),(x+8,y+14)],fill=(91,169,255,38))
    elif kind=="blackhole":
        x=w*.52+jitter_x*.48;y=h*.49+jitter_y*.48
        # A luminous accretion ellipse around a truly dark event horizon.
        for k in range(7):
            rx=w*(.20+k*.012); ry=h*(.055+k*.009)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),outline=(255,142-k*12,55+k*8,100-k*9),width=max(3,int(w*.006)))
        d.ellipse((x-w*.105,y-h*.105,x+w*.105,y+h*.105),fill=(0,0,0,255))
        d.ellipse((x-w*.12,y-h*.12,x+w*.12,y+h*.12),outline=(240,174,86,160),width=4)
        d.arc((x-w*.29,y-h*.10,x+w*.29,y+h*.12),0,180,fill=(255,210,138,180),width=6)
    elif kind=="magnetar":
        x=w*.52+jitter_x*.55;y=h*.50+jitter_y*.55
        for k in range(10):
            ang=k*math.pi/5
            pts=[]
            for t in np.linspace(-1,1,25):
                px=x+t*w*.42*math.cos(ang)
                py=y+t*h*.28*math.sin(ang)+math.sin(t*7+k)*h*.04
                pts.append((px,py))
            d.line(pts,fill=(76,207,255,90),width=max(2,int(w*.004)))
        d.ellipse((x-17,y-17,x+17,y+17),fill=(226,251,255,255))
        d.ellipse((x-34,y-34,x+34,y+34),outline=(67,188,255,190),width=6)
    elif kind=="warphub":
        x=w*.50+jitter_x*.55;y=h*.50+jitter_y*.55
        for k in range(12):
            rad=int(w*(.07+k*.022))
            box=(x-rad,y-rad*.76,x+rad,y+rad*.76)
            d.ellipse(box,outline=(68,202,231,25+k*8),width=max(2,int(w*.003)))
        for a in range(0,360,30):
            rad=w*.30
            px=x+math.cos(math.radians(a))*rad
            py=y+math.sin(math.radians(a))*rad*.76
            d.ellipse((px-3,py-3,px+3,py+3),fill=(183,149,255,210))
        d.ellipse((x-15,y-15,x+15,y+15),fill=(172,238,255,235))

def draw_variant_details(im:Image.Image,kind:str,seed:int)->None:
    """Add clearly distinguishable local objects without changing the biome identity."""
    w,h=im.size
    rng=np.random.default_rng(seed ^ 0x5A71C0DE)
    d=ImageDraw.Draw(im,"RGBA")
    palettes={
        "core":((154,187,212,220),(238,222,180,210),(110,142,179,150)),
        "nebula":((116,200,225,230),(207,162,244,205),(94,122,187,155)),
        "pulsar":((134,192,239,230),(219,237,255,220),(77,133,211,155)),
        "blackhole":((221,139,88,235),(255,205,139,215),(106,76,91,150)),
        "magnetar":((88,206,241,235),(207,249,255,225),(49,126,190,160)),
        "warphub":((114,210,226,235),(191,162,255,225),(62,129,192,165)),
    }
    tones=palettes[kind]
    # Separate orbital zones are selected from a stable seed, so each system
    # has a genuinely different arrangement of companion objects and debris.
    zones=[(0.16,0.19),(0.83,0.18),(0.17,0.81),(0.83,0.79),(0.49,0.13),(0.12,0.51),(0.88,0.52),(0.52,0.88)]
    order=rng.permutation(len(zones))
    count=int(rng.integers(2,5))
    scale=min(w,h)
    for index in range(count):
        zx,zy=zones[int(order[index])]
        x=w*(zx+float(rng.uniform(-0.045,0.045)))
        y=h*(zy+float(rng.uniform(-0.045,0.045)))
        radius=max(2,int(scale*float(rng.uniform(0.012,0.024))))
        color=tones[index%len(tones)]
        # A low-contrast orbital track gives the body a physical relationship
        # to the system rather than making it look like a pasted icon.
        rx=radius*float(rng.uniform(2.7,5.0))
        ry=radius*float(rng.uniform(1.6,2.8))
        d.ellipse((x-rx,y-ry,x+rx,y+ry),outline=(*color[:3],70),width=max(1,int(scale/330)))
        # Spherical shading and a narrow illuminated limb.
        d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(5,12,27,245),outline=color,width=max(1,int(scale/180)))
        d.ellipse((x-radius*0.55,y-radius*0.70,x+radius*0.62,y+radius*0.50),fill=(*color[:3],185))
        d.ellipse((x-radius*0.50,y-radius*0.64,x-radius*0.12,y-radius*0.27),fill=(239,247,255,150))
        if index%2==0 and kind in ("core","nebula","blackhole","warphub"):
            d.arc((x-radius*2.4,y-radius*0.7,x+radius*2.4,y+radius*0.7),185,350,fill=tones[1],width=max(1,int(scale/170)))
    # Biome-specific small structures complete the view: debris, magnetic
    # arcs, relay lights or a second distant accretion ribbon.
    if kind in ("core","nebula","pulsar"):
        cx=w*float(rng.uniform(.34,.66)); cy=h*float(rng.uniform(.32,.68))
        rx=scale*float(rng.uniform(.20,.31)); ry=scale*float(rng.uniform(.07,.13))
        for _ in range(95 if scale>300 else 18):
            a=float(rng.uniform(0,math.tau))
            radius=float(rng.uniform(.72,1.28))
            px=cx+math.cos(a)*rx*radius
            py=cy+math.sin(a)*ry*radius
            dot=max(1,int(scale*float(rng.uniform(.0015,.004))))
            d.ellipse((px-dot,py-dot,px+dot,py+dot),fill=(*tones[2][:3],int(rng.integers(65,190))))
    elif kind=="blackhole":
        # A faint secondary dust streamer is offset from the main accretion disc.
        y=h*float(rng.uniform(.28,.72))
        points=[]
        for t in np.linspace(0,1,42):
            x=w*(.12+.76*t)
            py=y+math.sin(t*math.pi*2+float(rng.uniform(-.02,.02)))*h*.035
            points.append((x,py))
        d.line(points,fill=tones[2],width=max(2,int(scale*.008)))
    elif kind=="magnetar":
        cx=w*float(rng.uniform(.35,.65)); cy=h*float(rng.uniform(.35,.65))
        for arc in range(3):
            x0=cx-scale*(.18+arc*.035); y0=cy-scale*(.10+arc*.02)
            x1=cx+scale*(.18+arc*.035); y1=cy+scale*(.10+arc*.02)
            d.arc((x0,y0,x1,y1),int(190+rng.integers(-15,15)),int(345+rng.integers(-15,15)),fill=tones[0],width=max(1,int(scale*.004)))
    elif kind=="warphub":
        for px,py in ((.23,.26),(.76,.28),(.23,.74),(.77,.73)):
            x=w*(px+float(rng.uniform(-.04,.04))); y=h*(py+float(rng.uniform(-.04,.04)))
            radius=max(3,int(scale*.012))
            d.ellipse((x-radius*2,y-radius*2,x+radius*2,y+radius*2),outline=tones[1],width=max(1,int(scale*.004)))
            d.ellipse((x-radius*.55,y-radius*.55,x+radius*.55,y+radius*.55),fill=tones[0])

def render_biome(name:str,entry:dict,w:int,h:int,seed_offset:int=0)->Image.Image:
    im=base_field(w,h,entry["seed"]+seed_offset,entry["palette"],entry["clouds"])
    draw_feature(im,entry["feature"],entry["seed"]+seed_offset)
    if seed_offset:
        draw_variant_details(im,entry["feature"],entry["seed"]+seed_offset)
    # Darken the outer edge for readable UI overlays while leaving the main
    # physical feature visible; this is a subtle vignette rather than a frame.
    yy,xx=np.mgrid[0:h,0:w]
    nx=(xx-w*.5)/(w*.78); ny=(yy-h*.5)/(h*.78)
    vignette=np.clip(1-0.18*(nx*nx+ny*ny),.62,1.0)
    arr=np.asarray(im).copy()
    arr[:,:,:3]=(arr[:,:,:3].astype(np.float32)*vignette[:,:,None]).astype(np.uint8)
    result=Image.fromarray(arr,"RGBA")
    # The four per-system scenes are not just recolours of one backdrop.
    # Their star-field composition and the direction of the environmental
    # structure are deliberately varied, while retaining the same biome.
    if seed_offset:
        variant=max(1,seed_offset//0x10211)
        transforms=(
            Image.Transpose.ROTATE_90,
            Image.Transpose.ROTATE_180,
            Image.Transpose.ROTATE_270,
            Image.Transpose.FLIP_LEFT_RIGHT,
        )
        result=result.transpose(transforms[(variant-1)%len(transforms)])
    return result

def render_tile(entry:dict,index:int)->Image.Image:
    # All tiles share a related dark base palette so a randomized 6x6 mosaic
    # reads as one coherent battlefield, not a pasted collage.
    p=entry["palette"]
    seed=entry["seed"]+0x5000+index*97
    im=base_field(144,144,seed,p,entry["clouds"],1)
    d=ImageDraw.Draw(im,"RGBA")
    rng=np.random.default_rng(seed)
    kind=entry["feature"]
    if kind=="blackhole":
        cx=float(rng.uniform(.25,.75))*144; cy=float(rng.uniform(.25,.75))*144
        d.ellipse((cx-23,cy-7,cx+23,cy+7),outline=(227,135,73,75),width=2)
        d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=(0,0,0,255))
    elif kind=="pulsar":
        cx=float(rng.uniform(.25,.75))*144; cy=float(rng.uniform(.25,.75))*144
        d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=(183,224,255,190))
        d.ellipse((cx-19,cy-19,cx+19,cy+19),outline=(80,165,255,55),width=2)
    elif kind=="warphub":
        cx=72;cy=72
        for rr in (15,26,38):
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(58,196,220,60),width=2)
    elif kind=="magnetar":
        x0=int(rng.integers(10,70)); y0=int(rng.integers(10,70))
        d.arc((x0,y0,x0+85,y0+64),180,345,fill=(90,220,255,65),width=3)
    elif kind=="nebula":
        d.arc((-20,12,160,150),15,250,fill=(174,108,223,55),width=8)
    else:
        d.arc((-25,25,160,150),185,355,fill=(211,155,88,38),width=4)
    return im.resize((72,72),Image.Resampling.LANCZOS)

def main():
    records=[]
    for name,entry in BIOMES.items():
        # Full star-system thumbnail/report art.
        thumb=render_biome(name,entry,128,128,0)
        p=SYS/f"{name}.png"; thumb.save(p,optimize=True)
        records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"system-picture","biome":name,"size":[128,128],"sha256":sha(p)})
        # Layout-specific starmap/background image (square because legacy
        # engine centres/crops it into the central system panel).
        for layout,size in LAYOUTS.items():
            image=render_biome(name,entry,size,size,0)
            p=SYS/layout/f"{name}.png"
            p.parent.mkdir(parents=True,exist_ok=True)
            image.save(p,optimize=True)
            records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"system-background","biome":name,"layout":layout,"size":[size,size],"sha256":sha(p)})
        # Four deterministic scene variations per biome. The game selects
        # one by stable SystemId, so each system has its own composition while
        # keeping one coherent colour and physical-environment identity.
        for variant in range(1,5):
            offset=0x10000*variant+0x211*variant
            thumb=render_biome(name,entry,128,128,offset)
            p=SYS/f"{name}_V{variant}.png"
            thumb.save(p,optimize=True)
            records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"system-picture-variant","biome":name,"variant":variant,"size":[128,128],"sha256":sha(p)})
            for layout,size in LAYOUTS.items():
                image=render_biome(name,entry,size,size,offset)
                p=SYS/layout/f"{name}_V{variant}.png"
                image.save(p,optimize=True)
                records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"system-background-variant","biome":name,"variant":variant,"layout":layout,"size":[size,size],"sha256":sha(p)})
        # Nine distinct tactical texture tiles per system biome.
        for i in range(1,10):
            tile=render_tile(entry,i)
            p=SYS/f"{name}Tile{i}.png"
            tile.save(p,optimize=True)
            records.append({"file":p.relative_to(ROOT).as_posix(),"kind":"tactical-tile","biome":name,"variant":i,"size":[72,72],"sha256":sha(p)})
    ARCH.mkdir(parents=True,exist_ok=True)
    manifest={
        "title":"VOIDREIGN original star-system biomes and tactical fields",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "generator":"tools/art/generate_system_biomes.py",
        "method":"Deterministic procedural nebula fields, stars, plasma structures, singularity and warp geometry",
        "biomes":list(BIOMES),
        "system_variants_per_biome":4,
        "tactical_tile_variants_per_biome":9,
        "assets":records,
    }
    (ARCH/"GENERATION-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"Generated {len(BIOMES)} biome families, {len(BIOMES)*4} distinct system scenes, {len(BIOMES)*4*2} layout backgrounds, {len(BIOMES)*9} tactical tiles and {len(BIOMES)} base system thumbnails.")
    print(f"Manifest: {ARCH/'GENERATION-MANIFEST.json'}")
if __name__=="__main__":main()

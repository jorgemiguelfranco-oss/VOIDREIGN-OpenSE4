from __future__ import annotations

"""Generate original component and facility artwork for native VOIDREIGN IDs.

Every named ruleset entry gets its own 128x128 transparent PNG. The same
illustration is used at 36x36 in lists and at 128x128 in help/detail panels.
Art is drawn procedurally from semantic silhouettes; no borrowed game images.
"""

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "game-data" / "Data"
PICTURES = ROOT / "game-data" / "Pictures"
OUT = ROOT / "art-library" / "voidreign-art-native-components"
SIZE = 512
SCALE = 4

PALETTES = {
    "Ship Systems": ((65, 192, 220), (155, 240, 238), (15, 78, 108)),
    "Engines": ((255, 145, 54), (255, 220, 130), (126, 48, 23)),
    "Cargo": ((224, 177, 84), (255, 224, 148), (98, 63, 27)),
    "Weapons": ((255, 91, 102), (255, 190, 157), (118, 29, 47)),
    "Colonization": ((88, 207, 148), (189, 255, 184), (22, 91, 75)),
    "Construction": ((226, 170, 90), (255, 224, 155), (111, 67, 31)),
    "Sensors": ((157, 142, 255), (215, 207, 255), (56, 43, 124)),
    "Shields": ((74, 183, 255), (188, 237, 255), (30, 73, 133)),
    "Support": ((216, 194, 104), (255, 240, 180), (101, 79, 31)),
    "Resource Generation": ((105, 205, 151), (205, 255, 191), (25, 92, 65)),
    "Point Generation": ((163, 153, 255), (231, 220, 255), (54, 49, 122)),
    "Spaceport": ((104, 188, 235), (199, 239, 255), (25, 78, 119)),
    "Space Yard": ((225, 158, 83), (255, 221, 151), (110, 60, 27)),
    "Supply Generation": ((83, 203, 215), (195, 255, 242), (23, 89, 102)),
    "Resource Storage": ((214, 171, 91), (255, 232, 157), (103, 69, 30)),
    "Observatory": ((148, 144, 255), (223, 215, 255), (49, 51, 125)),
}
DEFAULT = ((91, 190, 210), (211, 247, 249), (24, 76, 104))


def parse_entries(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    chunks = re.split(r"(?m)(?=^Name\s*:=)", text)
    out = []
    for chunk in chunks:
        name = re.search(r"(?m)^Name\s*:=\s*(.+)$", chunk)
        if not name:
            continue
        def field(key: str) -> str:
            m = re.search(r"(?m)^" + re.escape(key) + r"\s*:=\s*(.*)$", chunk)
            return m.group(1).strip() if m else ""
        out.append({
            "name": name.group(1).strip(),
            "description": field("Description"),
            "group": field("General Group"),
            "ability": field("Ability 1 Type"),
            "pic": field("Pic Num"),
        })
    return out


def reassign_picture_numbers(path: Path, expected: int) -> list[dict[str, str]]:
    raw = path.read_text(encoding="utf-8-sig")
    starts = list(re.finditer(r"(?m)^Name\s*:=\s*(.+)$", raw))
    if len(starts) != expected:
        raise RuntimeError(f"{path.name}: expected {expected} definitions, found {len(starts)}")
    pieces = []
    cursor = 0
    entries = []
    for i, match in enumerate(starts, 1):
        end = starts[i].start() if i < len(starts) else len(raw)
        piece = raw[cursor:end]
        block = raw[match.start():end]
        block = re.sub(r"(?m)^Pic Num\s*:=\s*\d+.*$", f"Pic Num := {i}", block, count=1)
        if not re.search(r"(?m)^Pic Num\s*:=", block):
            raise RuntimeError(f"{path.name}: {match.group(1).strip()} has no Pic Num")
        piece = raw[cursor:match.start()] + block
        pieces.append(piece)
        entries.append({
            "name": match.group(1).strip(),
            "pic": str(i),
            "description": (re.search(r"(?m)^Description\s*:=\s*(.*)$", block) or [None, ""])[1].strip(),
            "group": (re.search(r"(?m)^General Group\s*:=\s*(.*)$", block) or [None, ""])[1].strip(),
            "ability": (re.search(r"(?m)^Ability 1 Type\s*:=\s*(.*)$", block) or [None, ""])[1].strip(),
        })
        cursor = end
    path.write_text("".join(pieces), encoding="utf-8", newline="\n")
    return entries


def rgb_lerp(a, b, t):
    return tuple(int(a[i] * (1.0 - t) + b[i] * t) for i in range(3))


def draw_glow(base: Image.Image, center: tuple[int, int], color: tuple[int, int, int], radius: int, alpha: int = 110):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    x, y = center
    for r in range(radius, 0, -8):
        a = int(alpha * (1 - r / radius) ** 2 * 0.22)
        gd.ellipse((x-r, y-r, x+r, y+r), fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(glow)


def glyph(draw: ImageDraw.ImageDraw, kind: str, accent, light, dark, seed: int, tier: int):
    # Coordinates use a 512px canvas. Every glyph is a distinct, functional silhouette.
    C = (256, 247)
    x, y = C
    w = 10
    line = lambda pts, fill=accent, width=w: draw.line(pts, fill=(*fill, 255), width=width, joint="curve")
    poly = lambda pts, fill=accent, outline=light, width=7: draw.polygon(pts, fill=(*fill, 255) if fill is not None else None, outline=(*outline, 255) if outline is not None else None)
    ell = lambda box, fill=None, outline=accent, width=7: draw.ellipse(box, fill=(*fill, 255) if fill else None,
                                                                        outline=(*outline, 255) if outline else None, width=width)
    if kind in ("bridge", "life", "quarters"):
        if kind == "bridge":
            poly([(148, 302), (173, 220), (218, 178), (294, 178), (339, 220), (364, 302), (331, 335), (181, 335)],
                 dark, light)
            ell((207, 164, 305, 254), accent, light, 9)
            line([(156, 309), (356, 309)], light, 13)
            for px in (218, 244, 270, 296):
                ell((px-5, 268, px+5, 284), light, None, 1)
        elif kind == "life":
            ell((190, 168, 322, 300), dark, light, 10)
            ell((222, 200, 290, 268), accent, light, 5)
            for bx, by in ((157, 177), (348, 193), (160, 317), (354, 316)):
                ell((bx-18, by-18, bx+18, by+18), None, light, 7)
            line([(190, 210), (158, 190), (139, 190)], light, 8)
            line([(322, 232), (356, 212), (373, 212)], light, 8)
            line([(222, 302), (194, 341), (166, 341)], light, 8)
            line([(286, 302), (314, 341), (342, 341)], light, 8)
        else:
            ell((140, 168, 372, 332), None, light, 11)
            ell((179, 198, 333, 306), dark, accent, 9)
            for px in (189, 226, 263, 300):
                ell((px, 239, px+20, 260), light, None, 2)
            for angle in range(0, 360, 90):
                r = math.radians(angle)
                p1 = (x + 74*math.cos(r), y + 50*math.sin(r))
                p2 = (x + 111*math.cos(r), y + 80*math.sin(r))
                line([p1, p2], accent, 10)
    elif kind in ("engine", "warp"):
        if kind == "engine":
            poly([(143, 175), (315, 204), (366, 249), (315, 294), (143, 323), (176, 249)], dark, light, 9)
            ell((119, 191, 207, 307), accent, light, 10)
            for n in range(3):
                dy = -36 + n*36
                line([(375, 249+dy), (414, 249+dy)], light, 7)
            poly([(398, 206), (461, 249), (398, 292)], light, accent, 5)
        else:
            ell((145, 139, 367, 361), None, accent, 18)
            ell((184, 178, 328, 322), dark, light, 8)
            ell((224, 218, 288, 282), accent, light, 5)
            for j in range(3):
                draw.arc((112+j*16, 112+j*16, 400-j*16, 400-j*16), 200, 520,
                         fill=(*light, 255), width=6)
            line([(255, 128), (255, 85)], light, 9)
            line([(255, 384), (255, 427)], light, 9)
    elif kind in ("cargo", "warehouse"):
        boxes = [((150, 205, 252, 295), accent), ((260, 173, 354, 270), dark), ((220, 284, 336, 357), light)]
        for box, col in boxes:
            draw.rounded_rectangle(box, radius=14, fill=(*col, 255), outline=(*light, 255), width=8)
            x0, y0, x1, y1 = box
            line([(x0+10, y0+18), (x1-10, y0+18)], dark, 5)
            line([(x0+10, y1-18), (x1-10, y1-18)], dark, 5)
        if kind == "warehouse":
            poly([(130, 180), (256, 114), (382, 180), (382, 350), (130, 350)], None, light, 10)
            line([(256, 114), (256, 350)], light, 7)
    elif kind in ("weapon", "lance"):
        if kind == "weapon":
            poly([(140, 205), (316, 205), (360, 235), (316, 279), (140, 279)], dark, light, 10)
            ell((112, 204, 191, 281), accent, light, 10)
            poly([(344, 225), (405, 242), (405, 260), (344, 278)], light, accent, 5)
            for q in range(3):
                yy = 218 + q*24
                line([(408, yy), (455, yy)], light, 5)
            ell((222, 222, 278, 278), accent, light, 5)
        else:
            ell((145, 145, 367, 367), None, light, 9)
            ell((191, 191, 321, 321), dark, accent, 11)
            ell((231, 231, 281, 281), light, None, 3)
            for q in range(4):
                ang = q*math.pi/2 + seed*0.31
                line([(x+62*math.cos(ang), y+62*math.sin(ang)),
                      (x+154*math.cos(ang+0.14), y+154*math.sin(ang+0.14))], accent, 7)
            line([(256, 92), (256, 410)], light, 5)
    elif kind in ("colonize", "planet"):
        ell((171, 250, 340, 419), dark, light, 9)
        draw.arc((168, 245, 342, 419), 190, 345, fill=(*accent,255), width=15)
        poly([(208, 231), (228, 170), (284, 170), (306, 231), (281, 265), (232, 265)], accent, light, 8)
        line([(228, 265), (196, 301), (174, 317)], light, 8)
        line([(284, 265), (317, 301), (340, 317)], light, 8)
        ell((235, 186, 266, 218), light, None, 1)
        if seed % 3 == 1:
            line([(194, 360), (318, 360)], accent, 8)
        elif seed % 3 == 2:
            for px in (218, 254, 290):
                ell((px-8, 319, px+8, 337), light, None, 1)
    elif kind in ("construction", "shipyard"):
        poly([(132, 146), (380, 146), (380, 360), (132, 360)], dark, light, 8)
        for i in range(5):
            xx = 151 + i*51
            line([(xx, 155), (xx, 352)], accent, 6)
        for yy in (187, 250, 313):
            line([(145, yy), (367, yy)], light, 6)
        line([(256, 146), (256, 88), (348, 88), (348, 167)], light, 9)
        line([(256, 146), (312, 203)], accent, 7)
        ell((298, 188, 327, 218), accent, light, 4)
    elif kind in ("sensor", "observatory"):
        ell((161, 156, 351, 346), None, light, 9)
        poly([(195, 281), (218, 205), (304, 205), (328, 281)], accent, light, 9)
        line([(256, 205), (256, 365)], light, 10)
        ell((220, 345, 292, 385), dark, light, 7)
        for rad in (115, 154, 192):
            draw.arc((x-rad, y-rad, x+rad, y+rad), 200, 340, fill=(*accent,255), width=6)
        if kind == "observatory":
            line([(220, 208), (185, 153), (170, 130)], light, 9)
            line([(185, 153), (210, 136)], accent, 8)
    elif kind in ("shield", "defence"):
        poly([(256, 116), (365, 159), (354, 285), (256, 396), (158, 285), (147, 159)], dark, light, 12)
        poly([(256, 159), (329, 188), (320, 274), (256, 344), (192, 274), (183, 188)], accent, light, 6)
        for yy in (213, 256, 299):
            line([(205, yy), (307, yy)], light, 5)
    elif kind in ("matrix", "support", "science"):
        pts = [(256, 145), (166, 218), (347, 220), (196, 334), (317, 335), (256, 260)]
        links = [(0,1),(0,2),(1,3),(1,5),(2,4),(2,5),(3,4),(3,5),(4,5)]
        for a,b in links: line([pts[a],pts[b]], light, 7)
        for j,(px,py) in enumerate(pts):
            ell((px-24,py-24,px+24,py+24), accent if j%2==0 else dark, light, 7)
    else:
        # Generic power/core, used only for data not yet classified.
        ell((160, 160, 352, 352), None, light, 11)
        ell((212, 212, 300, 300), accent, light, 7)
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            line([(256+80*math.cos(a),256+80*math.sin(a)),
                  (256+140*math.cos(a),256+140*math.sin(a))], light, 7)

    # Upgrade markers: distinct, readable tier pips, not text baked into art.
    if tier > 1:
        for i in range(min(5, tier)):
            px = 188 + i * 34
            ell((px-8, 394, px+8, 410), light, accent, 3)


def render_card(name: str, category: str, seed: int, tier: int, kind: str) -> Image.Image:
    accent, light, dark = PALETTES.get(category, DEFAULT)
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
    # Radial background glow, subtle circuit grain and a deep blue metallic faceplate.
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    dist = np.sqrt(((xx-256)/320)**2 + ((yy-250)/290)**2)
    pulse = np.clip(1.0-dist, 0, 1) ** 2
    grain = rng.normal(0, 1.3, (SIZE,SIZE))
    arr = np.zeros((SIZE,SIZE,4), dtype=np.uint8)
    for c, base in enumerate((7, 15, 31)):
        arr[:,:,c] = np.clip(base + pulse * dark[c] * 0.35 + grain, 0, 255).astype(np.uint8)
    arr[:,:,3] = 255
    im = Image.fromarray(arr, "RGBA")
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((18,18,494,494), radius=42, fill=255)
    im.putalpha(mask)
    draw_glow(im, (256, 250), accent, 180, 125)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14,14,498,498), radius=43, outline=(79,112,150,255), width=8)
    d.rounded_rectangle((25,25,487,487), radius=35, outline=(*accent,170), width=3)
    d.line((46,54,466,54), fill=(118,151,184,110), width=3)
    d.line((46,460,466,460), fill=(42,71,104,180), width=3)
    # Technical corner pins and faint segmented traces.
    for px,py in ((42,42),(470,42),(42,470),(470,470)):
        d.ellipse((px-5,py-5,px+5,py+5), fill=(*light,230), outline=(*accent,255), width=2)
    for k in range(5):
        yy0 = 83 + k*26
        d.line((43, yy0, 60, yy0), fill=(*accent,65), width=2)
        d.line((451, yy0, 468, yy0), fill=(*accent,65), width=2)
    glyph(d, kind, accent, light, dark, seed, tier)
    return im.resize((128,128), Image.Resampling.LANCZOS)


def detect_component_kind(item):
    n=item["name"].lower()
    group=item["group"]
    if "bridge" in n: return "bridge"
    if "life support" in n: return "life"
    if "crew quarters" in n: return "quarters"
    if group == "Engines": return "warp" if "horizon" in n else "engine"
    if group == "Cargo": return "matrix" if "support matrix" in n else "cargo"
    if group == "Weapons": return "lance" if "gravity" in n else "weapon"
    if group == "Colonization": return "colonize"
    if group == "Construction": return "construction"
    if group == "Sensors": return "sensor"
    if group == "Shields": return "shield"
    if group == "Support": return "matrix"
    return "core"


def detect_facility_category(item):
    n=item["name"].lower()
    if "extractor" in n: return "Resource Generation", "cargo"
    if "hydroponics" in n: return "Resource Generation", "colonize"
    if "isotope" in n or "reactor" in n: return "Resource Generation", "core"
    if "research" in n: return "Point Generation", "observatory"
    if "intelligence" in n: return "Point Generation", "sensor"
    if "spaceport" in n: return "Spaceport", "construction"
    if "shipyard" in n: return "Space Yard", "shipyard"
    if "warehouse" in n: return "Resource Storage", "warehouse"
    if "supply" in n: return "Supply Generation", "engine"
    if "observatory" in n: return "Observatory", "observatory"
    return "Construction", "construction"


def tier_from_name(name: str) -> int:
    m = re.search(r"\b(?:II|III|IV|V|VI)\b|(?:\s([2-6]))$", name)
    if not m: return 1
    token = m.group(0).strip()
    return {"II":2,"III":3,"IV":4,"V":5,"VI":6}.get(token, int(token) if token.isdigit() else 1)


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()


def glyph_icon(category: str, kind: str, seed: int, tier: int) -> Image.Image:
    accent, light, dark = PALETTES.get(category, DEFAULT)
    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(icon, "RGBA"), kind, accent, light, dark, seed, tier)
    return icon.resize((36, 36), Image.Resampling.LANCZOS)


def save_icon_sheet(images: list[Image.Image], path: Path, columns: int) -> None:
    cell = 36
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGBA", (columns * cell, rows * cell), (0, 0, 0, 0))
    for i, icon in enumerate(images):
        sheet.alpha_composite(icon, ((i % columns) * cell, (i // columns) * cell))
    sheet.save(path, optimize=True, compress_level=9)


def main():
    comp_path=DATA/"Components.txt"
    fac_path=DATA/"Facility.txt"
    comps=reassign_picture_numbers(comp_path,49)
    facilities=reassign_picture_numbers(fac_path,29)
    comp_dir=PICTURES/"Components"; fac_dir=PICTURES/"Facilities"
    comp_dir.mkdir(parents=True,exist_ok=True); fac_dir.mkdir(parents=True,exist_ok=True)
    assets=[]
    component_icons=[]
    facility_icons=[]
    for i,item in enumerate(comps,1):
        kind=detect_component_kind(item)
        group=item["group"] if item["group"] in PALETTES else "Support"
        tier=tier_from_name(item["name"])
        image=render_card(item["name"],group,0xC001+i,tier,kind)
        path=comp_dir/f"Comp_{i:03d}.png"
        image.save(path,optimize=True,compress_level=9)
        component_icons.append(glyph_icon(group,kind,0xC001+i,tier))
        assets.append({"file":path.relative_to(ROOT).as_posix(),"name":item["name"],"category":group,"pic_num":i,"size":[128,128],"sha256":sha(path)})
    for i,item in enumerate(facilities,1):
        category,kind=detect_facility_category(item)
        tier=tier_from_name(item["name"])
        image=render_card(item["name"],category,0xF001+i,tier,kind)
        path=fac_dir/f"Facil_{i:03d}.png"
        image.save(path,optimize=True,compress_level=9)
        facility_icons.append(glyph_icon(category,kind,0xF001+i,tier))
        assets.append({"file":path.relative_to(ROOT).as_posix(),"name":item["name"],"category":category,"pic_num":i,"size":[128,128],"sha256":sha(path)})
    save_icon_sheet(component_icons,comp_dir/"Components.png",7)
    save_icon_sheet(facility_icons,fac_dir/"Facility.png",6)
    manifest={
        "title":"VOIDREIGN native component and facility art",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "renderer":"tools/art/generate_component_facility_art.py",
        "method":"Original procedural vector illustration with custom silhouettes, bevels, lighting and per-item semantic forms",
        "components":49,"facilities":29,"assets":assets
    }
    out=OUT
    out.mkdir(parents=True,exist_ok=True)
    (out/"GENERATION-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"Created {len(comps)} unique component portraits and {len(facilities)} unique facility portraits.")
    print(f"Manifest: {out/'GENERATION-MANIFEST.json'}")
    print("Pic Num values now uniquely identify each named component/facility.")
if __name__=="__main__":
    main()

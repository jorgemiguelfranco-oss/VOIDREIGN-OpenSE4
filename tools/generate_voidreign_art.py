#!/usr/bin/env python3
"""Generate original VOIDREIGN BMP artwork for the bundled GameData tree.

The generator uses only Python's standard library and writes deterministic,
uncompressed 24-bit BMP files in the dimensions expected by OpenSE4's client.
It creates original abstract/sci-fi artwork; it never reads or copies game art.
"""
from __future__ import annotations

import argparse
import math
import random
import struct
from pathlib import Path

FACTIONS = [
    ("Aurel", (72, 170, 218)), ("Dravak", (205, 105, 72)),
    ("Keth", (93, 182, 139)), ("Kharel", (163, 123, 207)),
    ("Myriads", (185, 190, 105)), ("Nyx", (90, 112, 192)),
    ("Olyss", (214, 159, 98)), ("Qorathi", (89, 181, 184)),
    ("Solari", (224, 184, 78)), ("Teran", (96, 147, 207)),
    ("Veyran", (184, 104, 158)), ("Vosk", (135, 174, 104)),
]
NEUTRALS = [
    ("FreeSystems", (91, 174, 180)), ("Driftborn", (133, 151, 196)),
    ("Ashen", (180, 112, 82)),
]
HULLS = ("VF", "AC", "PA", "MF", "CP", "IN", "RS")
PLANETS = ("rock", "star", "ice", "gas", "asteroids", "storm", "warp")
EVENTS = ("MineralBloom", "CivicAccord", "AtmosphericShift", "VeteranCadre",
          "SupplyAnomaly", "DriveCascade", "InfrastructureFailure")


class Bitmap:
    def __init__(self, w: int, h: int, color=(0, 0, 0)):
        self.w, self.h = w, h
        self.data = bytearray(bytes(color) * (w * h))

    def pixel(self, x: int, y: int, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.data[i:i + 3] = bytes(color)

    def rect(self, x: int, y: int, w: int, h: int, color, fill=True):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        if fill:
            row = bytes(color) * (x1 - x0)
            for yy in range(y0, y1):
                p = (yy * self.w + x0) * 3
                self.data[p:p + len(row)] = row
        else:
            self.line(x0, y0, x1 - 1, y0, color)
            self.line(x0, y1 - 1, x1 - 1, y1 - 1, color)
            self.line(x0, y0, x0, y1 - 1, color)
            self.line(x1 - 1, y0, x1 - 1, y1 - 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e = 2 * err
            if e >= dy:
                err += dy
                x0 += sx
            if e <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True, width=1):
        r = max(0, int(r))
        inner = max(0, r - width)
        r2, inner2 = r * r, inner * inner
        for y in range(max(0, cy - r), min(self.h, cy + r + 1)):
            for x in range(max(0, cx - r), min(self.w, cx + r + 1)):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if d <= r2 and (fill or d >= inner2):
                    self.pixel(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color, fill=False, width=1):
        rx, ry = max(1, rx), max(1, ry)
        threshold = (1 - width / max(1, min(rx, ry))) ** 2
        for y in range(max(0, cy - ry), min(self.h, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(self.w, cx + rx + 1)):
                q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if q <= 1 and (fill or q >= threshold):
                    self.pixel(x, y, color)

    def paste(self, other: "Bitmap", ox: int, oy: int):
        for y in range(other.h):
            dy = y + oy
            if not 0 <= dy < self.h:
                continue
            for x in range(other.w):
                dx = x + ox
                if 0 <= dx < self.w:
                    si = (y * other.w + x) * 3
                    color = other.data[si:si + 3]
                    if color != b"\0\0\0":
                        self.pixel(dx, dy, color)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        row = self.w * 3
        stride = (row + 3) & ~3
        size = stride * self.h
        with path.open("wb") as f:
            f.write(struct.pack("<2sIHHI", b"BM", 54 + size, 0, 0, 54))
            f.write(struct.pack("<IiiHHIIiiII", 40, self.w, self.h, 1, 24, 0, size, 2835, 2835, 0, 0))
            pad = b"\0" * (stride - row)
            for y in range(self.h - 1, -1, -1):
                start = y * row
                src = self.data[start:start + row]
                bgr = bytearray(row)
                bgr[0::3], bgr[1::3], bgr[2::3] = src[2::3], src[1::3], src[0::3]
                f.write(bgr)
                f.write(pad)


def blend(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def icon(im: Bitmap, x: int, y: int, w: int, h: int, kind: int, color):
    cx, cy = x + w // 2, y + h // 2
    r = max(2, min(w, h) // 3)
    mode = kind % 8
    if mode == 0:
        im.circle(cx, cy, r, color, False, max(1, w // 18))
        im.line(cx - r, cy, cx + r, cy, color, 2)
        im.line(cx, cy - r, cx, cy + r, color, 2)
    elif mode == 1:
        im.rect(x + w // 4, y + h // 4, w // 2, h // 2, color, False)
        im.line(x + w // 4, cy, x + w * 3 // 4, cy, color, 2)
    elif mode == 2:
        im.circle(cx, cy, r, color, False, 2)
        im.circle(cx, cy, max(2, r // 2), color, False, 2)
        im.line(cx - r, cy, cx + r, cy, color, 1)
    elif mode == 3:
        im.line(cx, y + h // 5, cx, y + h * 4 // 5, color, 3)
        im.line(x + w // 5, cy, x + w * 4 // 5, cy, color, 3)
    elif mode == 4:
        im.line(x + w // 4, y + h * 3 // 4, cx, y + h // 4, color, 3)
        im.line(cx, y + h // 4, x + w * 3 // 4, y + h * 3 // 4, color, 3)
        im.line(x + w // 4, y + h * 3 // 4, x + w * 3 // 4, y + h * 3 // 4, color, 3)
    elif mode == 5:
        im.rect(x + w // 5, y + h // 3, w * 3 // 5, h // 3, color, False)
        im.line(cx, y + h // 5, cx, y + h * 4 // 5, color, 2)
    elif mode == 6:
        im.circle(cx, cy, r, color)
        im.circle(cx, cy, r + 2, color, False, 1)
    else:
        im.ellipse(cx, cy, w // 3, h // 5, color, False, 2)
        im.line(cx - w // 3, cy, cx + w // 3, cy, color, 2)


def starfield(w, h, seed, planet=True):
    rng = random.Random(seed)
    im = Bitmap(w, h)
    cx, cy = int(w * .53), int(h * .48)
    # Dark navy field and a deterministic two-tone nebula, drawn in scan lines.
    for y in range(h):
        ny = (y - cy) / h
        row = bytearray(w * 3)
        for x in range(w):
            nx = (x - cx) / w
            neb = math.exp(-((nx * 2.0) ** 2 + (ny * 2.3) ** 2) * 3.0)
            band = .5 + .5 * math.sin(x * .009 + math.sin(y * .014) * 2 + seed)
            k = neb * (.28 + .52 * band)
            i = x * 3
            row[i:i + 3] = bytes((4 + int(25 * k), 8 + int(36 * k), 22 + int(64 * k)))
        i = y * w * 3
        im.data[i:i + w * 3] = row
    for _ in range(max(100, w * h // 5000)):
        x, y = rng.randrange(w), rng.randrange(h)
        c = rng.choice(((100, 145, 190), (144, 178, 210), (202, 216, 232), (80, 114, 166)))
        im.pixel(x, y, c)
        if rng.random() < .08:
            im.line(x - 2, y, x + 2, y, c)
            im.line(x, y - 2, x, y + 2, c)
    if planet:
        r, px, py = int(min(w, h) * .17), int(w * .77), int(h * .67)
        im.circle(px, py, r + 5, (44, 103, 151), False, 2)
        for y in range(max(0, py - r), min(h, py + r + 1)):
            for x in range(max(0, px - r), min(w, px + r + 1)):
                dx, dy = (x - px) / r, (y - py) / r
                d = dx * dx + dy * dy
                if d <= 1:
                    band = .5 + .5 * math.sin((dy + .13 * math.sin(dx * 7)) * 18)
                    light = max(.15, .98 - .72 * math.sqrt(d) - max(0, dx * .6 + dy * .2))
                    col = (18 + int(30 * band), 63 + int(70 * band), 104 + int(87 * band))
                    im.pixel(x, y, tuple(int(c * light) for c in col))
        im.ellipse(px, py, r + 12, max(8, r // 3), (75, 140, 185), False, 3)
    sx, sy = int(w * .27), int(h * .29)
    im.circle(sx, sy, max(4, h // 65), (255, 217, 153))
    im.circle(sx, sy, max(9, h // 28), (114, 157, 200), False, 2)
    return im


def planet_icon(size, kind, seed):
    rng = random.Random(seed)
    im = Bitmap(size, size)
    cx = cy = size // 2
    colors = {
        "rock": ((44, 91, 128), (173, 139, 95)),
        "star": ((182, 83, 28), (255, 224, 146)),
        "ice": ((35, 88, 146), (179, 222, 244)),
        "gas": ((99, 62, 47), (222, 168, 108)),
        "asteroids": ((73, 92, 107), (155, 169, 178)),
        "storm": ((37, 53, 116), (135, 105, 211)),
        "warp": ((22, 105, 140), (124, 237, 240)),
    }
    lo, hi = colors[kind]
    r = int(size * .36)
    if kind == "asteroids":
        for _ in range(28):
            x, y = rng.randrange(size), rng.randrange(size)
            im.circle(x, y, rng.randrange(1, max(2, size // 14)), rng.choice((lo, hi)))
        return im
    if kind == "warp":
        for q in range(r, 1, -max(3, size // 14)):
            im.circle(cx, cy, q, (90, 220, 235), False, 1)
    for y in range(size):
        for x in range(size):
            dx, dy = (x - cx) / r, (y - cy) / r
            d = dx * dx + dy * dy
            if d <= 1:
                t = .5 + .5 * math.sin((dy * 5 + math.sin(dx * 5)) * 2.1)
                shade = max(.18, .98 - .72 * math.sqrt(d) - max(0, dx * .6 + dy * .22))
                im.pixel(x, y, tuple(int(v * shade) for v in blend(lo, hi, t)))
    im.circle(cx, cy, r + 1, (130, 181, 211), False, 1)
    if kind == "star":
        im.circle(cx, cy, r + 3, (255, 164, 74), False, 2)
    return im


def panel(w, h):
    im = Bitmap(w, h, (7, 15, 28))
    im.rect(0, 0, w, h, (8, 19, 35))
    im.rect(0, 0, w, max(2, h // 8), (22, 46, 70))
    im.line(0, 0, w - 1, 0, (92, 156, 190), 2)
    im.line(0, h - 1, w - 1, h - 1, (38, 82, 117), 2)
    im.line(0, 0, 0, h - 1, (47, 92, 125), 2)
    im.line(w - 1, 0, w - 1, h - 1, (47, 92, 125), 2)
    return im


def sheet(path, cw, ch, cols, rows, count, seed):
    im = Bitmap(cw * cols, ch * rows, (5, 12, 24))
    rng = random.Random(seed)
    palette = ((81, 194, 226), (222, 174, 97), (126, 164, 222), (104, 202, 163))
    for i in range(count):
        x, y = (i % cols) * cw, (i // cols) * ch
        im.rect(x, y, cw, ch, (8, 20, 36))
        im.rect(x + 1, y + 1, cw - 2, ch - 2, (32, 61, 89), False)
        icon(im, x, y, cw, ch, i, rng.choice(palette))
    im.save(path)


def race_art(root: Path, style: str, color, neutral=False):
    group = "RaceGeneric" if style == "Generic" else ("RaceNeutral" if neutral else "Races")
    d = root / "Pictures" / group / style
    if style == "Generic":
        variant = -1
    elif neutral:
        variant = len(FACTIONS) + next((i for i, (name, _) in enumerate(NEUTRALS) if name == style), 0)
    else:
        variant = next((i for i, (name, _) in enumerate(FACTIONS) if name == style), 0)

    main = Bitmap(100, 20, (4, 11, 24))
    main.rect(1, 1, 24, 16, blend(color, (5, 16, 28), .42))
    main.circle(13, 9, 5, (228, 243, 252), False, 1)
    main.rect(26, 0, 2, 20, (77, 110, 144))
    main.rect(28, 0, 12, 20, color)
    for i in range(3):
        icon(main, 40 + i * 20, 0, 20, 20, i + max(0, variant) + 31, color)
    main.save(d / f"{style}_Main.bmp")

    # Each species has a distinct silhouette language. These are abstract
    # alien busts rather than one human face with fifteen palette swaps.
    portrait = Bitmap(128, 128, (5, 12, 25))
    portrait.circle(64, 66, 48, blend(color, (6, 23, 42), .38))
    portrait.circle(64, 66, 48, color, False, 3)
    if variant % 6 == 0:
        portrait.ellipse(64, 65, 27, 36, blend(color, (218, 231, 243), .3), True)
        portrait.line(45, 43, 35, 23, color, 6)
        portrait.line(83, 43, 93, 23, color, 6)
        portrait.circle(53, 57, 4, (235, 248, 255))
        portrait.circle(75, 57, 4, (235, 248, 255))
    elif variant % 6 == 1:
        portrait.ellipse(64, 66, 36, 27, blend(color, (218, 231, 243), .28), True)
        portrait.line(32, 58, 15, 39, color, 5)
        portrait.line(96, 58, 113, 39, color, 5)
        portrait.line(42, 79, 31, 104, color, 3)
        portrait.line(86, 79, 97, 104, color, 3)
        for x in (49, 64, 79):
            portrait.circle(x, 57, 3, (235, 248, 255))
    elif variant % 6 == 2:
        portrait.ellipse(64, 66, 24, 39, blend(color, (218, 231, 243), .3), True)
        portrait.line(49, 40, 35, 15, color, 3)
        portrait.line(64, 35, 64, 9, color, 3)
        portrait.line(79, 40, 93, 15, color, 3)
        portrait.circle(53, 58, 4, (235, 248, 255))
        portrait.circle(75, 58, 4, (235, 248, 255))
        portrait.line(49, 87, 79, 87, blend(color, (18, 33, 52), .3), 4)
    elif variant % 6 == 3:
        portrait.ellipse(64, 67, 30, 34, blend(color, (218, 231, 243), .22), True)
        portrait.line(36, 64, 51, 31, color, 5)
        portrait.line(51, 31, 64, 18, color, 5)
        portrait.line(64, 18, 77, 31, color, 5)
        portrait.line(77, 31, 92, 64, color, 5)
        portrait.circle(53, 59, 4, (235, 248, 255))
        portrait.circle(75, 59, 4, (235, 248, 255))
        portrait.line(64, 50, 64, 91, blend(color, (18, 33, 52), .2), 2)
    elif variant % 6 == 4:
        portrait.ellipse(64, 67, 31, 34, blend(color, (218, 231, 243), .24), True)
        for x, y in ((48, 53), (80, 53), (56, 70), (72, 70)):
            portrait.circle(x, y, 4, (235, 248, 255))
        portrait.line(42, 81, 31, 104, color, 4)
        portrait.line(86, 81, 97, 104, color, 4)
    else:
        portrait.ellipse(64, 67, 34, 31, blend(color, (218, 231, 243), .24), True)
        portrait.ellipse(64, 65, 43, 40, color, False, 4)
        portrait.circle(52, 58, 4, (235, 248, 255))
        portrait.circle(76, 58, 4, (235, 248, 255))
        for x in (35, 44, 84, 93):
            portrait.line(x, 80, x + (x - 64) // 3, 105, color, 3)
    portrait.line(53, 91, 75, 91, blend(color, (18, 33, 52), .28), 3)
    # A species mark is cut into the brow and is repeated on its ship portraits.
    icon(portrait, 51, 24, 26, 22, max(0, variant), (224, 242, 252))
    portrait.save(d / f"{style}_Race_Portrait.bmp")

    for suffix, size in (("Pop_Mini", 20), ("Pop_Portrait", 36)):
        pop = Bitmap(size, size, (5, 12, 25))
        pop.circle(size // 2, size // 2, size * 35 // 100, color)
        pop.circle(size // 2, size // 2, size * 35 // 100, (214, 235, 248), False, 1)
        icon(pop, size // 6, size // 6, size * 4 // 6, size * 4 // 6,
             max(0, variant), (238, 248, 255))
        pop.save(d / f"{style}_{suffix}.bmp")

    # Every faction/neutral has its own colour and silhouette variant for
    # every ship class. Hull classes also differ in span, bridge and engines.
    for idx, code in enumerate(HULLS):
        tint = blend(color, (232, 243, 252), .18)
        profile = (max(0, variant) + idx) % 5
        width = 6 + ((idx + max(0, variant)) % 5) * 2
        mini = Bitmap(36, 36)
        mini.circle(18, 18, 16, blend(color, (5, 15, 29), .65), False, 1)
        if profile == 0:
            mini.line(18, 3, 18, 33, tint, 2 + idx % 2)
            mini.line(18, 10, 18 - width, 27, color, 2)
            mini.line(18, 10, 18 + width, 27, color, 2)
        elif profile == 1:
            mini.line(18, 4, 18, 32, tint, 3)
            mini.line(18, 15, 3, 20, color, 3)
            mini.line(18, 15, 33, 20, color, 3)
            mini.line(18, 24, 7, 30, color, 2)
            mini.line(18, 24, 29, 30, color, 2)
        elif profile == 2:
            mini.line(18, 3, 18, 33, tint, 3)
            mini.line(18, 14, 4, 29, color, 3)
            mini.line(18, 14, 32, 29, color, 3)
            mini.line(4, 29, 18, 25, tint, 1)
            mini.line(32, 29, 18, 25, tint, 1)
        elif profile == 3:
            mini.line(18, 3, 18, 33, tint, 2)
            mini.line(18, 16, 4, 16, color, 3)
            mini.line(18, 16, 32, 16, color, 3)
            mini.line(18, 23, 8, 31, color, 2)
            mini.line(18, 23, 28, 31, color, 2)
        else:
            mini.line(18, 3, 18, 33, tint, 3)
            mini.line(18, 11, 5, 24, color, 3)
            mini.line(18, 18, 31, 24, color, 3)
            mini.line(18, 25, 9, 32, tint, 2)
            mini.line(18, 25, 27, 32, tint, 2)
        mini.circle(18, 7, 2 + idx % 2, (230, 246, 255))
        mini.circle(18, 31, 2, (68, 206, 235))
        mini.save(d / f"{style}_Mini_{code}.bmp")

        portrait = Bitmap(128, 128, (5, 12, 25))
        portrait.circle(64, 64, 57, blend(color, (5, 14, 28), .58))
        portrait.circle(64, 64, 57, color, False, 2)
        orbit = 48 + (idx % 3) * 3
        portrait.ellipse(64, 66, orbit, 17 + (idx % 2) * 5,
                         blend(color, (16, 36, 55), .25), False, 3)
        if profile == 0:
            portrait.line(64, 13, 64, 111, tint, 6)
            portrait.line(64, 32, 29, 93, color, 4)
            portrait.line(64, 32, 99, 93, color, 4)
        elif profile == 1:
            portrait.line(64, 16, 64, 110, tint, 7)
            portrait.line(64, 41, 12, 67, color, 5)
            portrait.line(64, 41, 116, 67, color, 5)
            portrait.line(35, 80, 93, 80, color, 3)
        elif profile == 2:
            portrait.line(64, 12, 64, 111, tint, 8)
            portrait.line(64, 31, 17, 100, color, 5)
            portrait.line(64, 31, 111, 100, color, 5)
            portrait.line(17, 100, 64, 83, tint, 2)
            portrait.line(111, 100, 64, 83, tint, 2)
        elif profile == 3:
            portrait.line(64, 13, 64, 112, tint, 6)
            portrait.line(64, 48, 11, 48, color, 6)
            portrait.line(64, 48, 117, 48, color, 6)
            portrait.line(36, 85, 92, 85, color, 4)
        else:
            portrait.line(64, 14, 64, 110, tint, 7)
            portrait.line(64, 37, 18, 72, color, 5)
            portrait.line(64, 58, 110, 72, color, 5)
            portrait.line(30, 96, 97, 96, color, 3)
        portrait.circle(64, 31, 8, (225, 244, 255))
        portrait.save(d / f"{style}_Portrait_{code}.bmp")

def hull_art(root: Path, code: str, idx: int):
    d = root / "Pictures" / "RaceGeneric"
    color = (106 + idx * 12 % 100, 165, 210)
    mini = Bitmap(36, 36)
    mini.line(18, 3, 18, 32, color, 3)
    mini.line(18, 8, 7 + idx % 3, 26, (78, 129, 177), 2)
    mini.line(18, 8, 29 - idx % 3, 26, (78, 129, 177), 2)
    mini.circle(18, 8, 3, (228, 245, 255))
    mini.save(d / f"Generic_Mini_{code}.bmp")
    portrait = Bitmap(128, 128, (5, 12, 25))
    portrait.circle(64, 64, 50, (22, 45, 70))
    portrait.circle(64, 64, 50, color, False, 2)
    portrait.line(64, 17, 64, 110, (144, 198, 228), 7)
    portrait.line(64, 33, 30 + idx % 3 * 4, 96, color, 4)
    portrait.line(64, 33, 98 - idx % 3 * 4, 96, color, 4)
    portrait.circle(64, 34, 7, (225, 245, 255))
    portrait.save(d / f"Generic_Portrait_{code}.bmp")


def build(root: Path):
    pic = root / "Pictures"
    # Original high-resolution intro and system map backgrounds.
    starfield(1024, 768, 24).save(pic / "Game/Screens/1024X768/Intro.bmp")
    starfield(800, 600, 25).save(pic / "Game/Screens/800X600/Intro.bmp")
    starfield(660, 660, 26).save(pic / "Systems/1024X768/Starfield.bmp")
    starfield(490, 490, 27).save(pic / "Systems/800X600/Starfield.bmp")
    starfield(660, 660, 28).save(pic / "Systems/1024X768/Starmap.bmp")
    starfield(490, 490, 29).save(pic / "Systems/800X600/Starmap.bmp")
    starfield(128, 128, 30).save(pic / "Systems/Starfield.bmp")
    for n in range(1, 9):
        starfield(72, 72, 40 + n, False).save(pic / f"Systems/Ion StormTile{n}.bmp")

    # Planets: the 36px strip is indexed by SectType; portraits by 1-based picture.
    strip = Bitmap(36 * len(PLANETS), 36)
    for i, kind in enumerate(PLANETS):
        strip.paste(planet_icon(36, kind, i + 1), i * 36, 0)
        planet_icon(128, kind, i + 11).save(pic / f"Planets/p{i + 1:04d}.bmp")
    strip.save(pic / "Planets/Planets.bmp")

    # Component Pic Num values are modulo 64 in the generated data; provide all cells.
    sheet(pic / "Components/Components.bmp", 36, 36, 60, 1, 60, 60)
    for i in range(1, 61):
        sheet(pic / f"Components/Comp_{i:03d}.bmp", 128, 128, 1, 1, 1, i + 100)
    # Facility records are numbered 1..14 in file order.
    sheet(pic / "Facilities/Facility.bmp", 36, 36, 14, 1, 14, 80)
    for i in range(1, 15):
        sheet(pic / f"Facilities/Facil_{i:03d}.bmp", 128, 128, 1, 1, 1, i + 150)

    general = Bitmap(380, 176, (5, 12, 24))
    for i, kind in enumerate(PLANETS[:6]):
        general.paste(planet_icon(16, kind, i + 31), i * 16, 0)
        general.paste(planet_icon(32, kind, i + 41), i * 32, 32)
    for i in range(38):
        icon(general, (i % 19) * 20, 136 + (i // 19) * 20, 20, 20, i, (105 + i * 11 % 100, 184, 220))
    for x in (177, 190, 203):
        general.circle(x + 5, 6, 4, (91, 211, 150))
        general.circle(x + 5, 6, 4, (218, 244, 228), False, 1)
    general.save(pic / "Game/General.bmp")

    for layout, width, height in (("1024X768", 1024, 768), ("800X600", 800, 600)):
        d = pic / f"Game/Screens/{layout}"
        dims = {
            "Top.bmp": (width, 29), "Toptitle.bmp": (width, 77),
            "Topsys.bmp": (width, 7), "Bottom.bmp": (width, 8 if width > 800 else 6),
            "Left.bmp": (10, height), "Middle.bmp": (16, 662 if width > 800 else 565),
            "Right.bmp": (67 if width > 800 else 12, height),
            "Topgal.bmp": (360 if width > 800 else 300, 9),
        }
        for name, (w, h) in dims.items():
            panel(w, h).save(d / name)
        if width > 800:
            panel(62, 365).save(d / "RightFiller.bmp")
        else:
            panel(1, 1).save(d / "RightFiller.bmp")
    panel(300, 200).save(pic / "Game/Dialogs/MainParts.bmp")
    panel(256, 24).save(pic / "Game/Dialogs/Rowgrid.bmp")

    # Indexed classic button sheets.
    for name, cw, ch, cols, rows, count, seed in (
        ("Main.bmp", 34, 34, 12, 3, 36, 3), ("Orders.bmp", 34, 34, 23, 12, 276, 7),
        ("Close.bmp", 20, 20, 3, 3, 9, 9), ("BigLeftRightArrows.bmp", 14, 50, 2, 3, 6, 11),
        ("Nextprev.bmp", 48, 24, 4, 3, 12, 12), ("DetailUp.bmp", 33, 21, 1, 3, 3, 13),
        ("BigUpDownArrows.bmp", 64, 17, 2, 3, 6, 14), ("SmallLeftRightArrows.bmp", 16, 38, 2, 3, 6, 15),
        ("Arrows.bmp", 24, 24, 2, 3, 6, 16), ("TabBtns.bmp", 72, 30, 2, 2, 4, 17),
    ):
        sheet(pic / "Game/Buttons" / name, cw, ch, cols, rows, count, seed)

    # Illustrated event cards are referenced by the actual Events.txt
    # records and displayed in the event log using Art::eventPicture.
    event_palette = (
        (216, 178, 91), (104, 200, 148), (97, 173, 219),
        (178, 157, 221), (212, 133, 75), (222, 109, 82), (148, 156, 174),
    )
    for idx, (name, color) in enumerate(zip(EVENTS, event_palette)):
        card = Bitmap(128, 128, (5, 12, 25))
        for y in range(128):
            shade = y / 127
            card.rect(0, y, 128, 1, blend((8, 18, 35), blend(color, (5, 12, 25), .72), shade * .65))
        card.circle(64, 64, 56, blend(color, (8, 19, 35), .25), False, 3)
        card.circle(64, 64, 46, (58, 91, 126), False, 1)
        card.ellipse(64, 64, 53, 18, blend(color, (220, 239, 250), .22), False, 2)
        icon(card, 18, 18, 92, 92, idx + 2, blend(color, (241, 247, 252), .16))
        card.line(15, 112, 113, 112, blend(color, (238, 246, 251), .25), 2)
        card.save(pic / "Events" / f"{name}.bmp")

    # Twelve playable species and three neutral powers.
    for idx, (name, color) in enumerate(FACTIONS):
        race_art(root, name, color)
    for idx, (name, color) in enumerate(NEUTRALS):
        race_art(root, name, color, True)
    generic = pic / "RaceGeneric"
    race_art(root, "Generic", (112, 161, 198), True)
    for idx, code in enumerate(HULLS):
        hull_art(root, code, idx)
    for idx, group in enumerate(("Fleet", "FighterGroup")):
        hull_art(root, group, idx + 12)

    # Generic racial main/popup portrait and group fallbacks are required even
    # when a race has no custom ship or fleet artwork.
    for group in ("Fleet", "FighterGroup"):
        if not (generic / f"Generic_Mini_{group}.bmp").exists():
            hull_art(root, group, 0)

    print(f"Generated VOIDREIGN artwork in {pic}")


def dimensions(path: Path):
    try:
        data = path.read_bytes()[:30]
        if len(data) < 30 or data[:2] != b"BM":
            return None
        w, h, planes, bits = struct.unpack("<iiHH", data[18:30])
        return (w, h) if planes == 1 and bits == 24 else None
    except OSError:
        return None


def verify(root: Path):
    p = root / "Pictures"
    required = {
        "Game/General.bmp": (380, 176),
        "Game/Buttons/Main.bmp": (408, 102),
        "Game/Buttons/Orders.bmp": (782, 408),
        "Game/Screens/1024X768/Intro.bmp": (1024, 768),
        "Game/Screens/1024X768/Top.bmp": (1024, 29),
        "Game/Screens/1024X768/Toptitle.bmp": (1024, 77),
        "Game/Screens/800X600/Middle.bmp": (16, 565),
        "Game/Screens/800X600/Right.bmp": (12, 600),
        "Game/Screens/800X600/Bottom.bmp": (800, 6),
        "Systems/1024X768/Starmap.bmp": (660, 660),
        "Systems/1024X768/Starfield.bmp": (660, 660),
        "Systems/800X600/Starfield.bmp": (490, 490),
        "Planets/Planets.bmp": (252, 36),
        "Planets/p0007.bmp": (128, 128),
        "Components/Components.bmp": (2160, 36),
        "Components/Comp_060.bmp": (128, 128),
        "Facilities/Facility.bmp": (504, 36),
        "Facilities/Facil_014.bmp": (128, 128),
        "RaceGeneric/Generic_Race_Portrait.bmp": (128, 128),
        "RaceGeneric/Generic_Mini_VF.bmp": (36, 36),
        "RaceGeneric/Generic_Portrait_Fleet.bmp": (128, 128),\n        "Races/Aurel/Aurel_Mini_VF.bmp": (36, 36),\n        "Races/Aurel/Aurel_Portrait_VF.bmp": (128, 128),
        "Systems/Ion StormTile1.bmp": (72, 72),
        "Events/MineralBloom.bmp": (128, 128),
        "Events/CivicAccord.bmp": (128, 128),
        "Events/AtmosphericShift.bmp": (128, 128),
        "Events/VeteranCadre.bmp": (128, 128),
        "Events/SupplyAnomaly.bmp": (128, 128),
        "Events/DriveCascade.bmp": (128, 128),
        "Events/InfrastructureFailure.bmp": (128, 128),
    }
    errors = []
    for name, expected in required.items():
        actual = dimensions(p / name)
        if actual != expected:
            errors.append(f"Pictures/{name}: got {actual}, expected {expected}")
    for name, _ in FACTIONS:
        d = p / "Races" / name
        for suffix, size in (("Main.bmp", (100, 20)), ("Race_Portrait.bmp", (128, 128)),
                             ("Pop_Mini.bmp", (20, 20)), ("Pop_Portrait.bmp", (36, 36))):
            path = d / f"{name}_{suffix}"
            if dimensions(path) != size:
                errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected {size}")
        for code in HULLS:
            for kind, size in (("Mini", (36, 36)), ("Portrait", (128, 128))):
                path = d / f"{name}_{kind}_{code}.bmp"
                if dimensions(path) != size:
                    errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected {size}")
    for name, _ in NEUTRALS:
        d = p / "RaceNeutral" / name
        for suffix, size in (("Main.bmp", (100, 20)), ("Race_Portrait.bmp", (128, 128)),
                             ("Pop_Mini.bmp", (20, 20)), ("Pop_Portrait.bmp", (36, 36))):
            path = d / f"{name}_{suffix}"
            if dimensions(path) != size:
                errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected {size}")
        for code in HULLS:
            for kind, size in (("Mini", (36, 36)), ("Portrait", (128, 128))):
                path = d / f"{name}_{kind}_{code}.bmp"
                if dimensions(path) != size:
                    errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected {size}")
    for index in range(1, 61):
        path = p / f"Components/Comp_{index:03d}.bmp"
        if dimensions(path) != (128, 128):
            errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected (128, 128)")
    for index in range(1, 15):
        path = p / f"Facilities/Facil_{index:03d}.bmp"
        if dimensions(path) != (128, 128):
            errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected (128, 128)")
    for code in HULLS + ("Fleet", "FighterGroup"):
        for kind, size in (("Mini", (36, 36)), ("Portrait", (128, 128))):
            path = p / "RaceGeneric" / f"Generic_{kind}_{code}.bmp"
            if dimensions(path) != size:
                errors.append(f"{path.relative_to(root)}: got {dimensions(path)}, expected {size}")
    if sum(1 for path in p.rglob("*.bmp")) < 400:
        errors.append("Generated artwork coverage unexpectedly contains fewer than 400 BMP files")
    if errors:
        raise SystemExit("VOIDREIGN art validation failed:\n" + "\n".join(errors))
    count = sum(1 for path in p.rglob("*.bmp"))
    print(f"VOIDREIGN art validated: {count} BMP files; core UI, maps, planets, modules, hull fallbacks and 15 species")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", type=Path, default=Path("GameData"))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify(args.output)
    else:
        build(args.output)


if __name__ == "__main__":
    main()

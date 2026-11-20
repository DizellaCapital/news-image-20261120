#!/usr/bin/env python3
"""news-image-20261120 v3 — front page rebuilt in the winners' classic newspaper grammar.

Cream serif masthead, stat strip DIRECTLY under the masthead, 3 literal hero
scenes, 10 vignettes in two rows of 5 with headlines, every story numbered
1-44, world map at the BOTTOM with pins, date-check footer.

Deterministic: Pillow + DejaVu fonts only, no randomness, no clock, no network.
Renders entry.png (1024x1024) next to this script. Run: python3 render.py
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 242, 231)
PAPER = (250, 246, 236)
INK = (26, 26, 26)
RED = (178, 34, 34)
GREY = (105, 105, 100)
LIGHT_GREY = (180, 175, 165)
OCEAN = (216, 230, 233)
LAND = (203, 191, 158)
LAND_LINE = (138, 127, 102)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_c(d, cx, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, y), s, font=font, fill=fill)


def text_lines(d, x, y, lines, font, fill, leading=None):
    if leading is None:
        leading = font.size + 3
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def badge(d, x, y, n, r=11):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=2)
    f = F(SANS_B, 12 if r >= 11 else 10)
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((x - tw / 2, y - 8 if r >= 11 else y - 7), t, font=f, fill=(255, 255, 255))


def rule(d, x0, x1, y, width=1, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- scenes
def scene_kyiv(d, x, y, w, h):
    # Night sky gradient bands
    top, bot = (13, 24, 43), (38, 56, 76)
    bands = 14
    for i in range(bands):
        t = i / (bands - 1)
        col = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        d.rectangle([x, y + i * h // bands, x + w, y + (i + 1) * h // bands + 1], fill=col)
    # Stars
    for sx, sy in [(18, 14), (52, 30), (96, 10), (140, 26), (180, 12), (220, 34),
                   (260, 16), (300, 30), (40, 52), (150, 48), (240, 58), (285, 52)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(230, 230, 210))
    # Missile trails (diagonal, glowing heads)
    for (tx, ty, ln) in [(40, 8, 90), (150, 4, 110), (250, 12, 80)]:
        d.line([(x + tx, y + ty), (x + tx + ln, y + ty + int(ln * 0.55))],
               fill=(255, 214, 120), width=3)
        d.ellipse([x + tx + ln - 4, y + ty + int(ln * 0.55) - 4,
                   x + tx + ln + 4, y + ty + int(ln * 0.55) + 4], fill=(255, 240, 180))
    # Skyline silhouettes
    base = y + h
    heights = [58, 84, 66, 104, 78, 92, 60, 110, 72, 88, 64, 96, 70]
    bw = w / len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx, base - hh, bx + bw - 2, base], fill=(8, 14, 24))
        for wy in range(base - hh + 10, base - 8, 14):
            if (i * 7 + wy) % 3 == 0:
                d.rectangle([bx + 4, wy, bx + 8, wy + 5], fill=(255, 210, 110))
    # Explosions on the skyline
    for ex, ey, r in [(90, base - 96, 16), (215, base - 108, 20)]:
        for rr, col in [(r, (255, 140, 40)), (int(r * 0.6), (255, 200, 90)),
                        (int(r * 0.3), (255, 240, 180))]:
            d.ellipse([x + ex - rr, ey - rr, x + ex + rr, ey + rr], fill=col)
        for a in range(0, 360, 45):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(x + ex + dx * r, ey + dy * r),
                    (x + ex + dx * (r + 9), ey + dy * (r + 9))], fill=(255, 170, 60), width=2)
    # Smoke
    for sx, sy, sr in [(70, base - 130, 26), (120, base - 118, 20), (235, base - 140, 24)]:
        d.ellipse([x + sx - sr, sy - sr // 2, x + sx + sr, sy + sr // 2], fill=(90, 95, 105))


def scene_akvan(d, x, y, w, h):
    # Sky and sea
    d.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(176, 205, 224))
    d.rectangle([x, y + int(h * 0.42), x + w, y + h], fill=(43, 103, 133))
    # Clouds
    for cx, cy, cr in [(40, 18, 22), (80, 12, 16), (240, 20, 24), (280, 12, 15)]:
        d.ellipse([x + cx - cr, y + cy - cr // 2, x + cx + cr, y + cy + cr // 2],
                  fill=(235, 240, 242))
    # Coastline (land on the right)
    d.polygon([(x + w, y + int(h * 0.42)), (x + int(w * 0.72), y + int(h * 0.42)),
               (x + int(w * 0.78), y + int(h * 0.62)), (x + int(w * 0.70), y + h),
               (x + w, y + h)], fill=(198, 178, 138))
    d.line([(x + int(w * 0.72), y + int(h * 0.42)), (x + int(w * 0.78), y + int(h * 0.62)),
            (x + int(w * 0.70), y + h)], fill=(150, 130, 100), width=2)
    # Cyclone spiral over the coast
    cx, cy = x + int(w * 0.52), y + int(h * 0.40)
    for k, (r, a0, a1) in enumerate([(66, 20, 300), (52, 140, 420), (38, 260, 540),
                                    (25, 40, 320), (13, 160, 430)]):
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(255, 255, 255), width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(30, 60, 80))
    # Rain streaks
    for rx in range(10, w - 10, 22):
        d.line([(x + rx, y + 8), (x + rx - 6, y + 34)], fill=(220, 235, 240), width=2)
    # Whitecaps
    for wx, wy in [(30, int(h * 0.55)), (90, int(h * 0.68)), (160, int(h * 0.58)),
                   (230, int(h * 0.72)), (290, int(h * 0.62))]:
        d.arc([x + wx - 14, y + wy - 5, x + wx + 14, y + wy + 5], 180, 360,
              fill=(220, 235, 240), width=2)


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 224, 200))
    # Sun
    sx, sy = x + w - 42, y + 30
    for a in range(0, 360, 30):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(sx + dx * 18, sy + dy * 18), (sx + dx * 26, sy + dy * 26)],
               fill=(220, 160, 40), width=3)
    d.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(240, 190, 60))
    # Globe (left)
    gx, gy, gr = x + 78, y + int(h * 0.52), 62
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(110, 165, 205),
              outline=(40, 80, 110), width=2)
    for lon in (-40, 0, 40):
        d.arc([gx - gr + abs(lon) // 2, gy - gr, gx + gr - abs(lon) // 2, gy + gr],
              270 if lon >= 0 else 90, 90 if lon >= 0 else 270, fill=(230, 240, 245), width=1)
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=(230, 240, 245), width=1)
    d.arc([gx - gr, gy - gr // 2, gx + gr, gy + gr // 2], 0, 360, fill=(230, 240, 245), width=1)
    for (lx, ly, lr) in [(-28, -18, 16), (18, 8, 20), (28, -28, 12), (-8, 26, 12)]:
        d.ellipse([gx + lx - lr, gy + ly - lr // 2, gx + lx + lr, gy + ly + lr // 2],
                  fill=(96, 150, 90))
    # Thermometer (right)
    tx = x + w - 88
    d.rounded_rectangle([tx, y + 26, tx + 26, y + h - 34], radius=13,
                        outline=(120, 60, 60), width=2, fill=(255, 255, 255))
    d.ellipse([tx - 8, y + h - 52, tx + 34, y + h - 18], fill=(200, 60, 50))
    d.rounded_rectangle([tx + 6, y + 44, tx + 20, y + h - 40], radius=7, fill=(210, 70, 55))
    for i, ty in enumerate(range(y + 34, y + h - 60, 16)):
        d.line([(tx + 26, ty), (tx + 34, ty)], fill=(120, 60, 60), width=2)
    # Ground line + small flags
    d.line([(x + 14, y + h - 12), (x + w - 14, y + h - 12)], fill=(120, 110, 90), width=2)
    for fx, col in [(x + 170, (60, 120, 90)), (x + 200, (180, 60, 50)), (x + 230, (60, 90, 160))]:
        d.line([(fx, y + h - 12), (fx, y + h - 40)], fill=INK, width=2)
        d.polygon([(fx, y + h - 40), (fx + 18, y + h - 35), (fx, y + h - 30)], fill=col)


def mini(d, x, y, w, h, kind):
    bg = {
        "power": (43, 43, 58), "border": (62, 92, 58), "tower": (91, 107, 122),
        "scales": (122, 106, 79), "chart_down": (122, 46, 46), "mine": (107, 90, 46),
        "runner": (46, 90, 122), "court": (74, 74, 85), "chart_up": (46, 107, 51),
        "vangogh": (30, 58, 95),
    }[kind]
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if kind == "power":
        d.line([(x + 20, y + h), (x + 34, y + 8), (x + 48, y + h)], fill=(200, 200, 210), width=2)
        d.line([(x + 12, y + 16), (x + 56, y + 16)], fill=(200, 200, 210), width=2)
        d.polygon([(x + w - 26, y + 6), (x + w - 14, y + 20), (x + w - 22, y + 20),
                   (x + w - 12, y + 38), (x + w - 30, y + 18), (x + w - 20, y + 18)],
                  fill=(255, 220, 80))
    elif kind == "border":
        for fx in range(x + 8, x + w - 6, 12):
            d.line([(fx, y + 6), (fx, y + h - 6)], fill=(220, 225, 210), width=2)
        d.line([(x, y + 12), (x + w, y + 12)], fill=(220, 225, 210), width=2)
        d.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(220, 225, 210), width=2)
        d.rectangle([x + w - 46, y + 4, x + w - 4, y + 14], fill=(40, 90, 160))
        d.rectangle([x + w - 46, y + 14, x + w - 4, y + 24], fill=(20, 20, 20))
        d.rectangle([x + w - 46, y + 24, x + w - 4, y + 34], fill=(240, 240, 240))
    elif kind == "tower":
        d.polygon([(x + w // 2 - 16, y + h), (x + w // 2 - 8, y + 8),
                   (x + w // 2 + 6, y + 8), (x + w // 2 + 14, y + h)], fill=(40, 48, 58))
        for wy in range(y + 14, y + h - 4, 10):
            d.rectangle([x + w // 2 - 10, wy, x + w // 2 - 4, wy + 4], fill=(255, 210, 110))
            d.rectangle([x + w // 2 + 2, wy, x + w // 2 + 8, wy + 4], fill=(255, 210, 110))
        d.line([(x + w // 2 + 2, y + 10), (x + w // 2 - 4, y + 24), (x + w // 2 + 4, y + 36),
                (x + w // 2 - 2, y + 48)], fill=(255, 90, 60), width=2)
    elif kind == "scales":
        d.line([(x + w // 2, y + 8), (x + w // 2, y + h - 8)], fill=(245, 235, 210), width=3)
        d.line([(x + w // 2 - 34, y + 16), (x + w // 2 + 34, y + 16)], fill=(245, 235, 210), width=3)
        for s in (-1, 1):
            px = x + w // 2 + s * 30
            d.line([(px, y + 16), (px, y + 30)], fill=(245, 235, 210), width=2)
            d.arc([px - 12, y + 28, px + 12, y + 44], 0, 180, fill=(245, 235, 210), width=2)
        d.ellipse([x + w // 2 - 5, y + 6, x + w // 2 + 5, y + 16], fill=(245, 235, 210))
    elif kind == "chart_down":
        pts = [(x + 10, y + 10), (x + 40, y + 16), (x + 70, y + 12), (x + 100, y + 26),
               (x + 130, y + 22), (x + 160, y + 40), (x + w - 10, y + 44)]
        d.line(pts, fill=(255, 255, 255), width=3, joint="curve")
        d.polygon([(x + w - 10, y + 44), (x + w - 22, y + 40), (x + w - 12, y + 32)],
                  fill=(255, 255, 255))
        for gx in range(x + 8, x + w - 4, 18):
            d.line([(gx, y + h - 8), (gx, y + h - 4)], fill=(255, 255, 255), width=1)
    elif kind == "mine":
        d.polygon([(x + w // 2 - 26, y + h), (x + w // 2 - 14, y + 10),
                   (x + w // 2 + 14, y + 10), (x + w // 2 + 26, y + h)], fill=(30, 25, 18))
        for nx, ny, nr in [(x + w // 2 - 34, y + h - 12, 6), (x + w // 2 + 30, y + h - 10, 5),
                           (x + w // 2 + 40, y + h - 16, 4)]:
            d.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(255, 205, 70))
        d.line([(x + 10, y + 12), (x + w - 10, y + 12)], fill=(220, 210, 180), width=2)
    elif kind == "runner":
        d.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(255, 255, 255), width=2)
        d.line([(x, y + h - 22), (x + w, y + h - 22)], fill=(200, 220, 235), width=1)
        hx, hy = x + 46, y + 16
        d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(255, 255, 255))
        d.line([(hx, hy + 5), (hx + 4, hy + 18)], fill=(255, 255, 255), width=3)
        d.line([(hx, hy + 10), (hx - 10, hy + 4)], fill=(255, 255, 255), width=3)
        d.line([(hx, hy + 10), (hx + 12, hy + 16)], fill=(255, 255, 255), width=3)
        d.line([(hx + 4, hy + 18), (hx - 8, hy + 30)], fill=(255, 255, 255), width=3)
        d.line([(hx + 4, hy + 18), (hx + 16, hy + 28)], fill=(255, 255, 255), width=3)
        d.ellipse([x + w - 34, y + 8, x + w - 12, y + 30], outline=(255, 220, 80), width=2)
        d.line([(x + w - 23, y + 19), (x + w - 23, y + 12)], fill=(255, 220, 80), width=2)
        d.line([(x + w - 23, y + 19), (x + w - 17, y + 15)], fill=(255, 220, 80), width=2)
    elif kind == "court":
        for cx in (x + 22, x + w // 2, x + w - 26):
            d.rectangle([cx - 5, y + 12, cx + 5, y + h - 12], fill=(235, 230, 215))
        d.rectangle([x + 8, y + 6, x + w - 8, y + 12], fill=(235, 230, 215))
        d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 6], fill=(235, 230, 215))
        d.rectangle([x + w - 30, y + h - 30, x + w - 14, y + h - 22], fill=(160, 120, 60))
        d.line([(x + w - 22, y + h - 22), (x + w - 22, y + h - 12)], fill=(160, 120, 60), width=3)
    elif kind == "chart_up":
        pts = [(x + 10, y + h - 12), (x + 40, y + h - 20), (x + 70, y + h - 16),
               (x + 100, y + h - 30), (x + 130, y + h - 26), (x + 160, y + 12),
               (x + w - 10, y + 8)]
        d.line(pts, fill=(255, 255, 255), width=3, joint="curve")
        d.polygon([(x + w - 10, y + 8), (x + w - 24, y + 8), (x + w - 12, y + 18)],
                  fill=(255, 255, 255))
        f = F(SANS_B, 13)
        d.text((x + 10, y + 8), "ANT", font=f, fill=(255, 255, 255))
    elif kind == "vangogh":
        for (rx, ry, rr, a0, a1) in [(40, 22, 16, 200, 340), (90, 16, 12, 160, 300),
                                     (140, 26, 18, 200, 330), (60, 34, 10, 0, 200)]:
            d.arc([x + rx - rr, y + ry - rr, x + rx + rr, y + ry + rr], a0, a1,
                  fill=(255, 210, 90), width=3)
        for sx, sy in [(20, 10), (120, 8), (165, 12), (150, 38), (30, 38)]:
            d.polygon([(x + sx, y + sy - 5), (x + sx + 2, y + sy - 2), (x + sx + 5, y + sy),
                       (x + sx + 2, y + sy + 2), (x + sx, y + sy + 5), (x + sx - 2, y + sy + 2),
                       (x + sx - 5, y + sy), (x + sx - 2, y + sy - 2)], fill=(255, 230, 140))
        d.ellipse([x + w - 34, y + 6, x + w - 14, y + 26], fill=(245, 230, 180))


# ---------------------------------------------------------------- content
STATS = [
    ("50,000", "evacuated as Cyclone Akvan hits Odisha"),
    ("5", "killed in Kyiv's overnight barrage"),
    ("\u22126.6%", "Taiex falls on AI bubble fears"),
    ("$97.17", "Anthropic closes +17% on debut"),
    ("24.6M", "GTA VI day-one copies sold"),
    ("589M", "children lived in war zones in 2025"),
]

REGIONS = [
    ("EUROPE", (31, 58, 95)), ("MIDDLE EAST", (140, 74, 47)),
    ("ASIA-PACIFIC", (46, 107, 107)), ("AFRICA", (154, 123, 45)),
    ("AMERICAS", (74, 93, 35)), ("CLIMATE", (47, 107, 51)),
]

UTC_ITEMS = [
    ("01:22", "Kyiv barrage"), ("02:00", "Akvan landfall"),
    ("04:22", "Kharkiv hospital"), ("05:45", "COP31 opens"),
    ("07:37", "Ukraine power cuts"), ("09:34", "N. Korea missile"),
]

HEROES = [
    (1, scene_kyiv, "Russia's overnight barrage kills five in Kyiv and Lviv",
     "Ballistic missiles and drones hit Kyiv for 6+ hours; three Dnipro bridges damaged.",
     "CNN \u00b7 20 NOV"),
    (15, scene_akvan, "Cyclone Akvan makes landfall near Gopalpur, Odisha",
     "Winds 70\u201380 km/h gusting to 90; ~50,000 evacuated in Odisha.",
     "IMD \u00b7 20 NOV"),
    (35, scene_cop31, "COP31 enters its final day with no deal \u2014 and no fossil fuels in the draft",
     "Revised Antalya text drops coal, oil and gas and the $120bn adaptation figure.",
     "REUTERS \u00b7 20 NOV"),
]

VIGNETTES = [
    (2, "power", "Ukraine imposes emergency power cuts",
     "Ukrenergo cuts power in three regions; grid \u2018extremely critical\u2019.", "H.UA \u00b7 20 NOV"),
    (5, "border", "Estonia plans to close border with Russia",
     "Crossings to shut from December after an attack on a defence firm.", "MUNICH EYE"),
    (8, "tower", "Houthi missile damages Riyadh's PIF Tower",
     "Facade of Riyadh's tallest building damaged across several floors.", "TIMES OF ISRAEL / AFP"),
    (16, "scales", "ICJ rules Myanmar guilty of Rohingya genocide",
     "UN top court finds genocide; lead story on front pages worldwide.", "LE MONDE \u00b7 20 NOV"),
    (18, "chart_down", "Asian markets plunge on AI bubble fears",
     "Steep Friday losses across Asia despite Anthropic's historic IPO.", "NEWS MEDIA HOUSE"),
    (23, "mine", "Drone strike kills 10 at Sudan gold mine",
     "Strike on a mine in South Kordofan kills ten.", "ONE TURN BRIEF"),
    (28, "runner", "Kenya's Jepchirchir banned three years for EPO",
     "Marathon champion handed a three-year doping ban.", "NB NEWS WRAP"),
    (33, "court", "Florida pastor convicted over Mo\u00efse assassination",
     "Convicted in the US over the assassination of Haiti's president.", "LE MONDE \u00b7 20 NOV"),
    (39, "chart_up", "Anthropic closes up 17% on debut",
     "ANT closes $97.17 vs $83 IPO after the record $81.3bn IPO.", "MARKET WRAP"),
    (43, "vangogh", "Van Gogh sells for $190.4 million \u2014 record",
     "Late Van Gogh tops $190m at auction.", "MUNICH EYE"),
]

BRIEFS = [
    (3, "Kharkiv hospital hit, four injured"),
    (4, "Massive drone attack hits Kryvyi Rih"),
    (6, "UK PM Burnham reopens the EU question"),
    (7, "General strike disrupts Spain"),
    (9, "Saudi coalition intercepts Houthi missile"),
    (10, "Saudi airstrikes hit Sanaa on Friday"),
    (11, "Iraqi forces deploy to Jurf al-Sakhr"),
    (12, "Trump \u2018not rushing\u2019 on Iran; war powers rejected"),
    (13, "Mossad chief urges multi-day Iran air campaign"),
    (14, "Hormuz threat stays \u2018severe\u2019"),
    (17, "N. Korea launches missile into Sea of Japan"),
    (19, "Shenzhen declaration omits Ukraine, Iran, Taiwan"),
    (20, "White House: bag phones on China return flight"),
    (21, "India's PM pulls up industry over imports"),
    (22, "Australia: drop religion from terror definition"),
    (24, "Senegal boat capsizing kills four"),
    (25, "Malawi fuel crisis triggers violence"),
    (26, "Africa demands tripled climate finance"),
    (27, "South Africa holds repo rate at 7.25%"),
    (29, "Bukele to register for third term"),
    (30, "Lula visits ailing Chief Raoni"),
    (31, "S&P 500 falls for sixth straight session"),
    (32, "Chicago man pleads not guilty in temple plot"),
    (34, "Kushner: Trump open to Article 5-style guarantee"),
    (36, "COP31 keeps 35\u00d735 electrification goal"),
    (37, "WMO: 136 nations run early-warning systems"),
    (38, "589M children lived in war zones in 2025 \u2014 record"),
    (40, "GTA VI day-one sales put at 24.6M copies"),
    (41, "Google books Blue Origin's New Glenn for 2029"),
    (42, "Moonshot AI scraps $150M Nvidia B300 deal"),
    (44, "EU hit by AI-assisted hack"),
]

# Simplified continent outlines (lon, lat) — stylised strip-map shapes.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 74), (-75, 72),
     (-70, 62), (-75, 45), (-80, 32), (-85, 30), (-90, 21), (-95, 19), (-100, 23),
     (-105, 20), (-110, 23), (-115, 30), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76), (-50, 74), (-58, 64)],
    [(-80, 10), (-75, 5), (-80, -5), (-85, -15), (-80, -25), (-70, -35), (-65, -45),
     (-60, -55), (-55, -35), (-45, -25), (-40, -15), (-35, -5), (-45, 0), (-55, 5),
     (-65, 10), (-75, 12)],
    [(-10, 36), (-5, 44), (0, 48), (5, 55), (10, 58), (15, 60), (20, 65), (25, 70),
     (30, 70), (35, 65), (40, 60), (35, 55), (30, 50), (25, 45), (20, 40),
     (15, 38), (10, 37), (5, 36), (0, 36)],
    [(-10, 35), (-5, 30), (0, 32), (10, 35), (15, 32), (20, 30), (30, 31), (35, 28),
     (40, 20), (45, 12), (50, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (25, -35), (20, -35), (15, -30), (12, -18), (10, -5), (5, 5), (0, 10),
     (-5, 15), (-10, 25)],
    [(35, 70), (45, 72), (60, 73), (75, 73), (90, 75), (110, 76), (130, 72),
     (150, 70), (160, 65), (170, 66), (175, 60), (160, 55), (150, 50), (140, 45),
     (130, 42), (125, 38), (120, 35), (115, 30), (110, 25), (105, 20), (100, 15),
     (95, 10), (90, 15), (85, 20), (80, 15), (75, 10), (70, 20), (65, 25),
     (60, 25), (55, 25), (50, 28), (45, 30), (40, 35), (35, 38)],
    [(115, -20), (120, -15), (125, -12), (130, -10), (135, -12), (140, -15),
     (145, -18), (150, -22), (150, -30), (145, -35), (140, -38), (135, -35),
     (130, -32), (125, -32), (120, -30), (115, -25)],
]

PINS = [
    # (lon, lat, number, label, pin offset dx, dy) — offsets spread the
    # Europe / Middle East cluster with leader lines so pins never overlap.
    (30.5, 50.5, 1, "Kyiv", 0, -12), (36.2, 49.9, 3, None, 18, -8),
    (46.7, 24.6, 8, "Riyadh", 16, 6), (44.2, 15.3, 10, None, -4, 18),
    (85.0, 19.3, 15, "Odisha", 0, -12), (130, 39, 17, None, 0, 0),
    (30.7, 36.9, 35, "Antalya", -2, 14), (29, 11, 23, None, 0, 0),
    (-89, 13.7, 29, None, 0, 0), (-52, -10, 30, None, 0, 0),
]


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    X0, X1 = 28, 996
    CW = X1 - X0
    y = 10

    # Kicker + corner notes
    f_kick = F(SANS_B, 14)
    f_tiny = F(SANS, 9)
    d.text((X0, y), "No. 44 \u2014 44 STORIES", font=f_tiny, fill=GREY)
    rt = "FRIDAY EDITION"
    d.text((X1 - d.textlength(rt, font=f_tiny), y), rt, font=f_tiny, fill=GREY)
    kick = "T H E   W O R L D   I N   O N E   P A G E"
    text_c(d, W // 2, y - 2, kick, f_kick, RED)
    y += 22

    # Serif masthead: the date
    f_mast = F(SERIF_B, 50)
    text_c(d, W // 2, y, "Friday 20 November 2026", f_mast, INK)
    y += 60
    rule(d, X0, X1, y, width=3)
    rule(d, X0, X1, y + 5, width=1)
    y += 12

    # Stat strip — 6 big numbers directly under the masthead
    col_w = CW / 6
    f_num = F(SERIF_B, 26)
    f_lab = F(SANS, 10)
    for i, (num, lab) in enumerate(STATS):
        cx = X0 + col_w * i + col_w / 2
        if i:
            d.line([(X0 + col_w * i, y + 4), (X0 + col_w * i, y + 50)], fill=LIGHT_GREY, width=1)
        text_c(d, cx, y, num, f_num, INK)
        for j, ln in enumerate(wrap(d, lab, f_lab, col_w - 14)):
            text_c(d, cx, y + 32 + j * 12, ln, f_lab, GREY)
    y += 54

    # Region chips
    chip_w = (CW - 5 * 6) / 6
    f_chip = F(SANS_B, 12)
    for i, (name, col) in enumerate(REGIONS):
        cx0 = X0 + i * (chip_w + 6)
        d.rounded_rectangle([cx0, y, cx0 + chip_w, y + 24], radius=12, fill=col)
        text_c(d, cx0 + chip_w / 2, y + 5, name, f_chip, (255, 255, 255))
    y += 30

    # UTC timeline strip
    rule(d, X0, X1, y, width=1, fill=LIGHT_GREY)
    f_utc_l = F(SANS_B, 11)
    f_utc = F(SANS, 10)
    lab = "THE DAY IN UTC"
    d.text((X0, y + 5), lab, font=f_utc_l, fill=RED)
    slot_w = (CW - d.textlength(lab, font=f_utc_l) - 24) / 6
    for i, (t, ev) in enumerate(UTC_ITEMS):
        cx = X0 + d.textlength(lab, font=f_utc_l) + 24 + slot_w * i + slot_w / 2
        s = f"{t}  {ev}"
        w = d.textlength(s, font=f_utc)
        d.text((cx - w / 2, y + 5), s, font=f_utc, fill=INK)
    y += 24
    rule(d, X0, X1, y, width=1, fill=LIGHT_GREY)
    y += 8

    # Heroes — 3 large literal scenes
    hw = (CW - 2 * 8) / 3
    f_h_head = F(SERIF_B, 15)
    f_h_sum = F(SANS, 10)
    f_src = F(SANS, 9)
    hero_y = y
    for i, (num, fn, head, summ, src) in enumerate(HEROES):
        hx = X0 + i * (hw + 8)
        fn(d, int(hx), hero_y, int(hw), 160)
        badge(d, int(hx) + 16, hero_y + 16, num)
        ty = hero_y + 166
        for ln in wrap(d, head, f_h_head, hw):
            d.text((hx, ty), ln, font=f_h_head, fill=INK)
            ty += 18
        for ln in wrap(d, summ, f_h_sum, hw):
            d.text((hx, ty), ln, font=f_h_sum, fill=(60, 60, 58))
            ty += 13
        d.text((hx, ty + 2), src, font=f_src, fill=GREY)
    y = hero_y + 160 + 82

    # Vignettes — two rows of 5, headline + 2-line summary + source tag
    vw = (CW - 4 * 8) / 5
    f_v_head = F(SANS_B, 11)
    f_v_sum = F(SANS, 9)
    f_v_src = F(SANS, 8)
    row_h = 108
    for r in range(2):
        vy = y + r * (row_h + 6)
        for c in range(5):
            num, kind, head, summ, src = VIGNETTES[r * 5 + c]
            vx = X0 + c * (vw + 8)
            mini(d, int(vx), vy, int(vw), 46, kind)
            badge(d, int(vx) + 14, vy + 14, num, r=10)
            ty = vy + 50
            for ln in wrap(d, head, f_v_head, vw):
                d.text((vx, ty), ln, font=f_v_head, fill=INK)
                ty += 13
            for ln in wrap(d, summ, f_v_sum, vw):
                d.text((vx, ty), ln, font=f_v_sum, fill=(60, 60, 58))
                ty += 11
            d.text((vx, ty + 1), src, font=f_v_src, fill=GREY)
    y = y + 2 * row_h + 6

    # Numbered briefs — the remaining 31 stories, 3 columns
    f_b_head = F(SANS_B, 11)
    f_b = F(SANS, 10)
    f_b_num = F(SANS_B, 10)
    d.text((X0, y), "BRIEFS \u2014 THE REST OF THE DAY'S 44 STORIES", font=f_b_head, fill=INK)
    rule(d, X0, X1, y + 15, width=1, fill=LIGHT_GREY)
    by = y + 20
    bw = CW / 3
    for i, (num, head) in enumerate(BRIEFS):
        col, row = i % 3, i // 3
        bx = X0 + col * bw
        byy = by + row * 10.5
        d.text((bx, byy), f"{num}.", font=f_b_num, fill=RED)
        d.text((bx + 24, byy), head, font=f_b, fill=INK)
    y = by + 11 * 10.5 + 6

    # World map at the bottom — WHERE IT HAPPENED, numbered pins
    f_m_head = F(SANS_B, 12)
    d.text((X0, y), "WHERE IT HAPPENED", font=f_m_head, fill=INK)
    rule(d, X0, X1, y + 16, width=1, fill=LIGHT_GREY)
    my0, my1 = y + 20, H - 88
    d.rectangle([X0, my0, X1, my1], fill=OCEAN)
    d.rectangle([X0, my0, X1, my1], outline=LAND_LINE, width=1)

    def proj(lon, lat):
        px = X0 + (lon + 170) / 360 * CW
        py = my0 + (75 - lat) / 130 * (my1 - my0)
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND, outline=LAND_LINE)
    f_pin = F(SANS_B, 9)
    f_lab = F(SANS_B, 8)
    for lon, lat, num, label, dx, dy in PINS:
        px, py = proj(lon, lat)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (qx, qy)], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([qx - 8, qy - 8, qx + 8, qy + 8], fill=RED, outline=(255, 255, 255), width=2)
        t = str(num)
        tw = d.textlength(t, font=f_pin)
        d.text((qx - tw / 2, qy - 6), t, font=f_pin, fill=(255, 255, 255))
        if label:
            lx = 12 if qx < X1 - 90 else -62
            d.text((qx + lx, qy - 5), label, font=f_lab, fill=INK)
    y = my1 + 6

    # Date-check footer
    rule(d, X0, X1, y, width=2)
    y += 6
    f_f_head = F(SANS_B, 11)
    f_f = F(SANS, 9)
    d.text((X0, y), "DATE CHECK \u2014 WHAT WE LEFT OUT ON PURPOSE", font=f_f_head, fill=RED)
    y += 15
    foot = [
        "Not 20 Nov news, so not here: the Shenzhen Trump\u2013Xi\u2013Putin summit itself (19 Nov); "
        "the first Gulf missile strikes (19 Nov); the Kerch Bridge span falling (19 Nov); "
        "Anthropic IPO pricing (18 Nov); Taiwan's 4.6% plunge (18 Nov).",
        "The ICJ Myanmar ruling was delivered 19 Nov but leads today's front pages \u2014 "
        "reported here as #16. All 44 stories sourced and dated Friday 20 November 2026.",
        "Sources: CNN \u00b7 Reuters \u00b7 AFP \u00b7 Le Monde \u00b7 ISW \u00b7 WMO \u00b7 IMD and others "
        "\u2014 Confidence: Officials say / Reported / Ongoing / Estimate",
    ]
    for para in foot:
        for ln in wrap(d, para, f_f, CW):
            d.text((X0, y), ln, font=f_f, fill=(60, 60, 58))
            y += 11
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = render()
    img.save(out, format="PNG")
    data = open(out, "rb").read()
    print(f"entry.png {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    print(f"size {img.size}")


if __name__ == "__main__":
    main()

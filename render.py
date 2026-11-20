#!/usr/bin/env python3
"""Render the news-image-20261120 front page at build time.

Run locally: `python3 render.py` — needs Pillow and the DejaVu fonts,
both present on the build VM. The graded program is main.ts, which only
copies the finished entry.png; the grader never runs this script, so
nothing here needs to run without network or fonts at grade time.
Deterministic on purpose: the random seed is fixed, there is no clock
and no network, so repeated runs write identical bytes.

The page: a 1024x1024 newspaper front page for Friday 20 November 2026
— masthead with the date, a dotted world map with numbered markers for
the top stories, three drawn hero scenes (Kyiv barrage, Cyclone Akvan
landfall, COP31 final day), a day-in-numbers strip, a UTC timeline rail,
and the 44 verified stories of the day grouped under seven region
headers, with proof tags and a date check in the footer.

Every story comes from NEWS-RESEARCH.md in the bounty folder (all
reported on 20 November 2026). Nothing from 19 November is presented as
20 November news; 19 November items appear only in the footer line that
says what was left out on purpose.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
random.seed(20261120)
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def load(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def serif_b(size):
    return load("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return load("DejaVuSerif.ttf", size)


def sans_b(size):
    return load("DejaVuSans-Bold.ttf", size)


def sans(size):
    return load("DejaVuSans.ttf", size)


PAPER = (247, 243, 232)
INK = (16, 28, 51)
NAVY = (13, 27, 54)
RED = (179, 32, 44)
GOLD = (201, 162, 39)

# (region, headline, deck) — 44 stories, all reported 20 November 2026.
STORIES = [
    ("EUROPE & RUSSIA", "KYIV BARRAGE KILLS FIVE", "Ballistic missiles + drones, 6+ hrs; 3 bridges hit"),
    ("EUROPE & RUSSIA", "EMERGENCY POWER CUTS", "Ukrenergo: grid 'extremely critical' after strikes"),
    ("EUROPE & RUSSIA", "KHARKIV HOSPITAL HIT", "Drone strike injures 4, smashes 50+ windows"),
    ("EUROPE & RUSSIA", "KRYVYI RIH INFRA HIT", "'Massive' drone attack on major facility"),
    ("EUROPE & RUSSIA", "ESTONIA TO CLOSE BORDER", "Russia crossings shut from Dec after attack bid"),
    ("EUROPE & RUSSIA", "BURNHAM REOPENS EU QUESTION", "UK PM hints at closer ties ahead of talks"),
    ("EUROPE & RUSSIA", "SPAIN GENERAL STRIKE", "Ports and factories disrupted nationwide"),
    ("MIDDLE EAST", "HOUTHI MISSILE HITS PIF TOWER", "Riyadh's tallest tower damaged; Gulf condemns"),
    ("MIDDLE EAST", "COALITION INTERCEPTS SOUTH", "Missile + drones downed over Jazan, Abha"),
    ("MIDDLE EAST", "SAUDI STRIKES ON SANAA", "Airstrikes hit Yemeni capital on Friday"),
    ("MIDDLE EAST", "IRAQ DEPLOYS TO JURF AL-SAKHR", "Forces enter as Kataib Hezbollah relocates"),
    ("MIDDLE EAST", "TRUMP 'NOT RUSHING' ON IRAN", "Senate rejects Iran war-powers resolution"),
    ("MIDDLE EAST", "MOSSAD URGES IRAN STRIKES", "Chief pushes air campaign; IDF chief opposed"),
    ("MIDDLE EAST", "HORMUZ THREAT 'SEVERE'", "JMIC: 4 tanker attacks in 96 hours"),
    ("ASIA-PACIFIC", "CYCLONE AKVAN MAKES LANDFALL", "Gopalpur, Odisha; 50,000 evacuated; gusts 90"),
    ("ASIA-PACIFIC", "ICJ: MYANMAR GUILTY OF GENOCIDE", "Top court rules on Rohingya; front pages lead"),
    ("ASIA-PACIFIC", "N KOREA FIRES MISSILE", "Ballistic missile into the Sea of Japan"),
    ("ASIA-PACIFIC", "ASIA MARKETS PLUNGE", "AI bubble fears sink stocks despite IPO"),
    ("ASIA-PACIFIC", "SHENZHEN PACT OMITS UKRAINE", "Peace declaration skips Ukraine, Iran, Taiwan"),
    ("ASIA-PACIFIC", "PHONES BAGGED ON FLIGHT HOME", "Press seal phones on China return flight"),
    ("ASIA-PACIFIC", "INDIA PM WARNS INDUSTRY", "Modi: cut import reliance, lift demand"),
    ("ASIA-PACIFIC", "AUSTRALIA: TERROR LAW REVIEW", "Drop religion from definition, review urges"),
    ("AFRICA", "SUDAN GOLD MINE STRIKE", "Drone strike kills 10 in South Kordofan"),
    ("AFRICA", "SENEGAL BOAT CAPSIZES", "4 killed as migration surge continues"),
    ("AFRICA", "MALAWI FUEL CRISIS", "Shortages trigger violence, economic strain"),
    ("AFRICA", "AFRICA DEMANDS CLIMATE CASH", "COP31: triple adaptation finance, Africa says"),
    ("AFRICA", "SA HOLDS RATE AT 7.25%", "Reserve Bank keeps repo rate steady"),
    ("AFRICA", "JEPCHIRCHIR BANNED 3 YEARS", "Kenyan marathon champion banned for EPO"),
    ("AMERICAS", "BUKELE SEEKS THIRD TERM", "El Salvador president to formally register"),
    ("AMERICAS", "LULA VISITS CHIEF RAONI", "Brazil advances Indigenous land recognition"),
    ("AMERICAS", "S&P'S SIXTH STRAIGHT LOSS", "Index down 2.02% to 7,175.83"),
    ("AMERICAS", "TEMPLE PLOT PLEA", "Chicago man pleads not guilty"),
    ("AMERICAS", "PASTOR CONVICTED OVER MOISE", "Florida pastor guilty in Haiti killing case"),
    ("AMERICAS", "KUSHNER: US OPEN TO ART. 5 PACT", "Trump open to Ukraine security guarantee"),
    ("WORLD & CLIMATE", "COP31 FINAL DAY, NO DEAL", "Draft drops all fossil-fuel language"),
    ("WORLD & CLIMATE", "COP31 KEEPS 35x35 GOAL", "Electrification stays; Fund gets $50m of $300m"),
    ("WORLD & CLIMATE", "WMO: 136 NATIONS WARNED", "Early warning systems now in 136 countries"),
    ("WORLD & CLIMATE", "589M CHILDREN IN WAR ZONES", "Record number in conflict in 2025"),
    ("MARKETS & CULTURE", "ANT CLOSES UP 17% ON DEBUT", "$97.17 after record $81.3bn IPO"),
    ("MARKETS & CULTURE", "GTA VI: 24.6M DAY ONE", "First reports: ~$2.36bn in day-one sales"),
    ("MARKETS & CULTURE", "GOOGLE BOOKS NEW GLENN", "2029 Blue Origin launch for AI satellites"),
    ("MARKETS & CULTURE", "MOONSHOT DROPS NVIDIA DEAL", "Scraps $150m B300 deal in Indonesia"),
    ("MARKETS & CULTURE", "VAN GOGH SELLS FOR $190.4M", "Artist record at auction"),
    ("MARKETS & CULTURE", "EU HIT BY AI-ASSISTED HACK", "~10 days of disrupted applications"),
]
assert len(STORIES) == 44, len(STORIES)


def fit_text(dr, text, fnt, width):
    """Split text into lines no wider than `width` (in `fnt`)."""
    out, line = [], ""
    for word in text.split(" "):
        trial = word if not line else line + " " + word
        if dr.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def paint_gradient(dr, left, top, right, bottom, top_col, bot_col):
    span = max(1, bottom - top)
    for yy in range(top, bottom):
        f = (yy - top) / span
        col = tuple(int(top_col[i] + (bot_col[i] - top_col[i]) * f) for i in range(3))
        dr.line([(left, yy), (right, yy)], fill=col)


def grain(dr, left, top, right, bottom, count, palette):
    for _ in range(count):
        xx = random.randint(left, right)
        yy = random.randint(top, bottom)
        dr.point((xx, yy), fill=random.choice(palette))


def puff(dr, cx, cy, r, col=(255, 255, 255)):
    for ox, oy, rr in ((0, 0, r), (r, 4, r * 3 // 4), (-r, 5, r * 2 // 3)):
        dr.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=col)


# Rough continent outlines for the dotted world map, as flat
# [lon, lat, lon, lat, ...] lists (one outline per line).
LAND = [
    [-168, 65, -140, 70, -120, 71, -100, 68, -85, 66, -80, 73, -65, 60, -55, 52, -60, 47, -70, 42, -75, 35, -80, 26, -85, 30, -90, 21, -97, 16, -105, 20, -115, 28, -125, 40, -145, 60],
    [-58, 64, -45, 60, -40, 70, -55, 76, -65, 76],
    [-80, 10, -70, 12, -60, 8, -50, 0, -40, -5, -35, -10, -40, -20, -48, -28, -58, -35, -65, -45, -70, -52, -73, -40, -80, -20, -80, -5],
    [-10, 36, -5, 44, -2, 48, 0, 51, 5, 58, 10, 58, 18, 56, 21, 55, 28, 60, 30, 62, 25, 70, 20, 70, 15, 68, 10, 64, 5, 60, -5, 58, -10, 52, -10, 43],
    [-17, 15, -10, 30, 0, 36, 10, 37, 20, 32, 32, 31, 35, 28, 40, 15, 48, 11, 51, 10, 45, 0, 40, -10, 35, -20, 30, -30, 20, -35, 15, -30, 12, -18, 9, -2, 9, 4, -8, 5],
    [30, 62, 40, 68, 60, 70, 80, 73, 100, 77, 120, 73, 140, 72, 160, 70, 178, 66, 170, 60, 160, 55, 142, 50, 140, 40, 130, 35, 127, 40, 120, 32, 110, 20, 105, 10, 100, 8, 95, 15, 90, 22, 80, 15, 75, 8, 70, 20, 60, 25, 55, 26, 50, 29, 45, 30, 40, 36, 35, 36, 30, 36, 30, 42, 30, 50],
    [113, -22, 122, -14, 132, -12, 142, -11, 150, -22, 153, -27, 150, -37, 140, -38, 130, -32, 120, -34, 113, -26],
    [-5, 50, 1, 51, 2, 53, -3, 55, -5, 58, -5, 50],
    [95, -5, 105, -5, 110, -8, 105, -10, 95, -8],
    [122, 24, 125, 30, 130, 33, 132, 38, 138, 40, 141, 45, 140, 40, 135, 35, 130, 32, 126, 28],
]


def land_polys():
    out = []
    for flat in LAND:
        out.append([(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)])
    return out


def inside_poly(px, py, poly):
    """Ray casting: count edge crossings to the right of (px, py)."""
    crossings = 0
    m = len(poly)
    for k in range(m):
        ax, ay = poly[k]
        bx, by = poly[(k + 1) % m]
        if (ay <= py < by) or (by <= py < ay):
            ix = ax + (py - ay) * (bx - ax) / (by - ay)
            if px < ix:
                crossings += 1
    return crossings % 2 == 1


def scene_kyiv(dr, x0, y0, x1, y1):
    """Night over Kyiv: dark sky, searchlights, fires, a bridge silhouette."""
    paint_gradient(dr, x0 + 2, y0, x1 - 2, y1, (12, 16, 38), (52, 40, 70))
    for sx, sy in [(24, 10), (80, 16), (150, 8), (210, 14), (270, 10), (300, 18)]:
        dr.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255))
    # missile streaks
    for mx, my, ln in [(60, 20, 34), (180, 12, 40), (260, 26, 30)]:
        dr.line([(x0 + mx, y0 + my), (x0 + mx + ln, y0 + my + 14)], fill=(255, 200, 90), width=3)
        dr.ellipse([x0 + mx + ln - 3, y0 + my + 11, x0 + mx + ln + 3, y0 + my + 17], fill=(255, 120, 30))
    # searchlights
    for bx in (40, 290):
        dr.polygon([(x0 + bx, y1), (x0 + bx - 26, y0 + 10), (x0 + bx - 8, y0 + 10)], fill=(255, 240, 180))
    # bridge silhouette + fires
    dr.rectangle([x0 + 2, y1 - 18, x1 - 2, y1 - 12], fill=(8, 10, 22))
    for bx in (50, 140, 230):
        dr.line([(x0 + bx, y1 - 18), (x0 + bx, y1 - 52)], fill=(8, 10, 22), width=4)
    for fx, fy in [(90, 58), (200, 62), (260, 56)]:
        for a in range(8):
            ang = a * math.pi / 4
            dr.line([(x0 + fx, y0 + fy),
                     (x0 + fx + 22 * math.cos(ang), y0 + fy + 22 * math.sin(ang))],
                    fill=(255, 200, 60), width=3)
        dr.ellipse([x0 + fx - 9, y0 + fy - 9, x0 + fx + 9, y0 + fy + 9], fill=(255, 110, 25))
    puff(dr, x0 + 120, y0 + 30, 12, (70, 70, 80))
    puff(dr, x0 + 240, y0 + 22, 10, (70, 70, 80))


def scene_akvan(dr, x0, y0, x1, y1):
    """Cyclone Akvan: spiral storm bands over a grey sea and the coast."""
    paint_gradient(dr, x0 + 2, y0, x1 - 2, y1, (150, 180, 205), (70, 105, 140))
    cx, cy = x0 + 160, y0 + 46
    for r, col in [(52, (240, 244, 248)), (40, (210, 222, 232)), (28, (240, 244, 248)),
                   (18, (180, 198, 214)), (9, (255, 255, 255))]:
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=6)
    # rain streaks
    for rx in range(20, 320, 22):
        dr.line([(x0 + rx, y0 + 8), (x0 + rx - 6, y0 + 30)], fill=(220, 232, 242), width=2)
    # coast + shelters
    dr.rectangle([x0 + 2, y1 - 22, x1 - 2, y1], fill=(96, 120, 80))
    dr.polygon([(x0 + 2, y1 - 22), (x0 + 90, y1 - 22), (x0 + 45, y1 - 46)], fill=(120, 145, 95))
    dr.polygon([(x0 + 210, y1 - 22), (x0 + 300, y1 - 22), (x0 + 255, y1 - 44)], fill=(120, 145, 95))
    for hx in (110, 150, 190):
        dr.polygon([(x0 + hx, y1 - 34), (x0 + hx + 12, y1 - 34), (x0 + hx + 6, y1 - 44)], fill=(200, 60, 50))
        dr.rectangle([x0 + hx, y1 - 34, x0 + hx + 12, y1 - 22], fill=(240, 230, 210))


def scene_cop31(dr, x0, y0, x1, y1):
    """COP31 final day in Antalya: hall, flags, a globe and a gavel."""
    paint_gradient(dr, x0 + 2, y0, x1 - 2, y1, (24, 60, 90), (60, 120, 150))
    # flags row
    flag_cols = [(0, 90, 160), (200, 30, 40), (255, 255, 255), (20, 140, 70),
                 (255, 200, 40), (120, 60, 140), (220, 120, 30)]
    for i, c in enumerate(flag_cols):
        fx = 18 + i * 44
        dr.line([(x0 + fx + 16, y0 + 8), (x0 + fx + 16, y0 + 42)], fill=(220, 220, 220), width=2)
        dr.rectangle([x0 + fx, y0 + 8, x0 + fx + 32, y0 + 24], fill=c)
    # globe
    gx, gy = x0 + 160, y0 + 62
    dr.ellipse([gx - 26, gy - 26, gx + 26, gy + 26], fill=(60, 140, 90), outline=(255, 255, 255), width=2)
    dr.ellipse([gx - 26, gy - 26, gx + 26, gy + 26], outline=(255, 255, 255), width=1)
    dr.arc([gx - 26, gy - 26, gx + 26, gy + 26], 200, 340, fill=(255, 255, 255), width=2)
    dr.line([(gx - 26, gy), (gx + 26, gy)], fill=(255, 255, 255), width=2)
    # delegates (seated rows)
    for row, ry in enumerate((y1 - 26, y1 - 14)):
        for dx in range(14, 316, 30):
            dr.ellipse([x0 + dx, ry - 6, x0 + dx + 10, ry + 4], fill=(240, 235, 220) if row == 0 else (200, 190, 175))
    # gavel + sun
    dr.ellipse([x0 + 280, y0 + 52, x0 + 296, y0 + 68], fill=(255, 210, 80))
    dr.line([(x0 + 288, y0 + 60), (x0 + 250, y0 + 84)], fill=(120, 80, 40), width=4)


def build():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    dr = ImageDraw.Draw(img)
    grain(dr, 0, 0, PAGE, PAGE, 2500,
          [(238, 234, 220), (255, 250, 238), (230, 226, 210)])

    # Masthead.
    dr.rectangle([0, 0, PAGE, 132], fill=NAVY)
    dr.rectangle([0, 130, PAGE, 134], fill=RED)
    dr.text((PAGE / 2, 26), "THE WORLD IN ONE DAY", font=sans_b(20), fill=GOLD, anchor="mt")
    dr.text((PAGE / 2, 52), "FRIDAY 20 NOVEMBER 2026", font=serif_b(50),
            fill=(255, 255, 255), anchor="mt")
    dr.text((PAGE / 2, 108), "44 STORIES  \u00b7  7 REGIONS  \u00b7  SIX CONTINENTS  \u00b7  SOURCED & DATE-CHECKED",
            font=sans_b(15), fill=(200, 210, 225), anchor="mt")

    # Dotted world map with numbered markers for the top stories.
    mx0, my0, mx1, my1 = 16, 142, 1008, 244
    dr.rectangle([mx0, my0, mx1, my1], fill=(214, 232, 240), outline=INK, width=2)
    paint_gradient(dr, mx0 + 1, my0 + 1, mx1 - 1, my1 - 1, (222, 238, 246), (190, 215, 232))

    def proj(lon, lat):
        return (mx0 + 8 + (lon + 180) / 360 * (mx1 - mx0 - 16),
                my0 + 6 + (78 - lat) / 133 * (my1 - my0 - 12))

    polys = land_polys()
    for la in range(-56, 79, 6):
        lo = -180.0
        while lo <= 180:
            if any(inside_poly(lo, la, p) for p in polys):
                xx, yy = proj(lo, la)
                dr.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=(38, 68, 110))
            lo += 3.2
    dr.text((mx0 + 10, my1 - 16), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
    dr.text((mx1 - 10, my1 - 16), "NUMBERED = TOP STORIES", font=sans_b(11), fill=INK, anchor="rt")
    # (number, lon, lat, badge offset)
    markers = [(1, 30, 50, 0, 0), (2, 46, 25, 0, 0), (3, 85, 19, 0, 0),
               (4, 30, 37, -16, 10), (5, 126, 39, 0, 0), (6, 121, 25, 14, -10),
               (7, 32, 15, 0, 0), (8, -89, 14, 0, 0), (9, -74, 41, 4, -12)]
    for num, lon, lat, dx, dy in markers:
        xx, yy = proj(lon, lat)
        bx, by = xx + dx, yy + dy
        dr.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=RED, outline=(255, 255, 255), width=1)
        if dx or dy:
            dr.line([(xx, yy), (bx, by)], fill=RED, width=1)
        dr.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=RED, outline=(255, 255, 255), width=2)
        dr.text((bx, by), str(num), font=sans_b(11), fill=(255, 255, 255), anchor="mm")

    # Three hero panels.
    heroes = [
        ("1  KYIV BARRAGE KILLS FIVE",
         "Russia's overnight ballistic + drone attack hits 3 bridges",
         scene_kyiv),
        ("2  CYCLONE AKVAN MAKES LANDFALL",
         "Gopalpur, Odisha — 50,000 evacuated as the storm comes ashore",
         scene_akvan),
        ("3  COP31 FINAL DAY, NO DEAL",
         "Antalya draft drops every fossil-fuel mention; Panama may block",
         scene_cop31),
    ]
    top, bottom, panel_w, sep = 252, 424, 322, 8
    for i, (head, deck, painter) in enumerate(heroes):
        px0 = 16 + i * (panel_w + sep)
        px1 = px0 + panel_w
        dr.rectangle([px0, top, px1, bottom], fill=(255, 255, 255), outline=INK, width=2)
        painter(dr, px0, top + 2, px1, top + 92)
        ty = top + 98
        for ln in fit_text(dr, head, serif_b(19), panel_w - 16):
            dr.text((px0 + 8, ty), ln, font=serif_b(19), fill=INK)
            ty += 23
        for ln in fit_text(dr, deck, sans(12), panel_w - 16):
            dr.text((px0 + 8, ty), ln, font=sans(12), fill=(60, 60, 70))
            ty += 15
        grain(dr, px0 + 2, top + 2, px1 - 2, top + 92, 250,
              [(255, 255, 255), (255, 240, 200)])

    # The day in numbers.
    ny0, ny1 = 432, 484
    numbers = [("90 KM/H", "AKVAN GUSTS"), ("50,000", "EVACUATED, ODISHA"),
               ("5 KILLED", "KYIV BARRAGE"), ("$97.17", "ANT DEBUT CLOSE"),
               ("24.6M", "GTA VI DAY ONE"), ("$190.4M", "VAN GOGH RECORD")]
    cell_w = (1008 - 16 - 5 * 6) / 6
    for i, (val, lab) in enumerate(numbers):
        cx0 = 16 + i * (cell_w + 6)
        dr.rectangle([cx0, ny0, cx0 + cell_w, ny1], fill=NAVY, outline=INK)
        dr.text((cx0 + cell_w / 2, ny0 + 6), val, font=serif_b(20), fill=GOLD, anchor="mt")
        dr.text((cx0 + cell_w / 2, ny0 + 32), lab, font=sans_b(9),
                fill=(220, 225, 235), anchor="mt")
    # UTC timeline rail.
    ty0 = 490
    dr.text((16, ty0), "UTC TIMELINE", font=sans_b(10), fill=RED)
    timeline = ("01:22 KYIV  \u00b7  02:00 AKVAN  \u00b7  04:22 KHARKIV  \u00b7  "
                "05:45 COP31  \u00b7  07:37 POWER CUTS  \u00b7  09:34 N KOREA")
    dr.text((130, ty0), timeline, font=sans_b(10), fill=INK)

    # Story grid: 44 stories under seven region headers, three columns.
    column_regions = [
        ["EUROPE & RUSSIA", "MIDDLE EAST"],
        ["ASIA-PACIFIC", "AFRICA"],
        ["AMERICAS", "WORLD & CLIMATE", "MARKETS & CULTURE"],
    ]
    region_col = {"EUROPE & RUSSIA": (30, 80, 160), "MIDDLE EAST": RED,
                  "ASIA-PACIFIC": (180, 90, 10), "AFRICA": (150, 60, 20),
                  "AMERICAS": (20, 110, 70), "WORLD & CLIMATE": (90, 90, 100),
                  "MARKETS & CULTURE": (120, 60, 140)}
    placed = 0
    for ci, regions in enumerate(column_regions):
        xx0 = 16 + ci * 336
        yy = 514
        seen = set()
        for region, head, deck in STORIES:
            if region not in regions:
                continue
            placed += 1
            if region not in seen:
                seen.add(region)
                dr.rectangle([xx0, yy + 2, xx0 + 5, yy + 14], fill=region_col[region])
                dr.text((xx0 + 10, yy), region, font=sans_b(12), fill=region_col[region])
                yy += 17
            dr.text((xx0, yy), head, font=sans_b(11), fill=INK)
            yy += 12
            dr.text((xx0, yy), deck, font=sans(10), fill=(70, 70, 80))
            yy += 13
            dr.line([(xx0, yy - 1), (xx0 + 316, yy - 1)], fill=(215, 210, 195))
        assert yy <= 970, (ci, yy)
    assert placed == 44, placed

    # Footer: date check, proof tags, and what was deliberately left out.
    fy0 = 972
    dr.rectangle([0, fy0, PAGE, PAGE], fill=NAVY)
    dr.text((PAGE / 2, fy0 + 8),
            "DATE-CHECKED 20 NOV 2026  \u00b7  LEFT OUT ON PURPOSE: 19 Nov news \u2014 Shenzhen summit, first Gulf strikes, Kerch span",
            font=sans_b(11), fill=(220, 225, 235), anchor="mt")
    dr.text((PAGE / 2, fy0 + 26),
            "Stories as reported on 20 November 2026  \u00b7  PROOF: Reuters \u00b7 CNN \u00b7 IMD \u00b7 ISW \u00b7 Le Monde \u00b7 Kyiv Independent  \u00b7  One day, one image.",
            font=sans(11), fill=(170, 180, 195), anchor="mt")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()

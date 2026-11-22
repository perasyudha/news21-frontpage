#!/usr/bin/env python3
"""Draw the 21 November 2026 front page: 1024x1024 PNG, deterministic, Pillow only.

Run:  python3 render.py            -> entry.png
The image is a one-day world-news front page: masthead, serif dateline, 11
illustrated cards in a 3+4+4 grid, a map with a seven-swatch region legend,
a two-column briefs rail carrying the running index to 35, and a footer that
states the attribution rule and the agencies.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 24
CONTENT = W - 2 * MARGIN  # 976

INK = (20, 22, 26)
PAPER = (246, 242, 233)
PAPER_ALT = (238, 232, 220)
RULE = (200, 192, 176)
MUTED = (94, 98, 104)
WHITE = (255, 255, 255)

REGIONS = {
    "AMERICAS": (176, 58, 58),
    "EUROPE": (40, 84, 148),
    "MIDDLE EAST": (206, 122, 40),
    "AFRICA": (54, 122, 72),
    "ASIA": (116, 72, 146),
    "OCEANIA": (32, 136, 136),
    "GLOBAL": (98, 102, 110),
}

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(text: str, f: ImageFont.FreeTypeFont, max_w: float) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if not lines:
            lines.append(word)
            continue
        trial = f"{lines[-1]} {word}"
        if f.getlength(trial) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


def block(draw, x, y, text, f, fill, max_w, line_h, max_lines, spacing=0):
    """Draw wrapped text and refuse silently-clipped copy."""
    lines = wrap(text, f, max_w)
    if len(lines) > max_lines:
        raise ValueError(f"copy overflows {max_lines} lines at {max_w}px: {text!r} -> {lines}")
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, font=f, fill=fill)
    return y + len(lines) * line_h + spacing


def tracked(draw, x, y, text, f, fill, tracking=1.2):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += f.getlength(ch) + tracking
    return cx - tracking


# ---------------------------------------------------------------- content ----

CARDS = [
    dict(n=1, region="EUROPE", field="CLIMATE", art="summit", lead=True,
         head="COP31 summit runs past its deadline",
         deck="Nearly 200 nations still talking in Antalya after Friday’s deadline; a $120bn adaptation target is gone",
         at=(30.7, 36.9)),
    dict(n=2, region="MIDDLE EAST", field="CONFLICT", art="plant",
         head="Iranian strike hits Bahrain plant",
         deck="No injuries; Bahrain hosts the US Fifth Fleet",
         at=(50.6, 26.2)),
    dict(n=3, region="EUROPE", field="WAR", art="strike",
         head="Missile strike kills two in Kryvyi Rih",
         deck="Two dead, 60 wounded; hospital and schools hit",
         at=(33.4, 47.9)),
    dict(n=4, region="AMERICAS", field="SECURITY", art="cuffs",
         head="Mexico seizes \u2018El Chapo Isidro\u2019; 11 die",
         deck="Eight arrested; 7 gunmen and 4 soldiers killed",
         at=(-108.2, 25.5)),
    dict(n=5, region="AMERICAS", field="POLITICS", art="hospital",
         head="Bolsonaro taken to intensive care",
         deck="Acute abdominal blockage; serving 27 years",
         at=(-47.9, -15.8)),
    dict(n=6, region="AFRICA", field="OBITUARY", art="candle",
         head="Mlambo-Ngcuka dies at 71",
         deck="First woman deputy president; UN Women 2013-21",
         at=(18.4, -33.9)),
    dict(n=7, region="MIDDLE EAST", field="HUMANITARIAN", art="aidvan",
         head="Aid van struck in Gaza, three killed",
         deck="Drone strike on a food-aid van in Tal al-Hawa",
         at=(34.5, 31.5)),
    dict(n=8, region="GLOBAL", field="SPACE", art="mercury",
         head="BepiColombo\u2019s twin craft reach Mercury",
         deck="Seven-year cruise ends; first visit in years",
         at=None),
    dict(n=9, region="EUROPE", field="BUDGET", art="budget",
         head="EU budget cuts divide Paris and Berlin",
         deck="\u20ac40bn cut plus a digital tax; France objects",
         at=(4.4, 50.8)),
    dict(n=10, region="GLOBAL", field="AI GOVERNANCE", art="robot",
         head="Killer-robot talks end with more talks",
         deck="Talks go to 2028; no firm commitment yet",
         at=(-74.0, 40.7)),
    dict(n=11, region="AMERICAS", field="TECHNOLOGY", art="servers",
         head="Trump threatens tax on AI centres abroad",
         deck="Overseas AI sites face \u201ca tremendous tax\u201d",
         at=(-77.0, 38.9)),
]

BRIEFS = [
    (12, "EUROPE", "Cargo ship hit by drones on fire off Finland"),
    (13, "MIDDLE EAST", "Qatari team in Tehran; Iran sees a chance"),
    (14, "MIDDLE EAST", "US denies Iran claim a missile hit an F-16"),
    (15, "MIDDLE EAST", "Basra power station fire kills 4, hurts 35"),
    (16, "AFRICA", "Curfew in Sennar as Blue Nile fighting spreads"),
    (17, "AFRICA", "Mali says four killed; air raids near Kidal"),
    (18, "AMERICAS", "Three Salvadoran soldiers die in Haiti"),
    (19, "AMERICAS", "Supercell storm batters southern Brazil town"),
    (20, "AMERICAS", "FBI probes hack of its crime database"),
    (21, "AMERICAS", "Second judge blocks Trump\u2019s memorial arch"),
    (22, "AMERICAS", "Agents arrest travellers at Seattle airport"),
    (23, "AMERICAS", "Mamdani plan puts Rikers closure at 2032"),
    (24, "AMERICAS", "Pentagon curbs on Canada target think tanks"),
    (25, "EUROPE", "Denmark urges EU travel curbs on Russians"),
    (26, "EUROPE", "Zagreb rally over psychiatric hospital death"),
    (27, "ASIA", "Kim tours factories after Trump leaves Asia"),
    (28, "ASIA", "Trump basks in summit pomp as Xi gains"),
    (29, "ASIA", "Russia warns on ISIS-K, offers mediation"),
    (30, "GLOBAL", "UN sets AI-safety summit in Barbados"),
    (31, "AMERICAS", "Senate Democrats test leadership vote"),
    (32, "OCEANIA", "Magnitude 6.8 quake shakes Banda Sea"),
    (33, "ASIA", "Indonesia ammonia project moves ahead"),
    (34, "AMERICAS", "Trump defends calling Putin a friend"),
    (35, "ASIA", "Protests at Meta offices in three India cities"),
]

TOTAL = len(CARDS) + len(BRIEFS)
assert (TOTAL, len(BRIEFS)) == (35, 24)


# ----------------------------------------------------------- illustrations ---

def art_summit(d, box, accent):
    x, y, w, h = box
    cx, cy, r = x + w * 0.26, y + h * 0.56, h * 0.32
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=accent, width=3)
    d.arc((cx - r, cy - r, cx + r, cy + r), 195, 345, fill=accent, width=3)
    for i in range(3):
        d.line((cx - r * 0.7, cy - r * 0.35 + i * 6, cx + r * 0.7, cy - r * 0.35 + i * 6),
               fill=accent, width=2)
    base = y + h - 8
    for i, (dx, ht) in enumerate([(0, 26), (14, 40), (28, 32)]):
        bx = x + w * 0.54 + dx
        d.rectangle((bx, base - ht, bx + 9, base), fill=INK)
    d.line((x + w * 0.50, base, x + w * 0.90, base), fill=INK, width=2)
    tx = x + w * 0.92
    d.rounded_rectangle((tx - 5, y + 8, tx + 5, base - 10), radius=5, outline=INK, width=2)
    d.ellipse((tx - 9, base - 20, tx + 9, base - 2), outline=INK, width=2)
    d.line((tx, y + 14, tx, base - 24), fill=accent, width=4)


def art_plant(d, box, accent):
    x, y, w, h = box
    d.rectangle((x + 8, y + h * 0.52, x + w * 0.52, y + h - 6), outline=INK, width=2)
    for i in range(3):
        d.rectangle((x + 14 + i * 26, y + h * 0.62, x + 32 + i * 26, y + h - 12), fill=accent)
    d.ellipse((x + w * 0.36, y + 10, x + w * 0.50, y + h * 0.40), outline=INK, width=2)
    d.line((x + w * 0.43, y + h * 0.40, x + w * 0.43, y + h * 0.52), fill=INK, width=2)
    fx = x + w * 0.66
    d.polygon([(fx, y + h - 8), (fx + 10, y + h * 0.52), (fx + 20, y + h - 8)], fill=accent)
    d.polygon([(fx + 8, y + h - 8), (fx + 16, y + h * 0.70), (fx + 24, y + h - 8)], fill=INK)
    d.line((x + w * 0.58, y + h - 8, x + w * 0.92, y + h - 8), fill=INK, width=2)


def art_strike(d, box, accent):
    x, y, w, h = box
    d.rectangle((x + 10, y + 18, x + w * 0.56, y + h - 6), outline=INK, width=2)
    for r in range(3):
        for c in range(4):
            if (r + c) % 3 == 1:
                d.rectangle((x + 18 + c * 20, y + 26 + r * 16, x + 32 + c * 20, y + 38 + r * 16),
                            fill=accent)
            else:
                d.rectangle((x + 18 + c * 20, y + 26 + r * 16, x + 32 + c * 20, y + 38 + r * 16),
                            outline=MUTED, width=1)
    d.line((x + w * 0.60, y + h - 6, x + w * 0.94, y + 12), fill=accent, width=4)
    d.polygon([(x + w * 0.94, y + 12), (x + w * 0.84, y + 16), (x + w * 0.90, y + 26)], fill=accent)


def art_cuffs(d, box, accent):
    x, y, w, h = box
    cy = y + h * 0.52
    d.arc((x + w * 0.16, cy - 26, x + w * 0.42, cy + 22), 20, 340, fill=INK, width=4)
    d.arc((x + w * 0.46, cy - 26, x + w * 0.72, cy + 22), 200, 160, fill=INK, width=4)
    d.line((x + w * 0.40, cy - 2, x + w * 0.48, cy - 2), fill=INK, width=4)
    d.polygon([(x + w * 0.80, y + 14), (x + w * 0.90, y + 20), (x + w * 0.86, y + 30),
               (x + w * 0.74, y + 30), (x + w * 0.70, y + 20)], outline=accent, width=3)
    d.ellipse((x + w * 0.79, y + 34, x + w * 0.81, y + 36), fill=accent)


def art_hospital(d, box, accent):
    x, y, w, h = box
    d.rounded_rectangle((x + 10, y + 20, x + w * 0.62, y + h - 10), radius=6, outline=INK, width=2)
    d.rectangle((x + 16, y + 26, x + w * 0.40, y + 34), fill=accent)
    # monitor trace
    pts = []
    for i in range(40):
        t = i / 39
        px = x + w * 0.62 + t * w * 0.32
        py = y + h * 0.46
        if 0.42 < t < 0.5:
            py -= 18
        elif 0.5 <= t < 0.56:
            py += 10
        pts.append((px, py))
    d.line(pts, fill=accent, width=3)
    d.rounded_rectangle((x + w * 0.62, y + h * 0.60, x + w * 0.96, y + h * 0.86), radius=4,
                        outline=INK, width=2)
    d.line((x + w * 0.70, y + h * 0.73, x + w * 0.74, y + h * 0.73), fill=INK, width=2)
    d.line((x + w * 0.78, y + h * 0.66, x + w * 0.78, y + h * 0.80), fill=INK, width=2)


def art_candle(d, box, accent):
    x, y, w, h = box
    cx = x + w * 0.30
    base = y + h - 8
    d.rectangle((cx - 13, y + h * 0.44, cx + 13, base), fill=accent)
    d.line((cx - 13, y + h * 0.44, cx + 13, y + h * 0.44), fill=INK, width=2)
    d.rectangle((cx - 4, y + h * 0.44 - 8, cx + 4, y + h * 0.44), fill=INK)
    d.line((cx, y + h * 0.44 - 8, cx, y + h * 0.30), fill=INK, width=2)
    d.ellipse((cx - 9, y + h * 0.12, cx + 9, y + h * 0.32), outline=INK, width=2)
    d.ellipse((cx - 4, y + h * 0.18, cx + 4, y + h * 0.30), fill=accent)
    d.arc((cx - 30, base - 26, cx + 30, base + 6), 20, 160, fill=MUTED, width=2)
    d.line((x + w * 0.58, y + 12, x + w * 0.58, base), fill=RULE, width=2)
    for i in range(3):
        d.rectangle((x + w * 0.66, y + 16 + i * 16, x + w * 0.94, y + 24 + i * 16),
                    fill=[accent, INK, accent][i])


def art_aidvan(d, box, accent):
    x, y, w, h = box
    bx, by, bw, bh = x + 12, y + h * 0.36, w * 0.62, h * 0.40
    d.rounded_rectangle((bx, by, bx + bw * 0.66, by + bh), radius=5, outline=INK, width=2)
    d.polygon([(bx + bw * 0.66, by), (bx + bw, by + bh * 0.30), (bx + bw, by + bh),
               (bx + bw * 0.66, by + bh)], outline=INK, width=2)
    d.ellipse((bx + 6, by + bh * 0.55, bx + 16, by + bh * 0.95), outline=accent, width=2)
    d.ellipse((bx + bw * 0.80, by + bh * 0.55, bx + bw * 0.90, by + bh * 0.95), outline=accent, width=2)
    d.arc((bx + 14, by + 6, bx + 44, by + 30), 0, 180, fill=accent, width=2)
    d.line((x + w * 0.86, y + 14, x + w * 0.86, y + 34), fill=INK, width=2)
    d.polygon([(x + w * 0.86, y + 34), (x + w * 0.80, y + 40), (x + w * 0.92, y + 40)], fill=accent)


def art_mercury(d, box, accent):
    x, y, w, h = box
    cx, cy, r = x + w * 0.42, y + h * 0.52, h * 0.30
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=2)
    d.ellipse((cx - r * 0.4, cy - r * 0.6, cx - r * 0.05, cy - r * 0.25), fill=accent)
    d.ellipse((cx + r * 0.16, cy + r * 0.10, cx + r * 0.5, cy + r * 0.42), fill=accent)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=2)
    d.arc((cx - r * 2.0, cy - r * 0.7, cx + r * 2.0, cy + r * 0.7), 200, 340, fill=MUTED, width=2)
    d.arc((cx - r * 1.6, cy - r * 0.5, cx + r * 1.6, cy + r * 0.5), 20, 160, fill=accent, width=2)
    d.rectangle((cx + r * 1.7, cy - 4, cx + r * 2.2, cy + 4), fill=INK)
    d.rectangle((cx - r * 2.3, cy - 3, cx - r * 1.9, cy + 3), fill=INK)


def art_budget(d, box, accent):
    x, y, w, h = box
    for i in range(4):
        d.rectangle((x + 14, y + h - 18 - i * 12, x + w * 0.34, y + h - 8 - i * 12),
                    outline=INK, width=2, fill=accent if i % 2 else None)
    for i in range(12):
        import math
        a = math.radians(i * 30 - 90)
        cxx = x + w * 0.66 + math.cos(a) * 20
        cyy = y + h * 0.44 + math.sin(a) * 20
        d.ellipse((cxx - 3, cyy - 3, cxx + 3, cyy + 3), fill=accent)
    d.rectangle((x + w * 0.56, y + h * 0.68, x + w * 0.96, y + h * 0.90), outline=INK, width=2)
    d.line((x + w * 0.62, y + h * 0.76, x + w * 0.90, y + h * 0.76), fill=MUTED, width=2)
    d.line((x + w * 0.62, y + h * 0.83, x + w * 0.82, y + h * 0.83), fill=MUTED, width=2)


def art_robot(d, box, accent):
    x, y, w, h = box
    d.rounded_rectangle((x + w * 0.20, y + 16, x + w * 0.56, y + h * 0.60), radius=8,
                        outline=INK, width=3)
    d.ellipse((x + w * 0.28, y + 28, x + w * 0.34, y + 38), fill=accent)
    d.ellipse((x + w * 0.42, y + 28, x + w * 0.48, y + 38), fill=accent)
    d.line((x + w * 0.30, y + h * 0.46, x + w * 0.46, y + h * 0.46), fill=INK, width=2)
    d.line((x + w * 0.38, y + 16, x + w * 0.38, y + 8), fill=INK, width=2)
    d.ellipse((x + w * 0.34, y + 2, x + w * 0.42, y + 10), fill=accent)
    d.line((x + w * 0.70, y + 10, x + w * 0.70, y + h * 0.64), fill=INK, width=3)
    d.polygon([(x + w * 0.70, y + h * 0.30), (x + w * 0.94, y + h * 0.22),
               (x + w * 0.94, y + h * 0.38), (x + w * 0.70, y + h * 0.46)], outline=accent, width=3)
    d.rectangle((x + w * 0.56, y + h * 0.66, x + w * 0.86, y + h * 0.80), outline=INK, width=2)


def art_servers(d, box, accent):
    x, y, w, h = box
    for i in range(3):
        d.rounded_rectangle((x + 14, y + 12 + i * 20, x + w * 0.46, y + 26 + i * 20), radius=3,
                            outline=INK, width=2)
        d.ellipse((x + 20, y + 17 + i * 20, x + 26, y + 23 + i * 20), fill=accent)
    cx, cy, r = x + w * 0.74, y + h * 0.52, h * 0.26
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=2)
    d.arc((cx - r, cy - r, cx + r, cy + r), 210, 330, fill=accent, width=3)
    d.line((cx - r, cy, cx + r, cy), fill=MUTED, width=2)
    d.line((cx, cy - r, cx, cy + r), fill=MUTED, width=2)


ART = {"summit": art_summit, "plant": art_plant, "strike": art_strike, "cuffs": art_cuffs,
       "hospital": art_hospital, "candle": art_candle, "aidvan": art_aidvan,
       "mercury": art_mercury, "budget": art_budget, "robot": art_robot, "servers": art_servers}


# ---------------------------------------------------------------- drawing ----

def draw_masthead(d):
    f = font(SANS_B, 11)
    tracked(d, MARGIN, 9, "THE DAY IN WORLD NEWS", f, INK, 1.6)
    right = f"{TOTAL} STORIES \u00b7 7 REGIONS \u00b7 ONE DAY"
    d.text((W - MARGIN - f.getlength(right), 9), right, font=f, fill=MUTED)
    d.line((MARGIN, 30, W - MARGIN, 30), fill=INK, width=2)


def draw_dateline(d):
    text = "Saturday 21 November 2026"
    size = 58
    f = font(SERIF_B, size)
    while f.getlength(text) > CONTENT and size > 30:
        size -= 1
        f = font(SERIF_B, size)
    d.text((MARGIN, 36), text, font=f, fill=INK)
    deck = ("COP31 runs into overtime \u00b7 Iran strikes Bahrain \u00b7 "
            "Mexico seizes \u2018El Chapo Isidro\u2019 as 11 die in Sinaloa")
    fd = font(SANS, 12)
    deck_y = d.textbbox((MARGIN, 36), text, font=f)[3] + 8
    block(d, MARGIN, deck_y, deck, fd, MUTED, CONTENT, 15, 1)
    d.line((MARGIN, 131, W - MARGIN, 131), fill=RULE, width=1)


CARD_TOP = 138
CARD_H = 176
CARD_GAP = 10
ROW_GAP = 10


def draw_card(d, card, x, y, w):
    accent = REGIONS[card["region"]]
    d.rectangle((x, y, x + w, y + CARD_H), fill=WHITE, outline=RULE, width=1)
    # illustration panel
    ix, iy, iw, ih = x + 1, y + 1, w - 2, 80
    d.rectangle((ix, iy, ix + iw, iy + ih), fill=PAPER_ALT)
    ART[card["art"]](d, (ix + 8, iy + 6, iw - 16, ih - 12), accent)
    # number badge
    bx, by, r = x + 14, y + ih - 6, 12
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=accent, outline=WHITE, width=2)
    fn = font(SANS_B, 13)
    tw = fn.getlength(str(card["n"]))
    d.text((bx - tw / 2, by - 8), str(card["n"]), font=fn, fill=WHITE)

    ty = y + ih + 8
    fk = font(SANS_B, 10)
    tracked(d, x + 12, ty, f"{card['region']} \u00b7 {card['field']}", fk, accent, 0.8)
    ty += 13
    lead = card.get("lead", False)
    fh = font(SERIF_B, 18 if lead else 16)
    ty = block(d, x + 12, ty, card["head"], fh, INK, w - 24, 21 if lead else 19, 2)
    fd = font(SANS, 11)
    block(d, x + 12, ty + 1, card["deck"], fd, MUTED, w - 24, 13, 2)


MAP_X, BAND_Y = MARGIN, CARD_TOP + 3 * CARD_H + 2 * ROW_GAP + 14
MAP_W, MAP_H = 372, 186


def project(lon, lat, box):
    x, y, w, h = box
    return (x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)


def draw_map(d, land):
    f = font(SANS_B, 11)
    tracked(d, MAP_X, BAND_Y, "WHERE IT HAPPENED", f, INK, 1.4)
    box = (MAP_X, BAND_Y + 18, MAP_W, MAP_H)
    d.rectangle((box[0], box[1], box[0] + box[2], box[1] + box[3]), fill=(232, 227, 214),
                outline=RULE, width=1)
    for ring in land:
        pts = [(box[0] + nx * box[2], box[1] + ny * box[3]) for nx, ny in ring]
        if len(pts) > 2:
            d.polygon(pts, fill=(196, 190, 174), outline=(150, 144, 130))
    for gx in range(1, 6):
        px = box[0] + box[2] * gx / 6
        d.line((px, box[1], px, box[1] + box[3]), fill=(221, 216, 203), width=1)
    for gy in range(1, 4):
        py = box[1] + box[3] * gy / 4
        d.line((box[0], py, box[0] + box[2], py), fill=(221, 216, 203), width=1)

    offsets = {1: (-16, -6), 2: (18, 12), 3: (8, -16), 4: (-2, -18), 5: (-2, 16),
               6: (2, 18), 7: (14, -4), 9: (-16, -6), 10: (-24, -14), 11: (18, -16)}
    for card in CARDS:
        if not card["at"]:
            continue
        tx, ty_ = project(card["at"][0], card["at"][1], box)
        accent = REGIONS[card["region"]]
        d.ellipse((tx - 4, ty_ - 4, tx + 4, ty_ + 4), fill=accent, outline=WHITE, width=1)
        dx, dy = offsets.get(card["n"], (0, 0))
        px, py = tx + dx, ty_ + dy
        if dx or dy:
            d.line((tx, ty_, px, py), fill=accent, width=1)
        d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=accent, outline=WHITE, width=2)
        fn = font(SANS_B, 11)
        label = str(card["n"])
        tw = fn.getlength(label)
        d.text((px - tw / 2, py - 6), label, font=fn, fill=WHITE)

    # legend: seven swatches in two columns of four
    ly = box[1] + box[3] + 8
    fl = font(SANS_B, 11)
    counts = {k: 0 for k in REGIONS}
    for card in CARDS:
        counts[card["region"]] += 1
    for _, region, _ in BRIEFS:
        counts[region] += 1
    for i, (name, colour) in enumerate(REGIONS.items()):
        col, row = divmod(i, 4)
        lx = MAP_X + col * 186
        lyy = ly + row * 14
        d.rectangle((lx, lyy + 2, lx + 10, lyy + 11), fill=colour)
        tracked(d, lx + 16, lyy, f"{name} {counts[name]}", fl, INK, 0.6)
    ly += 4 * 14
    fc = font(SANS, 11)
    block(d, MAP_X, ly + 4,
          "Cards 1-11 are plotted; 8 is off-planet. Briefs 12-35 are not.",
          fc, MUTED, MAP_W, 12, 2)


BRIEF_X = MAP_X + MAP_W + 18
BRIEF_W = W - MARGIN - BRIEF_X


def draw_briefs(d):
    f = font(SANS_B, 11)
    tracked(d, BRIEF_X, BAND_Y, "ALSO ON 21 NOVEMBER", f, INK, 1.4)
    d.line((BRIEF_X, BAND_Y + 16, W - MARGIN, BAND_Y + 16), fill=RULE, width=1)
    cols = 3
    gutter = 12
    col_w = (BRIEF_W - gutter * (cols - 1)) // cols
    per_col = (len(BRIEFS) + cols - 1) // cols
    top = BAND_Y + 24
    bottom = 984
    row_h = (bottom - top) // per_col
    for idx, (n, region, text) in enumerate(BRIEFS):
        col, row = divmod(idx, per_col)
        x = BRIEF_X + col * (col_w + gutter)
        y = top + row * row_h
        accent = REGIONS[region]
        fn = font(SANS_B, 11)
        d.text((x, y), str(n), font=fn, fill=accent)
        fw = fn.getlength(str(n))
        d.rectangle((x + fw + 4, y + 4, x + fw + 5, y + 10), fill=RULE)
        block(d, x + fw + 9, y, text, font(SANS, 11), INK, col_w - fw - 9, 12, 2)


def draw_footer(d):
    d.line((MARGIN, 988, W - MARGIN, 988), fill=INK, width=1)
    f = font(SANS, 11)
    line = ("Every story was reported on Saturday 21 November 2026; disputed claims are "
            "attributed. Sources: AP, Reuters, AFP, BBC, Al Jazeera, UN News. Original drawings.")
    d.text((MARGIN, 992), line, font=f, fill=MUTED)


def main() -> None:
    land = json.loads((Path(__file__).resolve().parent / "land.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_dateline(d)

    gutter = 12
    col_w = (CONTENT - gutter * 3) // 4
    rows = [[2 * col_w + gutter, col_w, col_w], [col_w] * 4, [col_w] * 4]
    n = 0
    for r, widths in enumerate(rows):
        y = CARD_TOP + r * (CARD_H + ROW_GAP)
        x = MARGIN
        for w in widths:
            draw_card(d, CARDS[n], x, y, w)
            x += w + gutter
            n += 1
    draw_map(d, land)
    draw_briefs(d)
    draw_footer(d)

    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True, compress_level=9)
    size = out.stat().st_size
    print(f"wrote {out} {img.width}x{img.height} {size} bytes")


if __name__ == "__main__":
    main()

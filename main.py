#!/usr/bin/env python3
"""VELMARA — a travel poster for a place that isn't there.

Velmara is an invented island, the Isle of the Glowing Sea. This
program draws its vintage travel poster at 1024x1024: a dusk sky
fading from indigo to amber, the Luminous Spire lighthouse throwing
a warm beam across a glowing sea, a lantern sailboat on the sun's
light path, and the island's name set big across the sky.

Only the Python standard library is used (math, os, struct, zlib).
The run is fully deterministic — fixed numbers throughout, no
clock, no randomness, no network — and writes entry.png into
/output, or into $MAKEFUN_OUTPUT_DIR when that is set.

Nothing here is a real destination: no quotes, no star ratings,
no borrowed place.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette: dusk over a glowing sea --------------------------------
PAPER = (250, 240, 214)       # poster paper, also the outer frame
NIGHT = (24, 22, 44)          # silhouettes after dark
DUSK_TOP = (44, 34, 96)      # indigo at the top of the sky
DUSK_MID = (112, 62, 138)     # violet band
DUSK_LOW = (198, 84, 112)     # magenta dusk
DUSK_GLOW = (250, 148, 62)    # amber where the sky meets the sea
SUN = (255, 214, 110)         # the low sun
SUN_HEART = (255, 236, 180)   # the sun's bright core
TIDE_TOP = (22, 92, 118)      # teal sea at the horizon
TIDE_DEEP = (10, 42, 72)      # deep water at the foot
GOLD = (255, 190, 80)         # lanterns and rules
CRYSTAL = (238, 230, 216)     # pale lighthouse stone
CRYSTAL_DIM = (196, 182, 196) # its shaded bands
ROCK = (18, 20, 44)           # islets and horizon islands
PINE = (14, 40, 34)           # headland pines
WHITE = (255, 255, 255)       # starlight

# --- 5x7 pixel font --------------------------------------------------
# One glyph is seven rows of five bits, written as strings so the
# picture of each letter is visible in the source: "1" paints a
# pixel, "0" leaves it blank, leftmost character first.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def blend(a, b, t):
    """Mix two RGB colours; t=0 gives a, t=1 gives b."""
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def gradient(stops, t):
    """Colour of a multi-stop gradient at position t in [0, 1]."""
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(1, len(stops)):
        if t <= stops[i][0]:
            t0, c0 = stops[i - 1]
            t1, c1 = stops[i]
            return blend(c0, c1, (t - t0) / (t1 - t0))
    return stops[-1][1]


class Poster:
    """A plain RGB pixel buffer with small vector drawing helpers."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(bg) * (width * height)

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            at = (y * self.w + x) * 3
            self.buf[at] = colour[0]
            self.buf[at + 1] = colour[1]
            self.buf[at + 2] = colour[2]

    def box(self, x, y, w, h, colour):
        stripe = bytes(colour) * w
        left = max(x, 0)
        right = min(x + w, self.w)
        if right <= left:
            return
        for yy in range(max(y, 0), min(y + h, self.h)):
            at = (yy * self.w + left) * 3
            self.buf[at:at + 3 * (right - left)] = \
                stripe[3 * (left - x):3 * (right - x)]

    def border(self, x, y, w, h, colour, thick=2):
        self.box(x, y, w, thick, colour)
        self.box(x, y + h - thick, w, thick, colour)
        self.box(x, y, thick, h, colour)
        self.box(x + w - thick, y, thick, h, colour)

    def hbar(self, x, y, w, colour, thick=1):
        self.box(x, y, w, thick, colour)

    def vbar(self, x, y, h, colour, thick=1):
        self.box(x, y, thick, h, colour)

    def stroke(self, x0, y0, x1, y1, colour, thick=1):
        # Bresenham walk; each step stamps a thick square.
        run = abs(x1 - x0)
        rise = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = run + rise
        px, py = x0, y0
        half = thick // 2
        while True:
            self.box(px - half, py - half, thick, thick, colour)
            if px == x1 and py == y1:
                return
            e2 = 2 * err
            if e2 >= rise:
                err += rise
                px += sx
            if e2 <= run:
                err += run
                py += sy

    def spot(self, cx, cy, r, colour):
        # Filled circle, one horizontal run per row.
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) * (yy - cy))))
            self.box(cx - dx, yy, 2 * dx + 1, 1, colour)

    def wedge(self, ax, ay, bx, by, cx, cy, colour):
        # Filled triangle by scanlines between its three edges.
        top = min(ay, by, cy)
        bottom = max(ay, by, cy)
        edges = ((ax, ay, bx, by), (bx, by, cx, cy), (cx, cy, ax, ay))
        for yy in range(top, bottom + 1):
            hits = []
            for (x1, y1, x2, y2) in edges:
                if y1 == y2:
                    continue
                low, high = (y1, y2) if y1 < y2 else (y2, y1)
                if low <= yy < high or (yy == bottom and yy == high):
                    hits.append(x1 + (x2 - x1) * (yy - y1) / (y2 - y1))
            if len(hits) >= 2:
                self.box(int(min(hits)), yy,
                         int(max(hits)) - int(min(hits)) + 1, 1, colour)

    def vshade(self, x, y, w, h, stops):
        """Fill a band with a vertical multi-stop gradient."""
        for yy in range(y, y + h):
            t = (yy - y) / max(1, h - 1)
            self.box(x, yy, w, 1, gradient(stops, t))


def text_width(text, scale):
    # Six pixels per character cell (five glyph pixels plus spacing).
    return len(text) * 6 * scale


def draw_string(pg, x, y, text, scale, colour):
    """Draw uppercase text; a character outside the font is blank."""
    cursor = x
    for ch in text:
        rows = FONT.get(ch) or FONT[" "]
        for row_no, row in enumerate(rows):
            for col_no, bit in enumerate(row):
                if bit == "1":
                    pg.box(cursor + col_no * scale,
                           y + row_no * scale, scale, scale, colour)
        cursor += 6 * scale
    return cursor


def draw_centered(pg, x, y, width, text, scale, colour):
    draw_string(pg, x + (width - text_width(text, scale)) // 2,
                y, text, scale, colour)


def draw_title(pg, x, y, width, text, scale, colour, shadow):
    """Centred text with a soft offset shadow behind it."""
    w = text_width(text, scale)
    cx = x + (width - w) // 2
    draw_string(pg, cx + 3, y + 4, text, scale, shadow)
    draw_string(pg, cx, y, text, scale, colour)


# ---------------------------------------------------------------- scene

SKY = ((0.0, DUSK_TOP), (0.45, DUSK_MID),
       (0.78, DUSK_LOW), (1.0, DUSK_GLOW))
SEA = ((0.0, TIDE_TOP), (1.0, TIDE_DEEP))

# Frame and picture area.
X0, Y0, PW, PH = 24, 24, 976, 976
SEALINE = 560        # y of the sea line, inside the frame
SHORE = 880          # where the foreground headland starts

# Early stars in the indigo top of the sky, as (x, y) inside the frame.
STARS = ((80, 60), (150, 44), (230, 84), (330, 52),
         (460, 50), (700, 58), (820, 80), (920, 48),
         (880, 130), (120, 130), (520, 40), (770, 150),
         (600, 36), (950, 170))
# Three birds crossing the dusk: (x, y, wingspan), kept clear of the
# place name and its subtitle.
BIRDS = ((830, 190, 12), (880, 240, 9), (790, 270, 8))
# Long low waves: (y, x-start, x-end).
WAVES = ((600, 60, 420), (640, 780, 960), (680, 90, 380),
         (720, 800, 950), (760, 120, 420), (810, 700, 940),
         (840, 150, 480), (860, 560, 940))
# Pines on the headland: (x, height).
PINES = ((120, 64), (180, 84), (880, 70), (930, 56))
# Lantern dots along the headland path.
PATH_LAMPS = (420, 480, 540, 600)


def paint_sky(pg):
    pg.vshade(X0, Y0, PW, SEALINE - Y0, SKY)
    for (star_x, star_y) in STARS:
        pg.spot(X0 + star_x, Y0 + star_y, 2, WHITE)
        pg.spot(X0 + star_x, Y0 + star_y, 1, SUN_HEART)
    for (bird_x, bird_y, span) in BIRDS:
        pg.stroke(bird_x - span, bird_y, bird_x, bird_y - span // 2,
                  NIGHT, 2)
        pg.stroke(bird_x, bird_y - span // 2, bird_x + span, bird_y,
                  NIGHT, 2)


def paint_sun(pg):
    # Low sun over the sea, with a soft glow fading into the sky.
    # Its centre sits just above the horizon so the disc dips into
    # the sea line, and it stands right of the lighthouse beam so
    # the beam never crosses the sun itself.
    sx, sy = 740, 548
    for r, col in ((140, blend(DUSK_GLOW, SUN, 0.25)),
                   (112, blend(DUSK_GLOW, SUN, 0.45)),
                   (88, blend(DUSK_GLOW, SUN, 0.7)),
                   (68, SUN)):
        pg.spot(sx, sy, r, col)
    pg.spot(sx, sy, 52, SUN_HEART)
    # Flat bottom where the sun meets the sea line.
    pg.box(sx - 52, SEALINE - 6, 104, 10, TIDE_TOP)


def paint_sea(pg):
    pg.vshade(X0, SEALINE, PW, SHORE - SEALINE, SEA)
    # The sun's light path on the water: gold dashes widening
    # towards the viewer, brightest at the horizon, each offset a
    # little so the path shimmers instead of laddering.
    for (wy, half, off, col) in (
            (566, 22, -4, blend(TIDE_TOP, SUN, 0.85)),
            (590, 34, 6, blend(TIDE_TOP, SUN, 0.7)),
            (620, 48, -8, blend(TIDE_TOP, SUN, 0.55)),
            (655, 64, 5, blend(TIDE_TOP, SUN, 0.42)),
            (695, 82, -6, blend(TIDE_TOP, SUN, 0.3)),
            (740, 100, 8, blend(TIDE_TOP, SUN, 0.2)),
            (790, 118, -5, blend(TIDE_TOP, SUN, 0.12))):
        pg.box(740 - half + off, wy, 2 * half, 5, col)
    for (wy, x0, x1) in WAVES:
        pg.hbar(x0, wy, x1 - x0, blend(TIDE_TOP, WHITE, 0.35), 2)


def paint_isles(pg):
    # Two low dark islands on the horizon, clear of the sun path.
    pg.wedge(60, SEALINE, 150, SEALINE - 34, 250, SEALINE, ROCK)
    pg.wedge(180, SEALINE, 260, SEALINE - 22, 340, SEALINE, ROCK)
    pg.wedge(830, SEALINE, 900, SEALINE - 26, 970, SEALINE, ROCK)
    # A tiny watchtower on the left island.
    pg.box(140, SEALINE - 52, 10, 20, ROCK)
    pg.wedge(138, SEALINE - 52, 152, SEALINE - 52, 145, SEALINE - 62,
             ROCK)


def paint_spire(pg):
    # The Luminous Spire: Velmara's crystal lighthouse on its rocky
    # islet, left of centre, with its beam sweeping over the sea.
    isle_x, isle_y = 330, SEALINE   # islet centre at the horizon
    # Rocky islet: a low wide mound, not a ball.
    pg.wedge(isle_x - 78, isle_y, isle_x - 30, isle_y - 30,
             isle_x + 20, isle_y, ROCK)
    pg.wedge(isle_x - 10, isle_y, isle_x + 40, isle_y - 24,
             isle_x + 78, isle_y, ROCK)
    pg.box(isle_x - 78, isle_y - 4, 156, 12, ROCK)
    pg.wedge(isle_x + 50, isle_y, isle_x + 64, isle_y - 14,
             isle_x + 78, isle_y, ROCK)
    pg.wedge(isle_x - 60, isle_y, isle_x - 20, isle_y - 26,
             isle_x + 10, isle_y, ROCK)
    # Tower: stacked bands, tapering towards the lantern room.
    lamp_y, foot_y = 356, isle_y - 4
    steps = 12
    for i in range(steps):
        t = i / steps
        yy = int(lamp_y + (foot_y - lamp_y) * t)
        hh = int((foot_y - lamp_y) / steps) + 1
        half = int(26 - 12 * t)
        col = CRYSTAL if i % 2 == 0 else CRYSTAL_DIM
        pg.box(isle_x - half, yy, 2 * half, hh, col)
    # Lantern room: gold glow and a crystal cap.
    pg.spot(isle_x, lamp_y - 6, 22, SUN)
    pg.spot(isle_x, lamp_y - 6, 13, SUN_HEART)
    pg.wedge(isle_x - 20, lamp_y - 16, isle_x + 20, lamp_y - 16,
             isle_x, lamp_y - 38, CRYSTAL)
    pg.spot(isle_x, lamp_y - 40, 4, GOLD)
    # The beam: a wide warm-gold wedge sweeping right over the sea.
    # Two wedges layered: a broad pale wash, then a brighter core
    # inside it, so the beam reads as light rather than a flat bar.
    pg.wedge(isle_x + 10, lamp_y - 6, 940, SEALINE - 58,
             940, SEALINE + 6, blend(DUSK_GLOW, SUN_HEART, 0.55))
    pg.wedge(isle_x + 10, lamp_y - 6, 940, SEALINE - 30,
             940, SEALINE - 6, blend(DUSK_GLOW, SUN_HEART, 0.8))
    # Two lanterns on the islet rocks.
    pg.spot(isle_x - 52, isle_y - 18, 4, GOLD)
    pg.spot(isle_x + 48, isle_y - 22, 4, GOLD)


def paint_boat(pg):
    # A small sailboat with a lantern, crossing the light path.
    boat_x, boat_y = 740, 700
    # Hull.
    pg.wedge(boat_x - 34, boat_y, boat_x + 34, boat_y,
             boat_x, boat_y + 16, NIGHT)
    # Mast and two sails, cream against the dusk.
    pg.vbar(boat_x, boat_y - 62, 62, NIGHT, 3)
    pg.wedge(boat_x + 3, boat_y - 60, boat_x + 3, boat_y - 6,
             boat_x + 34, boat_y - 6, PAPER)
    pg.wedge(boat_x - 3, boat_y - 52, boat_x - 3, boat_y - 6,
             boat_x - 28, boat_y - 6, PAPER)
    # A lantern at the stern.
    pg.spot(boat_x - 38, boat_y - 8, 4, GOLD)


def paint_shore(pg):
    # Dark foreground headland along the bottom, with pine trees
    # and a tiny lantern-lit path, framing the poster.
    pg.box(X0, SHORE, PW, Y0 + PH - SHORE, NIGHT)
    pg.wedge(X0, SHORE, X0 + 260, SHORE, X0 + 60, SHORE - 46, NIGHT)
    pg.wedge(X0 + PW - 300, SHORE, X0 + PW, SHORE,
             X0 + PW - 80, SHORE - 40, NIGHT)
    # Pine silhouettes on the headland, darkest green-black.
    for (tree_x, tree_h) in PINES:
        pg.wedge(tree_x - 16, SHORE - 8, tree_x + 16, SHORE - 8,
                 tree_x, SHORE - 8 - tree_h, PINE)
        pg.wedge(tree_x - 12, SHORE - 8 - tree_h // 2,
                 tree_x + 12, SHORE - 8 - tree_h // 2,
                 tree_x, SHORE - 8 - tree_h - 12, PINE)
        pg.box(tree_x - 2, SHORE - 10, 4, 10, PINE)
    # Lantern dots along a path on the headland.
    for lamp_x in PATH_LAMPS:
        pg.spot(lamp_x, SHORE + 34, 3, GOLD)


def build_poster():
    pg = Poster(W, H, PAPER)
    # Vintage poster frame: cream border, gold rule, dark inner line.
    pg.border(0, 0, W, H, PAPER, 24)
    pg.border(12, 12, W - 24, H - 24, GOLD, 2)
    pg.border(X0 - 2, Y0 - 2, PW + 4, PH + 4, NIGHT, 2)

    # Paint back to front: sky first, then the sun, the sea, the
    # islands, the spire and its beam, the boat, and the dark
    # headland that frames the bottom. The type goes on last.
    paint_sky(pg)
    paint_sun(pg)
    paint_sea(pg)
    paint_isles(pg)
    paint_spire(pg)
    paint_boat(pg)
    paint_shore(pg)

    # The place name, large across the dusk sky, with a shadow so it
    # reads against the violet: the eye starts here, then drops to
    # the spire and the glowing horizon.
    draw_title(pg, X0, 84, PW, "VELMARA", 12, PAPER, DUSK_TOP)
    # A thin gold rule under the name.
    name_w = text_width("VELMARA", 12)
    rule_x = X0 + (PW - name_w) // 2
    pg.hbar(rule_x, 84 + 7 * 12 + 14, name_w, GOLD, 3)
    draw_centered(pg, X0, 84 + 7 * 12 + 26, PW,
                  "ISLE OF THE GLOWING SEA", 3, SUN_HEART)

    # The promise, set into the dark headland at the foot.
    draw_centered(pg, X0, SHORE + 62, PW,
                  "WHERE THE SEA GLOWS AT DUSK", 3, PAPER)
    draw_centered(pg, X0, SHORE + 92, PW,
                  "SAIL BEYOND THE MAP", 2, GOLD)
    return pg


def png_bytes(pg):
    """Encode the poster as a 1024x1024 RGB PNG, filter 0 per row."""

    def pack(kind, payload):
        framed = struct.pack(">I", len(payload)) + kind + payload
        return framed + struct.pack(">I", zlib.crc32(kind + payload)
                                    & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", pg.w, pg.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for row_no in range(pg.h):
        raw.append(0)
        raw += pg.buf[row_no * pg.w * 3:(row_no + 1) * pg.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + pack(b"IHDR", header)
            + pack(b"IDAT", zlib.compress(bytes(raw), 6))
            + pack(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_poster())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()

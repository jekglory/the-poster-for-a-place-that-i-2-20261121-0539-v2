#!/usr/bin/env python3
"""the-poster-for-a-place-that-i-2-20261121-0539-v2 - VELMARA.

A travel poster for a place that does not exist: Velmara, the Isle
of the Glowing Sea. Pure Python standard library (math, os, struct,
zlib only). It paints a 1024x1024 vintage travel poster: a sunset
sky over a glowing sea, the Luminous Spire lighthouse on its rocky
islet, a lantern sailboat, and the place name set large across the
sky. Deterministic: fixed constants, no clock, no randomness, no
network. Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

The place is invented: Velmara, its glowing sea and its crystal
lighthouse exist only in this poster. No real destination is shown,
no quotes, no star ratings.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette -------------------------------------------------------
CREAM = (250, 240, 214)      # poster paper / frame
PAPER_DARK = (232, 214, 178)
INK = (24, 22, 44)           # deep night silhouette
SKY_TOP = (44, 34, 96)       # indigo dusk
SKY_MID = (112, 62, 138)     # violet
SKY_LOW = (198, 84, 112)     # magenta dusk
SKY_HORIZON = (250, 148, 62) # amber at the horizon
SUN = (255, 214, 110)        # low sun
SUN_CORE = (255, 236, 180)
SEA_TOP = (22, 92, 118)      # teal sea at the horizon
SEA_DEEP = (10, 42, 72)      # deep sea
GOLD = (255, 190, 80)
SPIRE = (238, 230, 216)      # pale crystal lighthouse
SPIRE_SHADE = (196, 182, 196)
ROCK = (18, 20, 44)
LEAF = (14, 40, 34)
WHITE = (255, 255, 255)

# 5x7 pixel font. Each glyph is seven rows; each row is a 5-bit
# integer, bit 4 first (leftmost pixel), bit 0 last.
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ".": (0, 0, 0, 0, 0, 12, 12),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0),
    ":": (0, 12, 12, 0, 12, 12, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "*": (0, 4, 21, 14, 21, 4, 0),
}


def lerp(a, b, t):
    """Blend two RGB colours; t=0 gives a, t=1 gives b."""
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grad_at(stops, t):
    """Colour of a multi-stop gradient at position t in [0, 1]."""
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(1, len(stops)):
        if t <= stops[i][0]:
            t0, c0 = stops[i - 1]
            t1, c1 = stops[i]
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return stops[-1][1]


class Canvas:
    """A plain RGB pixel buffer with small vector drawing helpers."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg) * (width * height)

    def dot(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            at = (y * self.w + x) * 3
            self.px[at] = colour[0]
            self.px[at + 1] = colour[1]
            self.px[at + 2] = colour[2]

    def rect(self, x, y, w, h, colour):
        stripe = bytes(colour) * w
        left = max(x, 0)
        right = min(x + w, self.w)
        if right <= left:
            return
        for yy in range(max(y, 0), min(y + h, self.h)):
            at = (yy * self.w + left) * 3
            self.px[at:at + 3 * (right - left)] = \
                stripe[3 * (left - x):3 * (right - x)]

    def frame(self, x, y, w, h, colour, thick=2):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        # Bresenham walk; each step stamps a thick square.
        run = abs(x1 - x0)
        rise = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = run + rise
        px, py = x0, y0
        half = thick // 2
        while True:
            self.rect(px - half, py - half, thick, thick, colour)
            if px == x1 and py == y1:
                return
            e2 = 2 * err
            if e2 >= rise:
                err += rise
                px += sx
            if e2 <= run:
                err += run
                py += sy

    def disc(self, cx, cy, r, colour):
        # Filled circle, one horizontal run per row.
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) * (yy - cy))))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        # Circle outline: pixels whose distance is near r.
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= r * r:
                    self.dot(xx, yy, colour)

    def tri(self, ax, ay, bx, by, cx, cy, colour):
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
                self.rect(int(min(hits)), yy,
                          int(max(hits)) - int(min(hits)) + 1, 1, colour)

    def vgrad(self, x, y, w, h, stops):
        """Fill a band with a vertical multi-stop gradient."""
        for yy in range(y, y + h):
            t = (yy - y) / max(1, h - 1)
            self.rect(x, yy, w, 1, grad_at(stops, t))


def text_w(text, scale):
    # Six pixels per character cell (five glyph pixels plus spacing).
    return len(text) * 6 * scale


def draw_text(cv, x, y, text, scale, colour):
    """Draw uppercase text; a character outside the font is blank."""
    cursor = x
    for ch in text:
        rows = FONT.get(ch) or FONT[" "]
        for row_no, bits in enumerate(rows):
            for col_no in range(5):
                if bits & (16 >> col_no):
                    cv.rect(cursor + col_no * scale,
                            y + row_no * scale, scale, scale, colour)
        cursor += 6 * scale
    return cursor


def draw_centred(cv, x, y, width, text, scale, colour):
    draw_text(cv, x + (width - text_w(text, scale)) // 2,
              y, text, scale, colour)


def draw_shadow_text(cv, x, y, width, text, scale, colour, shadow):
    """Centred text with a soft offset shadow behind it."""
    w = text_w(text, scale)
    cx = x + (width - w) // 2
    draw_text(cv, cx + 3, y + 4, text, scale, shadow)
    draw_text(cv, cx, y, text, scale, colour)


# ---------------------------------------------------------------- scene

SKY_STOPS = ((0.0, SKY_TOP), (0.45, SKY_MID),
             (0.78, SKY_LOW), (1.0, SKY_HORIZON))
SEA_STOPS = ((0.0, SEA_TOP), (1.0, SEA_DEEP))

# Frame and picture area.
FX, FY, FW, FH = 24, 24, 976, 976
HORIZON = 560          # y of the sea line, inside the frame
SEA_BOTTOM = 880       # where the foreground headland starts


def scene_sky(cv):
    cv.vgrad(FX, FY, FW, HORIZON - FY, SKY_STOPS)
    # A few early stars in the indigo top of the sky.
    for (sx, sy) in ((80, 60), (150, 44), (230, 84), (330, 52),
                     (460, 50), (700, 58), (820, 80), (920, 48),
                     (880, 130), (120, 130), (520, 40), (770, 150),
                     (600, 36), (950, 170)):
        cv.disc(FX + sx, FY + sy, 2, WHITE)
        cv.disc(FX + sx, FY + sy, 1, SUN_CORE)
    # Three birds crossing the dusk, small dark chevrons, kept clear
    # of the place name and its subtitle.
    for (bx, by, s) in ((830, 190, 12), (880, 240, 9), (790, 270, 8)):
        cv.line(bx - s, by, bx, by - s // 2, INK, 2)
        cv.line(bx, by - s // 2, bx + s, by, INK, 2)


def scene_sun(cv):
    # Low sun over the sea, with a soft glow fading into the sky.
    # Its centre sits just above the horizon so the disc dips into
    # the sea line, and it stands right of the lighthouse beam so
    # the beam never crosses the sun itself.
    cx, cy = 740, 548
    for r, col in ((140, lerp(SKY_HORIZON, SUN, 0.25)),
                   (112, lerp(SKY_HORIZON, SUN, 0.45)),
                   (88, lerp(SKY_HORIZON, SUN, 0.7)),
                   (68, SUN)):
        cv.disc(cx, cy, r, col)
    cv.disc(cx, cy, 52, SUN_CORE)
    # Flat bottom where the sun meets the sea line.
    cv.rect(cx - 52, HORIZON - 6, 104, 10, SEA_TOP)


def scene_sea(cv):
    cv.vgrad(FX, HORIZON, FW, SEA_BOTTOM - HORIZON, SEA_STOPS)
    # The sun's light path on the water: gold dashes widening
    # towards the viewer, brightest at the horizon, each offset a
    # little so the path shimmers instead of laddering.
    for i, (wy, half, off, col) in enumerate((
            (566, 22, -4, lerp(SEA_TOP, SUN, 0.85)),
            (590, 34, 6, lerp(SEA_TOP, SUN, 0.7)),
            (620, 48, -8, lerp(SEA_TOP, SUN, 0.55)),
            (655, 64, 5, lerp(SEA_TOP, SUN, 0.42)),
            (695, 82, -6, lerp(SEA_TOP, SUN, 0.3)),
            (740, 100, 8, lerp(SEA_TOP, SUN, 0.2)),
            (790, 118, -5, lerp(SEA_TOP, SUN, 0.12)))):
        cv.rect(740 - half + off, wy, 2 * half, 5, col)
    # Long low waves: thin pale lines across the sea.
    for (wy, x0, x1) in ((600, 60, 420), (640, 780, 960), (680, 90, 380),
                         (720, 800, 950), (760, 120, 420), (810, 700, 940),
                         (840, 150, 480), (860, 560, 940)):
        cv.hline(x0, wy, x1 - x0, lerp(SEA_TOP, WHITE, 0.35), 2)


def scene_islands(cv):
    # Two low dark islands on the horizon, clear of the sun path.
    cv.tri(60, HORIZON, 150, HORIZON - 34, 250, HORIZON, ROCK)
    cv.tri(180, HORIZON, 260, HORIZON - 22, 340, HORIZON, ROCK)
    cv.tri(830, HORIZON, 900, HORIZON - 26, 970, HORIZON, ROCK)
    # A tiny watchtower on the left island.
    cv.rect(140, HORIZON - 52, 10, 20, ROCK)
    cv.tri(138, HORIZON - 52, 152, HORIZON - 52, 145, HORIZON - 62, ROCK)


def scene_spire(cv):
    # The Luminous Spire: Velmara's crystal lighthouse on its rocky
    # islet, left of centre, with its beam sweeping over the sea.
    ix, iy = 330, HORIZON          # islet centre at the horizon
    # Rocky islet: a low wide mound, not a ball.
    cv.tri(ix - 78, iy, ix - 30, iy - 30, ix + 20, iy, ROCK)
    cv.tri(ix - 10, iy, ix + 40, iy - 24, ix + 78, iy, ROCK)
    cv.rect(ix - 78, iy - 4, 156, 12, ROCK)
    cv.tri(ix + 50, iy, ix + 64, iy - 14, ix + 78, iy, ROCK)
    cv.tri(ix - 60, iy, ix - 20, iy - 26, ix + 10, iy, ROCK)
    # Tower: stacked bands, tapering towards the lantern room.
    top_y, base_y = 356, iy - 4
    steps = 12
    for i in range(steps):
        t = i / steps
        yy = int(top_y + (base_y - top_y) * t)
        hh = int((base_y - top_y) / steps) + 1
        half = int(26 - 12 * t)
        col = SPIRE if i % 2 == 0 else SPIRE_SHADE
        cv.rect(ix - half, yy, 2 * half, hh, col)
    # Lantern room: gold glow and a crystal cap.
    cv.disc(ix, top_y - 6, 22, SUN)
    cv.disc(ix, top_y - 6, 13, SUN_CORE)
    cv.tri(ix - 20, top_y - 16, ix + 20, top_y - 16, ix, top_y - 38,
           SPIRE)
    cv.disc(ix, top_y - 40, 4, GOLD)
    # The beam: a wide warm-gold wedge sweeping right over the sea.
    cv.tri(ix + 10, top_y - 6, 940, HORIZON - 58, 940, HORIZON + 6,
           lerp(SKY_HORIZON, SUN_CORE, 0.55))
    cv.tri(ix + 10, top_y - 6, 940, HORIZON - 30, 940, HORIZON - 6,
           lerp(SKY_HORIZON, SUN_CORE, 0.8))
    # Two lanterns on the islet rocks.
    cv.disc(ix - 52, iy - 18, 4, GOLD)
    cv.disc(ix + 48, iy - 22, 4, GOLD)


def scene_boat(cv):
    # A small sailboat with a lantern, crossing the light path.
    bx, by = 740, 700
    # Hull.
    cv.tri(bx - 34, by, bx + 34, by, bx, by + 16, INK)
    # Mast and two sails, cream against the dusk.
    cv.vline(bx, by - 62, 62, INK, 3)
    cv.tri(bx + 3, by - 60, bx + 3, by - 6, bx + 34, by - 6, CREAM)
    cv.tri(bx - 3, by - 52, bx - 3, by - 6, bx - 28, by - 6, CREAM)
    # A lantern at the stern.
    cv.disc(bx - 38, by - 8, 4, GOLD)


def scene_headland(cv):
    # Dark foreground headland along the bottom, with pine trees
    # and a tiny lantern-lit path, framing the poster.
    cv.rect(FX, SEA_BOTTOM, FW, FY + FH - SEA_BOTTOM, INK)
    cv.tri(FX, SEA_BOTTOM, FX + 260, SEA_BOTTOM,
           FX + 60, SEA_BOTTOM - 46, INK)
    cv.tri(FX + FW - 300, SEA_BOTTOM, FX + FW, SEA_BOTTOM,
           FX + FW - 80, SEA_BOTTOM - 40, INK)
    # Pine silhouettes on the headland, darkest green-black.
    for (tx, th) in ((120, 64), (180, 84), (880, 70), (930, 56)):
        cv.tri(tx - 16, SEA_BOTTOM - 8, tx + 16, SEA_BOTTOM - 8,
               tx, SEA_BOTTOM - 8 - th, LEAF)
        cv.tri(tx - 12, SEA_BOTTOM - 8 - th // 2,
               tx + 12, SEA_BOTTOM - 8 - th // 2,
               tx, SEA_BOTTOM - 8 - th - 12, LEAF)
        cv.rect(tx - 2, SEA_BOTTOM - 10, 4, 10, LEAF)
    # Lantern dots along a path on the headland.
    for lx in (420, 480, 540, 600):
        cv.disc(lx, SEA_BOTTOM + 34, 3, GOLD)


def compose():
    cv = Canvas(W, H, CREAM)
    # Vintage poster frame: cream border, gold rule, dark inner line.
    cv.frame(0, 0, W, H, CREAM, 24)
    cv.frame(12, 12, W - 24, H - 24, GOLD, 2)
    cv.frame(FX - 2, FY - 2, FW + 4, FH + 4, INK, 2)

    scene_sky(cv)
    scene_sun(cv)
    scene_sea(cv)
    scene_islands(cv)
    scene_spire(cv)
    scene_boat(cv)
    scene_headland(cv)

    # The place name, large across the dusk sky, with a shadow so it
    # reads against the violet: the eye starts here, then drops to
    # the spire and the glowing horizon.
    draw_shadow_text(cv, FX, 84, FW, "VELMARA", 12, CREAM, SKY_TOP)
    # A thin gold rule under the name.
    name_w = text_w("VELMARA", 12)
    rule_x = FX + (FW - name_w) // 2
    cv.hline(rule_x, 84 + 7 * 12 + 14, name_w, GOLD, 3)
    draw_centred(cv, FX, 84 + 7 * 12 + 26, FW,
                 "ISLE OF THE GLOWING SEA", 3, SUN_CORE)

    # The promise, set into the dark headland at the foot.
    draw_centred(cv, FX, SEA_BOTTOM + 62, FW,
                 "WHERE THE SEA GLOWS AT DUSK", 3, CREAM)
    draw_centred(cv, FX, SEA_BOTTOM + 92, FW,
                 "SAIL BEYOND THE MAP", 2, GOLD)
    return cv


def encode_png(cv):
    """Encode the canvas as a 1024x1024 RGB PNG, filter 0 per row."""

    def pack(kind, payload):
        framed = struct.pack(">I", len(payload)) + kind + payload
        return framed + struct.pack(">I", zlib.crc32(kind + payload)
                                    & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for row_no in range(cv.h):
        raw.append(0)
        raw += cv.px[row_no * cv.w * 3:(row_no + 1) * cv.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + pack(b"IHDR", header)
            + pack(b"IDAT", zlib.compress(bytes(raw), 6))
            + pack(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(compose())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()

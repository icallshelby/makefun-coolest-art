#!/usr/bin/env python3
"""make.fun coolest-art-01 entry: "The Star Fisherman" (v4)

Pure Python 3 standard library (no PIL, no numpy, no network).
Renders a poetic night scene: a small lone fisherman in a rowboat
fishing stars from the sky with a long line, under a giant glowing
crescent moon and shimmering sea, using signed-distance shapes and
1.5 px analytic anti-aliasing.

Writes a deterministic PNG to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader container).

Run:  python3 main.py
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024
HYPOT = math.hypot


# ---------------------------------------------------------------- canvas

class Canvas:
    """RGB bytearray canvas; shapes paint colour where their SDF <= 0."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set_bg(self, top, bottom):
        w, h, px = self.w, self.h, self.px
        for y in range(h):
            t = y / (h - 1)
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            row = y * w * 3
            line = bytes((r, g, b)) * w
            px[row:row + w * 3] = line

    def get_sky_color(self, x, y):
        t = y / (self.h - 1)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        return (r, g, b)

    def paint(self, bbox, dist_fn, color):
        """dist_fn(x, y) <= 0 is inside; 1.5 px AA band on the edge."""
        x0, y0, x1, y1 = bbox
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w - 1, x1); y1 = min(self.h - 1, y1)
        px, w = self.px, self.w
        cr, cg, cb = color
        for y in range(y0, y1 + 1):
            base = y * w * 3
            for x in range(x0, x1 + 1):
                d = dist_fn(x, y)
                if d < 0.75:
                    a = 1.0 if d <= -0.75 else (0.75 - d) / 1.5
                    i = base + x * 3
                    ia = 1.0 - a
                    px[i] = int(cr * a + px[i] * ia + 0.5)
                    px[i + 1] = int(cg * a + px[i + 1] * ia + 0.5)
                    px[i + 2] = int(cb * a + px[i + 2] * ia + 0.5)

    def paint_fn(self, bbox, fn):
        """fn(x, y) -> (color, alpha) or None, for shaded/glowing shapes."""
        x0, y0, x1, y1 = bbox
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w - 1, x1); y1 = min(self.h - 1, y1)
        px, w = self.px, self.w
        for y in range(y0, y1 + 1):
            base = y * w * 3
            for x in range(x0, x1 + 1):
                out = fn(x, y)
                if out is not None:
                    color, a = out
                    if a > 0.0:
                        if a > 1.0:
                            a = 1.0
                        i = base + x * 3
                        ia = 1.0 - a
                        px[i] = int(color[0] * a + px[i] * ia + 0.5)
                        px[i + 1] = int(color[1] * a + px[i + 1] * ia + 0.5)
                        px[i + 2] = int(color[2] * a + px[i + 2] * ia + 0.5)


# ------------------------------------------------------- distance helpers

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def cov(d):
    return clamp(0.75 - d, 0.0, 1.0)


def d_circle(x, y, cx, cy, r):
    return HYPOT(x - cx, y - cy) - r


def d_ellipse(x, y, cx, cy, rx, ry):
    return (HYPOT((x - cx) / rx, (y - cy) / ry) - 1.0) * (rx if rx < ry else ry)


def d_segment(x, y, ax, ay, bx, by):
    px, py = x - ax, y - ay
    dx, dy = bx - ax, by - ay
    t = clamp((px * dx + py * dy) / (dx * dx + dy * dy), 0.0, 1.0)
    return HYPOT(px - dx * t, py - dy * t)


def d_polyline(x, y, pts):
    best = 1e18
    for i in range(len(pts) - 1):
        d = d_segment(x, y, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
        if d < best:
            best = d
    return best


def bezier_pts(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def bbox_of(pts, pad):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (int(min(xs) - pad), int(min(ys) - pad),
            int(max(xs) + pad), int(max(ys) + pad))


# ---------------------------------------------------------------- palette

SKY_TOP = (8, 10, 30)
SKY_BOT = (24, 30, 70)
SEA_TOP = (18, 23, 56)
SEA_BOT = (6, 8, 20)

MOON_COLOR = (255, 246, 218)
MOON_GLOW = (255, 230, 160)

BOAT_DARK = (45, 28, 16)
BOAT_WOOD = (82, 50, 28)
BOAT_LIGHT = (112, 70, 40)
ROWER_COAT = (30, 42, 70)
ROWER_HAT = (40, 52, 88)
SKIN = (210, 155, 115)
RIM_LIGHT = (255, 238, 190)
ROD_COLOR = (60, 38, 22)
LINE_COLOR = (255, 235, 175)

LANTERN_BODY = (40, 28, 18)
LANTERN_METAL = (65, 50, 38)
LANTERN_GLOW = (255, 190, 60)
LANTERN_CORE = (255, 255, 240)

STAR_GOLD = (255, 220, 100)
STAR_WHITE = (255, 255, 255)


# ---------------------------------------------------------------- drawing

def draw():
    cv = Canvas(W, H)
    
    # 1. Sky & Sea Background
    cv.set_bg(SKY_TOP, SKY_BOT)
    
    # Paint sea below horizon y = 670 with rich gradient
    def sea_fn(x, y):
        if y < 670:
            return None
        t = (y - 670) / 354.0
        r = int(SEA_TOP[0] + (SEA_BOT[0] - SEA_TOP[0]) * t)
        g = int(SEA_TOP[1] + (SEA_BOT[1] - SEA_TOP[1]) * t)
        b = int(SEA_TOP[2] + (SEA_BOT[2] - SEA_TOP[2]) * t)
        return ((r, g, b), 1.0)
    cv.paint_fn((0, 670, W, H), sea_fn)

    # Subtle horizon line
    cv.paint_fn((0, 668, W, 672), lambda x, y: ((65, 80, 140), 0.5 * cov(abs(y - 670) - 1)))

    # 2. Rich Starry Sky (star near moon upper-left edge moved to (640, 120))
    stars_data = [
        (100, 120, 4, 0.85), (260, 80, 5, 0.95), (410, 170, 3, 0.65),
        (180, 280, 4, 0.75), (80, 420, 3, 0.55), (330, 380, 5, 0.85),
        (490, 100, 4, 0.95), (600, 310, 3, 0.7), (160, 540, 3, 0.6),
        (430, 520, 4, 0.8), (280, 220, 3, 0.65), (560, 440, 4, 0.85),
        (640, 120, 3, 0.7), (850, 450, 4, 0.8), (940, 180, 3, 0.75),
    ]
    for (sx, sy, sr, sa) in stars_data:
        bb = (sx - sr * 4, sy - sr * 4, sx + sr * 4, sy + sr * 4)
        cv.paint_fn(bb, lambda x, y, cx=sx, cy=sy, r=sr, a=sa:
                    (STAR_WHITE, a * cov(d_circle(x, y, cx, cy, r))) if d_circle(x, y, cx, cy, r) < 1.2 else None)
        cv.paint(bb, lambda x, y, cx=sx, cy=sy, r=sr: d_segment(x, y, cx - r * 2.5, cy, cx + r * 2.5, cy) - 0.8, STAR_GOLD)
        cv.paint(bb, lambda x, y, cx=sx, cy=sy, r=sr: d_segment(x, y, cx, cy - r * 2.5, cx, cy + r * 2.5) - 0.8, STAR_GOLD)

    # 3. Giant Radiant Crescent Moon (Top Right) - Clean cream crescent with soft radial glow falloff (NO solid disc)
    mx, my, mr = 810, 230, 150
    m_glow_r = 240
    m_bb = (mx - m_glow_r, my - m_glow_r, mx + m_glow_r, my + m_glow_r)

    # Soft radial glow falloff (multiple faint halos fading with distance, no solid disc)
    def moon_glow_fn(x, y):
        d = HYPOT(x - mx, y - my)
        if d <= m_glow_r:
            t = d / m_glow_r
            alpha = (1.0 - t * t) * 0.18
            if alpha > 0.005:
                return (MOON_GLOW, alpha)
        return None
    cv.paint_fn(m_bb, moon_glow_fn)

    # Clean crisp crescent moon via boolean difference; cutout painted in exact SKY color
    def crescent_fn(x, y):
        d1 = d_circle(x, y, mx, my, mr)
        d2 = d_circle(x, y, mx - 58, my - 12, mr - 22)
        if d1 <= 0.75:
            if d2 < -0.75:
                # Cutout region: paint exact background sky color so no grey smudge appears
                return (cv.get_sky_color(x, y), 1.0)
            cov1 = cov(d1)
            cov2 = 1.0 if d2 > 0.75 else cov(-d2)
            alpha = min(cov1, cov2)
            if alpha > 0:
                return (MOON_COLOR, alpha)
        return None
    cv.paint_fn(m_bb, crescent_fn)

    # Soft horizontal sea shimmer under the moon (3-4 horizontal soft ellipses, fading as they go down)
    def sea_shimmer_fn(x, y):
        if y < 670 or y > 950:
            return None
        depth = (y - 670) / 280.0
        total_a = 0.0
        for sy_center, band_w, max_a in [
            (715, 60, 0.32),
            (785, 90, 0.22),
            (865, 130, 0.12),
        ]:
            if abs(y - sy_center) < band_w:
                dx = abs(x - mx)
                spread = 120 + (sy_center - 670) * 0.4
                if dx < spread:
                    wave = math.sin(x * 0.06 + sy_center * 0.1) * 0.5 + 0.5
                    factor = (1.0 - (dx / spread)) * (1.0 - abs(y - sy_center) / band_w) * wave * max_a
                    total_a += factor
        if total_a > 0.01:
            return (MOON_GLOW, min(total_a, 0.4))
        return None
    cv.paint_fn((mx - 220, 670, mx + 220, 960), sea_shimmer_fn)


    # 4. Wooden Rowboat (Bottom-Left / Centre)
    cv.paint((185, 670, 535, 755), lambda x, y: d_ellipse(x, y, 360, 714, 170, 44), BOAT_DARK)
    cv.paint((193, 676, 527, 748), lambda x, y: d_ellipse(x, y, 360, 710, 160, 38), BOAT_WOOD)
    cv.paint((205, 680, 515, 722), lambda x, y: d_ellipse(x, y, 360, 702, 142, 26), (15, 20, 38))
    cv.paint((193, 672, 527, 696), lambda x, y: d_ellipse(x, y, 360, 686, 160, 15), BOAT_LIGHT)

    # Water ripples around boat
    cv.paint((175, 705, 550, 740), lambda x, y: d_segment(x, y, 175, 720, 550, 720) - (2.2 + abs(math.sin(x * 0.09)) * 3.2), (30, 40, 75))


    # 5. Fisherman: clear silhouette (wide-brim hat, seated body, bent arm, warm rim-light on moon-facing edge)
    # Torso
    cv.paint((300, 595, 400, 700), lambda x, y: d_ellipse(x, y, 350, 650, 44, 58), ROWER_COAT)
    # Bent arm reaching forward towards rod base (360, 635)
    cv.paint((330, 620, 390, 670), lambda x, y: d_segment(x, y, 350, 640, 375, 630) - 10, ROWER_COAT)
    # Head & Wide-brim hat
    cv.paint((315, 525, 385, 605), lambda x, y: d_circle(x, y, 350, 565, 24), SKIN)
    cv.paint((300, 535, 400, 575), lambda x, y: d_ellipse(x, y, 350, 550, 42, 12), ROWER_HAT) # wide brim
    cv.paint((318, 515, 382, 560), lambda x, y: d_ellipse(x, y, 350, 538, 24, 16), ROWER_HAT) # crown

    # Thin warm rim-light on moon-facing (right) edge of fisherman to separate from dark sea
    def fisherman_rim_fn(x, y):
        d_hat = d_ellipse(x, y, 350, 550, 42, 12)
        d_head = d_circle(x, y, 350, 565, 24)
        d_coat = d_ellipse(x, y, 350, 650, 44, 58)
        is_right = (x > 350)
        if is_right:
            if -1.5 <= d_coat <= 1.5:
                return (RIM_LIGHT, 0.8 * cov(d_coat))
            if -1.5 <= d_head <= 1.5:
                return (RIM_LIGHT, 0.7 * cov(d_head))
            if -1.5 <= d_hat <= 1.5:
                return (RIM_LIGHT, 0.8 * cov(d_hat))
        return None
    cv.paint_fn((340, 510, 400, 710), fisherman_rim_fn)


    # 6. Actual Small Lantern sitting on boat deck (warm core, rounded-rectangle body, handle on top, tight ~70px max radius glow)
    lx, ly = 430, 685
    # TIGHT soft radial falloff with radius 35 (~70px max diameter)
    cv.paint_fn((lx - 40, ly - 45, lx + 40, ly + 25), lambda x, y: (LANTERN_GLOW, 0.35 * cov(d_circle(x, y, lx, ly - 5, 35))) if d_circle(x, y, lx, ly - 5, 35) < 0.75 else None)
    
    # Lantern physical body (rounded rectangle / stacked ellipses + handle)
    l_bb = (lx - 16, ly - 32, lx + 16, ly + 8)
    cv.paint(l_bb, lambda x, y: d_ellipse(x, y, lx, ly - 12, 11, 14), LANTERN_BODY)
    cv.paint(l_bb, lambda x, y: d_ellipse(x, y, lx, ly - 12, 7, 10), LANTERN_GLOW)
    cv.paint(l_bb, lambda x, y: d_circle(x, y, lx, ly - 12, 4), LANTERN_CORE)
    # Metal top cap & handle arc
    cv.paint((lx - 10, ly - 32, lx + 10, ly - 22), lambda x, y: d_ellipse(x, y, lx, ly - 27, 8, 3), LANTERN_METAL)
    cv.paint((lx - 8, ly - 38, lx + 8, ly - 27), lambda x, y: d_segment(x, y, lx - 7, ly - 27, lx + 7, ly - 27) - 1.5, LANTERN_METAL)


    # 7. Bucket with caught glowing stars inside boat (no grey circle)
    bx_b, by_b = 275, 695
    cv.paint((bx_b - 18, by_b - 15, bx_b + 18, by_b + 15), lambda x, y: d_ellipse(x, y, bx_b, by_b, 16, 12), (55, 45, 35))
    cv.paint((bx_b - 15, by_b - 15, bx_b + 15, by_b + 5), lambda x, y: d_ellipse(x, y, bx_b, by_b - 2, 13, 8), (20, 16, 14))
    for (csx, csy) in ((bx_b - 5, by_b - 4), (bx_b + 4, by_b - 6), (bx_b - 1, by_b - 8)):
        cv.paint((csx - 6, csy - 6, csx + 6, csy + 6), lambda x, y, cx=csx, cy=csy: d_circle(x, y, cx, cy, 4), STAR_GOLD)
        cv.paint_fn((csx - 10, csy - 10, csx + 10, csy + 10), lambda x, y, cx=csx, cy=csy: (STAR_GOLD, 0.4 * cov(d_circle(x, y, cx, cy, 9))) if d_circle(x, y, cx, cy, 9) < 0.75 else None)


    # 8. Fishing Rod and Arcing Fishing Line with Caught Star (NO grey circle behind caught star)
    rod_pts = [(360, 635), (410, 560), (460, 480)]
    cv.paint(bbox_of(rod_pts, 8), lambda x, y: d_polyline(x, y, rod_pts) - 3.5, ROD_COLOR)

    line_pts = bezier_pts((460, 480), (515, 360), (555, 275), (575, 250), 40)
    cv.paint(bbox_of(line_pts, 8), lambda x, y: d_polyline(x, y, line_pts) - 1.5, LINE_COLOR)

    # Caught star at (575, 250) - clean star with small soft halo, NO grey circle behind it
    star_cx, star_cy = 575, 250
    s_bb = (star_cx - 28, star_cy - 28, star_cx + 28, star_cy + 28)
    cv.paint_fn(s_bb, lambda x, y: (STAR_GOLD, 0.3 * cov(d_circle(x, y, star_cx, star_cy, 26))) if d_circle(x, y, star_cx, star_cy, 26) < 0.75 else None)
    cv.paint(s_bb, lambda x, y: d_circle(x, y, star_cx, star_cy, 8), STAR_WHITE)
    cv.paint(s_bb, lambda x, y: d_segment(x, y, star_cx - 20, star_cy, star_cx + 20, star_cy) - 1.5, STAR_WHITE)
    cv.paint(s_bb, lambda x, y: d_segment(x, y, star_cx, star_cy - 20, star_cx, star_cy + 20) - 1.5, STAR_WHITE)
    cv.paint(s_bb, lambda x, y: d_segment(x, y, star_cx - 14, star_cy - 14, star_cx + 14, star_cy + 14) - 1.0, STAR_GOLD)
    cv.paint(s_bb, lambda x, y: d_segment(x, y, star_cx - 14, star_cy + 14, star_cx + 14, star_cy - 14) - 1.0, STAR_GOLD)

    return cv


# ------------------------------------------------------------------- PNG

def write_png(cv, path):
    w, h = cv.w, cv.h
    raw = bytearray()
    rowlen = w * 3
    for y in range(h):
        raw.append(0)
        raw += cv.px[y * rowlen:(y + 1) * rowlen]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Space Slate Theme - logo candidate generator (code-drawn with PIL).

Run from the project root:
    python3 scripts/generate-logo-candidates.py

Outputs (relative paths only - avoids the Windows non-ASCII path OSError in PIL):
    assets/logo-candidates/<nn>-<slug>.png  512x512 RGBA, transparent background
    assets/logo-candidates/contact-light.png
    assets/logo-candidates/contact-dark.png
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

OUT_DIR = "assets/logo-candidates"
ICON_OUT = "assets/icon.png"
SELECTED = "04-comet"   # candidate adopted as the extension icon
BASE = 512          # exported size
SS = 4              # supersample factor (render 2048 then downscale)

# ---------------------------------------------------------------- palette ----
INK = (23, 21, 34, 255)        # #171522  editor background (dark)
INK_SOFT = (41, 39, 51, 255)   # #292733  side bar (dark)
SLATE_DK = (68, 66, 78, 255)   # #44424E  deep slate
SLATE = (108, 108, 108, 255)   # #6C6C6C  slate (light theme accent)
SLATE_MID = (138, 138, 148, 255)
SLATE_LT = (194, 194, 194, 255)  # #C2C2C2  light slate
LAV = (228, 226, 239, 255)     # #E4E2EF  activity bar
LAV_LT = (240, 238, 252, 255)  # #F0EEFC  editor background (light)
WHITE = (246, 246, 246, 255)   # #F6F6F6
SAGE = (179, 191, 122, 255)    # #B3BF7A
TEAL = (135, 187, 194, 255)    # #87BBC2
PINK = (211, 147, 175, 255)    # #D393AF
AMBER = (223, 192, 136, 255)   # #DFC088

CANDIDATES = []


def candidate(fn):
    CANDIDATES.append(fn)
    return fn


# ---------------------------------------------------------------- helpers ----
def new_layer(size):
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def circle_mask(size, cx, cy, r):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def disc(size, color):
    return Image.new("RGBA", (size, size), color)


def sparkle(cx, cy, r, inner=0.24, points=4, rot=-math.pi / 2):
    """4-point star (sparkle) polygon vertices."""
    pts = []
    for i in range(points * 2):
        a = rot + i * math.pi / points
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def quad_bezier(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def rotated(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


# ------------------------------------------------------------ candidates ----
@candidate
def orbit_slate(S):
    """A slate planet with a tilted orbit ring and a distant moon."""
    img = new_layer(S)
    cx, cy = S * 0.50, S * 0.52
    R = S * 0.215
    rx, ry, rw, ang = S * 0.385, S * 0.135, S * 0.045, 20.0

    ring = new_layer(S)
    ImageDraw.Draw(ring).ellipse(
        [cx - rx, cy - ry, cx + rx, cy + ry], outline=SLATE_DK, width=int(rw)
    )
    ring = ring.rotate(ang, resample=Image.BICUBIC, center=(cx, cy))
    front = ring.copy()
    fm = Image.new("L", (S, S), 0)
    ImageDraw.Draw(fm).rectangle([0, cy, S, S], fill=255)
    front.putalpha(ImageChops.multiply(front.getchannel("A"), fm))
    img.alpha_composite(ring)

    pm = circle_mask(S, cx, cy, R)
    img.alpha_composite(Image.composite(disc(S, SLATE), new_layer(S), pm))
    sm = circle_mask(S, cx, cy + R * 0.42, R)
    shadow = new_layer(S)
    ImageDraw.Draw(shadow).ellipse(
        [cx - R, cy + R * 0.42 - R, cx + R, cy + R * 0.42 + R], fill=(23, 21, 34, 150)
    )
    img.alpha_composite(
        Image.composite(shadow, new_layer(S), ImageChops.multiply(pm, sm))
    )

    moon = rotated([(cx + rx * math.cos(math.radians(28)),
                     cy + ry * math.sin(math.radians(28)))], cx, cy, -ang)[0]
    mm = circle_mask(S, moon[0], moon[1], S * 0.052)
    img.alpha_composite(Image.composite(disc(S, AMBER), new_layer(S), mm))
    img.alpha_composite(front)
    return img


@candidate
def strata_tile(S):
    """A dark slate tile with stacked strata bands and a spark."""
    img = new_layer(S)
    tile = [S * 0.155, S * 0.155, S * 0.845, S * 0.845]
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(tile, radius=S * 0.20, fill=INK)

    x0, x1 = S * 0.255, S * 0.745
    d.rounded_rectangle([x0, S * 0.545, x1, S * 0.655], radius=S * 0.021, fill=SLATE_LT)
    d.rounded_rectangle([x0, S * 0.688, x1, S * 0.762], radius=S * 0.018, fill=SLATE)
    d.rounded_rectangle([x0, S * 0.790, x1 - S * 0.145, S * 0.838], radius=S * 0.014,
                        fill=SLATE_DK)
    d.polygon(sparkle(S * 0.395, S * 0.365, S * 0.115), fill=AMBER)
    d.polygon(sparkle(S * 0.585, S * 0.285, S * 0.052), fill=WHITE)
    return img


@candidate
def constellation_disc(S):
    """A star disc: ink circle with an abstract constellation and an orbit arc."""
    img = new_layer(S)
    cx, cy, R = S * 0.50, S * 0.50, S * 0.325
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=INK)
    d.arc([cx - S * 0.390, cy - S * 0.390, cx + S * 0.390, cy + S * 0.390],
          start=-38, end=196, fill=SLATE, width=int(S * 0.038))

    nodes = [(0.325, 0.335), (0.470, 0.255), (0.655, 0.380),
             (0.700, 0.620), (0.470, 0.720), (0.290, 0.600)]
    pts = [(S * x, S * y) for x, y in nodes]
    for a, b in [(0, 1), (1, 2), (3, 4), (4, 5), (5, 0), (2, 3)]:
        d.line([pts[a], pts[b]], fill=SLATE_DK, width=int(S * 0.026))
    for i, (px, py) in enumerate(pts):
        r = S * (0.052 if i in (1, 4) else 0.038)
        d.ellipse([px - r, py - r, px + r, py + r], fill=WHITE if i != 4 else SLATE_LT)
    d.polygon(sparkle(S * 0.470, S * 0.470, S * 0.135), fill=AMBER)
    return img


@candidate
def comet(S):
    """A comet: slate spark with a tapering twin tail across the frame."""
    img = new_layer(S)
    head = (S * 0.665, S * 0.325)

    def tail(p0, p1, p2, w0, power, t_end=1.0, steps=44):
        up, dn = [], []
        for i in range(steps + 1):
            t = (i / steps) * t_end
            px, py = quad_bezier(p0, p1, p2, t)
            tx, ty = quad_bezier(p0, p1, p2, min(1.0, t + 0.02))
            vx, vy = tx - px, ty - py
            n = math.hypot(vx, vy) or 1.0
            nx, ny = -vy / n, vx / n
            w = w0 * max(0.06, (1 - t) ** power)
            up.append((px + nx * w, py + ny * w))
            dn.append((px - nx * w, py - ny * w))
        return up + dn[::-1]

    d = ImageDraw.Draw(img)
    p0, p1, p2 = (S * 0.605, S * 0.395), (S * 0.450, S * 0.620), (S * 0.150, S * 0.850)
    d.polygon(tail(p0, p1, p2, S * 0.098, 1.5), fill=SLATE)
    d.polygon(tail((p0[0] + S * 0.055, p0[1] - S * 0.030),
                   (p1[0] + S * 0.030, p1[1] - S * 0.055),
                   (p2[0] + S * 0.030, p2[1] - S * 0.055), S * 0.040, 1.6,
                   t_end=0.84), fill=SLATE_MID)
    d.polygon(sparkle(head[0], head[1], S * 0.185), fill=SLATE_LT)
    d.polygon(sparkle(S * 0.845, S * 0.185, S * 0.062), fill=AMBER)
    return img


@candidate
def shard(S):
    """A faceted slate shard with a spark accent."""
    img = new_layer(S)
    cx, cy = S * 0.47, S * 0.52
    K = S * 1.0
    raw = [(0.00, -0.345), (0.175, -0.120), (0.165, 0.170),
           (0.00, 0.355), (-0.165, 0.170), (-0.175, -0.120)]
    poly = rotated([(cx + x * K, cy + y * K) for x, y in raw], cx, cy, 16)
    d = ImageDraw.Draw(img)
    d.polygon(poly, fill=SLATE)
    left = [poly[3], poly[4], poly[5], poly[0], (cx, cy)]
    right = [poly[0], poly[1], poly[2], poly[3], (cx, cy)]
    d.polygon(left, fill=SLATE_LT)
    d.polygon(right, fill=SLATE_MID)
    tip = [poly[2], poly[3], poly[4], (cx, cy)]
    d.polygon(tip, fill=SLATE_DK)
    d.polygon(sparkle(S * 0.775, S * 0.235, S * 0.098), fill=AMBER)
    return img


@candidate
def orbit_arcs(S):
    """Concentric orbit arcs with a travelling node."""
    img = new_layer(S)
    d = ImageDraw.Draw(img)
    cx, cy = S * 0.50, S * 0.50
    specs = [(0.355, -150, 118, SLATE),
             (0.268, 30, 250, SLATE_MID),
             (0.183, 150, 402, SLATE_LT)]
    for r, a0, a1, col in specs:
        d.arc([cx - S * r, cy - S * r, cx + S * r, cy + S * r],
              start=a0, end=a1, fill=col, width=int(S * 0.052))
    node = (cx + S * 0.355 * math.cos(math.radians(-150)),
            cy + S * 0.355 * math.sin(math.radians(-150)))
    nr = S * 0.078
    d.ellipse([node[0] - nr, node[1] - nr, node[0] + nr, node[1] + nr], fill=AMBER)
    d.polygon(sparkle(cx, cy, S * 0.118), fill=WHITE)
    return img


# ------------------------------------------------------------------ export ---
def render(fn, target=0.72):
    """Render at SS scale, downscale, then optically center: crop to content,
    fit its longer side to `target` of the canvas and re-center it."""
    big = fn(BASE * SS)
    small = big.resize((BASE, BASE), Image.LANCZOS)
    bbox = small.getbbox()
    if not bbox:
        return small
    content = small.crop(bbox)
    w, h = content.size
    scale = (BASE * target) / max(w, h)
    content = content.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                             Image.LANCZOS)
    out = new_layer(BASE)
    out.alpha_composite(content, ((BASE - content.width) // 2,
                                  (BASE - content.height) // 2))
    return out


def load_font(size, bold=True):
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf",
                                                                         "arial.ttf"]
    for n in names:
        path = os.path.join("C:/Windows/Fonts", n)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def contact_sheet(items, bg, out_path):
    cell, gap, pad, label_h = 232, 26, 30, 78
    cols, rows = 3, 2
    W = pad * 2 + cols * cell + (cols - 1) * gap
    H = pad * 2 + rows * (cell + label_h) + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    f_name = load_font(23)
    f_small = load_font(15)
    light_bg = sum(bg) > 380
    ink = (38, 37, 45) if light_bg else (240, 238, 252)
    dim = (120, 118, 132) if light_bg else (150, 148, 162)
    for i, (slug, img) in enumerate(items):
        c, r = i % cols, i // cols
        x = pad + c * (cell + gap)
        y = pad + r * (cell + label_h + gap)
        thumb = img.resize((cell, cell), Image.LANCZOS)
        sheet.paste(thumb, (x, y), thumb)
        # 32px legibility chip in the cell corner
        chip = 40
        d.rounded_rectangle([x + cell - chip, y + 2, x + cell - 2, y + chip + 2],
                            radius=9, fill=(255, 255, 255) if light_bg else (32, 30, 42))
        tiny = img.resize((32, 32), Image.LANCZOS)
        sheet.paste(tiny, (x + cell - chip + 4, y + 6), tiny)
        d.text((x + 1, y + cell + 8), f"{i + 1:02d}  {slug.split('-')[1]}", font=f_name,
               fill=ink)
        d.text((x + 1, y + cell + 44), f"{slug} - 512px", font=f_small, fill=dim)
    sheet.save(out_path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    items = []
    for i, fn in enumerate(CANDIDATES, start=1):
        img = render(fn)
        name = f"{i:02d}-{fn.__name__.replace('_', '-')}"
        path = f"{OUT_DIR}/{name}.png"
        img.save(path)
        for px in (256, 128):
            img.resize((px, px), Image.LANCZOS).save(f"{OUT_DIR}/{name}-{px}.png")
        bbox = img.getbbox()
        lo, hi = int(BASE * 0.085), int(BASE * 0.915)
        ok = bbox and bbox[0] >= lo and bbox[1] >= lo and bbox[2] <= hi and bbox[3] <= hi
        print(f"{path:52s} bbox={bbox} margins_ok={bool(ok)}")
        items.append((name, img))
    contact_sheet(items, (240, 238, 252), f"{OUT_DIR}/contact-light.png")
    contact_sheet(items, (23, 21, 34), f"{OUT_DIR}/contact-dark.png")
    print(f"wrote {OUT_DIR}/contact-light.png and contact-dark.png")

    chosen = dict(items).get(SELECTED)
    if chosen is not None:
        chosen.save(ICON_OUT)
        print(f"extension icon -> {ICON_OUT}  (from {SELECTED})")


if __name__ == "__main__":
    main()

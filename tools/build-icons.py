"""Generate favicon + app icons (192/512/maskable/apple-touch/favicon.ico).

Usage: python tools/build-icons.py <site_dir> --carry malzahar --tank ekko --glyph tools/glyph.png [--carry-align 0.9] [--tank-align 0.5]
  --carry/--tank  unit keys; art read from assets/units/<key>.webp|.png (wide splash or square)
  --glyph         white-on-black PNG of the comp's trait symbol (render an SVG with headless Edge if needed)
  --colors        two hex colors for the plan tints, e.g. --colors b98bff ff5fae
"""
import sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

import argparse
ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--carry", required=True); ap.add_argument("--tank", required=True)
ap.add_argument("--glyph", required=True); ap.add_argument("--carry-align", type=float, default=0.5); ap.add_argument("--tank-align", type=float, default=0.5)
ap.add_argument("--colors", nargs=2, default=["b98bff", "ff5fae"])
ARGS = ap.parse_args()
root = ARGS.root
A = lambda *p: os.path.join(root, *p)
out = A("assets", "icons"); os.makedirs(out, exist_ok=True)

TEAL = tuple(int(ARGS.colors[0][i:i+2], 16) for i in (0, 2, 4)); RED = tuple(int(ARGS.colors[1][i:i+2], 16) for i in (0, 2, 4)); GOLD = (245, 196, 81); BG = (11, 15, 23)

def glyph_mask(size):
    """Crisp mask of the trait glyph (white on black PNG given by --glyph)."""
    g = Image.open(os.path.abspath(ARGS.glyph)).convert("L")
    return g.resize((size, size), Image.LANCZOS).point(lambda v: 255 if v > 128 else int(v * 2 * 0.5))

def diag_gradient(s, c1, c2):
    im = Image.new("RGB", (s, s))
    px = im.load()
    for y in range(s):
        for x in range(s):
            t = (x + y) / (2 * s - 2)
            px[x, y] = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
    return im

def unit_art(key):
    for ext in (".webp", ".png", ".jpg"):
        p = A("assets", "units", key + ext)
        if os.path.exists(p): return Image.open(p).convert("RGB")
    return Image.open(A("assets", "units-sq", key + ".png")).convert("RGB")

def crop_sq(im, align=0.5):
    w, h = im.size
    x = int((w - h) * align)
    return im.crop((x, 0, x + h, h))

def art_icon(s, maskable=False):
    """Split Pebbles / Brambleback art with a glowing glyph medallion."""
    peb = crop_sq(unit_art(ARGS.carry), ARGS.carry_align).resize((s, s), Image.LANCZOS)
    bra = crop_sq(unit_art(ARGS.tank), ARGS.tank_align).resize((s, s), Image.LANCZOS)
    # diagonal split mask (top-left = carry)
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (s, 0), (0, s)], fill=255)
    base = Image.composite(peb, bra, m)
    # tint halves toward plan colors
    tint = Image.composite(Image.new("RGB", (s, s), TEAL), Image.new("RGB", (s, s), RED), m)
    base = Image.blend(base, tint, 0.18)
    base = ImageEnhance.Contrast(ImageEnhance.Brightness(base).enhance(0.72)).enhance(1.25)
    base = ImageEnhance.Color(base).enhance(1.35)
    # darken toward center so the medallion pops
    vign = Image.new("L", (s, s), 0)
    ImageDraw.Draw(vign).ellipse([s * .18, s * .18, s * .82, s * .82], fill=150)
    vign = vign.filter(ImageFilter.GaussianBlur(s * .08))
    base = Image.composite(Image.new("RGB", (s, s), BG), base, vign)
    # gold split line
    d = ImageDraw.Draw(base)
    d.line([(s, 0), (0, s)], fill=GOLD, width=max(2, s // 64))
    # medallion
    r = s * (0.27 if maskable else 0.31)
    cx = cy = s / 2
    glow = Image.new("L", (s, s), 0)
    ImageDraw.Draw(glow).ellipse([cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25], fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(s * .05))
    base = Image.composite(Image.new("RGB", (s, s), GOLD), base, glow.point(lambda v: v // 3))
    d = ImageDraw.Draw(base)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BG, outline=GOLD, width=max(2, s // 48))
    gs = int(r * 1.35)
    gm = glyph_mask(gs)
    gfill = diag_gradient(gs, (225, 200, 255), (255, 190, 225))
    base.paste(gfill, (int(cx - gs / 2), int(cy - gs / 2 + gs * .02)), gm)
    return base

def rounded(im, radius_frac=0.22):
    s = im.size[0]
    m = Image.new("L", (s * 4, s * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, s * 4 - 1, s * 4 - 1], radius=int(s * 4 * radius_frac), fill=255)
    m = m.resize((s, s), Image.LANCZOS)
    o = im.convert("RGBA"); o.putalpha(m); return o

def fav(s):
    """Small favicon: glyph on teal→red gradient tile."""
    bg = diag_gradient(s * 4, (110, 50, 220), (200, 40, 120)).resize((s, s), Image.LANCZOS)
    gs = int(s * .78)
    gm = glyph_mask(gs)
    bg.paste(Image.new("RGB", (gs, gs), (255, 255, 255)), ((s - gs) // 2, (s - gs) // 2), gm)
    return rounded(bg, .24)

big = art_icon(1024)
big.resize((512, 512), Image.LANCZOS).save(os.path.join(out, "icon-512.png"))
big.resize((192, 192), Image.LANCZOS).save(os.path.join(out, "icon-192.png"))
big.resize((180, 180), Image.LANCZOS).save(os.path.join(out, "apple-touch-icon.png"))
art_icon(1024, maskable=True).resize((512, 512), Image.LANCZOS).save(os.path.join(out, "icon-maskable-512.png"))
rounded(big.resize((256, 256), Image.LANCZOS)).save(os.path.join(out, "icon-256-rounded.png"))
for s in (16, 32, 48):
    fav(s).save(os.path.join(out, f"favicon-{s}.png"))
fav(64).save(A("favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print("icons ok")

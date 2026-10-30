"""Generate a KDP-ready demo coloring book: interior PDF + full-wrap cover PDF.

Specs (Amazon KDP paperback, US):
  - Trim 8.5" x 11", no bleed on interior, black ink, white paper
  - Single-sided designs (blank backs) so markers don't bleed through
  - Cover = back + spine + front with 0.125" bleed on every edge
"""
import math
import random

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

TRIM_W, TRIM_H = 8.5 * inch, 11 * inch
MARGIN = 0.75 * inch           # safe area (KDP minimum is 0.375" inside / 0.25" outside)
BLEED = 0.125 * inch
SPINE_PER_PAGE = 0.002252 * inch  # white paper, black ink
TITLE = "Calm Mandalas"
SUBTITLE = "A Mini Coloring Book for Relaxation"
AUTHOR = "Your Pen Name"


# ---------- pattern primitives ----------

def petal_path(c, r_in, r_out, half_angle, pointed=True):
    p = c.beginPath()
    p.moveTo(r_in, 0)
    a = math.radians(half_angle)
    mid = (r_in + r_out) / 2
    p.curveTo(mid, mid * math.tan(a), r_out * 0.9, r_out * math.tan(a) * (0.3 if pointed else 0.8),
              r_out, 0)
    p.curveTo(r_out * 0.9, -r_out * math.tan(a) * (0.3 if pointed else 0.8), mid, -mid * math.tan(a),
              r_in, 0)
    p.close()
    return p


def ring_of(c, n, draw):
    for i in range(n):
        c.saveState()
        c.rotate(360 / n * i)
        draw(i)
        c.restoreState()


def mandala(c, cx, cy, R, rng):
    c.saveState()
    c.translate(cx, cy)
    c.setLineWidth(1.6)
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.circle(0, 0, R, stroke=1, fill=0)
    radii = sorted(rng.sample([i / 12 for i in range(2, 12)], 5))
    radii = [r * R for r in radii] + [R]
    prev = R * 0.08
    c.circle(0, 0, prev, stroke=1, fill=0)
    for k, r in enumerate(radii):
        n = rng.choice([8, 10, 12, 16, 18, 24])
        style = rng.choice(["petal", "round", "dots", "arch", "double"])
        half = 180 / n * rng.uniform(0.7, 1.0)
        if style in ("petal", "round"):
            ring_of(c, n, lambda i: c.drawPath(petal_path(c, prev, r, half, style == "petal"), stroke=1, fill=0))
        elif style == "double":
            ring_of(c, n, lambda i: c.drawPath(petal_path(c, prev, r, half, True), stroke=1, fill=0))
            ring_of(c, n, lambda i: c.drawPath(petal_path(c, prev + (r - prev) * 0.25, r * 0.85, half * 0.5, True), stroke=1, fill=0))
        elif style == "dots":
            dr = min((r - prev) / 2, math.pi * (prev + r) / 2 / n) * 0.8
            ring_of(c, n, lambda i: c.circle((prev + r) / 2, 0, dr, stroke=1, fill=0))
        elif style == "arch":
            def arch(i):
                p = c.beginPath()
                a = math.radians(180 / n)
                p.moveTo(prev * math.cos(-a), prev * math.sin(-a))
                p.curveTo(r * math.cos(-a), r * math.sin(-a) * 0.6, r * math.cos(a), r * math.sin(a) * 0.6,
                          prev * math.cos(a), prev * math.sin(a))
                c.drawPath(p, stroke=1, fill=0)
            ring_of(c, n, arch)
        c.circle(0, 0, r, stroke=1, fill=0)
        prev = r
    # outer flourish
    n = rng.choice([12, 16, 20])
    ring_of(c, n, lambda i: c.drawPath(petal_path(c, R, R * 1.12, 180 / n * 0.8, True), stroke=1, fill=0))
    c.restoreState()


def hex_pattern(c, x0, y0, w, h, rng):
    c.saveState()
    clip = c.beginPath(); clip.rect(x0, y0, w, h); c.clipPath(clip, stroke=0)
    s = rng.choice([0.45, 0.55, 0.65]) * inch
    dx, dy = 1.5 * s, math.sqrt(3) * s
    c.setLineWidth(1.4)
    col = 0
    x = x0 - s
    while x < x0 + w + s:
        y = y0 - dy + (dy / 2 if col % 2 else 0)
        while y < y0 + h + dy:
            pts = [(x + s * math.cos(math.radians(60 * k)), y + s * math.sin(math.radians(60 * k))) for k in range(6)]
            p = c.beginPath(); p.moveTo(*pts[0])
            for q in pts[1:]: p.lineTo(*q)
            p.close(); c.drawPath(p, stroke=1, fill=0)
            inner = rng.choice(["star", "circle", "flower", "none"])
            if inner == "circle":
                c.circle(x, y, s * 0.5, stroke=1, fill=0)
            elif inner == "star":
                p = c.beginPath()
                for k in range(12):
                    rr = s * (0.7 if k % 2 == 0 else 0.35)
                    a = math.radians(30 * k)
                    (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
                p.close(); c.drawPath(p, stroke=1, fill=0)
            elif inner == "flower":
                c.saveState(); c.translate(x, y)
                ring_of(c, 6, lambda i: c.drawPath(petal_path(c, s * 0.1, s * 0.75, 22, False), stroke=1, fill=0))
                c.restoreState()
            y += dy
        x += dx
        col += 1
    c.restoreState()
    c.setLineWidth(2); c.rect(x0, y0, w, h, stroke=1, fill=0)


def truchet(c, x0, y0, w, h, rng):
    c.saveState()
    s = rng.choice([0.6, 0.75]) * inch
    cols, rows = int(w // s), int(h // s)
    ox, oy = x0 + (w - cols * s) / 2, y0 + (h - rows * s) / 2
    c.setLineWidth(1.4)
    for i in range(cols):
        for j in range(rows):
            x, y = ox + i * s, oy + j * s
            if rng.random() < 0.5:
                c.arc(x - s / 2, y - s / 2, x + s / 2, y + s / 2, 0, 90)
                c.arc(x + s / 2, y + s / 2, x + 3 * s / 2, y + 3 * s / 2, 180, 90)
            else:
                c.arc(x + s / 2, y - s / 2, x + 3 * s / 2, y + s / 2, 90, 90)
                c.arc(x - s / 2, y + s / 2, x + s / 2, y + 3 * s / 2, 270, 90)
            c.circle(x + s / 2, y + s / 2, s * 0.12, stroke=1, fill=0)
    c.setLineWidth(2); c.rect(ox, oy, cols * s, rows * s, stroke=1, fill=0)
    c.restoreState()


def corner_mandalas(c, x0, y0, w, h, rng):
    """One big mandala plus four quarter-mandalas in the corners."""
    c.saveState()
    clip = c.beginPath(); clip.rect(x0, y0, w, h); c.clipPath(clip, stroke=0)
    for (cx, cy) in [(x0, y0), (x0 + w, y0), (x0, y0 + h), (x0 + w, y0 + h)]:
        mandala(c, cx, cy, w * 0.28, random.Random(rng.random()))
    c.restoreState()
    mandala(c, x0 + w / 2, y0 + h / 2, w * 0.36, rng)
    c.setLineWidth(2); c.rect(x0, y0, w, h, stroke=1, fill=0)


# ---------- pages ----------

def centered(c, text, y, size, font="Helvetica-Bold"):
    c.setFont(font, size)
    c.drawCentredString(TRIM_W / 2, y, text)


def build_interior(path, n_designs=12, seed=7):
    rng = random.Random(seed)
    c = canvas.Canvas(path, pagesize=(TRIM_W, TRIM_H))
    c.setTitle(f"{TITLE} - Interior"); c.setAuthor(AUTHOR)

    # 1. Title page
    centered(c, TITLE, TRIM_H * 0.62, 44)
    centered(c, SUBTITLE, TRIM_H * 0.62 - 40, 18, "Helvetica")
    centered(c, AUTHOR, TRIM_H * 0.35, 14, "Helvetica")
    c.showPage()
    # 2. Copyright page
    c.setFont("Helvetica", 10)
    lines = [f"{TITLE}: {SUBTITLE}", f"Copyright © 2026 {AUTHOR}. All rights reserved.",
             "No part of this book may be reproduced without written permission,",
             "except for personal, non-commercial colouring use.", "",
             "Independently published.", "ISBN: (free KDP ISBN will be assigned at upload)"]
    for i, ln in enumerate(lines):
        c.drawString(MARGIN, MARGIN + 120 - i * 14, ln)
    c.showPage()
    # 3. Colour test page + 4. its blank back
    centered(c, "Color Test Page", TRIM_H - MARGIN - 30, 24)
    c.setFont("Helvetica", 11)
    c.drawCentredString(TRIM_W / 2, TRIM_H - MARGIN - 52, "Try your pens, pencils and markers here before you start.")
    c.setLineWidth(1.2)
    for r in range(8):
        for q in range(5):
            c.circle(MARGIN + 0.7 * inch + q * 1.4 * inch, TRIM_H - MARGIN - 1.6 * inch - r * 1.05 * inch, 0.42 * inch)
    c.showPage(); c.showPage()

    makers = [mandala] * 6 + [hex_pattern, truchet, corner_mandalas] * 2
    rng.shuffle(makers)
    for k in range(n_designs):
        maker = makers[k % len(makers)]
        w, h = TRIM_W - 2 * MARGIN, TRIM_H - 2 * MARGIN
        if maker is mandala:
            mandala(c, TRIM_W / 2, TRIM_H / 2, (w / 2) * 0.88, rng)
        else:
            maker(c, MARGIN, MARGIN, w, h, rng)
        c.showPage()
        # blank back side, with a tiny note (common in coloring books)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(TRIM_W / 2, MARGIN / 2, "This page intentionally left blank to prevent bleed-through.")
        c.showPage()

    # Closing page
    centered(c, "Thank you for coloring!", TRIM_H * 0.55, 26)
    c.setFont("Helvetica", 12)
    c.drawCentredString(TRIM_W / 2, TRIM_H * 0.55 - 30, "If you enjoyed this book, a short review on Amazon helps a lot.")
    c.showPage()
    pages = 4 + 2 * n_designs + 1
    if pages % 2:
        c.showPage(); pages += 1
    c.save()
    return pages


def build_cover(path, pages, seed=11):
    spine = pages * SPINE_PER_PAGE
    W = BLEED + TRIM_W + spine + TRIM_W + BLEED
    H = BLEED + TRIM_H + BLEED
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(f"{TITLE} - Cover")
    bg, accent = HexColor("#2E3A59"), HexColor("#F2C14E")
    c.setFillColor(bg); c.rect(0, 0, W, H, stroke=0, fill=1)

    front_x = BLEED + TRIM_W + spine
    # front: coloured mandala preview
    c.saveState()
    c.setFillColor(HexColor("#FFF8E7")); c.circle(front_x + TRIM_W / 2, BLEED + TRIM_H * 0.45, TRIM_W * 0.40, stroke=0, fill=1)
    c.restoreState()
    mandala(c, front_x + TRIM_W / 2, BLEED + TRIM_H * 0.45, TRIM_W * 0.34, random.Random(seed))
    c.setFillColor(accent); c.setFont("Helvetica-Bold", 54)
    c.drawCentredString(front_x + TRIM_W / 2, BLEED + TRIM_H - 1.6 * inch, TITLE)
    c.setFillColor(white); c.setFont("Helvetica", 22)
    c.drawCentredString(front_x + TRIM_W / 2, BLEED + TRIM_H - 2.1 * inch, SUBTITLE)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(front_x + TRIM_W / 2, BLEED + 0.9 * inch, "12 Unique Single-Sided Designs  •  8.5 x 11 in")
    c.setFont("Helvetica", 14)
    c.drawCentredString(front_x + TRIM_W / 2, BLEED + 0.55 * inch, AUTHOR)

    # back: blurb + barcode area (KDP places the barcode bottom-right, 2" x 1.2")
    bx = BLEED + 0.75 * inch
    c.setFillColor(accent); c.setFont("Helvetica-Bold", 22)
    c.drawString(bx, BLEED + TRIM_H - 1.5 * inch, "Slow down. Breathe. Color.")
    c.setFillColor(white); c.setFont("Helvetica", 13)
    blurb = ["Inside you'll find 12 original mandala and pattern designs,",
             "each printed on its own page so markers won't bleed through.",
             "", "• Large 8.5 x 11 inch pages", "• Designs from simple to detailed",
             "• A color test page to try your supplies", "• A thoughtful gift for adults and teens"]
    for i, ln in enumerate(blurb):
        c.drawString(bx, BLEED + TRIM_H - 2.1 * inch - i * 20, ln)
    c.setFillColor(white)
    c.rect(BLEED + TRIM_W - 0.25 * inch - 2 * inch, BLEED + 0.25 * inch, 2 * inch, 1.2 * inch, stroke=0, fill=1)
    c.setFillColor(HexColor("#888888")); c.setFont("Helvetica", 8)
    c.drawCentredString(BLEED + TRIM_W - 1.25 * inch, BLEED + 0.8 * inch, "barcode area (KDP adds)")

    # spine guides are omitted: KDP only allows spine text above 79 pages
    c.save()
    return W / inch, H / inch, spine / inch


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    pages = build_interior(f"{out}/interior.pdf")
    w, h, s = build_cover(f"{out}/cover.pdf", pages)
    print(f"interior pages: {pages}; cover {w:.3f} x {h:.3f} in; spine {s:.4f} in")

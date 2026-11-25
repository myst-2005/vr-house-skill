"""Paint coconut-palm frond textures (RGBA, leaflets on transparent ground): green and dry."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

random.seed(11)
W, H = 2048, 512
OUT = r"D:\Kochi-Residence-Interior\video\blender\ph\tex"


def frond(path, base, dry=False):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = H / 2
    x = 120
    while x < W - 40:
        t = x / W
        L = (H / 2 - 12) * (1.0 - 0.62 * t ** 1.4) * random.uniform(0.86, 1.0)
        wid = 13 * (1 - 0.4 * t) + random.uniform(-2, 2)
        for side in (-1, 1):
            ang = math.radians(random.uniform(48, 62))          # leaflets lean toward the tip
            tipx = x + L * math.cos(ang)
            tipy = cy + side * L * math.sin(ang)
            droop = random.uniform(-0.12, 0.12) * L
            mx, my = (x + tipx) / 2 + droop * 0.3, (cy + tipy) / 2
            nx, ny = -math.sin(ang) * wid / 2, side * math.cos(ang) * wid / 2
            v = random.uniform(-14, 14)
            c = tuple(max(0, min(255, int(ch + v * (1.2 if i == 1 else 0.8)))) for i, ch in enumerate(base)) + (255,)
            if dry and random.random() < 0.25:
                continue                                          # dry fronds have gaps
            d.polygon([(x, cy), (mx + nx, my + ny), (tipx, tipy), (mx - nx, my - ny)], fill=c)
            hl = tuple(min(255, ch + 22) for ch in c[:3]) + (255,)
            d.line([(x, cy), (tipx, tipy)], fill=hl, width=2)     # midrib of the leaflet
        x += random.uniform(15, 21)
    # rachis (the frond's stem), thick at the base
    for i in range(0, W, 4):
        t = i / W
        r = 9 * (1 - 0.8 * t) + 2
        col = (150, 140, 90, 255) if not dry else (140, 112, 70, 255)
        d.ellipse([i - r, cy - r, i + r, cy + r], fill=col)
    img = img.filter(ImageFilter.SMOOTH)
    img.save(path)
    print("saved", path)


frond(OUT + r"\palm_frond_green.png", (62, 104, 40))
frond(OUT + r"\palm_frond_yellow.png", (104, 120, 46))
frond(OUT + r"\palm_frond_dry.png", (128, 98, 58), dry=True)

"""Technical sheets for Option B, drawn on a copy of the furniture layout.

usage: python mep_sheets.py <E1|L1|P1>
E1 = electrical & switchboards, L1 = lighting & false ceiling, P1 = flooring & plumbing.
Plan coordinates are building-local (outer SW corner 0,0); GF origin (1200,1500), FF origin (16200,1500).
"""
import math
import os
import sys
import time

from pyautocad import Autocad, APoint, aDouble

ROOT = r"D:\Kochi-Residence-Interior"
BASE = os.path.join(ROOT, "Kochi-Residence_Option-B_Furniture-Layout.dwg")
SHEET = sys.argv[1].upper()
NAMES = {"E1": "Kochi-Residence_Option-B_E1_Electrical-Layout",
         "L1": "Kochi-Residence_Option-B_L1_Lighting-Ceiling",
         "P1": "Kochi-Residence_Option-B_P1_Flooring-Plumbing"}
GF, FF = (1200.0, 1500.0), (16200.0, 1500.0)
NOTE_X, NOTE_Y = 28390.0, 16088.0


def retry(fn, tries=30):
    for _ in range(tries):
        try:
            return fn()
        except Exception as e:
            if "rejected" not in str(e).lower():
                raise
            time.sleep(1)
    sys.exit("AutoCAD stayed busy. Press Esc in AutoCAD and run again.")


acad = Autocad(create_if_not_exists=False)
app = acad.app
def _close_old():                                   # drop any open copy of this sheet
    for i in reversed(range(app.Documents.Count)):
        d = app.Documents.Item(i)
        if d.Name.lower().startswith(NAMES[SHEET].lower()):
            d.Close(False)


retry(_close_old)
doc = retry(lambda: app.Documents.Open(BASE))
time.sleep(2)
try:
    doc.Activate()
except Exception:
    pass
retry(lambda: doc.SaveAs(os.path.join(ROOT, NAMES[SHEET] + ".dwg")))
time.sleep(1)


def _find():
    for i in range(app.Documents.Count):
        d = app.Documents.Item(i)
        if d.Name.lower().startswith(NAMES[SHEET].lower()):
            return d
    raise RuntimeError("sheet document not found after SaveAs")


doc = retry(_find)
_ = retry(lambda: doc.Layers.Count)
ms = retry(lambda: doc.ModelSpace)


def layer(name, color):
    lyr = retry(lambda: doc.Layers.Add(name))
    lyr.color = color
    return name


O = [0.0, 0.0]
CUR = ["0"]


def P(x, y):
    return APoint(x + O[0], y + O[1])


def L(o, lay=None):
    o.Layer = lay or CUR[0]
    return o


def line(x1, y1, x2, y2, lay=None):
    return L(retry(lambda: ms.AddLine(P(x1, y1), P(x2, y2))), lay)


def dashed(x1, y1, x2, y2, dash=180, gap=110, lay=None):
    d = math.hypot(x2 - x1, y2 - y1)
    if d < 1:
        return
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    t = 0.0
    while t < d:
        e = min(t + dash, d)
        line(x1 + ux * t, y1 + uy * t, x1 + ux * e, y1 + uy * e, lay)
        t = e + gap


def dashed_rect(x1, y1, x2, y2, lay=None, **kw):
    for a, b, c, d in ((x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)):
        dashed(a, b, c, d, lay=lay, **kw)


def rect(x1, y1, x2, y2, lay=None):
    flat = [x1 + O[0], y1 + O[1], x2 + O[0], y1 + O[1], x2 + O[0], y2 + O[1], x1 + O[0], y2 + O[1]]
    o = retry(lambda: ms.AddLightWeightPolyline(aDouble(*flat)))
    o.Closed = True
    return L(o, lay)


def circle(x, y, r, lay=None):
    return L(retry(lambda: ms.AddCircle(P(x, y), r)), lay)


def arc(x, y, r, a1, a2, lay=None):
    return L(retry(lambda: ms.AddArc(P(x, y), r, math.radians(a1), math.radians(a2))), lay)


def text(s, x, y, h=90, lay=None, align=10, rot=0.0):
    t = retry(lambda: ms.AddText(s, P(x, y), h))
    if align:
        t.Alignment = align
        t.TextAlignmentPoint = P(x, y)
    t.Rotation = rot
    return L(t, lay)


# ------------------------------------------------------------------ symbols
def s6(x, y):           # 6A socket
    circle(x, y, 90); line(x - 30, y - 45, x - 30, y + 45); line(x + 30, y - 45, x + 30, y + 45)


def s16(x, y):          # 16A power socket
    circle(x, y, 110); circle(x, y, 55)


def usb(x, y):
    rect(x - 80, y - 80, x + 80, y + 80); text("U", x, y, 90)


def data(x, y):         # LAN / data
    p = [(x, y + 110), (x - 95, y - 55), (x + 95, y - 55)]
    for i in range(3):
        line(*p[i], *p[(i + 1) % 3])
    text("D", x, y - 10, 70)


def tv(x, y):
    rect(x - 130, y - 85, x + 130, y + 85); text("TV", x, y, 80)


def ac(x, y):
    rect(x - 200, y - 75, x + 200, y + 75); text("AC", x, y, 85)


def sb(x, y, label):    # switchboard
    rect(x - 160, y - 80, x + 160, y + 80); line(x - 160, y - 80, x + 160, y + 80)
    text(label, x, y + 150, 75)


def db(x, y, label):    # distribution board
    rect(x - 260, y - 140, x + 260, y + 140); line(x - 260, y + 140, x + 260, y - 140); line(x - 260, y - 140, x + 260, y + 140)
    text(label, x, y + 230, 95)


def gy(x, y):           # geyser
    circle(x, y, 140); text("G", x, y, 110)


def ef(x, y):           # exhaust fan
    rect(x - 110, y - 110, x + 110, y + 110); line(x - 110, y - 110, x + 110, y + 110); line(x - 110, y + 110, x + 110, y - 110)


def fan(x, y):
    circle(x, y, 60)
    for a in (90, 210, 330):
        r = math.radians(a)
        line(x + 60 * math.cos(r), y + 60 * math.sin(r), x + 260 * math.cos(r), y + 260 * math.sin(r))


def tagged(x, y, tag):  # small circle with a short tag (CB, WP, AP, CCTV, bell)
    circle(x, y, 85); text(tag, x, y, 60)


def dl(x, y):           # recessed downlight
    circle(x, y, 75); line(x - 75, y, x + 75, y); line(x, y - 75, x, y + 75)


def pend(x, y):
    circle(x, y, 160); circle(x, y, 60)


def wl(x, y, facing):   # wall light, semicircle opening toward `facing`
    a = {"E": -90, "W": 90, "N": 0, "S": 180}[facing]
    arc(x, y, 130, a, a + 180)


def panel(x1, y1, x2, y2):
    rect(x1, y1, x2, y2); line(x1, y1, x2, y2)


def strip(x1, y1, x2, y2):
    dashed(x1, y1, x2, y2, dash=120, gap=60)


def bollard(x, y):
    circle(x, y, 60); circle(x, y, 25)


def cw(x, y):           # cold water point
    circle(x, y, 70); text("C", x, y, 70)


def hw(x, y):           # hot water point
    circle(x, y, 70); text("H", x, y, 70)


def ft(x, y):           # floor trap
    rect(x - 90, y - 90, x + 90, y + 90); circle(x, y, 55)


def ic(x, y, tag="IC"):  # inspection chamber
    rect(x - 230, y - 230, x + 230, y + 230); line(x - 230, y - 230, x + 230, y + 230); text(tag, x, y + 330, 90)


def stack(x, y, tag):   # vertical soil / rainwater pipe
    circle(x, y, 75); circle(x, y, 40); text(tag, x + 260, y, 75)


def grid(x1, y1, x2, y2, dx, dy, lay=None):
    """Tile / plank pattern lines inside a rectangle (dx or dy = 0 to skip a direction)."""
    if dx:
        x = x1 + dx
        while x < x2 - 1:
            line(x, y1, x, y2, lay); x += dx
    if dy:
        y = y1 + dy
        while y < y2 - 1:
            line(x1, y, x2, y, lay); y += dy


def set_notes(title, body):
    for i in range(ms.Count):
        o = ms.Item(i)
        if o.ObjectName == "AcDbMText" and ("FURNITURE LAYOUT" in o.TextString or "TWO-STOREY" in o.TextString):
            o.TextString = "{\\fArial|b1;" + title + "}\\P" + \
                "Residence, Kochi, Kerala  |  Option B (approved)  |  Road: North\\P" + \
                "{\\fArial|b1;FOR CLIENT APPROVAL - NOT FOR CONSTRUCTION}\\P\\P" + body
            return


def legend(items, y0=6200.0):
    """Legend under the notes: list of (draw_fn, label)."""
    O[:] = [NOTE_X + 400, y0]
    text("LEGEND", 200, 500, 200, align=0)
    for k, (fn, lab) in enumerate(items):
        yy = -k * 420
        fn(250, yy)
        text(lab, 650, yy, 130, align=9)


def freeze(*names):
    for n in names:
        try:
            doc.Layers.Item(n).Freeze = True
        except Exception:
            pass


def fade(*names, color=253):
    for n in names:
        try:
            doc.Layers.Item(n).color = color
        except Exception:
            pass


# =====================================================================================  E1
if SHEET == "E1":
    CUR[0] = layer("E-POWR", 1)
    freeze("I-FURN", "I-TEXT")
    O[:] = list(GF)
    db(2600, 7400, "MDB + RCCB (GF)")
    # living
    sb(5700, 11950, "SB-12M"); tv(5700, 10300); s6(5700, 9850); s6(5700, 10750); s16(5700, 11200); data(5700, 9500)
    s6(9600, 9300); usb(9600, 9600); s6(9600, 12350); usb(9600, 12650); s6(7000, 13400); ac(5700, 12900)
    tagged(5300, 13500, "BELL"); fan(7630, 11118)
    # dining
    sb(5700, 8450, "SB-6M"); s6(8300, 5200); s6(9100, 5200); ac(9600, 6300)
    # kitchen
    sb(6300, 4800, "SB-8M"); s16(5650, 2300); s16(5650, 3150); s16(5650, 3700); s6(8500, 4800); s6(9650, 3000)
    s6(9650, 4100); s6(7900, 4800); s6(9650, 3600); text("RO", 9450, 3600, 70); s16(9400, 2700); text("DW", 9150, 2700, 70)
    # work area
    sb(9550, 1550, "SB-4M"); s16(6400, 350); s6(8100, 350); ef(7300, 1650)
    # office
    sb(3700, 11450, "SB-8M"); s6(3100, 9500); s6(3100, 9900); s6(3100, 10300); usb(3100, 10650); data(3400, 10650)
    ac(5250, 10200); s6(5250, 9200); fan(4190, 10243)
    # sit-out, porch, gate
    tagged(5250, 12300, "WP"); tagged(2700, 9000, "WP"); tagged(2700, 13600, "CCTV"); tagged(200, 13600, "CCTV")
    s16(300, 9100); text("EV PROVISION", 900, 9100, 70, align=9)
    # hall, pooja, stair
    sb(3150, 8000, "SB-6M"); s6(5250, 6200); s6(3700, 6850); s6(5250, 4300)
    # common bath
    sb(3150, 5150, "SB-2M"); ef(400, 4700); gy(2700, 5150)
    # mother's room + bath
    sb(5250, 3700, "SB-6M"); s6(600, 3700); usb(900, 3700); s6(2800, 3700); tagged(2450, 3700, "CB")
    ac(1500, 3750); fan(1905, 2060); s6(500, 600); gy(5200, 2500); ef(4400, 350)
    # first floor
    O[:] = list(FF)
    db(4900, 8200, "DB (FF)")
    tagged(4190, 7300, "AP")
    sb(3100, 8000, "SB-4M"); s6(5250, 7000)
    # children's room + bath
    sb(4800, 8900, "SB-8M"); s6(350, 9300); usb(350, 9600); s6(350, 13000); usb(350, 12700)
    s6(350, 10400); s6(350, 11800); usb(350, 11100); data(650, 11100); ac(1500, 8900); fan(1905, 11150)
    gy(5250, 11300); ef(4300, 13450)
    # master + dressing + bath
    sb(5650, 9450, "SB-8M"); s6(5600, 9900); usb(5600, 10200); s6(5600, 12900); usb(5600, 12600)
    s6(9650, 13400); ac(9650, 9700); fan(7630, 11423); s6(7100, 8600); text("HAIR DRYER", 6700, 8350, 60)
    gy(9650, 8950); ef(9650, 7900); s6(8500, 9050)
    # gaming room - dedicated circuit
    sb(5250, 6400, "SB-8M"); s16(7300, 6400); s16(8200, 6400); s6(6900, 6400); s6(7600, 6400); s6(7900, 6400); s6(8600, 6400)
    data(7000, 6150); data(8500, 6150); text("DEDICATED 20A CIRCUIT + UPS", 7750, 5850, 70)
    tv(3600, 6400); s6(3250, 6400); s6(3950, 6400); data(4300, 6400); ac(4650, 6380); fan(6380, 5254)
    # laundry, terrace
    s16(500, 4800); s16(500, 4300); s6(1800, 4500); ef(1500, 4100)
    tagged(1500, 400, "WP"); tagged(8500, 400, "WP")
    set_notes("E1 - ELECTRICAL & SWITCHBOARD LAYOUT",
              "Mounting heights (FFL): switchboards +1200; 6A/16A general +300; kitchen counter +1100;\\P"
              "TV point +1200 (living) / +1100 (gaming); AC point +2400; geyser +1950; bedside +600.\\P"
              "Separate circuits: kitchen 16A, ACs (one MCB each), geysers, gaming room (20A + UPS).\\P"
              "All wet-area points on RCCB (30 mA). Outdoor points weatherproof IP65.\\P"
              "Provision: solar inverter tie-in at MDB, EV charging 16A at porch, CCTV + Wi-Fi APs.\\P"
              "Final circuiting, loads and cable sizes by licensed electrical engineer.")
    legend([(s6, "6A socket"), (s16, "16A power socket"), (usb, "USB socket"), (data, "Data / LAN"),
            (tv, "TV point"), (ac, "AC point (16A)"), (lambda x, y: sb(x, y, ""), "Switchboard (modules)"),
            (gy, "Geyser point"), (ef, "Exhaust fan"), (fan, "Ceiling fan"), (lambda x, y: tagged(x, y, "WP"), "Weatherproof / CCTV / AP / bell")])

# =====================================================================================  L1
if SHEET == "L1":
    CUR[0] = layer("L-CLNG", 4)
    layer("L-LITE", 2)
    freeze("I-FURN", "I-TEXT")
    fade("I-FIXT")

    def cove(x1, y1, x2, y2, band=450, lvl="FCL +2700 / CL +3000"):
        CUR[0] = "L-CLNG"
        rect(x1 + band, y1 + band, x2 - band, y2 - band)
        CUR[0] = "L-LITE"
        dashed_rect(x1 + band - 90, y1 + band - 90, x2 - band + 90, y2 - band + 90)
        CUR[0] = "L-CLNG"
        text(lvl, (x1 + x2) / 2, y1 + band / 2, 80)
        CUR[0] = "L-LITE"

    def flat(x1, y1, x2, y2, lvl):
        CUR[0] = "L-CLNG"
        text(lvl, (x1 + x2) / 2, y1 + 200, 75)
        CUR[0] = "L-LITE"

    O[:] = list(GF)
    cove(5500, 8678, 9760, 13558); cove(5500, 5018, 9760, 8678, lvl="FCL +2700 / CL +3000")
    for x, y in ((6600, 10400), (8700, 10400), (6600, 12400), (8700, 12400), (7630, 9300)):
        dl(x, y)
    fan(7630, 11118)
    for x in (7180, 7630, 8080):
        pend(x, 6850)
    strip(7700, 5300, 9600, 5300); dl(6000, 6000); dl(6000, 7700)
    wl(5520, 10300, "E"); text("TV WALL GRAZER", 6200, 10800, 70)
    flat(5500, 1853, 9760, 4903, "GYPSUM FLAT FCL +2850")
    panel(6600, 2900, 6900, 4100); panel(8300, 2600, 8600, 3800); strip(7650, 4450, 9150, 4450); strip(9250, 2600, 9250, 4250)
    flat(5500, 230, 9760, 1738, "MR GYPSUM FCL +2850"); panel(7300, 800, 7600, 1300)
    flat(3000, 8873, 5385, 11613, "FCL +2850"); panel(4000, 9700, 4400, 10800); dl(3400, 9300); dl(3400, 11200)
    flat(3000, 11728, 5385, 13788, "TEAK SLAT CEILING (SIT-OUT)"); dl(4190, 12750); wl(5370, 12550, "W"); wl(5370, 13300, "W"); wl(3010, 13300, "E")
    flat(0, 8748, 2885, 13788, "PORCH: UNDERSIDE OF FF"); dl(800, 10000); dl(2000, 10000); dl(800, 12500); dl(2000, 12500)
    flat(3000, 4005, 5385, 8758, "FCL +2850"); dl(4800, 5000); dl(4800, 6600); dl(4800, 8100); strip(3050, 6900, 4200, 6900); text("POOJA BACKLIGHT", 3610, 7050, 60)
    cove(230, 230, 3580, 3890, band=400, lvl="FCL +2700"); fan(1905, 2060); dl(700, 700); dl(3100, 700); wl(400, 3750, "S"); wl(2900, 3750, "S")
    text("NIGHT LIGHT +450", 1905, 3500, 60)
    for (x1, y1, x2, y2) in ((230, 4005, 2885, 5318), (3695, 230, 5385, 2670)):
        flat(x1, y1, x2, y2, "MR FCL +2600"); dl((x1 + x2) / 2, (y1 + y2) / 2); ef(x1 + 300, y2 - 300)
    for y in (5800, 6800, 7800):
        wl(250, y, "E")
    text("STAIR WALL LIGHTS", 1100, 7200, 70)
    for x, y in ((6600, 14900), (7600, 14900), (8600, 14900), (9600, 14900)):
        bollard(x, y)
    O[:] = list(FF)
    cove(230, 8748, 3580, 13558, band=400, lvl="FCL +2650"); fan(1905, 11150); dl(700, 11100); dl(700, 9400); dl(700, 12800)
    flat(3695, 8748, 5385, 11003, "FCL +2650"); dl(4540, 9900); strip(4785, 9750, 4785, 10950)
    cove(5500, 9288, 9760, 13558, band=450, lvl="FCL +2650"); fan(7630, 11423)
    pend(5850, 9875); pend(5850, 12855); dl(9000, 13000); dl(8800, 9800); wl(5520, 11415, "E"); text("HEADBOARD GRAZER", 6300, 11415, 60)
    flat(5500, 6618, 7190, 9173, "FCL +2650"); strip(5600, 7150, 7100, 7150); dl(6350, 8100)
    for (x1, y1, x2, y2) in ((7305, 6618, 9760, 9173), (3695, 11118, 5385, 13558), (230, 4005, 2885, 5318)):
        flat(x1, y1, x2, y2, "MR FCL +2550"); dl((x1 + x2) / 2, (y1 + y2) / 2); ef(x2 - 300, y2 - 300)
    strip(7600, 9050, 9400, 9050); text("MIRROR LED", 8500, 8900, 60)
    cove(3000, 4005, 9760, 6503, band=400, lvl="FCL +2650 - RGB COVE"); fan(6380, 5254)
    dl(3800, 5300); dl(5600, 5300); dl(9100, 5300); strip(6650, 6430, 8850, 6430); text("DESK LED + SHELF LED", 7750, 6250, 60)
    flat(3000, 6618, 5385, 8633, "FCL +2650"); dl(4190, 7200); dl(4190, 8200)
    for x in (2000, 5000, 8000):
        wl(x, 250, "N")
    text("TERRACE WALL LIGHTS (IP65)", 5000, 700, 80)
    set_notes("L1 - LIGHTING & FALSE CEILING PLAN",
              "False ceiling: gypsum board on GI frame; cove bands 400-450 wide, 300 drop, LED in cove.\\P"
              "Wet areas: moisture-resistant (MR) board. Sit-out: teak/WPC slat ceiling.\\P"
              "Clear heights assumed: GF slab 3000, FF 2900 (FF capsule curve at sides) - verify on site.\\P"
              "Colour temperature: 2700K living/bedrooms (warm), 3000K kitchen/baths, 4000K task strips;\\P"
              "gaming room: RGB cove on separate controller + 2700K dimmable downlights.\\P"
              "All downlights dimmable where marked on cove circuits. Fans: BLDC, 1200 mm sweep.")
    legend([(dl, "Recessed downlight"), (pend, "Pendant light"), (lambda x, y: wl(x, y, "N"), "Wall light"),
            (lambda x, y: strip(x - 200, y, x + 200, y), "LED strip / cove LED"), (lambda x, y: panel(x - 150, y - 80, x + 150, y + 80), "Panel / linear light"),
            (fan, "Ceiling fan"), (ef, "Exhaust fan"), (bollard, "Bollard light"),
            (lambda x, y: rect(x - 200, y - 80, x + 200, y + 80, "L-CLNG"), "False ceiling edge (cove band)")])

# =====================================================================================  P1
if SHEET == "P1":
    CUR[0] = layer("A-FLOR", 252)
    layer("P-WATR", 5); layer("P-WAST", 6); layer("P-SOIL", 1)
    freeze("I-FURN", "I-TEXT")

    def floor(x1, y1, x2, y2, dx, dy, label):
        CUR[0] = "A-FLOR"
        grid(x1, y1, x2, y2, dx, dy)
        text(label, (x1 + x2) / 2, y2 - 280, 75)

    O[:] = list(GF)
    floor(5500, 5018, 9760, 13558, 1200, 600, "PORCELAIN 1200x600 MATTE STONE-LOOK  FFL +-0")
    floor(5500, 1853, 9760, 4903, 600, 600, "KITCHEN 600x600 MATTE")
    floor(5500, 230, 9760, 1738, 600, 600, "WORK AREA 600x600 ANTI-SKID  -15")
    floor(3000, 4005, 5385, 11613, 1200, 600, "PORCELAIN 1200x600")
    floor(230, 230, 3580, 3890, 1200, 200, "WOOD-LOOK PLANK 1200x200 (MOTHER)")
    floor(3000, 11728, 5385, 13788, 600, 600, "FLAMED GRANITE  -150")
    floor(0, 8748, 2885, 13788, 600, 600, "GRANITE PAVERS (PORCH)  -450")
    for (x1, y1, x2, y2) in ((230, 4005, 2885, 5318), (3695, 230, 5385, 2670)):
        floor(x1, y1, x2, y2, 300, 300, "ANTI-SKID 300x300  -15")
    O[:] = list(FF)
    floor(230, 8748, 5385, 13558, 1200, 200, "ENGINEERED OAK / SPC PLANK")
    floor(5500, 9288, 9760, 13558, 1200, 200, "ENGINEERED OAK / SPC PLANK")
    floor(5500, 6618, 7190, 9173, 1200, 200, "OAK PLANK")
    floor(3000, 4005, 9760, 6503, 1200, 200, "OAK PLANK + ACOUSTIC UNDERLAY")
    floor(3000, 6618, 5385, 8633, 1200, 600, "PORCELAIN 1200x600")
    floor(230, 230, 9760, 3775, 0, 150, "WPC DECK ON PEDESTALS (TERRACE)")
    for (x1, y1, x2, y2) in ((7305, 6618, 9760, 9173), (3695, 11118, 5385, 13558), (230, 4005, 2885, 5318)):
        floor(x1, y1, x2, y2, 300, 300, "ANTI-SKID 300x300  -15")
    # ---- plumbing (GF)
    O[:] = list(GF)
    CUR[0] = "P-WATR"
    for (x, y) in ((1550, 4250), (2400, 4300)):
        cw(x, y)
    hw(2550, 4550); cw(700, 4900); hw(950, 4900)          # common bath: WC, basin, shower
    for (x, y) in ((5150, 1550), (5100, 2250)):
        cw(x, y)
    hw(4900, 2250); cw(4300, 450); hw(4550, 450)          # mother's bath
    cw(9550, 3050); hw(9550, 3350); cw(9550, 3650); text("RO", 9300, 3650, 60)   # kitchen sink + RO
    cw(6700, 450); cw(9550, 1100)                         # work area sink, outdoor tap
    CUR[0] = "P-WAST"
    ft(1700, 4700); ft(4540, 1200); ft(7600, 700); ft(9200, 2300)
    CUR[0] = "P-SOIL"
    stack(-250, 4600, "SVP-1"); stack(4540, -250, "SVP-2"); stack(10200, 900, "WP-1")
    dashed(1550, 4450, 230, 4600); dashed(230, 4600, -250, 4600)
    dashed(5100, 1550, 4540, 230); dashed(4540, 230, 4540, -250)
    CUR[0] = "P-WAST"
    dashed(9200, 2300, 9760, 2300); dashed(9760, 2300, 10200, 2300); dashed(7600, 700, 7600, 230); dashed(7600, 230, 7600, -300)
    CUR[0] = "P-SOIL"
    ic(-700, 4600, "IC-1"); ic(4540, -750, "IC-2"); ic(7600, -750, "IC-3 (GT)"); ic(10500, 2300, "IC-4")
    dashed(-700, 4370, -700, -750); dashed(-470, -750, 4310, -750); dashed(4770, -750, 7370, -750)
    text("TO SEPTIC TANK / SEWER (LOCATION TBC)", 3000, -1250, 90)
    for (x, y) in ((-250, -250), (10240, -250), (10240, 13900), (-250, 9000)):
        stack(x, y, "RWP")
    # ---- plumbing (FF)
    O[:] = list(FF)
    CUR[0] = "P-WATR"
    cw(7900, 6900); cw(8100, 9000); hw(8350, 9000); cw(8900, 9000); hw(9150, 9000); cw(9300, 6800); hw(9550, 6800)
    cw(5150, 11900); cw(5150, 12300); hw(5150, 12500); cw(4300, 13300); hw(4550, 13300)
    cw(600, 4800); text("WM", 900, 4800, 60); cw(2000, 4200)
    CUR[0] = "P-WAST"
    ft(9200, 7200); ft(4540, 13100); ft(1200, 4600)
    CUR[0] = "P-SOIL"
    stack(10200, 7800, "SVP-3"); stack(5650, 11900, "SVP-4 (DUCT)"); stack(-250, 4600, "SVP-1")
    for (x, y) in ((-250, -250), (10240, -250)):
        stack(x, y, "RWP")
    text("OHT 2000 L ON ROOF ABOVE STAIR", 1557, 7000, 80)
    set_notes("P1 - FLOORING & PLUMBING LAYOUT",
              "Flooring (matte finishes only, per brief): GF porcelain 1200x600 stone-look; FF engineered oak or\\P"
              "SPC plank; wet areas anti-skid 300x300 with 1:100 fall to floor traps; sit-out/porch flamed granite.\\P"
              "Levels (FFL): wet areas -15, sit-out -150, porch -450. Gaming room: acoustic underlay.\\P"
              "Water: CPVC hot/cold; overhead tank 2000 L + pressure pump for FF showers. Solar water heater provision.\\P"
              "Drainage: uPVC SWR soil/waste to inspection chambers, grease trap on kitchen line (IC-3).\\P"
              "Pipe routes are indicative; final sizing, slopes and septic/sewer connection by plumbing consultant.")
    legend([(cw, "Cold water point"), (hw, "Hot water point"), (ft, "Floor trap"),
            (lambda x, y: stack(x, y, ""), "Soil / waste / rainwater stack"), (lambda x, y: ic(x, y, ""), "Inspection chamber"),
            (lambda x, y: dashed(x - 250, y, x + 250, y), "Drain line (indicative)"),
            (lambda x, y: grid(x - 250, y - 120, x + 250, y + 120, 120, 120), "Floor finish pattern")])

retry(lambda: app.ZoomExtents())
retry(lambda: doc.Regen(1))
retry(lambda: doc.Save())
print("saved", doc.FullName, "| objects:", ms.Count)

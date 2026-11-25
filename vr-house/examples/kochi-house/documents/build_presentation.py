"""Builds the single client presentation PDF for the Kochi residence (Option B).

Run with: tools\\.pdfenv\\Scripts\\python.exe tools\\build_presentation.py
All BOQ figures are computed here from quantities x rates.
"""
import io
import os

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = r"D:\Kochi-Residence-Interior"
OUT = os.path.join(ROOT, "Kochi-Residence_Option-B_Design-Presentation.pdf")
W, H = landscape(A3)
BUDGET = 15_00_000

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial", boldItalic="Arial-Bold")

INK = colors.HexColor("#2b2620")
MUTED = colors.HexColor("#6f665b")
ACCENT = colors.HexColor("#8a4a24")
RULE = colors.HexColor("#d9cfc2")
PAPER = colors.HexColor("#faf7f2")


def inr(n):
    s = str(int(round(n)))
    neg = s.startswith("-")
    s = s.lstrip("-")
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if neg else "") + "\u20b9" + s


# ============================================================================ BOQ DATA
# (code, description, specification, qty, unit, rate)
BOQ = [
    ("A", "Modular kitchen & utility", [
        ("A1", "Kitchen base units with drawers", "BWP ply (IS:710) carcass, matte laminate shutters, soft-close", 12.8, "rft", 4800),
        ("A2", "Kitchen wall units", "BWP ply, matte laminate, lift-up + hinged shutters", 7.2, "rft", 3800),
        ("A3", "Tall units: fridge surround + oven/microwave tower", "BWP ply, matte laminate, appliance cut-outs", 2, "nos", 22000),
        ("A4", "Countertop", "Honed black granite 20 mm, edge-polished", 30, "sqft", 300),
        ("A5", "Backsplash", "Travertine-look matte porcelain", 22, "sqft", 180),
        ("A6", "Kitchen accessories", "Tandem drawers, cutlery tray, corner unit, bottle pull-out, bin", 1, "LS", 24000),
        ("A7", "Work area: utility sink cabinet + open rack", "BWP ply, laminate, SS rack", 1, "LS", 22000),
    ]),
    ("B", "Wardrobes & built-in storage", [
        ("B1", "Master wardrobes in dressing area (7 ft + loft)", "BWP ply, matte laminate, internal drawers", 54, "sqft", 1200),
        ("B2", "Master dressing unit with mirror", "Walnut-finish laminate, drawers", 1, "LS", 16000),
        ("B3", "Mother's wardrobe with locker, low hanging rail", "BWP ply, matte laminate", 46, "sqft", 1200),
        ("B4", "Children's wardrobe (study nook)", "BWP ply, matte laminate, hinged", 30, "sqft", 1150),
        ("B5", "Crockery unit: base cabinet + 2 open shelves", "Walnut-finish laminate, stone-look top", 6.2, "rft", 4500),
        ("B6", "Pooja unit, backlit", "Walnut finish, CNC jali shutters, LED backlight", 1, "LS", 26000),
        ("B7", "Shoe cabinet with key ledge", "Walnut-finish laminate", 1, "LS", 11000),
        ("B8", "Master bath double vanity", "Wall-hung, water-resistant ply, quartz top", 1, "nos", 18000),
        ("B9", "Single vanities (3 baths)", "Wall-hung, water-resistant ply, quartz top", 3, "nos", 10000),
        ("B10", "Laundry counter + overhead storage", "BWP ply, laminate", 1, "LS", 14000),
    ]),
    ("C", "Feature walls, media units & desks", [
        ("C1", "Living TV wall: stone slab panel", "Travertine-look porcelain slab 1600 x 2700", 46, "sqft", 320),
        ("C2", "Living TV wall: fluted panels", "Oak-finish fluted panels, both flanks", 43, "sqft", 320),
        ("C3", "Floating TV unit with LED under-glow", "Walnut finish, push-to-open drawers", 8.5, "rft", 3300),
        ("C4", "Gaming room acoustic slat wall (behind desk)", "Walnut-finish slats on PET acoustic felt", 74, "sqft", 420),
        ("C5", "Gaming PC desk 2.3 m with cable tray", "Walnut laminate top, powder-coated frame", 1, "LS", 18000),
        ("C6", "Gaming display shelves x3 with LED", "Walnut finish, aluminium LED profile", 1, "LS", 6000),
        ("C7", "Gaming media / console unit", "Walnut finish, floating", 1, "LS", 10000),
        ("C8", "Gaming room acoustic door", "Solid-core flush door, perimeter seals", 1, "nos", 15000),
        ("C9", "Office desk + bookshelf video-call backdrop", "Oak/walnut laminate", 1, "LS", 20000),
        ("C10", "Children's study desk 2.1 m + overhead shelf", "Oak laminate", 1, "LS", 22000),
    ]),
    ("D", "False ceiling", [
        ("D1", "Cove ceilings: living/dining, master, gaming, mother", "Gypsum board on GI frame, 300 drop, LED cove, painted", 902, "sqft", 110),
        ("D2", "Bath ceilings (4 nos)", "Moisture-resistant board, painted", 172, "sqft", 95),
        ("D3", "Sit-out slat ceiling", "WPC slats, teak finish", 53, "sqft", 320),
    ]),
    ("E", "Lighting & fans", [
        ("E1", "COB downlights 7 W, dimmable", "2700 K / 3000 K as per L1", 40, "nos", 650),
        ("E2", "LED strip in aluminium profile with drivers", "Coves, TV unit, desk, shelves, mirrors, kitchen", 75, "rm", 260),
        ("E3", "RGB controller + strip (gaming cove)", "App / remote control", 1, "LS", 4500),
        ("E4", "Dining pendants", "Matte black dome, warm LED", 3, "nos", 4000),
        ("E5", "Master bedside pendants", "Opal glass globe", 2, "nos", 3500),
        ("E6", "Indoor wall lights / grazers", "Stair, mother's room, TV & headboard walls", 7, "nos", 2200),
        ("E7", "Outdoor wall lights IP65", "Sit-out and terrace", 5, "nos", 2800),
        ("E8", "Floor lamp (living)", "Matte black arc, opal shade", 1, "nos", 5500),
        ("E9", "Garden bollards", "IP65, warm white", 4, "nos", 2400),
        ("E10", "Panel / linear lights", "Kitchen, office, work area", 4, "nos", 1800),
        ("E11", "BLDC ceiling fans 1200 mm", "Energy-efficient, remote", 6, "nos", 4200),
        ("E12", "Exhaust fans", "Baths, work area, laundry", 6, "nos", 1600),
        ("E13", "Smart dimmer scene control", "Living and gaming room", 2, "nos", 3500),
    ]),
    ("F", "Loose furniture", [
        ("F1", "L-sectional sofa with chaise", "Oatmeal textured fabric, solid wood frame", 1, "nos", 68000),
        ("F2", "Mid-century lounge chair (living)", "Leather-look upholstery, walnut shell", 1, "nos", 24000),
        ("F3", "Coffee table", "Stone top, oak frame", 1, "nos", 12000),
        ("F4", "Dining table 6-seater + 6 upholstered chairs", "Oak-finish top, black metal base; grey fabric chairs", 1, "set", 56000),
        ("F5", "King bed, upholstered headboard, hydraulic storage", "Grey fabric", 1, "nos", 42000),
        ("F6", "Queen bed (mother), 450 mm easy-height", "Solid wood, upholstered headboard", 1, "nos", 28000),
        ("F7", "Single beds (children)", "Oak finish", 2, "nos", 14000),
        ("F8", "Bedside tables", "Walnut finish, floating/drawer", 4, "nos", 3500),
        ("F9", "Mattress - king", "Pocket spring / memory foam", 1, "nos", 22000),
        ("F10", "Mattress - queen", "Orthopaedic, medium-firm", 1, "nos", 16000),
        ("F11", "Mattresses - single", "Foam, medium", 2, "nos", 9000),
        ("F12", "Bench at bed end (master)", "Oak frame, boucle seat", 1, "nos", 7000),
        ("F13", "Ergonomic office chair", "Mesh back, lumbar support", 1, "nos", 14000),
        ("F14", "Children's study chairs", "Height adjustable", 2, "nos", 3500),
        ("F15", "Recliner (mother's room)", "Single-seat, manual", 1, "nos", 22000),
        ("F16", "Sit-out chairs (2) + side table", "Outdoor-grade, teak finish", 1, "set", 12000),
    ]),
    ("G", "Soft furnishings & decor", [
        ("G1", "Curtains: sheer + lined linen with tracks", "Living, dining, bedrooms, office", 1, "LS", 48000),
        ("G2", "Blackout roller blinds (gaming room)", "Fabric blackout, chain operated", 85, "sqft", 220),
        ("G3", "Rugs: living, master, gaming", "Wool blend / flat-weave", 1, "LS", 15000),
        ("G4", "Bath mirrors", "Rounded, backlit-ready", 4, "nos", 3000),
        ("G5", "Cushions, throws, bedding", "Rust / olive / oatmeal accents", 1, "LS", 16000),
        ("G6", "Plants, planters, decor accessories", "Ceramic vases, books, indoor plants", 1, "LS", 8000),
    ]),
]

DEFERRED = [
    ("Master headboard oak-slat feature wall (shown in render)", 73, "sqft", 380),
    ("Gaming console sofa (2-seater) + ottoman (shown in plan)", 1, "LS", 22000),
    ("Second lounge chair - master bedroom (shown in render)", 1, "nos", 24000),
    ("Terrace outdoor sofa + dining set", 1, "LS", 25000),
    ("Under-stair pull-out storage", 1, "LS", 15000),
    ("Children's room cove ceiling", 172, "sqft", 110),
    ("Second floor lamp (master)", 1, "nos", 5500),
    ("Smart scene control - master bedroom", 1, "nos", 3500),
    ("Third tall kitchen unit (pantry pull-out)", 1, "nos", 22000),
]

EXCLUSIONS = [
    "Appliances: chimney, hob, built-in oven, microwave, fridge, dishwasher, washer/dryer, RO purifier, TVs, ACs.",
    "Gaming PC, monitors, peripherals and gaming chair (client-owned).",
    "Civil works incl. the new gaming-room partition wall, doors (except the acoustic door), windows and glazing.",
    "Flooring, wall tiling, sanitaryware & CP fittings, plumbing, electrical wiring, switches & sockets, DBs.",
    "Interior and exterior painting (building contractor) - feature finishes above are included.",
    "Structural, MEP and statutory approvals; landscaping and compound works.",
]


def amount(item):
    return round(item[3] * item[5])


SECTION_TOTALS = [(code, title, sum(amount(i) for i in items)) for code, title, items in BOQ]
CORE = sum(t for _, _, t in SECTION_TOTALS)
CONTINGENCY = BUDGET - CORE
DEFERRED_TOTAL = sum(round(q * r) for _, q, _, r in DEFERRED)
assert CORE <= BUDGET, f"core scope {CORE} exceeds budget"
assert CONTINGENCY >= 0.015 * BUDGET, f"contingency only {CONTINGENCY}"


# ============================================================================ PAGE HELPERS
def header(c, title, sub=None, page_no=None):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Arial-Bold", 22)
    c.drawString(20 * mm, H - 22 * mm, title)
    if sub:
        c.setFont("Arial", 11)
        c.setFillColor(MUTED)
        c.drawString(20 * mm, H - 29 * mm, sub)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.line(20 * mm, H - 33 * mm, W - 20 * mm, H - 33 * mm)
    c.setFont("Arial", 8.5)
    c.setFillColor(MUTED)
    c.drawString(20 * mm, 10 * mm, "Residence, Kochi, Kerala  |  Option B two-storey  |  For client approval - not for construction")
    if page_no:
        c.drawRightString(W - 20 * mm, 10 * mm, f"{page_no}")


def para(c, text, x, y, width, size=11, leading=None, color=INK, bold=False):
    st = ParagraphStyle("p", fontName="Arial-Bold" if bold else "Arial", fontSize=size,
                        leading=leading or size * 1.35, textColor=color)
    p = Paragraph(text, st)
    _, h = p.wrap(width, H)
    p.drawOn(c, x, y - h)
    return y - h


def image_page(c, path, title, caption, page_no):
    header(c, title, caption, page_no)
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    buf.seek(0)
    iw, ih = img.size
    box_w, box_h = W - 40 * mm, H - 55 * mm
    s = min(box_w / iw, box_h / ih)
    dw, dh = iw * s, ih * s
    c.drawImage(ImageReader(buf), (W - dw) / 2, 18 * mm + (box_h - dh) / 2, dw, dh)


def lin_to_srgb(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def swatch(c, x, y, rgb_lin, name, note):
    r, g, b = (lin_to_srgb(v) for v in rgb_lin)
    c.setFillColorRGB(r, g, b)
    c.setStrokeColor(RULE)
    c.rect(x, y, 34 * mm, 24 * mm, stroke=1, fill=1)
    c.setFillColor(INK)
    c.setFont("Arial-Bold", 10)
    c.drawString(x, y - 5 * mm, name)
    c.setFont("Arial", 8.5)
    c.setFillColor(MUTED)
    c.drawString(x, y - 9.5 * mm, note)


def table(c, data, x, y_top, col_w, font=8.5, header_bg=colors.HexColor("#ece4d8"), bold_rows=(), right_cols=()):
    t = Table(data, colWidths=col_w, repeatRows=1)
    style = [
        ("FONT", (0, 0), (-1, -1), "Arial", font),
        ("FONT", (0, 0), (-1, 0), "Arial-Bold", font),
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]
    for r in bold_rows:
        style += [("FONT", (0, r), (-1, r), "Arial-Bold", font), ("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f2ece3"))]
    for col in right_cols:
        style.append(("ALIGN", (col, 0), (col, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    _, h = t.wrap(sum(col_w), H)
    t.drawOn(c, x, y_top - h)
    return y_top - h


def qty_str(q):
    return f"{q:g}"


# ============================================================================ GENERATED PAGES
def build_generated():
    """Returns {key: pdf-bytes} for every generated page."""
    pages = {}

    def new():
        buf = io.BytesIO()
        return buf, canvas.Canvas(buf, pagesize=(W, H))

    # ---- cover
    buf, c = new()
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    img = Image.open(os.path.join(ROOT, "OptionB_Exterior_01_Front-Corner.png")).convert("RGB")
    jb = io.BytesIO(); img.save(jb, "JPEG", quality=90); jb.seek(0)
    c.drawImage(ImageReader(jb), W * 0.42, 0, W * 0.58, H, preserveAspectRatio=False)
    c.setFillColor(INK); c.setFont("Arial-Bold", 34)
    c.drawString(20 * mm, H - 55 * mm, "Residence, Kochi")
    c.setFont("Arial", 16); c.setFillColor(MUTED)
    c.drawString(20 * mm, H - 66 * mm, "Architecture, interior design & BOQ")
    c.drawString(20 * mm, H - 74 * mm, "Option B - two-storey contemporary home")
    c.setStrokeColor(ACCENT); c.setLineWidth(2); c.line(20 * mm, H - 82 * mm, 80 * mm, H - 82 * mm)
    contents = ["1  Design summary", "2  Architectural plans (Option B)", "3  Furniture layout",
                "4  Electrical & switchboards (E1)", "5  Lighting & false ceiling (L1)", "6  Flooring & plumbing (P1)",
                "7  Exterior views", "8  Interior concept & materials", "9  Interior views",
                "10 Furniture & finishes specification", "11 Bill of quantities", "12 Deferred items, exclusions & credits"]
    c.setFont("Arial-Bold", 12); c.setFillColor(INK); c.drawString(20 * mm, H - 100 * mm, "CONTENTS")
    c.setFont("Arial", 11)
    for i, line in enumerate(contents):
        c.drawString(20 * mm, H - 110 * mm - i * 7 * mm, line)
    c.setFont("Arial", 9); c.setFillColor(MUTED)
    c.drawString(20 * mm, 20 * mm, "Plot 40' x 60' (12.19 x 18.29 m), road to the north  |  Family of five  |  Interior budget " + inr(BUDGET))
    c.drawString(20 * mm, 14 * mm, "Issued for client approval - November 2026 - not for construction")
    c.showPage(); c.save(); pages["cover"] = buf.getvalue()

    # ---- design summary
    buf, c = new()
    header(c, "1  Design summary", "What the scheme is, what it assumes, and what is still open", 2)
    col_w = (W - 60 * mm) / 3
    x1, x2, x3 = 20 * mm, 30 * mm + col_w, 40 * mm + 2 * col_w
    top = H - 42 * mm
    y = para(c, "<b>The scheme</b>", x1, top, col_w, 13)
    y = para(c, "Two-storey contemporary home on a 40' x 60' plot facing the road to the north, about "
                "<b>2,550 sq ft</b> built-up (ground 1,483 sq ft incl. car porch and sit-out; first 1,064 sq ft "
                "+ 418 sq ft open terrace).<br/><br/>"
                "<b>Ground floor</b> - car porch under the cantilevered first floor, sit-out, home office with its own "
                "client entrance, living, dining, L-shaped kitchen with work area, pooja, common bath, and the "
                "mother's room with attached bath (no stairs for her).<br/><br/>"
                "<b>First floor</b> - master suite with walk-through dressing and bath, children's room with study nook "
                "and bath, adult PC <b>gaming room</b> (former family lounge, now closed with an acoustic door), "
                "laundry, and a rear terrace.", x1, y - 2 * mm, col_w, 10.5)
    y = para(c, "<b>Design direction</b>", x2, top, col_w, 13)
    y = para(c, "<b>Exterior</b> - from the client's references: a rounded, fluted-timber first-floor volume with a "
                "white rim and full glass ends, cantilevered over the porch; white ground floor with a rounded glass "
                "frame at the living room; flat roofs and a glass-railed terrace.<br/><br/>"
                "<b>Interior</b> - warm minimalism as briefed: cream walls, stone-look floors and travertine, fluted oak, "
                "walnut, oatmeal fabrics with rust and olive accents, matte finishes only, cove and indirect lighting, "
                "no gold or gloss. The gaming room uses the same palette in a moodier key: walnut acoustic slats, "
                "warm-grey walls and a purple cove.", x2, y - 2 * mm, col_w, 10.5)
    y = para(c, "<b>Assumptions & open items</b>", x3, top, col_w, 13)
    para(c, "- Setbacks assumed 3.0 m front, 1.5 m rear, 1.2 / 1.0 m sides - verify with the local body (KMBR).<br/>"
            "- Floor-to-floor 3.15 m; clear heights ~3.0 m GF / ~2.9 m FF - verify on site.<br/>"
            "- Structure (cantilever, rounded shell, columns) to be designed by a structural engineer.<br/>"
            "- Electrical loads, cable and pipe sizes, septic / sewer connection: MEP consultants.<br/>"
            "- Built-up area grew from the brief's 1,500-1,600 sq ft to ~2,550 sq ft; the interior budget is held at "
            + inr(BUDGET) + " by phasing some items (see section 12).<br/>"
            "- 4 bathrooms (brief: 3) so the first floor has its own.<br/>"
            "- Option A (single storey) and its hip-roof exterior are superseded and not included.",
            x3, y - 2 * mm, col_w, 10.5)
    strip = Image.open(os.path.join(ROOT, "Interior_04_Living-Dining.png")).convert("RGB")
    sw_, sh_ = strip.size
    target_w, target_h = W - 40 * mm, 120 * mm
    crop_h = int(sw_ * target_h / target_w)
    top_px = max(0, (sh_ - crop_h) // 2)
    strip = strip.crop((0, top_px, sw_, top_px + crop_h))
    sb_ = io.BytesIO(); strip.save(sb_, "JPEG", quality=88); sb_.seek(0)
    c.drawImage(ImageReader(sb_), 20 * mm, 18 * mm, target_w, target_h)
    c.showPage(); c.save(); pages["summary"] = buf.getvalue()

    # ---- interior concept & materials
    buf, c = new()
    header(c, "8  Interior concept & materials", "Warm minimalism - natural, matte, layered light", 11)
    para(c, "A calm, warm backdrop of cream walls and stone-look floors, with natural oak and walnut carrying the "
            "joinery. Texture does the work instead of ornament: fluted panels, travertine, boucle and linen. Light is "
            "mostly indirect - cove LEDs, wall grazers on the TV and headboard walls, and pendants where people gather. "
            "Rust and olive appear only in small doses (cushions, throws, art).", 20 * mm, H - 42 * mm, W - 40 * mm, 11.5)
    sw = [((0.76, 0.67, 0.54), "Warm cream paint", "All walls, matte"), ((0.56, 0.48, 0.37), "Stone-look porcelain", "GF floors, 1200x600 matte"),
          ((0.62, 0.52, 0.38), "Travertine-look slab", "TV wall, backsplash"), ((0.50, 0.35, 0.21), "Natural oak", "Fluted panels, FF floors, desks"),
          ((0.22, 0.12, 0.065), "Walnut", "TV unit, pooja, slats, side tables"), ((0.72, 0.64, 0.52), "Oatmeal boucle", "Sofa, bench, chairs"),
          ((0.88, 0.84, 0.76), "Linen sheer", "Curtains"), ((0.46, 0.17, 0.07), "Rust accent", "Cushions, throw, art"),
          ((0.27, 0.28, 0.15), "Olive accent", "Cushions, plants"), ((0.025, 0.025, 0.025), "Matte black metal", "Pendants, legs, frames"),
          ((0.24, 0.23, 0.21), "Warm grey (gaming)", "Gaming room walls"), ((0.42, 0.28, 1.0), "Purple LED (gaming)", "RGB cove, shelf LEDs")]
    for i, (rgb, name, note) in enumerate(sw):
        col, row = i % 6, i // 6
        swatch(c, 20 * mm + col * 64 * mm, H - 112 * mm - row * 52 * mm, rgb, name, note)
    para(c, "<b>Lighting temperatures:</b> 2700 K living and bedrooms, 3000 K kitchen and baths, 4000 K task strips. "
            "<b>Joinery:</b> BWP plywood carcasses with matte laminate or veneer; soft-close hardware. "
            "<b>Wet areas:</b> anti-skid matte tiles, moisture-resistant ceilings, wall-hung vanities.",
         20 * mm, 38 * mm, W - 40 * mm, 10.5, color=MUTED)
    c.showPage(); c.save(); pages["concept"] = buf.getvalue()

    # ---- furniture & finishes specification
    buf, c = new()
    header(c, "10  Furniture & finishes specification", "Key furniture and joinery per room - sizes are nominal (mm)", 16)
    spec = [["Room", "Item", "Size (mm)", "Material / finish", "Notes"],
            ["Living", "L-sectional sofa with chaise", "3200 x 2050", "Oatmeal textured fabric, wood frame", "4 seats + chaise; with lounge chair seats 6"],
            ["Living", "Mid-century lounge chair", "1000 x 1190", "Leather-look, walnut shell", "Swivel base"],
            ["Living", "Coffee table", "1200 x 600 x 390", "Stone top, oak frame", ""],
            ["Living", "TV wall + floating TV unit", "2600 long, unit 450 deep", "Travertine-look slab, fluted oak, walnut", "Concealed storage, LED under-glow"],
            ["Dining", "Dining table + 6 chairs", "2160 x 1040 table", "Oak-finish top, black base; grey fabric chairs", "Two end chairs"],
            ["Dining", "Crockery unit", "1900 x 450 + shelves", "Walnut laminate, stone-look top", "Slim unit keeps chair clearance"],
            ["Kitchen", "L-shaped modular kitchen", "East 2350 + north 1560 run", "BWP ply, matte laminate, black granite", "Fridge, oven/MW tower, pantry"],
            ["Office", "Desk + video-call backdrop shelf", "1400 x 600 desk", "Oak/walnut laminate", "Ergonomic chair; acoustic rug"],
            ["Mother", "Queen bed + recliner + wardrobe", "Bed 1500 x 2000", "Wood, upholstered; matte laminate", "450 mm bed height, grab bars in bath"],
            ["Master", "King bed, upholstered", "2000 x 2200", "Grey fabric, hydraulic storage", "Bedside pendants"],
            ["Master", "Dressing: wardrobes + dressing unit", "2.4 m run + unit", "Matte laminate, walnut", "Walk-through to bath"],
            ["Children", "2 single beds + shared study desk", "Beds 900 x 1950; desk 2100", "Oak laminate", "Wardrobe in study nook"],
            ["Gaming", "PC desk (triple monitor)", "2300 x 700", "Walnut top, metal frame, cable tray", "Dedicated 20 A circuit + UPS"],
            ["Gaming", "Acoustic slat wall, shelves, media unit", "2600 x 2650 wall", "Walnut slats on PET felt", "Blackout blinds, acoustic door"],
            ["Sit-out", "2 chairs + side table", "", "Outdoor-grade, teak finish", "WPC slat ceiling"]]
    table(c, spec, 20 * mm, H - 40 * mm, [28 * mm, 70 * mm, 50 * mm, 95 * mm, 137 * mm], font=9.5)
    c.showPage(); c.save(); pages["spec"] = buf.getvalue()

    # ---- BOQ summary
    buf, c = new()
    header(c, "11  Bill of quantities - summary", "Indicative Kochi market rates, Nov 2026, incl. material, fabrication, installation and GST", 17)
    rows = [["Section", "Scope", "Amount", "% of budget"]]
    for code, title, tot in SECTION_TOTALS:
        rows.append([code, title, inr(tot), f"{tot / BUDGET * 100:.1f}%"])
    rows.append(["", "Core scope", inr(CORE), f"{CORE / BUDGET * 100:.1f}%"])
    rows.append(["H", "Contingency", inr(CONTINGENCY), f"{CONTINGENCY / BUDGET * 100:.1f}%"])
    rows.append(["", "TOTAL (= interior budget)", inr(CORE + CONTINGENCY), "100.0%"])
    y = table(c, rows, 20 * mm, H - 42 * mm, [22 * mm, 110 * mm, 40 * mm, 30 * mm], font=11,
              bold_rows=(len(rows) - 3, len(rows) - 1), right_cols=(2, 3))
    # bar chart of section shares
    bx, by, bw = 250 * mm, H - 50 * mm, 140 * mm
    c.setFont("Arial-Bold", 11); c.setFillColor(INK); c.drawString(bx, by + 4 * mm, "Where the money goes")
    mx = max(t for _, _, t in SECTION_TOTALS)
    for i, (code, title, tot) in enumerate(SECTION_TOTALS):
        yy = by - 8 * mm - i * 10 * mm
        c.setFillColor(MUTED); c.setFont("Arial", 9); c.drawString(bx, yy + 2 * mm, f"{code}  {title}")
        c.setFillColor(ACCENT); c.rect(bx, yy - 3 * mm, bw * tot / mx, 4 * mm, stroke=0, fill=1)
        c.setFillColor(INK); c.drawString(bx + bw * tot / mx + 2 * mm, yy - 2.2 * mm, inr(tot))
    para(c, f"<b>Within budget:</b> the core scope is {inr(CORE)}, leaving a {inr(CONTINGENCY)} contingency "
            f"({CONTINGENCY / BUDGET * 100:.1f}%), so the total equals the {inr(BUDGET)} interior budget. "
            f"With the deferred items in section 12 ({inr(DEFERRED_TOTAL)}), the full design as rendered would be about "
            f"{inr(CORE + CONTINGENCY + DEFERRED_TOTAL)}.<br/><br/>"
            "<b>How it fits:</b> the house is ~2,550 sq ft, so " + inr(BUDGET) + " is about " + inr(BUDGET / 2550) +
            " per sq ft for the interior. It fits by using matte laminate on BWP ply rather than veneer, cove ceilings "
            "only in the key rooms, local-make furniture to the specified designs, and phasing a few add-ons.<br/><br/>"
            "<b>Before ordering:</b> rates are indicative (+/-10%). Get three itemised vendor quotes against this BOQ, "
            "and confirm the builder's scope (painting, flooring, wiring, sanitaryware) in writing.",
         20 * mm, y - 10 * mm, 200 * mm, 10.5)
    c.showPage(); c.save(); pages["boq_summary"] = buf.getvalue()

    # ---- BOQ detail pages (split sections across pages)
    detail_pages = []
    groups = [["A", "B", "C"], ["D", "E", "F", "G"]]
    for gi, grp in enumerate(groups):
        buf, c = new()
        header(c, f"11  Bill of quantities - detail ({gi + 1}/2)", "Qty x rate = amount; LS = lump sum, rft = running foot, rm = running metre", 18 + gi)
        rows = [["Code", "Item", "Specification", "Qty", "Unit", "Rate", "Amount"]]
        bold = []
        for code, title, items in BOQ:
            if code not in grp:
                continue
            for it in items:
                rows.append([it[0], it[1], it[2], qty_str(it[3]), it[4], inr(it[5]), inr(amount(it))])
            bold.append(len(rows))
            rows.append(["", f"Total {code} - {title}", "", "", "", "", inr(sum(amount(i) for i in items))])
        table(c, rows, 20 * mm, H - 40 * mm, [14 * mm, 112 * mm, 138 * mm, 18 * mm, 14 * mm, 32 * mm, 34 * mm],
              font=8.6, bold_rows=bold, right_cols=(3, 5, 6))
        c.showPage(); c.save(); detail_pages.append(buf.getvalue())
    pages["boq_detail"] = detail_pages

    # ---- deferred, exclusions, credits
    buf, c = new()
    header(c, "12  Deferred items, exclusions & credits", "Phase-2 add-ons are designed in and can be added later without rework", 20)
    rows = [["Deferred / optional item", "Qty", "Unit", "Rate", "Amount"]]
    for d, q, u, r in DEFERRED:
        rows.append([d, qty_str(q), u, inr(r), inr(round(q * r))])
    rows.append(["Total deferred", "", "", "", inr(DEFERRED_TOTAL)])
    y = table(c, rows, 20 * mm, H - 42 * mm, [120 * mm, 16 * mm, 14 * mm, 28 * mm, 30 * mm], font=9.5,
              bold_rows=(len(rows) - 1,), right_cols=(1, 3, 4))
    yy = para(c, "<b>Not in the interior budget (builder / client scope)</b>", 20 * mm, y - 10 * mm, 210 * mm, 12)
    para(c, "<br/>".join("- " + e for e in EXCLUSIONS), 20 * mm, yy - 2 * mm, 210 * mm, 10)
    credits = open(os.path.join(ROOT, "3D-Model-Credits.txt"), encoding="utf-8").read().strip().splitlines()[3:]
    cy = para(c, "<b>3D model credits (renders)</b>", 250 * mm, H - 42 * mm, 150 * mm, 12)
    para(c, "<br/>".join(l.replace("&", "&amp;") for l in credits if l.strip()), 250 * mm, cy - 2 * mm, 150 * mm, 8.2, color=MUTED)
    c.showPage(); c.save(); pages["closing"] = buf.getvalue()

    # ---- image pages
    imgs = [("ext1", "OptionB_Exterior_01_Front-Corner.png", "7  Exterior views", "Front corner from the road - fluted-timber capsule cantilevered over the car porch", 8),
            ("ext2", "OptionB_Exterior_02_Front-Elevation.png", "7  Exterior views", "Front elevation - full-glass first-floor end with white rim, rounded living-room frame below", 9),
            ("ext3", "OptionB_Exterior_03_Rear-Terrace-Aerial.png", "7  Exterior views", "Rear aerial - terrace with glass railing off the gaming room", 10),
            ("int1", "Interior_01_Living.png", "9  Interior views", "Living - travertine and fluted-oak TV wall, L-sectional, lounge chair, cove ceiling", 12),
            ("int2", "Interior_04_Living-Dining.png", "9  Interior views", "Living to dining - 6-seater oak table, dome pendants, crockery unit", 13),
            ("int3", "Interior_03_Master-Bedroom.png", "9  Interior views", "Master bedroom - upholstered bed, oak-slat wall (deferred item), glass pendants, sheer + linen curtains", 14),
            ("int4", "Interior_02_Gaming-Room.png", "9  Interior views", "Gaming room - triple-monitor PC desk, walnut acoustic slats, purple cove, blackout blinds", 15)]
    for key, f, t, cap, pn in imgs:
        buf, c = new()
        image_page(c, os.path.join(ROOT, f), t, cap, pn)
        c.showPage(); c.save(); pages[key] = buf.getvalue()
    return pages


def main():
    pages = build_generated()
    writer = PdfWriter()

    def add_bytes(b):
        for p in PdfReader(io.BytesIO(b)).pages:
            writer.add_page(p)

    def add_pdf(name):
        for p in PdfReader(os.path.join(ROOT, name)).pages:
            writer.add_page(p)

    add_bytes(pages["cover"])
    add_bytes(pages["summary"])
    for f in ("Kochi-Residence_Option-B_Two-Storey-Plans.pdf", "Kochi-Residence_Option-B_Furniture-Layout.pdf",
              "Kochi-Residence_Option-B_E1_Electrical-Layout.pdf", "Kochi-Residence_Option-B_L1_Lighting-Ceiling.pdf",
              "Kochi-Residence_Option-B_P1_Flooring-Plumbing.pdf"):
        add_pdf(f)
    # drawing pages carry no page numbers of their own; the generated pages are numbered to match the merged order
    for k in ("ext1", "ext2", "ext3", "concept", "int1", "int2", "int3", "int4", "spec", "boq_summary"):
        add_bytes(pages[k])
    for b in pages["boq_detail"]:
        add_bytes(b)
    add_bytes(pages["closing"])
    writer.add_metadata({"/Title": "Residence, Kochi - Option B design presentation", "/Author": "Design team"})
    writer.compress_identical_objects()
    with open(OUT, "wb") as fh:
        writer.write(fh)
    print("written", OUT, "| pages:", len(writer.pages), "| size MB:", round(os.path.getsize(OUT) / 1e6, 1))
    print("core", inr(CORE), "| contingency", inr(CONTINGENCY), f"({CONTINGENCY / BUDGET * 100:.1f}%)", "| deferred", inr(DEFERRED_TOTAL))
    for code, title, tot in SECTION_TOTALS:
        print(" ", code, title, inr(tot))


if __name__ == "__main__":
    main()

"""
Generates uml_final.png — a UML class diagram for PawPal+ drawn with Pillow.
Run once:  python generate_uml.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

# ---------------------------------------------------------------------------
# Data — one dict per class, relationships defined separately
# ---------------------------------------------------------------------------

CLASSES = [
    {
        "name": "Task",
        "stereotype": "«dataclass»",
        "attrs": [
            "+ name : str",
            "+ category : str",
            "+ duration_minutes : int",
            "+ priority : str",
            "+ preferred_time_of_day : str",
            "+ frequency_per_day : int",
            "+ notes : str",
            "+ completed : bool",
            "+ recurrence : str | None",
            "+ due_date : date | None",
        ],
        "methods": [
            "+ is_high_priority() : bool",
            "+ get_priority_score() : int",
            "+ mark_complete() : None",
            "+ next_occurrence() : Task | None",
        ],
    },
    {
        "name": "Pet",
        "stereotype": "«dataclass»",
        "attrs": [
            "+ name : str",
            "+ species : str",
            "+ breed : str",
            "+ age_years : int",
            "+ weight_lbs : float",
            "+ health_conditions : list[str]",
            "+ tasks : list[Task]",
        ],
        "methods": [
            "+ add_task(task: Task) : None",
            "+ remove_task(task_name: str) : None",
            "+ get_pending_tasks() : list[Task]",
            "+ get_care_requirements() : list[Task]",
            "+ update_health_info(condition: str) : None",
        ],
    },
    {
        "name": "Owner",
        "stereotype": "",
        "attrs": [
            "+ name : str",
            "+ available_minutes : int",
            "+ preferred_times : list[str]",
            "+ energy_level : str",
            "+ preferences : dict",
            "+ pets : list[Pet]",
        ],
        "methods": [
            "+ add_pet(pet: Pet) : None",
            "+ remove_pet(pet_name: str) : None",
            "+ get_all_tasks() : list[tuple]",
            "+ get_pending_tasks() : list[tuple]",
            "+ add_constraint(key, value) : None",
            "+ update_preferences(key, value) : None",
            "+ get_available_slots() : list[str]",
        ],
    },
    {
        "name": "Scheduler",
        "stereotype": "",
        "attrs": [
            "+ owner : Owner",
            "+ date : str",
            "+ scheduled : list[dict]",
            "+ skipped : list[dict]",
            "- _time_used : int",
            "$ TIME_ORDER : list[str]",
        ],
        "methods": [
            "- _collect_tasks() : list[tuple]",
            "- _rank_tasks(tasks) : list[tuple]",
            "- _assign_slot(task) : str",
            "+ generate_plan() : None",
            "+ detect_conflicts() : list[str]",
            "+ sort_by_time() : list[dict]",
            "+ filter_tasks(completed, pet_name) : list[dict]",
            "+ mark_task_done(task_name) : bool",
            "+ get_summary() : dict",
            "+ explain_plan() : str",
        ],
    },
]

# (from_class, to_class, label, arrow_style)
# arrow_style: "composition" | "association"
RELATIONSHIPS = [
    ("Pet",      "Task",    "tasks\n1 *-- many",  "composition"),
    ("Owner",    "Pet",     "pets\n1 *-- many",   "composition"),
    ("Scheduler","Owner",   "uses\n-->",          "association"),
]

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
PAD          = 18
HEADER_H     = 44        # name + stereotype row
ROW_H        = 18        # per attribute / method line
DIVIDER_GAP  = 6
BOX_W        = 340
MARGIN       = 60        # canvas edge margin
COL_GAP      = 80        # horizontal gap between columns
ROW_GAP      = 60        # vertical gap between rows

# Colours
BG           = (245, 248, 252)
BOX_BG       = (255, 255, 255)
HEADER_BG    = (30, 90, 160)
HEADER_FG    = (255, 255, 255)
ATTR_BG      = (240, 244, 250)
METHOD_BG    = (252, 252, 255)
BORDER       = (30, 90, 160)
TEXT_DARK    = (20, 20, 40)
STEREO_FG    = (100, 140, 200)
ARROW_COLOR  = (60, 60, 140)
DIVIDER_CLR  = (180, 200, 230)

# ---------------------------------------------------------------------------
# Font (fall back to default if no truetype font is found)
# ---------------------------------------------------------------------------
def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT_NAME   = load_font(13, bold=True)
FONT_STEREO = load_font(10)
FONT_ATTR   = load_font(11)
FONT_REL    = load_font(10)

# ---------------------------------------------------------------------------
# Measure box height for a class
# ---------------------------------------------------------------------------
def box_height(cls):
    n_attrs    = len(cls["attrs"])
    n_methods  = len(cls["methods"])
    return HEADER_H + PAD + n_attrs * ROW_H + DIVIDER_GAP + n_methods * ROW_H + PAD

# ---------------------------------------------------------------------------
# Draw one class box; returns (x, y, w, h) of the box
# ---------------------------------------------------------------------------
def draw_class(draw, cls, x, y):
    h = box_height(cls)
    w = BOX_W

    # Shadow
    shadow_off = 4
    draw.rectangle(
        [x + shadow_off, y + shadow_off, x + w + shadow_off, y + h + shadow_off],
        fill=(200, 210, 225),
    )

    # Box background
    draw.rectangle([x, y, x + w, y + h], fill=BOX_BG, outline=BORDER, width=2)

    # Header band
    draw.rectangle([x, y, x + w, y + HEADER_H], fill=HEADER_BG)

    # Stereotype
    cy = y + 4
    if cls["stereotype"]:
        draw.text((x + w // 2, cy), cls["stereotype"], font=FONT_STEREO,
                  fill=STEREO_FG, anchor="mt")
        cy += 14
    else:
        cy += 8

    # Class name
    draw.text((x + w // 2, cy), cls["name"], font=FONT_NAME,
              fill=HEADER_FG, anchor="mt")

    # Attributes section
    ay = y + HEADER_H + PAD // 2
    draw.rectangle([x + 1, ay, x + w - 1, ay + len(cls["attrs"]) * ROW_H + PAD // 2],
                   fill=ATTR_BG)
    for i, attr in enumerate(cls["attrs"]):
        draw.text((x + PAD, ay + 4 + i * ROW_H), attr, font=FONT_ATTR, fill=TEXT_DARK)

    # Divider
    div_y = ay + len(cls["attrs"]) * ROW_H + PAD // 2
    draw.line([(x + 1, div_y), (x + w - 1, div_y)], fill=DIVIDER_CLR, width=1)

    # Methods section
    my = div_y + DIVIDER_GAP
    for i, method in enumerate(cls["methods"]):
        draw.text((x + PAD, my + 2 + i * ROW_H), method, font=FONT_ATTR, fill=TEXT_DARK)

    return (x, y, w, h)

# ---------------------------------------------------------------------------
# Draw an arrow between two boxes
# ---------------------------------------------------------------------------
def midpoint(bx, by, bw, bh, side):
    """Return (x,y) of a midpoint on a box edge."""
    if side == "right":  return (bx + bw, by + bh // 2)
    if side == "left":   return (bx,      by + bh // 2)
    if side == "bottom": return (bx + bw // 2, by + bh)
    if side == "top":    return (bx + bw // 2, by)

def draw_arrow(draw, p1, p2, style, label=""):
    draw.line([p1, p2], fill=ARROW_COLOR, width=2)
    # Arrowhead at p2
    import math
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    aw = 10
    ax1 = (p2[0] - aw * ux + aw * 0.4 * uy, p2[1] - aw * uy - aw * 0.4 * ux)
    ax2 = (p2[0] - aw * ux - aw * 0.4 * uy, p2[1] - aw * uy + aw * 0.4 * ux)
    draw.polygon([p2, ax1, ax2], fill=ARROW_COLOR)

    if style == "composition":
        # Diamond at p1
        ds = 10
        d1 = (p1[0] + ds * ux + ds * 0.5 * uy, p1[1] + ds * uy - ds * 0.5 * ux)
        d2 = (p1[0] + ds * 2 * ux,              p1[1] + ds * 2 * uy)
        d3 = (p1[0] + ds * ux - ds * 0.5 * uy, p1[1] + ds * uy + ds * 0.5 * ux)
        draw.polygon([p1, d1, d2, d3], fill=HEADER_BG)

    # Label
    if label:
        mx = (p1[0] + p2[0]) // 2
        my = (p1[1] + p2[1]) // 2
        draw.text((mx + 6, my), label, font=FONT_REL, fill=ARROW_COLOR)

# ---------------------------------------------------------------------------
# Layout: 2 columns, 2 rows  (Task | Pet)  /  (Owner | Scheduler)
# ---------------------------------------------------------------------------
def compute_positions():
    positions = {}
    grid = [
        ["Task",      "Pet"],
        ["Owner",     "Scheduler"],
    ]
    x_starts = [MARGIN, MARGIN + BOX_W + COL_GAP]

    y = MARGIN
    for row_idx, row in enumerate(grid):
        row_h = max(box_height(next(c for c in CLASSES if c["name"] == name)) for name in row)
        for col_idx, name in enumerate(row):
            positions[name] = (x_starts[col_idx], y)
        y += row_h + ROW_GAP

    return positions

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    positions = compute_positions()

    # Canvas size
    boxes = {cls["name"]: cls for cls in CLASSES}
    max_x = max(positions[n][0] + BOX_W for n in positions) + MARGIN
    max_y = max(positions[n][1] + box_height(boxes[n]) for n in positions) + MARGIN + 30

    img  = Image.new("RGB", (max_x, max_y), BG)
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((max_x // 2, 14), "PawPal+  —  UML Class Diagram (Final)",
              font=FONT_NAME, fill=HEADER_BG, anchor="mt")

    # Draw boxes; collect rects
    rects = {}
    for cls in CLASSES:
        name = cls["name"]
        x, y = positions[name]
        _, _, w, h = draw_class(draw, cls, x, y)
        rects[name] = (x, y, w, h)

    # Draw relationships
    # Pet *-- Task  (right side of Pet → left of Task ... actually Pet is col 1, Task is col 0)
    # Pet is at right, Task at left in row 0 → arrow from Pet left edge to Task right edge
    bx, by, bw, bh = rects["Pet"]
    tx, ty, tw, th = rects["Task"]
    p1 = midpoint(bx, by, bw, bh, "left")
    p2 = midpoint(tx, ty, tw, th, "right")
    draw_arrow(draw, p1, p2, "composition", "tasks  1 *── *")

    # Owner *-- Pet  (Owner bottom → Pet top? Owner is row 1 col 0, Pet is row 0 col 1)
    ox, oy, ow, oh = rects["Owner"]
    p1 = midpoint(ox, oy, ow, oh, "right")
    p2 = midpoint(bx, by, bw, bh, "bottom")
    # Draw L-shaped line
    mx = (p1[0] + p2[0]) // 2
    draw.line([p1, (p2[0], p1[1]), p2], fill=ARROW_COLOR, width=2)
    # Arrowhead
    draw.polygon([p2, (p2[0]-7, p2[1]-10), (p2[0]+7, p2[1]-10)], fill=ARROW_COLOR)
    # Diamond at p1
    d = 9
    draw.polygon([p1, (p1[0]+d, p1[1]-d//2), (p1[0]+2*d, p1[1]), (p1[0]+d, p1[1]+d//2)], fill=HEADER_BG)
    draw.text((p1[0]+5, p1[1]-22), "pets  1 *── *", font=FONT_REL, fill=ARROW_COLOR)

    # Scheduler --> Owner  (Scheduler left → Owner right)
    sx, sy, sw, sh = rects["Scheduler"]
    p1 = midpoint(sx, sy, sw, sh, "left")
    p2 = midpoint(ox, oy, ow, oh, "right")
    draw_arrow(draw, p1, p2, "association", "uses ──>")

    out_path = os.path.join(os.path.dirname(__file__), "uml_final.png")
    img.save(out_path, "PNG")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()

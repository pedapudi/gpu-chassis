"""Sliding lid and upper rear cover.

- The lid slides on four flush-head press-in studs in the body walls. L-shaped
  slots in its side returns take a vertical entry from the lower edge, then a
  rearward leg. The lid drops on 10 mm behind its seated position and slides
  forward against the front carrier. Removal reverses this.
- Two tabs folded down from the lid's rear edge sit behind the rear cover.
  Two M3 retention screws, one per tab, thread into extruded threads in the
  cover web and stop the lid sliding back.
- The rear cover is a perforated web with two side returns and a forward
  lower lip. M3 screws through the body walls thread into its returns.

Coordinates follow the calling build: X across the body, Y rearward, Z up.
`D` is the body's rear plane.
"""
import cadquery as cq
from mounting_hardware import box, cyl, nut, screw

T = 1.5                  # sheet thickness of the body, cover and lid
LID_SCREW_INSET = 24.0   # lid retention screw axes from the body's outer faces
TAB_SPAN = (14.0, 34.0)  # lid tab extent from each body side
TAB_DROP = 17.0          # lid tab depth below the lid top
LIP_SPAN = (15.0, 425.0)
RETURN_DEPTH = 13.3      # cover side returns run forward from the web
SIDE_SCREW_Y = 7.8       # cover side-screw axes ahead of the rear plane
SLIDE = 10.0             # lid travel between the seated and lift-off positions
STUD_RADIUS = 2.0
SLOT_WIDTH = 4.6
CLEARANCE_HOLE = 1.7


def lid_screw_x(W):
    return (LID_SCREW_INSET, W - LID_SCREW_INSET)


def cover(W, D, bottom, top, side_z, lid_z):
    """Perforated web between the walls with two side returns and a forward lower lip.

    `top` sits one thickness below the lid underside: the lid tab bends occupy
    the corner above it. Returns the formed shape, its folds and its holes.
    """
    web = box(T, D - T, bottom, W - 2 * T, T, top - bottom)
    returns = [box(x, D - T - RETURN_DEPTH, bottom, T, RETURN_DEPTH, top - bottom) for x in (T, W - 2 * T)]
    lip = box(LIP_SPAN[0], D - T - 2.5, bottom, LIP_SPAN[1] - LIP_SPAN[0], 2.5, T)
    shape = cq.Workplane().add(web).union(returns[0]).union(returns[1]).union(lip).val()
    folds = [('z', (T, D), (1, -1)), ('z', (W - T, D), (-1, -1)),
             ('x', (D, bottom), (-1, 1), dict(span=LIP_SPAN, relief=True))]
    holes = [cyl(-1, D - SIDE_SCREW_Y, z, CLEARANCE_HOLE, W + 2, (1, 0, 0)) for z in side_z]
    holes += [cyl(x, D - 2, lid_z, CLEARANCE_HOLE, 3, (0, 1, 0)) for x in lid_screw_x(W)]
    return shape, folds, holes


def body_side_holes(W, D, side_z):
    return [cyl(-1, D - SIDE_SCREW_Y, z, CLEARANCE_HOLE, W + 2, (1, 0, 0)) for z in side_z]


def cover_fasteners(W, D, side_z, lid_z):
    """Side screws into the cover returns and the lid retention screws into the cover web.

    Nut placeholders mark each thread; the build converts them into extruded
    threads in the cover.
    """
    y = D - SIDE_SCREW_Y
    parts = []
    for z in side_z:
        parts += [(f'left_rear_cover_M3x6_{z:g}', screw((0, y, z), (1, 0, 0), 'M3', 6), 'fasteners'),
                  (f'right_rear_cover_M3x6_{z:g}', screw((W, y, z), (-1, 0, 0), 'M3', 6), 'fasteners'),
                  (f'left_rear_cover_thread_nut_{z:g}', nut((2 * T, y, z), (1, 0, 0), 'M3'), 'fasteners'),
                  (f'right_rear_cover_thread_nut_{z:g}', nut((W - 2 * T, y, z), (-1, 0, 0), 'M3'), 'fasteners')]
    for x in lid_screw_x(W):
        parts += [(f'Lid_rear_retention_M3x6_{x:g}', screw((x, D + T, lid_z), (0, -1, 0), 'M3', 6), 'lid_screws'),
                  (f'Lid_retention_thread_nut_{x:g}', nut((x, D - T, lid_z), (0, -1, 0), 'M3'), 'fasteners')]
    return parts


def perforation_allowed(W, H, x, z, lid_z, r=4.0):
    """Perforations stay clear of the lid screw holes and of the area behind the lid tabs."""
    behind_tab = z + r > H - TAB_DROP - 2 and (x - r < TAB_SPAN[1] + 2 or x + r > W - TAB_SPAN[1] - 2)
    near_screw = any(abs(x - sx) < r + CLEARANCE_HOLE + 2 and abs(z - lid_z) < r + CLEARANCE_HOLE + 2 for sx in lid_screw_x(W))
    return not (behind_tab or near_screw)


def lid_top(W, D, H, y0, lid_z):
    """Lid top sheet reaching over the cover, with two rear tabs folded down behind it."""
    top = box(0, y0, H - T, W, D + T - y0, T)
    spans = [TAB_SPAN, (W - TAB_SPAN[1], W - TAB_SPAN[0])]
    tabs = [box(a, D, H - TAB_DROP, b - a, T, TAB_DROP - T) for a, b in spans]
    shape = cq.Workplane().add(top).union(tabs[0]).union(tabs[1]).val()
    folds = [('x', (D + T, H), (-1, -1), dict(span=s, relief=True)) for s in spans]
    holes = [cyl(x, D - 1, lid_z, CLEARANCE_HOLE, 3, (0, 1, 0)) for x in lid_screw_x(W)]
    return shape, folds, holes


def lid_slots(W, H, studs):
    """L-shaped slots in both lid returns: a vertical entry from the lower edge, then a rearward leg.

    With the lid seated, each stud sits at the rear end of its slot's
    horizontal leg; with the lid SLIDE mm rearward it reaches the vertical
    entry.
    """
    tools = []
    r = SLOT_WIDTH / 2
    for y, z in studs:
        entry = y - SLIDE
        tools += [cyl(-1, y_c, z, r, W + 2, (1, 0, 0)) for y_c in (entry, y)]
        tools.append(box(-1, entry, z - r, W + 2, SLIDE, SLOT_WIDTH))
        tools.append(box(-1, entry - r, H - 20, W + 2, SLOT_WIDTH, z - (H - 20)))
    return tools


def stud_holes(W, studs):
    return [cyl(-1, y, z, STUD_RADIUS, W + 2, (1, 0, 0)) for y, z in studs]


def lid_studs(W, studs):
    """Flush-head press-in studs, 4 mm diameter, projecting 2.5 mm inside each wall."""
    out = []
    for y, z in studs:
        out.append((f'Lid_locating_stud_left_{y:g}', cyl(0, y, z, STUD_RADIUS - .01, T + 2.5, (1, 0, 0))))
        out.append((f'Lid_locating_stud_right_{y:g}', cyl(W - T - 2.5, y, z, STUD_RADIUS - .01, T + 2.5, (1, 0, 0))))
    return out


def lid_removal_hits(lid, fixed, overlap):
    """Slide the lid rearward to the slot entries, then lift it; list any fixed part it meets."""
    hits = []
    for dy, dz in [(2, 0), (5, 0), (SLIDE, 0), (SLIDE, 3), (SLIDE, 10), (SLIDE, 40)]:
        moved = lid.translate((0, dy, dz))
        hits += [dict(slide_mm=dy, lift_mm=dz, part=p['name']) for p in fixed if overlap(moved, p['shape']) > 1e-4]
    return hits

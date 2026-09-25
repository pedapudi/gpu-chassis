"""Lid and upper rear cover retained by rear-facing captive thumbscrews.

Rack slides and posts leave no room for fasteners on the body sides, so every
thumbscrew faces rearward:

- The body side walls end in two inward flanges behind the GPU brackets. Each
  flange carries two extruded M3 threads.
- The upper rear cover is a flat perforated web behind the flanges. Two
  captive thumbscrews in the web thread into the lower flange threads.
- Two tabs folded down from the lid's rear edge carry the lid thumbscrews.
  They pass through clearance holes in the cover and thread into the upper
  flange threads.
- At the front, L-shaped slots in the lid side returns engage flush-head
  press-in studs in the body walls. The lid drops on 10 mm behind its seated
  position, slides forward against the front carrier and is then screwed at
  the rear; removal reverses this.

Coordinates follow the calling build: X across the body, Y rearward, Z up.
"""
import cadquery as cq
from mounting_hardware import box, cyl, nut
from threads import captive_screw

T = 1.5                # sheet thickness of the body, cover and lid
FLANGE_WIDTH = 17.0    # rear flange width from the body's outer face
SCREW_INSET = 10.0     # thumbscrew axes from the body's outer faces
TAB_SPAN = (4.0, 44.0)  # lid tab extent from each body side
TAB_DROP = 17.0        # lid tab depth below the lid top
LIP_SPAN = (19.0, 421.0)  # cover lower lip; it stops short of the flanges
SLIDE = 10.0           # lid travel between the seated and lift-off positions
STUD_RADIUS = 2.0
SLOT_WIDTH = 4.6
FERRULE_HOLE = 3.2     # radius of the press-fit ferrule hole
CLEARANCE_HOLE = 1.7


def screw_x(W):
    return (SCREW_INSET, W - SCREW_INSET)


def body_flanges(W, D, z0, z_top, z_low, z_high):
    """Solids to add, the wall-end notch, folds and holes that form the two rear flanges.

    The flanges lie in Y D-3 to D-1.5, so the cover web closes the body's rear
    plane behind them. The wall ends are cut back to the flange plane over the
    cover height.
    """
    adds = [box(0, D - 2 * T, z0, FLANGE_WIDTH, T, z_top - z0), box(W - FLANGE_WIDTH, D - 2 * T, z0, FLANGE_WIDTH, T, z_top - z0)]
    notch = box(-1, D - T, z0 - T, W + 2, T + 1, z_top - z0 + T + 1)
    folds = [('z', (0, D - T), (1, -1), dict(span=(z0, z_top), relief=True)),
             ('z', (W, D - T), (-1, -1), dict(span=(z0, z_top), relief=True))]
    holes = [cyl(x, D - 5, z, CLEARANCE_HOLE, 5, (0, 1, 0)) for x in screw_x(W) for z in (z_low, z_high)]
    return adds, notch, folds, holes


def flange_nuts(W, D, z_low, z_high):
    """Nut placeholders on the flange fronts; the build converts them to extruded threads."""
    return [(f'Rear_flange_thread_nut_{x:g}_{z:g}', nut((x, D - 2 * T, z), (0, -1, 0), 'M3')) for x in screw_x(W) for z in (z_low, z_high)]


def cover(W, D, bottom, top, z_low, z_high, extra_holes=()):
    """Flat perforated web across the full width with a forward lower lip.

    `top` should sit one thickness below the lid underside: the lid tab bends
    occupy the corner above it.
    """
    shape = cq.Workplane().add(box(0, D - T, bottom, W, T, top - bottom)).union(
        box(LIP_SPAN[0], D - T - 2.5, bottom, LIP_SPAN[1] - LIP_SPAN[0], 2.5, T)).val()
    folds = [('x', (D, bottom), (-1, 1), dict(span=LIP_SPAN, relief=True))]
    holes = [cyl(x, D - 2, z_low, FERRULE_HOLE, 3, (0, 1, 0)) for x in screw_x(W)]
    holes += [cyl(x, D - 2, z_high, CLEARANCE_HOLE, 3, (0, 1, 0)) for x in screw_x(W)]
    return shape, folds, holes + list(extra_holes)


def perforation_allowed(W, H, x, z, r=4.0):
    """Perforations stay clear of the thumbscrew holes and of the area behind the lid tabs."""
    if x - r < SCREW_INSET + FERRULE_HOLE + 2 or x + r > W - SCREW_INSET - FERRULE_HOLE - 2:
        return False
    behind_tab = z + r > H - TAB_DROP and (x - r < TAB_SPAN[1] + 4 or x + r > W - TAB_SPAN[1] - 4)
    return not behind_tab


def lid_top(W, D, H, y0, z_high):
    """Lid top sheet reaching over the cover, with two rear tabs folded down behind it."""
    top = box(0, y0, H - T, W, D + T - y0, T)
    spans = [TAB_SPAN, (W - TAB_SPAN[1], W - TAB_SPAN[0])]
    tabs = [box(a, D, H - TAB_DROP, b - a, T, TAB_DROP - T) for a, b in spans]
    shape = cq.Workplane().add(top).union(tabs[0]).union(tabs[1]).val()
    folds = [('x', (D + T, H), (-1, -1), dict(span=s, relief=True)) for s in spans]
    holes = [cyl(x, D - 1, z_high, FERRULE_HOLE, 3, (0, 1, 0)) for x in screw_x(W)]
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


def lid_thumbscrews(W, D, z_high):
    """Captive thumbscrews in the lid tabs; they pass the cover and thread into the upper flange threads."""
    return [(f'Lid_rear_captive_thumbscrew_{x:g}', captive_screw((x, D, z_high), (0, -1, 0), 5.5)) for x in screw_x(W)]


def cover_thumbscrews(W, D, z_low):
    """Captive thumbscrews in the cover web; they thread into the lower flange threads."""
    return [(f'Rear_cover_captive_thumbscrew_{x:g}', captive_screw((x, D - T, z_low), (0, -1, 0), 4.5)) for x in screw_x(W)]


def lid_removal_hits(lid, fixed, overlap):
    """Slide the lid rearward to the slot entries, then lift it; list any fixed part it meets."""
    hits = []
    for dy, dz in [(2, 0), (5, 0), (SLIDE, 0), (SLIDE, 3), (SLIDE, 10), (SLIDE, 40)]:
        moved = lid.translate((0, dy, dz))
        hits += [dict(slide_mm=dy, lift_mm=dz, part=p['name']) for p in fixed if overlap(moved, p['shape']) > 1e-4]
    return hits

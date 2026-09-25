"""Extruded tapped threads and embossed bosses.

Captive hex nuts are replaced by threads formed in the sheet that held them:
the clearance hole becomes a tap-drill hole and a collar extruded from the
sheet, on the side the nut occupied, lengthens the thread. Screws that engage
a formed thread record the sheet part in `thread_host`, so interference checks
treat the overlap as thread engagement.
"""
import math
import re
import cadquery as cq
from sheetmetal import sheet_parts, bounds

# Tap drill and extruded-collar outside diameter for each thread.
TAP = {'M3': (2.5, 3.7), 'M4': (3.3, 4.9), '6-32': (2.705, 4.1)}
NUT_HEIGHT = {2.4: 'M3', 3.2: 'M4', 2.78: '6-32', 2.2: 'M4'}
FILL_RADIUS = 2.3


def _vec(i, s=1.0):
    v = [0., 0., 0.]; v[i] = s; return cq.Vector(*v)


def _axis(shape):
    b = bounds(shape); ext = [b[i + 3] - b[i] for i in range(3)]
    i = min(range(3), key=lambda k: ext[k])
    return i, ext[i], cq.Vector(*[(b[k] + b[k + 3]) / 2 for k in range(3)])


def _thickness(part, piece):
    if piece and piece.get('t'): return piece['t']
    b = bounds(part['shape']); return round(min(b[k + 3] - b[k] for k in range(3)), 3)


def form_thread(shape, centre, axis, outward, t, thread, collar=True):
    """Turn a clearance hole into a tapped hole; `outward` points from the sheet toward the collar side."""
    drill, od = TAP[thread]
    face = centre  # a point on the sheet face where the collar starts
    inward = _vec(axis, -outward)
    # Fill only the existing hole: the void region that contains the thread axis.
    probe = cq.Vertex.makeVertex(*(face + inward * (t / 2)).toTuple())
    fill = cq.Solid.makeCylinder(FILL_RADIUS, t, face, inward)
    void = [v for v in fill.cut(shape).Solids() if v.distance(probe) < 1e-6]
    if void:
        # A void filling the whole cylinder means the axis misses this sheet.
        assert void[0].Volume() < fill.Volume() * 0.99, 'Thread axis is not in a hole of this sheet'
        shape = shape.fuse(void[0])
    height = min(t, 1.5) if (collar and t < 3) else 0
    if height:
        shape = shape.fuse(cq.Solid.makeCylinder(od / 2, height, face, _vec(axis, outward)))
    bore = cq.Solid.makeCylinder(drill / 2, t + height + 2, face - _vec(axis, outward) * (t + 1), _vec(axis, outward))
    return shape.cut(bore).clean(), height


def tap_captive_nuts(parts, select, keep=()):
    """Replace selected nuts with extruded tapped threads in the sheet they bear on."""
    sheets = sheet_parts(parts); tapped = []
    for nut in [p for p in parts if select(p) and not any(k in p['name'] for k in keep)]:
        axis, height, c = _axis(nut['shape'])
        thread = NUT_HEIGHT.get(round(height, 2))
        assert thread, ('Unrecognised nut', nut['name'], height)
        ends = [c + _vec(axis, s) * (height / 2) for s in (-1, 1)]
        for s in sheets:
            if not s.get('pieces') and s['shape'].distance(nut['shape']) < 1e-3:
                # A flat part gets an explicit blank so its collars stay out of the flat pattern.
                s['pieces'] = [dict(name=s['name'], shape=s['shape'], t=_thickness(s, None), bends=[])]
        # The thread goes in the sheet, nut end and blank that surround the nut's axis with a hole.
        options = [(_hole_land(q['shape'], e, axis, 1 if (c - e).dot(_vec(axis)) > 0 else -1, _thickness(s, q)), s, q, e)
                   for s in sheets if s['shape'].distance(nut['shape']) < 1e-3 for q in s['pieces'] for e in ends]
        assert options, ('Nut does not bear on a sheet part', nut['name'])
        land, host, piece, end = max(options, key=lambda o: o[0])
        assert land > 0, ('No clearance hole on the nut axis', nut['name'])
        outward = 1 if (c - end).dot(_vec(axis)) > 0 else -1
        t = _thickness(host, piece)
        try:
            host['shape'], collar = form_thread(host['shape'], end, axis, outward, t, thread)
        except AssertionError as e:
            raise AssertionError('Cannot form thread', nut['name'], host['name'], piece['name']) from e
        # The flat blank marks the thread with its tap-drill hole; the collar is formed after bending.
        piece['shape'], _ = form_thread(piece['shape'], end, axis, outward, t, thread, collar=False)
        piece.setdefault('tapped', []).append(dict(thread=thread, centre=[round(v, 3) for v in end.toTuple()]))
        host.setdefault('tapped', []).append(dict(thread=thread, centre=[round(v, 3) for v in end.toTuple()], collar_mm=collar))
        for s in parts:
            if s is nut or not re.search(r'screw|M\dx\d', s['name']) or 'nut' in s['name'] or 'washer' in s['name']: continue
            sa, _, sc = _axis_long(s['shape'])
            if sa == axis and all(abs(getattr(sc, 'xyz'[k]) - getattr(c, 'xyz'[k])) < .3 for k in range(3) if k != axis) \
                    and s['shape'].distance(nut['shape']) < .5:
                s['thread_host'] = host['name']
        parts.remove(nut); tapped.append(dict(nut=nut['name'], host=host['name'], thread=thread))
    return tapped


def _hole_land(shape, face, axis, outward, t):
    """Sheet volume within the fill radius around a hole whose face is at `face`; zero without a hole."""
    probe = cq.Vertex.makeVertex(*(face + _vec(axis, -outward) * (t / 2)).toTuple())
    if shape.distance(probe) < 1e-6: return 0.0
    ring = cq.Solid.makeCylinder(FILL_RADIUS, t, face, _vec(axis, -outward))
    return ring.intersect(shape).Volume()


def _axis_long(shape):
    b = bounds(shape); ext = [b[i + 3] - b[i] for i in range(3)]
    i = max(range(3), key=lambda k: ext[k])
    return i, ext[i], cq.Vector(*[(b[k] + b[k + 3]) / 2 for k in range(3)])


def emboss_boss(shape, x, y, z_bottom, t, height, thread='M3', base_radius=10.0, top_radius=5.0):
    """Raise a conical boss from a horizontal sheet whose underside is at `z_bottom`.

    The boss top surface sits `height` above the sheet's top surface and carries
    an extruded tapped thread whose collar hangs inside the boss.
    """
    top = z_bottom + t + height
    outer = cq.Solid.makeCone(base_radius, top_radius, top - z_bottom, cq.Vector(x, y, z_bottom))
    # Offset the cone wall inward by the sheet thickness along its normal.
    run, rise = base_radius - top_radius, top - z_bottom
    length = math.hypot(run, rise); n_r, n_z = -rise / length, -run / length
    r0, z0 = base_radius + t * n_r, t * n_z
    slope = -run / rise
    inner_base = r0 + slope * (0 - z0)
    inner_top_z = top - z_bottom - t
    inner_top = r0 + slope * (inner_top_z - z0)
    inner = cq.Solid.makeCone(inner_base, inner_top, inner_top_z, cq.Vector(x, y, z_bottom))
    shape = shape.cut(inner).fuse(outer.cut(inner)).clean()
    assert len(shape.Solids()) == 1, 'Boss must join its sheet'
    return form_thread(shape, cq.Vector(x, y, top - t), 2, -1, t, thread)[0]


"""Formed sheet-metal bends and developed flat patterns for axis-aligned parts.

A part is first modeled with sharp, box-union corners. `fold` replaces one
outside corner with an inside radius R and outside radius R + T while keeping
every flat face in place. Each bend records its bend zone: the (R + T) square
region at the corner, extruded along the bend line. `unfold` removes the bend
zones, lays the remaining flat panels out through the bend tree and inserts a
strip of width equal to the bend allowance for every 90-degree bend.

Defaults describe cold-rolled mild steel air-bent on standard tooling:
inside radius equal to sheet thickness and K-factor 0.40. A fabricator's
tooling values replace them before release.
"""
import math
import cadquery as cq

K_FACTOR = 0.40
AXES = 'xyz'


def unit(axis, sign=1.0):
    v = [0.0, 0.0, 0.0]; v[AXES.index(axis)] = float(sign); return cq.Vector(*v)


def bend_allowance(t, r, k=K_FACTOR):
    return math.pi / 2 * (r + k * t)


def fold(shape, bends, axis, corner, into, t, r=None, span=None, relief=False):
    """Form the outside corner at `corner` (coordinates of the two axes other than
    `axis`, in xyz order) whose legs extend in the `into` directions (+1/-1).

    Appends the bend-zone box to `bends` and returns the formed solid. With
    `relief`, a slot one thickness wide is cut at each end of a partial bend,
    0.5 mm deeper than the bend zone, so the bend can form without tearing.
    """
    r = t if r is None else r
    other = [a for a in AXES if a != axis]
    b = shape.BoundingBox()
    lo = {'x': b.xmin, 'y': b.ymin, 'z': b.zmin}; hi = {'x': b.xmax, 'y': b.ymax, 'z': b.zmax}
    s0, s1 = span if span else (lo[axis], hi[axis])
    size = r + t
    mins, lens, centre = {}, {}, {}
    for a, c, d in zip(other, corner, into):
        mins[a] = c if d > 0 else c - size; lens[a] = size; centre[a] = c + d * size
    mins[axis] = s0; lens[axis] = s1 - s0; centre[axis] = s0
    zone = cq.Solid.makeBox(lens['x'], lens['y'], lens['z'], cq.Vector(mins['x'], mins['y'], mins['z']))
    sharp = shape.intersect(zone).Volume()
    expected = (2 * size * t - t * t) * (s1 - s0)
    assert abs(sharp - expected) < 1e-3 * expected + 1e-6, ('Bend zone is not a clean sharp corner', axis, corner, sharp, expected)
    origin = cq.Vector(centre['x'], centre['y'], centre['z'])
    outer = cq.Solid.makeCylinder(size, s1 - s0, origin, unit(axis))
    inner = cq.Solid.makeCylinder(r, s1 - s0, origin, unit(axis))
    formed = shape.cut(zone).fuse(outer.cut(inner).intersect(zone)).clean()
    if relief:
        rmin = dict(mins); rlen = dict(lens)
        for a, d in zip(other, into):
            rlen[a] = size + .5
            if d < 0: rmin[a] = mins[a] - .5
        for start in (s0 - t, s1):
            rmin[axis] = start; rlen[axis] = t
            cutter = cq.Solid.makeBox(rlen['x'], rlen['y'], rlen['z'], cq.Vector(rmin['x'], rmin['y'], rmin['z']))
            if formed.intersect(cutter).Volume() > 1e-6: formed = formed.cut(cutter).clean()
    assert formed.isValid(), 'Formed bend produced an invalid solid'
    bends.append(dict(zone=zone, axis=axis, t=t, r=r))
    return formed


def transform_bends(bends, fn):
    return [dict(b, zone=fn(b['zone'])) for b in bends]


def bounds(shape):
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    box = Bnd_Box(); BRepBndLib.AddOptimal_s(shape.wrapped, box, False, False); return box.Get()


def _range(shape, axis):
    b = bounds(shape); i = AXES.index(axis)
    return b[i], b[i + 3]


def _thickness_axis(shape, t):
    b = bounds(shape); ext = [b[i + 3] - b[i] for i in range(3)]
    axis = min(range(3), key=lambda i: abs(ext[i] - t))
    assert abs(ext[axis] - t) < 1e-4, ('Panel is not a flat slab of the sheet thickness', ext, t)
    return AXES[axis]


def _rigid(P0, E1, E2, F0, M, flip):
    """Matrix mapping 3D panel coordinates to the flat XY plane."""
    N = E1.cross(E2) * (1 if flip > 0 else -1)
    rows = [E1 * M[0][0] + E2 * M[0][1], E1 * M[1][0] + E2 * M[1][1], N]
    t = [F0[0] - rows[0].dot(P0), F0[1] - rows[1].dot(P0), -rows[2].dot(P0)]
    from OCP.gp import gp_Trsf
    trsf = gp_Trsf()
    trsf.SetValues(*[v for i in range(3) for v in (rows[i].x, rows[i].y, rows[i].z, t[i])])
    return trsf


def unfold(shape, bends, t, k=K_FACTOR):
    """Return the developed flat face (in the XY plane), its bend table and size."""
    zones = [b['zone'] for b in bends]
    body = shape
    for zone in zones: body = body.cut(zone)
    panels = [p for p in body.Solids() if p.Volume() > 1e-6]
    info = []
    for p in panels:
        n = _thickness_axis(p, t); lo, hi = _range(p, n)
        info.append(dict(solid=p, n=n, mid=(lo + hi) / 2))
    # Each bend zone joins exactly two panels; the formed arc must be intact.
    links = []
    for b in bends:
        size = b['r'] + t; span = _range(b['zone'], b['axis'])
        arc = shape.intersect(b['zone']).Volume()
        full = math.pi / 4 * (size ** 2 - b['r'] ** 2) * (span[1] - span[0])
        assert abs(arc - full) < 1e-3 * full, ('A cut crosses a bend zone', arc, full)
        # A panel joins the bend where it shares a face with the zone across the bend line.
        grown = b['zone'].BoundingBox(); pad = [0.01 if a != b['axis'] else -0.01 for a in AXES]
        probe = cq.Solid.makeBox(grown.xlen + 2 * pad[0], grown.ylen + 2 * pad[1], grown.zlen + 2 * pad[2],
                                 cq.Vector(grown.xmin - pad[0], grown.ymin - pad[1], grown.zmin - pad[2]))
        touching = [i for i, p in enumerate(info) if p['solid'].intersect(probe).Volume() > 1e-6]
        assert len(touching) == 2, ('Bend zone must join two panels', len(touching))
        links.append((b, touching))
    root = max(range(len(info)), key=lambda i: info[i]['solid'].Volume())
    in_plane = [a for a in AXES if a != info[root]['n']]
    maps = {root: dict(P0=unit(info[root]['n']) * info[root]['mid'], E1=unit(in_plane[0]), E2=unit(in_plane[1]), F0=(0.0, 0.0), M=((1, 0), (0, 1)), flip=1,
                       top=unit(in_plane[0]).cross(unit(in_plane[1])))}
    def lin(m, v):
        a, b = v.dot(m['E1']), v.dot(m['E2'])
        return (m['M'][0][0] * a + m['M'][0][1] * b, m['M'][1][0] * a + m['M'][1][1] * b)
    def flat(m, p):
        a, b = lin(m, p - m['P0']); return (m['F0'][0] + a, m['F0'][1] + b)
    strips, table, pending = [], [], list(links)
    ba = None
    while pending:
        progress = False
        for item in list(pending):
            b, (i, j) = item
            if i in maps and j not in maps: parent, child = i, j
            elif j in maps and i not in maps: parent, child = j, i
            elif i in maps and j in maps: pending.remove(item); continue
            else: continue
            pending.remove(item); progress = True
            P, C, m = info[parent], info[child], maps[parent]
            a = unit(b['axis']); z = b['zone'].BoundingBox()
            zlo = {'x': z.xmin, 'y': z.ymin, 'z': z.zmin}; zhi = {'x': z.xmax, 'y': z.ymax, 'z': z.zmax}
            pc = P['solid'].BoundingBox().center; cc = C['solid'].BoundingBox().center; zc = z.center
            bp = next(x for x in AXES if x not in (b['axis'], P['n']))
            sp = 1 if getattr(zc, bp) > getattr(pc, bp) else -1
            bc = P['n']; sc = 1 if getattr(cc, bc) > getattr(zc, bc) else -1
            qP = cq.Vector(0, 0, 0); setattr(qP, bp, zlo[bp] if sp > 0 else zhi[bp]); setattr(qP, P['n'], P['mid'])
            qC = cq.Vector(0, 0, 0); setattr(qC, bc, zhi[bc] if sc > 0 else zlo[bc]); setattr(qC, C['n'], C['mid'])
            dP, dC = unit(bp, sp), unit(bc, sc)
            g = lin(m, dP); m1 = lin(m, a); ba = bend_allowance(t, b['r'], k)
            base = flat(m, qP)
            F0 = (base[0] + g[0] * ba, base[1] + g[1] * ba)
            up = dC.dot(m['top']) > 0
            maps[child] = dict(P0=qC, E1=a, E2=dC, F0=F0, M=((m1[0], g[0]), (m1[1], g[1])),
                               flip=1 if (m1[0] * g[1] - m1[1] * g[0]) > 0 else -1, top=dP * (-1 if up else 1))
            s0, s1 = zlo[b['axis']], zhi[b['axis']]
            plo, phi = _range(P['solid'], bp); clo, chi = _range(C['solid'], bc)
            legs = [0., 0.]
            legs[0] = round(abs(getattr(qP, bp) - (plo if sp > 0 else phi)), 4)
            legs[1] = round(abs((chi if sc > 0 else clo) - getattr(qC, bc)), 4)
            p0 = (base[0] + m1[0] * s0, base[1] + m1[1] * s0); p1 = (base[0] + m1[0] * s1, base[1] + m1[1] * s1)
            corners = [p0, p1, (p1[0] + g[0] * ba, p1[1] + g[1] * ba), (p0[0] + g[0] * ba, p0[1] + g[1] * ba)]
            strips.append(cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(x, y, 0) for x, y in corners], close=True)))
            mid = ((p0[0] + p1[0]) / 2 + g[0] * ba / 2, (p0[1] + p1[1]) / 2 + g[1] * ba / 2)
            table.append(dict(start=[round(p0[0] + g[0] * ba / 2, 4), round(p0[1] + g[1] * ba / 2, 4)],
                              end=[round(p1[0] + g[0] * ba / 2, 4), round(p1[1] + g[1] * ba / 2, 4)],
                              direction='up' if up else 'down', angle_deg=90, inside_radius_mm=b['r'],
                              bend_allowance_mm=round(ba, 4), length_mm=round(s1 - s0, 4), centre=[round(mid[0], 4), round(mid[1], 4)],
                              flat_leg_lengths_mm=legs, outside_flange_lengths_mm=[round(v + b['r'] + t, 4) for v in legs]))
        assert progress, 'Bend tree is disconnected'
    assert len(maps) == len(info), 'Some panels are not connected by bends'
    faces = []
    for i, p in enumerate(info):
        m = maps[i]; plane = [0, 0, 0]; plane[AXES.index(p['n'])] = 1
        origin = [0, 0, 0]; origin[AXES.index(p['n'])] = p['mid']
        section = p['solid'].intersect(cq.Face.makePlane(basePnt=cq.Vector(*origin), dir=cq.Vector(*plane)))
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
        moved = cq.Shape.cast(BRepBuilderAPI_Transform(section.wrapped, _rigid(m['P0'], m['E1'], m['E2'], m['F0'], m['M'], m['flip']), True).Shape())
        faces.extend(moved.Faces())
    # Orient every piece with its normal toward +Z so coplanar faces merge.
    shapes = [f if f.normalAt().z > 0 else cq.Face(f.wrapped.Reversed()) for f in faces + strips]
    flat_shape = shapes[0].fuse(*shapes[1:]).clean() if len(shapes) > 1 else shapes[0]
    flat_faces = flat_shape.Faces()
    assert len(flat_faces) == 1, ('Flat pattern is not a single connected face', len(flat_faces))
    face = flat_faces[0]; bb = face.BoundingBox()
    shift = cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin)
    face = face.translate(shift)
    # Holes closer than twice the thickness to a bend distort when the bend forms.
    near = []
    for wire in face.innerWires():
        gap = min(wire.distance(strip.translate(shift)) for strip in strips) if strips else None
        if gap is not None and gap < 2 * t - 1e-6:
            wb = wire.BoundingBox(); near.append(dict(centre=[round(wb.center.x, 3), round(wb.center.y, 3)], distance_to_bend_mm=round(gap, 3)))
    for row in table:
        for key in ('start', 'end', 'centre'):
            row[key] = [round(row[key][0] + shift.x, 4), round(row[key][1] + shift.y, 4)]
    return dict(face=face, bends=table, size_mm=[round(bb.xlen, 4), round(bb.ylen, 4)], thickness_mm=t,
                k_factor=k, area_mm2=round(face.Area(), 3), holes_near_bends=near)


FASTENER_GROUPS = ('fasteners', 'intake_fasteners', 'adapter_fasteners', 'hold_downs', 'rear_release', 'partition_screws', 'lid_screws', 'lid_guides', 'entry_fasteners')
FASTENER_TOKENS = ('nut', 'screw', 'standoff', 'washer', 'stud', 'M3', 'M4')


def sheet_parts(parts):
    """Fabricated sheet parts, using the same selection as the drawing set."""
    return [p for p in parts if p['role'] == 'fabricated' and p['group'] not in FASTENER_GROUPS
            and (not any(t in p['name'] for t in FASTENER_TOKENS) or '_guide_strip_' in p['name'])]


def move_part(part, fn):
    """Apply one rigid placement to a part and its formed pieces."""
    q = dict(part); q['shape'] = fn(part['shape'])
    if part.get('pieces'):
        q['pieces'] = [dict(piece, shape=fn(piece['shape']), bends=transform_bends(piece['bends'], fn),
                            tapped=[dict(h, centre=list(_point(fn, h['centre']))) for h in piece.get('tapped', [])]) for piece in part['pieces']]
    if part.get('tapped'):
        q['tapped'] = [dict(h, centre=list(_point(fn, h['centre']))) for h in part['tapped']]
    return q


def _point(fn, xyz):
    """Apply a part transform to a point; trimming functions such as cuts leave points in place."""
    moved = fn(cq.Vertex.makeVertex(*xyz)).Vertices()
    if len(moved) != 1: return tuple(xyz)
    c = moved[0].Center()
    return round(c.x, 3), round(c.y, 3), round(c.z, 3)


def _add_bend_lines(path, bends):
    """Mark bend centrelines as dashed lines on the cut layer and declare millimetre units."""
    import ezdxf
    doc = ezdxf.readfile(str(path))
    if 'DASHED' not in doc.linetypes:
        doc.linetypes.add('DASHED', pattern=[6.0, 4.0, -2.0], description='Bend centreline')
    doc.header['$INSUNITS'] = 4; doc.header['$MEASUREMENT'] = 1
    msp = doc.modelspace()
    for b in bends:
        msp.add_line(tuple(b['start']), tuple(b['end']), dxfattribs={'layer': '0', 'linetype': 'DASHED'})
    doc.saveas(str(path))


def export_flat_patterns(parts, out):
    """Write one developed DXF per sheet piece and a JSON bend schedule."""
    import json
    from pathlib import Path
    folder = Path(out) / 'flat_patterns'; folder.mkdir(parents=True, exist_ok=True)
    records = []
    for p in sheet_parts(parts):
        pieces = p.get('pieces') or [dict(name=p['name'], shape=p['shape'], t=None, bends=[], tapped=p.get('tapped', []))]
        for piece in pieces:
            b = bounds(piece['shape'])
            t = piece['t'] or round(min(b[i + 3] - b[i] for i in range(3)), 4)
            record = dict(part=p['name'], piece=piece['name'], thickness_mm=t, bend_count=len(piece['bends']))
            try:
                result = unfold(piece['shape'], piece['bends'], t)
            except AssertionError as error:
                records.append(record | dict(developed=False, reason=str(error))); continue
            path = folder / (piece['name'] + '.dxf')
            cq.exporters.export(cq.Workplane().add(result['face']), str(path))
            _add_bend_lines(path, result['bends'])
            # The formed piece, moved to its own origin, is the fabricator's 3D reference.
            lo = bounds(piece['shape'])
            cq.exporters.export(piece['shape'].translate(cq.Vector(-lo[0], -lo[1], -lo[2])), str(folder / (piece['name'] + '.step')))
            records.append(record | dict(developed=True, dxf=path.name, flat_size_mm=result['size_mm'], flat_area_mm2=result['area_mm2'],
                                         k_factor=result['k_factor'], bends=result['bends'], holes_near_bends=result['holes_near_bends'],
                                         tapped_holes=piece.get('tapped', [])))
    (folder / 'flat_patterns.json').write_text(json.dumps(records, indent=2))
    return records


def _overlap(a, b):
    x, y = a.BoundingBox(), b.BoundingBox()
    if x.xmax < y.xmin or y.xmax < x.xmin or x.ymax < y.ymin or y.ymax < x.ymin or x.zmax < y.zmin or y.zmax < x.zmin:
        return 0.
    return a.intersect(b).Volume()


def fastener_sheet_intersections(parts):
    """Fastener solids that overlap a sheet part, except screws in tapped shelf threads."""
    sheets = sheet_parts(parts); names = {p['name'] for p in sheets}
    fasteners = [p for p in parts if p['name'] not in names and (p['group'] in FASTENER_GROUPS or any(t in p['name'] for t in FASTENER_TOKENS))]
    hits = []
    for f in fasteners:
        for s in sheets:
            tapped = f['name'].endswith('_M3x5_screw') and f['name'].startswith(('GPU_', 'Auxiliary_')) and 'rear' in s['name']
            if tapped or f.get('thread_host') == s['name']: continue
            v = _overlap(f['shape'], s['shape'])
            if v > 1e-3: hits.append(dict(fastener=f['name'], sheet_part=s['name'], volume_mm3=round(v, 4)))
    return hits


def formed_part_report(parts, out):
    """Export flat patterns and record development and fastener-clearance results."""
    import json
    from pathlib import Path
    records = export_flat_patterns(parts, out)
    report = dict(inside_bend_radius='equal to sheet thickness', k_factor=K_FACTOR,
                  developed_pieces=sum(r['developed'] for r in records),
                  undeveloped=[dict(part=r['part'], piece=r['piece'], reason=r['reason']) for r in records if not r['developed']],
                  minimum_flange_rule='outside flange length at least 4 x thickness for standard V-die air bending',
                  short_flanges=[dict(piece=r['piece'], bend=i + 1, outside_flange_lengths_mm=b['outside_flange_lengths_mm'], minimum_mm=4 * r['thickness_mm'])
                                 for r in records if r['developed'] for i, b in enumerate(r['bends']) if min(b['outside_flange_lengths_mm']) < 4 * r['thickness_mm'] - 1e-6],
                  holes_near_bends=[dict(piece=r['piece'], **h) for r in records if r['developed'] for h in r['holes_near_bends']],
                  fastener_sheet_intersections=fastener_sheet_intersections(parts))
    intended, unexpected = assembly_overlaps(parts)
    report['intended_overlap_count'] = len(intended)
    report['unexpected_overlaps'] = unexpected
    (Path(out) / 'formed_part_checks.json').write_text(json.dumps(report, indent=2))
    (Path(out) / 'assembly_overlaps.json').write_text(json.dumps(dict(intended=intended, unexpected=unexpected), indent=2))
    assert not report['undeveloped'], ('Sheet pieces did not develop', report['undeveloped'])
    assert not report['fastener_sheet_intersections'] and not unexpected, ('Assembly collisions', report['fastener_sheet_intersections'], unexpected)
    return report


ROUTING_GROUPS = ('power', 'mcio', 'hoses', 'external_route')


def assembly_overlaps(parts):
    """Every overlapping pair of solids, classed as intended or unexpected.

    Intended overlaps are thread engagement (screws in the tapped GPU shelf,
    self-tapping screws in fan frames) and routing envelopes, which describe
    cable and hose occupancy rather than solid parts.
    """
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    solids = [p for p in parts if p['role'] != 'clearance' and p['group'] not in ('board_alternatives', 'oem_cage')]
    boxes = []
    for p in solids:
        b = Bnd_Box(); BRepBndLib.Add_s(p['shape'].wrapped, b); boxes.append(b.Get())
    intended, unexpected = [], []
    for i, a in enumerate(solids):
        ba = boxes[i]
        for j in range(i + 1, len(solids)):
            bb_ = boxes[j]
            if ba[3] < bb_[0] or bb_[3] < ba[0] or ba[4] < bb_[1] or bb_[4] < ba[1] or ba[5] < bb_[2] or bb_[5] < ba[2]:
                continue
            b = solids[j]
            v = a['shape'].intersect(b['shape']).Volume()
            if v <= 1e-3:
                continue
            names = (a['name'], b['name']); groups = (a['group'], b['group'])
            thread = (any(n.endswith('_M3x5_screw') and n.startswith(('GPU_', 'Auxiliary_')) for n in names) and any('rear' in n for n in names)) \
                or a.get('thread_host') == b['name'] or b.get('thread_host') == a['name']
            fan = any('_self_tapping_5x10_screw_' in n for n in names) and any(g in ('fans', 'fan_pads', 'exhaust') for g in groups)
            route = any(g in ROUTING_GROUPS for g in groups)
            row = dict(parts=list(names), volume_mm3=round(v, 4))
            (intended if (thread or fan or route) else unexpected).append(row | dict(reason='thread engagement' if thread else 'fan screw thread' if fan else 'routing envelope' if route else 'collision'))
    return intended, unexpected

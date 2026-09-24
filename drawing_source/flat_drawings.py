"""Developed flat-pattern sheets: blank outline, cutouts, bend lines and bend table."""
import json
import cadquery as cq


def cut_faces(path):
    """Faces of a flat-pattern DXF built from its cut geometry only."""
    import ezdxf, tempfile, os
    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    for e in [e for e in msp if e.dxf.get('linetype', '').upper() == 'DASHED']:
        msp.delete_entity(e)
    fd, tmp = tempfile.mkstemp(suffix='.dxf'); os.close(fd)
    try:
        doc.saveas(tmp)
        return cq.importers.importDXF(tmp).faces().vals()
    finally:
        os.unlink(tmp)


def flat_pattern_pages(part_name, root, api):
    """Draw one sheet per developed piece of the named part; return the piece count."""
    from annotated_geometry import planar, INK
    from section_drawings import fmt
    c, new, para, table, view, W, H, out = api
    index = root / 'flat_patterns' / 'flat_patterns.json'
    if not index.exists():
        return 0
    records = [r for r in json.loads(index.read_text()) if r['part'] == part_name and r['developed']]
    for r in records:
        # Drawing from the DXF shows exactly the blank supplied for cutting; dashed bend lines are drawn separately.
        faces = cut_faces(root / 'flat_patterns' / r['dxf'])
        assert len(faces) == 1, (r['piece'], len(faces))
        face = faces[0]
        new(part_name.replace('_', ' ') + ' | flat pattern' + ('' if r['piece'] == part_name else ' | ' + r['piece'].replace('_', ' ')), part_name + '::flat')
        size = r['flat_size_mm']
        para(f"Developed blank {fmt(size[0])} × {fmt(size[1])} × {fmt(r['thickness_mm'])} thick; area {fmt(r['flat_area_mm2'])} mm². "
             f"Bend allowance uses K-factor {r['k_factor']} and the listed inside radius. Dashed lines are bend centrelines; UP bends toward the viewer of this sheet. "
             f"Cut every hole and cutout in the flat blank; file flat_patterns/{r['dxf']}. Confirm radius and K-factor with the forming tooling before cutting.",
             32, H - 82, W - 64, 10)
        p, lo, hi = planar(c, face, 2, 0, (35, 150, 700, 520))
        c.setStrokeColor(INK); c.setDash(6, 3); c.setLineWidth(.6)
        for i, b in enumerate(r['bends'], 1):
            x0, y0 = p(*b['start']); x1, y1 = p(*b['end']); c.line(x0, y0, x1, y1)
            c.setFont('Helvetica-Bold', 9); c.drawString((x0 + x1) / 2 + 4, (y0 + y1) / 2 + 4, f'B{i}')
        c.setDash()
        if r['bends']:
            rows = [['Bend', 'Direction', 'Angle', 'Inside R', 'Allowance', 'Length', 'Outside flanges']]
            rows += [[f'B{i}', b['direction'].upper(), f"{b['angle_deg']}°", fmt(b['inside_radius_mm']), fmt(b['bend_allowance_mm']), fmt(b['length_mm']),
                      ' / '.join(fmt(v) for v in b['outside_flange_lengths_mm'])] for i, b in enumerate(r['bends'], 1)]
            table(rows, 760, H - 150, [42, 62, 42, 55, 62, 55, 85], 9)
        else:
            para('Flat part; no bends.', 760, H - 150, 380, 10)
        near = r.get('holes_near_bends', [])
        if near:
            para(f"{len(near)} cutout(s) lie closer than twice the thickness to a bend line; minimum {fmt(min(h['distance_to_bend_mm'] for h in near))} mm. "
                 "Confirm distortion allowance with the fabricator.", 760, 200, 380, 9)
    return len(records)

"""Permanent mesh-to-frame joints, separate from removable cover screws."""
from manufacturing_revision import add
from mounting_hardware import cyl, union
from sheetmetal import bounds


def apply(parts, report):
    frame = next(p for p in parts if p['name'] == 'Front_full_face_mesh_clamping_frame')
    mesh = next(p for p in parts if p['name'] == 'Stock_hex_perforated_mesh_cut_to_size')
    if mesh.get('rivet_holes_xz'):
        return
    b = bounds(frame['shape']); z0, z1 = b[2], b[5]
    modular = report['configuration'].startswith('modular')
    sides = [z0+65, z0+135] if modular else [75, 190, 320]
    points = [(x,z) for x in (12.,428.) for z in sides]
    edge_x = (60.,160.,280.,380.) if modular else (80.,220.,360.)
    points += [(x,z) for x in edge_x for z in (z0+12,z1-12)]
    bores = [cyl(x,b[1]-1,z,1.65,6,(0,1,0)) for x,z in points]
    frame['shape'] = frame['shape'].cut(*bores)
    mesh['shape'] = mesh['shape'].cut(*bores)
    for i,(x,z) in enumerate(points,1):
        # The manufactured head faces the fans. This bounds the inward
        # projection independently of the variable formed tail on the outside.
        washer = cyl(x,-3.8,z,4.5,.8,(0,1,0)).cut(cyl(x,-4,z,1.6,2,(0,1,0)))
        rivet = union([cyl(x,-3,z,3.25,.8,(0,1,0)),
                       cyl(x,b[1],z,1.6,-3-b[1],(0,1,0)),
                       cyl(x,b[1]-3,z,3.25,3,(0,1,0))])
        add(parts,f'Front_cover_rivet_{i}',rivet,'intake_grilles',catalog='97447A801',
            specification='3.2 mm aluminum blind rivet, grip 1.5-3.5 mm; install from mesh side',
            notes='Outside formed tail shown as a DIA 6.5 x 3 mm clearance envelope; verify set rivet on a coupon.')
        add(parts,f'Front_cover_rivet_large_washer_{i}',washer,'intake_grilles',catalog='91116A120')
    mesh['rivet_holes_xz'] = points
    frame['rivet_holes_xz'] = points
    frame['notes'] = 'Rivet stock mesh to frame on a bench. Remove the completed front cover using the separate M3 screws.'
    report['riveted_front_cover'] = dict(
        rivet='97447A801', washer='91116A120', quantity=len(points),
        hole_diameter_mm=3.3, points_xz_mm=points, grip_stack_mm=3.2144,
        allowed_grip_mm=[1.5,3.5], inward_projection_from_mesh_mm=1.6,
        rivet_head_to_carrier_mm=2.2, outside_tail_envelope_mm=[6.5,3],
        installation='Fit each rivet from the mesh side through a large washer, mesh and frame. Pull with the cover off the chassis. The formed tail faces outside.',
        qualification='Check actual washer bore, grip stack and formed tail on a coupon before riveting the cover.')

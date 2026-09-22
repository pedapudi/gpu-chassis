"""Form the GPU retention shelf into the rear panel without moving card datums."""
import cadquery as cq


def box(x, y, z, dx, dy, dz):
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def consolidate_gpu_rear(parts, out=None):
    rear = next(p for p in parts if p['name'] == 'Full_width_twenty_slot_rear_with_side_returns')
    shelf = next(p for p in parts if p['name'] == 'Upper_bank_retention_flange')
    # Analytic faces define the dimensions; tessellation bounds have edge tolerance.
    faces = [f for f in shelf['shape'].Faces() if abs(f.normalAt().z) > .999]
    top = max(f.Center().z for f in faces)
    bottom = min(f.Center().z for f in faces)
    rear_y = min(v.Center().y for v in rear['shape'].Vertices())
    x0 = min(v.Center().x for v in shelf['shape'].Vertices())
    x1 = max(v.Center().x for v in shelf['shape'].Vertices())
    end_y = max(v.Center().y for v in shelf['shape'].Vertices())
    thickness, inside_radius = 1.2, 1.2
    outside_radius = thickness + inside_radius
    cy, cz = rear_y + outside_radius, top - outside_radius
    # The quarter annulus joins the vertical web to the outward horizontal shelf.
    outer = cq.Solid.makeCylinder(outside_radius, x1-x0, cq.Vector(x0,cy,cz), cq.Vector(1,0,0))
    inner = cq.Solid.makeCylinder(inside_radius, x1-x0+2, cq.Vector(x0-1,cy,cz), cq.Vector(1,0,0))
    bend = outer.cut(inner).intersect(box(x0,rear_y,cz,x1-x0,outside_radius,outside_radius))
    panel = rear['shape'].cut(box(x0,rear_y-.1,cz,x1-x0,outside_radius+.2,outside_radius+.2))
    flat = box(x0,cy,top-thickness,x1-x0,end_y-cy,thickness)
    panel = panel.fuse(bend,flat)
    axes=[]
    for p in parts:
        if p['name'].startswith('GPU_') and p['name'].endswith('_captive_6_32_hex_nut'):
            p['shape'] = p['shape'].translate((0,0,(top-thickness)-bottom))
            centre = p['shape'].Center(); axes.append((centre.x,centre.y))
    for x,y in axes:
        panel = panel.cut(cq.Solid.makeCylinder(1.95,5,cq.Vector(x,y,top-3)))
        # Each relief clears the standard hex nut and interrupts the bend locally.
        panel = panel.cut(box(x-5,rear_y-1,top-1.5-2.778-.5,10,4,3.578))
    panel = panel.clean()
    assert panel.isValid() and len(panel.Solids()) == 1, 'GPU rear panel must be one connected formed sheet'
    rear['shape'] = panel
    parts.remove(shelf)
    if out is not None:
        from pathlib import Path
        face = max((f for f in panel.Faces() if abs(f.Center().y-rear_y)<1e-5), key=lambda f:f.Area())
        cq.exporters.export(cq.Workplane().newObject(face.rotate((0,0,0),(1,0,0),90).Wires()), str(Path(out)/'cut_profiles/upper_rear_face_no_returns.dxf'))
    return gpu_rear_panel_design(parts)


def gpu_rear_panel_design(parts):
    rear=next(p['shape'] for p in parts if p['name']=='Full_width_twenty_slot_rear_with_side_returns')
    top=max(f.Center().z for f in rear.Faces() if f.geomType()=='PLANE' and abs(f.normalAt().z)>.999)
    axes=sorted((p['shape'].Center().x,p['shape'].Center().y) for p in parts if p['name'].startswith('GPU_') and p['name'].endswith('_captive_6_32_hex_nut'))
    return {'sheet_thickness_mm':1.2,'top_bend_inside_radius_mm':1.2,
            'top_bend_outside_radius_mm':2.4,'top_bend_angle_deg':90,
            'retention_top_z_mm':top,'retention_hole_diameter_mm':3.9,
            'retention_hole_axes_xy_mm':axes,'retention_integral':True,
            'toe_receiver':'Separate 1.5 mm comb strip, factory stitch welded before tray assembly',
            'toe_weld':'1 mm nominal fillet leg, 6 mm long at each of 19 inter-slot midpoints; underside only; qualify distortion and strength'}

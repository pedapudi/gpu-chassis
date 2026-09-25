"""Form the GPU retention shelf into the rear panel without moving card datums."""
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from sheetmetal import fold,bounds

REAR = 'Full_width_twenty_one_slot_rear_with_side_returns'
THICKNESS, INSIDE_RADIUS = 1.2, 1.2
# #6-32 UNC-2B tapped in an extruded collar: #36 tap drill, 2.5 mm total thread length.
TAP_DRILL, COLLAR_OD, COLLAR_HEIGHT = 2.705, 4.1, 1.3


def box(x, y, z, dx, dy, dz):
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def retention_axes(parts):
    """GPU-bank bracket screw axes (X, Y), sorted by X."""
    screws = [p['shape'].BoundingBox() for p in parts
              if p['name'].startswith(('GPU_', 'Auxiliary_')) and p['name'].endswith('_6_32_screw')]
    return sorted((b.center.x, b.center.y) for b in screws)


def consolidate_gpu_rear(parts, out=None):
    rear = next(p for p in parts if p['name'] == REAR)
    shelf = next(p for p in parts if p['name'] == 'Upper_bank_retention_flange')
    # Analytic faces define the dimensions; tessellation bounds have edge tolerance.
    faces = [f for f in shelf['shape'].Faces() if abs(f.normalAt().z) > .999]
    top = max(f.Center().z for f in faces)
    rear_y = min(v.Center().y for v in rear['shape'].Vertices())
    end_y = max(v.Center().y for v in shelf['shape'].Vertices())
    # Exact bounds locate the formed edges; a loose box leaves slivers across the reliefs.
    xmin, _, zmin, xmax = bounds(rear['shape'])[:4]
    zone = THICKNESS + INSIDE_RADIUS
    # Each side return ends one thickness below the shelf bend zone. A relief slot across the
    # return bend zone separates the two bends; the shelf still reaches the return's inner face.
    return_top = top - zone - THICKNESS
    x0, x1 = xmin + THICKNESS, xmax - THICKNESS
    notches = [box(xmin - 1, rear_y - 1, return_top, THICKNESS + 1, 20, 10), box(x1, rear_y - 1, return_top, THICKNESS + 1, 20, 10),
               box(xmin - 1, rear_y - 1, return_top, zone + 1.5, 20, THICKNESS), box(xmax - zone - .5, rear_y - 1, return_top, zone + 1.5, 20, THICKNESS)]
    # Overlapping tools in one compound make the boolean unreliable, so cut them in turn.
    panel = rear['shape']
    for notch in notches:panel = panel.cut(notch)
    assert panel.intersect(box(xmin, rear_y, return_top, THICKNESS, 14, 4)).Volume() < 1e-6, 'Corner relief was not cut'
    panel = panel.fuse(box(x0, rear_y, top - THICKNESS, x1 - x0, end_y - rear_y, THICKNESS))
    bends = []
    panel = fold(panel, bends, 'z', (xmin, rear_y), (1, 1), THICKNESS, INSIDE_RADIUS, span=(zmin, return_top))
    panel = fold(panel, bends, 'z', (xmax, rear_y), (-1, 1), THICKNESS, INSIDE_RADIUS, span=(zmin, return_top))
    panel = fold(panel, bends, 'x', (rear_y, top), (1, -1), THICKNESS, INSIDE_RADIUS, span=(x0, x1))
    axes = retention_axes(parts)
    underside = top - THICKNESS
    collars = [cq.Solid.makeCylinder(COLLAR_OD/2, COLLAR_HEIGHT, cq.Vector(x,y,underside-COLLAR_HEIGHT)) for x,y in axes]
    bores = [cq.Solid.makeCylinder(TAP_DRILL/2, THICKNESS+COLLAR_HEIGHT+2, cq.Vector(x,y,underside-COLLAR_HEIGHT-1)) for x,y in axes]
    panel = panel.fuse(*collars).cut(cq.Compound.makeCompound(bores)).clean()
    assert panel.isValid() and len(panel.Solids()) == 1, 'GPU rear panel must be one connected formed sheet'
    # Below the bend every web between apertures must still carry the shelf.
    # Sample inside the aperture band: each web between apertures must reach the bend intact.
    below = panel.intersect(cq.Face.makePlane(basePnt=cq.Vector(0,0,top-6),dir=cq.Vector(0,0,1)))
    assert len(below.Faces()) == len(axes)+1, ('Shelf is detached from the webs', len(below.Faces()))
    rear['shape'] = panel
    # Collars are extruded after cutting, so the flat pattern marks each collar at its tap-drill
    # diameter; the fabricator's extrusion tooling sets the actual pierce size.
    flat = panel.cut(cq.Compound.makeCompound([cq.Solid.makeCylinder(COLLAR_OD/2 + .01, COLLAR_HEIGHT + .01, cq.Vector(x,y,underside-COLLAR_HEIGHT-.01)) for x,y in axes]))
    rear['pieces'] = [dict(name=REAR, shape=flat, t=THICKNESS, bends=bends,
                           tapped=[dict(thread='6-32', centre=[round(x, 3), round(y, 3), round(underside, 3)]) for x, y in axes])]
    parts.remove(shelf)
    if out is not None:
        from pathlib import Path
        face = max((f for f in panel.Faces() if abs(f.Center().y-rear_y)<1e-5), key=lambda f:f.Area())
        cq.exporters.export(cq.Workplane().newObject(face.rotate((0,0,0),(1,0,0),90).Wires()), str(Path(out)/'cut_profiles/upper_rear_face_no_returns.dxf'))
    return gpu_rear_panel_design(parts)


def gpu_rear_panel_design(parts):
    rear=next(p['shape'] for p in parts if p['name']==REAR)
    toe=next(p['shape'].BoundingBox() for p in parts if p['name']=='Upper_bank_toe_receiver')
    top=max(f.Center().z for f in rear.Faces() if f.geomType()=='PLANE' and abs(f.normalAt().z)>.999)
    def shelf_bend(f):
        c=BRepAdaptor_Surface(f.wrapped).Cylinder()
        return abs(c.Radius()-THICKNESS-INSIDE_RADIUS)<1e-6 and abs(c.Axis().Direction().X())>.999
    bend=[f.BoundingBox() for f in rear.Faces() if f.geomType()=='CYLINDER' and shelf_bend(f)]
    axes=retention_axes(parts)
    return {'sheet_thickness_mm':THICKNESS,'top_bend_inside_radius_mm':INSIDE_RADIUS,
            'top_bend_outside_radius_mm':THICKNESS+INSIDE_RADIUS,'top_bend_angle_deg':90,
            'bend_span_x_mm':[min(b.xmin for b in bend),max(b.xmax for b in bend)],
            'retention_top_z_mm':top,'retention_thread':'#6-32 UNC-2B, tapped through an extruded collar',
            'tap_drill_diameter_mm':TAP_DRILL,'collar_outside_diameter_mm':COLLAR_OD,
            'collar_height_below_shelf_mm':COLLAR_HEIGHT,'thread_length_mm':THICKNESS+COLLAR_HEIGHT,
            'retention_hole_axes_xy_mm':axes,'retention_integral':True,
            'toe_receiver_x_mm':[toe.xmin,toe.xmax],
            'toe_receiver':'Separate 1.5 mm comb strip, factory stitch welded before tray assembly',
            'toe_weld':f'1 mm nominal fillet leg, 6 mm long at each of {len(axes)-1} inter-slot midpoints; underside only; qualify distortion and strength'}

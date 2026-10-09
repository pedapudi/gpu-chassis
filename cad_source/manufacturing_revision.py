"""Replace adjustable PCB rails and custom punched grilles in analytic assemblies.

The steel GPU tray carries the load. Two printed adapters locate metric
spacers and heat-set inserts; changing the PCB pattern changes only the print.
All coordinates are exported assembly coordinates, in millimeters.
"""
import io
import json
import math
import pickle
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

from mounting_hardware import box, cyl, screw, union, orient
from sheetmetal import bounds, fold, sheet_parts

VARIANTS = ('nine-u', 'nine-u-180', 'nine-u-120', 'modular', 'modular-120-80', 'modular-180')
PRINT_THICKNESS = 8.5
SPACER_HEIGHT = 8.0
PEM = {'M3': dict(hole=4.22, od=6.35, height=1.5, shank=.97, diameter=3., edge=4.8, stock='95185A530'),
       'M4': dict(hole=5.41, od=7.87, height=2., shank=.97, diameter=4., edge=6.9, stock='95185A590')}


def load(folder):
    rows = pickle.loads((Path(folder) / 'parts.brep.pickle').read_bytes())
    for p in rows:
        p['shape'] = cq.Shape.importBrep(io.BytesIO(p.pop('brep')))
    return rows


def save(parts, folder):
    rows = []
    for p in parts:
        q = {k:v for k,v in p.items() if k not in ('shape', 'pieces')}
        buf = io.BytesIO(); p['shape'].exportBrep(buf); q['brep'] = buf.getvalue(); rows.append(q)
    (Path(folder) / 'parts.brep.pickle').write_bytes(pickle.dumps(rows))


def step_shape(part):
    """Purchased mesh STEP controls only the cut blank and assembly holes."""
    if not part['name'].startswith('Stock_hex_'):return part['shape']
    b=bounds(part['shape']);shape=box(*b[:3],b[3]-b[0],b[4]-b[1],b[5]-b[2])
    if part.get('corner_radius_mm'):
        shape=cq.Workplane(obj=shape).edges('|Y').fillet(part['corner_radius_mm']).val()
    for x,z,w,h in part.get('blank_notches_xz',[]):
        shape=shape.cut(box(x,b[1]-1,z,w,b[4]-b[1]+2,h))
    holes = [cyl(x,b[1]-1,z,1.7,b[4]-b[1]+2,(0,1,0)) for x,z in part['mounting_holes_xz']]
    holes += [cyl(x,b[1]-1,z,1.65,b[4]-b[1]+2,(0,1,0)) for x,z in part.get('rivet_holes_xz',[])]
    return shape.cut(cq.Compound.makeCompound(holes))


def add(parts, name, shape, group='hardware', role='purchased', moving=False, color='#71808b', **data):
    assert shape.isValid() and shape.Volume() > 0, name
    p = dict(name=name, shape=shape, group=group, role=role, moving=moving, visible=True, color=color, **data)
    parts.append(p)
    return p


def clinch_shape(point, axis, thread):
    """Point is the sheet face on the nut side; axis points into the sheet."""
    s = PEM[thread]
    body = union([cyl(0,0,-s['height'],s['od']/2,s['height']), cyl(0,0,0,(s['hole']-.03)/2,s['shank'])])
    return orient(body.cut(cyl(0,0,-s['height']-1,s['diameter']/2,s['height']+s['shank']+2)),point,axis)


def replace_supports(parts):
    tray = next(p for p in parts if p['name']=='GPU_tray_two_side_bends')
    tb = bounds(tray['shape']); z = tb[2]; top = z + 1.5
    # Remove only the four embossed rail bosses; restore the continuous tray floor.
    for x in (20.,420.):
        for y in (208.2,458.2):
            tray['shape'] = tray['shape'].cut(cyl(x,y,z-.1,10.05,6.3)).fuse(cyl(x,y,z,10.05,1.5)).clean()
    remove = ('Longitudinal_mount_rail_', 'Rail_', 'Sliding_crossbar_', 'Crossbar_',
              'Standoff_lower_', 'M3_8mm_female_female_standoff_', 'Backplane_M3x6_')
    parts[:] = [p for p in parts if not p['name'].startswith(remove)]
    tray.pop('tapped', None)
    pcb = next(p for p in parts if p['name']=='Miwin_MG_SW510B_429x225_PCB_photo_reference')
    pcb_z = bounds(pcb['shape'])[2]
    assert abs(top + PRINT_THICKNESS + SPACER_HEIGHT - pcb_z) < 1e-5
    points = [(357.,225.),(92.6,225.),(275.5,318.5),(148.5,318.5),(275.5,434.2),(148.5,434.2)]
    fixing = [(x,y) for x in (25.,209.5,230.5,415.) for y in (220.,439.)]
    for side, x0, x1 in [('left',10.,219.5),('right',220.5,430.)]:
        plate = box(x0,208.2,top,x1-x0,240.,PRINT_THICKNESS)
        # Windows leave continuous perimeter and broad webs beneath all PCB posts.
        for yy,dd in ((241.,56.),(337.,72.)):
            plate = plate.cut(box(x0+20,yy,top-1,x1-x0-40,dd,PRINT_THICKNESS+2))
        pts = [(x,y) for x,y in points if x0 < x < x1]
        for x,y in pts:
            # A 6.7 mm blind pilot leaves 1 mm below the 5.7 mm insert.
            plate = plate.cut(cyl(x,y,top+PRINT_THICKNESS-6.7,2.,6.8))
        for x,y in fixing:
            if x0 < x < x1: plate = plate.cut(cyl(x,y,top-1,1.7,PRINT_THICKNESS+2))
        add(parts,'Printed_backplane_adapter_'+side,plate,'printed_adapter','fabricated',True,'#657ca0',
            material='Unfilled flame-retardant PC; qualify printed material and hot creep',thickness_mm=PRINT_THICKNESS,
            board_holes_xy=pts, mounting_holes_xy=[p for p in fixing if x0<p[0]<x1],
            notes='Blind 4.0 mm insert pilots, 6.7 mm deep from top; coupon-test fit. Print flat, six walls and solid local bosses.')
    for i,(x,y) in enumerate(points,1):
        ins_top = top + PRINT_THICKNESS
        insert = cyl(x,y,ins_top-5.7,2.,5.7).cut(cyl(x,y,ins_top-6,1.5,7))
        add(parts,f'Backplane_heat_insert_M3_{i}',insert,moving=True,color='#bc9d62',catalog='94459A140')
        spacer = cyl(x,y,ins_top,3.,8.).cut(cyl(x,y,ins_top-1,1.6,10.))
        add(parts,f'Backplane_metric_spacer_8mm_{i}',spacer,'standoffs',moving=True,catalog='92871A011')
        add(parts,f'Backplane_M3x16_screw_{i}',screw((x,y,pcb_z+3),(0,0,-1),'M3',16),moving=True,
            thread_host=f'Backplane_heat_insert_M3_{i}')
    for i,(x,y) in enumerate(fixing,1):
        tray['shape'] = tray['shape'].cut(cyl(x,y,z-1,PEM['M3']['hole']/2,4))
        add(parts,f'Adapter_tray_PEM_M3_{i}',clinch_shape((x,y,z),(0,0,1),'M3'),moving=True,catalog='95185A530',thread_host=tray['name'])
        add(parts,f'Adapter_M3x12_screw_{i}',screw((x,y,top+PRINT_THICKNESS),(0,0,-1),'M3',12),moving=True,thread_host=f'Adapter_tray_PEM_M3_{i}')
    tray['press_fit_holes'] = [dict(centre=[x,y,z],diameter=4.22,thread='M3',axis=[0,0,1]) for x,y in fixing]
    return dict(plate_thickness_mm=PRINT_THICKNESS,spacer_height_mm=8.,tray_top_z_mm=top,PCB_underside_z_mm=pcb_z,
                insert='94459A140',spacer='92871A011',PCB_screw='M3 x 16',PCB_screw_insert_engagement_mm=5.,
                insert_bottom_clearance_mm=1.,mounting_points=fixing,PCB_points=points,
                plate_segment_size_mm=[209.5,240.,8.5],print_bed_mm=[256,256],brim_mm=5,
                print_hole_positions='Provisional PCB photo-derived positions; measure actual board before printing')


def replace_grille(parts, modular):
    grilles = [p for p in parts if p['group']=='intake_grilles']
    assert len(grilles)==1
    old = grilles[0]; b = bounds(old['shape']); z0,z1=b[2],b[5]; h=z1-z0
    parts.remove(old)
    # Remove old front grille screws and their threaded collars from the front face.
    old_screws = [p for p in parts if p['name'].startswith(('Grille_M3','Intake_grille_M3'))]
    hosts={tuple(round((bounds(p['shape'])[k]+bounds(p['shape'])[k+3])/2,3) for k in (0,2)):p.get('thread_host') for p in old_screws}
    parts[:] = [p for p in parts if p not in old_screws]
    # A full-face clamping frame hides all cut mesh edges. Only rectangular blanks
    # and assembly holes are cut; stock perforations are never custom-punched.
    fixes = ([(20.,z0+8.75),(220.,z0+8.75),(420.,z0+8.75),(7.5,z0+202.75),(432.5,z0+202.75)] if modular
             else [(x,z) for x in (15.,425.) for z in (32.,138.,270.,383.)])
    thickness=.9144  # Catalog 20 ga / 0.036 in; purchased stock, all assembly dimensions metric.
    mesh_back=-3.8
    mesh_front=mesh_back-thickness
    frame_front=mesh_front-1.5
    frame=box(0,frame_front,z0,440,1.5,h).cut(box(20,frame_front-1,z0+20,400,4,h-40))
    # Cut-to-size stock has no individually specified perforation origin.
    mesh=box(4,mesh_front,z0+4,432,thickness,h-8)
    # Hexagonal stock pattern: 6.35 across flats; 7.1374 pitch; nominal 79% open.
    holes=[]; pitch=7.1374; dy=pitch*math.sqrt(3)/2
    for row in range(int((h-8)/dy)+1):
        zz=z0+4+row*dy
        for col in range(62):
            xx=4+col*pitch+(row%2)*pitch/2
            if not (24<xx<416 and z0+24<zz<z1-24): continue
            vertices=[(xx+6.35/math.sqrt(3)*math.cos(math.radians(30+60*k)),zz+6.35/math.sqrt(3)*math.sin(math.radians(30+60*k))) for k in range(6)]
            wire=cq.Workplane('XZ').polyline(vertices).close().val().translate((0,mesh_front,0))
            holes.append(wire)
    holes += [cq.Wire.makeCircle(1.7,cq.Vector(x,mesh_front,z),cq.Vector(0,1,0)) for x,z in fixes]
    outer=cq.Workplane('XZ').polyline([(4,z0+4),(436,z0+4),(436,z1-4),(4,z1-4)]).close().val().translate((0,mesh_front,0))
    mesh=cq.Solid.extrudeLinear(outer,holes,cq.Vector(0,thickness,0))
    for x,z in fixes:
        frame=frame.cut(cyl(x,frame_front-1,z,1.7,5,(0,1,0)))
        spacer=cyl(x,-3,z,3,3,(0,1,0)).cut(cyl(x,-4,z,1.6,5,(0,1,0)))
        washer=cyl(x,-3.8,z,4.5,.8,(0,1,0)).cut(cyl(x,-4,z,1.6,2,(0,1,0)))
        add(parts,f'Front_cover_metric_3mm_spacer_{x}_{z}',spacer,'intake_fasteners',catalog='92871A003')
        add(parts,f'Front_cover_M3_large_washer_{x}_{z}',washer,'intake_fasteners',specification='ISO 7093 M3, 9 mm OD x 0.8 mm')
        add(parts,f'Front_frame_M3x12_{x}_{z}',screw((x,frame_front,z),(0,1,0),'M3',12),'intake_fasteners',thread_host=hosts.get((round(x,3),round(z,3))))
    add(parts,'Front_full_face_mesh_clamping_frame',frame,'intake_grilles','fabricated',color='#304553',thickness_mm=1.5,
        notes='Remove frame and mesh for fan screw access. No fan load transfers through mesh.')
    add(parts,'Stock_hex_perforated_mesh_cut_to_size',mesh,'intake_grilles','fabricated',color='#88949a',thickness_mm=thickness,
        catalog='92725T3',notes='Cut stock mesh; visible pattern is illustrative. Concealed perforations are omitted from CAD. Deburr all cut edges.',
        blank_size_mm=[432.,h-8],mounting_holes_xz=fixes)
    return dict(stock='92725T3',thickness_mm=thickness,open_area_percent=79,hex_across_flats_mm=6.35,pitch_mm=pitch,
                cut_size_mm=[432.,h-8],frame_size_mm=[440,h,1.5],assembly_holes_diameter_mm=3.4,
                front_projection_mm=-frame_front,stock_holes='Existing stock pattern; do not manufacture the individual perforations')


def replace_motherboard_supports(parts):
    posts=[p for p in parts if p['name'].startswith('Motherboard_M3_ATX_male_female_standoff_')]
    if not posts:return []
    parts[:]=[p for p in parts if p not in posts and not p['name'].startswith('Motherboard_M3x5_')]
    positions=[]
    for p in posts:
        b=bounds(p['shape']);x=(b[0]+b[3])/2;y=(b[1]+b[4])/2;top=b[5];tray=top-6.5
        key=p['name'].rsplit('_',1)[1]
        spacer=cyl(x,y,tray+.5,3.,6.).cut(cyl(x,y,tray,1.6,8.))
        add(parts,'Motherboard_metric_6mm_spacer_'+key,spacer,'motherboard_mounts',catalog='92871A009')
        for name,z in [('height_washer',tray),('top_washer',top+1.57)]:
            washer=cyl(x,y,z,3.5,.5).cut(cyl(x,y,z-.1,1.6,.7))
            add(parts,'Motherboard_M3_'+name+'_'+key,washer,'motherboard_mounts',specification='ISO 7089 M3 washer, 7 mm OD x 0.5 mm')
        add(parts,'Motherboard_M3x12_'+key,screw((x,y,top+2.07),(0,0,-1),'M3',12),'motherboard_mounts',thread_host=p['thread_host'])
        positions.append([x,y])
    return positions


def cylinder_axis_at(shape, centre, radius):
    c=cq.Vector(*centre); matches=[]
    for face in shape.Faces():
        if face.geomType()!='CYLINDER':continue
        surface=BRepAdaptor_Surface(face.wrapped).Cylinder()
        if abs(surface.Radius()-radius)>.025:continue
        loc=cq.Vector(surface.Location().X(),surface.Location().Y(),surface.Location().Z())
        d=cq.Vector(surface.Axis().Direction().X(),surface.Axis().Direction().Y(),surface.Axis().Direction().Z())
        dist=(c-loc).cross(d).Length
        if dist<.03:matches.append((face.distance(cq.Vertex.makeVertex(*centre)),d))
    if not matches:return None
    return min(matches,key=lambda q:q[0])[1]


def replace_collars(parts):
    """Replace recorded panel thread collars with catalog self-clinching nuts.

    A nut is installed only where its complete seating annulus fits the sheet.
    Rejected locations remain recorded as exceptions for a separate joint detail.
    """
    result=[]
    for host in list(sheet_parts(parts)):
        records=host.get('tapped',[])
        for n,r in enumerate(records):
            if not r.get('collar_mm'):continue
            thread=r['thread'];spec=PEM[thread];c=cq.Vector(*r['centre'])
            d=cylinder_axis_at(host['shape'],r['centre'],{'M3':1.25,'M4':1.65}[thread])
            assert d is not None,(host['name'],r)
            i=max(range(3),key=lambda k:abs(d.toTuple()[k]));d=cq.Vector(*[1 if k==i else 0 for k in range(3)])
            # Find which side of the datum contains the collar, using a thin annulus.
            def annulus(direction,rad):
                return cq.Solid.makeCylinder(rad,.3,c+direction*.05,direction).cut(cq.Solid.makeCylinder(1.9 if thread=='M3' else 2.5,.5,c,direction))
            plus=annulus(d,3.).intersect(host['shape']).Volume()
            minus=annulus(d*-1,3.).intersect(host['shape']).Volume()
            inward=d if plus>minus else d*-1
            # Flat, continuous sheet around the full head is required.
            ring=annulus(inward,spec['edge'])
            land=ring.intersect(host['shape']).Volume()/ring.Volume()
            if land<.98:
                result.append(dict(host=host['name'],centre=r['centre'],thread=thread,status='retain formed thread: interrupted seating land',land_fraction=land));continue
            outward=inward*-1
            collar_r={'M3':1.85,'M4':2.45}[thread]
            host['shape']=host['shape'].cut(cq.Solid.makeCylinder(collar_r+.01,r['collar_mm']+.01,c,outward))
            host['shape']=host['shape'].cut(cq.Solid.makeCylinder(spec['hole']/2,8,c-inward*.1,inward)).clean()
            name=f"PEM_{thread}_{host['name']}_{n+1}"
            add(parts,name,clinch_shape(c.toTuple(),inward.toTuple(),thread),moving=host['moving'],catalog=spec['stock'],thread_host=host['name'])
            r['joint']='self-clinching nut';r['hole_diameter_mm']=spec['hole'];r['collar_mm']=0
            host.setdefault('press_fit_holes',[]).append(dict(centre=r['centre'],diameter=spec['hole'],thread=thread,axis=inward.toTuple()))
            result.append(dict(host=host['name'],centre=r['centre'],thread=thread,status='self-clinching nut',catalog=spec['stock'],land_fraction=land))
    return result


def revise(parts, modular=False):
    print('  replacing PCB rails',flush=True)
    support=replace_supports(parts)
    motherboard=replace_motherboard_supports(parts)
    print('  building stock mesh cover',flush=True)
    front=replace_grille(parts,modular)
    print('  converting panel collars',flush=True)
    pem=replace_collars(parts)
    from service_crossbar import apply
    service=apply(parts)
    print('  geometry revision complete',flush=True)
    return dict(backplane_support=support,motherboard_spacer_points=motherboard,front=front,panel_threads=pem,service_crossbar=service)

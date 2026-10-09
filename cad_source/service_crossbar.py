"""Rounded stock-mesh cover and a removable sheet-metal chassis tie.

The tie mounts ahead of the reference GPUs. Its fixed ledges stay outside
their vertical extraction path. Optional fingers touch verified shroud lands;
they are not a shipping restraint or a substitute for bracket retention.
"""
import cadquery as cq
from mounting_hardware import box, cyl, screw, union
from sheetmetal import bounds, fold


def rounded_plate(x, y, z, width, depth, height, radius):
    return cq.Workplane(obj=box(x,y,z,width,depth,height)).edges('|Y').fillet(radius).val()


def round_rack_ears(parts):
    """Round free corners without changing rack holes or the folded interface."""
    for p in parts:
        if p['group'] != 'rack_ears' or p.get('corner_radii_mm'):
            continue
        shape=p['shape']; b=bounds(shape)
        outside=b[0] if b[0]<0 else b[3]
        front=[e for e in shape.Edges() if e.geomType()=='LINE' and abs(e.Length()-3)<1e-5
               and abs(e.Center().x-outside)<1e-5
               and min(abs(e.Center().z-b[2]),abs(e.Center().z-b[5]))<1e-5]
        assert len(front)==2, p['name']
        shape=shape.fillet(5,front)
        rear=[e for e in shape.Edges() if e.geomType()=='LINE' and abs(e.Length()-3)<1e-5
              and abs(e.Center().y-b[4])<1e-5
              and min(abs(e.Center().z-b[2]),abs(e.Center().z-b[5]))<1e-5]
        assert len(rear)==2, p['name']
        p['shape']=shape.fillet(3,rear)
        p['corner_radii_mm']={'front_free_corners':5,'rear_flange_free_corners':3}
        p['notes']='3 mm steel. Front free corners R5; rear flange free corners R3. Deburr both faces and break all exposed edges 0.3-0.5 mm. Rack holes and side screw axes remain at the drawing datums.'
        assert p['shape'].isValid(), p['name']


def bolt_on_handholds(parts):
    """Top-access tab screws stay attached during cartridge removal."""
    from manufacturing_revision import add, clinch_shape
    tray=next(p for p in parts if p['name']=='GPU_tray_two_side_bends')
    bearing=next(p for p in parts if p['name']=='Front_bearing_angle_spot_welded_to_side_angles')
    tb=bounds(tray['shape'])
    for p in list(parts):
        if not p['name'].startswith('Tray_handhold_') or p.get('bolted_handhold'):
            continue
        b=bounds(p['shape']); x0,y0,z0=b[:3]
        # Rebuild the square opening with R3 corners; retain the existing foot and bend.
        fill=box(x0+5,b[4]-1.6,z0+9.5,18,1.6,18)
        opening=rounded_plate(x0+5,b[4]-2,z0+9.5,18,4,18,3)
        p['shape']=p['shape'].fuse(fill).cut(opening).clean()
        corners=[e for e in p['shape'].Edges() if e.geomType()=='LINE' and abs(e.Length()-1.5)<1e-5
                 and abs(e.Center().z-b[5])<1e-5
                 and min(abs(e.Center().x-b[0]),abs(e.Center().x-b[3]))<1e-5]
        assert len(corners)==2,p['name']
        p['shape']=p['shape'].fillet(3,corners)
        for x in (x0+7,x0+21):
            y=y0+6
            p['shape']=p['shape'].cut(cyl(x,y,z0-.1,1.7,2))
            tray['shape']=tray['shape'].cut(cyl(x,y,tb[2]-.1,4.22/2,2))
            # Bearing clearance admits the captive nut and protruding screw tip.
            bearing['shape']=bearing['shape'].cut(cyl(x,y,tb[2]-8,4,10))
            nut_name=f'Handhold_tray_PEM_M3_{x:g}'
            add(parts,nut_name,clinch_shape((x,y,tb[2]),(0,0,1),'M3'),'hardware',moving=True,catalog='95185A530',thread_host=tray['name'])
            add(parts,f'Handhold_M3x6_{x:g}',screw((x,y,z0+1.5),(0,0,-1),'M3',6),'hardware',moving=True,thread_host=nut_name)
        p['bolted_handhold']=True
        p['drawing_family']='Tray_handhold_45'
        p['notes']='1.5 mm steel. Opening 18 x 18, R3; top outer corners R3. Two diameter 3.4 foot holes, 14 apart, 6 from front edge; M3 x 6 into tray press nuts. Deburr grip edges. Not load-qualified.'
        assert p['shape'].isValid(),p['name']
    bearing['notes']='Four diameter 8 clearance holes beneath handhold nuts; these are not fastening holes. Cartridge lifts vertically with nuts and tab screws attached.'


def shorten_lid_guide_screws(parts):
    """Limit inward screw projection while retaining the sliding-lid head datum."""
    from rear_closure import lid_slots
    wall=next(p for p in parts if p['name'].startswith(('U_shaped_body_','Upper_module_U_body_')))
    lid=next(p for p in parts if p['group']=='lid')
    height=bounds(lid['shape'])[5]
    rear_moved=False
    for p in parts:
        if not p['name'].startswith('Lid_pin_') or 'M3x6' not in p['name']:
            continue
        b=bounds(p['shape']);left=b[0]<0
        y=(b[1]+b[4])/2;z=(b[2]+b[5])/2
        if y>400:
            if not rear_moved:
                for x in (0,438.5):wall['shape']=wall['shape'].fuse(cyl(x,y,z,1.26,1.5,(1,0,0))).clean()
                wall['shape']=wall['shape'].cut(cyl(-1,455,z,1.25,442,(1,0,0))).clean()
                old_tools=union(lid_slots(440,height,[(y,z)]))
                for x in (1.5,437):
                    strip=box(x,22,height-18,1.5,437.2,16.5)
                    lid['shape']=lid['shape'].fuse(old_tools.intersect(strip)).clean()
                lid['shape']=lid['shape'].cut(union(lid_slots(440,height,[(455,z)]))).clean()
                rear_moved=True
            y=455
        p['shape']=screw((0 if left else 440,y,z),(1,0,0) if left else (-1,0,0),'M3',3)
        assert p['name'].count('M3x6')==1
        p['name']=f'Lid_pin_{"left" if left else "right"}_M3x3_{y:g}'
        p['notes']='M3 x 3 lid guide screw. Rear guides at Y455 clear the rising PCB edge. Shank projects 1.5 mm beyond the wall; do not use longer screws.'


def apply(parts):
    from manufacturing_revision import add, clinch_shape
    frame = next(p for p in parts if p['name']=='Front_full_face_mesh_clamping_frame')
    mesh = next(p for p in parts if p['name'].startswith('Stock_hex_'))
    fb, mb = bounds(frame['shape']), bounds(mesh['shape'])
    frame['shape'] = rounded_plate(*fb[:3],440,1.5,fb[5]-fb[2],12).cut(
        rounded_plate(20,fb[1]-1,fb[2]+20,400,4,fb[5]-fb[2]-40,8))
    for x,z in mesh['mounting_holes_xz']:
        frame['shape'] = frame['shape'].cut(cyl(x,fb[1]-1,z,1.7,5,(0,1,0)))
    blank=rounded_plate(*mb[:3],432,mb[4]-mb[1],mb[5]-mb[2],8)
    source_face=cq.Workplane(obj=mesh['shape']).faces('<Y').val()
    outer=cq.Workplane(obj=blank).faces('<Y').val().outerWire()
    mesh['shape']=cq.Solid.extrudeLinear(outer,source_face.innerWires(),cq.Vector(0,mb[4]-mb[1],0))
    mesh['corner_radius_mm'] = 8
    frame['notes'] = '1.5 steel; outer corners R12, opening corners R8. Keep the stock mesh edges concealed; remove the cover for fan access.'
    mesh['notes'] = 'Cut stock 92725T3: outer corners R8; deburr. Perforation phase is uncontrolled; assembly holes diameter 3.4.'
    assert not any(p['group']=='crossbar' for p in parts)
    gpus = sorted((p for p in parts if p['group']=='gpus'),key=lambda p:int(p['name'].split('_')[1]))
    gpu_top = bounds(gpus[0]['shape'])[5]
    shift = gpu_top-309.11
    top = 345.5+shift
    wall = next(p for p in parts if p['name'].startswith(('U_shaped_body_', 'Upper_module_U_body_')))
    # The open channel spans between side walls; 1.5 mm inside bend radii.
    beam = union([box(4.5,165,top-1.5,431,30,1.5),
                  box(4.5,165,top-20,431,1.5,20),
                  box(4.5,193.5,top-20,431,1.5,20)])
    bends=[]
    beam=fold(beam,bends,'x',(165,top),(1,-1),1.5)
    beam=fold(beam,bends,'x',(195,top),(-1,-1),1.5)
    # Four top screws remove the tie. Two screws per end prevent rotation.
    for side in ('left','right'):
        left=side=='left'; x0=1.5 if left else 415
        bracket=union([box(1.5,168.5,312+shift,1.5,23,32),box(1.5,168.5,342.5+shift,23.5,23,1.5)])
        bracket=fold(bracket,[],'y',(1.5,344+shift),(1,-1),1.5)
        if not left:bracket=bracket.mirror('YZ',(220,0,0))
        name='Crossbar_side_ledge_'+side
        xx=14 if left else 426
        for yy in (175.5,184.5):
            beam=beam.cut(cyl(xx,yy,top-2,2.25,4))
            bracket=bracket.cut(cyl(xx,yy,341+shift,5.41/2,5))
            nut_name=f'Crossbar_ledge_PEM_M4_{side}_{yy}'
            add(parts,nut_name,clinch_shape((xx,yy,342.5+shift),(0,0,1),'M4'),'crossbar_mounts',catalog='95185A590',thread_host=name)
            add(parts,f'Crossbar_release_M4x8_{side}_{yy}',screw((xx,yy,top),(0,0,-1),'M4',8),'crossbar',thread_host=nut_name)
        for zz in (322+shift,334+shift):
            axis=(1,0,0) if left else (-1,0,0)
            outside=0 if left else 440
            bracket=bracket.cut(cyl(outside-1 if left else outside+1,180,zz,5.41/2,8,axis))
            wall['shape']=wall['shape'].cut(cyl(outside-1 if left else outside+1,180,zz,2.25,4,axis))
            nx=3 if left else 437
            nut_name=f'Crossbar_wall_PEM_M4_{side}_{zz:.2f}'
            add(parts,nut_name,clinch_shape((nx,180,zz),tuple(-a for a in axis),'M4'),'crossbar_mounts',catalog='95185A590',thread_host=name)
            add(parts,f'Crossbar_wall_M4x8_{side}_{zz:.2f}',screw((outside,180,zz),axis,'M4',8),'crossbar_mounts',thread_host=nut_name)
        add(parts,name,bracket,'crossbar_mounts','fabricated',color='#aebbc6',thickness_mm=1.5,drawing_family='Crossbar_side_ledge_left',
            notes='Two identical 1.5 steel ledges; rotate 180 degrees for the opposite wall. R1.5 bend. Install before rack insertion with two side M4 x 8 screws per ledge. Fixed ledges stay ahead of the GPU extraction path.')
    finger_centres=[]
    for i,gpu in enumerate(gpus,1):
        b=bounds(gpu['shape']); x=(b[0]+b[3])/2
        finger_centres.append(x)
        # Two parallel vertical slots prevent a finger from pivoting about one screw.
        bottom=gpu_top+1.5875
        finger=union([box(x-11,195,bottom,22,1.5,top-1.5-bottom),box(x-11,195,bottom,22,25,1.5)])
        finger=fold(finger,[],'x',(195,bottom),(1,1),1.5)
        for sx in (x-6,x+6):
            beam=beam.cut(cyl(sx,192,334+shift,4.22/2,5,(0,1,0)))
            tool=union([cyl(sx,194,330+shift,1.7,4,(0,1,0)),cyl(sx,194,338+shift,1.7,4,(0,1,0)),box(sx-1.7,194,330+shift,3.4,4,8)])
            finger=finger.cut(tool)
            nut_name=f'Stabilizer_PEM_M3_{i}_{sx:.3f}'
            add(parts,nut_name,clinch_shape((sx,193.5,334+shift),(0,1,0),'M3'),'gpu_stabilizers',catalog='95185A530',thread_host='Removable_chassis_crossbar',optional=True)
            add(parts,f'Stabilizer_M3x6_{i}_{sx:.3f}',screw((sx,196.5,334+shift),(0,-1,0),'M3',6),'gpu_stabilizers',thread_host=nut_name,optional=True)
        add(parts,f'GPU_stabilizer_finger_{i}',finger,'gpu_stabilizers','fabricated',color='#b39a6b',optional=True,drawing_family='GPU_stabilizer_finger_1',thickness_mm=1.5,
            notes='OPTIONAL: ten identical 1.5 steel fingers. R1.5 bend; two 3.4 x 11.4 slots, axes 12 apart. Adjustment +/-4 vertical. Set foam to light contact on a verified rigid shroud land; do not load vents or PCB.')
        add(parts,f'Stabilizer_silicone_pad_{i}',box(x-10,204,gpu_top,20,12,1.5875),'gpu_stabilizers',color='#4a555c',optional=True,
            specification='Silicone foam pad 20 x 12 x 1.5875; cut from 86235K311',catalog='86235K311')
    add(parts,'Removable_chassis_crossbar',beam,'crossbar','fabricated',color='#879baa',thickness_mm=1.5,
        notes='431 x 30 x 20 inverted U; 1.5 steel, two R1.5 bends. Four diameter 4.5 top holes; remove four M4 x 8 screws and lift. Twenty diameter 4.22 rear holes accept optional M3 press nuts. No captive nut access is needed for service.')
    return dict(cover_outer_radius_mm=12,cover_opening_radius_mm=8,stock_mesh_radius_mm=8,
                top_z_mm=top,channel_mm=[431,30,20,1.5],span_x_mm=[4.5,435.5],span_y_mm=[165,195],
                top_fixing_points=[[x,y,top] for x in (14,426) for y in (175.5,184.5)],
                release_screws='Four top-access M4 x 8',fixed_bracket_y_mm=[168.5,191.5],
                gpu_nose_y_mm=bounds(gpus[0]['shape'])[1],gpu_top_z_mm=gpu_top,
                optional_finger_centres_x_mm=finger_centres,finger_adjustment_mm=4,
                foam_stock='86235K311',foam_pad_mm=[20,12,1.5875],
                contact='Nominal zero compression on envelope only; verify shroud contact land and set by hand. Not a shipping restraint.',
                removal='Lid off; disconnect harnesses if removing cards; remove four top crossbar screws; lift bar and attached fingers at least 40 mm; move forward and lift clear; release GPU or cartridge retention screws. The manufacturing export provides a fixed rear frame clear of the lift path.')

"""Fixed rear mesh frame with all fastening hardware outside the cartridge path."""
import math
import cadquery as cq
from mounting_hardware import box,cyl,screw,union,orient
from sheetmetal import bounds,fold
from service_crossbar import rounded_plate

REAR_OFFSET = 1.0

def flat_screw(point,length=6):
    # Catalog 92010A116: 90-degree head, diameter 5.6, height 1.65.
    head=union([cyl(0,0,0,2.8,.35),cq.Solid.makeCone(2.8,1.5,1.3,cq.Vector(0,0,.35))])
    return orient(head.fuse(cyl(0,0,1.65,1.5,length-1.65)),point,(0,1,0))


def apply(parts):
    from manufacturing_revision import add,clinch_shape
    old=next(p for p in parts if p['group']=='rear_vent')
    if old.get('fixed_mesh_frame'):return
    ob=bounds(old['shape']);bottom,top=ob[2],ob[5];height=top-bottom
    modular=any(p['name'].startswith('Upper_module_U_body') for p in parts)
    wall=next(p for p in parts if p['name'].startswith(('U_shaped_body_','Upper_module_U_body_')))
    old_side=[p for p in parts if p['name'].startswith(('left_rear_cover_M3','right_rear_cover_M3'))]
    # Replace former clearance holes with the specified tapped-wall geometry.
    for p in old_side:
        b=bounds(p['shape']);left=b[0]<0;x=0 if left else 438.5
        wall['shape']=wall['shape'].fuse(cyl(x,(b[1]+b[4])/2,(b[2]+b[5])/2,1.71,1.5,(1,0,0))).clean()
    old_name=old['name']
    parts[:]=[p for p in parts if p is not old and p not in old_side and p.get('thread_host')!=old_name
              and not p['name'].startswith(('Rear_MCIO_','Lid_rear_retention_'))]
    retained={id(p) for p in parts}
    frame_name='Fixed_rear_mesh_frame'
    frame=rounded_plate(1.5,483.5,bottom,437,2,height,3)
    windows=([(22,120),(320,418)] if modular else [(22,418)])
    for xa,xb in windows:
        frame=frame.cut(rounded_plate(xa,483,bottom+12,xb-xa,3,height-24,3))
    for a,b in ((12,36),(404,428)):
        frame=frame.fuse(box(a,483.5,top-15,b-a,2,15)).clean()
    notch=top+1.5-35
    if modular:frame=frame.cut(box(150,483,notch,140,4,50))
    fix_z=(bottom+12,top-12)
    for side in ('left','right'):
        left=side=='left'; x=8 if left else 432
        bracket=union([box(-1.5,469,bottom,1.5,18,height),box(-1.5,485.5,bottom,14.5,1.5,height)])
        bracket=fold(bracket,[],'z',(-1.5,487),(1,-1),1.5)
        if not left:bracket=bracket.mirror('YZ',(220,0,0))
        name='Rear_frame_external_angle_'+side
        for z in fix_z:
            # Flush inner heads prevent the rising PCIe rear panel catching a screw.
            frame=frame.cut(cyl(x,483,z,1.7,4,(0,1,0)))
            frame=frame.cut(cq.Solid.makeCone(3.15,1.7,1.45,cq.Vector(x,483.5,z),cq.Vector(0,1,0)))
            bracket=bracket.cut(cyl(x,485,z,4.22/2,4,(0,1,0)))
            nut_name=f'Rear_frame_external_PEM_M3_{side}_{z:g}'
            add(parts,nut_name,clinch_shape((x,487,z),(0,-1,0),'M3'),'hardware',catalog='95185A530',thread_host=name)
            add(parts,f'Rear_frame_flush_screw_{side}_{z:g}',flat_screw((x,483.5,z)),'hardware',catalog='92010A116',
                specification='M3 x 6 flat-head Phillips screw, 90 deg',thread_host=nut_name)
            ax=(1,0,0) if left else (-1,0,0);outside=-1.5 if left else 441.5
            bracket=bracket.cut(cyl(outside-.1*ax[0],477.2,z,1.7,2,ax))
            wall['shape']=wall['shape'].cut(cyl(-1,477.2+REAR_OFFSET,z,1.25,442,(1,0,0)))
            add(parts,f'Rear_angle_wall_M3x3_{side}_{z:g}',screw((outside,477.2,z),ax,'M3',3),'hardware',thread_host=wall['name'])
        add(parts,name,bracket,'rear_frame_mounts','fabricated',thickness_mm=1.5,drawing_family='Rear_frame_external_angle_left',
            notes='Two identical 1.5 steel angles; rotate 180 degrees about Y for opposite side. R1.5 bend. Two M3 x 3 screws into tapped body wall; tips flush with inner wall. Rear leg has two diameter 4.22 holes for outward M3 press nuts.')
    # Extend only the rear lid tabs and bend; retain the side-guide locations.
    lid=next(p for p in parts if p['group']=='lid');lb=bounds(lid['shape'])
    tail=lid['shape'].intersect(box(-5,483,lb[2]-1,450,20,lb[5]-lb[2]+2))
    lid['shape']=lid['shape'].cut(box(-5,483,lb[2]-1,450,20,lb[5]-lb[2]+2)).fuse(
        tail.translate((0,.5+REAR_OFFSET,0)),box(0,483,lb[5]-1.5,440,.5+REAR_OFFSET,1.5)).clean()
    lid_z=lb[5]-10
    for x in (24,416):
        frame=frame.cut(cyl(x,483,lid_z,1.25,4,(0,1,0)))
        add(parts,f'Lid_rear_retention_M3x3_{x:g}',screw((x,487,lid_z),(0,-1,0),'M3',3),'lid_screws',thread_host=frame_name)
    lid['notes']='Rear tab outer face Y488, 3 mm aft of body rear Y485. Rear guide slots end at Y455. Two M3 x 3 rear retention screws; do not use longer screws.'
    if modular:
        cap_bottom=top-11.55;cap_screw_z=top-6.55
        entry_fix=[(x,z) for x in (143,297) for z in (notch-6,cap_screw_z)]
        base=box(138,485.5,bottom,164,1.5,top+1.5-bottom).cut(box(150,485,notch,140,4,50))
        for x,z in entry_fix:
            frame=frame.cut(cyl(x,483,z,1.25,4,(0,1,0)))
            base=base.cut(cyl(x,485,z,1.7,4,(0,1,0)))
            cap_screw=z==cap_screw_z
            add(parts,f'Rear_MCIO_{"cap" if cap_screw else "base"}_M3x{5 if cap_screw else 3}_{x}',
                screw((x,488.5 if cap_screw else 487,z),(0,-1,0),'M3',5 if cap_screw else 3),'entry_fasteners',thread_host=frame_name)
        cap=union([box(138,487,cap_bottom,10,1.5,top+1.5-cap_bottom),box(292,487,cap_bottom,10,1.5,top+1.5-cap_bottom),
                   box(138,487,top-1.55,164,1.5,3.05),box(138,488.5,top,164,6,1.5)])
        cap=fold(cap,[],'x',(487,top+1.5),(1,-1),1.5)
        for x in (143,297):cap=cap.cut(cyl(x,486,cap_screw_z,1.7,4,(0,1,0)))
        add(parts,'Rear_MCIO_lower_U_frame_140x35_entry',base,'external_entry','fabricated',thickness_mm=1.5,
            notes='140 wide x 35 high clear opening with cap removed. Two lower M3 x 3 and two cap M3 x 5 screws into the tapped rear frame. No nut or screw tip projects forward of Y484.5.')
        add(parts,'Rear_MCIO_removable_folded_brush_cap',cap,'external_entry','fabricated',thickness_mm=1.5,
            notes='Remove two M3 x 5 screws for connector passage. Folded cap ties the 140 mm opening across its top; silicone/brush sealing is not a structural member.')
        add(parts,'Rear_MCIO_lower_brush_strip',box(150,485.7,notch,140,1,17.5),'brush','reference',color='#303a41')
        add(parts,'Rear_MCIO_upper_brush_strip',box(150,487.2,notch+17.5,140,1,14.45),'brush','reference',color='#303a41')
    mesh_ranges=([(14,128),(312,426)] if modular else [(14,426)])
    for i,(xa,xb) in enumerate(mesh_ranges):
        lower_x=(xa+4,xb-4) if modular else (18,220,422)
        upper_x=(max(xa+4,42),min(xb-4,398)) if modular else (42,220,398)
        fixes=[(x,bottom+8) for x in lower_x]+[(x,top-8) for x in upper_x]
        blank=rounded_plate(xa,485.5,bottom+4,xb-xa,.9144,height-8,3)
        notches=[(12,36),(404,428)]
        for a,b in notches:
            blank=blank.cut(box(a,485,top-15,b-a,3,20))
        outer=cq.Workplane(obj=blank).faces('<Y').val().outerWire();holes=[];pitch=7.1374;dy=pitch*math.sqrt(3)/2
        for row in range(int(height/dy)+1):
            z=bottom+row*dy
            for col in range(int((xb-xa)/pitch)+1):
                x=xa+col*pitch+(row%2)*pitch/2
                if not (xa+12<x<xb-12 and bottom+16<z<top-16):continue
                if z>top-19 and any(a-4<x<b+4 for a,b in notches):continue
                vertices=[(x+6.35/math.sqrt(3)*math.cos(math.radians(30+60*k)),z+6.35/math.sqrt(3)*math.sin(math.radians(30+60*k))) for k in range(6)]
                holes.append(cq.Workplane('XZ').polyline(vertices).close().val().translate((0,485.5,0)))
        holes += [cq.Wire.makeCircle(1.7,cq.Vector(x,485.5,z),cq.Vector(0,1,0)) for x,z in fixes]
        mesh=cq.Solid.extrudeLinear(outer,holes,cq.Vector(0,.9144,0))
        name=f'Stock_hex_rear_mesh_{i+1}'
        add(parts,name,mesh,'rear_mesh','fabricated',catalog='92725T3',thickness_mm=.9144,corner_radius_mm=3,
            drawing_family='Stock_hex_rear_mesh_1',blank_size_mm=[xb-xa,height-8],mounting_holes_xz=fixes,
            blank_notches_xz=[[a,top-15,b-a,20] for a,b in notches if a<xb and b>xa],
            notes='Stock 92725T3 cut blank with R3 corners; deburr. Perforation phase is illustrative. Clamp to the frame with M3 x 3 screws and 9 mm OD washers; mesh carries no structural load.')
        for x,z in fixes:
            frame=frame.cut(cyl(x,483,z,1.25,4,(0,1,0)))
            washer=cyl(x,486.4144,z,4.5,.8,(0,1,0)).cut(cyl(x,486,z,1.6,2,(0,1,0)))
            add(parts,f'Rear_mesh_M3_large_washer_{x:g}_{z:g}',washer,'hardware')
            add(parts,f'Rear_mesh_M3x3_{x:g}_{z:g}',screw((x,487.2144,z),(0,-1,0),'M3',3),'hardware',thread_host=frame_name)
    add(parts,frame_name,frame,'rear_vent','fabricated',thickness_mm=2,fixed_mesh_frame=True,
        notes='2 mm steel frame; inside face Y484.5 stays flush. Four diameter 3.4 holes: inner countersink 90 degrees, diameter 6.3, M3 flat heads. Diameter 2.5 holes: tap M3 x 0.5. Use specified screw lengths; no inward nuts or tips.')
    for p in parts:
        if id(p) not in retained:p['shape']=p['shape'].translate((0,REAR_OFFSET,0))
    return dict(rear_frame_inner_y_mm=483.5+REAR_OFFSET,frame_thickness_mm=2,mesh_stock='92725T3',
                mesh_blanks_mm=[[b-a,height-8] for a,b in mesh_ranges],module_entry_mm=[140,35] if modular else None,
                fixed_during_cartridge_removal=True,wall_screw_length_mm=3,lid_retention_length_mm=3)

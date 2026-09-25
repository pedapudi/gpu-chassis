"""RM53-502 replacement-lid GPU module; supplier mating geometry remains a fit template."""
from pathlib import Path
import json
import cadquery as cq
from mounting_hardware import box,cyl,union,cut,screw,fan_screw,nut,slot
from build_chassis import overlap
import gpu_geometry
from sheetmetal import fold,move_part
from threads import tap_captive_nuts,captive_screw
from front_hardware import add_ears,ear_holes,grille_holes

# Each intake option has its own removable front carrier; one grille gives tool access to all three.
# Padded fans sit on 1 mm front pads (frame at Y3); unpadded frames seat on the carrier (Y2).
INTAKES={
 '3x140':[dict(size=140,depth=25,pitch=124.5,opening=136,xs=(78.,220.,362.),z=330.,pad=141,model='Noctua_NF_A14')],
 '3x120_80':[dict(size=120,depth=25,pitch=105.,opening=116,xs=(78.,220.,362.),z=299.,pad=120,model='Noctua_NF_A12x25'),
             dict(size=80,depth=25,pitch=71.5,opening=76,xs=(52.,136.,220.,304.,388.),z=401.,pad=None,model='Noctua_NF_A8')],
 '2x180':[dict(size=180,depth=32,pitch=165.,opening=175,xs=(128.,312.),z=330.,pad=None,model='SilverStone_AP183')]}
GRILLE_FIX=[(20.,231.),(220.,231.),(420.,231.),(7.5,425.),(432.5,425.)]

def fan_axes(row):
 m=row['pitch']/2
 return [(x+dx,row['z']+dz) for x in row['xs'] for dx in (-m,m) for dz in (-m,m)]

def build_modular(full_parts,out,return_parts=False,intake='3x140'):
 rows=INTAKES[intake]
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 (out/'formed_parts').mkdir(exist_ok=True);(out/'cut_profiles').mkdir(exist_ok=True)
 W,D=440.,485.;bottom=222.25;H=444.;lift=72.25;parts=[]
 # A 5U module: 221.75 tall. Rear entry features sit at the top of the rear cover.
 rise=H-399.55
 def add(name,shape,group,color='#aebbc6',role='fabricated',visible=True,moving=False,pieces=None):
  assert shape.isValid(),name
  p=dict(name=name,shape=shape,group=group,color=color,role=role,visible=visible,moving=moving)
  if pieces:p['pieces']=pieces
  parts.append(p);return shape
 def form(name,shape,t,folds,tools=()):
  """Form the listed sharp corners of one sheet piece, then cut its features."""
  bends=[]
  for f in folds:shape=fold(shape,bends,*f[:3],t,**(f[3] if len(f)>3 else {}))
  shape=cut(shape,list(tools))
  return shape,dict(name=name,shape=shape,t=t,bends=bends)
 def profile(name,s,axis,value):
  fs=[f for f in s.clean().Faces() if abs(getattr(f.Center(),axis)-value)<1e-5];f=max(fs,key=lambda x:x.Area())
  if axis=='y':f=f.rotate((0,0,0),(1,0,0),90)
  if axis=='x':f=f.rotate((0,0,0),(0,1,0),90)
  cq.exporters.export(cq.Workplane().newObject(f.Wires()),str(out/'cut_profiles'/f'{name}.dxf'))
 def hole_side(y,z,r=1.7):return cyl(-2,y,z,r,W+4,(1,0,0))
 keep={'guides','hold_downs','rear_release'}
 for p in full_parts:
  if p['name'].startswith(('Baffle_side_welded_tab_','Baffle_captive_nut_')):continue
  selected=p['moving'] or p['group'] in keep or (p['group']=='strain_relief' and p['shape'].BoundingBox().zmin>160)
  selected |= p['name'].startswith(('Side_ledge_','power_restraint_','signal_restraint_','Backplane_MCIO_mated_plug_'))
  if not selected:continue
  q=move_part(p,lambda s:s.translate((0,0,lift)))
  if q['group']=='fans':q['shape']=q['shape'].translate((0,-1.5,0))
  # Bearing-angle lower tips stop above the module floor's inside bend radius.
  if q['group']=='guides':q=move_part(q,lambda s:s.cut(box(-5,-5,0,450,495,bottom+3)))
  assert q['shape'].Volume()>0,q['name'];parts.append(q)
 # Wide connector passages line up through the module floor and forward baffle.
 passage=[cq.Workplane().add(box(x,108.2,bottom-1,195,65,5)).edges('|Z').fillet(6).val() for x in (15,230)]
 mounting=[(x,y) for x in (10,430) for y in (80,242.5,410)]
 holes=[cyl(x,y,bottom-1,1.7,5) for x,y in mounting]
 floor=cut(box(0,2,bottom,W,D-2,1.5),passage+holes)
 body=union([floor,box(0,2,bottom+1.5,1.5,D-2,H-bottom-3),box(W-1.5,2,bottom+1.5,1.5,D-2,H-bottom-3)])
 bh=[]
 for y,z in [(233.2,230.25),(343.2,230.25),(443.2,230.25),(143.2,252.25),(143.2,272.25),(477.2,277.25),(477.2,362.25)]:bh.append(hole_side(y,z))
 for z in (242,320,388,430):bh.append(hole_side(12,z))
 bh += [hole_side(477.2,233.75),hole_side(477.2,390,3.2),hole_side(118.2,H-10,3.2),hole_side(433.2,H-10,3.2)]
 for y in (100,240,380):bh.append(hole_side(y,231,2.25))
 bh += ear_holes(0,(252,354))
 body,piece=form('Upper_module_U_body_with_cable_passages',body,1.5,[('y',(0,bottom),(1,1)),('y',(W,bottom),(-1,1))],bh)
 body=add('Upper_module_U_body_with_cable_passages',body,'shell',pieces=[piece]);profile('upper_module_floor_no_returns',body,'z',bottom)
 front=union([box(0,0,bottom,440,2,H-bottom),box(1.5,2,bottom+2,1.5,18,H-bottom-4),box(437,2,bottom+2,1.5,18,H-bottom-4)])
 tools=[]
 def obround(x,z,length):
  half=(length-5.5)/2
  return union([box(x-half,-1,z-2.75,2*half,5,5.5),cyl(x-half,-1,z,2.75,5,(0,1,0)),cyl(x+half,-1,z,2.75,5,(0,1,0))])
 for row in rows:
  tools += [cyl(x,-1,row['z'],row['opening']/2,5,(0,1,0)) for x in row['xs']]
  # Screw axes closer than 25 mm share one horizontal obround; others get a 9 mm slot.
  for z in sorted({z for _,z in fan_axes(row)}):
   xs=sorted(x for x,zz in fan_axes(row) if zz==z);i=0
   while i<len(xs):
    if i+1<len(xs) and xs[i+1]-xs[i]<25:tools.append(obround((xs[i]+xs[i+1])/2,z,xs[i+1]-xs[i]+9));i+=2
    else:tools.append(obround(xs[i],z,9));i+=1
 add_ears(add,0,bottom,H-bottom,(252,354),5)
 grille_fix=GRILLE_FIX
 tools += [cyl(x,-1,z,1.7,5,(0,1,0)) for x,z in grille_fix]
 tools += [hole_side(12,z) for z in (242,320,388,430)]
 # Joined assembly: 2 mm front face and two 1.5 mm return strips.
 front_pieces=[form(f'Upper_module_front_carrier_{intake}_2mm_face',box(0,0,bottom,440,2,H-bottom),2,[],tools)[1]]
 front_pieces+=[form(f'Upper_module_front_carrier_{intake}_{side}_return_strip',box(x,2,bottom+3,1.5,18,H-bottom-5),1.5,[],tools)[1] for side,x in (('left',1.5),('right',437))]
 front=add('Upper_module_front_carrier_'+intake,union([p['shape'] for p in front_pieces]),'shell','#304553',pieces=front_pieces);profile('upper_module_front_no_returns',front,'y',0)
 all_fan_axes=sorted({a for option in INTAKES.values() for row in option for a in fan_axes(row)})
 for row in rows:
  size,depth,half,mount=row['size'],row['depth'],row['size']/2,row['pitch']/2;fan_y=3 if row['pad'] else 2;z=row['z']
  for x in row['xs']:
   bores=[cyl(x+dx,1,z+dz,2.2,depth+6,(0,1,0)) for dx in (-mount,mount) for dz in (-mount,mount)]
   frame=box(x-half,fan_y,z-half,size,depth,size).cut(cyl(x,fan_y-1,z,half-5,depth+2,(0,1,0))).cut(cq.Compound.makeCompound(bores))
   rotor=union([cyl(x,fan_y+4,z,size*.14,depth-10,(0,1,0)),box(x-2,fan_y+depth-3,z-half+5,4,2,size-10)])
   add(f"{row['model']}_{size}x{depth}_frame_reference_{x:g}_{z:g}",union([frame,rotor]),'fans','#304553','reference')
   if not row['pad']:continue
   # Padded envelope is published; individual pad outlines are nominal references.
   pads=[];pw=row['pad']
   for dx in (-1,1):
    for dz in (-1,1):
     xx=x-pw/2 if dx<0 else x+pw/2-12;zz=z-pw/2 if dz<0 else z+pw/2-12
     for yy in (fan_y-1,fan_y+depth):pads.append(box(xx,yy,zz,12,1,12).cut(cyl(x+dx*mount,yy-.1,z+dz*mount,2.75,1.2,(0,1,0))))
   add(f'Fan_{size}mm_corner_pads_{pw}x{pw}x27_envelope_{x:g}',cq.Compound.makeCompound(pads),'fan_pads','#655148','reference')
  for x,zz in fan_axes(row):
   add(f'Upper_fan_self_tapping_5x8_screw_{x:g}_{zz:g}',fan_screw((x,0,zz),(0,1,0)),'intake_fasteners','#304553')
 grille=box(0,-1,bottom,440,1,H-bottom)
 gh=grille_holes(-1,bottom,H-bottom,all_fan_axes,grille_fix)
 gh += [cyl(x,-2,z,4.4,4,(0,1,0)) for x,z in all_fan_axes]+[cyl(x,-2,z,1.7,4,(0,1,0)) for x,z in grille_fix]
 grille=add('Upper_module_full_face_1mm_perforated_grille',grille.cut(cq.Compound.makeCompound(gh)),'intake_grilles','#304553')
 profile('upper_module_full_face_grille',grille,'y',-1)
 for x,z in grille_fix:
  add(f'Grille_M3x8_{x:g}_{z:g}',screw((x,-1,z),(0,1,0),'M3',8),'intake_fasteners','#304553')
  add(f'Grille_captive_M3_nut_{x:g}_{z:g}',nut((x,2,z),(0,1,0),'M3'),'intake_fasteners','#b39451')
 for z in (242,320,388,430):
  for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
   add(f'Front_side_M3x8_{x}_{z}',screw((x,12,z),ax,'M3',8),'fasteners','#304553')
   add(f'Front_side_nut_{x}_{z}',nut((nx,12,z),ax,'M3'),'fasteners','#b39451')
 # The rear sill closes the space between the module floor and removable cartridge.
 sill=union([box(1.5,469,223.75,437,1.2,20),box(1.5,470.2,223.75,1.5,13.3,20),box(437,470.2,223.75,1.5,13.3,20)])
 # Joined assembly: 1.2 mm web and two 1.5 mm return strips.
 sill_pieces=[form('Upper_module_rear_sill_1p2mm_web',box(1.5,469,223.75,437,1.2,20),1.2,[],[hole_side(477.2,233.75),box(0,468,222,3,4,3.25),box(437,468,222,3,4,3.25)])[1]]
 sill_pieces+=[form(f'Upper_module_rear_sill_{side}_return_strip',box(x,470.2,225.25,1.5,13.3,18.5),1.5,[],[hole_side(477.2,233.75)])[1] for side,x in (('left',1.5),('right',437))]
 sill=add('Upper_module_rear_sill_with_side_returns',union([p['shape'] for p in sill_pieces]),'shell',pieces=sill_pieces)
 profile('upper_module_rear_sill_no_returns',sill,'y',469)
 for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
  add(f'Rear_sill_M3x8_{x}',screw((x,477.2,233.75),ax,'M3',8),'fasteners')
  add(f'Rear_sill_nut_{x}',nut((nx,477.2,233.75),ax,'M3'),'fasteners')
 # The cassette occupies the lower rear; a separate panel closes the area above its brackets.
 vb=375.32
 vent=union([box(1.5,D-1.5,vb,437,1.5,H-1.5-vb),box(1.5,470.2,vb,1.5,13.3,H-1.5-vb),box(437,470.2,vb,1.5,13.3,H-1.5-vb),box(15,481,vb,410,2.5,1.5)])
 vh=[hole_side(477.2,390)]
 # The top-open notch accepts plugs after the folded brush cap is removed.
 notch=380.5+rise
 vh.append(box(150,482,notch,140,5,25))
 # Cap screws sit below the cap's return bend so their heads clear the inside bend radius.
 entry_fix=[(x,z) for x in (143,297) for z in (notch,390+rise)]
 vh += [cyl(x,482,z,1.7,5,(0,1,0)) for x,z in entry_fix]
 # Perforation rows stay two thicknesses clear of the lower lip bend.
 for row,z in enumerate(range(386,int(H-10),10)):
  for x in range(14+5*(row%2),427,10):
   if 132<x<308:continue
   vh.append(cyl(x,482,z,4,5,(0,1,0)))
 vent,piece=form('Upper_module_rear_perforated_cover',vent,1.5,[('z',(1.5,D),(1,-1)),('z',(438.5,D),(-1,-1)),('x',(D,vb),(-1,1),dict(span=(15,425),relief=True))],vh)
 vent=add('Upper_module_rear_perforated_cover',vent,'rear_vent','#304553',pieces=[piece]);profile('upper_module_rear_vent_no_returns',vent,'y',485)
 # Two lower screws retain the U-frame; two upper screws release the folded cap.
 base=box(138,485,vb,164,1.5,H-1.5-vb).cut(box(150,484,notch,140,4,25))
 base=base.cut(cq.Compound.makeCompound([cyl(x,484,z,1.7,5,(0,1,0)) for x,z in entry_fix]))
 add('Rear_MCIO_lower_U_frame_140mm_top_open_entry',base,'external_entry','#304553')
 cap=union([box(138,486.5,385+rise,10,1.5,H-1.5-385-rise),box(292,486.5,385+rise,10,1.5,H-1.5-385-rise),box(138,486.5,395+rise,164,1.5,3.05),box(138,488,396.55+rise,164,6,1.5)])
 cap,piece=form('Rear_MCIO_removable_folded_brush_cap',cap,1.5,[('x',(486.5,H-1.5),(1,-1))],[cyl(x,486,390+rise,1.7,4,(0,1,0)) for x in (143,297)])
 add('Rear_MCIO_removable_folded_brush_cap',cap,'external_entry','#304553',pieces=[piece])
 add('Rear_MCIO_lower_brush_strip',box(150,485.2,notch,140,1,6.5),'brush','#303a41','reference')
 add('Rear_MCIO_upper_brush_strip',box(150,486.7,388.5+rise,140,1,6.5),'brush','#303a41','reference')
 for x,z in entry_fix:
  cap_screw=z>notch;head_y=488 if cap_screw else 486.5
  add(f'Rear_MCIO_{"cap" if cap_screw else "base"}_M3x8_screw_{x}',screw((x,head_y,z),(0,-1,0),'M3',8),'entry_fasteners','#304553')
  add(f'Rear_MCIO_captive_M3_nut_{x}_{z:g}',nut((x,483.5,z),(0,-1,0),'M3'),'entry_fasteners','#b39451')
 add('Rear_MCIO_35x14_plug_transit_cap_removed',box(202.5,440,383+rise,35,100,14),'clearance','#cb843c','clearance',False)
 for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
  add(f'Rear_vent_captive_thumbscrew_{x}',captive_screw((1.5 if x==0 else 438.5,477.2,390),ax,5),'fasteners')
  add(f'Rear_vent_nut_{x}',nut((nx,477.2,390),ax,'M3'),'fasteners')
 # The lid is a flat top with two welded inset strips.
 lid_tools=[hole_side(y,H-10,1.8) for y in (118.2,433.2)]
 lid_pieces=[form('Upper_module_lid_top_sheet',box(0,2,H-1.5,W,D-2,1.5),1.5,[],lid_tools)[1]]
 lid_pieces+=[form(f'Upper_module_lid_{side}_return_strip',box(x,22,H-18,1.5,438,16.5),1.5,[],lid_tools)[1] for side,x in (('left',1.5),('right',437))]
 add('Upper_module_side_fastened_lid',union([p['shape'] for p in lid_pieces]),'lid',visible=False,pieces=lid_pieces)
 for y in (118.2,433.2):
  for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
   add(f'Lid_captive_thumbscrew_{x}_{y}',captive_screw((1.5 if x==0 else 438.5,y,H-10),ax,5),'lid_screws',visible=False)
   add(f'Lid_captive_nut_{x}_{y}',nut((nx,y,H-10),ax,'M3'),'lid_guides')
 # OEM mating holes are intentionally absent: transfer from the actual removed cover.
 ring=cut(box(0,0,220,W,D,1.5),[box(15,15,219,410,455,4)]+[cyl(x,y,219,1.7,4) for x,y in mounting])
 # Joined assembly: flat ring and two welded return strips.
 adapter_pieces=[dict(name='Replacement_lid_adapter_ring',shape=ring,t=1.5,bends=[])]
 adapter_pieces+=[dict(name=f'Replacement_lid_adapter_{side}_return_strip',shape=box(x,20,205,1.5,445,15),t=1.5,bends=[]) for side,x in (('left',1.5),('right',437))]
 adapter=add('Replacement_lid_adapter_with_undrilled_OEM_side_returns',union([p['shape'] for p in adapter_pieces]),'adapter','#889ba8',pieces=adapter_pieces)
 profile('adapter_ring_no_returns_TRANSFER_OEM_HOLES',adapter,'z',221.5)
 gasket=cut(box(0,0,221.5,W,D,.75),[box(15,15,221,410,455,2)]+[cyl(x,y,221,1.7,3) for x,y in mounting])
 add('Adapter_perimeter_gasket_0p75_nominal',gasket,'gasket','#35464d','reference')
 for x,y in mounting:
  add(f'Module_to_adapter_M3x8_{x}_{y}',screw((x,y,223.75),(0,0,-1),'M3',8),'adapter_fasteners')
  add(f'Adapter_captive_nut_{x}_{y}',nut((x,y,220),(0,0,-1),'M3'),'adapter_fasteners','#b39451')
 # This is a size reference, not a reverse-engineered OEM chassis or motherboard layout.
 ref=union([box(0,0,0,W,D,1.5),box(0,0,1.5,1.5,D,218.5),box(438.5,0,1.5,1.5,D,218.5),box(0,0,1.5,W,1.5,218.5),box(0,483.5,1.5,W,1.5,218.5)])
 add('RM53_502_440x485x220_open_body_SIZE_REFERENCE_ONLY',ref,'oem_reference','#728392','reference')
 add('OEM_rear_fan_cage_530mm_total_depth_keepout',box(0,485,0,W,45,220),'oem_cage','#cb843c','clearance',False)
 # Individual preterminated cables pass through both aligned openings; all unplug before tray lift.
 for x in (100,130,160,190,244,274,304,329):
  xx=440-x;yy=150.2 if x==329 else (170.2 if x>=244 else 165.2)
  from build_chassis import tube
  add(f'MCIO_vertical_service_route_{x}',tube([(xx,yy,190),(xx,yy,269.75),(xx,193.7,269.75)],3),'mcio','#337f89','reference')
 for i in range(10):
  # Reference upper mating plugs reuse the checked full-enclosure locations.
  p=next(p for p in full_parts if p['name']==f'GPU_{i+1}_nose_power_plug_envelope')
  q=p.copy();q['shape']=q['shape'].translate((0,0,lift));parts.append(q)
 # Power service stubs pass through the openings before reaching the forward GPU plugs.
 for i in range(10):
  p=next(p for p in full_parts if p['name']==f'GPU_{i+1}_nose_power_plug_envelope')
  c=p['shape'].Center();px=c.x;pz=c.z+lift;nose=c.y+11
  sx=440-(24+(i%5)*16);sy=137.2+(i//5)*19;lane=113.2+(i//5)*18
  points=[(sx,sy,190),(sx,sy,250.25+(i//5)*16),(px,lane,253.25+(i//5)*16),(px,lane,pz-22),(px,nose-57,pz),(px,nose-22,pz)]
  add(f'GPU_{i+1}_paired_power_service_stub',tube(points,6),'power','#cb843c','reference')
 add('External_MCIO_rear_entry_optional_route',tube([(220,540,390+rise),(220,460,390+rise),(220,180,390+rise),(330,180,350),(330,180,269.75),(340,193.7,269.75)],3),'external_route','#337f89','clearance',False)
 add('Backplane_auxiliary_power_service_stub',tube([(352,158.2,190),(352,158.2,266.75),(367,243.2,267.75)],4),'power','#cb843c','reference')
 # Captive nuts become extruded tapped threads in the sheet that held them.
 tapped_threads=tap_captive_nuts(parts,lambda p:'nut' in p['name'] and 'DIN562' not in p['name'] and '_guide_strip_' not in p['name'])
 (out/'tapped_threads.json').write_text(json.dumps(tapped_threads,indent=2))
 # Floor passage fit and removable-tray travel are checked with disconnected harnesses.
 fixed=[p for p in parts if not p['moving'] and p['role']=='fabricated' and p['group'] in ('shell','guides','partition','strain_relief','adapter')]
 moving=[p for p in parts if p['moving'] and p['role']!='clearance' and p['group'] not in ('fasteners','board_alternatives')]
 motion=[]
 for dz in (0,5,25,90,190,360):
  hits=[]
  for p in moving:
   s=p['shape'].translate((0,0,dz))
   for q in fixed:
    if overlap(s,q['shape'])>1e-4:hits.append([p['name'],q['name']])
  motion.append(dict(lift_mm=dz,intersections=hits))
 route_hits=[]
 for p in parts:
  if p['group'] not in ('mcio','power','external_route'):continue
  for q in fixed:
   if overlap(p['shape'],q['shape'])>1e-4:route_hits.append([p['name'],q['name']])
 signal_power_hits=[]
 for p in parts:
  if p['group']!='mcio':continue
  for q in parts:
   if q['group'] in ('power','fans','gpus','aux_card') and overlap(p['shape'],q['shape'])>1e-4:signal_power_hits.append([p['name'],q['name']])
 # Intake parts must clear every other part; fan screws thread into fan plastic and grille screws into formed threads.
 intake_hits=[]
 for p in parts:
  if p['group'] not in ('fans','fan_pads','intake_grilles','intake_fasteners'):continue
  for q in parts:
   if q is p or q['role']=='clearance' or q['group'] in ('board_alternatives','oem_cage'):continue
   screw_in_fan=('_self_tapping_5x8_screw_' in p['name'] and q['group'] in ('fans','fan_pads')) or ('_self_tapping_5x8_screw_' in q['name'] and p['group'] in ('fans','fan_pads'))
   screw_in_fan|=p.get('thread_host')==q['name'] or q.get('thread_host')==p['name']
   if not screw_in_fan and overlap(p['shape'],q['shape'])>1e-4:intake_hits.append(sorted([p['name'],q['name']]))
 intake_hits=sorted(map(list,{tuple(h) for h in intake_hits}))
 gpu_top=max(p['shape'].BoundingBox().zmax for p in parts if p['group']=='gpus')
 fan_rows=[dict(model=r['model'],size_mm=r['size'],depth_mm=r['depth'],count=len(r['xs']),centres_x_mm=list(r['xs']),centre_z_mm=r['z'],hole_pitch_mm=r['pitch'],air_opening_diameter_mm=r['opening'],padded_envelope_mm=r['pad'],screw_penetration_mm=8-(3 if r['pad'] else 2)) for r in rows]
 checks=dict(routing_structure_intersections=route_hits,MCIO_to_components=signal_power_hits,intake_component_intersections=intake_hits,body_width_mm=440,body_depth_mm=485,module_base_z_mm=bottom,module_height_mm=H-bottom,module_rack_units=5,combined_height_mm=H,rack_units_combined=10,OEM_body_mm=[440,485,220],OEM_with_fan_cage_depth_mm=530,upper_slot_count=21,slot_pitch_mm=20.32,intake_option=intake,fan_rows=fan_rows,all_intake_options=list(INTAKES),grille_fixing_axes_xz_mm=GRILLE_FIX,GPU_envelope_top_z_mm=gpu_top,lid_underside_z_mm=H-1.5,clearance_above_GPU_envelope_mm=H-1.5-gpu_top,chassis_fan_screw="5 x 8 mm self-tapping plastic fan screw",MCIO_opening_mm=[140,17.55],MCIO_opening_z_mm=[notch,H-1.5],MCIO_entry_location="rear cover top edge, above the GPU brackets",MCIO_connector_test_mm=[35,14],MCIO_service="Remove the two cap screws and folded upper brush cap before passing plugs. Disconnect external cables and remove the rear cover with its brush assembly before GPU or cartridge extraction.",interdeck_openings_mm=[195,65],cassette_motion=motion,OEM_lid_fit='UNVERIFIED: adapter side returns and fastener locations require the actual lid as a template',OEM_fastener_holes_modeled=0,load_support='Separate rack rails or rated shelf under the upper module; OEM lid screws provide location only',valid_shapes=len(parts))
 from rear_panel import gpu_rear_panel_design
 (out/'rear_panel_design.json').write_text(json.dumps(gpu_rear_panel_design(parts),indent=2))
 (out/'validation.json').write_text(json.dumps(checks,indent=2));assert not any(x['intersections'] for x in motion),motion
 assert not route_hits,route_hits
 assert not signal_power_hits,signal_power_hits
 assert not intake_hits,intake_hits
 asm=cq.Assembly(name='RM53_502_upper_GPU_module');combined=cq.Assembly(name='RM53_502_modular_size_study');meshes=[]
 for p in parts:
  color=cq.Color(*[int(p['color'][i:i+2],16)/255 for i in (1,3,5)])
  if p['role']!='clearance' and p['group']!='board_alternatives' and not gpu_geometry.cable_route(p):
   combined.add(p['shape'],name=p['name'],color=color)
   if p['group']!='oem_reference':asm.add(p['shape'],name=p['name'],color=color)
  if p['role']=='fabricated' and p['group'] in ('shell','rear_vent','lid','adapter','external_entry','intake_grilles','fan_adapters'):
   cq.exporters.export(p['shape'],str(out/'formed_parts'/f"{p['name']}.step"))
  vs,fs=p['shape'].tessellate(.7,.25);meshes.append({k:p[k] for k in ('name','group','color','role','visible','moving')}|dict(vertices=[[round(v.x,4),round(v.y,4),round(v.z,4)] for v in vs],faces=fs))
 asm.export(str(out/'upper_gpu_module.step'));combined.export(str(out/'modular_assembly.step'));cq.exporters.export(adapter,str(out/'replacement_lid_adapter.step'))
 gpu_geometry.neutral_headers(out)
 (out/'model_meshes.json').write_text(json.dumps(dict(parts=meshes,parameters=checks,cable_paths=[]),separators=(',',':')))
 (out/'parts.csv').write_text('name,group,role,moves_with_cassette\n'+'\n'.join(f"{p['name']},{p['group']},{p['role']},{p['moving']}" for p in parts)+'\n')
 return (parts,checks) if return_parts else checks

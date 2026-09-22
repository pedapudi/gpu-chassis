"""RM53-502 replacement-lid GPU module; supplier mating geometry remains a fit template."""
from pathlib import Path
import json
import cadquery as cq
from mounting_hardware import box,cyl,union,cut,screw,fan_screw,nut,slot
from build_chassis import overlap
import gpu_geometry
from front_hardware import add_ears,ear_holes,grille_holes

def build_modular(full_parts,out,return_parts=False,fan_size=140):
 assert fan_size in (120,140)
 pitch=124.5 if fan_size==140 else 105.
 half=fan_size/2; mount=pitch/2; fan_y=3 if fan_size==140 else 4
 pad_width=141 if fan_size==140 else 120
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 (out/'formed_parts').mkdir(exist_ok=True);(out/'cut_profiles').mkdir(exist_ok=True)
 W,D=440.,485.;bottom=222.25;H=399.55;lift=72.25;parts=[]
 def add(name,shape,group,color='#aebbc6',role='fabricated',visible=True,moving=False):
  assert shape.isValid(),name
  p=dict(name=name,shape=shape,group=group,color=color,role=role,visible=visible,moving=moving);parts.append(p);return shape
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
  q=p.copy();q['shape']=p['shape'].translate((0,0,lift))
  if q['group']=='fans':q['shape']=q['shape'].translate((0,-1.5,0))
  # Bearing-angle lower tips meet the upper module floor at its top surface.
  if q['group']=='guides':q['shape']=q['shape'].cut(box(-5,-5,0,450,495,bottom+1.5))
  assert q['shape'].Volume()>0,q['name'];parts.append(q)
 # Wide connector passages line up through the module floor and forward baffle.
 passage=[cq.Workplane().add(box(x,108.2,bottom-1,195,65,5)).edges('|Z').fillet(6).val() for x in (15,230)]
 mounting=[(x,y) for x in (10,430) for y in (80,242.5,410)]
 holes=[cyl(x,y,bottom-1,1.7,5) for x,y in mounting]
 floor=cut(box(0,2,bottom,W,D-2,1.5),passage+holes)
 body=union([floor,box(0,2,bottom+1.5,1.5,D-2,H-bottom-3),box(W-1.5,2,bottom+1.5,1.5,D-2,H-bottom-3)])
 bh=[]
 for y,z in [(233.2,230.25),(343.2,230.25),(443.2,230.25),(143.2,249.25),(143.2,272.25),(477.2,277.25),(477.2,362.25)]:bh.append(hole_side(y,z))
 for z in (242,320,388):bh.append(hole_side(12,z))
 bh += [hole_side(477.2,233.75),hole_side(477.2,390),hole_side(118.2,H-10,1.8),hole_side(433.2,H-10,1.8)]
 for y in (100,240,380):bh.append(hole_side(y,231,2.25))
 bh += ear_holes(0,(252,354))
 body=add('Upper_module_U_body_with_cable_passages',cut(body,bh),'shell');profile('upper_module_floor_no_returns',body,'z',bottom)
 front=union([box(0,0,bottom,440,2,H-bottom),box(1.5,2,bottom+2,1.5,18,H-bottom-4),box(437,2,bottom+2,1.5,18,H-bottom-4)])
 tools=[]
 def obround(x,z,length):
  half=(length-5.5)/2
  return union([box(x-half,-1,z-2.75,2*half,5,5.5),cyl(x-half,-1,z,2.75,5,(0,1,0)),cyl(x+half,-1,z,2.75,5,(0,1,0))])
 fan_centres=(78.,220.,362.);fan_z=(bottom+H)/2
 for x in fan_centres:tools.append(cyl(x,-1,fan_z,68,5,(0,1,0)))
 for z in (fan_z-62.25,fan_z+62.25):
  tools += [obround(x,z,9) for x in (15.75,424.25)]+[obround(x,z,27) for x in (149,291)]
 for z in (fan_z-52.5,fan_z+52.5):
  tools += [obround(x,z,7) for x in (25.5,414.5)]+[obround(x,z,44) for x in (149,291)]
 add_ears(add,0,bottom,H-bottom,(252,354),4)
 grille_fix=[(x,z) for x in (20,220,420) for z in (232,390)]
 tools += [cyl(x,-1,z,1.7,5,(0,1,0)) for x,z in grille_fix]
 tools += [hole_side(12,z) for z in (242,320,388)]
 front=add('Upper_module_front_dual_120_140mm_fan_carrier',front.cut(cq.Compound.makeCompound(tools)),'shell','#304553');profile('upper_module_front_no_returns',front,'y',0)
 all_fan_axes=[(x+dx,fan_z+dz) for m in (52.5,62.25) for x in fan_centres for dx in (-m,m) for dz in (-m,m)]
 fan_axes=[(x+dx,fan_z+dz) for x in fan_centres for dx in (-mount,mount) for dz in (-mount,mount)]
 for x in fan_centres:
  bores=[cyl(x+dx,1,fan_z+dz,2.2,31,(0,1,0)) for dx in (-mount,mount) for dz in (-mount,mount)]
  if fan_size==120:
   plate=cut(box(x-70,2,fan_z-70,140,1,140),[cyl(x,1,fan_z,58,3,(0,1,0))]+[cyl(x+dx,1,fan_z+dz,2.75,3,(0,1,0)) for dx in (-mount,mount) for dz in (-mount,mount)])
   add(f'120mm_fan_1mm_blanking_plate_{x}',plate,'fan_adapters','#aebbc6');profile(f'120mm_fan_blanking_plate_{x}',plate,'y',2)
  frame=box(x-half,fan_y,fan_z-half,fan_size,25,fan_size).cut(cyl(x,fan_y-1,fan_z,half-5,27,(0,1,0))).cut(cq.Compound.makeCompound(bores))
  rotor=union([cyl(x,fan_y+4,fan_z,20,15,(0,1,0)),box(x-2,fan_y+22,fan_z-half+5,4,2,fan_size-10)])
  add(f'Noctua_{'NF_A14' if fan_size==140 else 'NF_A12x25'}_{fan_size}x25_frame_reference_{x}',union([frame,rotor]),'fans','#304553','reference')
  # Padded envelope is published; individual pad outlines are nominal references.
  pads=[]
  for dx in (-1,1):
   for dz in (-1,1):
    xx=x-pad_width/2 if dx<0 else x+pad_width/2-12;zz=fan_z-pad_width/2 if dz<0 else fan_z+pad_width/2-12
    for yy in (fan_y-1,fan_y+25):pads.append(box(xx,yy,zz,12,1,12).cut(cyl(x+dx*mount,yy-.1,fan_z+dz*mount,2.75,1.2,(0,1,0))))
  add(f'Fan_{fan_size}mm_corner_pads_{pad_width}x{pad_width}x27_envelope_{x}',cq.Compound.makeCompound(pads),'fan_pads','#655148','reference')
 grille=box(0,-1,bottom,440,1,H-bottom)
 gh=grille_holes(-1,bottom,H-bottom,all_fan_axes,grille_fix)
 gh += [cyl(x,-2,z,4.4,4,(0,1,0)) for x,z in all_fan_axes]+[cyl(x,-2,z,1.7,4,(0,1,0)) for x,z in grille_fix]
 grille=add('Upper_module_full_face_1mm_perforated_grille',grille.cut(cq.Compound.makeCompound(gh)),'intake_grilles','#304553')
 profile('upper_module_full_face_grille',grille,'y',-1)
 for x,z in grille_fix:
  add(f'Grille_M3x8_{x}_{z}',screw((x,-1,z),(0,1,0),'M3',8),'intake_fasteners','#304553')
  add(f'Grille_captive_M3_nut_{x}_{z}',nut((x,2,z),(0,1,0),'M3'),'intake_fasteners','#b39451')
 for x,z in fan_axes:
  add(f'Upper_fan_self_tapping_5x8_screw_{x}_{z}',fan_screw((x,0,z),(0,1,0)),'intake_fasteners','#304553')
 for z in (242,320,388):
  for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
   add(f'Front_side_M3x8_{x}_{z}',screw((x,12,z),ax,'M3',8),'fasteners','#304553')
   add(f'Front_side_nut_{x}_{z}',nut((nx,12,z),ax,'M3'),'fasteners','#b39451')
 # The rear sill closes the space between the module floor and removable cartridge.
 sill=union([box(1.5,469,223.75,437,1.2,20),box(1.5,470.2,223.75,1.5,13.3,20),box(437,470.2,223.75,1.5,13.3,20)])
 sill=add('Upper_module_rear_sill_with_side_returns',sill.cut(hole_side(477.2,233.75)),'shell')
 profile('upper_module_rear_sill_no_returns',sill,'y',469)
 for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
  add(f'Rear_sill_M3x8_{x}',screw((x,477.2,233.75),ax,'M3',8),'fasteners')
  add(f'Rear_sill_nut_{x}',nut((nx,477.2,233.75),ax,'M3'),'fasteners')
 # The cassette occupies the lower rear; a separate panel closes the area above its brackets.
 vb=375.32
 vent=union([box(1.5,D-1.5,vb,437,1.5,H-1.5-vb),box(1.5,470.2,vb,1.5,13.3,H-1.5-vb),box(437,470.2,vb,1.5,13.3,H-1.5-vb),box(15,481,vb,410,2.5,1.5)])
 vh=[hole_side(477.2,390)]
 # The top-open notch accepts plugs after the folded brush cap is removed.
 vh.append(box(150,482,380.5,140,5,25))
 entry_fix=[(x,z) for x in (143,297) for z in (380.5,393)]
 vh += [cyl(x,482,z,1.7,5,(0,1,0)) for x,z in entry_fix]
 for row,z in enumerate((382,392)):
  for x in range(14+5*(row%2),427,10):
   if 132<x<308:continue
   vh.append(cyl(x,482,z,4,5,(0,1,0)))
 vent=add('Upper_module_rear_perforated_cover',vent.cut(cq.Compound.makeCompound(vh)),'rear_vent','#304553');profile('upper_module_rear_vent_no_returns',vent,'y',485)
 # Two lower screws retain the U-frame; two upper screws release the folded cap.
 base=box(138,485,vb,164,1.5,H-1.5-vb).cut(box(150,484,380.5,140,4,25))
 base=base.cut(cq.Compound.makeCompound([cyl(x,484,z,1.7,5,(0,1,0)) for x,z in entry_fix]))
 add('Rear_MCIO_lower_U_frame_140mm_top_open_entry',base,'external_entry','#304553')
 cap=union([box(138,486.5,387,10,1.5,H-1.5-387),box(292,486.5,387,10,1.5,H-1.5-387),box(138,486.5,395,164,1.5,3.05),box(138,488,396.55,164,6,1.5)])
 cap=cap.cut(cq.Compound.makeCompound([cyl(x,486,393,1.7,4,(0,1,0)) for x in (143,297)]))
 add('Rear_MCIO_removable_folded_brush_cap',cap,'external_entry','#304553')
 add('Rear_MCIO_lower_brush_strip',box(150,485.2,380.5,140,1,6.5),'brush','#303a41','reference')
 add('Rear_MCIO_upper_brush_strip',box(150,486.7,388.5,140,1,6.5),'brush','#303a41','reference')
 for x,z in entry_fix:
  cap_screw=z==393;head_y=488 if cap_screw else 486.5
  add(f'Rear_MCIO_{"cap" if cap_screw else "base"}_M3x8_screw_{x}',screw((x,head_y,z),(0,-1,0),'M3',8),'entry_fasteners','#304553')
  add(f'Rear_MCIO_captive_M3_nut_{x}_{z}',nut((x,483.5,z),(0,-1,0),'M3'),'entry_fasteners','#b39451')
 add('Rear_MCIO_35x14_plug_transit_cap_removed',box(202.5,440,383,35,100,14),'clearance','#cb843c','clearance',False)
 for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
  add(f'Rear_vent_M3x8_{x}',screw((x,477.2,390),ax,'M3',8),'fasteners')
  add(f'Rear_vent_nut_{x}',nut((nx,477.2,390),ax,'M3'),'fasteners')
 lid=union([box(0,2,H-1.5,W,D-2,1.5),box(1.5,22,H-18,1.5,438,16.5),box(437,22,H-18,1.5,438,16.5)])
 lid=cut(lid,[hole_side(y,H-10,1.8) for y in (118.2,433.2)])
 add('Upper_module_side_fastened_lid',lid,'lid',visible=False)
 for y in (118.2,433.2):
  for x,ax,nx in [(0,(1,0,0),3),(440,(-1,0,0),437)]:
   add(f'Lid_M3x6_{x}_{y}',screw((x,y,H-10),ax,'M3',6),'lid_screws',visible=False)
   add(f'Lid_captive_nut_{x}_{y}',nut((nx,y,H-10),ax,'M3'),'lid_guides')
 # OEM mating holes are intentionally absent: transfer from the actual removed cover.
 ring=cut(box(0,0,220,W,D,1.5),[box(15,15,219,410,455,4)]+[cyl(x,y,219,1.7,4) for x,y in mounting])
 ring=union([ring,box(1.5,20,205,1.5,445,15),box(437,20,205,1.5,445,15)])
 adapter=add('Replacement_lid_adapter_with_undrilled_OEM_side_returns',ring,'adapter','#889ba8')
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
 add('External_MCIO_rear_entry_optional_route',tube([(220,540,390),(220,460,390),(220,180,390),(330,180,350),(330,180,269.75),(340,193.7,269.75)],3),'external_route','#337f89','clearance',False)
 add('Backplane_auxiliary_power_service_stub',tube([(352,158.2,190),(352,158.2,266.75),(367,243.2,267.75)],4),'power','#cb843c','reference')
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
   if q['group'] in ('power','fans','gpus') and overlap(p['shape'],q['shape'])>1e-4:signal_power_hits.append([p['name'],q['name']])
 checks=dict(routing_structure_intersections=route_hits,MCIO_to_components=signal_power_hits,body_width_mm=440,body_depth_mm=485,module_base_z_mm=bottom,module_height_mm=H-bottom,combined_height_mm=H,rack_units_combined=9,OEM_body_mm=[440,485,220],OEM_with_fan_cage_depth_mm=530,upper_slot_count=20,slot_pitch_mm=20.32,fan_size_mm=fan_size,fan_pattern_mm=pitch,available_fan_patterns_mm=[105,124.5],fan_frame_pitch_mm=142,fan_centres_x_mm=list(fan_centres),fan_centre_z_mm=fan_z,fan_model_reference="Noctua NF-A14 industrialPPC" if fan_size==140 else "Noctua NF-A12x25 PWM",fan_bare_frame_mm=[fan_size,fan_size,25],fan_padded_envelope_mm=[pad_width,pad_width,27],fan_row_width_mm=284+pad_width,chassis_fan_screw="5 x 8 mm self-tapping plastic fan screw",GPU_fan_screw_penetration_mm=8-fan_y,fan_mount_slot_mm=[9 if fan_size==140 else 7,5.5],shared_fan_mount_slot_mm=[27 if fan_size==140 else 44,5.5],MCIO_opening_mm=[140,17.55],MCIO_entry_location="rear above GPU brackets",MCIO_connector_test_mm=[35,14],MCIO_service="Remove the two cap screws and folded upper brush cap before passing plugs. Disconnect external cables and remove the rear cover with its brush assembly before GPU or cartridge extraction.",interdeck_openings_mm=[195,65],cassette_motion=motion,OEM_lid_fit='UNVERIFIED: adapter side returns and fastener locations require the actual lid as a template',OEM_fastener_holes_modeled=0,load_support='Separate rack rails or rated shelf under the upper module; OEM lid screws provide location only',valid_shapes=len(parts))
 (out/'validation.json').write_text(json.dumps(checks,indent=2));assert not any(x['intersections'] for x in motion),motion
 assert not route_hits,route_hits
 assert not signal_power_hits,signal_power_hits
 asm=cq.Assembly(name='RM53_502_upper_GPU_module');combined=cq.Assembly(name='RM53_502_modular_size_study');meshes=[]
 for p in parts:
  color=cq.Color(*[int(p['color'][i:i+2],16)/255 for i in (1,3,5)])
  if p['role']!='clearance' and p['group']!='board_alternatives':
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

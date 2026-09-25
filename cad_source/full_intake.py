"""Interchangeable single-row intake inserts for the full 9U enclosure.

Exported assembly coordinates are used directly. The AIO and GPU deck datums
remain fixed. AP183 dimensions follow the manufacturer's fan drawing.
"""
from pathlib import Path
import json,io,pickle
import cadquery as cq
from mounting_hardware import box,cyl,union,screw,nut,fan_screw
from front_hardware import grille_holes
from gpu_geometry import neutral_headers,cable_route
from sheetmetal import fold

FAN_DRAWING='https://www.silverstonetek.com/upload/goods_cable_define/fan-cable-define.pdf'
CARRIER='Front_fan_carrier_with_side_returns'
GRILLE='Full_face_1mm_perforated_grille_AIO_and_GPU'
INSERT_FIXES=[(x,z) for x in (30.,410.) for z in (175.,270.,365.)]
GRILLE_FIXES=[(x,z) for x in (15.,425.) for z in (32.,138.,270.,383.)]

def intake_part(a):
 return a['group'] in ('fans','intake_fasteners','intake_grilles') or a['name']==CARRIER or a['name'].startswith('Full_chassis_upper_intake_insert_')

def slot(x,y,z,length,width,depth):
 h=(length-width)/2;r=width/2
 return union([box(x-h,y,z-r,2*h,depth,width),cyl(x-h,y,z,r,depth,(0,1,0)),cyl(x+h,y,z,r,depth,(0,1,0))])

def settings(mode):
 assert mode in ('2x180','3x120')
 size=180 if mode=='2x180' else 120
 return dict(mode=mode,size=size,depth=32 if size==180 else 38,pitch=165 if size==180 else 105,
             x_centres=[128.,312.] if size==180 else [100.,220.,340.],z=270.,opening=175 if size==180 else 116)

def configure(parts,mode):
 spec=settings(mode);result=[a for a in parts if not intake_part(a)]
 def add(name,shape,group='shell',role='fabricated',color='#304553',pieces=None):
  assert shape.isValid() and shape.Volume()>0,name
  result.append(dict(name=name,shape=shape,group=group,color=color,role=role,visible=True,moving=False)|(dict(pieces=pieces) if pieces else {}))
 # The unchanged side returns retain all body, ear and grille attachment datums.
 front=union([box(0,0,0,440,2,399.25),box(1.5,2,2,1.5,18,395.25),box(437,2,2,1.5,18,395.25),box(1.5,2,2,18.5,1.5,395.25),box(420,2,2,18.5,1.5,395.25)])
 cuts=[box(24,-1,159,392,4,222)]
 for x in (100,220,340):cuts.append(cyl(x,-1,85,58,5,(0,1,0)))
 for z in (32.5,137.5):
  cuts += [slot(x,-1,z,9,4.8,5) for x in (47.5,392.5)]
  cuts += [slot(x,-1,z,24,4.8,5) for x in (160,280)]
 cuts += [cyl(x,-1,z,1.7,6,(0,1,0)) for x,z in GRILLE_FIXES]
 cuts += [cyl(-5,12,z,1.7,450,(1,0,0)) for z in (22,148,205,290,381.45)]
 front_cuts=cq.Compound.makeCompound(cuts)
 # A factory-attached backing ring supports the flush, front-removable insert.
 ring=box(21,2,150,398,2,240).cut(box(35,1,170,370,4,200))
 ring=ring.cut(cq.Compound.makeCompound([cyl(x,1,z,1.7,4,(0,1,0)) for x,z in INSERT_FIXES]))
 # Joined assembly: 2 mm face, two formed 1.5 mm side angles and the 2 mm backing ring.
 pieces=[dict(name='Full_chassis_front_carrier_2mm_face',shape=box(0,0,0,440,2,399.25).cut(front_cuts),t=2.,bends=[])]
 for side,x0,cx,sx in (('left',1.5,1.5,1),('right',420,438.5,-1)):
  bends=[];angle=fold(union([box(1.5 if sx>0 else 437,2,3,1.5,18,394.25),box(x0,2,3,18.5,1.5,394.25)]),bends,'z',(cx,2),(sx,1),1.5)
  pieces.append(dict(name=f'Full_chassis_front_carrier_{side}_1p5mm_side_angle',shape=angle.cut(front_cuts),t=1.5,bends=bends))
 pieces.append(dict(name='Full_chassis_front_carrier_2mm_backing_ring',shape=ring,t=2.,bends=[]))
 add(CARRIER,union([p['shape'] for p in pieces]),pieces=pieces)
 insert=box(25,0,160,390,2,220);cuts=[cyl(x,-1,270,spec['opening']/2,4,(0,1,0)) for x in spec['x_centres']]
 axes=[(x+dx,270+dz) for x in spec['x_centres'] for dx in (-spec['pitch']/2,spec['pitch']/2) for dz in (-spec['pitch']/2,spec['pitch']/2)]
 for z in (270-spec['pitch']/2,270+spec['pitch']/2):
  if mode=='2x180':cuts += [slot(x,-1,z,length,5.5,4) for x,length in ((45.5,9),(220,24.5),(394.5,9))]
  else:cuts += [slot(x,-1,z,length,5.5,4) for x,length in ((47.5,9),(160,24),(280,24),(392.5,9))]
 cuts += [cyl(x,-1,z,1.7,4,(0,1,0)) for x,z in INSERT_FIXES]
 add('Full_chassis_upper_intake_insert_'+mode,insert.cut(cq.Compound.makeCompound(cuts)))
 for x,z in INSERT_FIXES:
  add(f'Intake_insert_M3x8_screw_{x}_{z}',screw((x,0,z),(0,1,0),'M3',8),'intake_fasteners')
  add(f'Intake_insert_captive_M3_nut_{x}_{z}',nut((x,4,z),(0,1,0),'M3'),'intake_fasteners',color='#b39451')
 # One grille has tool access for both insert patterns and the unchanged AIO.
 all_axes=[(x+dx,z+dz) for x in (100,220,340) for z in (85,) for dx in (-52.5,52.5) for dz in (-52.5,52.5)]
 for other in ('2x180','3x120'):
  s=settings(other);all_axes += [(x+dx,270+dz) for x in s['x_centres'] for dx in (-s['pitch']/2,s['pitch']/2) for dz in (-s['pitch']/2,s['pitch']/2)]
 access=all_axes+INSERT_FIXES
 cuts=grille_holes(-1,0,399.25,access,GRILLE_FIXES)
 cuts += [cyl(x,-2,z,1.7,4,(0,1,0)) for x,z in GRILLE_FIXES]
 cuts += [cyl(x,-2,z,4.4,4,(0,1,0)) for x,z in access]
 add(GRILLE,box(0,-1,0,440,1,399.25).cut(cq.Compound.makeCompound(cuts)),'intake_grilles')
 for x,z in GRILLE_FIXES:
  add(f'Intake_grille_M3x8_{x}_{z}',screw((x,-1,z),(0,1,0),'M3',8),'intake_fasteners')
  add(f'Intake_grille_M3_nut_{x}_{z}',nut((x,3.5,z),(0,1,0),'M3'),'intake_fasteners',color='#b39451')
 size=spec['size'];depth=spec['depth'];pitch=spec['pitch']
 for x in spec['x_centres']:
  # Conservative frame envelope; the supplier drawing controls lug details.
  frame=box(x-size/2,2,270-size/2,size,depth,size)
  cutout=[cyl(x,1,270,(175 if size==180 else 110)/2,depth+2,(0,1,0))]
  cutout += [cyl(x+dx,1,270+dz,2.25 if size==180 else 2.2,depth+2,(0,1,0)) for dx in (-pitch/2,pitch/2) for dz in (-pitch/2,pitch/2)]
  frame=frame.cut(cq.Compound.makeCompound(cutout))
  frame=union([frame,cyl(x,8,270,size*.14,depth-8,(0,1,0)),box(x-2,7,270-size/2+5,4,2,size-10)])
  add(f'Upper_{size}mm_fan_{x}_270',frame,'fans','reference')
  for dx in (-pitch/2,pitch/2):
   for dz in (-pitch/2,pitch/2):
    sx,sz=x+dx,270+dz;add(f'GPU_fan_self_tapping_5x8_screw_{sx}_{sz}',fan_screw((sx,0,sz),(0,1,0)),'intake_fasteners')
 # The insert and grille nuts become extruded tapped threads in the carrier.
 from threads import tap_captive_nuts
 tap_captive_nuts(result,lambda a:a['name'].startswith(('Intake_insert_captive_M3_nut_','Intake_grille_M3_nut_')))
 return result,spec

def export_variant(parts,base_checks,out,mode):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'formed_parts').mkdir(exist_ok=True);(out/'cut_profiles').mkdir(exist_ok=True)
 checks=dict(base_checks);s=settings(mode)
 checks.update(full_intake_mode=mode,upper_fan_size_mm=s['size'],upper_fan_centres_x_mm=s['x_centres'],upper_fan_centres_z_mm=[270],upper_fan_count=len(s['x_centres']),upper_fan_depth_mm=s['depth'],upper_fan_hole_pitch_mm=s['pitch'],front_intake_aperture_mm=s['opening'],grille_to_GPU_fan_face_mm=2,fan_frame_pitch_mm=s['x_centres'][1]-s['x_centres'][0],GPU_fan_screw_penetration_mm=6,valid_shapes=len(parts),fan_size_mm=s['size'],upper_fan_reference='SilverStone AP183 mounting drawing' if s['size']==180 else '120 mm frame, ARCTIC 105 mm square mounting reference; 38 mm depth allowance',intake_insert_bounds_xyz_mm=[[25,0,160],[415,2,380]],intake_insert_fixing_axes_xz_mm=INSERT_FIXES)
 for stale in ('intake_component_intersections','cassette_motion','individual_GPU_motion','lower_retimer_motion'):
  checks.pop(stale,None)
 checks['validation_scope']='Inherited rear/motherboard datums; use full_intake_checks.json for changed intake geometry and sampled service paths.'
 (out/'validation.json').write_text(json.dumps(checks,indent=2));(out/'parameters.json').write_text(json.dumps(dict(width=440,depth=485,height=399.25,gpu_deck_z=170,full_intake_mode=mode,upper_fan_size=s['size']),indent=2))
 serial=[]
 for a in parts:
  q=a.copy();q.pop('pieces',None);buf=io.BytesIO();q.pop('shape').exportBrep(buf);q['brep']=buf.getvalue();serial.append(q)
  if a['role']=='fabricated' and a['group'] in ('shell','cassette','lid','rear_vent','guides','strain_relief','mounts','motherboard_mounts','psu_support','intake_grilles','rack_ears') and not any(t in a['name'] for t in ('nut','screw','standoff','washer','M3','M4')):cq.exporters.export(a['shape'],str(out/'formed_parts'/(a['name']+'.step')))
 (out/'parts.brep.pickle').write_bytes(pickle.dumps(serial))
 for name,filter_part in [('double_deck_assembly',lambda a:a['role']!='clearance' and a['group'] not in ('board_alternatives','io_shield') and not cable_route(a)),('front_intake_assembly',intake_part),('upper_fan_modules',lambda a:a['group']=='fans')]:
  asm=cq.Assembly(name=name)
  for a in parts:
   if filter_part(a):asm.add(a['shape'],name=a['name'],color=cq.Color(*[int(a['color'][i:i+2],16)/255 for i in (1,3,5)]))
  asm.export(str(out/(name+'.step')))
 for name in (CARRIER,GRILLE,'Full_chassis_upper_intake_insert_'+mode):
  shape=next(a['shape'] for a in parts if a['name']==name);station={CARRIER:0,GRILLE:-1}.get(name,0)
  face=max((f for f in shape.Faces() if abs(f.Center().y-station)<1e-5),key=lambda f:f.Area())
  cq.exporters.export(cq.Workplane().newObject(face.rotate((0,0,0),(1,0,0),90).Wires()),str(out/'cut_profiles'/(name+'.dxf')))
 neutral_headers(out)
 (out/'parts.csv').write_text('name,group,role,moves_with_cassette\n'+'\n'.join(f"{a['name']},{a['group']},{a['role']},{a['moving']}" for a in parts)+'\n')
 return checks

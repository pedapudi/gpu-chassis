"""Nine-unit sheet-metal chassis with a removable twenty-one-position GPU deck.
All lengths are millimetres. Hardware envelopes do not certify supplier fit.
"""
from pathlib import Path
import argparse,json,math,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cadquery as cq
from mounting_hardware import box,cyl,union,cut,screw,fan_screw,nut,hex_prism,supports,slot,pem_632
import gpu_geometry
from sheetmetal import fold,transform_bends
from threads import tap_captive_nuts,emboss_boss,form_thread
import rear_closure as rc
from front_hardware import add_ears,ear_holes,grille_holes
from component_models import add_psu,psu_holes,psu_vent,backplane_outline,add_board_details,BOARD_X,BOARD_Y,BOARD_SLOT_X,BOARD_MOUNT_POINTS,board_hole_tools
P=dict(width=440.,depth=485.,height=399.25,sheet=1.5,gpu_deck_z=170.,rear_bracket_plane=469.,
       motherboard_bottom=16.,motherboard_thickness=1.57,motherboard_x=20.2,standoff_body=8.,
       upper_fan_size=120,case_fan_depth=38.,aio_fan_depth=38.,aio_radiator_depth=28.,slot_pitch=20.32,upper_slot_count=21,lower_slot_count=8,
       gpu_length=266.7,gpu_height=111.76,gpu_width=40.,socket_height=11.25,socket_seating_depth=4.4,
       power_plug_length=22.,power_straight_length=35.,power_bundle_diameter=12.,
       power_plug_height_from_card_datum=28.,retimer_length=160.,mcio_bundle_diameter=6.,
       fan_mount_slot_length=9.,fan_mount_slot_width=5.5,AIO_fan_mount_slot_width=4.8,vent_hole_diameter=9.,vent_pitch=10.,
       cable_passage_width=195.,cable_passage_depth=65.,cable_passage_corner_radius=6.)

def overlap(a,b):
 aa=a.BoundingBox();bb=b.BoundingBox()
 if any(min(getattr(aa,k+'max'),getattr(bb,k+'max'))<=max(getattr(aa,k+'min'),getattr(bb,k+'min'))+1e-6 for k in 'xyz'):return 0.
 return a.intersect(b).Volume()

def tube(points,r):
 """Round-ended segments represent routing occupancy, not cable bend qualification."""
 shapes=[]
 for a,b in zip(points,points[1:]):
  v=cq.Vector(*b)-cq.Vector(*a);shapes.append(cyl(*a,r,v.Length,v.normalized().toTuple()))
 for p in points[1:-1]:shapes.append(cq.Solid.makeSphere(r,cq.Vector(*p),angleDegrees1=-90))
 return union(shapes)

def build(out,cache,fan_size=120,return_parts=False):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'formed_parts').mkdir(exist_ok=True);(out/'cut_profiles').mkdir(exist_ok=True)
 P['upper_fan_size']=fan_size
 # Detailed component references share the chassis construction datum.
 W,H,Z=P['width'],P['height'],P['gpu_deck_z']
 # Rear-anchored hardware stays at its construction datum; added depth extends the front service bay.
 D=431.8;R=415.8;F=D-P['depth'];parts=[];paths=[];profiles=[]
 silver='#aebbc6';dark='#304553';green='#216b55';gold='#b39451';blue='#3c7b93';orange='#cb843c';teal='#337f89'
 # Construction X measures from the rear viewer's left; exported X is right-handed.
 def physical(shape):return shape.mirror('YZ',(W/2,0,0)).translate((0,-F,0))
 def add(name,shape,group,color=silver,role='fabricated',visible=True,moving=False,pieces=None):
  assert shape.isValid() and shape.Volume()>0,name
  part=dict(name=name,shape=physical(shape),group=group,color=color,role=role,visible=visible,moving=moving)
  # Formed sheet pieces carry their bend zones for flat-pattern development.
  if pieces:part['pieces']=[dict(p,shape=physical(p['shape']),bends=transform_bends(p['bends'],physical),tapped=[dict(h,centre=[W-h['centre'][0],h['centre'][1]-F,h['centre'][2]]) for h in p.get('tapped',[])]) for p in pieces]
  parts.append(part);return shape
 def form(name,shape,t,folds,tools=()):
  """Form the listed sharp corners of one sheet piece, then cut its features."""
  bends=[]
  for f in folds:shape=fold(shape,bends,*f[:3],t,**(f[3] if len(f)>3 else {}))
  shape=cut(shape,list(tools))
  return shape,dict(name=name,shape=shape,t=t,bends=bends)
 def profile(name,s,axis,value):
  s=physical(s).clean()
  if axis=='y':value-=F
  fs=[f for f in s.Faces() if abs(getattr(f.Center(),axis)-value)<1e-5]
  f=max(fs,key=lambda a:a.Area())
  if axis=='y':f=f.rotate((0,0,0),(1,0,0),90)
  elif axis=='x':f=f.rotate((0,0,0),(0,1,0),90)
  cq.exporters.export(cq.Workplane().newObject(f.Wires()),str(out/'cut_profiles'/f'{name}.dxf'))
  profiles.append(name)
 def fast(name,point,axis,thread,length,group='fasteners',moving=False,visible=True):
  return add(name,screw(point,axis,thread,length),group,dark,visible=visible,moving=moving)
 def side_holes(y,z,r=1.7):return cyl(-5,y,z,r,450,(1,0,0))
 def fan_slot(x,y,z,depth,length=9.,width=4.8):
  half=(length-width)/2;r=width/2
  return union([box(x-half,y,z-r,2*half,depth,width),cyl(x-half,y,z,r,depth,(0,1,0)),cyl(x+half,y,z,r,depth,(0,1,0))])
 def perforations(cx,cz,radius,y,depth):
  holes=[];pitch=P['vent_pitch'];r=P['vent_hole_diameter']/2
  for row in range(-int(radius/8.66)-1,int(radius/8.66)+2):
   z=cz+row*pitch*math.sqrt(3)/2
   for col in range(-int(radius/pitch)-1,int(radius/pitch)+2):
    x=cx+pitch*(col+(row%2)*.5)
    if math.hypot(x-cx,z-cz)+r<=radius:holes.append(cyl(x,y,z,r,depth,(0,1,0)))
  return holes
 # One U-section: floor and sidewalls are a single bent-sheet component.
 body=union([box(0,F+2,0,W,D-F-2,1.5),box(0,F+2,1.5,1.5,D-F-2,H-3),box(W-1.5,F+2,1.5,1.5,D-F-2,H-3)])
 panel_side_z=[22,148,205,290,381.45]
 # Cartridge rear screws sit 3.5 mm ahead of the rear-panel return ends, which stop clear of the body rear flanges.
 cassette_y=422.1
 body_holes=[side_holes(F+12,z) for z in panel_side_z]+[side_holes(424,z) for z in (22,148)]+[side_holes(cassette_y,z) for z in (205,290)]
 # Rear-facing thumbscrews: the walls end in two tapped rear flanges; the lid front locates on wall studs.
 vent_bottom=303.07;cover_low=320;cover_high=H-10;lid_studs=[(75,H-10),(380,H-10)]
 flange_adds,flange_notch,flange_folds,flange_holes=rc.body_flanges(W,D,vent_bottom,H-1.5,cover_low,cover_high)
 body_holes += flange_holes+rc.stud_holes(W,lid_studs)
 body_holes += [psu_vent(R)]+[cyl(-1,y,16.5,1.7,5,(1,0,0)) for y in (R-165,R-10)]
 # Screw positions for fixed support angles and front cable restraints.
 body_holes += [side_holes(y,158) for y in (180,290,390)]
 body_holes += [side_holes(y,z) for y,z in ((90,180),(90,200),(220,75))]
 body_holes += ear_holes(F,(45,185,345))
 body=union([body]+flange_adds).cut(flange_notch)
 body,piece=form('U_shaped_body_1p5mm_two_longitudinal_bends',body,1.5,[('y',(0,0),(1,1)),('y',(W,0),(-1,1))]+flange_folds,body_holes)
 # Four tapped bosses embossed 4.5 mm up from the floor carry the motherboard tray.
 tray_fix=[(118,80),(418,80),(118,402),(418,402)]
 for x,y in tray_fix:body=emboss_boss(body,x,y,0,1.5,4.5,'M3')
 piece['shape']=cut(piece['shape'],[cyl(x,y,-1,1.25,4) for x,y in tray_fix]);piece['tapped']=[dict(thread='M3',centre=[x,y,4.5]) for x,y in tray_fix]
 add('U_shaped_body_1p5mm_two_longitudinal_bends',body,'shell',pieces=[piece])
 # Front carrier cutouts; the face and its two side angles are separate pieces below.
 fc=[]
 for z in (85,210,330):
  for x in (100,220,340):fc.append(cyl(x,F-1,z,58,5,(0,1,0)))
  # Each boundary opening accepts the two screw axes 15 mm apart.
  for zz in (z-52.5,z+52.5):
   fc += [fan_slot(x,F-1,zz,5,9,4.8 if z==85 else 5.5) for x in (47.5,392.5)]
   fc += [fan_slot(x,F-1,zz,5,24,4.8 if z==85 else 5.5) for x in (160,280)]
 add_ears(add,F,0,H,(45,185,345),9)
 grille_fix=[(x,z) for x in (15,425) for z in (32,138,270,383)]
 fc += [cyl(x,F-1,z,1.7,5,(0,1,0)) for x,z in grille_fix]
 fc += [side_holes(F+12,z) for z in panel_side_z]
 # Joined assembly: 2 mm front face and two formed 1.5 mm side angles.
 front_pieces=[form('Front_fan_carrier_2mm_face',box(0,F,0,440,2,H),2,[],fc)[1]]
 for side,x0,cx,sx in (('left',1.5,1.5,1),('right',420,438.5,-1)):
  angle=union([box(1.5 if sx>0 else 437,F+2,3,1.5,18,H-5),box(x0,F+2,3,18.5,1.5,H-5)])
  front_pieces.append(form(f'Front_fan_carrier_{side}_1p5mm_side_angle',angle,1.5,[('z',(cx,F+2),(sx,1))],fc)[1])
 front=add('Front_fan_carrier_with_side_returns',union([p['shape'] for p in front_pieces]),'shell',dark,pieces=front_pieces);profile('front_face_no_returns',front,'y',F)
 # Side screws engage extruded tapped threads in the front returns and lower rear returns.
 for y in (F+12,424):
  for z in panel_side_z:
   if y==424 and z not in (22,148):continue
   for side,x,ax,nx in [('left',0,(1,0,0),3),('right',440,(-1,0,0),437)]:
    fast(f'{side}_panel_M3x8_{y:g}_{z}',(x,y,z),ax,'M3',8)
    add(f'{side}_panel_captive_nut_{y:g}_{z}',nut((nx,y,z),ax,'M3'),'fasteners',gold)
 # Upper rear side fixings belong to the removable cassette and are removed before lifting.
 for z in (205,290):
  for side,x,ax,nx in [('left',0,(1,0,0),3),('right',440,(-1,0,0),437)]:
   fast(f'{side}_cassette_rear_M3x8_{z}',(x,cassette_y,z),ax,'M3',8,'rear_release')
   add(f'{side}_cassette_rear_captive_nut_{z}',nut((nx,cassette_y,z),ax,'M3'),'cassette',gold,moving=True)
 # The upper rear cover sits behind the wall flanges and is removed rearward after the lid.
 vent,vent_folds,vh=rc.cover(W,D,vent_bottom,H-3,cover_low,cover_high)
 # Perforation rows stay two thicknesses clear of the lower lip bend.
 for row,z in enumerate([313.5+9.75*i for i in range(9)]):
  for x in range(14+5*(row%2),427,10):
   if rc.perforation_allowed(W,H,x,z):vh.append(cyl(x,D-2,z,4,4,(0,1,0)))
 vent,vent_piece=form('Upper_rear_perforated_cover',vent,1.5,vent_folds,vh)
 add('Upper_rear_perforated_cover',vent,'rear_vent',dark,pieces=[vent_piece])
 profile('upper_rear_perforated_face',vent,'y',D)
 for name,shape in rc.cover_thumbscrews(W,D,cover_low):add(name,shape,'fasteners',dark)
 for name,shape in rc.flange_nuts(W,D,cover_low,cover_high):add(name,shape,'fasteners',gold)
 # The lid top reaches over the cover and folds two rear tabs; its welded side returns carry L-slots for the wall studs.
 lid_top,lid_folds,lid_holes=rc.lid_top(W,D,H,F+2,cover_high)
 lid_tools=rc.lid_slots(W,H,lid_studs)+[box(-3,F+12-4.5,H-18.1,446,9,5.3)]
 lid_pieces=[form('Lid_top_sheet_with_rear_tabs',lid_top,1.5,lid_folds,lid_holes)[1]]
 lid_pieces+=[form(f'Lid_{side}_return_strip',box(x,F+22,H-18,1.5,394-F,16.5),1.5,[],lid_tools)[1] for side,x in (('left',1.5),('right',W-3))]
 add('Lid_with_rear_tabs',union([p['shape'] for p in lid_pieces]),'lid',visible=False,pieces=lid_pieces)
 for name,shape in rc.lid_thumbscrews(W,D,cover_high):add(name,shape,'lid_screws',dark,visible=False)
 for name,shape in rc.lid_studs(W,lid_studs):add(name,shape,'lid_guides',gold)
 def fan(name,x,y,z,size,depth,group,moving=False):
  sp={80:71.5,120:105,140:124.5}[size]
  f=cut(box(x-size/2,y,z-size/2,size,depth,size),[cyl(x,y-1,z,size/2-5,depth+2,(0,1,0))]+[cyl(x+dx,y-1,z+dz,(2.2 if size==120 else 2.25),depth+2,(0,1,0)) for dx in (-sp/2,sp/2) for dz in (-sp/2,sp/2)])
  f=union([f,cyl(x,y+4,z,size*.14,depth-8,(0,1,0)),box(x-2,y+3,z-size/2+5,4,2,size-10)])
  return add(name,f,group,dark,'reference',moving=moving)
 # One full-face removable grille spans the AIO and both GPU intake rows.
 grille=box(0,F-1,0,440,1,H)
 fan_axes=[(x+dx,z+dz) for x in (100,220,340) for z in (85,210,330) for dx in (-52.5,52.5) for dz in (-52.5,52.5)]
 tools=grille_holes(F-1,0,H,fan_axes,grille_fix)
 tools += [cyl(x,F-2,z,1.7,4,(0,1,0)) for x,z in grille_fix]
 tools += [cyl(x,F-2,z,4.4,4,(0,1,0)) for x,z in fan_axes]
 grille=grille.cut(cq.Compound.makeCompound(tools))
 add('Full_face_1mm_perforated_grille_AIO_and_GPU',grille,'intake_grilles',dark)
 profile('full_face_intake_grille',grille,'y',F-1)
 for x,z in grille_fix:
  fast(f'Intake_grille_M3x8_{x}_{z}',(x,F-1,z),(0,1,0),'M3',8,'intake_fasteners')
  add(f'Intake_grille_M3_nut_{x}_{z}',nut((x,F+3.5,z),(0,1,0),'M3'),'intake_fasteners',gold)
 for z in (210,330):
  for x in (100,220,340):
   fan(f'Upper_120mm_fan_{x}_{z}',x,F+2,z,120,P['case_fan_depth'],'fans')
   for dx in (-52.5,52.5):
    for dz in (-52.5,52.5):
     sx,sz=x+dx,z+dz
     add(f'GPU_fan_self_tapping_5x8_screw_{sx}_{sz}',fan_screw((sx,F,sz),(0,1,0)),'intake_fasteners',dark)
 # The PSU reference includes the actual envelope and photo-derived interfaces.
 cradle_y=add_psu(add,R)
 for y in cradle_y:
  fast(f'PSU_cradle_M3x6_side_screw_{y}',(0,y,16.5),(1,0,0),'M3',6)
  add(f'PSU_cradle_M3_nut_{y}',nut((3,y,16.5),(1,0,0),'M3'),'fasteners',gold)
 # Board and slots share a seating datum. Aperture dimensions follow ATX/CEM.
 board_top=17.57;host_w=board_top+11.25-4.4;host_bearing=host_w+104.86
 board_datum_y=R-59.05+46.94;board_rear=board_datum_y+10.16;board_front=board_rear-330.2
 host_axes=[115+162.26+20.32*i for i in range(7)];host_centres=[115+162.26+20.32*i+7.155 for i in range(8)]
 io_x=115+288.29-5.196*25.4-6.25*25.4;io_z=16-.088*25.4
 lower=union([box(1.5,R,1.5,437,1.2,167),box(1.5,R+1.2,1.5,1.5,14.8,167),box(437,R+1.2,1.5,1.5,14.8,167)])
 atx=psu_holes()
 opening=cut(box(8,R-1,12,82,4,146),[box(x-6,R-2,z-6,12,6,12) for x,z in atx])
 lc=[opening,box(110,R-1,11,164,4,50)]+[cyl(x,R-1,z,1.95,4,(0,1,0)) for x,z in atx]
 lc += [box(x-7.5,R-1,host_w-.67,15,4,103) for x in host_centres]
 lc += [box(272,R-1,host_bearing,164.5,4,7)]
 lc += [box(279,R-1,140,139,5,25)]
 lc += [cyl(x,R-1,152.5,1.7,5,(0,1,0)) for x in (275,422)]
 lc += [side_holes(424,z) for z in (22,148)]
 lc += [cyl(x,R-2,z,1.7,6,(0,1,0)) for x in (122,260) for z in (7.5,64.5)]
 for x in (149,231):
  lc += [cyl(x,R-1,110,38,5,(0,1,0))]+[fan_slot(x+dx,R-1,110+dz,5,width=5.5) for dx in (-35.75,35.75) for dz in (-35.75,35.75)]
  fan(f'Lower_rear_80mm_exhaust_{x}',x,R-25,110,80,25,'exhaust')
  for dx in (-35.75,35.75):
   for dz in (-35.75,35.75):
    add(f'Rear_fan_self_tapping_5x8_screw_{x+dx}_{110+dz}',fan_screw((x+dx,R+1.2,110+dz),(0,-1,0)),'fasteners',dark)
 # Joined assembly: 1.2 mm rear web and two 1.5 mm return strips.
 # Parts in the body's floor-to-wall corners stop clear of its inside bend radius.
 corner_clear=[box(0,R-1,0,3,20,3),box(437,R-1,0,3,20,3)]
 lower_pieces=[form('Lower_rear_1p2mm_web',box(1.5,R,1.5,437,1.2,167),1.2,[],lc+corner_clear)[1]]
 lower_pieces+=[form(f'Lower_rear_{side}_1p5mm_return_strip',box(x,R+1.2,3,1.5,14.8,165.5),1.5,[],lc)[1] for side,x in (('left',1.5),('right',437))]
 lower=add('Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns',union([p['shape'] for p in lower_pieces]),'shell',pieces=lower_pieces);profile('lower_rear_face_no_returns',lower,'y',R)
 io_carrier=cut(box(108,R-1.2,4,165.86,1.2,64),[box(io_x,R-2,io_z,158.75,4,44.45)]+[cyl(x,R-2,z,1.7,6,(0,1,0)) for x in (122,260) for z in (7.5,64.5)])
 add('Flat_1p2mm_IO_carrier_with_clear_shield_lands',io_carrier,'shell');profile('IO_shield_carrier',io_carrier,'y',R-1.2)
 for x in (122,260):
  for z in (7.5,64.5):
   fast(f'IO_carrier_M3x6_{x}_{z}',(x,R+1.2,z),(0,-1,0),'M3',6)
   add(f'IO_carrier_nut_{x}_{z}',nut((x,R-1.2,z),(0,-1,0),'M3'),'fasteners',gold)
 add('WRX90_integrated_IO_shield_fit_envelope',box(io_x+.5,R-.8,io_z+.5,157.75,.8,43.45),'io_shield',dark,'reference',False)
 frame=cut(box(272,R+1.2,137,153,1.5,31),[box(279,R,140,139,5,25)]+[cyl(x,R,152.5,1.7,5,(0,1,0)) for x in (275,422)])
 add('External_MCIO_removable_frame_139x25_clear_aperture',frame,'external_entry',dark)
 for z in (140,153.5):add(f'External_MCIO_split_brush_{z}',box(279,R+1.4,z,139,1,11.5),'brush',dark,'reference')
 for x in (275,422):
  fast(f'External_entry_M3x6_{x}',(x,R+2.7,152.5),(0,-1,0),'M3',6)
  add(f'External_entry_nut_{x}',nut((x,R,152.5),(0,-1,0),'M3'),'fasteners',gold)
 add('External_35x14mm_plug_transit_envelope',box(325,R-10,145.5,35,35,14),'clearance',orange,'clearance',False)
 # Folded angles bolt to the U-shell; the GPU tray rests on them.
 # Hold-down nuts sit clear of the front bearing angle's inside bend radius.
 hold=[(12,134.5),(90,134.5),(350,134.5),(428,134.5)]
 for x in (1.5,420):
  rail=union([box(x,145,Z-1.5,18.5,270,1.5),box(1.5 if x==1.5 else 437,145,150,1.5,270,18.5)])
  rail,piece=form(f'Bolted_folded_side_bearing_{x}',rail,1.5,[('y',(1.5 if x==1.5 else 438.5,Z),(1 if x==1.5 else -1,-1))],[side_holes(y,158) for y in (180,290,390)])
  add(f'Bolted_folded_side_bearing_{x}',rail,'guides',pieces=[piece])
  ax=(1,0,0) if x==1.5 else (-1,0,0);sx=0 if x==1.5 else 440;nx=3 if x==1.5 else 437
  for y in (180,290,390):
   headx=sx-.5 if ax==(1,0,0) else sx+.5
   fast(f'Side_ledge_M3x6_{x}_{y}',(headx,y,158),ax,'M3',6)
   add(f'Side_ledge_M3_washer_{x}_{y}',cyl(headx,y,158,3.5,.5,ax).cut(cyl(headx,y,158,1.6,.5,ax)),'fasteners')
   add(f'Side_ledge_nut_{x}_{y}',nut((nx,y,158),ax,'M3'),'fasteners',gold)
 front_ledge=union([box(1.5,126,168.5,437,19,1.5),box(1.5,126,150,437,1.5,18.5)])
 front_ledge,piece=form('Front_bearing_angle_spot_welded_to_side_angles',front_ledge,1.5,[('x',(126,Z),(1,-1))],[cyl(x,y,168,2.25,4) for x,y in hold])
 add('Front_bearing_angle_spot_welded_to_side_angles',front_ledge,'guides',pieces=[piece])
 for x,y in hold:
  add(f'Tray_M4_captive_nut_{x}',nut((x,y,168.5),(0,0,-1),'M4'),'guides',gold)
  fast(f'Tray_M4x8_hold_down_{x}',(x,y,171.5),(0,0,-1),'M4',8,'hold_downs')
 tray=union([box(4.5,126,170,431,R-126,1.5),box(4.5,145,171.5,1.5,260,10.5),box(434,145,171.5,1.5,260,10.5)])
 # Partial-length side flanges need bend reliefs where the floor edge continues.
 tray,piece=form('GPU_tray_two_side_bends',tray,1.5,[('y',(4.5,170),(1,1),dict(span=(145,405),relief=True)),('y',(435.5,170),(-1,1),dict(span=(145,405),relief=True))],[cyl(x,y,169,2.25,4) for x,y in hold])
 # Four M4-tapped bosses, 4.5 mm high, carry the ends of the backplane rails.
 for x in (20,420):
  for y in (155,405):tray=emboss_boss(tray,x,y,170,1.5,4.5,'M4')
 piece['shape']=cut(piece['shape'],[cyl(x,y,169,1.65,4) for x in (20,420) for y in (155,405)]);piece['tapped']=[dict(thread='M4',centre=[x,y,174.5]) for x in (20,420) for y in (155,405)]
 add('GPU_tray_two_side_bends',tray,'cassette',moving=True,pieces=[piece]);profile('GPU_tray_floor_no_returns',tray,'z',170)
 for y in (146,399):
  # A 14 mm crown leaves an 8 mm flat between the two bends for standard press-brake tooling.
  channel,piece=form(f'GPU_tray_spot_welded_channel_{y}',union([box(22,y,168.5,396,14,1.5),box(22,y,161,396,1.5,7.5),box(22,y+12.5,161,396,1.5,7.5)]),1.5,[('x',(y,170),(1,-1)),('x',(y+14,170),(-1,-1))])
  add(f'GPU_tray_spot_welded_channel_{y}',channel,'cassette',moving=True,pieces=[piece])
 # Simple punched tie slots in side-mounted angles, outside the GPU extraction path.
 for side,x in [('power',1.5),('signal',426.5)]:
  bracket=union([box(x,70,171.5,12,50,1.5),box(1.5 if side=='power' else 437,70,171.5,1.5,50,38)])
  # Tie slots sit 3 mm from the free edge on both angles, clear of the bend.
  slot_x=x+6 if side=='power' else x+3
  bracket,piece=form(f'{side}_side_cable_restraint_angle',bracket,1.5,[('y',(1.5 if side=='power' else 438.5,171.5),(1 if side=='power' else -1,1))],[box(slot_x,y,170,3,9,5) for y in (77,96)]+[side_holes(90,z) for z in (180,200)])
  add(f'{side}_side_cable_restraint_angle',bracket,'strain_relief',pieces=[piece])
  sx=0 if side=='power' else 440;ax=(1,0,0) if side=='power' else (-1,0,0);nx=3 if side=='power' else 437
  # The lower restraint nut clears the angle's inside bend radius.
  for z in (180,200):
   fast(f'{side}_restraint_M3x8_{z}',(sx,90,z),ax,'M3',8)
   add(f'{side}_restraint_nut_{z}',nut((nx,90,z),ax,'M3'),'fasteners',gold)
 # Adjustable backplane supports: rows slide in Y and standoff studs slide in X.
 points=BOARD_MOUNT_POINTS
 def mount_add(name,s,group,color,role='fabricated',visible=True,pieces=None):
  lift=lambda shape:shape.translate((0,0,170))
  return add(name,lift(s),group,color,role,visible,True,[dict(p,shape=lift(p['shape']),bends=transform_bends(p['bends'],lift)) for p in pieces] if pieces else None)
 supports(mount_add,[171.8,265.3,381.0],points,18,female=True)
 for a in parts:
  if a['name'].startswith('Rail_M4x6_screw_'):a['thread_host']='GPU_tray_two_side_bends'
 bz=188.;bt=2.5;gw=bz+bt+11.25-4.4;gb=gw+104.86
 gpu_axes=[BOARD_X+x for x in BOARD_SLOT_X[1:-1]]
 # Twenty-one positions span all twelve sockets: slots[0] serves the leading single-width socket,
 # the ten GPUs use slots[1:], and slots[-1] also aligns with the trailing single-width socket.
 aux_axis=BOARD_X+BOARD_SLOT_X[0]
 slots=[aux_axis+7.155+i*20.32 for i in range(P['upper_slot_count'])]
 assert all(abs(slots[2*i+1]-x-7.155)<1e-9 for i,x in enumerate(gpu_axes))
 outline=backplane_outline()
 pcb=cq.Workplane('XY').polyline(outline).close().extrude(bt).translate((0,0,bz)).val()
 pcb=cut(pcb,board_hole_tools(bz-1,bt+2))
 add('Miwin_MG_SW510B_429x225_PCB_photo_reference',pcb,'backplane',green,'reference',moving=True)
 photo_extra=add_board_details(add,bz+bt)
 for name,x,y,w,d in [('Seven_slot_431p8x189',4.1,216,431.8,189),('Twelve_slot_429x225',BOARD_X,BOARD_Y,429,225)]:
  add(name+'_alternative_fit_envelope',box(x,y,bz,w,d,2.5),'board_alternatives',green,'reference',False,True)
 for i,(x,y) in enumerate(points):
  add(f'Backplane_M3_washer_{i}',cyl(x,y,190.5,3.5,.5).cut(cyl(x,y,190,1.6,2)),'fasteners',moving=True)
  fast(f'Backplane_M3x6_{i}',(x,y,191),(0,0,-1),'M3',6,moving=True)
 def socket(name,x,z,group,moving=False):
  sy=R-59.05-74.5;w=z+11.25-4.4
  s=box(x-3.75,sy,z,7.5,89,11.25).cut(box(x-.8,sy+2,w,1.6,85,5))
  s=s.fuse(box(x-.8,R-59.05-.75,w,1.6,1.5,4.4))
  add(name,s,group,dark,'reference',moving=moving)
 def bracket(name,cx,w,group,moving=False,blank=False,tapped=False):
  bearing=w+104.86;tip=bearing+.86-120.02;sx=cx-9.21
  b=box(cx-9.21,R-.86,tip+7.27,18.42,.86,111.89)
  if not blank:b=b.cut(box(cx-6.03,R-1.5,bearing+.86-10.16-89.9,12.06,3,89.9))
  b=union([b,box(cx-5.095,R-.86,tip,10.19,.86,7.27),box(cx-9.21,R-.86,bearing,18.42,11.43,.86)])
  b=cut(b,[cyl(sx,R+5.08,bearing-1,2.21,3),box(cx-9.22,R+2.87,bearing-1,max(.01,sx-cx+9.22),4.42,3)])
  add(name,b,group,gold,'reference',moving=moving)
  fast(name+'_6_32_screw',(sx,R+5.08,bearing+.86),(0,0,-1),'6-32',6.35,moving=moving)
  # Bracket screws thread into extruded tapped collars in the GPU shelf and the lower retention strip.
  if not tapped:add(name+'_captive_6_32_hex_nut',nut((sx,R+5.08,bearing-1.5),(0,0,-1),'6-32'),'fasteners',gold,moving=moving)
 def retention(name,centres,w,group,moving=False):
  bearing=w+104.86;tip=bearing+.86-120.02;x0=centres[0]-14;ww=min(436.5,centres[-1]+14)-x0
  shelf=cut(box(x0-3,R+1.2,bearing-1.5,ww+3,10.8,1.5),[cyl(x-9.21,R+5.08,bearing-2,1.95,4) for x in centres])
  add(name+'_retention_flange',shelf,group,moving=moving)
  if name!='Upper_bank':profile(name+'_retention_flange',shelf,'z',bearing-1.5)
  toe_x=max(x0,274.5) if group=='shell' else x0
  # The GPU comb is 12 mm deep for weld access and stiffness; the motherboard comb stays 4 mm to clear the board posts.
  depth=12 if group=='cassette' else 4
  toe=cut(box(toe_x,R-depth,tip+1,x0+ww-toe_x,depth,1.5),[box(x-5.395,R-1.3,tip,10.79,1.3,4) for x in centres])
  add(name+'_toe_receiver',toe,group,moving=moving)
 retention('Upper_bank',slots,gw,'cassette',True);retention('Lower_bank',host_centres,host_w,'shell')
 # Rear bank ends at the bracket shelf. The removable lid closes the space above it.
 rear=union([box(1.8,R,171.5,436.4,1.2,gb-171.5),box(1.8,R+1.2,171.5,1.2,9.8,gb-171.5),box(437,R+1.2,171.5,1.2,9.8,gb-171.5),box(1.8,R,171.5,436.4,1.2,3)])
 # Apertures stop two thicknesses below the shelf bend tangent so forming does not distort them.
 rear=cut(rear,[box(x-7.5,R-1,gw-.67,15,4,100.5) for x in slots]+[side_holes(cassette_y,z) for z in (205,290)])
 rear=add('Full_width_twenty_one_slot_rear_with_side_returns',rear,'cassette',moving=True);profile('upper_rear_face_no_returns',rear,'y',R)
 for i,x in enumerate((BOARD_X+BOARD_SLOT_X[0],BOARD_X+BOARD_SLOT_X[-1]),1):
  socket(f'Backplane_auxiliary_single_width_socket_{i}',x,190.5,'backplane',True)
 # CEM single-width envelope: 2.67 secondary-side and 14.47 primary-side component height.
 aux_body=box(aux_axis-3.455,R-1.9-266.7,gw+8.89,18.71,266.7,111.76-8.89)
 aux_edge=box(aux_axis-.785,R-59.05-71.5,gw,1.57,83,8.89).cut(box(aux_axis-1,R-59.05-.85,gw-1,2,1.7,8.8))
 add('Auxiliary_socket_1_single_width_card_envelope',union([aux_body,aux_edge]),'aux_card',green,'reference',moving=True)
 bracket('Auxiliary_socket_1_bracket',slots[0],gw,'brackets',True,tapped=True)
 for i,x in enumerate(gpu_axes):
  socket(f'GPU_socket_{i+1}',x,190.5,'backplane',True)
  body=box(x-3.455,R-1.9-266.7,gw+8.89,40,266.7,111.76-8.89)
  edge=box(x-.785,R-59.05-71.5,gw,1.57,83,8.89).cut(box(x-1,R-59.05-.85,gw-1,2,1.7,8.8))
  add(f'GPU_{i+1}_Max_Q_envelope',union([body,edge]),'gpus',blue,'reference',moving=True)
  for j in (0,1):bracket(f'GPU_{i+1}_bracket_{j+1}',slots[2*i+1+j],gw,'brackets',True,tapped=True)
 # Handles are forward of all GPU bodies; they do not cover the backplane latches.
 for x in (45,360):
  h=union([box(x,129,171.5,28,12,1.5),box(x,139.5,173,28,1.5,32)])
  h,piece=form(f'Tray_handhold_{x}',h,1.5,[('x',(141,171.5),(-1,1))],[box(x+5,138.5,181,18,4,18)])
  add(f'Tray_handhold_{x}',h,'cassette',moving=True,pieces=[piece])
 # Ten nominal SSI EEB positions matched to the ten holes in the ASUS manual.
 local=[('F',6.35,33.02),('M',6.35,237.49),('Z',6.35,322.58),('C',163.83,10.16),('H',163.83,165.10),('Y',163.83,322.58),('A',288.29,10.16),('G',288.29,165.10),('K',288.29,237.49),('X',293.37,322.58)]
 mh=[(n,115+x,board_rear-d) for n,x,d in local]
 mbtray=cut(box(112,74,6,314,336.5,2),[cyl(x,y,5,1.7,5) for _,x,y in mh]+[cyl(x,y,5,1.7,5) for x,y in tray_fix])
 # Standoffs screw into extruded M3 threads in the tray; the blank carries tap-drill holes.
 flat_tray=mbtray
 for _,x,y in mh:
  mbtray=form_thread(mbtray,cq.Vector(x,y,6),2,-1,2,'M3')[0];flat_tray=form_thread(flat_tray,cq.Vector(x,y,6),2,-1,2,'M3',collar=False)[0]
 add('WRX90_board_specific_replaceable_tray',mbtray,'motherboard_mounts',pieces=[dict(name='WRX90_board_specific_replaceable_tray',shape=flat_tray,t=2,bends=[],tapped=[dict(thread='M3',centre=[x,y,6]) for _,x,y in mh])]);profile('motherboard_tray',mbtray,'z',6)
 for x,y in tray_fix:
  fast(f'Motherboard_tray_M3x6_{x}_{y}',(x,y,8),(0,0,-1),'M3',6,'motherboard_mounts')
  parts[-1]['thread_host']='U_shaped_body_1p5mm_two_longitudinal_bends'
 board=cut(box(115,board_front,16,304.8,330.2,1.57),[cyl(x,y,15,1.7,4) for _,x,y in mh])
 add('WRX90E_SAGE_SE_EEB_reference',board,'motherboard',green,'reference')
 for n,x,y in mh:
  # M3 x 8 mm male-female standoff: 6 mm stud into the tray thread, 5.5 mm female thread above.
  post=union([hex_prism(x,y,8,5,8).cut(cyl(x,y,10.5,1.5,6)),cyl(x,y,2,1.5,6)])
  add(f'Motherboard_M3_8mm_male_female_standoff_{n}',post,'motherboard_mounts',gold)
  parts[-1]['thread_host']='WRX90_board_specific_replaceable_tray'
  add(f'Motherboard_M3_washer_{n}',cyl(x,y,17.57,3.5,.5).cut(cyl(x,y,17,1.6,2)),'motherboard_mounts')
  fast(f'Motherboard_M3x5_{n}',(x,y,18.07),(0,0,-1),'M3',5,'motherboard_mounts')
 for i,x in enumerate(host_axes):
  socket(f'Motherboard_native_x16_socket_{i+1}',x,17.57,'motherboard')
  # Short retimer geometry is a configurable fit envelope; no specific card is selected.
  card=box(x-.785,R-1.9-P['retimer_length'],host_w+8.89,1.57,P['retimer_length'],102.26)
  add(f'Retimer_{i+1}_full_height_160mm_reference',card,'retimers',green,'reference')
  bracket(f'Retimer_{i+1}_bracket',host_centres[i],host_w,'retimers')
  for j,z in enumerate((104,123)):
   add(f'Retimer_{i+1}_forward_MCIO_port_{j+1}',box(x-4,R-1.9-P['retimer_length']-10,z-4,8,10,8),'retimers',dark,'reference')
 bracket('Eighth_lower_case_blank',host_centres[7],host_w,'lower_blank',blank=True)
 # CPU position follows the manual illustration; exact socket/fitting coordinates remain adjustable.
 cpu_x=191.;cpu_y=257.
 add('WRX90_CPU_socket_location_reference',box(cpu_x-32,cpu_y-41,17.57,64,82,8),'cpu',gold,'reference')
 block=add('XE360_TR5_block_79x119x25_reference',box(cpu_x-39.5,cpu_y-59.5,25.57,79,119,25),'aio',blue,'reference')
 for x in (132,255):
  for i in range(4):add(f'WRX90_DIMM_{x}_{i}',box(x+i*7-11,185,17.57,3,135,32),'motherboard',dark,'reference')
 add('XE360_TR5_radiator_394x120x28_reference',box(23,F+3.5,25,394,28,120),'aio',dark,'reference')
 for x in (100,220,340):fan(f'Lower_AIO_120mm_fan_{x}',x,F+31.5,85,120,P['aio_fan_depth'],'aio')
 # Hose paths stay below the removable deck and forward of the retimer cards.
 # Both block fittings leave the same forward edge, matching the cooler photo.
 # Hose points are routed from explicit ports rather than reflecting a finished hose assembly.
 for x in (174,204):add(f'AIO_block_forward_fitting_{x}',union([cyl(x,185.5,38.57,7,12,(0,1,0)),cyl(x,185.5,38.57,7,7)]),'aio',dark,'reference')
 hose_routes=[[(408.5,F+31.5,110),(409,35,110),(370,75,125),(300,155,140),(204,185.5,115),(204,185.5,70),(204,185.5,45.57)],
[(408.5,F+31.5,65),(422,50,70),(370,105,110),(270,145,95),(174,160,95),(174,185.5,75),(174,185.5,45.57)]]
 lengths=[];hose_shapes=[]
 for i,pts in enumerate(hose_routes):
  e=cq.Edge.makeSpline([cq.Vector(*p) for p in pts]);w=cq.Wire.assembleEdges([e]);lengths.append(e.Length())
  h=cq.Workplane(cq.Plane(origin=pts[0],normal=e.tangentAt(0))).circle(7).sweep(cq.Workplane().newObject([w]),isFrenet=True).val()
  hose_shapes.append(h);add(f'AIO_hose_{i+1}_14mm_OD_provisional_route',h,'hoses','#526879','reference')
 # Power: twenty independent eight-pin cable legs are reserved as ten paired routes.
 # Each GPU uses its supplied dual-eight-pin adapter; no common high-current junction is implied.
 nose=R-1.9-266.7;pz=gw+P['power_plug_height_from_card_datum']
 for i,x in enumerate(gpu_axes):
  px=x+16.5
  plug=box(px-10,nose-22,pz-6,20,22,12)
  add(f'GPU_{i+1}_nose_power_plug_envelope',plug,'power',orange,'reference')
  straight=35.;end=nose-22-straight
  # Front harness lanes are below the fan frame, then rise ahead of each GPU nose.
  points=[(24+(i%5)*16,220,30+(i//5)*20),(24+(i%5)*16,84+(i//5)*19,40+(i//5)*20),(24+(i%5)*16,84+(i//5)*19,178+(i//5)*16),
          (px,60+(i//5)*18,181+(i//5)*16),(px,60+(i//5)*18,pz-22),(px,end,pz),(px,nose-22,pz)]
  shape=tube(points,6);add(f'GPU_{i+1}_paired_power_cable_route',shape,'power',orange,'reference')
  paths.append(dict(name=f'GPU {i+1} paired power leads',points=points,radius=6))
  add(f'GPU_{i+1}_power_no_bend_zone',box(px-11,end,pz-8,22,35,16),'clearance',orange,'clearance',False)
 # The backplane has a separate auxiliary-power service route below the GPU bodies.
 bp_power=[(80,220,95),(112,140,108),(78,105,160),(88,105,180),(88,105,194.5),(73,190,195.5)]
 add('Backplane_auxiliary_power_route_provisional',tube(bp_power,4),'power',orange,'reference')
 paths.append(dict(name='Backplane auxiliary power',points=bp_power,radius=4))
 # Eight edge-bank MCIO ports span both switches. Four paired retimer routes
 # illustrate connector access; port assignments are not an electrical design.
 mcio_front_x=[100.,130.,160.,190.,244.,274.,304.,329.]
 mcio_shapes=[]
 for i,dest in enumerate(mcio_front_x):
  host=i//2;x=host_axes[host];port_z=(104,123)[i%2]
  rise_x=dest;rise_y=97. if i==7 else (117. if i>=4 else 112.)
  points=[(x,243.9,port_z),(x,200,70+i%2*9),(x,30,70+i%2*9),(rise_x,30,70+i%2*9),(rise_x,rise_y,70+i%2*9),(rise_x,rise_y,197.5),(dest,122,197.5),(dest,140.5,197.5)]
  sh=tube(points,3);mcio_shapes.append(sh)
  add(f'Internal_MCIO_retimer_{host+1}_port_{i%2+1}_route',sh,'mcio',teal,'reference')
  add(f'Backplane_MCIO_edge_bank_port_{i+1}',box(dest-12,BOARD_Y,190.5,24,10,8),'backplane',dark,'reference',moving=True)
  add(f'Backplane_MCIO_mated_plug_{i+1}_provisional',box(dest-12,BOARD_Y-25,190.5,24,25,14),'mcio',teal,'reference')
  paths.append(dict(name=f'Retimer {host+1} port {i%2+1} MCIO',points=points,radius=3))
 # The external option enters the same long-edge connector bank after passing the side corridor.
 ext=[(350,D+40,152.5),(350,R-18,152.5),(431,365,150),(431,200,70),(329,150,70),(329,97,70),(329,97,197.5),(329,140.5,197.5)]
 ext_shape=tube(ext,3);mcio_shapes.append(ext_shape)
 add('External_MCIO_optional_route',ext_shape,'external_route',teal,'clearance',False)
 # Compact tie tabs touch the shell. Cable ties are released and harnesses parked forward for service.
 tab=union([box(1.5,205,60,1.5,30,30),box(1.5,205,60,15,30,1.5)])
 # The tie slot sits 3 mm clear of the bend.
 tab,piece=form('Lower_PSU_harness_side_tie_tab',tab,1.5,[('y',(1.5,60),(1,1))],[side_holes(220,75),box(7.5,211,59,4,16,4)])
 add('Lower_PSU_harness_side_tie_tab',tab,'strain_relief',pieces=[piece])
 fast('Lower_PSU_tie_M3x8',(0,220,75),(1,0,0),'M3',8)
 add('Lower_PSU_tie_M3_nut',nut((3,220,75),(1,0,0),'M3'),'fasteners',gold)
 from rear_panel import consolidate_gpu_rear
 rear_panel_design=consolidate_gpu_rear(parts,out)
 (out/'rear_panel_design.json').write_text(json.dumps(rear_panel_design,indent=2))
 rear_shape=next(a['shape'] for a in parts if a['name']=='Full_width_twenty_one_slot_rear_with_side_returns')
 for a in parts:
  if 'cassette_rear_captive_nut' in a['name']:
   assert a['shape'].distance(rear_shape)<1e-5 and overlap(a['shape'],rear_shape)<1e-5,a['name']
 # Captive nuts become extruded tapped threads in the sheet that held them; sliding crossbar nuts stay.
 tapped_threads=tap_captive_nuts(parts,lambda p:'nut' in p['name'] and 'DIN562' not in p['name'] and '_guide_strip_' not in p['name'])
 (out/'tapped_threads.json').write_text(json.dumps(tapped_threads,indent=2))
 lid_shape=next(a['shape'] for a in parts if a['group']=='lid')
 lid_hits=[a['name'] for a in parts if a['group']=='fasteners' and overlap(lid_shape,a['shape'])>1e-4]
 assert not lid_hits,('Lid conflicts with panel fasteners',lid_hits)
 # With its thumbscrews loosened, the lid slides rearward off the wall studs and lifts clear.
 lid_removal=rc.lid_removal_hits(lid_shape,[a for a in parts if a['group'] not in ('lid','lid_screws','board_alternatives') and a['role']!='clearance'],overlap)
 assert not lid_removal,('Lid removal path is blocked',lid_removal[:6])
 # Board components must clear one another and the selected mounting fasteners.
 bp=[a for a in parts if a['group']=='backplane' and 'PCB_photo_reference' not in a['name']]
 bp_hits=[]
 for i,a in enumerate(bp):
  for b in bp[i+1:]:
   if overlap(a['shape'],b['shape'])>1e-4:bp_hits.append([a['name'],b['name']])
  for b in parts:
   if b['name'].startswith(('Backplane_M3_washer_','Backplane_M3x6_')) and overlap(a['shape'],b['shape'])>1e-4:bp_hits.append([a['name'],b['name']])
 assert not bp_hits,('Backplane component conflicts',bp_hits)
 # Remove the lid, rear cover and cables before lifting the cartridge.

 moving=[a for a in parts if a['moving'] and a['role']!='clearance' and a['group'] not in ('fasteners','board_alternatives')]
 fixed=[a for a in parts if not a['moving'] and a['role']!='clearance' and a['group'] not in ('lid','lid_screws','lid_guides','rear_vent','hold_downs','rear_release','fasteners','power','mcio','io_shield')]
 motion=[]
 for dz in (0,5,25,90,190,360):
  hits=[]
  for a in moving:
   s=a['shape'].translate((0,0,dz))
   for b in fixed:
    if overlap(s,b['shape'])>1e-4:hits.append([a['name'],b['name']])
  motion.append(dict(lift_mm=dz,intersections=hits))
 # Individual cards rise vertically after the lid, rear cover, bracket screws and power plugs are removed.
 card_motion=[]
 for dz in (1,10,50,125,170):
  hits=[]
  for a in parts:
   if a['group'] not in ('gpus','aux_card','brackets'):continue
   s=a['shape'].translate((0,0,dz))
   for b in parts:
    if b['group'] in ('shell','cassette','strain_relief','guides','partition') and overlap(s,b['shape'])>1e-4:hits.append([a['name'],b['name']])
  card_motion.append(dict(lift_mm=dz,intersections=hits))
 retimer_motion=[]
 for dy,dz in ((0,5),(-12,5),(-12,30),(-12,160)):
  hits=[]
  for a in parts:
   if a['group']!='retimers':continue
   for b in fixed:
    if b['role']=='fabricated' and b['group'] in ('shell','guides','strain_relief','rear_vent') and overlap(a['shape'].translate((0,dy,dz)),b['shape'])>1e-4:hits.append([a['name'],b['name']])
  retimer_motion.append(dict(forward_mm=-dy,lift_mm=dz,intersections=hits))
 component_route_hits=[]
 for i,a in enumerate(mcio_shapes,1):
  for b in parts:
   if b['group'] in ('hoses','aio','gpus','aux_card','psu','power','motherboard','cpu') and overlap(physical(a),b['shape'])>1e-4:component_route_hits.append([f'MCIO_route_{i}',b['name']])
 psu_envelope=physical(box(6,R-175,10,86,175,150))
 psu_hits=[a['name'] for a in parts if a['group'] in ('hoses','motherboard','retimers','power','mcio','cpu') and overlap(psu_envelope,a['shape'])>1e-4]
 assert not psu_hits,('PSU occupancy conflicts',psu_hits)
 hardware_hits=[]
 for a in parts:
  if a['group'] not in ('gpus','aux_card','retimers','lower_blank','power','mcio','hoses','external_route'):continue
  for b in parts:
   if b['role']=='fabricated' and b['group'] in ('shell','cassette','guides','partition','strain_relief','rear_vent'):
    if overlap(a['shape'],b['shape'])>1e-4:hardware_hits.append([a['name'],b['name']])
 intake_hits=[]
 for a in parts:
  if a['group'] not in ('fans','intake_grilles','intake_spacers','intake_fasteners'):continue
  for b in parts:
   if a is b or b['role']=='clearance' or b['group'] in ('board_alternatives','io_shield'):continue
   plastic_joint=('_self_tapping_5x8_screw_' in a['name'] and b['group']=='fans') or ('_self_tapping_5x8_screw_' in b['name'] and a['group']=='fans')
   plastic_joint|=a.get('thread_host')==b['name'] or b.get('thread_host')==a['name']
   if not plastic_joint and overlap(a['shape'],b['shape'])>1e-4:intake_hits.append([a['name'],b['name']])
 assert not intake_hits,('Intake component interference',intake_hits)
 checks=dict(PSU_model='ASUS-PRO-WS-3000P',PSU_size_depth_width_height_mm=[175,150,86],PSU_rear_mount_holes_construction_xz_mm=atx,PSU_handedness='Rear-view counterclockwise quarter-turn of the standard ATX pattern',backplane_socket_count=12,backplane_GPU_socket_pitch_mm=40.64,backplane_auxiliary_end_slot_gap_mm=20.32,backplane_PCB_origin_construction_xy_mm=[BOARD_X,BOARD_Y],backplane_dimensions_mm=[429,225,2.5],backplane_mounting_holes_photo_estimates=True,motherboard_standoff_type="M3 x 8 mm male-female hex standoff, 6 mm stud",motherboard_stud_thread_engagement_mm=3.5,motherboard_upper_screw_engagement_mm=2.93,motherboard_stud_tip_to_floor_mm=0.5,backplane_supported_holes_construction_xy_mm=BOARD_MOUNT_POINTS,cartridge_removal_requires=['lid (four captive thumbscrews)','upper rear vent and its fasteners','tray hold-down screws','disconnected harnesses'],enclosure_mm=[482.6,P['depth'],H],body_width_mm=W,rack_units=9,upper_rear_positions=P['upper_slot_count'],dual_slot_GPU_envelopes=10,single_width_auxiliary_card_envelopes=1,backplane_trailing_auxiliary_socket='Shares the last rear position with the tenth GPU second bracket; usable only without that GPU',lower_rear_positions=8,
  lid_to_panel_fastener_intersections=lid_hits,lid_removal_intersections=lid_removal,intake_component_intersections=intake_hits,gpu_deck_z_mm=170,upper_fan_centres_z_mm=[210,330],upper_fan_count=6,upper_inlet_spacer_mm=0,grille_to_GPU_fan_face_mm=2,front_intake_aperture_mm=116,grille_perforation_diameter_mm=9,grille_perforation_pitch_mm=10,slot_pitch_mm=20.32,dual_slot_pitch_mm=40.64,upper_bracket_centres_x_mm=[W-x for x in slots],lower_card_planes_x_mm=[W-x for x in host_axes],
  upper_retention_screws_x_mm=[W-x+9.21 for x in slots],lower_retention_screws_x_mm=[W-x+9.21 for x in host_centres],
  lower_bracket_centres_x_mm=[W-x for x in host_centres],upper_card_planes_x_mm=[W-x for x in gpu_axes],
  bracket_screw_offset_from_centre_mm=9.21,bracket_screw_offset_from_PCB_centre_mm=2.055,
  bracket_screw_y_mm=R+5.08-F,upper_bracket_retention='#6-32 UNC-2B threads tapped in extruded collars of the integral 1.2 mm shelf; no nuts',upper_bracket_tap_drill_mm=2.705,lower_bracket_retention='#6-32 UNC-2B threads tapped in extruded collars of the separate 1.5 mm strip; no nuts',lower_bracket_tap_drill_mm=2.705,
  fan_mount_slot_mm=[9,5.5],shared_fan_mount_slot_mm=[24,5.5],AIO_fan_mount_slot_mm=[9,4.8],AIO_shared_fan_mount_slot_mm=[24,4.8],chassis_fan_screw="5 x 8 mm self-tapping plastic fan screw",GPU_fan_screw_penetration_mm=6,rear_fan_screw_penetration_mm=6.8,fan_frame_pitch_mm=120,adjacent_fan_screw_gap_mm=15,vent_hole_diameter_mm=9,front_vent_pitch_mm=10,
  rear_upper_vent_bounds_xz_mm=[1.5,303.07,437,H-1.5-303.07],rear_upper_vent_hole_count=len(vh)-2,rear_cover_side_screw_count=4,rear_cover_screw_heights_mm=[313,381.45],
  motherboard_CPU_centre_x_mm=W-cpu_x,rear_view_order='PSU, CPU and I/O, PCIe bank (left to right)',

  motherboard_standoff_mm=8,motherboard_PCB_bottom_z_mm=16,motherboard_PCB_top_z_mm=17.57,
  IO_aperture_mm=[158.75,44.45],IO_aperture_origin_xz_mm=[W-io_x-158.75,io_z],rear_IO_sheet_mm=1.2,IO_outer_face_to_board_datum_mm=R-board_datum_y,ATX_IO_depth_nominal_mm=12.2682,ATX_IO_depth_tolerance_mm=.254,
  lower_card_datum_W_mm=host_w,lower_bracket_bearing_z_mm=host_bearing,upper_card_datum_W_mm=gw,upper_bracket_bearing_z_mm=gb,
  upper_fan_hole_pitch_mm=105,lower_80mm_fan_hole_pitch_mm=71.5,AIO_fan_hole_pitch_mm=105,
  motherboard_nominal_holes=[dict(name=n,x=W-x,y=y-F) for n,x,y in mh],motherboard_front_y_mm=board_front-F,
  power_connector_location='GPU forward end',power_connector_envelope_mm=[20,22,12],power_straight_after_plug_mm=35,
  MCIO_edge_bank_centres_x_mm=[W-x for x in mcio_front_x],MCIO_additional_photo_locations_xy_mm=[[W-x,y-F] for x,y in photo_extra],MCIO_to_component_intersections=component_route_hits,external_MCIO_clear_aperture_mm=[139,25],MCIO_test_plug_cross_section_mm=[35,14],
  AIO_model="XE360-TR5",AIO_radiator_mm=[394,120,28],AIO_fan_depth_mm=38,AIO_stack_depth_mm=66,AIO_stack_rear_y_mm=69.5,AIO_to_motherboard_front_clearance_mm=board_front-F-69.5,upper_fan_depth_mm=38,hose_route_lengths_mm=lengths,hose_available_nominal_mm=460,hose_top_z_mm=max(h.BoundingBox().zmax for h in hose_shapes),
  cassette_motion=motion,individual_GPU_motion=card_motion,lower_retimer_motion=retimer_motion,routing_structure_intersections=hardware_hits,valid_shapes=len(parts),
  limits=['Reference board, retimer and GPU connector coordinates require supplier CAD.',
  'I/O carrier depth is within the ATX nominal tolerance; integrated shield compression still requires the physical motherboard.',
  'Hose routes are occupancy references; unused length, fittings and minimum bend radius require cooler CAD.',
  'ASUS 3000P has four native GPU 16-pin cables and four 8-pin GPU cables; ten GPU routes are service envelopes, not a qualified wiring plan.',
  'Miwin photo reconstruction: standard socket pitch is assumed; undimensioned coordinates require supplier verification.',
  'Miwin lists four x16 slots per switch. Photo labels suggest the two end double-width positions and both single-width sockets connect to host or NIC connectors instead; confirm slot wiring with the supplier.',
  'Bends are formed with inside radius equal to sheet thickness and developed with K-factor 0.40; confirm both with the fabricator before cutting blanks.'])
 (out/'validation.json').write_text(json.dumps(checks,indent=2))
 print(json.dumps(checks,indent=2),flush=True)
 assert not any(v['intersections'] for v in motion), 'Cassette motion intersects fixed structure'
 assert not any(v['intersections'] for v in card_motion), ('GPU extraction intersects structure',[v for v in card_motion if v['intersections']])
 assert not hardware_hits,'Cable or card intersects fabricated structure'
 assert not component_route_hits,'MCIO route intersects cooling or GPU envelope'
 assert not any(v['intersections'] for v in retimer_motion),'Retimer service path intersects structure'
 assert overlap(hose_shapes[0],hose_shapes[1])<1e-4,'AIO hose envelopes intersect'
 assert all(v<=460.001 for v in lengths),'Hose too short'
 asm=cq.Assembly(name='Nine_unit_WRX90_GPU_chassis');cass=cq.Assembly(name='Removable_GPU_cassette');meshes=[]
 for a in parts:
  rgb=[int(a['color'][i:i+2],16)/255 for i in (1,3,5)]
  if a['role']!='clearance' and a['group'] not in ('board_alternatives','io_shield') and not gpu_geometry.cable_route(a):asm.add(a['shape'],name=a['name'],color=cq.Color(*rgb))
  if a['moving'] and a['role']!='clearance' and a['group']!='board_alternatives':cass.add(a['shape'],name=a['name'],color=cq.Color(*rgb))
  if a['role']=='fabricated' and a['group'] in ('shell','cassette','lid','rear_vent','guides','partition','strain_relief','mounts','motherboard_mounts','psu_support','fans','intake_grilles') and not any(v in a['name'] for v in ('nut','screw','standoff','washer','M3','M4')):
   cq.exporters.export(a['shape'],str(out/'formed_parts'/(a['name']+'.step')))
  vs,fs=a['shape'].tessellate(.7,.25)
  meshes.append({k:a[k] for k in ('name','group','color','role','visible','moving')}|dict(vertices=[[round(v.x,4),round(v.y,4),round(v.z,4)] for v in vs],faces=fs))
 for component,group in [('asus_pro_ws_3000p_reference','psu'),('miwin_switch_backplane_reference','backplane')]:
  component_asm=cq.Assembly(name=component)
  for a in parts:
   if a['group']==group:component_asm.add(a['shape'],name=a['name'])
  component_asm.export(str(out/(component+'.step')))
 fan_asm=cq.Assembly(name='Upper_fan_modules')
 for a in parts:
  if a['group']=='fans':fan_asm.add(a['shape'],name=a['name'])
 fan_asm.export(str(out/f'upper_{fan_size}mm_fan_modules.step'))
 asm.export(str(out/'double_deck_assembly.step'));cass.export(str(out/'removable_gpu_cassette.step'));gpu_geometry.neutral_headers(out)
 (out/'model_meshes.json').write_text(json.dumps(dict(parts=meshes,parameters=P,cable_paths=[]),separators=(',',':')))
 (out/'parameters.json').write_text(json.dumps(P,indent=2))
 (out/'parts.csv').write_text('name,group,role,moves_with_cassette\n'+'\n'.join(f"{a['name']},{a['group']},{a['role']},{a['moving']}" for a in parts)+'\n')
 for route in paths:route['points']=[[W-x,y-F,z] for x,y,z in route['points']]
 (out/'cable_routes.json').write_text(json.dumps(paths,indent=2))
 if return_parts:return parts,checks
 return checks
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--work-dir',required=True);ap.add_argument('--fan-size',type=int,choices=[120],default=120);a=ap.parse_args();build(a.out,a.work_dir,a.fan_size)

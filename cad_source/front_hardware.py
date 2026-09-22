"""Screw-mounted folded rack ears and a continuous perforated intake face."""
from mounting_hardware import box,cyl,union,screw,nut
import math

def ear_holes(y0,zlevels):
 return [cyl(-5,y0+y,z,2.25,450,(1,0,0)) for y in (32,55) for z in zlevels]

def add_ears(add,y0,z0,height,zlevels,units):
 for side in ('left','right'):
  left=side=='left';x=-3 if left else 440;face_x=-21.3 if left else 440
  ear=union([box(face_x,y0-3,z0,21.3,3,height),box(x,y0,z0,3,64,height)])
  holes=ear_holes(y0,zlevels)
  panel_levels=(22,148,205,290,381.45) if units==9 else (242,320,388)
  holes += [cyl(-5,y0+12,z,3.3,450,(1,0,0)) for z in panel_levels]
  if units==9:holes.append(cyl(-5,y0+65,z0+height-10,3.3,450,(1,0,0)))
  for i in range(units):holes.append(cyl(-12.55 if left else 452.55,y0-4,z0+21.825+44.45*i,3.5,5,(0,1,0)))
  add('Screw_mounted_3mm_rack_ear_'+side,ear.cut(__import__('cadquery').Compound.makeCompound(holes)),'rack_ears','#526776')
  axis=(1,0,0) if left else (-1,0,0)
  for y in (32,55):
   for z in zlevels:
    point=(-3 if left else 443,y0+y,z)
    add(f'Rack_ear_{side}_M4x10_side_screw_{y}_{z}',screw(point,axis,'M4',10),'fasteners','#304553')
    add(f'Rack_ear_{side}_captive_M4_nut_{y}_{z}',nut((1.5 if left else 438.5,y0+y,z),axis,'M4'),'fasteners','#b39451')

def grille_holes(y,z0,height,fan_axes,fixes,entry=None):
 holes=[]
 for row in range(int(height/8.660254)+1):
  z=z0+12+row*8.660254
  if z>z0+height-9:continue
  for col in range(42):
   x=15+10*col+(row%2)*5
   if x>425:continue
   if any(math.hypot(x-a,z-b)<11 for a,b in fan_axes+fixes):continue
   if entry and entry[0]-5<x<entry[2]+5 and entry[1]-5<z<entry[3]+5:continue
   holes.append(cyl(x,y-1,z,4.5,4,(0,1,0)))
 return holes

"""Hardware references based on published envelopes and manufacturer photographs.
Photo-derived feature sizes are explicit modeling estimates, not production drawings.
"""
import cadquery as cq
from mounting_hardware import box,cyl,union,cut,screw,slot
from sheetmetal import fold
ATX_REAR_HOLES=[(6,80),(144,80),(120,6),(6,16)]
PSU_DEPTH=175.
BOARD_X=2.5
BOARD_Y=165.5
# Underside photograph: twelve obround mounting holes and three round holes.
# The selected six supports avoid sockets and rail-end bolts; coordinates remain photo estimates.
BOARD_MOUNT_POINTS=[(83.,171.8),(347.4,171.8),(164.5,265.3),(291.5,265.3),(164.5,381.),(291.5,381.)]
BOARD_OBROUND_HOLES=[(x,y) for y in (265.3,381.) for x in (27.6,164.5,291.5,419.5)]+[(150.4,321.3),(291.5,321.3),(83.,171.8),(347.4,171.8)]
BOARD_ROUND_HOLES=[(27.6,321.3),(374.,321.3),(206.8,171.8)]
def board_hole_tools(z,depth):
    return [slot(x,y-3.25,z,6.5,3.4,depth,'y') for x,y in BOARD_OBROUND_HOLES]+[cyl(x,y,z,1.7,depth) for x,y in BOARD_ROUND_HOLES]

BOARD_SLOT_X=[11.3,31.62,72.26,112.90,153.54,194.18,234.82,275.46,316.10,356.74,397.38,417.70]

def psu_holes():
    # After the chassis export transform, this is a proper counterclockwise rear-view rotation.
    return [(92-v,10+u) for u,v in ATX_REAR_HOLES]

def psu_vent(rear):
    return cq.Workplane().add(box(-1,rear-157.5,15,5,140,140)).edges('|X').fillet(8).val()

def add_psu(add, rear):
    # Canonical coordinates: X = right in the rear photograph, Y = depth into the PSU,
    # Z = up in the rear photograph. Combined with export, the transform is a rigid rotation.
    def place(s):return s.rotate((0,0,0),(0,1,0),-90).mirror('XZ').translate((92,rear,10))
    def ref(name,s,color='#303a41'):return add(name,place(s),'psu',color,'reference')
    shell=box(0,0,0,150,175,86).cut(box(1,1,1,148,173,84))
    holes=[cyl(u,-1,v,1.7526,7,(0,1,0)) for u,v in ATX_REAR_HOLES]
    # Broad-face grille location and fan diameter are scaled from the product image.
    holes.append(box(7,19,84.5,136,136,3))
    for u in range(5,94,4):
        for v in range(5,70,4):
            if all((u+1.35-hu)**2+(v+1.35-hv)**2>25 for hu,hv in ATX_REAR_HOLES):holes.append(box(u,-1,v,2.7,3,2.7))
    for u in range(97,145,4):
        for v in (63,67):holes.append(box(u,-1,v,2.7,3,2.7))
    holes += [box(102,-1,26,36,3,28),box(105,-1,12,30,3,12)]
    # Recessed modular sockets, as seen looking at the PSU cable face.
    connectors=[('MB_10pin',24,63,22,10,5,2),('MB_18pin',57,63,40,10,9,2)]
    connectors += [(f'Peripheral_6pin_{i+1}',x,v,14,10,3,2) for i,(x,v) in enumerate([(92,63),(112,63),(132,63),(139,42),(139,22)])]
    connectors += [(f'Native_12V_2x6_{i+1}',x,v,20,10,6,2) for i,(x,v) in enumerate([(23,42),(47,42),(23,22),(47,22)])]
    connectors += [(f'CPU_PCIe_8pin_{i+1}',x,v,19,11,4,2) for i,(x,v) in enumerate([(72,42),(95,42),(119,42),(72,22),(95,22),(119,22)])]
    for name,screen_x,v,w,h,cols,rows in connectors:
        u=150-screen_x
        holes.append(box(u-w/2,173.5,v-h/2,w,3,h))
        housing=box(u-w/2,169,v-h/2,w,6,h)
        apertures=[box(u-w/2+2+c*(w-4)/cols,171,v-h/2+1+r*(h-2)/rows,(w-4)/cols-1,5,(h-2)/rows-1) for c in range(cols) for r in range(rows)]
        ref('ASUS_3000P_'+name+'_photo_position',housing.cut(cq.Compound.makeCompound(apertures)),'#19242c')
    ref('ASUS_3000P_175x150x86_shell',shell.cut(cq.Compound.makeCompound(holes)))
    bars=[box(7,y,85,136,3,1) for y in range(20,154,12)]
    bars += [box(u,19,85,2,136,1) for u in (48,100)]
    ref('ASUS_3000P_fan_grille_photo_reference',cq.Compound.makeCompound(bars),'#4b555c')
    hub=cyl(75,87.5,78,18,5)
    blades=[]
    for i in range(9):
        blade=cq.Workplane('XY').polyline([(89,87.5),(130,69),(139,80),(97,100)]).close().extrude(2).translate((0,0,79)).val().rotate((75,87.5,0),(75,87.5,1),i*40)
        blades.append(blade)
    ref('ASUS_3000P_135mm_fan_photo_estimate',union([hub]+blades),'#626c74')
    socket=box(102,-.6,26,36,10.6,28).cut(box(105,-1,29,30,8,22))
    ref('ASUS_3000P_AC_inlet_photo_reference',socket,'#111c24')
    ref('ASUS_3000P_AC_contact_references',cq.Compound.makeCompound([box(u,1,v,3,4,1) for u,v in [(111,43),(128,43),(119.5,34)]]),'#baa77a')
    ref('ASUS_3000P_power_switch_photo_reference',box(105,-.6,12,30,1.6,12),'#172129')
    # Recessed thread cylinders make the nominal standard mount visible on the PSU itself.
    for i,(u,v) in enumerate(ATX_REAR_HOLES):
        ref(f'ASUS_3000P_ATX_thread_boss_{i+1}',cyl(u,1,v,3.5,5,(0,1,0)).cut(cyl(u,0,v,1.7526,7,(0,1,0))))
    cradle=union([box(1.5,rear-175,8.5,94,175,1.5),box(1.5,rear-175,10,1.5,175,10),box(94,rear-175,10,1.5,175,12)])
    mounts=(rear-165,rear-10)
    bends=[]
    cradle=fold(cradle,bends,'y',(1.5,8.5),(1,1),1.5);cradle=fold(cradle,bends,'y',(95.5,8.5),(-1,1),1.5)
    cradle=cradle.cut(cq.Compound.makeCompound([cyl(0,y,16.5,1.7,5,(1,0,0)) for y in mounts]))
    add('ASUS_3000P_folded_175mm_cradle',cradle,'psu_support',pieces=[dict(name='ASUS_3000P_folded_175mm_cradle',shape=cradle,t=1.5,bends=bends)])
    for i,(x,z) in enumerate(psu_holes(),1):
        add(f'ATX_6_32xquarter_inch_screw_{i}',screw((x,rear+1.2,z),(0,-1,0),'6-32',6.35),'fasteners','#304553')
    return mounts

def backplane_outline():
    x,y=BOARD_X,BOARD_Y
    return [(x+62,y),(x+364,y),(x+364,y+76),(x+429,y+76),(x+429,y+225),(x,y+225),(x,y+76),(x+62,y+76)]

def add_board_details(add, bz):
    for i,x in enumerate((91,244),1):
        y=187.5
        sink=union([box(x,y,bz,91,68,2)]+[box(x+j*4,y,bz+2,1.5,68,8) for j in range(23)])
        add(f'Miwin_switch_{i}_heatsink_photo_reference',sink,'backplane','#304553','reference',moving=True)
    # Ten additional MCIO sockets supplement the eight routed connectors along the forward edge.
    extra=[(18,248),(45,248),(389,248),(416,248),(218,215),(218,253),(54,305.7),(54,362.2),(379.56,305.7),(379.56,362.2)]
    for i,(x,y) in enumerate(extra,1):
        w,d=24,10
        housing=box(x-w/2,y-d/2,bz,w,d,8).cut(box(x-w/2+1,y-d/2+1,bz+2,w-2,d-2,7))
        add(f'Miwin_MCIO_additional_{i}_photo_reference',housing,'backplane','#606c75','reference',moving=True)
    for i,(x,y) in enumerate([(73,190),(73,224),(352,190),(352,224)],1):
        socket=box(x-7,y,bz,14,18,10).cut(box(x-5,y+2,bz+2,10,14,9))
        add(f'Miwin_auxiliary_8pin_power_{i}_photo_reference',socket,'backplane','#d7d6c4','reference',moving=True)
    for i,(x,y) in enumerate([(88,273),(115,273),(309,273),(337,273),(362,273)],1):
        add(f'Miwin_4pin_fan_header_{i}_photo_reference',box(x,y,bz,9,5,7),'backplane','#d7d6c4','reference',moving=True)
    for i,x in enumerate((206,225),1):add(f'Miwin_IPMB_header_{i}_photo_reference',box(x,177,bz,9,5,7),'backplane','#d7d6c4','reference',moving=True)
    return extra

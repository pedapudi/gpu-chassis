"""Adjustable PCB support and serviceable cable-entry hardware; all lengths in mm."""
import cadquery as cq
import math
V=cq.Vector

def box(x,y,z,w,d,h):return cq.Solid.makeBox(w,d,h,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,V(x,y,z),V(*axis))
def union(shapes):return shapes[0].fuse(*shapes[1:]) if len(shapes)>1 else shapes[0]
def cut(s,shapes):return s.cut(union(shapes)) if shapes else s

def hex_prism(x,y,z,af,h):
    r=af/math.sqrt(3)
    return cq.Workplane('XY').polygon(6,2*r).extrude(h).translate((x,y,z)).val()

def orient(shape,point,axis):
    rotations={(1,0,0):((0,1,0),90),(-1,0,0):((0,1,0),-90),(0,1,0):((1,0,0),-90),(0,-1,0):((1,0,0),90),(0,0,-1):((1,0,0),180)}
    if axis!=(0,0,1):
        vector,angle=rotations[axis];shape=shape.rotate((0,0,0),vector,angle)
    return shape.translate(point)

def screw(point,axis,thread,length):
    # Nominal major-diameter and head envelopes; helical threads and drive recesses are omitted.
    d,head_d,head_h={'M3':(3,5.6,2.4),'M4':(4,8,3.1),'6-32':(3.5052,6.35,2.6)}[thread]
    shape=union([cyl(0,0,0,d/2,length),cyl(0,0,-head_h,head_d/2,head_h)])
    return orient(shape,point,axis)

def fan_screw(point,axis,length=8):
    """Nominal 5 x 8 mm plastic-thread-forming fan screw; thread envelope only.

    The 5 mm major diameter intentionally overlaps the plastic pilot bore.
    A 2 mm panel leaves 6 mm penetration including the tapered lead.
    Actual fan-supplied screw geometry and permitted penetration control fit.
    """
    head=cyl(0,0,-2.5,4.25,2.5)
    recess=union([box(-2,-.55,-2.6,4,1.1,1.1),box(-.55,-2,-2.6,1.1,4,1.1)])
    shank=cyl(0,0,0,2.5,length-1.5)
    tip=cq.Solid.makeCone(2.5,1.5,1.5,V(0,0,length-1.5))
    return orient(union([head.cut(recess),shank,tip]),point,axis)

def nut(point,axis,thread):
    af,h,bore={'M3':(5.5,2.4,1.5),'M4':(7,3.2,2),'6-32':(7.9375,2.778,1.7526)}[thread]
    shape=hex_prism(0,0,0,af,h).cut(cyl(0,0,-1,bore,h+2))
    return orient(shape,point,axis)

def slot(x,y,z,length,width,height,axis='x'):
    assert length>=width
    r=width/2
    if axis=='x':return union([box(x+r,y-r,z,length-width,width,height),cyl(x+r,y,z,r,height),cyl(x+length-r,y,z,r,height)])
    return union([box(x-r,y+r,z,width,length-width,height),cyl(x,y+r,z,r,height),cyl(x,y+length-r,z,r,height)])

def supports(add,rows,points,board_z=18,female=False):
    """Crossbars translate in Y; captive M3 standoffs translate in X along each crossbar."""
    assert all(166.25<=y<=395.75 for y in rows)
    assert all(32<=x<=408 and y in rows for x,y in points)
    assert abs(board_z-18)<1e-8, "Catalog 8 mm standoff requires a PCB underside at Z=18"
    for x in (20,420):
        rail=box(x-8,150,6,16,260,2)
        rail=cut(rail,[slot(x,164,5,234,4.5,4,'y'),cyl(x,155,5,2.25,4),cyl(x,405,5,2.25,4)])
        for y in (155,405):
            foot=union([box(x-8,y-5,4.5,16,10,1.5),box(x-8,y-5,1.5,1.5,10,3),box(x+6.5,y-5,1.5,1.5,10,3)]).cut(cyl(x,y,1,2.25,6))
            add(f'Rail_welded_sheet_bridge_{x}_{y}',foot,'mounts','#9aaeba')
            add(f'Rail_bridge_captive_DIN562_M4_nut_{x}_{y}',box(x-3.5,y-3.5,2.3,7,7,2.2).cut(cyl(x,y,2,2,3)),'fasteners','#b39a61')
            add(f'Rail_M4x6_screw_{x}_{y}',screw((x,y,8),(0,0,-1),'M4',6),'fasteners','#647783')
        add(f'Longitudinal_mount_rail_{x}',rail,'mounts','#9aaeba')
        # Two welded sheet strips restrain standard square nuts while allowing Y adjustment.
        for sx in (x-4.8,x+3.6):
            add(f'Rail_square_nut_guide_strip_{x}_{sx}',box(sx,166,2.2,1.2,228,3.8),'mounts','#9aaeba')
    for y in rows:
        cross=box(12,y-7,8,416,14,2)
        cross=cut(cross,[slot(29,y,7,382,3.5,4),cyl(20,y,7,2.25,4),cyl(420,y,7,2.25,4)])
        add(f'Sliding_crossbar_Y_{y}',cross,'mounts','#bcc8cd')
        for x in (20,420):
            add(f'Crossbar_DIN562_M4_square_nut_{x}_{y}',box(x-3.5,y-3.5,3.8,7,7,2.2).cut(cyl(x,y,3,2,4)),'fasteners','#b39a61')
            add(f'Crossbar_M4x8_screw_{x}_{y}',screw((x,y,10),(0,0,-1),'M4',8),'fasteners','#647783')
    for i,(x,y) in enumerate(points,1):
        if female:
            # Two M3x6 screws engage an 8 mm through-threaded spacer without meeting.
            post=hex_prism(x,y,10,5,8).cut(cyl(x,y,9,1.5,10))
            add(f'M3_8mm_female_female_standoff_{i}',post,'standoffs','#b39a61')
            washer=cyl(x,y,7.5,3.5,.5).cut(cyl(x,y,7,1.6,2))
            add(f'Standoff_lower_M3_washer_{i}',washer,'fasteners','#647783')
            add(f'Standoff_lower_M3x6_screw_{i}',screw((x,y,7.5),(0,0,1),'M3',6),'fasteners','#647783')
            continue
        # Catalog 8 mm M3 male/female hex standoff, with 6 mm stud and 5.5 mm female engagement.
        add(f'Standoff_M3_hex_nut_{i}',nut((x,y,8),(0,0,-1),'M3'),'fasteners','#b39a61')
        post=hex_prism(x,y,10,5,8).cut(cyl(x,y,12.5,1.25,6.5))
        stud=cyl(x,y,4,1.5,6.1)
        add(f'M3_8mm_hex_standoff_6mm_stud_{i}',union([post,stud]),'standoffs','#b39a61')

def cable_entry(add,rear,z0,opening_h=32):
    """Large openings admit plugs. Removable brush cassettes close around cables afterward."""
    assert opening_h>=20
    windows=[(116,140),(280,140)]
    cutters=[]
    for x,w in windows:
        cutters.append(box(x,rear-1,z0,w,5,opening_h))
        # A four-sided cassette frame is clear across the full connector opening.
        frame=box(x-5,rear+1.5,z0-5,w+10,1.5,opening_h+10)
        frame=frame.cut(box(x,rear+.5,z0,w,4,opening_h))
        screw_pts=[(x-2.5,z0-2.5),(x+w+2.5,z0-2.5),(x-2.5,z0+opening_h+2.5),(x+w+2.5,z0+opening_h+2.5)]
        for sx,sz in screw_pts:
            tool=cyl(sx,rear-1,sz,1.6,6,(0,1,0));frame=frame.cut(tool);cutters.append(tool)
            add(f'Cable_frame_M3x6_screw_{sx}_{sz}',screw((sx,rear+3,sz),(0,-1,0),'M3',6),'fasteners','#647783')
            add(f'Cable_frame_M3_nut_{sx}_{sz}',nut((sx,rear,sz),(0,-1,0),'M3'),'fasteners','#b39a61')
        add(f'MCIO_removable_brush_frame_{x}',frame,'entry','#354d5c')
        mid=z0+opening_h/2
        add(f'MCIO_upper_brush_strip_{x}',box(x,rear+1.7,mid+1,w,1,opening_h/2-1),'seals','#303c42','reference')
        add(f'MCIO_lower_brush_strip_{x}',box(x,rear+1.7,z0,w,1,opening_h/2-1),'seals','#303c42','reference')
        # Connector envelope represents the accepted service aperture, not a selected cable part.
        add(f'MCIO_plug_service_envelope_{x}',box(x+50,rear-12,z0+(opening_h-14)/2,35,35,14),'plug_check','#d7a357','clearance',False)
    # Rear-attached L brackets support the tie bar. The bar touches the brackets at both ends.
    bar_z=z0-3
    for x in (105,426):
        bracket=union([box(x,rear-34,bar_z-1.5,8,34,1.5),box(x,rear-1.5,bar_z,8,1.5,16)])
        bracket=cut(bracket,[cyl(x+4,rear-28,bar_z-2,1.7,4),cyl(x+4,rear-3,bar_z+10,1.7,5,(0,1,0))])
        add(f'Tie_bar_rear_attachment_{x}',bracket,'strain_relief','#aebbc6')
        cutters.append(cyl(x+4,rear-1,bar_z+10,1.7,5,(0,1,0)))
        add(f'Tie_bracket_M3x6_screw_{x}',screw((x+4,rear+1.5,bar_z+10),(0,-1,0),'M3',6),'fasteners','#647783')
        add(f'Tie_bracket_M3_nut_{x}',nut((x+4,rear-1.5,bar_z+10),(0,-1,0),'M3'),'fasteners','#b39a61')
        add(f'Tie_bar_M3x6_screw_{x}',screw((x+4,rear-28,bar_z+1.5),(0,0,-1),'M3',6),'fasteners','#647783')
        add(f'Tie_bar_M3_nut_{x}',nut((x+4,rear-28,bar_z-1.5),(0,0,-1),'M3'),'fasteners','#b39a61')
    bar=box(105,rear-34,bar_z,329,12,1.5)
    bar=cut(bar,[box(x,rear-32,bar_z-1,3,8,4) for x in range(122,415,18)]+[cyl(x,rear-28,bar_z-1,1.7,4) for x in (109,430)])
    add('Bolted_MCIO_strain_relief_bar',bar,'strain_relief','#aebbc6')
    return cutters

def pem_632(x,y,z):
    """S-632-1 nominal envelope, fitted from below a 1.5 mm retention flange."""
    # Catalog nominal E=7.112, T=1.778, C=4.7498, A=.9652; hole=4.7625.
    body=union([cyl(x,y,z-1.778,3.556,1.778),cyl(x,y,z,2.3749,.9652)])
    return body.cut(cyl(x,y,z-2,1.7526,4))

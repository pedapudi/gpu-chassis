"""Local CAD sections identify clearance and installed-height measurements."""
import cadquery as cq
from section_drawings import bounds,section_at,fmt
from annotated_geometry import edge_points,polyline,dim,mark

def section_view(c,shapes,axis,station,limits,rect):
    b=limits
    clip=cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))
    sec=section_at(cq.Compound.makeCompound(shapes).intersect(clip),axis,station)
    assert sec.Edges(),(axis,station)
    uv=[i for i in range(3) if i!=axis];x,y,w,h=rect
    lo=[b[i] for i in uv];hi=[b[i+3] for i in uv];s=min(w/(hi[0]-lo[0]),h/(hi[1]-lo[1]))
    ox=x+(w-(hi[0]-lo[0])*s)/2;oy=y+(h-(hi[1]-lo[1])*s)/2
    def p(u,v):return ox+(u-lo[0])*s,oy+(v-lo[1])*s
    c.setLineWidth(.7)
    for e in sec.Edges():polyline(c,[p(*[q.toTuple()[i] for i in uv]) for q in edge_points(e)])
    return p

def clearance_details(parts,mod,api):
    c,new,para,table,view,W,H,out=api;lookup={a['name']:a['shape'] for a in parts}
    gpu1=lookup['GPU_1_Max_Q_envelope'];gpu2=lookup['GPU_2_Max_Q_envelope'];b1=bounds(gpu1);b2=bounds(gpu2)
    assert abs(b1[0]-b2[3]-.64)<1e-5
    new('GPU clearance | adjacent card envelopes','Assembly')
    para('Local CAD section through the two adjacent reference cards at Y300. Cut boundaries are cropped. This is the nominal envelope gap; card width tolerance, straightness and cooler protrusions remain supplier checks.',32,H-82,W-64,11)
    z=b1[2]+60
    p=section_view(c,[gpu1,gpu2],1,300,[b2[3]-12,299,z-12,b1[0]+12,301,z+12],(90,270,540,360))
    dim(c,p(b2[3],z),p(b1[0],z),'0.640 nominal gap',offset=210)
    mark(c,p(b2[3]-6,z+6),'GPU 2 envelope',(720,570));mark(c,p(b1[0]+6,z+6),'GPU 1 envelope',(720,510))
    para('40.640 populated socket pitch minus 40.000 card width = 0.640. Each dual-slot card occupies two rear positions at 20.320 pitch.',720,430,400,12)
    if not mod:
        psu=lookup['ASUS_3000P_175x150x86_shell'];screw=lookup['Side_ledge_M3x6_1.5_390'];pb=bounds(psu);sb=bounds(screw);gap=sb[0]-pb[3]
        assert abs(gap-.5)<1e-4
        new('PSU clearance | bearing screw tip section','Assembly')
        para('Local CAD section normal Y at Y443.2. The bearing screw is shown at its installed length. The PSU casing and screw tip have a nominal 0.500 gap; validate tolerances before fabrication.',32,H-82,W-64,11)
        p=section_view(c,[psu,screw],1,443.2,[430,442,153,444,445,161],(95,250,530,380))
        dim(c,p(pb[3],158),p(sb[0],158),'0.500 nominal gap',offset=220)
        mark(c,p(432,157),'PSU casing',(720,570));mark(c,p(438,158),'M3 × 6 bearing screw',(720,510))
        para('The dimension measures the gap along X. Nominal PSU envelope X348–434. Screw tip X434.5. Select screw length and washer stack from the installed joint.',720,430,400,12)
        fan=next(a['shape'] for a in parts if a['group']=='exhaust');io=lookup['Flat_1p2mm_IO_carrier_with_clear_shield_lands']
        fb=bounds(fan);ib=bounds(io);assert abs(fb[2]-ib[5]-2)<1e-4
        new('Lower rear clearance | exhaust fan and I/O carrier','Assembly')
        para('The fan frame starts at Z70; the separate I/O carrier ends at Z68. The local CAD section shows their 2.000 vertical separation. Cut boundaries are cropped.',32,H-82,W-64,11)
        x=(fb[0]+fb[3])/2
        p=section_view(c,[fan,io],0,x,[x-1,460,62,x+1,472,77],(100,240,470,420))
        dim(c,p(469,68),p(469,70),'2.000 gap',True,offset=-80)
        mark(c,p(465,72),'80 mm fan frame',(760,540));mark(c,p(470.8,66),'I/O carrier',(760,460))
    t=242.25 if mod else 170
    selected=[a['shape'] for a in parts if a['name'] in ('GPU_tray_two_side_bends','Miwin_MG_SW510B_429x225_PCB_photo_reference','M3_8mm_female_female_standoff_1') or 'Sliding_crossbar' in a['name'] or 'Longitudinal_mount_rail' in a['name'] or 'Rail_welded_sheet_bridge' in a['name']]
    new('Backplane support | installed height section','Assembly')
    para('Local CAD section at Y227 through a post and its crossbar. The rail is shown at the right. Cut boundaries are cropped; installed heights share the tray underside datum.',32,H-82,W-64,11)
    p=section_view(c,selected,1,227,[345,226,t,428,228,t+23],(100,300,800,270))
    dim(c,p(357,t+10),p(357,t+18),'8.000 catalog post',True,offset=65)
    mark(c,p(357,t+18),'PCB underside Z'+fmt(t+18),(970,660))
    mark(c,p(370,t+10),'Crossbar top Z'+fmt(t+10),(970,590))
    mark(c,p(424,t+8),'Rail top Z'+fmt(t+8),(970,520))
    mark(c,p(400,t+1.5),'Tray top Z'+fmt(t+1.5),(970,450))
    para('Tray underside Z'+fmt(t)+'. Rail top is 8 above the tray datum; crossbar top 10; PCB underside 18. Female-female posts fasten to loose crossbars from below before the PCB is installed. No nut is required beneath a fitted post.',50,230,1090,11)

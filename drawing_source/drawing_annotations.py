"""Direct dimensions on orthographic sheet profiles, in assembly coordinates."""
import math
from section_drawings import bounds


def dimension(c,a,b,label,offset=0,vertical=False):
    c.setLineWidth(.55);c.setFont('Helvetica',10)
    if vertical:
        x=a[0]+offset;c.line(*a,x-4,a[1]);c.line(*b,x-4,b[1]);c.line(x,a[1],x,b[1])
        for y in (a[1],b[1]):c.line(x-3,y-3,x+3,y+3)
        c.saveState();c.translate(x-7,(a[1]+b[1])/2);c.rotate(90);c.drawCentredString(0,0,label);c.restoreState()
    else:
        y=a[1]+offset;c.line(*a,a[0],y+4);c.line(*b,b[0],y+4);c.line(a[0],y,b[0],y)
        for x in (a[0],b[0]):c.line(x-3,y-3,x+3,y+3)
        c.drawCentredString((a[0]+b[0])/2,y-13,label)


def leader(c,point,end,lines):
    c.setLineWidth(.5);c.line(*point,end[0]-7,end[1]-4);c.circle(*point,1.8,stroke=1,fill=0)
    c.setFont('Helvetica',10)
    for i,line in enumerate(lines):c.drawString(end[0],end[1]+(len(lines)-1-i)*13,line)


def rear_elevation(shape,c,base_z,upper=True):
    """Outside rear: assembly X increases left; dimensions point to actual CAD edges."""
    s=2.15;left=110;bottom=365 if upper else 300
    def p(x,z):return left+(440-x)*s,bottom+(z-base_z)*s
    c.setLineWidth(.6)
    faces=[f for f in shape.Faces() if f.geomType()=='PLANE' and abs(f.Center().y-469)<1e-5 and abs(f.normalAt().y)>.99]
    assert faces,'rear web face is absent'
    for f in faces:
        for wire in f.Wires():
            for edge in wire.Edges():
                points=[edge.startPoint(),edge.endPoint()] if edge.geomType()=='LINE' else [edge.positionAt(i/48) for i in range(49)]
                path=c.beginPath();path.moveTo(*p(points[0].x,points[0].z))
                for v in points[1:]:path.lineTo(*p(v.x,v.z))
                c.drawPath(path)
    count=21 if upper else 8;centres=[(12.645 if upper else 13.345)+20.32*i for i in range(count)];zlo=base_z+16.68 if upper else 23.75;height=100.5 if upper else 103;zhi=zlo+height
    # The upper panel shares the same bracket centres as the lower bank.
    x=centres[-1]
    dimension(c,p(x+7.5,zlo),p(x-7.5,zlo),'15.000',offset=-29)
    dimension(c,p(x+7.5,zlo),p(x+7.5,zhi),f'{height:.3f}',offset=-32,vertical=True)
    xa,xb=centres[-4:-2] if upper else centres[1:3]
    dimension(c,p(xb,zhi),p(xa,zhi),'20.320',offset=42 if upper else 60)
    leader(c,p(x,zlo+48),(p(x,zlo)[0]+55,bottom-(0 if upper else 70)),[f'{count} apertures: 15.000 × {height:.3f}','Nominal R0; 5.320 web between openings'])
    leader(c,p(centres[2]+9.21,zhi-.3),(left+500,bottom+(310 if upper else 390)),['Shelf threads: #6-32 UNC-2B, extruded collars','Every web joins the upper bend','See enlarged top view for thread offset and toe notch'] if upper else ['Nut reliefs join aperture edges','Retention bores: DIA 3.900 / R1.950, normal Z','See enlarged top view for bore offset and toe notch'])
    if not upper:
        leader(c,p(209,110),(left+40,bottom+380),['2 × DIA 76 / R38 exhaust openings','80 mm fans: 71.500 square mounting pitch'])
        leader(c,p(428,154),(left+10,bottom-65),['4 × DIA 3.900 / R1.950','PSU mounting clearance'])
        leader(c,p(245,11),(left+520,bottom-100),['Rear-web clearance: 164.000 × 50.000','X166–330; Z11–61; separate carrier locates shield'])
    c.setFont('Helvetica',10);c.drawString(32,315 if upper else 145,'Exterior rear: X increases LEFT; Z increases UP. Solid lines are the analytic rear-web profile. Dimensions in mm.')


def lower_rear_sheet(parts,api):
    c,new,para,table,view,W,H,out=api
    shape=next(a['shape'] for a in parts if a['name']=='Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns')
    new('Lower rear | directly dimensioned hardware openings','Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns::annotated')
    para('Eight motherboard bracket positions are on the RIGHT when viewed from outside the rear. The power supply is on the LEFT. Leaders identify finished openings; adjacent coordinate schedules locate every repeated feature.',32,H-82,W-64,11)
    rear_elevation(shape,c,0,False)
    para('Rear web 1.200 thick; PCIe apertures Z23.750–126.750. Bracket bearing Z129.280. Motherboard tray top Z8; 8 mm standoffs; PCB underside Z16. The I/O opening and bracket datums use this installed stack.',32,117,W-64,10)


def intake_sheet(parts,checks,api):
    c,new,para,table,view,W,H,out=api;mode=checks['full_intake_mode'];size=checks['upper_fan_size_mm'];pitch=checks['upper_fan_hole_pitch_mm'];xs=checks['upper_fan_centres_x_mm'];diam=checks['front_intake_aperture_mm']
    name='Full_chassis_upper_intake_insert_'+mode
    new('Upper intake insert | fan pattern and front service',name+'::annotated')
    para(f'{len(xs)} × {size} mm fans at Z270. The 390 × 220 × 2 insert sits flush at Y0–2. Remove the grille and six M3 screws, disconnect fan leads, and withdraw the insert and attached fans straight forward.',32,H-82,W-64,11)
    s=2.2;ox=130;oy=240
    def p(x,z):return ox+(x-25)*s,oy+(z-160)*s
    shape=next(a['shape'] for a in parts if a['name']==name)
    for f in shape.Faces():
        if f.geomType()!='PLANE' or abs(f.Center().y)>1e-5:continue
        for edge in f.Edges():
            pts=[edge.startPoint(),edge.endPoint()] if edge.geomType()=='LINE' else [edge.positionAt(i/72) for i in range(73)]
            path=c.beginPath();path.moveTo(*p(pts[0].x,pts[0].z))
            for v in pts[1:]:path.lineTo(*p(v.x,v.z))
            c.drawPath(path)
    x=xs[0];lo=x-pitch/2;hi=x+pitch/2;zl=270-pitch/2;zh=270+pitch/2
    dimension(c,p(lo,zh),p(hi,zh),f'{pitch:.3f} mounting pitch',offset=32)
    dimension(c,p(lo,zl),p(lo,zh),f'{pitch:.3f} mounting pitch',offset=-70,vertical=True)
    leader(c,p(x,270),(p(x,270)[0]-100,p(x,270)[1]+18),[f'DIA {diam:.3f} / R{diam/2:.3f}',f'{len(xs)} airflow openings'])
    leader(c,p(220 if size==180 else 160,zl),(610,210),[f'Shared slots {24.5 if size==180 else 24:.3f} × 5.500; R2.750','Outer slots 9.000 × 5.500; R2.750'])
    leader(c,p(410,270),(1000,450),['6 × DIA 3.400','R1.700 THRU','M3 × 8 screws'])
    para('Carrier cutout 392 × 222: 1 mm clearance per insert edge. Fixed rear backing ring: 398 × 240 × 2; clear window 370 × 200. Capture six standard M3 nuts on the ring before installation; the nuts stay on the fixed carrier during service.',32,163,W-64,10)
    para('Fan screws: four 5 × 8 self-tapping screws per fan, through 2 mm insert into plastic; 6 mm penetration including tip. No fan nuts. Use manufacturer-approved screws. Backing-ring attachment strength, airflow, coating allowances and cable service require physical qualification.',32,112,W-64,10)

"""Dimensioned GPU bracket openings, retention bend, and toe-locator attachment."""
import json


def rear_details(parts, root, api):
    c,new,para,table,view,W,H,out=api
    data=json.loads((root/'rear_panel_design.json').read_text());top=data['retention_top_z_mm'];shift=top-302.21
    axes=[x for x,y in data['retention_hole_axes_xy_mm']];centres=[x-9.21 for x in axes]
    rear=next(p for p in parts if p['name']=='Full_width_twenty_slot_rear_with_side_returns')
    toe=next(p for p in parts if p['name']=='Upper_bank_toe_receiver')
    new('GPU rear panel | apertures, pitch and screw axes',rear['name']+'::interface')
    para('Twenty rear bracket positions serve ten dual-slot GPUs. Apertures and screw holes are different features. Chassis openings below are design dimensions; the PCIe bracket and slot-pitch references do not certify the supplier backplane mounting datum.',32,H-82,W-64,11)
    from drawing_annotations import rear_elevation
    rear_elevation(rear['shape'],c,180+shift,True)
    rows=[['Feature','Dimensions and location'],['20 main PCIe apertures','15.000 wide × 103.000 high; nominal R0 corners. X centre = bracket axis. Bottom Z'+f'{196.68+shift:.3f}; top Z{299.68+shift:.3f}.'],['Bracket spacing','20.320 centre pitch; 40.640 per dual-slot card; 5.320 nominal web between 15.000 apertures.'],['20 retention bores','DIA 3.900 / R1.950 THRU, normal Z, for #6-32 clearance. Y474.080; X = bracket centre + 9.210.'],['20 nut reliefs','10.000 wide × 3.578 high, cut from Y468 to 472. Bottom Z'+f'{top-1.5-2.778-.5:.3f}; top Z{top-1.2:.3f}. Centred on screw X. Reliefs join adjacent aperture edges near the top.'],['4 side-return holes','DIA 3.400 / R1.700 THRU, normal X. Y477.200; Z'+f'{205+shift:.3f} and {290+shift:.3f}; two holes per side.']]
    table(rows,32,288,[205,W-269],10)
    from annotated_geometry import planar,mark
    for start in (0,10):
        new('GPU rear panel | numbered bracket and screw locations',rear['name']+'::axes')
        para('Assembly coordinate view: X increases right. Position 1 has the smallest X. Numbers identify aperture centres in the adjacent schedule; bores lie on the folded shelf at Y474.080. Bracket-bearing plane Z'+f'{top:.3f}.',32,H-82,W-64,11)
        p,lo,hi=planar(c,rear['shape'],1,469,(35,180,640,500))
        rows=[['Position','Aperture X','Bore X','GPU bay']]
        for i in range(start,start+10):
            x=centres[i];xx,zz=p(x,245+shift)
            c.setFont('Helvetica-Bold',9);c.drawCentredString(xx,zz,str(i+1))
            rows.append([i+1,f'{x:.3f}',f'{axes[i]:.3f}',(i+2)//2])
        table(rows,710,H-150,[65,110,110,85],10)
        para('Each aperture is 15 × 103; centre pitch 20.320. Retention bore DIA3.9, offset +9.210 in X from its aperture. These axes do not certify the supplier backplane datum.',710,250,420,11)
    rows=[['Formed feature','Nominal specification'],['Rear web and integral upper shelf','1.200 sheet; one connected formed part. Upper shelf extends to Y481.000.'],['Top bend','90 degrees outward; inside R1.200, outside R2.400. Bend axis parallel X at Y471.400, Z'+f'{top-2.4:.3f}.'],['Tangencies','Vertical web tangent Z'+f'{top-2.4:.3f}; horizontal shelf tangent Y471.400. Flat bearing surface Z{top:.3f}.'],['Bend span','X3.500 to X415.725. Twenty nut-clearance reliefs interrupt the bend locally. Side returns retain their nominal formed geometry; tooling and corner reliefs require fabricator review.'],['Retention joint','GPU bracket 0.860; formed shelf 1.200; standard #6-32 UNC hex nut 2.778 high. A #6-32 × 1/4 inch screw projects 1.512 below the nut at nominal dimensions, without a washer. Nut top at Z'+f'{top-1.2:.3f}.'],['Nut installation','Proposed capture: fixture and weld or braze the twenty standard nuts beneath the shelf before fitting the rear panel to the tray. Protect threads and bracket seating surfaces. Qualify the capture method for tightening torque and repeated GPU service.'],['Forming access','Cut openings and nut reliefs first. Form the segmented upper shelf before the side returns; confirm tooling access on a sample. Clamp the bracket-bearing datum while attaching the toe strip.']]
    from annotated_geometry import context_pages
    context_pages(api,'GPU rear panel | integral retention bend',rear['name']+'::bend',rows[1:],'Integral 1.2 mm shelf and rear web. The following enlarged section identifies the bend radius and tangencies. Capture retention nuts before installing the rear panel.',[('Rear panel and integral shelf',rear['shape'])],[(414,475,top),(414,470.2,top-1.2),(414,471.4,top),(414,471.4,top-2.4),(axes[0],474.08,top-1.2),(axes[1],474.08,top-1.2),(414,470.2,top-2.4)])
    new('GPU rear panel | enlarged retention bend section',rear['name']+'::bend-section')
    import cadquery as cq
    from section_drawings import section_at
    from annotated_geometry import edge_points,polyline,dim
    sec=section_at(rear['shape'],0,414)
    def p(y,z):return 130+(y-468)*25,270+(z-(top-14))*25
    # Clip the intact section to the upper bend detail; the complete panel appears on the preceding sheets.
    box=cq.Solid.makeBox(3,16,16,cq.Vector(413,468,top-14))
    detail=sec.intersect(box)
    for e in detail.Edges():polyline(c,[p(q.y,q.z) for q in edge_points(e)])
    dim(c,p(471.4,top),p(481,top),'9.600 flat shelf',offset=-35)
    mark(c,p(469.35,top-1.15),'Outside R2.400',(660,655))
    mark(c,p(470.45,top-1.8),'Inside R1.200',(660,615))
    mark(c,p(476,top),'Bracket bearing Z'+f'{top:.3f}',(660,565))
    para('Section X414, through intact bend. Y increases right; Z increases up. Sheet 1.200; bend 90 degrees outward. Bend centre Y471.400, Z'+f'{top-2.4:.3f}. Vertical tangent at that Z; horizontal tangent Y471.400.',650,490,470,12)
    para('Retention joint: 0.860 bracket + 1.200 shelf + 2.778 nut. A 6-32 × 1/4 inch screw projects 1.512 beyond the nut without a washer. Fit and qualify the nut capture before closing the assembly.',650,340,470,11)
    new('GPU toe receiver | engagement and factory attachment',toe['name']+'::joint')
    view(toe['shape'],(32,360,1100,335),(0,0,1),'Top (+Z): comb strip inside rear face; open notches face +Y.','toe_detail')
    rows=[['Feature','Dimensions / assembly requirement'],['Locator strip','1.500 thick; X3.500 to X412.725; Y465.000 to Y469.000. Underside Z'+f'{184.05+shift:.3f}; top Z{185.55+shift:.3f}.'],['20 open toe notches','10.790 wide in X × 1.300 deep in Y, square nominal corners; open to Y469.000. Centres use the bracket X schedule; pitch 20.320.'],['Reference toe fit','10.190 × 0.860 bracket toe: 0.600 total X clearance and 0.440 total Y clearance. The toe projects 1.000 below the strip underside.'],['Factory joint to rear web','Underside stitch fillet weld: nominal 1 mm leg × 6 mm length, at each of the 19 inter-slot midpoints. Weld along X at Y469, Z'+f'{184.05+shift:.3f}. Keep welds out of toe notches; deburr before card installation.'],['Why it remains separate','The toe datum lies above the lower edge of the rear web, so a return at that edge cannot locate the toe. A separate flat strip sets this height without forming individual lanced tabs.'],['Assembly and service','Fixture the strip at its specified coordinates relative to the bracket-bearing surface. Weld before attaching the rear panel to the tray and before coating. Inspect with a bracket gauge. The strip stays on the cartridge during GPU insertion and vertical removal.']]
    table(rows,32,348,[215,W-279],10)
    para('The proposed toe weld requires prototype qualification for strength, distortion and bracket-gauge acceptance. Qualify forming tolerances and retention-nut capture separately. Rack ears use screw joints.',32,105,W-64,10)


def enlarged_details(api,lower=False):
    c,new,para,table,view,W,H,out=api
    count=8 if lower else 20
    new(('Motherboard' if lower else 'GPU')+' bracket interface | enlarged dimension details',('Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns' if lower else 'Full_width_twenty_slot_rear_with_side_returns')+'::dimensions')
    para('Coordinate views below use X to the right. Dimensions define the nominal cut features; the bracket-position coordinate schedule locates them on the rear panel. Nut reliefs join the aperture edges as shown on the full rear elevation.',32,H-82,W-64,11)
    def dimension(x1,y1,x2,y2,text,vertical=False,label_offset=-9):
        c.setLineWidth(.5);c.line(x1,y1,x2,y2)
        for x,y in ((x1,y1),(x2,y2)):c.line(x-3,y-3,x+3,y+3)
        c.setFont('Helvetica',11)
        if vertical:
            c.saveState();c.translate(x1+label_offset,(y1+y2)/2);c.rotate(90);c.drawCentredString(0,0,text);c.restoreState()
        else:c.drawCentredString((x1+x2)/2,y1-15,text)
    scale=4.5;x=120;y=170;w=15*scale;h=103*scale;pitch=20.32*scale
    c.setLineWidth(1)
    for xx in (x,x+pitch):
        c.rect(xx,y,w,h,stroke=1,fill=0)
        c.setDash(4,3);c.line(xx+w/2,y-10,xx+w/2,y+h+30);c.setDash()
    dimension(x,y-25,x+w,y-25,'15.000')
    dimension(x-28,y,x-28,y+h,'103.000',True)
    dimension(x+w/2,y+h+30,x+w/2+pitch,y+h+30,'20.320 centres')
    dimension(x+w,y+90,x+pitch,y+90,'5.320 web')
    para(f'MAIN APERTURES<br/>{count} × 15.000 × 103.000<br/>Nominal corner R0<br/>Bracket width 18.420<br/>1.710 overlap per side',335,595,230,12)
    c.setFont('Helvetica-Bold',12);c.drawString(660,680,'RETENTION SHELF - TOP VIEW')
    cx=800;cy=570;s=12;r=1.95*s
    c.circle(cx,cy,r,stroke=1,fill=0);c.setDash(4,3);c.line(cx-65,cy,cx+65,cy);c.line(cx,cy-55,cx,cy+55);c.setDash()
    c.line(cx+r*.707,cy+r*.707,950,630);c.setFont('Helvetica',12);c.drawString(955,630,'DIA 3.900 / R1.950')
    c.setDash(4,3);c.line(cx-9.21*s,cy-55,cx-9.21*s,cy+55);c.setDash()
    dimension(cx-9.21*s,cy-65,cx,cy-65,'9.210 to bracket axis')
    c.setFont('Helvetica',10);c.drawString(660,455,f'{count} bores, pitch 20.320; #6-32 screw clearance')
    c.setFont('Helvetica-Bold',12);c.drawString(660,390,'TOE NOTCH - TOP VIEW')
    x=675;y=310;s=12;length=24;depth=4;left=(length-10.79)/2
    pts=[(0,0),(length,0),(length,depth),(left+10.79,depth),(left+10.79,depth-1.3),(left,depth-1.3),(left,depth),(0,depth),(0,0)]
    path=c.beginPath();path.moveTo(x,y)
    for a,b in pts[1:]:path.lineTo(x+a*s,y+b*s)
    c.drawPath(path)
    dimension(x+left*s,y+depth*s+22,x+(left+10.79)*s,y+depth*s+22,'10.790')
    dimension(x+length*s+35,y+(depth-1.3)*s,x+length*s+35,y+depth*s,'1.300',True,20)
    c.line(x+(left+10.79)*s,y+(depth-1.3)*s,x+length*s+40,y+(depth-1.3)*s)
    c.line(x+length*s,y+depth*s,x+length*s+40,y+depth*s)
    para(f'{count} open notches, pitch 20.320. Strip thickness 1.500. The 10.190 × 0.860 bracket toe has 0.600 total lateral clearance and 0.440 total fore-aft clearance.',660,265,450,11)
    para('The lower locator stays in place for card removal. Welds are below the strip, between notches. Inspect notch width and seating alignment after welding and finishing.',660,170,450,11)

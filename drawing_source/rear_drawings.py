"""Dimensioned GPU bracket openings, retention bend, and toe-locator attachment."""
import json


def rear_details(parts, root, api):
    c,new,para,table,view,W,H,out=api
    from section_drawings import bounds
    name='Full_width_twenty_one_slot_rear_with_side_returns'
    data=json.loads((root/'rear_panel_design.json').read_text());top=data['retention_top_z_mm'];shift=top-302.21
    axes=[x for x,y in data['retention_hole_axes_xy_mm']];centres=[x-9.21 for x in axes];count=len(centres)
    rear=next(p for p in parts if p['name']==name)
    toe=next(p for p in parts if p['name']=='Upper_bank_toe_receiver')
    # Each rear position is labelled with the card whose bracket occupies it.
    owners=[((bounds(p['shape'])[0]+bounds(p['shape'])[3])/2,p['name']) for p in parts if p['group']=='brackets']
    def card(x):
        centre,owner=min(owners,key=lambda q:abs(q[0]-x));assert abs(centre-x)<1e-3,(x,owner)
        return 'Single-width card' if owner.startswith('Auxiliary_') else 'GPU '+owner.split('_')[1]
    new('GPU rear panel | apertures, pitch and screw axes',name+'::interface')
    para(f'{count} rear bracket positions. Position {count}, at the largest X, serves the leading single-width backplane socket; positions 1 to {count-1} serve ten dual-slot GPUs. Position 1 also aligns with the trailing single-width socket, which lies beneath the GPU 10 cooler; it can hold a card only when GPU 10 is absent. Every backplane socket therefore has a rear opening. Chassis openings below are design dimensions; the PCIe bracket and slot-pitch references do not certify the supplier backplane mounting datum.',32,H-82,W-64,11)
    from drawing_annotations import rear_elevation
    rear_elevation(rear['shape'],c,180+shift,True)
    rows=[['Feature','Dimensions and location'],[f'{count} main PCIe apertures','15.000 wide × 100.500 high; nominal R0 corners. X centre = bracket axis. Bottom Z'+f'{196.68+shift:.3f}; top Z{297.18+shift:.3f}, 2.630 below the shelf bend tangent.'],['Bracket spacing','20.320 centre pitch; 40.640 per dual-slot card; 5.320 nominal web between 15.000 apertures. Every web joins the upper bend.'],[f'{count} tapped holes',f'#6-32 UNC-2B THRU the shelf and an extruded collar, normal Z. Tap drill DIA {data["tap_drill_diameter_mm"]:.3f}; collar OD {data["collar_outside_diameter_mm"]:.3f}, {data["collar_height_below_shelf_mm"]:.3f} below the shelf. Y474.080; X = bracket centre + 9.210.'],['4 side-return holes','DIA 3.400 / R1.700 THRU, normal X. Y477.200; Z'+f'{205+shift:.3f} and {290+shift:.3f}; two holes per side.']]
    table(rows,32,288,[205,W-269],10)
    from annotated_geometry import planar,mark
    for start in range(0,count,11):
        new('GPU rear panel | numbered bracket and screw locations',name+'::axes')
        para('Assembly coordinate view: X increases right. Position 1 has the smallest X. Numbers identify aperture centres in the adjacent schedule; tapped holes lie on the folded shelf at Y474.080. Bracket-bearing plane Z'+f'{top:.3f}.',32,H-82,W-64,11)
        p,lo,hi=planar(c,rear['shape'],1,469,(35,180,640,500))
        rows=[['Position','Aperture X','Thread X','Card']]
        for i in range(start,min(start+11,count)):
            x=centres[i];xx,zz=p(x,245+shift)
            c.setFont('Helvetica-Bold',9);c.drawCentredString(xx,zz,str(i+1))
            rows.append([i+1,f'{x:.3f}',f'{axes[i]:.3f}',card(x)+(' or trailing single-width socket' if i==0 else '')])
        table(rows,710,H-150,[65,95,95,180],10)
        para('Each aperture is 15 × 100.5; centre pitch 20.320. Tapped #6-32 hole offset +9.210 in X from its aperture. Each dual-slot GPU occupies two adjacent positions. These axes do not certify the supplier backplane datum.',710,215,420,11)
    span=data['bend_span_x_mm'];xw=(centres[-1]-7.5+centres[-2]+7.5)/2
    rows=[['Formed feature','Nominal specification'],['Rear web and integral upper shelf','1.200 sheet; one connected formed part. Upper shelf extends to Y481.000.'],['Top bend','90 degrees outward; inside R1.200, outside R2.400. Bend axis parallel X at Y471.400, Z'+f'{top-2.4:.3f}.'],['Tangencies','Vertical web tangent Z'+f'{top-2.4:.3f}; horizontal shelf tangent Y471.400. Flat bearing surface Z{top:.3f}.'],['Bend span',f'X{span[0]:.3f} to X{span[1]:.3f}, uninterrupted. Every web between apertures joins the bend. Each side return is formed at R1.200 and ends one thickness below the shelf bend; a relief slot 1.200 high separates the two bends.'],['Retention joint',f'GPU bracket 0.860 on the 1.200 shelf. The #6-32 UNC-2B thread runs through the shelf and a {data["collar_height_below_shelf_mm"]:.3f} extruded collar: {data["thread_length_mm"]:.3f} total. A #6-32 × 1/4 inch screw projects {6.35-.86-data["thread_length_mm"]:.3f} below the collar at nominal dimensions, without a washer. Collar bottom Z{top-data["thread_length_mm"]:.3f}.'],['Thread forming','Pierce the collar pilot holes in the flat blank, form the shelf, then extrude and tap the collars. Each collar edge lies 0.63 from the bend tangent, inside the press-brake die footprint, so extrusion follows bending. No nuts or nut welds. Protect threads during finishing and qualify thread strength for tightening torque and repeated GPU service.'],['Forming access','Cut openings and pierce pilot holes first. Form the upper shelf before the side returns; confirm tooling access on a sample. Clamp the bracket-bearing datum while attaching the toe strip.']]
    from annotated_geometry import context_pages
    context_pages(api,'GPU rear panel | integral retention bend',name+'::bend',rows[1:],'Integral 1.2 mm shelf and rear web. The following enlarged section passes through a tapped hole and its supporting web.',[('Rear panel and integral shelf',rear['shape'])],[(xw,475,top),(xw,470.2,top-1.2),(xw,471.4,top),(xw,471.4,top-2.4),(axes[1],474.08,top-2.5),(axes[2],474.08,top-2.5),(xw,470.2,top-2.4)])
    new('GPU rear panel | enlarged retention bend section',name+'::bend-section')
    import cadquery as cq
    from section_drawings import section_at
    from annotated_geometry import edge_points,polyline,dim
    station=axes[-2]
    sec=section_at(rear['shape'],0,station)
    def p(y,z):return 130+(y-468)*25,270+(z-(top-14))*25
    # Clip the intact section to the upper bend detail; the complete panel appears on the preceding sheets.
    box=cq.Solid.makeBox(3,16,16,cq.Vector(station-1.5,468,top-14))
    detail=sec.intersect(box)
    for e in detail.Edges():polyline(c,[p(q.y,q.z) for q in edge_points(e)])
    under=top-data['sheet_thickness_mm'];bottom=top-data['thread_length_mm']
    dim(c,p(476.13,under),p(481,under),'4.870 shelf beyond collar',offset=40)
    dim(c,p(476.13,bottom),p(476.13,under),f'{data["collar_height_below_shelf_mm"]:.3f} collar',True,offset=-45)
    mark(c,p(478,top),'Bracket bearing Z'+f'{top:.3f}',(660,655))
    mark(c,p(469.35,top-1.15),'Outside R2.400',(660,615))
    mark(c,p(470.45,top-1.8),'Inside R1.200',(660,575))
    mark(c,p(475.6,top-2.2),f'#6-32 UNC-2B: 1.200 shelf + {data["collar_height_below_shelf_mm"]:.3f} collar',(660,535))
    para(f'Section X{station:.3f}, through a tapped hole over an interior web. Y increases right; Z increases up. Sheet 1.200; bend 90 degrees outward. Bend centre Y471.400, Z'+f'{top-2.4:.3f}. Vertical tangent at that Z; horizontal tangent Y471.400. The web continues below the bend.',650,490,470,12)
    para(f'Retention joint: 0.860 bracket on a {data["thread_length_mm"]:.3f} tapped thread (1.200 shelf + {data["collar_height_below_shelf_mm"]:.3f} collar). A 6-32 × 1/4 inch screw projects {6.35-.86-data["thread_length_mm"]:.3f} beyond the collar without a washer.',650,340,470,11)
    new('GPU toe receiver | engagement and factory attachment',toe['name']+'::joint')
    view(toe['shape'],(32,360,1100,335),(0,0,1),'Top (+Z): comb strip inside rear face; open notches face +Y.','toe_detail')
    tx=data['toe_receiver_x_mm']
    rows=[['Feature','Dimensions / assembly requirement'],['Locator strip',f'1.500 thick; X{tx[0]:.3f} to X{tx[1]:.3f}; Y465.000 to Y469.000. Underside Z'+f'{184.05+shift:.3f}; top Z{185.55+shift:.3f}.'],[f'{count} open toe notches','10.790 wide in X × 1.300 deep in Y, square nominal corners; open to Y469.000. Centres use the bracket X schedule; pitch 20.320.'],['Reference toe fit','10.190 × 0.860 bracket toe: 0.600 total X clearance and 0.440 total Y clearance. The toe projects 1.000 below the strip underside.'],['Factory joint to rear web',f'Underside stitch fillet weld: nominal 1 mm leg × 6 mm length, at each of the {count-1} inter-slot midpoints. Weld along X at Y469, Z'+f'{184.05+shift:.3f}. Keep welds out of toe notches; deburr before card installation.'],['Why it remains separate','The toe datum lies above the lower edge of the rear web, so a return at that edge cannot locate the toe. A separate flat strip sets this height without forming individual lanced tabs.'],['Assembly and service','Fixture the strip at its specified coordinates relative to the bracket-bearing surface. Weld before attaching the rear panel to the tray and before coating. Inspect with a bracket gauge. The strip stays on the cartridge during card insertion and vertical removal.']]
    table(rows,32,348,[215,W-279],10)
    para('The proposed toe weld requires prototype qualification for strength, distortion and bracket-gauge acceptance. Qualify forming tolerances and thread strength separately. Rack ears use screw joints.',32,105,W-64,10)


def enlarged_details(api,lower=False):
    c,new,para,table,view,W,H,out=api
    count=8 if lower else 21
    new(('Motherboard' if lower else 'GPU')+' bracket interface | enlarged dimension details',('Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns' if lower else 'Full_width_twenty_one_slot_rear_with_side_returns')+'::dimensions')
    para('Coordinate views below use X to the right. Dimensions define the nominal cut features; the bracket-position coordinate schedule locates them on the rear panel.'+(' Nut reliefs join the aperture edges as shown on the full rear elevation.' if lower else ' The shelf threads are tapped; the rear web has no nut reliefs.'),32,H-82,W-64,11)
    def dimension(x1,y1,x2,y2,text,vertical=False,label_offset=-9):
        c.setLineWidth(.5);c.line(x1,y1,x2,y2)
        for x,y in ((x1,y1),(x2,y2)):c.line(x-3,y-3,x+3,y+3)
        c.setFont('Helvetica',11)
        if vertical:
            c.saveState();c.translate(x1+label_offset,(y1+y2)/2);c.rotate(90);c.drawCentredString(0,0,text);c.restoreState()
        else:c.drawCentredString((x1+x2)/2,y1-15,text)
    height=103 if lower else 100.5
    scale=4.5;x=120;y=170;w=15*scale;h=height*scale;pitch=20.32*scale
    c.setLineWidth(1)
    for xx in (x,x+pitch):
        c.rect(xx,y,w,h,stroke=1,fill=0)
        c.setDash(4,3);c.line(xx+w/2,y-10,xx+w/2,y+h+30);c.setDash()
    dimension(x,y-25,x+w,y-25,'15.000')
    dimension(x-28,y,x-28,y+h,f'{height:.3f}',True)
    dimension(x+w/2,y+h+30,x+w/2+pitch,y+h+30,'20.320 centres')
    dimension(x+w,y+90,x+pitch,y+90,'5.320 web')
    para(f'MAIN APERTURES<br/>{count} × 15.000 × {height:.3f}<br/>Nominal corner R0<br/>Bracket width 18.420<br/>1.710 overlap per side',335,595,230,12)
    c.setFont('Helvetica-Bold',12);c.drawString(660,680,'RETENTION SHELF - TOP VIEW')
    cx=800;cy=570;s=12;r=1.95*s
    if not lower:
        r=2.705/2*s;c.setDash(2,2);c.circle(cx,cy,2.05*s,stroke=1,fill=0);c.setDash()
    c.circle(cx,cy,r,stroke=1,fill=0);c.setDash(4,3);c.line(cx-65,cy,cx+65,cy);c.line(cx,cy-55,cx,cy+55);c.setDash()
    c.line(cx+r*.707,cy+r*.707,950,630);c.setFont('Helvetica',12);c.drawString(955,630,'DIA 3.900 / R1.950' if lower else '#6-32 UNC-2B; tap drill DIA 2.705')
    if not lower:c.setFont('Helvetica',10);c.drawString(955,614,'Dashed: extruded collar OD 4.100, 1.300 below shelf')
    c.setDash(4,3);c.line(cx-9.21*s,cy-55,cx-9.21*s,cy+55);c.setDash()
    dimension(cx-9.21*s,cy-65,cx,cy-65,'9.210 to bracket axis')
    c.setFont('Helvetica',10);c.drawString(660,455,f'{count} bores, pitch 20.320; #6-32 screw clearance' if lower else f'{count} tapped holes, pitch 20.320; no nuts')
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

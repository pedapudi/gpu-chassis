"""Part-specific open-edge, rear-interface and assembly dimension schedules."""
import json,math
from section_drawings import bounds,fmt


def interface_details(parts,mod,api):
    c,new,para,table,view,W,H,out=api;lookup={a['name']:a for a in parts}
    # Module rear-entry and lid features follow the module top; 399.55 is the 4U reference top.
    top=bounds(lookup['Upper_module_lid_with_rear_tabs']['shape'])[5] if mod else 399.25;r=top-399.55
    def z(v):return fmt(v+r)
    def sheet(title,name,rows,note):
        from annotated_geometry import context_pages
        selected=[(name.replace('_',' '),lookup[name]['shape'])]
        extra=[]
        if 'lid' in title.lower():extra=[p for p in parts if p['group']=='lid']
        if 'frame and cap' in title.lower():extra=[p for p in parts if 'folded' in p['name'].lower() and 'cap' in p['name'].lower()]
        if 'rail supports' in title.lower():extra=[p for p in parts if 'Sliding_crossbar' in p['name']][:1]
        for p in extra:
            if p['name']!=name:selected.append((p['name'].replace('_',' '),p['shape']))
        anchors_by_name={
          'Upper_module_rear_perforated_cover':[(100,485,386),(220,485,380.5+r),(438.5,476,385),(220,481,376.82),(143,485,390+r),(24,485,389.55+r)],
          'Upper_rear_perforated_cover':[(220,485,350),(438.5,476,340),(220,481,303.07),(24,485,389.25),(24,486.5,389.25)],
          'Rear_MCIO_lower_U_frame_140mm_top_open_entry':[(140,486.5,378),(220,486.5,380.5+r),(297,488,390+r),(220,488,395+r),(220,494,398.05+r),(143,488,390+r),(220,486.5,380.5+r)],
          'Replacement_lid_adapter_with_undrilled_OEM_side_returns':[(220,240,top),(3,240,top-9.55),(3,118.2,top-10),(7.5,240,221.5),(3,240,212.5),(7.5,240,221.5),(3,100,212.5)],
          'Screw_mounted_3mm_rack_ear_left':[(440,30,200),(441.5,32,185),(220,240,399.25),(3,240,389),(3,128.2,389.25)]}
        if name=='Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns':
            if 'bank' in title:
                anchors=[(5.845,470.2,75.25),(13.345,470.2,75.25),(27.555,470.2,127.78),(22.555,474.08,129.28),(13.345,467.7,12.62),(18.74,468.35,12.62),(23.505,469,11.12)]
            else:anchors=[(435,470.2,80),(428,470.2,154),(247,470.2,110),(166,470.2,36),(318,470.2,7.5),(22.555,474.08,129.28)]
            for p in parts:
                if p['name'] in ('Lower_bank_toe_receiver','Lower_bank_retention_flange'):selected.append((p['name'].replace('_',' '),p['shape']))
        elif name=='Longitudinal_mount_rail_20':
            shift=72.25 if mod else 0
            t=170+shift
            anchors=[(100,190,t),(357,227.5,t+18),(220,226.75,t+10),(420,318.5,t+8),(420,300,t+4.2),(423.6,300,t+6),(420,208.2,t+6),(220,203.2,t)]
            for p in parts:
                if p['name'] in ('GPU_tray_two_side_bends','GPU_tray_spot_welded_channel_146','Rail_square_nut_guide_strip_20_15.2','Rail_square_nut_guide_strip_20_23.6','M3_8mm_female_female_standoff_1','Miwin_MG_SW510B_429x225_PCB_photo_reference'):
                    selected.append((p['name'].replace('_',' '),p['shape']))
        else:anchors=anchors_by_name[name]
        context_pages(api,title,name+'::edge-details',rows,note,selected,anchors)
    if mod:
        sheet('Rear cover | open cable notch and folded edges','Upper_module_rear_perforated_cover',[
            ['Rear web',f'1.500 thick; X1.5–438.5, Y483.5–485, Z375.32–{z(396.55)}. The web top stops 1.500 below the lid underside, clear of the lid tab bends.'],
            ['Top-open cable notch',f'140.000 wide; X150–290, from Z{z(380.5)} to the open web top. Nominal corner R0. Solid land below the notch {fmt(380.5+r-375.32)} high. With the cap removed the clear opening reaches the lid underside at Z{z(398.05)}.'],
            ['Side returns and screws',f'1.500 thick; X1.5–3 and 437–438.5; Y470.2–483.5; Z375.32–{z(396.55)}. One M3 × 6 pan-head screw per side through the body wall at Y477.2/Z390 threads into an extruded M3 thread in each return.'],
            ['Lower inward lip','X15–425, Y481–483.5, Z375.32–376.82: 410.000 wide ×2.500 projection ×1.500 thick. Ends stop 13.500 short of each web end; a 1.500 wide bend-relief slot is cut into the web at each lip end.'],
            ['Fastener roles','Four extruded M3 threads at X143,297 and Z'+z(380.5)+','+z(390)+' take the brush-frame and cap screws. Two more at X24 and 416, Z'+z(389.55)+' take the lid retention screws.'],
            ['Service','Disconnect external cables; remove the cover with its brush frame before GPU or cartridge extraction.']],
            'The upper edge remains open when the brush cap is removed. The printed notch is a clear opening, not a closed rectangular hole. Refer to the formed sections for return direction. Bends are formed at inside radius R1.5 with relief slots at the ends of the partial lower lip.')
        sheet('MCIO frame and cap | open contours and assembly','Rear_MCIO_lower_U_frame_140mm_top_open_entry',[
            ['Lower U-frame blank',f'X138–302, Y485–486.5, Z375.32–{z(398.05)}: 164.000 wide ×{fmt(398.05+r-375.32)} high ×1.500 thick.'],
            ['U-frame top-open notch',f'X150–290, Z{z(380.5)}–{z(398.05)}: 140.000 ×17.550. Side lands 12.000 wide; bottom land {fmt(380.5+r-375.32)} high. Nominal corner R0.'],
            ['Cap left/right ears',f'X138–148 and X292–302; Y486.5–488; Z{z(385)}–{z(398.05)}. Each ear is 10.000 wide ×13.050 high ×1.500 thick.'],
            ['Cap bottom-open recess',f'X148–292, Z{z(385)}–{z(395)}: 144.000 wide ×10.000 deep. Top connecting band Z{z(395)}–{z(398.05)} is 3.050 high. Nominal corner R0.'],
            ['Cap outward return',f'X138–302; Y488–494; Z{z(396.55)}–{z(398.05)}. 164.000 wide ×6.000 projection ×1.500 thick. Overall cap depth 7.500.'],
            ['Attachment order','The four M3 screws thread into extruded collars in the rear cover. Lower screws at X143,297/Z'+z(380.5)+' retain the U-frame; upper screws at X143,297/Z'+z(390)+' release the cap. All frame bores DIA3.4/R1.7.'],
            ['Connector service','Remove the cap before passing a 35 ×14 plug through the 140 ×17.55 opening. Refit around the cables. Brush compression and actual latch clearance require a physical sample.']],
            'The cap and U-frame have different open profiles. Do not substitute the cable-opening rectangle for either part outline. The cap return reaches Y494, 9 mm behind the body.')
        sheet('Module lid and adapter | returns and seating datums','Replacement_lid_adapter_with_undrilled_OEM_side_returns',[
            ['Lid top',f'X0–440; Y2–486.5; Z{z(398.05)}–{z(399.55)}. Sheet 1.500. Two rear tabs fold down at R1.5: X14–34 and 406–426, Y485–486.5, to Z{z(382.55)}.'],
            ['Lid side returns',f'X1.5–3 and X437–438.5; Y22–460; Z{z(381.55)}–{z(398.05)}. Length 438.000; drop 16.500 below top underside. Each return has two L-slots 3.400 wide: a vertical entry at Y108.2 and 423.2 from the lower edge, then a 10.000 rearward leg at Z{z(389.55)}.'],
            ['Lid retention',f'Four M3 × 6 pan-head screws, threaded into M3 holes tapped directly in the body walls at Y118.2 and 433.2, Z{z(389.55)}, act as lid pins; their shanks project 3.000 inside. Two M3 × 6 pan-head retention screws through DIA3.4 holes in the rear tabs, at X24 and 416, Z{z(389.55)}, thread into the rear cover and stop the lid sliding back. Remove: unscrew, slide 10 mm rearward, lift.'],
            ['Adapter ring','X0–440; Y0–485; Z220–221.5. Inner opening X15–425/Y15–470: 410 ×455; perimeter width 15.000.'],
            ['Adapter side returns','X1.5–3 and X437–438.5; Y20–465; Z205–220. Length 445.000; drop 15.000; end setbacks 20.000; clear inside span 434.000.'],
            ['Vertical stack','Adapter top Z221.5; gasket 0.750; module bottom Z222.25. Upper module fasteners locate in the six modeled DIA3.4 bores.'],
            ['OEM interface hold','No OEM screw holes or measured mating rebates are supplied. Transfer the actual lid interface before fabrication. Separate rated rack support carries the populated module.']],
            'Lid return edges and the adapter profile are nominal design geometry. No corner-relief cuts are modeled. Do not infer measured RM53-502 lid compatibility from these coordinate values.')
    else:
        centres=[13.345+20.32*i for i in range(8)]
        sheet('Lower rear bank | apertures, retention and toe engagement','Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns',[
            ['Eight bracket apertures','15.000 wide ×103.000 high, nominal corner R0. Z23.750–126.750; through rear web Y469–470.2. Pitch 20.320; nominal web 5.320.'],
            ['Aperture centre X','13.345, 33.665, 53.985, 74.305, 94.625, 114.945, 135.265, 155.585.'],
            ['Rear web above the bank','Solid between the apertures and the tab slot. The tapped collars under the retention strip stay 1.83 clear of the web, so the web needs no nut reliefs.'],
            ['Retention strip','1.500 thick; underside Z127.780; bracket bearing Z129.280. Eight M3 extruded tapped holes (tap drill DIA2.5, collar OD3.7 × 1.5 below the strip), normal Z, at Y474.080 and X22.555 +20.320n for n=0…7. M3 × 5 bracket screws.'],
            ['Lower toe receiver','1.500 thick; X3.5–165.5, Y465–469, Z11.120–12.620. Eight top-view notches, 10.790 wide ×1.300 deep, open to Y469; root Y467.700. Same centre X schedule as apertures.'],
            ['Toe clearance','Reference toe 10.190 wide ×0.860 thick. Total nominal clearance 0.600 across X and 0.440 along Y. Toe projects 1.000 below strip underside.'],
            ['Toe factory attachment','Proposed seven underside stitch fillet welds: nominal 1 mm leg ×6 mm length, along X at Y469/Z11.12. Centres X23.505 +20.320n, n=0…6. Fixture to bracket datum, weld and deburr before rear assembly installation.']],
            'The separate retention strip requires factory attachment before motherboard installation; extrude and tap its collars first. Qualify weld strength, distortion, screw torque and bracket seating with a physical gauge. The sheet openings are clearance features, not tapped holes.')
        sheet('Lower rear | hardware functions and mounting datums','Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns',[
            ['Panel construction','Rear web 1.200 thick; side returns 1.500. The thickness transition represents joined pieces, not a uniform-sheet bend.'],
            ['PSU mounting','Four DIA3.9/R1.95 clearance bores normal Y for standard #6-32 screws. X/Z centres: (428,16), (428,154), (354,130), (364,16). Rear-view orientation: PSU left.'],
            ['80 mm exhaust fans','Eight horizontal obrounds: 9.000 overall ×5.500 width, end R2.750. Centres X173.25,244.75,255.25,326.75 at Z74.25 and145.75. Two DIA76/R38 air openings at X209,291/Z110. Frame size 80; screw pitch 71.500 square. Verify supplied fan screws.'],
            ['Motherboard I/O clearance','Rear web: 164.000 ×50.000, X166–330/Z11–61. The separate 1.2 mm carrier locates the 158.750 ×44.450 shield reference at X168.6884–327.4384/Z13.7648–58.2148. Do not use shield size as the rear-web cut size.'],
            ['Rear attachment holes','Four DIA3.4/R1.7 clearance holes for the separate I/O carrier, whose screws thread into extruded M3 collars in the carrier, and two extruded M3 threads in the web for the external MCIO frame. The part hole schedule controls their individual centres.'],
            ['Motherboard height chain','Tray underside/top Z7.5 /9.5; ATX standoffs 6.5 high; PCB underside/top Z16 /17.57; lower bracket bearing Z129.28. I/O and PCIe openings share these installed datums.']],
            'Use the stepped PSU-opening profile on the following sheet; its bounding rectangle omits the screw lands. Rear-view diagrams place PSU left, I/O middle and PCIe positions right. Coordinate profiles explicitly use X increasing right.')
        psu_profile(lookup['Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns']['shape'],api)
        sheet('Rack ears, lid returns and lid pins','Screw_mounted_3mm_rack_ear_left',[
            ['Rack-ear construction','3.000 steel, formed at R3. Ears attach to the body with side M4 × 10 screws; rack-ear joints are not welded.'],
            ['Rack-ear side screws','Six per ear at Y32 and 55; Z45, 185 and 345. They thread into extruded M4 threads in the 1.5 mm body wall (tap drill DIA3.3).'],
            ['Lid top','X0–440; Y2–486.5; Z397.75–399.25. Sheet 1.500. It reaches over the rear cover and folds two rear tabs down.'],
            ['Lid returns','X1.5–3 and X437–438.5; Y22–459.2; Z381.25–397.75. Length 437.200; drop 16.500; they stop 11.000 ahead of the rear-cover returns so the lid can slide 10.000 rearward. Each return has two L-slots 3.400 wide: a vertical entry at Y118.2 and 423.2 from the lower edge, then a 10.000 rearward leg at Z389.25.'],
            ['Lid pins','Four M3 × 6 pan-head screws from outside the body walls at Y128.2 and 433.2, Z389.25. They thread into M3 holes tapped directly in the 1.5 mm walls (tap drill DIA2.5, no collar, so the lid returns lie flat) and their shanks project 3.000 inside.']],
            'The lid drops on 10 mm behind its seated position and slides forward until the pins reach the rear ends of the slots; two rear retention screws then stop it sliding back.')
        sheet('Rear cover and lid retention screws','Upper_rear_perforated_cover',[
            ['Cover web','X1.5–438.5, Y483.5–485, Z303.07–396.25; 1.500 sheet. DIA8 perforations on a 10.000 pitch stay clear of the lid screw holes and of the lid tabs. The web top stops 1.500 below the lid underside, clear of the lid tab bends.'],
            ['Side returns and screws','1.500 thick; X1.5–3 and 437–438.5; Y470.2–483.5. Two M3 × 6 pan-head screws per side through the body wall at Y477.2, Z313 and 381.45, thread into extruded M3 threads in the returns.'],
            ['Lower lip','X15–425, Y481–483.5, Z303.07–304.57, folded forward at R1.5, with a 1.500 wide relief slot at each lip end.'],
            ['Lid screw threads','Extruded M3 threads in the web at X24 and 416, Z389.25 (tap drill DIA2.5, collars forward).'],
            ['Lid rear tabs','Folded down from the lid rear edge at R1.5: X14–34 and 406–426, Y485–486.5, Z382.25–397.75. Each has a DIA3.4 hole for an M3 × 6 pan-head retention screw.']],
            'Remove the lid first: take out its two rear retention screws, slide it 10 mm rearward off the wall pins and lift it. Then remove the cover side screws and withdraw the cover.')
    sheet('Rail supports | installed levels and factory joints','Longitudinal_mount_rail_20',[
        ['GPU tray datum','Underside Z'+('242.250; top Z243.750.' if mod else '170.000; top Z171.500.')],
        ['Support and board levels',('Tray boss top /rail underside Z248.250; rail top /crossbar underside Z250.250; crossbar top Z252.250; PCB underside Z260.250; PCB top Z262.750.' if mod else 'Tray boss top /rail underside Z176.000; rail top /crossbar underside Z178.000; crossbar top Z180.000; PCB underside Z188.000; PCB top Z190.500.')],
        ['X adjustment','Crossbar slot 382.000 overall ×3.500 width, end R1.750. Permitted post centre X32–408. Catalog 8 mm M3 female–female posts attach from below the loose crossbar with M3 ×6 screws and 0.5 washers.'],
        ['Y adjustment','Guide strips span Y219.2–447.2; 7.000 square nuts give centre limits Y222.7–443.7. Selected crossbar Y225.0,318.5,434.2.'],
        ['Guide channel','7.200 clear guide gap for DIN562 M4 square nuts, nominal 7.000 AF ×2.200 high. Guide strips are 1.200 thick ×3.800 high ×228.000 long beneath the 2.000 rail.'],
        ['Guide-strip attachment','Factory-attach guide strips to the rail underside with the 7.200 gauge in place. Keep joint material outside the nut channel and sliding path. Load nuts from an open end before rail installation. Joint size and pitch require fabrication release.'],
        ['Tray bosses','Four bosses embossed 4.500 up from the 1.5 mm GPU tray at X20 and 420, Y208.2 and 458.2: DIA20 base, DIA10 top. Each carries an extruded M4 thread; the rails screw down onto them.'],
        ['Other fixed sheet joints','Tray stiffening channels attach on their upper crown; bearing stretchers attach to side angles. Complete fixed joints and formed threads on the bench before boards and cables. Weld type, size, pitch and acceptance criteria remain release holds.']],
        'Dimensions above use a single assembly Z datum. Tray underside, tray top and rail top are different levels. The joint notes identify assembly access; they do not certify welded-joint capacity.')


def psu_profile(shape,api):
    c,new,para,table,view,W,H,out=api
    wire=None
    for face in shape.Faces():
        if abs(face.Center().y-469)>1e-5:continue
        for candidate in face.Wires():
            b=bounds(candidate)
            if abs(b[0]-350)<1e-4 and abs(b[3]-432)<1e-4 and abs(b[2]-12)<1e-4 and abs(b[5]-158)<1e-4:wire=candidate;break
    assert wire is not None
    graph={}
    for edge in wire.Edges():
        assert edge.geomType()=='LINE'
        a=tuple(round(edge.startPoint().toTuple()[i],5) for i in (0,2));b=tuple(round(edge.endPoint().toTuple()[i],5) for i in (0,2))
        graph.setdefault(a,[]).append(b);graph.setdefault(b,[]).append(a)
    start=min(graph);points=[start];prev=None;now=start
    while True:
        nxt=next(p for p in sorted(graph[now]) if p!=prev)
        if nxt==start:break
        points.append(nxt);prev,now=now,nxt
        assert len(points)<=len(graph)
    assert len(points)==len(graph)
    new('PSU rear opening | exact stepped profile','Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns::psu-profile')
    para('Coordinate view: X increases right and Z increases up. Join numbered vertices in order and close the last to the first. Every edge is straight with nominal R0 corners. This is the clear cut through Y469–470.2; the surrounding screw lands remain solid.',32,H-82,W-64,11)
    x0,y0,s=100,130,3.7
    def p(q):return x0+(q[0]-350)*s,y0+(q[1]-12)*s
    path=c.beginPath();path.moveTo(*p(points[0]))
    for q in points[1:]+points[:1]:path.lineTo(*p(q))
    c.drawPath(path);c.setFont('Helvetica',10)
    for i,q in enumerate(points):
        x,y=p(q);c.circle(x,y,1.5,stroke=1,fill=0);c.drawString(x+5,y+5,str(i+1))
    table([['Vertex','X','Z','Length to next']]+[[i+1,fmt(q[0]),fmt(q[1]),fmt(math.dist(q,points[(i+1)%len(points)]))] for i,q in enumerate(points)],650,H-145,[80,100,100,150],10)
    para('Envelope 82.000 ×146.000; screw-land steps are defined by the vertex schedule. The separate PSU mounting bores are DIA3.9/R1.95 clearance for #6-32 fasteners.',650,190,450,11)
    (out/'coordinates/lower_rear_psu_opening_vertices.json').write_text(json.dumps(points,indent=2))

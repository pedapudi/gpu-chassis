"""Part-specific open-edge, rear-interface and assembly dimension schedules."""
import json,math
from section_drawings import bounds,fmt


def interface_details(parts,mod,api):
    c,new,para,table,view,W,H,out=api;lookup={a['name']:a for a in parts}
    def sheet(title,name,rows,note):
        new(title,name+'::edge-details')
        y=table([['Feature','Nominal formed dimensions / assembly requirement']]+rows,32,H-85,[235,885],11)
        para(note,32,y,W-64,11)
    if mod:
        sheet('Rear cover | open cable notch and folded edges','Upper_module_rear_perforated_cover',[
            ['Rear web','1.500 thick; X1.5–438.5, Y483.5–485, Z375.32–398.05.'],
            ['Top-open cable notch','140.000 wide ×17.550 deep; X150–290, Z380.5–398.05. Nominal corner R0. Lower land 5.180 high.'],
            ['Side returns','1.500 thick; X1.5–3 and 437–438.5; Y470.2–483.5; Z375.32–398.05. Projection 13.300; height 22.730.'],
            ['Lower inward lip','X15–425, Y481–483.5, Z375.32–376.82: 410.000 wide ×2.500 projection ×1.500 thick. Ends stop 13.500 short of each web end.'],
            ['Fastener roles','Two side-return DIA3.4/R1.7 holes at Y477.2/Z390 retain the cover. Four rear DIA3.4/R1.7 holes at X143,297 and Z380.5,393 attach the brush assembly. All are clearance holes.'],
            ['Service','Disconnect external cables; remove the cover with its brush frame before GPU or cartridge extraction.']],
            'The upper edge remains open when the brush cap is removed. The printed notch is a clear opening, not a closed rectangular hole. Refer to the formed sections for return direction. Bend radii and corner reliefs remain fabrication-release dimensions.')
        sheet('MCIO frame and cap | open contours and assembly','Rear_MCIO_lower_U_frame_140mm_top_open_entry',[
            ['Lower U-frame blank','X138–302, Y485–486.5, Z375.32–398.05: 164.000 wide ×22.730 high ×1.500 thick.'],
            ['U-frame top-open notch','X150–290, Z380.5–398.05: 140.000 ×17.550. Side lands 12.000 wide; bottom land 5.180 high. Nominal corner R0.'],
            ['Cap left/right ears','X138–148 and X292–302; Y486.5–488; Z387–398.05. Each ear is 10.000 wide ×11.050 high ×1.500 thick.'],
            ['Cap bottom-open recess','X148–292, Z387–395: 144.000 wide ×8.000 deep. Top connecting band Z395–398.05 is 3.050 high. Nominal corner R0.'],
            ['Cap outward return','X138–302; Y488–494; Z396.55–398.05. 164.000 wide ×6.000 projection ×1.500 thick. Overall cap depth 7.500.'],
            ['Attachment order','Capture the four standard M3 nuts on the rear cover before installation. Lower screws at X143,297/Z380.5 retain the U-frame; upper screws at X143,297/Z393 release the cap. All frame bores DIA3.4/R1.7.'],
            ['Connector service','Remove the cap before passing a 35 ×14 plug through the 140 ×17.55 opening. Refit around the cables. Brush compression and actual latch clearance require a physical sample.']],
            'The cap and U-frame have different open profiles. Do not substitute the cable-opening rectangle for either part outline. The cap return reaches Y494, 9 mm behind the body.')
        sheet('Module lid and adapter | returns and seating datums','Replacement_lid_adapter_with_undrilled_OEM_side_returns',[
            ['Lid top','X0–440; Y2–485; Z398.05–399.55. Sheet 1.500.'],
            ['Lid side returns','X1.5–3 and X437–438.5; Y22–460; Z381.55–398.05. Length 438.000; drop 16.500 below top underside; front/rear setbacks 20.000 /25.000 from top-sheet ends.'],
            ['Lid clearance bores','DIA3.6/R1.8 normal X at Y118.2 and 433.2, Z389.55; two per side. Use M3 ×6 screws and captive M3 nuts.'],
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
            ['Eight nut-clearance reliefs','10.000 wide ×3.278 high; Z124.502–127.780, normal Y through web. X centre = aperture centre +9.210. Reliefs merge with adjacent aperture edges; the combined cutout bounding box is not an individual PCIe opening.'],
            ['Retention strip','1.500 thick; underside Z127.780; bracket bearing Z129.280. Eight DIA3.9/R1.95 bores, normal Z, at Y474.080 and X22.555 +20.320n for n=0…7. Standard #6-32 ×1/4 in screws and captive hex nuts.'],
            ['Lower toe receiver','1.500 thick; X3.5–165.5, Y465–469, Z11.120–12.620. Eight top-view notches, 10.790 wide ×1.300 deep, open to Y469; root Y467.700. Same centre X schedule as apertures.'],
            ['Toe clearance','Reference toe 10.190 wide ×0.860 thick. Total nominal clearance 0.600 across X and 0.440 along Y. Toe projects 1.000 below strip underside.'],
            ['Toe factory attachment','Proposed seven underside stitch fillet welds: nominal 1 mm leg ×6 mm length, along X at Y469/Z11.12. Centres X23.505 +20.320n, n=0…6. Fixture to bracket datum, weld and deburr before rear assembly installation.']],
            'The separate retention strip and its standard captive nuts require factory attachment before motherboard installation. Qualify weld strength, distortion, screw torque and bracket seating with a physical gauge. The sheet openings are clearance features, not tapped holes.')
        sheet('Lower rear | hardware functions and mounting datums','Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns',[
            ['Panel construction','Rear web 1.200 thick; side returns 1.500. The thickness transition represents joined pieces, not a uniform-sheet bend.'],
            ['PSU mounting','Four DIA3.9/R1.95 clearance bores normal Y for standard #6-32 screws. X/Z centres: (428,16), (428,154), (354,130), (364,16). Rear-view orientation: PSU left.'],
            ['80 mm exhaust fans','Eight horizontal obrounds: 9.000 overall ×5.500 width, end R2.750. Centres X173.25,244.75,255.25,326.75 at Z74.25 and145.75. Two DIA76/R38 air openings at X209,291/Z110. Frame size 80; screw pitch 71.500 square. Verify supplied fan screws.'],
            ['Motherboard I/O clearance','Rear web: 164.000 ×50.000, X166–330/Z11–61. The separate 1.2 mm carrier locates the 158.750 ×44.450 shield reference at X168.6884–327.4384/Z13.7648–58.2148. Do not use shield size as the rear-web cut size.'],
            ['Rear attachment bores','Six DIA3.4/R1.7 clearance holes for the separate I/O carrier and external MCIO frame. The part hole schedule controls their individual centres. Use captive M3 nuts; no sheet tapping is modeled.'],
            ['Motherboard height chain','Tray underside/top Z6 /8; posts 8 high; PCB underside/top Z16 /17.57; lower bracket bearing Z129.28. I/O and PCIe openings share these installed datums.']],
            'Use the stepped PSU-opening profile on the following sheet; its bounding rectangle omits the screw lands. Rear-view diagrams place PSU left, I/O middle and PCIe positions right. Coordinate profiles explicitly use X increasing right.')
        psu_profile(lookup['Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns']['shape'],api)
        sheet('Rack-ear open clearance and lid return ends','Screw_mounted_3mm_rack_ear_left',[
            ['Rack-ear construction','3.000 steel; ears attach to the body with side M4 screws and captive nuts. Rack-ear joints are not spot welded.'],
            ['One edge notch per ear','Circular cut R3.300 centred Y65 /Z389.25, open to the flange edge Y64. Deepest point Y61.700, so edge-cut depth 2.300.'],
            ['Edge intersections','At Y64: Z386.105163 and Z392.394837. Notch passes through X−3–0 on one ear and X440–443 on the other. It is not a complete DIA6.6 hole.'],
            ['Lid top','X0–440; Y2–485; Z397.75–399.25. Sheet 1.500.'],
            ['Lid returns','X1.5–3 and X437–438.5; Y22–469.2; Z381.25–397.75. Length 447.200; drop 16.500. Front/rear setbacks 20.000 /15.800 from top-sheet ends.'],
            ['Lid bores','DIA3.6/R1.8 normal X at Y118.2,433.2 /Z389.25. Two per side. The delivered lid has no edge notch.']],
            'The rack-ear open clearance belongs to the ear. Do not add a corresponding notch to the lid unless the physical installation requires and verifies one.')
    sheet('Rail supports | installed levels and factory joints','Longitudinal_mount_rail_20',[
        ['GPU tray datum','Underside Z'+('242.250; top Z243.750.' if mod else '170.000; top Z171.500.')],
        ['Support and board levels',('Bridge top /rail underside Z248.250; rail top /crossbar underside Z250.250; crossbar top Z252.250; PCB underside Z260.250; PCB top Z262.750.' if mod else 'Bridge top /rail underside Z176.000; rail top /crossbar underside Z178.000; crossbar top Z180.000; PCB underside Z188.000; PCB top Z190.500.')],
        ['X adjustment','Crossbar slot 382.000 overall ×3.500 width, end R1.750. Permitted post centre X32–408. Catalog 8 mm M3 female–female posts attach from below the loose crossbar with M3 ×6 screws and 0.5 washers.'],
        ['Y adjustment','Guide strips span Y219.2–447.2; 7.000 square nuts give centre limits Y222.7–443.7. Selected crossbar Y225.0,318.5,434.2.'],
        ['Guide channel','7.200 clear guide gap for DIN562 M4 square nuts, nominal 7.000 AF ×2.200 high. Guide strips are 1.200 thick ×3.800 high ×228.000 long beneath the 2.000 rail.'],
        ['Guide-strip attachment','Factory-attach guide strips to the rail underside with the 7.200 gauge in place. Keep joint material outside the nut channel and sliding path. Load nuts from an open end before rail installation. Joint size and pitch require fabrication release.'],
        ['Bridges and captive nuts','Capture the standard bridge nuts before attaching bridge feet to the tray. Fasten rails from above. Keep welds clear of nut flats, threads and screw tool paths; qualify bridge strength and distortion.'],
        ['Other fixed sheet joints','Tray stiffening channels attach on their upper crown; bearing stretchers attach to side angles. Complete fixed joints and captive-nut installation on the bench before boards and cables. Weld type, size, pitch and acceptance criteria remain release holds.']],
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

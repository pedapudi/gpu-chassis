"""Dimensioned sections and planar sheet extents from the analytic formed parts."""
import json,math
import cadquery as cq
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box


def bounds(shape):
    box=Bnd_Box();BRepBndLib.AddOptimal_s(shape.wrapped,box,False,False);return list(box.Get())


def fmt(x):return f'{x:.4f}'.rstrip('0').rstrip('.')


def material_note(name):
    if name=='Front_fan_carrier_with_side_returns' or name.startswith('Upper_module_front_carrier_'):
        return 'Joined sheet assembly: 2.000 front web; 1.500 side angles. '+('Grille fixing lands overlap to 3.500. Single-row options add a 2 mm backing ring at Y2–4, factory attached before fitting the removable insert. ' if name=='Front_fan_carrier_with_side_returns' else '')+'Do not form this as a uniform-thickness blank.'
    if name in ('Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns','Upper_module_rear_sill_with_side_returns'):
        return 'Joined sheet assembly: 1.200 rear web; 1.500 side returns. Join before fitting hardware; the modeled thickness transition is not a single-sheet bend.'
    thick=1.5
    if any(t in name for t in ('1p2mm','_guide_strip_')) or name=='Full_width_twenty_one_slot_rear_with_side_returns':thick=1.2
    if any(t in name for t in ('Longitudinal_mount_rail','Sliding_crossbar','WRX90_board_specific','Full_chassis_upper_intake_insert')):thick=2
    if 'Screw_mounted_3mm' in name:thick=3
    if '1mm_perforated_grille' in name or '1mm_blanking_plate' in name:thick=1
    return f'Nominal steel sheet thickness {thick:.3f} mm. Material grade, finish and production tolerances require release review.'


def wall_faces(shape,name):
    rows=[];seen=set()
    for face in shape.Faces():
        if face.geomType()!='PLANE':continue
        normal=face.normalAt().toTuple();axis=max(range(3),key=lambda i:abs(normal[i]))
        if abs(normal[axis])<.999999:continue
        b=bounds(face);uv=[i for i in range(3) if i!=axis];sizes=[b[i+3]-b[i] for i in uv]
        # Narrow thickness faces and aperture walls are described by the sections.
        cover_lip=name in ('Upper_rear_perforated_panel_with_side_returns','Upper_module_rear_perforated_cover') and axis==2 and abs(sizes[0]-410)<1e-4 and abs(sizes[1]-2.5)<1e-4
        if min(sizes)<3.6 and not cover_lip:continue
        row=dict(normal='XYZ'[axis],station=round(face.Center().toTuple()[axis],4),axes=''.join('XYZ'[i] for i in uv),limits=[round(b[i],4) for i in uv]+[round(b[i+3],4) for i in uv])
        key=(row['normal'],row['station'],*row['limits'])
        if key not in seen:rows.append(row);seen.add(key)
    return sorted(rows,key=lambda r:(r['normal'],r['station'],r['limits']))


def section_at(shape,axis,station):
    origin=[0,0,0];origin[axis]=station;normal=[0,0,0];normal[axis]=1
    return shape.intersect(cq.Face.makePlane(basePnt=cq.Vector(*origin),dir=cq.Vector(*normal)))


def draw_sections(a,api):
    c,new,para,table,view,W,H,out=api;name=a['name'];shape=a['shape'];b=bounds(shape);dims=[b[i+3]-b[i] for i in range(3)]
    if min(dims)<=3.50001:return dict(part=name,section_sheets=0,reason='Flat part; overall and opening dimensions define the nominal plate. Edge-open cuts have separate interface details where present.')
    chosen=[]
    for axis in sorted(range(3),key=lambda i:-dims[i])[:2]:
        candidates=[]
        stations=[round(b[axis]+dims[axis]*fraction,5) for fraction in (.05,.25,.5,.75,.95)]
        # A section must cross the defining fold, not an unbent end margin.
        # Through a tapped hole over an interior web: the second-largest thread axis X.
        if name=='Full_width_twenty_one_slot_rear_with_side_returns' and axis==0:stations=[sorted({round(e.Center().x,4) for e in shape.Edges() if e.geomType()=='CIRCLE' and abs(e.radius()-1.3525)<1e-4})[-2]]
        if name in ('GPU_tray_two_side_bends','Lid_with_separate_side_fasteners','Upper_module_side_fastened_lid') and axis==1:stations=[328.2 if name=='GPU_tray_two_side_bends' else 240.0]
        thin_axis=min(range(3),key=lambda i:dims[i])
        for station in stations:
            sec=section_at(shape,axis,station)
            if sec.Edges():
                sb=bounds(sec);fold_span=round(sb[thin_axis+3]-sb[thin_axis],5)
                candidates.append((-fold_span,len(sec.Edges()),-sum(f.Area() for f in sec.Faces()),station,sec))
        if not candidates:continue
        _,_,_,station,sec=min(candidates,key=lambda q:q[:4]);uv=[i for i in range(3) if i!=axis]
        vertices=sorted(set(tuple(round(v.Center().toTuple()[i],5) for i in uv) for v in sec.Vertices()))
        edges=[]
        for edge in sec.Edges():
            row=dict(type=edge.geomType(),start=[round(edge.startPoint().toTuple()[i],5) for i in uv],end=[round(edge.endPoint().toTuple()[i],5) for i in uv],length=round(edge.Length(),5))
            if edge.geomType()=='CIRCLE':row['radius']=round(edge.radius(),5)
            edges.append(row)
        chosen.append(dict(axis=axis,station=station,uv=uv,shape=sec,vertices=vertices,edges=edges))
    new(name.replace('_',' ')+' | formed sections',name+'::sections')
    y=para(material_note(name),32,H-82,W-64,10)
    para('Sections use the assembly coordinates and positive axes shown below. Coordinates and successive gaps dimension each step in the section. The cuts include local openings if the section crosses them; they are not developed blanks.',32,y,W-64,10)
    for j,d in enumerate(chosen):
        x0=60+j*580;y0=425;ww=505;hh=220;sec=d['shape'];bb=bounds(sec);uv=d['uv'];lo=[bb[i] for i in uv];hi=[bb[i+3] for i in uv];scale=min(ww/max(hi[0]-lo[0],1),hh/max(hi[1]-lo[1],1))
        ox=x0+(ww-(hi[0]-lo[0])*scale)/2;oy=y0+(hh-(hi[1]-lo[1])*scale)/2
        def pt(vector):q=vector.toTuple();return ox+(q[uv[0]]-lo[0])*scale,oy+(q[uv[1]]-lo[1])*scale
        c.setFont('Helvetica-Bold',11);c.drawString(x0,680,f'Section normal {"XYZ"[d["axis"]]} at {"XYZ"[d["axis"]]} = {fmt(d["station"])}')
        c.setLineWidth(.65)
        for edge in sec.Edges():
            points=[pt(edge.startPoint()),pt(edge.endPoint())] if edge.geomType()=='LINE' else [pt(edge.positionAt(k/40)) for k in range(41)]
            path=c.beginPath();path.moveTo(*points[0])
            for p in points[1:]:path.lineTo(*p)
            c.drawPath(path)
        from annotated_geometry import dim
        dim(c,(ox,oy),(ox+(hi[0]-lo[0])*scale,oy),fmt(hi[0]-lo[0]),offset=17)
        dim(c,(ox,oy),(ox,oy+(hi[1]-lo[1])*scale),fmt(hi[1]-lo[1]),True,offset=18)
        c.setFont('Helvetica',9);c.drawString(x0,377,f'{"XYZ"[uv[0]]} increases right; {"XYZ"[uv[1]]} increases up. Section extents {fmt(hi[0]-lo[0])} × {fmt(hi[1]-lo[1])}.')
        rows=[['Axis','Coordinate levels','Successive gaps']]
        for index,ax in enumerate(uv):
            levels=sorted(set(v[index] for v in d['vertices']));gaps=[b-a for a,b in zip(levels,levels[1:])]
            rows.append(['XYZ'[ax],', '.join(fmt(q) for q in levels),', '.join(fmt(q) for q in gaps)])
        radii=sorted(set(q['radius'] for q in d['edges'] if 'radius' in q))
        rows.append(['Curves','R'+', R'.join(fmt(q) for q in radii) if radii else 'Straight edges; no bends in this section','Radii shown only where modeled.'])
        table(rows,x0,355,[45,245,215],9)
    para('Formed bends have inside radius equal to the sheet thickness; square corners in a section are joints between separate pieces or cut edges. Developed flat patterns and bend tables are in flat_patterns/. Weld distortion requires fabrication qualification. Exact section edges are supplied in the matching sections JSON.',32,115,W-64,10)
    serial=[{k:v for k,v in d.items() if k!='shape'} for d in chosen]
    (out/'coordinates'/(name+'_sections.json')).write_text(json.dumps(serial,indent=2))
    faces=wall_faces(shape,name)
    from annotated_geometry import planar
    face_groups={}
    for row in faces:face_groups.setdefault((row['normal'],row['station']),[]).append(row)
    face_groups=list(face_groups.items())
    for start in range(0,len(face_groups),4):
        new(name.replace('_',' ')+' | dimensioned sheet faces',name+'::walls')
        para('Complete contours of the physical faces. Each dimension and coordinate range refers to the adjacent face, including its actual holes and open-edge cuts. Thickness faces are shown in the formed sections. Coordinates use the assembly datum.',32,H-82,W-64,10)
        for j,((normal,station),face_rows) in enumerate(face_groups[start:start+4]):
            x=35+(j%2)*575;y=440-(j//2)*335
            p,lo,hi=planar(c,shape,'XYZ'.index(normal),station,(x,y,545,245))
            axes=face_rows[0]['axes']
            para(f'<b>{normal} = {fmt(station)}</b> | {axes[0]} {fmt(lo[0])} to {fmt(hi[0])}; {axes[1]} {fmt(lo[1])} to {fmt(hi[1])}. Complete contour bounds; openings remain void.',x,y-8,535,9)
        para('Formed bends use inside radius equal to thickness and K-factor 0.40 for development; confirm both with the fabricator before cutting blanks.',32,85,W-64,9)
    (out/'coordinates'/(name+'_walls.json')).write_text(json.dumps(faces,indent=2))
    return dict(part=name,section_sheets=1,wall_sheets=math.ceil(len(face_groups)/4),sections=[dict(normal='XYZ'[d['axis']],station=d['station'],edges=len(d['edges'])) for d in chosen])

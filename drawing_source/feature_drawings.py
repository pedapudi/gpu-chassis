"""Print dimensioned cutout families and datum coordinates from analytic sheet faces."""
import math, collections, json, csv
from pathlib import Path

# Outside diameters of the M3 and M4 extruded thread collars.
COLLAR_DIAMETERS={3.7,4.9}


def features(shape):
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_IN
    classifier=BRepClass3d_SolidClassifier(shape.wrapped)
    def inside(point):
        classifier.Perform(gp_Pnt(*point.toTuple()),1e-6)
        return classifier.State()==TopAbs_IN or classifier.IsOnAFace()
    found=collections.defaultdict(list)
    for face in shape.Faces():
        if face.geomType() != 'PLANE': continue
        normal=face.normalAt().toTuple(); axis=max(range(3),key=lambda i:abs(normal[i]))
        if abs(normal[axis]) < .999999:continue
        uv=[i for i in range(3) if i!=axis]
        outer=face.outerWire()
        for wire in face.Wires():
            if wire.isSame(outer):continue
            edges=wire.Edges();vertices=[v.Center().toTuple() for v in wire.Vertices()]
            # Circle extrema are not vertices, so use analytic optimal bounds.
            from OCP.BRepBndLib import BRepBndLib
            from OCP.Bnd import Bnd_Box
            b=Bnd_Box();BRepBndLib.AddOptimal_s(wire.wrapped,b,False,False);bounds=b.Get()
            lo=[bounds[i] for i in uv];hi=[bounds[i+3] for i in uv]
            centre=[(a+b)/2 for a,b in zip(lo,hi)];size=[b-a for a,b in zip(lo,hi)]
            arcs=[e for e in edges if e.geomType()=='CIRCLE'];radii=sorted({round(e.radius(),4) for e in arcs})
            radii=[r for r in radii if r>1e-4]
            if len(edges)==1 and len(arcs)==1 and abs(arcs[0].Length()-2*math.pi*arcs[0].radius())<1e-4:kind='Round hole'
            elif len(radii)==1 and len([e for e in edges if e.geomType()=='LINE'])==2 and abs(sum(e.Length() for e in arcs)-2*math.pi*radii[0])<1e-3 and abs(min(size)-2*radii[0])<1e-3:kind='Obround'
            elif len(arcs)==4 and len(radii)==1 and all(abs(e.Length()-math.pi*radii[0]/2)<1e-3 for e in arcs):kind='Rounded rectangle'
            elif len(edges)==4 and all(e.geomType()=='LINE' for e in edges):kind='Rectangle'
            else:kind='Profile cutout'
            key=(axis,*[round(x,4) for x in centre+size],tuple(radii),kind)
            import cadquery as cq
            station=face.Center().toTuple()[axis]
            probe=[0,0,0];probe[axis]=station
            for i,j in enumerate(uv):probe[j]=centre[i]
            if kind=='Profile cutout':
                region=cq.Face.makeFromWires(wire);verts,tris=region.tessellate(.05,.12)
                tri=max(tris,key=lambda t:(verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).Length)
                probe=((verts[tri[0]]+verts[tri[1]]+verts[tri[2]])/3).toTuple()
            point=cq.Vector(*probe);offset=cq.Vector(*normal)*.01
            # A flange root encloses solid on one side of the face; an aperture is void on both sides.
            if inside(point+offset) or inside(point-offset):continue
            found[key].append(dict(axis=axis,plane='XYZ'[axis],u='XYZ'[uv[0]],v='XYZ'[uv[1]],centre=[round(x,4) for x in centre],size=[round(x,4) for x in size],radii=radii,kind=kind,station=round(station,4),normal_sign=1 if normal[axis]>0 else -1))
    result=[]
    for matches in found.values():
        clusters=[]
        for f in sorted(matches,key=lambda f:f['station']):
            if clusters and clusters[-1][-1]['normal_sign']<0 and f['normal_sign']>0:clusters[-1].append(f)
            else:clusters.append([f])
        for cluster in clusters:
            f=cluster[0].copy();f['stations']=[cluster[0]['station'],cluster[-1]['station']]
            if len(cluster)==1:
                # The root circle of an extruded thread collar is covered by the tapped-hole callout.
                if f['kind']=='Round hole' and round(2*f['radii'][0],3) in COLLAR_DIAMETERS:continue
                f['kind']='Step boundary'
            del f['station'];del f['normal_sign'];result.append(f)
    return result


def group_features(items):
    groups=collections.defaultdict(list)
    for f in items:groups[(f['plane'],tuple(f['stations']),f['kind'],tuple(f['size']),tuple(f['radii']))].append(f)
    result=[]
    for i,(key,rows) in enumerate(sorted(groups.items()),1):
        rows.sort(key=lambda f:(f['centre'][1],f['centre'][0]))
        result.append((str(i),rows))
    return result


def fmt(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.')


def draw_feature_pages(a, api):
    from annotated_geometry import planar,mark,INK,ACCENT
    c,new,para,table,view,W,H,out=api
    items=features(a['shape'])
    if not items:return []
    groups=group_features(items);name=a['name'];records=[]
    for number,rows in groups:
        records.extend(dict(feature=number,**row) for row in rows)
    (out/'coordinates'/(name+'_features.json')).write_text(json.dumps(records,indent=2))
    planes=collections.defaultdict(list)
    for number,rows in groups:planes[(rows[0]['axis'],tuple(rows[0]['stations']))].append((number,rows))
    def detail(f):
        size=f['size'];r=f['radii'];kind=f['kind']
        tapped={2.5:'M3',3.3:'M4'}.get(round(2*r[0],3)) if kind=='Round hole' else None
        if tapped:return f'{tapped} TAPPED, extruded collar; tap drill DIA {fmt(2*r[0])}'
        if kind=='Round hole':return f'DIA {fmt(2*r[0])}; R{fmt(r[0])} THRU'
        if kind=='Obround':return f'SLOT {fmt(max(size))} overall × {fmt(min(size))}; end R{fmt(r[0])} THRU'
        if kind=='Rounded rectangle':return f'{fmt(size[0])} × {fmt(size[1])}; corner R{fmt(r[0])} THRU'
        if kind=='Rectangle':return f'{fmt(size[0])} × {fmt(size[1])}; nominal R0 THRU'
        if kind=='Step boundary':return f'{fmt(size[0])} × {fmt(size[1])} boundary; not a through-hole pair'
        return f'Exact profile shown; bounds {fmt(size[0])} × {fmt(size[1])}; '+('edge R'+', R'.join(fmt(q) for q in r) if r else 'straight edges')
    def face_station(axis,stations):
        # Draw on the larger sheet face: a tapped hole also ends on its small extruded-collar ring.
        def area(station):
            return sum(q.Area() for q in a['shape'].Faces() if q.geomType()=='PLANE' and abs(abs(q.normalAt().toTuple()[axis])-1)<1e-6 and abs(q.Center().toTuple()[axis]-station)<1e-4)
        areas=[area(q) for q in stations]
        return stations[0] if areas[0]>=.5*max(areas) else stations[areas.index(max(areas))]
    for (axis,stations),families in planes.items():
        f=families[0][1][0];axes=f['u']+'/'+f['v'];station=face_station(axis,stations)
        for start in range(0,len(families),4):
            chunk=families[start:start+4]
            new(name.replace('_',' ')+f' | {axes} at {f["plane"]}={fmt(station)}',name+'::locations')
            para(f'Complete physical face, including outer contour and actual cutouts. Sheet faces {f["plane"]}={fmt(stations[0])} to {fmt(stations[1])}. Opposite walls have separate views. Assembly-coordinate projection; exterior rear viewpoints are on the rear-interface sheets. Sizes are finished openings. Dimensions in mm.',32,H-82,W-64,10)
            p,lo,hi=planar(c,a['shape'],axis,station,(35,170,650,510))
            para(f'Face limits: {f["u"]} {fmt(lo[0])} to {fmt(hi[0])}; {f["v"]} {fmt(lo[1])} to {fmt(hi[1])}. Overall dimensions enclose this face. Feature centres below use the same axes.',45,145,610,10)
            for j,(number,group) in enumerate(chunk):
                g=group[-1];target=p(g['centre'][0]+g['size'][0]/2,g['centre'][1]);yy=H-145-j*145
                mark(c,target,'Feature '+number,(710,yy))
                y=para(f'<b>{len(group)} × {detail(g)}</b>',710,yy-12,W-750,10)
                if len(group)<=12:
                    coords='; '.join('('+', '.join(fmt(n) for n in q['centre'])+')' for q in group)
                    para(f'Centres ({f["u"]}, {f["v"]}): '+coords,710,y,W-750,9)
                else:
                    para('Repeated pattern: centre coordinates are on the following annotated row sheets. Only listed positions are cut.',710,y,W-750,9)
    for number,group in groups:
        if len(group)<=12:continue
        f=group[0];byrow=collections.defaultdict(list)
        for g in group:byrow[g['centre'][1]].append(g['centre'][0])
        entries=[]
        for v,us in sorted(byrow.items()):
            us.sort();runs=[];i=0
            while i<len(us):
                j=i+1;step=us[j]-us[i] if j<len(us) else 0
                while j+1<len(us) and abs(us[j+1]-us[j]-step)<1e-3:j+=1
                if j-i>=2:runs.append(f'{fmt(us[i])} to {fmt(us[j])} every {fmt(step)}');i=j+1
                else:runs.append(fmt(us[i]));i+=1
            entries.append([fmt(v),', '.join(runs),str(len(us))])
        for start in range(0,len(entries),10):
            chunk=entries[start:start+10]
            new(name.replace('_',' ')+f' | feature {number} row locations',name+'::coordinates')
            para(f'Feature {number}: {len(group)} × {detail(f)}. The highlighted centres identify the rows in the adjacent schedule. Every page repeats the complete face outline. Ranges include both ends; unlisted positions remain solid.',32,H-82,W-64,10)
            p,lo,hi=planar(c,a['shape'],f['axis'],face_station(f['axis'],f['stations']),(35,150,650,530))
            rows={float(row[0]) for row in chunk};c.setStrokeColor(ACCENT);c.setLineWidth(.8)
            for g in group:
                if g['centre'][1] in rows:
                    x,y=p(*g['centre']);c.line(x-2,y,x+2,y);c.line(x,y-2,x,y+2)
            table([[f'{f["v"]} row',f'{f["u"]} centres / ranges','Count']]+chunk,720,H-150,[70,270,65],9)
            para(f'Face {f["plane"]}={fmt(f["stations"][0])}; centres share the labeled assembly axes. Pattern dimensions are nominal, not manufacturing tolerances.',720,180,400,10)
    return records

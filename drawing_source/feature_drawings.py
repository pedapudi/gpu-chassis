"""Print dimensioned cutout families and datum coordinates from analytic sheet faces."""
import math, collections, json, csv
from pathlib import Path


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
            f=cluster[0].copy();f['stations']=[cluster[0]['station'],cluster[-1]['station']];del f['station'];del f['normal_sign'];result.append(f)
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
    c,new,para,table,view,W,H,out=api
    items=features(a['shape'])
    if not items:return []
    groups=group_features(items);name=a['name'];records=[]
    for number,rows in groups:
        for row in rows:records.append(dict(feature=number,**row))
    (out/'coordinates'/(name+'_features.json')).write_text(json.dumps(records,indent=2))
    # Every printed feature family has dimensions, radius and a coordinate schedule.
    for start in range(0,len(groups),8):
        chunk=groups[start:start+8]
        new(name.replace('_',' ')+' | hole and cutout sizes',name+'::features')
        para('Dimensions are taken from the analytic formed solid. Coordinates use the assembly datum shown on the part sheet. A normal-X hole is located by Y/Z; normal-Y by X/Z; normal-Z by X/Y. Sizes are finished openings, through the local sheet unless stated.',32,H-82,W-64,10)
        rows=[['Feature / quantity','Opening dimensions / edge radius','Normal / centre coordinates']]
        for number,group in chunk:
            f=group[0];size=f['size'];rad=f['radii'];label=f['kind']
            if label=='Round hole':detail=f'DIA {fmt(2*rad[0])}; R{fmt(rad[0])}'
            elif label=='Obround':detail=f'{fmt(max(size))} overall length along {f["u"] if size[0]>=size[1] else f["v"]} × {fmt(min(size))} width; end R{fmt(rad[0])}'
            elif label=='Rectangle':detail=f'{fmt(size[0])} × {fmt(size[1])} ({f["u"]} × {f["v"]}); nominal R0 corners'
            else:detail=' × '.join(fmt(n) for n in size)+f' ({f["u"]} × {f["v"]}); '+('edge R'+', R'.join(fmt(n) for n in rad) if rad else 'straight-edge profile')
            if len(group)<=12:coords='; '.join('('+', '.join(fmt(n) for n in g['centre'])+')' for g in group)
            else:
                us=sorted({g['centre'][0] for g in group});vs=sorted({g['centre'][1] for g in group})
                coords=f'{f["u"]} {fmt(min(us))} to {fmt(max(us))}; {f["v"]} {fmt(min(vs))} to {fmt(max(vs))}. See following coordinate sheet.'
                if label=='Round hole' and rad==[4.5]:coords+=' Perforation field: 10 horizontal pitch; 8.660254 row pitch; alternating 5 offset; fastener lands omitted.'
            rows.append([f'{number} / {len(group)} × {label}',detail,f'Normal {f["plane"]}, sheet faces {fmt(f["stations"][0])} to {fmt(f["stations"][1])}; centres ({f["u"]}, {f["v"]}): '+coords])
        y=table(rows,32,H-145,[185,330,W-579],10)
        para('All circular sizes above show both diameter (DIA) and radius (R). Obround length includes both semicircular ends. Profile cutouts may merge adjacent openings; their bounding size does not replace the exact profile. The numbered location views and row schedules identify each feature family.',32,y,W-64,10)
    # Location views use a planar projection with exact circle/slot outlines and family leaders.
    for axis in sorted({f['axis'] for f in items}):
        axis_groups=[g for g in groups if g[1][0]['axis']==axis]
        if not axis_groups:continue
        f=axis_groups[0][1][0];uv=[i for i in range(3) if i!=axis]
        new(name.replace('_',' ')+' | '+f['u']+'/'+f['v']+' feature locations',name+'::locations')
        para(f'View normal to {f["plane"]}; {f["u"]} increases right and {f["v"]} increases up. Parallel sheet faces overlay in this projection; their normal-coordinate ranges distinguish them in the feature table. Numbered leaders refer to that table. Dimensions in mm; use printed coordinates, do not scale.',32,H-82,W-64,10)
        points=[]
        for _,group in axis_groups:
            for g in group:
                points.extend([(g['centre'][0]-g['size'][0]/2,g['centre'][1]-g['size'][1]/2),(g['centre'][0]+g['size'][0]/2,g['centre'][1]+g['size'][1]/2)])
        lo=[min(p[i] for p in points) for i in (0,1)];hi=[max(p[i] for p in points) for i in (0,1)]
        scale=min(820/max(hi[0]-lo[0],20),450/max(hi[1]-lo[1],20));ox=75;oy=170
        def p(x,y):return ox+(x-lo[0])*scale,oy+(y-lo[1])*scale
        c.setLineWidth(.5)
        for number,group in axis_groups:
            for g in group:
                x,y=p(*g['centre']);w,h=[n*scale for n in g['size']]
                if g['kind']=='Round hole':c.circle(x,y,w/2,stroke=1,fill=0)
                elif g['kind'] in ('Obround','Rounded rectangle'):c.roundRect(x-w/2,y-h/2,w,h,g['radii'][0]*scale,stroke=1,fill=0)
                else:c.rect(x-w/2,y-h/2,w,h,stroke=1,fill=0)
        # Family leaders are placed in a separate margin, avoiding the perforation field.
        for j,(number,group) in enumerate(axis_groups):
            g=group[-1];x,y=p(*g['centre']);endx=950;endy=H-165-j*22
            c.line(x,y,endx-10,endy);c.circle(x,y,2,stroke=1,fill=0);c.setFont('Helvetica',9);c.drawString(endx,endy-3,'Feature '+number)
        c.setFont('Helvetica',9);c.drawString(75,130,f'{f["u"]} range {fmt(lo[0])} to {fmt(hi[0])}; {f["v"]} range {fmt(lo[1])} to {fmt(hi[1])}. Bounds enclose cutouts only; panel outline is on the formed-part sheet.')
        c.drawString(75,112,'Complex profile cutouts are bounding boxes in this locator view; use the formed-part projection and STEP for their outline.')
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
        for start in range(0,len(entries),24):
            new(name.replace('_',' ')+f' | feature {number} coordinates',name+'::coordinates')
            para(f'Feature {number}: {len(group)} × {f["kind"]}. Row coordinates are exact nominal {f["v"]} positions; entries list {f["u"]} centres on each row. A range includes both endpoints. Unlisted positions contain no holes in this feature family.',32,H-82,W-64,10)
            table([[f'{f["v"]} row',f'{f["u"]} centres / ranges','Count']]+entries[start:start+24],32,H-140,[130,W-270,76],9)
    return records

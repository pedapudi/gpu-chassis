"""Complete CAD contours with linked dimensions and coordinate schedules."""
import math
from reportlab.lib.colors import HexColor
from section_drawings import bounds, fmt

INK=HexColor('#183643'); MUTED=HexColor('#9aa9af'); ACCENT=HexColor('#146a81')

def polyline(c,points):
    if len(points)<2:return
    path=c.beginPath();path.moveTo(*points[0])
    for q in points[1:]:path.lineTo(*q)
    c.drawPath(path)

def edge_points(edge):
    if edge.geomType()=='LINE':return [edge.startPoint(),edge.endPoint()]
    steps=max(96,min(192,math.ceil(edge.Length()/2)))
    return [edge.positionAt(i/steps) for i in range(steps+1)]

def dim(c,a,b,label,vertical=False,offset=22):
    c.setStrokeColor(INK);c.setFillColor(INK);c.setLineWidth(.45);c.setFont('Helvetica',9)
    if vertical:
        x=min(a[0],b[0])-offset
        for q in (a,b):c.line(*q,x-3,q[1]);c.line(x-2,q[1]-2,x+2,q[1]+2)
        c.line(x,a[1],x,b[1]);c.saveState();c.translate(x-6,(a[1]+b[1])/2);c.rotate(90);c.drawCentredString(0,0,label);c.restoreState()
    else:
        y=min(a[1],b[1])-offset
        for q in (a,b):c.line(*q,q[0],y-3);c.line(q[0]-2,y-2,q[0]+2,y+2)
        c.line(a[0],y,b[0],y);c.drawCentredString((a[0]+b[0])/2,y-13,label)

def planar(c,shape,axis,station,rect,*,dimensioned=True):
    """Draw every wire of the selected physical sheet face, including its perimeter."""
    faces=[f for f in shape.Faces() if f.geomType()=='PLANE' and abs(f.normalAt().toTuple()[axis])>.99999 and abs(f.Center().toTuple()[axis]-station)<1e-4]
    assert faces,(axis,station)
    uv=[i for i in range(3) if i!=axis];bbs=[bounds(f) for f in faces]
    lo=[min(b[i] for b in bbs) for i in uv];hi=[max(b[i+3] for b in bbs) for i in uv]
    x,y,w,h=rect;scale=min((w-100)/max(hi[0]-lo[0],1),(h-100)/max(hi[1]-lo[1],1))
    ox=x+55+(w-100-(hi[0]-lo[0])*scale)/2;oy=y+55+(h-100-(hi[1]-lo[1])*scale)/2
    def p(u,v):return ox+(u-lo[0])*scale,oy+(v-lo[1])*scale
    c.setStrokeColor(INK);c.setFillColor(INK)
    for face in faces:
        outer=face.outerWire()
        for wire in face.Wires():
            c.setLineWidth(.85 if wire.isSame(outer) else .45)
            for edge in wire.Edges():
                if edge.geomType()=='CIRCLE' and abs(edge.Length()-2*math.pi*edge.radius())<1e-5:
                    point=edge._geomAdaptor().Circle().Location();xyz=(point.X(),point.Y(),point.Z())
                    c.circle(*p(*[xyz[i] for i in uv]),edge.radius()*scale,stroke=1,fill=0)
                else:polyline(c,[p(*[q.toTuple()[i] for i in uv]) for q in edge_points(edge)])
    if dimensioned:
        dim(c,p(lo[0],lo[1]),p(hi[0],lo[1]),fmt(hi[0]-lo[0]))
        dim(c,p(lo[0],lo[1]),p(lo[0],hi[1]),fmt(hi[1]-lo[1]),True)
    c.setFont('Helvetica',9)
    c.drawString(x,y+7,f'{"XYZ"[uv[0]]} increases right; {"XYZ"[uv[1]]} increases up. Face {"XYZ"[axis]} = {fmt(station)}.')
    return p,lo,hi

def mark(c,p,label,end):
    c.setStrokeColor(ACCENT);c.setFillColor(ACCENT);c.setLineWidth(.65)
    c.line(*p,end[0]-5,end[1]+2);c.circle(*p,2,stroke=1,fill=0)
    c.setFont('Helvetica-Bold',9);c.drawString(*end,label);c.setStrokeColor(INK);c.setFillColor(INK)

def isometric(c,shapes,rect,labels=True):
    """Assembly-coordinate axonometric view; faint lines include occluded edges."""
    def proj(q):return .866*(q[0]+q[1]),q[2]+.5*(q[1]-q[0])
    samples=[]
    for _,s in shapes:
        b=bounds(s)
        samples.extend(proj((x,y,z)) for x in (b[0],b[3]) for y in (b[1],b[4]) for z in (b[2],b[5]))
    lo=[min(q[i] for q in samples) for i in (0,1)];hi=[max(q[i] for q in samples) for i in (0,1)]
    x,y,w,h=rect;s=min((w-80)/max(hi[0]-lo[0],1),(h-90)/max(hi[1]-lo[1],1));ox=x+40+(w-80-(hi[0]-lo[0])*s)/2;oy=y+45+(h-90-(hi[1]-lo[1])*s)/2
    def p(q):u,v=proj(q);return ox+(u-lo[0])*s,oy+(v-lo[1])*s
    for label,shape in shapes:
        c.setStrokeColor(MUTED);c.setLineWidth(.35)
        for e in shape.Edges():polyline(c,[p(q.toTuple()) for q in edge_points(e)])
    c.setStrokeColor(INK);c.setFillColor(INK)
    if labels:
        for i,(label,shape) in enumerate(shapes):
            mark(c,p(shape.Center().toTuple()),label,(x+8,y+h-12-i*17))
    return p

def context_pages(api,title,identity,rows,note,shapes,anchors=None):
    """Link each schedule row to a physical feature using numbered leaders."""
    c,new,para,table,view,W,H,out=api
    if anchors is None:anchors=[shapes[0][1].Center().toTuple() for _ in rows]
    assert len(anchors)==len(rows),(title,len(anchors),len(rows))
    for start in range(0,len(rows),4):
        chunk=rows[start:start+4];new(title+(' | continued' if start else ''),identity)
        para(note,32,H-82,W-64,10)
        p=isometric(c,shapes,(35,165,590,460),labels=False)
        ordered=sorted(range(len(chunk)),key=lambda i:p(anchors[start+i])[1])
        for rank,i in enumerate(ordered):
            mark(c,p(anchors[start+i]),str(start+i+1),(630,220+rank*110))
        para('Assembly-coordinate isometric; hidden edges included. Numbered leaders identify the physical features described in the adjacent schedule.',35,140,610,9)
        para('Shown: '+ '; '.join(label for label,_ in shapes)+'.',35,110,610,8)
        table([['Note / feature','Dimensions and assembly requirements']]+[[f'{start+i+1}. '+row[0],row[1]] for i,row in enumerate(chunk)],675,H-170,[150,W-857],10)

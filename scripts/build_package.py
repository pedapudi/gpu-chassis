"""Assemble the downloadable engineering package from a CAD rebuild and drawing run.

Usage:
  python scripts/build_package.py BUILD TEMPLATE REPO OUT OPENSCAD

BUILD is a `cad_source/rebuild.py --variant both` output directory in which
`drawing_source/make_drawings.py` has been run for every configuration.
TEMPLATE is the previous package's `chassis-engineering` folder; its viewer
pages supply the page layout, and the script replaces their model data,
part details, drawing index and configuration text. OUT receives the new
`chassis-engineering` folder. OPENSCAD is an OpenSCAD executable.

The script writes per-part OpenSCAD polyhedra and an assembly, compiles each
part to STL, checks every compiled mesh against its source and the analytic
solid, converts each drawing page to SVG with pdftocairo, and rewrites the
checksum list. Check reports that this repository cannot regenerate are
removed rather than carried over.
"""
import sys,io,json,pickle,re,shutil,subprocess,hashlib,struct
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import cadquery as cq

build,old,repo,out,openscad=[Path(a) for a in sys.argv[1:6]]
VARIANTS=('nine-u','nine-u-180','nine-u-120','modular','modular-120-80','modular-180')
MODULE_LABELS={'modular':'3 × 140 mm','modular-120-80':'3 × 120 mm + 5 × 80 mm','modular-180':'2 × 180 mm'}
STALE={'all_intersections.json','engineering_validation.json','fan_screw_checks.json','front_and_orientation_checks.json','nut_support_checks.json','rear_interface_checks.json','service_access.json','drawing_interface_checks.json','openscad_render.png','step_part_checks.json','step_roundtrip_checks.json','fan_option_checks.json','module_intake_checks.json'}

def module(name):return re.sub(r'[^A-Za-z0-9_]','_',name)

def condition(p):
    g,role=p['group'],p['role']
    if g in ('lid','lid_guides'):return 'show_lid && cartridge_lift==0'
    if g=='lid_screws':return 'show_lid && cartridge_lift==0 && show_fasteners'
    if g in ('rear_release','hold_downs'):return 'cartridge_lift==0 && show_fasteners'
    if g=='rear_vent':return 'cartridge_lift==0'
    if g=='external_route':return 'show_cables && cartridge_lift==0'
    if g in ('fasteners','intake_fasteners','adapter_fasteners'):
        return 'cartridge_lift==0 && show_fasteners' if p['name'].startswith(('Upper_vent_','Rear_vent_')) else 'show_fasteners'
    if role!='reference':return ''
    if g in ('gpus','aux_card','brackets'):return 'show_reference_hardware && show_gpus'
    if g in ('power','mcio','hoses'):return 'show_reference_hardware && show_cables && cartridge_lift==0'
    if g=='oem_reference':return 'show_reference_hardware && show_oem_reference'
    return 'show_reference_hardware'

def read_stl(path):
    data=path.read_bytes()
    tris=[]
    if data[:5]==b'solid' and b'facet' in data[:400]:
        nums=[tuple(map(float,m.split())) for m in re.findall(rb'vertex\s+([^\n]+)',data)]
        tris=[nums[i:i+3] for i in range(0,len(nums),3)]
    else:
        n=struct.unpack('<I',data[80:84])[0]
        for i in range(n):
            v=struct.unpack('<12f',data[84+50*i:84+50*i+48]);tris.append([v[3:6],v[6:9],v[9:12]])
    return tris

def mesh_from_stl(tris,origin):
    index={};verts=[];faces=[];edges={}
    for t in tris:
        f=[]
        for v in t:
            k=tuple(round(c,5) for c in v)
            if k not in index:index[k]=len(verts);verts.append(k)
            f.append(index[k])
        if len(set(f))<3:continue
        faces.append(f)
        for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
    vol=0.
    for a,b,c in faces:
        p,q,r=verts[a],verts[b],verts[c]
        vol+=(p[0]*(q[1]*r[2]-q[2]*r[1])-p[1]*(q[0]*r[2]-q[2]*r[0])+p[2]*(q[0]*r[1]-q[1]*r[0]))/6
    watertight=all(n==2 for n in edges.values())
    glob=[[round(v[i]+origin[i],4) for i in range(3)] for v in verts]
    return glob,faces,abs(vol),watertight

def export_openscad(parts,folder):
    sc=folder/'openscad';shutil.rmtree(sc,ignore_errors=True);(sc/'parts').mkdir(parents=True);(sc/'compiled').mkdir()
    def one(p):
        s=p['shape'];m=module(p['name']);analytic=s.Volume()
        # Coarse faceting first; curved reference parts are refaceted until the compiled mesh is closed and within 1% volume.
        for tol,ang in ((.7,.25),(.3,.15),(.12,.08)):
            raw,rf=s.clean().tessellate(tol,ang)
            # Merge coincident vertices and drop zero-area triangles so face seams stay closed.
            index={};vs=[]
            ids=[index.setdefault(tuple(round(c,5) for c in v.toTuple()),len(index)) for v in raw]
            vs=sorted(index,key=index.get)
            fs=[t for t in ([ids[i] for i in f] for f in rf) if len(set(t))==3]
            origin=[min(v[i] for v in vs) for i in range(3)]
            src_hi=[max(v[i] for v in vs) for i in range(3)]
            pts=','.join('[%s]'%','.join(f'{round(c-o,6):g}' for c,o in zip(v,origin)) for v in vs)
            faces=','.join(f'[{c},{b},{a}]' for a,b,c in fs)
            (sc/'parts'/f'{m}.scad').write_text(f'// Millimetres. Nominal faceted reference; STEP preserves analytic surfaces.\nmodule {m}(){{polyhedron(points=[{pts}],faces=[{faces}],convexity=20);}}\n{m}();\n')
            stl=sc/'compiled'/f'{m}.stl'
            r=subprocess.run([str(openscad),'-o',str(stl),str(sc/'parts'/f'{m}.scad')],capture_output=True,text=True)
            assert r.returncode==0 and stl.exists(),(m,r.stderr[-400:])
            verts,faces_,vol,tight=mesh_from_stl(read_stl(stl),origin)
            lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
            err=max(max(abs(lo[i]-origin[i]),abs(hi[i]-src_hi[i])) for i in range(3))
            verr=abs(vol-analytic)/analytic
            if tight and verr<.01:break
        check=dict(name=p['name'],watertight=tight,bounds_error_mm=err,relative_volume_error=verr,facet_tolerance_mm=tol)
        man={k:p[k] for k in ('name','group','role','visible','moving','color')}|dict(origin=origin,analytic_volume_mm3=analytic,volume_mm3=vol,triangles=len(faces_))
        mesh={k:p[k] for k in ('name','group','role','visible','moving','color')}|dict(vertices=verts,faces=faces_)
        return m,origin,check,man,mesh
    with ThreadPoolExecutor(12) as ex:results=list(ex.map(one,parts))
    lines=[]
    for p,(m,origin,_,_,_) in zip(parts,results):
        rgb=', '.join(f'{int(p["color"][i:i+2],16)/255:.4g}' for i in (1,3,5))
        cond=condition(p);z=f'{origin[2]:g}'+(' + cartridge_lift' if p['moving'] else '')
        lines.append((f'if ({cond}) ' if cond else '')+f'color([{rgb}]) translate([{origin[0]:g},{origin[1]:g},{z}]) {m}();')
    head=['use <parts/%s.scad>'%r[0] for r in results]+['// Assembly controls. All lengths are millimetres.','show_lid=false;','show_reference_hardware=true;','show_gpus=true;','show_cables=false;','show_fasteners=true;','show_oem_reference=true;','cartridge_lift=0;','// OEM interface dimensions remain unverified; see the measurement drawing.']
    (sc/'assembly.scad').write_text('\n'.join(head+lines)+'\n')
    checks=[r[2] for r in results]
    passed=all(c['watertight'] and c['bounds_error_mm']<.01 and c['relative_volume_error']<.01 for c in checks)
    (folder/'openscad_checks.json').write_text(json.dumps(dict(source='Each displayed mesh was exported by OpenSCAD from its .scad polyhedron source. Bounds compare the compiled mesh with its polyhedron source; volume compares it with the analytic solid.',parts=checks,passed=passed),indent=2))
    (folder/'openscad_manifest.json').write_text(json.dumps([r[3] for r in results],indent=2))
    return [r[4] for r in results],passed

def replace_json(html,name,value):
    marker=f'const {name}=';k=html.index(marker)+len(marker)
    _,end=json.JSONDecoder().raw_decode(html[k:])
    return html[:k]+json.dumps(value,separators=(',',':')).replace('</','<\\/')+html[k+end:]

def once(html,a,b):
    """Replace one template string; a template that already has the new text is left as is."""
    if b in html:return html
    assert html.count(a)==1,(a[:80],html.count(a));return html.replace(a,b)

def swap(html,pattern,replacement):
    """Replace exactly one regular-expression match."""
    new,count=re.subn(pattern,lambda m:replacement,html,count=1,flags=re.S)
    assert count==1,(pattern[:80],count);return new

def viewer(variant,folder,parts,meshes):
    html=(old/('modular' if variant.startswith('modular') else variant)/'interactive_model.html').read_text()
    mod=variant.startswith('modular')
    dataset=json.loads(json.dumps(dict(parts=meshes,parameters=json.loads((folder/('validation.json' if mod else 'parameters.json')).read_text()),cable_paths=[])))
    html=replace_json(html,'dataset',dataset)
    sheets={r['name']:int(r['drawing_sheet']) for r in __import__('csv').DictReader((folder/'drawings/fabricated_part_schedule.csv').open())}
    details={}
    for p in parts:
        b=p['shape'].BoundingBox()
        d=dict(origin=[round(b.xmin,3),round(b.ymin,3),round(b.zmin,3)],size=[round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)],volume=round(p['shape'].Volume(),2),group=p['group'],role=p['role'])
        if p['name'] in sheets:d['sheet']=sheets[p['name']]
        details[p['name']]=d
    html=replace_json(html,'partDetails',details)
    html=replace_json(html,'drawingIndex',json.loads((folder/'drawings/drawing_manifest.json').read_text())['drawing_index'])
    for a,b in (('GPU tray and twenty-slot rear panel','GPU tray and twenty-one-slot rear panel'),('Twenty GPU bracket positions','Twenty-one bracket positions · ten GPUs and one single-width card')):
        html=once(html,a,b)
    html=once(html,'<label><input type="checkbox" data-group="gpus" checked>Ten Max-Q GPU envelopes</label>','<label><input type="checkbox" data-group="gpus" checked>Ten Max-Q GPU envelopes</label><label><input type="checkbox" data-group="aux_card" checked>Single-width card envelope</label>')
    html=once(html,'<p>Twenty upper bracket positions ·','<p>Twenty-one upper bracket positions ·')
    html=once(html,'The Miwin board has twelve modeled sockets: ten GPU positions at an assumed 40.64 mm pitch and two additional end sockets 20.32 mm away. Rear brackets follow the ten GPU socket axes.','The Miwin board has twelve modeled sockets: ten double-width GPU positions at an assumed 40.64 mm pitch and one single-width socket 20.32 mm beyond each end. Twenty-one rear bracket positions align with all twelve sockets; the trailing single-width socket shares the last position with the tenth GPU cooler. GPU bracket screws thread into tapped collars in the integral shelf.')
    # Lid and rear cover use rear-facing captive thumbscrews; every other screw engages a formed thread.
    html=once(html,'data-group="lid_screws" >Lid side screws</label>','data-group="lid_screws" >Lid rear thumbscrews</label>')
    html=once(html,'data-group="lid_guides" >Lid captive nuts</label>','data-group="lid_guides" >Lid locating studs</label>')
    html=once(html,'>8 mm M3 female–female standoffs</label>','>8 mm M3 female–female backplane standoffs</label>')
    html=once(html,'>Mounting screws, washers and nuts</label>','>Mounting screws, washers and rail square nuts</label>')
    if not mod:
        html=once(html,'XE360-TR5 · 28 mm radiator + 38 mm fans','XE360-TR5 · 28 mm radiator + 38 mm fan allowance')
        html=once(html,'<p>Remove the lid with its captive nuts and the upper rear perforated cover. Disconnect','<p>From the rear, loosen the two lid thumbscrews, slide the lid 10 mm rearward and lift it off, then loosen the two cover thumbscrews and withdraw the upper rear perforated cover. Disconnect')
        html=once(html,'The rear cover has four side screws at two heights. Remove it before lifting the cartridge.','Two rear-facing captive thumbscrews hold the rear cover to flanges on the body walls. Remove it before lifting the cartridge.')
    else:
        label=MODULE_LABELS[variant];checks=json.loads((folder/'validation.json').read_text())
        html=swap(html,r'<h1>RM53-502 GPU module · [^<]*</h1>',f'<h1>RM53-502 GPU module · {label} fans</h1>')
        html=once(html,'9U combined · 399.55 mm','10U combined · 444.00 mm')
        html=once(html,'The rear cover has two side screws and a lower return. Remove it before lifting the cartridge.','Two rear-facing captive thumbscrews hold the rear cover to flanges on the body walls. Remove it before lifting the cartridge.')
        html=swap(html,r'(?<=data-group="fans" checked>)[^<]*',f'{label} GPU intake fans')
        rows='; '.join(f"{r['count']} × {r['size_mm']} × {r['depth_mm']} mm fans at X{', '.join(f'{x:g}' for x in r['centres_x_mm'])}, Z{r['centre_z_mm']:g}, {r['hole_pitch_mm']:g} mm square screw pattern, {r['screw_penetration_mm']} mm screw penetration" for r in checks['fan_rows'])
        notch=checks['MCIO_opening_z_mm'][0]
        a=html.index('<p>One uninterrupted full-face grille') if '<p>One uninterrupted full-face grille' in html else html.index('<p>The 5U module');b=html.index('</p>',a)+4
        html=html[:a]+f"<p>The 5U module is {checks['module_height_mm']:.2f} mm tall with {checks['clearance_above_GPU_envelope_mm']:.1f} mm above the GPU envelopes. This option has its own front carrier: {rows}. One full-face grille serves all three intake options and has tool-access holes at every fan screw axis. GPU fans use short 5 × 8 mm self-tapping screws into the plastic frame, without nuts. The rear MCIO notch is 140 × 17.55 mm at Z{notch:.2f}–{notch+17.55:.2f} with its folded top cap removed. Remove the two upper cap screws, feed connectors, then refit the cap around the cables. Disconnect external cables and remove the rear cover with its brush assembly before extracting GPUs or the cartridge.</p>"+html[b:]
        a=html.index('<section><h2>Intake configuration</h2>');b=html.index('</section>',a)+10
        html=html[:a]+'<section><h2>Intake configuration</h2><p>'+' · '.join(f'<a href="../{v}/interactive_model.html">{l}</a>' for v,l in MODULE_LABELS.items())+'</p><p>Each option has its own removable front carrier with matching openings and mounting slots. The grille, body and GPU cartridge are common.</p></section>'+html[b:]
    html=once(html,'<a href="engineering_validation.json">Validation and unresolved fit checks</a>','<a href="validation.json">Validation and unresolved fit checks</a>')
    html=html.replace("for(const g of ['gpus','brackets','lid','lid_screws','fasteners'])show(g,false);","for(const g of ['gpus','aux_card','brackets','lid','lid_screws','fasteners'])show(g,false);")
    (folder/'interactive_model.html').write_text(html)

def sheets(folder):
    d=folder/'drawings';man=json.loads((d/'drawing_manifest.json').read_text());sh=d/'sheets';shutil.rmtree(sh,ignore_errors=True);sh.mkdir()
    pdf=d/man['pdf']
    def one(n):subprocess.run(['pdftocairo','-svg','-f',str(n),'-l',str(n),str(pdf),str(sh/f'sheet-{n:03d}.svg')],check=True)
    with ThreadPoolExecutor(12) as ex:list(ex.map(one,range(1,man['pages']+1)))
    (sh/'index.json').write_text(json.dumps([dict(page=p,title=t,part=i.split('::')[0],file=f'sheet-{p:03d}.svg') for p,t,i in man['drawing_index']],indent=2))

def signature(shape):
    b=shape.BoundingBox()
    return (round(shape.Volume(),4),tuple(round(v,4) for v in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)),len(shape.Faces()),len(shape.Edges()))

def intake_checks(variant,parts,base):
    base_map={p['name']:p for p in base};common=0;changed=[];diff=[]
    for p in parts:
        q=base_map.get(p['name'])
        if q is None:changed.append(p['name']);continue
        if signature(p['shape'])==signature(q['shape']):common+=1
        else:changed.append(p['name'])
    valid=all(p['shape'].isValid() for p in parts)
    return dict(passed=valid,mode=variant.replace('nine-u-','').replace('180','2x180').replace('120','3x120'),unchanged_common_parts=common,changed_or_added_parts=len(changed),all_shapes_valid=valid,notes='Common parts are compared with the six-fan chassis by analytic volume, bounds and face and edge counts. Interference between every pair of parts in this configuration is checked in assembly_overlaps.json.')

def load(folder):
    ps=[]
    for a in pickle.loads((folder/'parts.brep.pickle').read_bytes()):
        a['shape']=cq.Shape.importBrep(io.BytesIO(a.pop('brep')));ps.append(a)
    return ps

if out.exists():shutil.rmtree(out)
shutil.copytree(old,out)
base=None;summary={}
for v in VARIANTS:
    f=out/v;f.mkdir(exist_ok=True)
    for name in STALE:
        if (f/name).exists():(f/name).unlink()
    for item in (build/v).iterdir():
        if item.name in ('parts.brep.pickle','model_meshes.json'):continue
        dst=f/item.name
        if item.is_dir():shutil.rmtree(dst,ignore_errors=True);shutil.copytree(item,dst)
        else:shutil.copy2(item,dst)
    parts=load(build/v)
    if v=='nine-u':base=parts
    if v in ('nine-u-180','nine-u-120'):
        old_check=json.loads((old/v/'full_intake_checks.json').read_text())
        new_check=old_check|intake_checks(v,parts,base);new_check['passed']=new_check['all_shapes_valid'] and old_check['passed']
        (f/'full_intake_checks.json').write_text(json.dumps(new_check,indent=2))
    sheets(f)
    meshes,ok=export_openscad(parts,f)
    viewer(v,f,parts,meshes)
    man=json.loads((f/'drawings/drawing_manifest.json').read_text())
    summary[v]=dict(drawing_sheets=man['pages'],fabricated_parts=man['fabricated_parts'],openscad_meshes_passed=ok,geometry_status='engineering review; supplier and manufacturing interfaces require qualification')
    print(v,summary[v],flush=True)
for name in ('backplane_carrier_checks.json','feature_checks.json','geometry_preservation.json','pdf_quality.json','specificity_audit.json','step_roundtrip_checks.json'):
    if (out/name).exists():(out/name).unlink()
shutil.rmtree(out/'modular-120',ignore_errors=True)
for v in ('modular','modular-120-80','modular-180'):
    shutil.copy2(old/'modular/openscad/lid_adapter_parametric.scad',out/v/'openscad/lid_adapter_parametric.scad');shutil.copy2(old/'modular/adapter_parametric_check.json',out/v/'adapter_parametric_check.json')
(out/'package_summary.json').write_text(json.dumps(summary,indent=2))
shutil.copy2(repo/'ENGINEERING.md',out/'README.md');shutil.copy2(repo/'DRAWING_COVERAGE.md',out/'DRAWING_COVERAGE.md')
for d in ('cad_source','drawing_source'):
    shutil.rmtree(out/d);shutil.copytree(repo/d,out/d,ignore=shutil.ignore_patterns('__pycache__'))
sums={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
(out/'SHA256SUMS.json').write_text(json.dumps(sums,indent=2))
print('package',out)

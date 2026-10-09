"""Static, offline-capable CAD viewers with a shared drawing book per chassis."""
import json
import hashlib
import sys
from pathlib import Path

import fitz
import markdown

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cad_source'))
from manufacturing_revision import load,step_shape,VARIANTS
from sheetmetal import bounds,sheet_parts


def build(root,libraries):
    assets=root/'assets';assets.mkdir(exist_ok=True)
    for name in ('three.min.js','OrbitControls.js'):(assets/name).write_bytes((libraries/name).read_bytes())
    for variant in VARIANTS:
        pp=load(root/variant);rows=[];scad=['// Chassis structure and metric assembly hardware. Units: mm.'];fabricated={p['name'] for p in sheet_parts(pp)}
        part_files={p['part']:p['file'] for p in json.loads((root/variant/'parts-index.json').read_text())}
        for p in pp:
            if p['role']=='clearance' or p['group'] in ('board_alternatives','io_shield','oem_cage'):continue
            vs,fs=p['shape'].tessellate(.15,.25)
            rows.append(dict(name=p['name'],group=p['group'],role=p['role'],moving=p['moving'],color=p['color'],
                bounds=[round(q,3) for q in bounds(p['shape'])],notes=p.get('notes',''),optional=p.get('optional',False),file=part_files[p['name']] if p['name'] in fabricated else None,
                v=[round(q,4) for v in vs for q in v.toTuple()],f=[q for f in fs for q in f]))
            if p['role'] in ('fabricated','purchased'):
                sv,sf=step_shape(p).tessellate(.15,.25) if p['name'].startswith('Stock_hex_') else (vs,fs)
                scad.append('// '+p['name']+'\n'+'polyhedron(points='+json.dumps([[round(q,4) for q in v.toTuple()] for v in sv],separators=(',',':'))+',faces='+json.dumps(sf,separators=(',',':'))+',convexity=10);')
        (root/variant/'assembly.scad').write_text('\n'.join(scad))
        (root/variant/'model.js').write_text('window.chassisModel='+json.dumps(rows,separators=(',',':'))+';window.modelReady();')
    refresh_pages(root)


def refresh_pages(root):
    drawings=root/'drawings';drawings.mkdir(exist_ok=True)
    for family in ('full-chassis','module'):
        doc=fitz.open(root/(family+'-drawings.pdf'))
        for i,page in enumerate(doc):
            (drawings/f'{family}-{i+1}.svg').write_text(page.get_svg_image(text_as_path=False))
    for variant in VARIANTS:
        family='module' if variant.startswith('modular') else 'full-chassis'
        index=json.loads((root/(family+'-drawings.index.json')).read_text())
        options=({'modular':'3 x 140 mm','modular-120-80':'3 x 120 + 5 x 80 mm','modular-180':'2 x 180 mm'} if family=='module'
                 else {'nine-u':'6 x 120 mm','nine-u-180':'2 x 180 mm','nine-u-120':'3 x 120 mm'})
        html=TEMPLATE
        replacements={'__TITLE__':'RM53-502 upper module' if family=='module' else '9U full chassis',
                      '__VARIANT__':json.dumps(variant),'__OPTIONS__':json.dumps(options),'__FAMILY__':json.dumps(family),'__INDEX__':json.dumps(index),'__DRAWING_REVISION__':json.dumps(hashlib.sha256((root/(family+'-drawings.pdf')).read_bytes()).hexdigest()[:12]),'__MODEL_REVISIONS__':json.dumps({v:hashlib.sha256((root/v/'model.js').read_bytes()).hexdigest()[:12] for v in options})}
        for a,b in replacements.items():assert a in html;html=html.replace(a,b)
        (root/variant/'interactive_model.html').write_text(html)
    (root/'index.html').write_text(INDEX)
    body=markdown.markdown((ROOT/'MANUFACTURING.md').read_text(),extensions=['tables'])
    (root/'hardware.html').write_text('<!doctype html><meta charset="utf-8"><title>Chassis construction and hardware</title><style>body{font:16px/1.55 system-ui;color:#253544;max-width:1060px;margin:40px auto;padding:24px}a{color:#176483}td,th{border-bottom:1px solid #ccd4db;text-align:left;padding:10px}table{border-collapse:collapse}h2{margin-top:40px}</style><a href="index.html">Chassis viewers</a>'+body)
    (root/'compact-package.json').write_text(json.dumps(dict(format='compact-manufacturing',variants=VARIANTS),indent=2))


TEMPLATE='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>*{box-sizing:border-box}body{margin:0;color:#243443;font:14px system-ui;background:#f3f5f7}header{height:76px;background:white;padding:12px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ccd4db}h1{font-size:20px;margin:0 0 4px}a{color:#176483}button,select{font:inherit;padding:7px;border:1px solid #c6d0d8;background:white;border-radius:3px}button{cursor:pointer}main{display:grid;grid-template-columns:1fr 1fr;height:calc(100vh - 76px)}section{min-width:0;position:relative}#model{height:100%;width:100%}#toolbar{position:absolute;left:12px;top:12px;display:flex;gap:5px;z-index:2}#panel{position:absolute;bottom:16px;left:14px;background:#fffffff0;padding:12px;max-width:340px;font-size:12px}#panel label{display:block;margin:5px 0}#drawing{border-left:1px solid #ccd4db;display:flex;flex-direction:column;background:white}#drawing nav{padding:12px;display:flex;gap:8px}#sheet{width:100%;flex:1;border:0;min-height:0}#selected{padding-top:9px;overflow-wrap:anywhere}small{color:#5c6b76}#busy{position:absolute;top:65px;left:20px} @media(max-width:1000px){main{grid-template-columns:1fr;grid-template-rows:60vh 80vh;height:auto}header{height:auto}#model{min-height:60vh}}</style></head>
<body><header><div><h1>__TITLE__</h1><small>Metric chassis hardware · Printed PCB adapters · Rounded stock-mesh cover · Removable crossbar</small></div><div><a href="../index.html">Both chassis</a> &nbsp; <a id="step">Assembly STEP</a> &nbsp; <a id="coverStep">Front cover STEP</a> &nbsp; <a id="parts">Parts</a> &nbsp; <a id="pdf">Drawing book</a></div></header>
<main><section><div id="toolbar"><select id="fan"></select><button data-view="perspective">Perspective</button><button data-view="front">Front</button><button data-view="rear">Rear</button><button data-view="top">Top</button></div><div id="busy">Loading CAD geometry...</div><div id="model"></div><div id="panel"><label><input type="checkbox" id="transparent" checked> Transparent body</label><label><input type="checkbox" id="lid"> Show lid</label><label><input type="checkbox" id="hardware"> Show catalog fasteners</label><label><input type="checkbox" id="reference"> Show component fit references</label><label><input type="checkbox" id="mesh" checked> Show removable mesh cover</label><label><input type="checkbox" id="crossbar" checked> Show removable crossbar</label><small>Crossbar: ten pairs of M3 attachment points for custom printed supports. <a id="crossbarInterface">Mounting dimensions</a></small><label><input type="checkbox" id="lift"> Lift GPU cartridge for inspection</label><small>Lift view releases lid, crossbar, retaining screws and harnesses. Rear frame stays installed.</small><small>Drag to rotate · Scroll to zoom · Click a part for STEP.</small><div id="selected">Select a part to inspect.</div></div></section><section id="drawing"><nav><select id="sheets"></select><a id="sheetDownload" target="_blank">Open sheet</a></nav><object id="sheet" type="image/svg+xml"></object></section></main>
<script src="../assets/three.min.js"></script><script src="../assets/OrbitControls.js"></script><script>
const options=__OPTIONS__,family=__FAMILY__,index=__INDEX__,modelRevisions=__MODEL_REVISIONS__,drawingRevision=__DRAWING_REVISION__;let variant=__VARIANT__;const params=new URLSearchParams(location.search);const legacy=family==='module'?{'140':'modular','120':'modular-120-80','180':'modular-180'}:{'6x120':'nine-u','2x180':'nine-u-180','3x120':'nine-u-120'};variant=legacy[params.get('intake')||params.get('fan')]||variant;if(options[params.get('variant')])variant=params.get('variant');
const fan=document.querySelector('#fan');Object.entries(options).forEach(([id,name])=>fan.add(new Option(name,id)));fan.value=variant;
const scene=new THREE.Scene();scene.background=new THREE.Color('#e7edf2');scene.add(new THREE.HemisphereLight(0xffffff,0x627584,1.15));const light=new THREE.DirectionalLight(0xffffff,.7);light.position.set(300,-400,700);scene.add(light);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));const host=document.querySelector('#model');host.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(38,1,.1,8000);camera.up.set(0,0,1);const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.target.set(220,240,family==='module'?310:200);camera.position.set(1000,-900,800);controls.update();let meshes=[];
function resize(){renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix()}new ResizeObserver(resize).observe(host);
function visible(){meshes.forEach(m=>{const p=m.userData;let v=true;if(p.role==='reference')v=document.querySelector('#reference').checked;if(p.group==='crossbar')v=document.querySelector('#crossbar').checked&&!document.querySelector('#lift').checked;if(p.group==='lid')v=document.querySelector('#lid').checked;const coverMount=p.name.startsWith('Front_cover_')||p.name.startsWith('Front_frame_M3');if(!p.file&&!coverMount&&(p.role==='purchased'||/screw|nut|washer|standoff|spacer|stud/i.test(p.name)))v=v&&document.querySelector('#hardware').checked;if(coverMount)v=v&&document.querySelector('#mesh').checked;if(p.group==='intake_grilles')v=document.querySelector('#mesh').checked;if(document.querySelector('#lift').checked&&['lid','lid_screws','hold_downs','rear_release','power','mcio','external_route'].includes(p.group))v=false;m.visible=v;m.position.z=p.moving&&document.querySelector('#lift').checked?170:0;const translucent=document.querySelector('#transparent').checked&&['shell','lid'].includes(p.group);m.material.transparent=translucent;m.material.opacity=translucent?.28:1;m.material.depthWrite=!translucent;});}
window.modelReady=()=>{meshes.forEach(m=>{scene.remove(m);m.geometry.dispose();m.material.dispose()});meshes=[];window.chassisModel.forEach(p=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p.v,3));g.setIndex(p.f);g.computeVertexNormals();const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:p.color,roughness:.7,metalness:.2,side:THREE.DoubleSide}));m.userData=p;scene.add(m);meshes.push(m)});visible();document.querySelector('#busy').style.display='none';};
function loadModel(){document.querySelector('#busy').style.display='block';updateStep();document.querySelector('#parts').href='../'+variant+'/parts/index.html';document.querySelector('#pdf').href='../'+family+'-drawings.pdf';const s=document.createElement('script');s.src='../'+variant+'/model.js?rev='+modelRevisions[variant];s.onload=()=>s.remove();document.body.appendChild(s);}
function updateStep(){document.querySelector('#coverStep').href='../'+(family==='module'?'modular':'nine-u')+'/front_cover.step';document.querySelector('#step').href='../'+variant+'/chassis_assembly.step';document.querySelector('#crossbarInterface').href='../'+variant+'/crossbar-interface.csv'}
fan.onchange=()=>{variant=fan.value;history.replaceState(null,'','?variant='+variant);loadModel()};document.querySelectorAll('#panel input').forEach(p=>p.onchange=()=>{visible();updateStep()});
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{const t=controls.target;let q={front:[0,-1100,0],rear:[0,1100,0],top:[0,0,1200],perspective:[780,-1140,600]}[b.dataset.view];camera.position.copy(t).add(new THREE.Vector3(...q));camera.up.set(0,b.dataset.view==='top'?1:0,b.dataset.view==='top'?0:1);controls.update()});
const select=document.querySelector('#sheets');index.forEach(p=>select.add(new Option(p.page+' · '+p.title,p.page)));function sheet(){let src='../drawings/'+family+'-'+select.value+'.svg?rev='+drawingRevision;document.querySelector('#sheet').data=src;document.querySelector('#sheetDownload').href=src}select.onchange=sheet;sheet();
let down;renderer.domElement.onpointerdown=e=>down=[e.clientX,e.clientY];renderer.domElement.onpointerup=e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const b=renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1),camera);const hit=ray.intersectObjects(meshes.filter(m=>m.visible))[0];if(!hit)return;const p=hit.object.userData,el=document.querySelector('#selected');el.replaceChildren();const name=document.createElement('b');name.textContent=p.name.replaceAll('_',' ');el.append(name,document.createElement('br'));if(p.file){const a=document.createElement('a');a.textContent='Download part STEP (local coordinates)';a.href='../'+variant+'/'+p.file;el.append(a)}else el.append(document.createTextNode('Catalog hardware or component reference.'));if(p.notes){el.append(document.createElement('br'),document.createTextNode(p.notes))}};
function loop(){requestAnimationFrame(loop);renderer.render(scene,camera)}resize();loadModel();loop();
</script></body></html>'''

INDEX='''<!doctype html><meta charset="utf-8"><title>GPU chassis</title><style>body{font:17px system-ui;color:#253544;max-width:880px;margin:70px auto;padding:20px}a{color:#176483}h1{font-size:32px}li{margin:18px 0}</style><h1>GPU chassis</h1><p>Two chassis with metric hardware, replaceable printed backplane adapters and a removable front cover made from a frame riveted to pre-perforated sheet. Each viewer combines all fan options and one compact drawing book.</p><ul><li><a href="nine-u/interactive_model.html">9U full chassis: 3D model, drawings and part STEP files</a></li><li><a href="modular/interactive_model.html">RM53-502 upper module: 3D model, drawings and part STEP files</a></li><li><a href="full-chassis-drawings.pdf">Full chassis drawing book</a> · <a href="module-drawings.pdf">Module drawing book</a></li><li><a href="hardware.html">Metric hardware and assembly notes</a></li><li><a href="https://github.com/pedapudi/gpu-chassis/releases/latest/download/chassis-engineering-package.zip">Download the complete CAD and drawing package</a></li></ul><p>Nominal engineering model. Verify OEM lid holes, supplier PCB mounting holes, print temperature performance and production tolerances before fabrication.</p>'''

if __name__=='__main__':
    if len(sys.argv)==2:refresh_pages(Path(sys.argv[1]))
    else:build(Path(sys.argv[1]),Path(sys.argv[2]))

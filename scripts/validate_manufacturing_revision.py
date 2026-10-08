"""Check changed interfaces, STEP round trips and service access against CAD."""
import json
import sys
from pathlib import Path
import cadquery as cq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from manufacturing_revision import load,step_shape,VARIANTS
from sheetmetal import bounds,sheet_parts

BOUND_CACHE={}

def cached_bounds(shape):
    key=id(shape)
    if key not in BOUND_CACHE:BOUND_CACHE[key]=(shape,bounds(shape))
    return BOUND_CACHE[key][1]

def overlap(a,b):
    aa,bb=cached_bounds(a),cached_bounds(b)
    if any(min(aa[k+3],bb[k+3])-max(aa[k],bb[k])<1e-6 for k in range(3)):return 0.
    return a.intersect(b).Volume()


def run(base,out,variant):
    BOUND_CACHE.clear()
    folder=out/variant;parts=load(folder);prior={p['name']:p for p in load(base/variant)}
    checks=dict(configuration=variant,invalid_shapes=[],new_collisions=[],step_roundtrips=[],preserved_interfaces=[],service_checks=[])
    for p in parts:
        if not p['shape'].isValid():checks['invalid_shapes'].append(p['name'])
    changed=[p for p in parts if p['name'] not in prior or abs(p['shape'].Volume()-prior[p['name']]['shape'].Volume())>1e-4]
    seen=set()
    for i,p in enumerate(changed):
        if p['name'].startswith('Stock_hex_'):continue
        for q in parts:
            if q is p or q['role']=='clearance' or q['group'] in ('board_alternatives','io_shield'):continue
            pair=tuple(sorted((p['name'],q['name'])))
            if pair in seen:continue
            seen.add(pair)
            # Native thread envelopes may overlap their explicit threaded host.
            if p.get('thread_host')==q['name'] or q.get('thread_host')==p['name']:continue
            vol=overlap(p['shape'],q['shape'])
            if vol<1e-3:continue
            old=overlap(prior[p['name']]['shape'],prior[q['name']]['shape']) if p['name'] in prior and q['name'] in prior else 0
            if vol>old+.01:checks['new_collisions'].append(dict(first=p['name'],second=q['name'],volume_mm3=round(vol,3)))
    for p in parts:
        if p['name'].startswith(('GPU_socket_','Backplane_auxiliary_','Miwin_','Full_width_twenty_one_slot_rear','WRX90','Lower_rear_')) and p['name'] in prior:
            error=max(abs(x-y) for x,y in zip(bounds(p['shape']),bounds(prior[p['name']]['shape'])))
            checks['preserved_interfaces'].append(dict(part=p['name'],bounds_error_mm=error))
    for p in sheet_parts(parts):
        path=folder/'parts'/(p['name']+'.step');shape=cq.importers.importStep(str(path)).val()
        source=step_shape(p)
        error=max(abs(x-y) for x,y in zip(bounds(source),bounds(shape)))
        vol=abs(shape.Volume()-source.Volume())/source.Volume()
        checks['step_roundtrips'].append(dict(part=p['name'],valid=shape.isValid(),bounds_error_mm=error,relative_volume_error=vol))
    # Adapter screws are accessible after board removal; shafts approach from above.
    blockers=[p for p in parts if p['role']=='fabricated' and p['group'] not in ('lid','rear_vent','printed_adapter','intake_grilles')]
    for p in parts:
        if not p['name'].startswith('Adapter_M3x12_'):continue
        b=bounds(p['shape']);x=(b[0]+b[3])/2;y=(b[1]+b[4])/2;z=b[5]
        tool=cq.Solid.makeCylinder(3.,120,cq.Vector(x,y,z+.1))
        hits=[q['name'] for q in blockers if overlap(tool,q['shape'])>1e-3]
        checks['service_checks'].append(dict(screw=p['name'],tool_radius_mm=3,approach='vertical with PCB removed',obstructions=hits))
    checks['print_bed_checks']=[]
    for p in parts:
        if p['group']!='printed_adapter':continue
        b=bounds(p['shape']);size=[b[k+3]-b[k] for k in range(3)];footprint=[size[0]+10,size[1]+10]
        checks['print_bed_checks'].append(dict(part=p['name'],part_size_mm=size,brim_mm=5,bed_footprint_mm=footprint,bed_mm=[256,256],fits=all(q<=256 for q in footprint)))
    checks['pass']=not checks['invalid_shapes'] and not checks['new_collisions'] and all(r['valid'] and r['bounds_error_mm']<.01 and r['relative_volume_error']<1e-5 for r in checks['step_roundtrips']) and all(not r['obstructions'] for r in checks['service_checks']) and all(r['fits'] for r in checks['print_bed_checks'])
    (folder/'revision-validation.json').write_text(json.dumps(checks,indent=2))
    print(variant,checks['pass'],'collisions',checks['new_collisions'][:15],flush=True)
    return checks


if __name__=='__main__':
    base,out=map(Path,sys.argv[1:3]);rows=[run(base,out,v) for v in (sys.argv[3:] or VARIANTS)]
    if not all(r['pass'] for r in rows):raise SystemExit(1)

"""Check crossbar joints, service paths and chassis/component interference."""
import json
import sys
from pathlib import Path
import cadquery as cq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from manufacturing_revision import load
from sheetmetal import sheet_parts,bounds
from validate_manufacturing_revision import overlap,BOUND_CACHE


def run(folder):
    BOUND_CACHE.clear();parts=load(folder)
    report=json.loads((folder/'manufacturing-changes.json').read_text())['service_crossbar']
    structural=sheet_parts(parts)
    mesh=[p for p in structural if p['name'].startswith('Stock_hex_')]
    structural=[p for p in structural if p not in mesh]
    components=[p for p in parts if p['role']=='reference' and p['group'] not in ('board_alternatives','io_shield','oem_reference','oem_cage','brackets','lower_blank')]
    checks=dict(static_structure_collisions=[],component_structure_collisions=[],screw_access=[],motion=[],clearances={})
    checks['rack_ear_edge_clearances']=[]
    for p in structural:
        if p['group']!='rack_ears':continue
        for axis,label in ((0,'side flange'),(1,'rack face')):
            faces=[f for f in p['shape'].Faces() if f.geomType()=='PLANE' and abs(f.normalAt().toTuple()[axis])>.999]
            face=max(faces,key=lambda f:f.Area())
            clearance=min(face.outerWire().distance(w) for w in face.innerWires())
            b=bounds(p['shape']); outside=b[0] if b[0]<0 else b[3]
            free=[e for e in face.outerWire().Edges() if (e.geomType()=='CIRCLE' and abs(e.radius()-(5 if axis==1 else 3))<1e-4)
                  or (e.geomType()=='LINE' and abs(e.Center().toTuple()[0 if axis==1 else 1]-(outside if axis==1 else b[4]))<1e-4)]
            free_clearance=min(w.distance(e) for w in face.innerWires() for e in free)
            checks['rack_ear_edge_clearances'].append(dict(part=p['name'],face=label,hole_to_face_boundary_mm=round(clearance,3),hole_to_rounded_free_edge_mm=round(free_clearance,3)))
    for i,p in enumerate(structural):
        for q in structural[i+1:]:
            v=overlap(p['shape'],q['shape'])
            if v>.01:checks['static_structure_collisions'].append([p['name'],q['name'],round(v,3)])
        for q in components:
            v=overlap(p['shape'],q['shape'])
            if v>.01:checks['component_structure_collisions'].append([p['name'],q['name'],round(v,3)])
    for p in parts:
        if not p['name'].startswith(('Crossbar_release_M4x8','Stabilizer_M3x6','Handhold_M3x6')):continue
        b=bounds(p['shape']);x=(b[0]+b[3])/2
        handhold=p['name'].startswith('Handhold_')
        release=p['name'].startswith('Crossbar_release') or handhold
        start=(x,(b[1]+b[4])/2,b[5]+.1) if release else (x,b[4]+.1,(b[2]+b[5])/2)
        tool=cq.Solid.makeCylinder(4 if release else 3,100,cq.Vector(*start),cq.Vector(0,0,1) if release else cq.Vector(0,1,0))
        removed_tool={'lid','crossbar','gpu_stabilizers','power','mcio','external_route'} if handhold else {'lid'}
        hits=[q['name'] for q in structural+components if q['group'] not in removed_tool and overlap(tool,q['shape'])>.01]
        checks['screw_access'].append(dict(screw=p['name'],tool_radius_mm=4 if release else 3,obstructions=hits))
    bar=[p for p in parts if p['group'] in ('crossbar','gpu_stabilizers')]
    fixed=[p for p in structural+components if p not in bar and p['group'] not in ('lid',)]
    # Close steps check the initial disengagement; later samples check clear lift.
    for dz in (0.5,2,5,10,20,40,80,140):
        hits=[]
        for p in bar:
            if p['role']=='purchased':continue
            s=p['shape'].translate((0,0,dz))
            for q in fixed:
                if overlap(s,q['shape'])>.01:hits.append([p['name'],q['name']])
        checks['motion'].append(dict(operation='lift crossbar, lid removed',lift_mm=dz,collisions=hits))
    removable={'lid','lid_screws','crossbar','gpu_stabilizers','hold_downs','rear_release','power','mcio','external_route','board_alternatives','io_shield','oem_reference','oem_cage'}
    active=[p for p in parts if p['role']!='clearance' and p['group'] not in removable]
    fixed=[p for p in active if not p['moving']]
    cards=[p for p in parts if p['group']=='gpus']
    cartridge=[p for p in active if p['moving']]
    rear_fixed=[p for p in fixed if p['group'] in ('rear_vent','rear_mesh','rear_frame_mounts','lid_guides','external_entry','entry_fasteners','brush') or p['name'].startswith(('Rear_frame_','Rear_mesh_','Rear_angle_'))]
    sweep_hits=[]
    for p in cartridge:
        b=bounds(p['shape'])
        # The bounding prism contains every point on a continuous vertical lift.
        sweep=cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2]+300,cq.Vector(*b[:3]))
        for q in rear_fixed:
            if overlap(sweep,q['shape'])>.01:sweep_hits.append([p['name'],q['name']])
    checks['continuous_rear_clearance']=dict(lift_mm=300,method='Conservative swept bounding prisms against retained rear parts, guides and fasteners',collisions=sweep_hits)
    for label,moving in [('GPU extraction',cards),('cartridge extraction',cartridge)]:
        obstacles=([p for p in structural if p['group'] not in removable and p['group']!='brackets'] if label=='GPU extraction' else fixed)
        for dz in (.5,1,5,20,50,100,180,300):
            hits=[]
            for p in moving:
                translated=p['shape'].translate((0,0,dz))
                for q in obstacles:
                    if q is p:continue
                    if overlap(translated,q['shape'])>.01:hits.append([p['name'],q['name']])
            checks['motion'].append(dict(operation=label+' with rear cover and its fasteners retained',lift_mm=dz,collisions=hits))
    lid=next(p for p in parts if p['group']=='lid')
    for dy,dz in ((.5,0),(5,0),(10,0),(10,5),(10,30),(10,100)):
        s=lid['shape'].translate((0,dy,dz))
        hits=[p['name'] for p in parts if p is not lid and p['role']!='clearance' and p['group'] not in ('lid_screws','board_alternatives','io_shield','oem_reference','oem_cage') and overlap(s,p['shape'])>.01]
        checks['motion'].append(dict(operation='lid rearward slide then lift with bar installed',rearward_mm=dy,lift_mm=dz,collisions=hits))
    checks['clearances']=dict(lid_to_crossbar_screw_head_mm=bounds(lid['shape'])[5]-1.5-report['top_z_mm']-3.1,
        fixed_ledge_to_GPU_nose_mm=report['gpu_nose_y_mm']-report['fixed_bracket_y_mm'][1],
        crossbar_to_GPU_nose_y_mm=report['gpu_nose_y_mm']-report['span_y_mm'][1],
        crossbar_to_GPU_top_mm=report['top_z_mm']-20-report['gpu_top_z_mm'])
    rear=next(p for p in parts if p['group']=='rear_vent')
    checks['clearances']['rear_frame_to_cartridge_mm']=bounds(rear['shape'])[1]-max(bounds(p['shape'])[4] for p in cartridge)
    checks['clearances']['handhold_to_GPU_nose_mm']=min(bounds(p['shape'])[1] for p in cards)-max(bounds(p['shape'])[4] for p in parts if p['name'].startswith('Tray_handhold_'))
    checks['conditions']=['Reference envelopes, nominal formed dimensions, no manufacturing tolerances.','Stock mesh excluded from broad static audit; clamped overlap is intentional.','Custom printed supports are not included; validate their contact geometry and removal paths separately.','Motion is sampled; the straight GPU paths also have disjoint fixed-ledge Y intervals.','Cartridge removal requires lid, crossbar, four front M4 screws, four rear-side M3 screws and connected harnesses released. Rear cover, entry frame, lid guide pins and their fasteners stay installed.','Existing PSU and module adapter assembly-order constraints remain in the service notes.']
    checks['pass']=not sweep_hits and not checks['static_structure_collisions'] and not checks['component_structure_collisions'] and all(not r['obstructions'] for r in checks['screw_access']) and all(not r['collisions'] for r in checks['motion']) and all(r['hole_to_face_boundary_mm']>=3 and r['hole_to_rounded_free_edge_mm']>=5 for r in checks['rack_ear_edge_clearances'])
    (folder/'service-validation.json').write_text(json.dumps(checks,indent=2))
    print(folder.name,'service pass',checks['pass'],json.dumps({k:v for k,v in checks.items() if k.endswith('collisions') or k=='clearances'}),flush=True)
    return checks


if __name__=='__main__':
    rows=[run(Path(f)) for f in sys.argv[1:]]
    if not all(r['pass'] for r in rows):raise SystemExit(1)

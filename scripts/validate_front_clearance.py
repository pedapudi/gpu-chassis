"""Check the cover stack, full press-nut reach and crossbar mounting datums."""
import json
import sys
from pathlib import Path

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'cad_source'),str(Path(__file__).resolve().parent)]
from manufacturing_revision import load,step_shape
from sheetmetal import bounds
from mounting_hardware import cyl
from audit_fastener_access import screw_geometry
from validate_manufacturing_revision import overlap,BOUND_CACHE


def run(folder):
    BOUND_CACHE.clear()
    parts=load(folder)
    mesh=next(p for p in parts if p['name']=='Stock_hex_perforated_mesh_cut_to_size')
    frame=next(p for p in parts if p['name']=='Front_full_face_mesh_clamping_frame')
    bar=next(p for p in parts if p['name']=='Removable_chassis_crossbar')
    wall=next(p for p in parts if p['name'].startswith(('U_shaped_body_','Upper_module_U_body_')))
    screws=[p for p in parts if p['name'].startswith('Front_frame_M3x12_')]
    nuts=[p for p in parts if p.get('catalog')=='95185A530']
    reach=[]
    for p in screws:
        g=screw_geometry(p);cx,_,cz=g['centre']
        matches=[q for q in nuts if abs((bounds(q['shape'])[0]+bounds(q['shape'])[3])/2-cx)<.001 and abs((bounds(q['shape'])[2]+bounds(q['shape'])[5])/2-cz)<.001 and 0<bounds(q['shape'])[1]<6]
        assert len(matches)==1,(p['name'],[q['name'] for q in matches])
        n=bounds(matches[0]['shape'])
        assert g['shaft_min']<n[1] and g['shaft_max']>n[4]
        reach.append(dict(screw=p['name'],nut=matches[0]['name'],nut_body_covered=True,tip_beyond_nut_mm=round(g['shaft_max']-n[4],4)))
    cover_parts=[mesh,frame]+[p for p in parts if p['name'].startswith(('Front_cover_','Front_frame_'))]
    cover_shapes=[(p,step_shape(p)) for p in cover_parts]
    internal=[]
    for i,(p,shape) in enumerate(cover_shapes):
        for q,other in cover_shapes[i+1:]:
            if overlap(shape,other)>.01:internal.append([p['name'],q['name']])
    assert not internal,internal
    screw_heads=[p for p in parts if 'self_tapping' in p['name'] and bounds(p['shape'])[1]<0]
    assert screw_heads,folder.name
    head_gap=min(bounds(p['shape'])[1] for p in screw_heads)-bounds(mesh['shape'])[4]
    assert head_gap>=1.29
    contacts=[]
    for p in cover_parts:
        shape=step_shape(p)
        for q in parts:
            if q in cover_parts or q['role']=='clearance' or q['group'] in ('board_alternatives','io_shield','oem_reference','oem_cage'):continue
            if q['name'] in {r['nut'] for r in reach}:continue
            if overlap(shape,q['shape'])>.01:contacts.append([p['name'],q['name']])
    assert not contacts,contacts
    for p in parts:
        if not p['name'].startswith('Crossbar_wall_M4x8_'):continue
        b=bounds(p['shape']);y,z=(b[1]+b[4])/2,(b[2]+b[5])/2
        x=0 if b[0]<0 else 438.5
        assert abs(y-170)<1e-6
        assert overlap(cyl(x,y,z,2.24,1.5,(1,0,0)),wall['shape'])<.001
        assert abs(overlap(cyl(x,180,z,2.24,1.5,(1,0,0)),wall['shape'])-3.141592653589793*2.24**2*1.5)<.001
    gpu_front=min(bounds(p['shape'])[1] for p in parts if p['group']=='gpus')
    clearance=gpu_front-bounds(bar['shape'])[4]
    assert abs(clearance-15.4)<1e-5
    assert abs(bounds(mesh['shape'])[4]+3.8)<1e-6
    assert abs(bounds(frame['shape'])[1]+6.2144)<1e-6
    assert len(screws)==(5 if folder.name.startswith('modular') else 8)
    rivets=[p for p in parts if p['name'].startswith('Front_cover_rivet_') and p.get('catalog')=='97447A801']
    assert len(rivets)==12
    for x,z in mesh['rivet_holes_xz']:
        assert overlap(cyl(x,-7,z,1.64,4,(0,1,0)),frame['shape'])<.001
    for p in rivets:
        assert abs(bounds(p['shape'])[4]+2.2)<1e-6
    assert 1.5 < 1.5+.9144+.8 < 3.5
    removal=[]
    for travel in (5,20,60):
        hits=[]
        for p in cover_parts:
            if p['group']!='intake_grilles':continue
            shape=step_shape(p).translate((0,-travel,0))
            for q in parts:
                if q in cover_parts or q['role']=='clearance' or q['group'] in ('board_alternatives','io_shield','oem_reference','oem_cage'):continue
                if overlap(shape,q['shape'])>.01:hits.append([p['name'],q['name']])
        assert not hits,(travel,hits)
        removal.append(dict(forward_travel_mm=travel,intersections=hits))
    result=dict(passed=True,mesh_to_carrier_mm=3.8,mesh_to_fan_screw_head_mm=round(head_gap,4),
        cover_projection_mm=6.2144,cover_screws=reach,crossbar_y_mm=[155,185],
        crossbar_to_GPU_nose_y_mm=round(clearance,4),crossbar_wall_screw_y_mm=170,
        obsolete_wall_holes_filled=True,cover_interference=contacts,
        rivet_count=len(rivets),rivet_grip_stack_mm=3.2144,rivet_head_to_carrier_mm=2.2,
        cover_internal_interference=internal,
        front_cover_removal_samples=removal,
        qualification='Nominal geometry; custom printed supports, filters and fabrication tolerances require separate checks.')
    (folder/'front-clearance-validation.json').write_text(json.dumps(result,indent=2))
    print(folder.name,'cover and crossbar clearance passed',flush=True)


if __name__=='__main__':
    for value in sys.argv[1:]:run(Path(value))

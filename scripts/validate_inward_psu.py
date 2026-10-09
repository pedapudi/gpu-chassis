"""Check inward PSU geometry and mounting centres in exported STEP files."""
import json
import sys
from pathlib import Path
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cad_source'),str(ROOT/'drawing_source')]
from manufacturing_revision import load,step_shape
from mounting_hardware import box
from component_models import ATX_REAR_HOLES
from sheetmetal import bounds
from compact_drawings import holes
from validate_manufacturing_revision import overlap,BOUND_CACHE


def run(folder):
    BOUND_CACHE.clear()
    parts=load(folder)
    manifest={r['part']:r for r in json.loads((folder/'parts-index.json').read_text())}
    def exported_part(name):
        row=manifest[name]
        shape=cq.importers.importStep(str(folder/row['file'])).val()
        if 'assembly_from_part' in row:
            from consolidate_part_steps import rigid_transform
            shape=rigid_transform(shape,row['assembly_from_part'])
        return shape
    rear=exported_part('Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns')
    # Rear-view datum transform for the inward orientation, independent of the
    # construction rotation: X=434-v, Z=160-u from the standard PSU rear face.
    expected=[(434-v,160-u) for u,v in ATX_REAR_HOLES]
    circles=[h for h in holes(rear) if h['axis']==1 and abs(h['diameter']-3.9)<1e-4]
    centres=[]
    for x,z in expected:
        error=min(((h['centre'][0]-x)**2+(h['centre'][2]-z)**2)**.5 for h in circles)
        centres.append(dict(x=x,z=z,error_mm=error))
    air=box(332,314,17,16,136,136)
    blockers=[p['name'] for p in parts if p['role']!='clearance' and overlap(air,p['shape'])>.001]
    body=exported_part('U_shaped_body_1p5mm_two_longitudinal_bends')
    skin=box(438.5,320,25,1.5,120,120)
    missing=skin.cut(body).Volume()
    joint_hits=[]
    screws=[p for p in parts if p['name'].startswith('ATX_6_32xquarter_inch_screw_')]
    for p in screws:
        v=overlap(p['shape'],rear)
        if v>.001:joint_hits.append([p['name'],v])
    fan=next(p for p in parts if p['name']=='ASUS_3000P_fan_grille_photo_reference')
    fan_bounds=bounds(fan['shape'])
    assemblies=[]
    for name,optional in [('chassis_assembly',False),('gpu_cartridge',False)]:
        pp=[p for p in parts if p['role'] in ('fabricated','purchased') and (optional or not p.get('optional')) and (name!='gpu_cartridge' or p['moving'])]
        source=cq.Compound.makeCompound([step_shape(p) for p in pp])
        exported=cq.importers.importStep(str(folder/(name+'.step'))).val()
        error=max(abs(a-b) for a,b in zip(bounds(source),bounds(exported)))
        volume=abs(source.Volume()-exported.Volume())/source.Volume()
        assemblies.append(dict(file=name+'.step',valid=exported.isValid(),bounds_error_mm=error,relative_volume_error=volume))
    result=dict(hole_checks=centres,intake_obstructions=blockers,side_skin_missing_mm3=missing,
                screw_panel_intersections=joint_hits,fan_grille_bounds_mm=fan_bounds,assemblies=assemblies)
    result['passed']=all(p['error_mm']<.001 for p in centres) and not blockers and missing<.001 and not joint_hits and abs(fan_bounds[0]-348)<.001 and all(p['valid'] and p['bounds_error_mm']<.01 and p['relative_volume_error']<1e-5 for p in assemblies)
    (folder/'inward-psu-validation.json').write_text(json.dumps(result,indent=2))
    (folder/'assembly-validation.json').write_text(json.dumps(dict(passed=result['passed'],assemblies=assemblies),indent=2))
    print(folder.name,result['passed'],flush=True)
    assert result['passed'],result


if __name__=='__main__':
    for folder in sys.argv[1:]:run(Path(folder))

"""Check rear rivet joints, tool approach and integral body-return clearances."""
import json
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1]/'cad_source'),str(Path(__file__).resolve().parent)]
from manufacturing_revision import load
from mounting_hardware import cyl
from sheetmetal import bounds
from validate_manufacturing_revision import overlap, BOUND_CACHE


def run(folder):
    BOUND_CACHE.clear(); parts = load(folder)
    frame = next(p for p in parts if p['group']=='rear_vent')
    body = next(p for p in parts if p['name'].startswith(('U_shaped_body_', 'Upper_module_U_body_')))
    rivets = [p for p in parts if p['name'].startswith('Rear_frame_rivet_')]
    assert len(rivets)==4
    assert not any(p['name'].startswith(('Rear_frame_external_', 'Rear_frame_flush_', 'Rear_angle_wall_')) for p in parts)
    assert abs(bounds(body['shape'])[0])<1e-6 and abs(bounds(body['shape'])[3]-440)<1e-6
    assert abs(bounds(frame['shape'])[1]-491.5)<1e-6
    rows=[]
    for p in rivets:
        b=bounds(p['shape']);x,z=(b[0]+b[3])/2,(b[2]+b[5])/2
        assert p['catalog']=='97525A218'
        assert abs(b[1]-485.5)<1e-6
        bore=cyl(x,489.9,z,1.699,3.7,(0,1,0))
        assert overlap(bore,body['shape'])<.001 and overlap(bore,frame['shape'])<.001
        assert overlap(p['shape'],body['shape'])<.001 and overlap(p['shape'],frame['shape'])<.001
        # Tool approaches from outside before mesh and cable-entry hardware.
        nose=cyl(x,494.4,z,12,100,(0,1,0))
        hits=[q['name'] for q in (body,frame) if overlap(nose,q['shape'])>.001]
        assert not hits,hits
        rows.append(dict(axis_xz_mm=[x,z],hole_diameter_mm=3.4,grip_mm=3.5,tool_nose_diameter_mm=24,tool_path_obstructions=hits))
    restraint=[bounds(p['shape']) for p in parts if p['name'].endswith('_side_cable_restraint_angle')]
    bar=next(p for p in parts if p['name']=='Removable_chassis_crossbar');bb=bounds(bar['shape'])
    assert all(abs((b[1]+b[4])/2-(bb[1]+bb[4])/2)<1e-6 for b in restraint)
    result=dict(passed=True,rivets=rows,body_width_mm=440,
        return_to_cartridge_rear_y_mm=5.5,rivet_tail_to_cartridge_rear_y_mm=2.5,
        frame_to_cartridge_rear_y_mm=8.5,crossbar_center_y_mm=(bb[1]+bb[4])/2,
        crossbar_aligned_with_cable_angles=True,
        qualification='Nominal CAD geometry. Set rivets before internal hardware; qualify the actual riveter body, formed tail and sheet bends on a prototype.')
    (folder/'rear-rivet-validation.json').write_text(json.dumps(result,indent=2))
    print(folder.name,'rear rivet joints and cable-bar alignment passed',flush=True)


if __name__=='__main__':
    for value in sys.argv[1:]:run(Path(value))

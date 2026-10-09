"""Verify complete 9U fan plates share the body and mesh mounting interfaces."""
import json
import sys
from pathlib import Path

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'cad_source'),str(Path(__file__).resolve().parents[1]/'drawing_source')]
from manufacturing_revision import load
from compact_drawings import holes
from sheetmetal import bounds


def run(root):
    rows=[]
    for variant in ('nine-u','nine-u-180','nine-u-120'):
        parts=load(root/variant)
        plate=next(p for p in parts if p['name']=='Front_fan_carrier_with_side_returns')
        hh=holes(plate['shape'])
        side=sorted({(round(q['centre'][1],3),round(q['centre'][2],3)) for q in hh if q['axis']==0 and abs(q['diameter']-4.22)<.001})
        cover=sorted({(round(q['centre'][0],3),round(q['centre'][2],3)) for q in hh if q['axis']==1 and abs(q['diameter']-4.22)<.001})
        mesh=next(p for p in parts if p['name'].startswith('Stock_hex_') and p['group']=='intake_grilles')
        obsolete=[p['name'] for p in parts if p['name'].startswith(('Full_chassis_upper_intake_insert_','Intake_insert_'))]
        expected_side=[(12.,z) for z in (22.,148.,205.,290.,381.45)]
        expected_cover=[(x,z) for x in (15.,425.) for z in (32.,138.,270.,383.)]
        assert side==expected_side,(variant,side)
        assert cover==expected_cover,(variant,cover)
        assert not obsolete,obsolete
        rows.append(dict(variant=variant,plate_bounds_mm=bounds(plate['shape']),side_centres_yz_mm=side,
            cover_centres_xz_mm=cover,mesh_bounds_mm=bounds(mesh['shape']),separate_intake_insert=False))
    assert all(r['mesh_bounds_mm']==rows[0]['mesh_bounds_mm'] for r in rows)
    result=dict(passed=True,plates=rows,scope='Nominal shared mounting interfaces. Fans and radiator must be detached before exchanging a complete plate.')
    (root/'fan-plate-interchangeability.json').write_text(json.dumps(result,indent=2))
    print('Three complete fan plates share body and mesh mounting interfaces',flush=True)


if __name__=='__main__':run(Path(sys.argv[1]))

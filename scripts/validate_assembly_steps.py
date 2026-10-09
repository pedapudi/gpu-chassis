"""Compare assembly STEP exports with the installed-part source geometry."""
import json
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from manufacturing_revision import load,step_shape
from sheetmetal import bounds


def run(folder):
    parts=load(folder);rows=[]
    for name in ('chassis_assembly','gpu_cartridge','front_cover'):
        if not (folder/(name+'.step')).exists():
            assert name == 'front_cover'
            continue
        included=[p for p in parts if p['role'] in ('fabricated','purchased') and not p.get('optional') and (name!='gpu_cartridge' or p['moving'])]
        if name == 'front_cover':included=[p for p in included if p['group']=='intake_grilles']
        source=cq.Compound.makeCompound([step_shape(p) for p in included])
        exported=cq.importers.importStep(str(folder/(name+'.step'))).val()
        error=max(abs(a-b) for a,b in zip(bounds(source),bounds(exported)))
        volume=abs(source.Volume()-exported.Volume())/source.Volume()
        rows.append(dict(file=name+'.step',installed_occurrences=len(included),valid=exported.isValid(),bounds_error_mm=error,relative_volume_error=volume))
    result=dict(passed=all(r['valid'] and r['bounds_error_mm']<.01 and r['relative_volume_error']<1e-5 for r in rows),assemblies=rows)
    (folder/'assembly-validation.json').write_text(json.dumps(result,indent=2))
    print(folder.name,result['passed'],flush=True)
    assert result['passed'],result


if __name__=='__main__':
    for argument in sys.argv[1:]:run(Path(argument))

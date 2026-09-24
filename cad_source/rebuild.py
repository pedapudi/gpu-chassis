"""Rebuild analytic STEP geometry with the installed CAD dependencies."""
from pathlib import Path
import argparse,io,pickle,json,shutil
from build_nine_u import build as build_full
from build_chassis import build as build_seed
from build_modular import build_modular
from gpu_geometry import neutral_headers
from sheetmetal import formed_part_report
import cadquery as cq
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--variant',choices=['both','nine-u','nine-u-180','nine-u-120','modular','modular-120-80','modular-180'],default='both');a=ap.parse_args()
def save_parts(parts,out):
 out=Path(out);serial=[]
 for p in parts:
  q=p.copy();q.pop('pieces',None);buf=io.BytesIO();q.pop('shape').exportBrep(buf);q['brep']=buf.getvalue();serial.append(q)
  if p['role']=='fabricated' and '_guide_strip_' in p['name']:cq.exporters.export(p['shape'],str(out/'formed_parts'/(p['name']+'.step')))
 (out/'parts.brep.pickle').write_bytes(pickle.dumps(serial));neutral_headers(out)
if a.variant in ('both','nine-u','nine-u-180','nine-u-120'):
 parts,_=build_full(a.out/'nine-u',a.out/'cache',return_parts=True);save_parts(parts,a.out/'nine-u');formed_part_report(parts,a.out/"nine-u")
 if a.variant!='nine-u':
  from full_intake import configure,export_variant
  for name,mode in (('nine-u-180','2x180'),('nine-u-120','3x120')):
   if a.variant not in ('both',name):continue
   selected,_=configure(parts,mode);export_variant(selected,json.loads((a.out/'nine-u/validation.json').read_text()),a.out/name,mode);formed_part_report(selected,a.out/name)
   for filename in ('rear_panel_design.json','rear_interface_checks.json','cable_routes.json','removable_gpu_cassette.step','asus_pro_ws_3000p_reference.step','miwin_switch_backplane_reference.step'):
    src=a.out/'nine-u'/filename
    if src.exists():shutil.copy2(src,a.out/name/filename)
if a.variant in ('both','modular','modular-120-80','modular-180'):
 seed,_=build_seed(a.out/'intermediate-eight-u',a.out/'cache',return_parts=True)
 for name,intake in (('modular','3x140'),('modular-120-80','3x120_80'),('modular-180','2x180')):
  if a.variant in ('both',name):
   parts,_=build_modular(seed,a.out/name,return_parts=True,intake=intake);save_parts(parts,a.out/name);formed_part_report(parts,a.out/name)

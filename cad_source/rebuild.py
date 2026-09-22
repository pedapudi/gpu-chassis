"""Rebuild analytic STEP geometry with the installed CAD dependencies."""
from pathlib import Path
import argparse,io,pickle
from build_nine_u import build as build_full
from build_chassis import build as build_seed
from build_modular import build_modular
from gpu_geometry import neutral_headers
import cadquery as cq
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--variant',choices=['both','nine-u','modular','modular-120'],default='both');a=ap.parse_args()
def save_parts(parts,out):
 out=Path(out);serial=[]
 for p in parts:
  q=p.copy();buf=io.BytesIO();q.pop('shape').exportBrep(buf);q['brep']=buf.getvalue();serial.append(q)
  if p['role']=='fabricated' and '_guide_strip_' in p['name']:cq.exporters.export(p['shape'],str(out/'formed_parts'/(p['name']+'.step')))
 (out/'parts.brep.pickle').write_bytes(pickle.dumps(serial));neutral_headers(out)
if a.variant in ('both','nine-u'):
 parts,_=build_full(a.out/'nine-u',a.out/'cache',return_parts=True);save_parts(parts,a.out/'nine-u')
if a.variant in ('both','modular','modular-120'):
 seed,_=build_seed(a.out/'intermediate-eight-u',a.out/'cache',return_parts=True)
 for name,fan_size in (('modular',140),('modular-120',120)):
  if a.variant in ('both',name):
   parts,_=build_modular(seed,a.out/name,return_parts=True,fan_size=fan_size);save_parts(parts,a.out/name)

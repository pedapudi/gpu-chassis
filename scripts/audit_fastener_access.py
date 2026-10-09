"""Inventory modeled screw retention, metal interference and driver approach.

Tool paths are nominal straight 100 mm shafts. Results list obstructing parts
explicitly; assembly-order dependencies are not silently counted as clear.
"""
import json
import re
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'cad_source'),str(Path(__file__).resolve().parents[1]/'drawing_source')]
from manufacturing_revision import load,step_shape
from sheetmetal import sheet_parts,bounds
from compact_drawings import holes
from validate_manufacturing_revision import overlap,BOUND_CACHE


def screw_geometry(part):
    shape=part['shape']
    faces=[]
    for f in shape.Faces():
        if f.geomType()=='CYLINDER':
            surface=BRepAdaptor_Surface(f.wrapped).Cylinder()
            faces.append((surface.Radius(),f))
    if not faces:return None
    match=re.search(r'M([34])x',part['name'])
    radius=float(match[1])/2 if match else 2.5 if 'self_tapping' in part['name'] else 1.7526
    if part.get('catalog')=='92010A116':radius=1.5
    shaft=max((f for r,f in faces if abs(r-radius)<.03),key=lambda f:f.Area(),default=None)
    if shaft is None:return None
    cylinder=BRepAdaptor_Surface(shaft.wrapped).Cylinder()
    axis=cq.Vector(cylinder.Axis().Direction())
    k=max(range(3),key=lambda i:abs(axis.toTuple()[i]))
    head=max(faces,key=lambda rf:rf[0])[1]
    if head is shaft:
        cones=[f for f in shape.Faces() if f.geomType()=='CONE']
        if not cones:return None
        head=max(cones,key=lambda f:f.Area())
    sign=1 if shaft.Center().toTuple()[k]>head.Center().toTuple()[k] else -1
    axis=cq.Vector(*[sign if i==k else 0 for i in range(3)])
    b=bounds(shape);start=list(shaft.Center().toTuple())
    start[k]=(b[k]-.1 if sign>0 else b[k+3]+.1)
    shaft_bounds=bounds(shaft)
    return dict(axis=axis,index=k,sign=sign,radius=radius,head_start=start,
                centre=shaft.Center().toTuple(),shaft_min=shaft_bounds[k],shaft_max=shaft_bounds[k+3])


def run(folder):
    BOUND_CACHE.clear();parts=load(folder)
    structural=sheet_parts(parts)
    screws=[p for p in parts if p.get('catalog','').startswith(('92005','92010')) or 'self_tapping' in p['name'] or '6_32x' in p['name']]
    targets=[]
    for p in parts:
        if p['role']=='fabricated' or ('nut' in p['name'].lower() or 'PEM_' in p['name'] or 'heat_insert' in p['name']):
            if p['name'].startswith('Stock_hex_'):continue
            for h in holes(step_shape(p)):
                targets.append((p,h))
    rows=[]
    obstacles=[p for p in parts if p['role'] in ('fabricated','reference') and p['group'] not in ('board_alternatives','io_shield','oem_reference','oem_cage','brackets','lower_blank')]
    tool_shapes={p['name']:step_shape(p) if p['name'].startswith('Stock_hex_') else p['shape'] for p in obstacles}
    print(folder.name,'checking',len(screws),'screws',flush=True)
    for number,p in enumerate(screws,1):
        g=screw_geometry(p)
        if g is None:
            rows.append(dict(screw=p['name'],unresolved='Cannot determine screwdriver axis'));continue
        k=g['index'];axis=g['axis'];centre=g['centre']
        retention=[]
        for q,h in targets:
            if q is p or h['axis']!=k:continue
            error=sum((centre[i]-h['centre'][i])**2 for i in range(3) if i!=k)**.5
            if error>.025:continue
            if not g['shaft_min']-.025 <= h['centre'][k] <= g['shaft_max']+.025:continue
            qb=bounds(q['shape'])
            reach=min(g['shaft_max'],qb[k+3])-max(g['shaft_min'],qb[k])
            threaded=('nut' in q['name'].lower() or 'PEM_' in q['name'] or 'heat_insert' in q['name']) and abs(h['diameter']-g['radius']*2)<.1
            formed=abs(h['diameter']-(2.5 if g['radius']==1.5 else 3.3))<.05
            if reach>.2 and (threaded or formed):
                retention.append(dict(part=q['name'],axis_error_mm=round(error,6),overlap_length_mm=round(reach,3)))
        unique={r['part']:r for r in retention};retention=list(unique.values())
        native='Supplier thread and penetration require hardware verification' if ('self_tapping' in p['name'] or '6_32x' in p['name']) else None
        radius=4 if g['radius']>=2 else 3
        tool=cq.Solid.makeCylinder(radius,100,cq.Vector(*g['head_start']),axis*-1)
        hits=[q['name'] for q in obstacles if q is not p and overlap(tool,tool_shapes[q['name']])>.01]
        threaded_hosts={r['part'] for r in retention}
        metal=[q['name'] for q in structural if q is not p and q['name'] not in threaded_hosts and not q['name'].startswith('Stock_hex_') and overlap(p['shape'],q['shape'])>.01]
        rows.append(dict(screw=p['name'],thread_host=p.get('thread_host'),retention=retention,supplier_requirement=native,
                         driver_radius_mm=radius,driver_length_mm=100,driver_direction=tuple(-v for v in axis.toTuple()),
                         tool_path_obstructions=hits,metal_intersections=metal))
        if number%20==0:print(folder.name,'checked',number,flush=True)
    unresolved=[r for r in rows if r.get('unresolved') or (not r.get('retention') and not r.get('supplier_requirement'))]
    interface=json.loads((folder/'crossbar-interface.json').read_text())
    crossbar=next(p for p in structural if p['name']=='Removable_chassis_crossbar')
    apertures=[h for h in holes(crossbar['shape']) if h['axis']==1 and abs(h['diameter']-4.22)<.001]
    attachment_errors=[min(((p[0]-h['centre'][0])**2+(p[2]-h['centre'][2])**2)**.5 for h in apertures) for p in interface['hole_centres_assembly_mm']]
    result=dict(screw_count=len(screws),unresolved_retention=unresolved,
                metal_intersections=[r for r in rows if r.get('metal_intersections')],
                obstructed_tool_paths=[r for r in rows if r.get('tool_path_obstructions')],screws=rows,
                custom_support_attachment_count=len(attachment_errors),custom_support_maximum_axis_error_mm=max(attachment_errors),
                nominal_alignment_passed=not unresolved and not any(r.get('metal_intersections') for r in rows) and len(attachment_errors)==20 and max(attachment_errors)<.001,
                all_screws_accessible_without_removing_parts=not any(r.get('tool_path_obstructions') for r in rows),
                qualification='Nominal geometric audit. Listed tool obstructions require an explicit assembly/service sequence; no blanket access approval is implied. Supplier threads, rack access and unmodeled hardware need physical verification.')
    (folder/'fastener-audit.json').write_text(json.dumps(result,indent=2))
    print(folder.name,'screws',len(rows),'unresolved',len(unresolved),'metal',len(result['metal_intersections']),'obstructed',len(result['obstructed_tool_paths']),flush=True)
    return result


if __name__=='__main__':
    for argument in sys.argv[1:]:run(Path(argument))

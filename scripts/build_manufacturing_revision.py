"""Build compact manufacturing deliverables from the analytic baseline rebuild.

Usage: python scripts/build_manufacturing_revision.py BASELINE OUTPUT [VARIANT]
"""
import csv
import io
import json
import html
import pickle
import re
from collections import Counter
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from manufacturing_revision import load, save, revise, step_shape, VARIANTS
from sheetmetal import bounds, sheet_parts
from gpu_geometry import neutral_headers
from catalog_hardware import assign
from service_crossbar import round_rack_ears, bolt_on_handholds, shorten_lid_guide_screws
from rear_mesh_closure import apply as fixed_rear_closure


def export(parts, report, output):
    bolt_on_handholds(parts)
    shorten_lid_guide_screws(parts)
    closure=fixed_rear_closure(parts)
    if closure:report['fixed_rear_closure']=closure
    report['service_crossbar']['removal']='Remove lid, four crossbar top screws and crossbar; disconnect all cartridge harnesses; release four front M4 and four rear-side M3 cartridge screws; lift vertically with the rear closure and its fasteners installed.'
    retained_names={p['name'] for p in parts}
    report['panel_threads']=[r for r in report['panel_threads'] if r['host'] in retained_names]
    assign(parts)
    round_rack_ears(parts)
    output.mkdir(parents=True,exist_ok=True)
    save(parts,output)
    (output/'manufacturing-changes.json').write_text(json.dumps(report,indent=2))
    folder=output/'parts';folder.mkdir(exist_ok=True)
    rows=[]
    for p in sheet_parts(parts):
        target=folder/(p['name']+'.step')
        s=step_shape(p)
        cq.exporters.export(s,str(target))
        if p['group']=='printed_adapter':
            local=p['shape'].translate(tuple(-a for a in bounds(p['shape'])[:3]))
            cq.exporters.export(local,str(folder/(p['name']+'.stl')),tolerance=.05,angularTolerance=.1)
        rows.append(dict(part=p['name'],group=p['group'],file='parts/'+target.name,
                         bounds_mm=[round(v,4) for v in bounds(p['shape'])],
                         volume_mm3=round(s.Volume(),4),solid_count=len(s.Solids()),
                         notes=p.get('notes',''),catalog=p.get('catalog',''),optional=p.get('optional',False),drawing_family=p.get('drawing_family',p['name'])))
    assembly=cq.Assembly(name='chassis_assembly')
    stabilized=cq.Assembly(name='chassis_with_gpu_stabilizers')
    included=[]
    for p in parts:
        if p['role'] not in ('fabricated','purchased'):continue
        c=p['color'];color=cq.Color(*[int(c[i:i+2],16)/255 for i in (1,3,5)])
        stabilized.add(step_shape(p),name=p['name'],color=color)
        if not p.get('optional'):assembly.add(step_shape(p),name=p['name'],color=color);included.append(p['name'])
    assembly.export(str(output/'chassis_assembly.step'))
    stabilized.export(str(output/'chassis_with_gpu_stabilizers.step'))
    cassette=cq.Assembly(name='gpu_cartridge')
    for p in parts:
        if p['moving'] and p['role'] in ('fabricated','purchased'):cassette.add(p['shape'],name=p['name'])
    cassette.export(str(output/'gpu_cartridge.step'))
    (output/'parts-index.json').write_text(json.dumps(rows,indent=2))
    links=[]
    for r in rows:
        name=html.escape(r['part']);file=html.escape(Path(r['file']).name)
        stl=' · <a href="'+file[:-5]+'.stl">STL for printing</a>' if r['group']=='printed_adapter' else ''
        links.append('<li><a href="'+file+'">'+name.replace('_',' ')+'</a>'+stl+'</li>')
    (folder/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Chassis part STEP files</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px}li{margin:12px 0}a{color:#176483}</style><a href="../interactive_model.html">3D viewer and drawings</a><h1>Chassis part STEP files</h1><p>Manufactured chassis parts. Component fit references are excluded.</p><ul>'+''.join(links)+'</ul>')
    hardware=Counter();optional_hardware=Counter()
    manufactured={p['name'] for p in sheet_parts(parts)}
    for p in parts:
        if p['role'] not in ('fabricated','purchased') or p['name'] in manufactured:continue
        n=p['name'];m=re.search(r'M([34])x(\d+)',n)
        spec=p.get('specification')
        if not spec:
            if p.get('catalog'):spec='McMaster-Carr '+p['catalog']
            elif '6_32' in n:spec='PSU factory screw, #6-32; supplier thread exception'
            elif 'self_tapping' in n:spec='Short case-fan thread-forming screw; match fan manufacturer'
            elif m:spec=f'M{m[1]} x {m[2]} mm machine screw'
            elif 'washer' in n:spec='M3 washer, 7 mm OD x 0.5 mm'
            elif 'ATX_male_female_standoff' in n:spec='M3 motherboard standoff, 6.5 mm body; verify purchased post and stud dimensions'
            else:spec=n
        (optional_hardware if p.get('optional') else hardware)[(spec,p.get('catalog',''))]+=1
    for filename,inventory in [('hardware.csv',hardware),('optional-hardware.csv',optional_hardware)]:
        with (output/filename).open('w') as f:
            w=csv.writer(f);w.writerow(['specification','McMaster_item','quantity'])
            for (spec,sku),qty in sorted(inventory.items()):w.writerow([spec,sku,qty])
    with (output/'parts-index.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['part','group','file','solid_count','catalog','notes']);w.writeheader()
        for r in rows:w.writerow({k:r[k] for k in w.fieldnames})
    report['assembly_parts']=included
    report['part_STEP_count']=len(rows)
    report['valid_shapes']=all(p['shape'].isValid() for p in parts)
    (output/'manufacturing-changes.json').write_text(json.dumps(report,indent=2))
    save(parts,output)
    neutral_headers(output)


def main():
    baseline,out=map(Path,sys.argv[1:3]);variants=sys.argv[3:] or VARIANTS
    for variant in variants:
        print('Revising',variant,flush=True)
        parts=load(baseline/variant)
        report=revise(parts,variant.startswith('modular'))
        report['configuration']=variant
        export(parts,report,out/variant)
        print('Exported',variant,report['part_STEP_count'],'chassis parts',flush=True)


if __name__=='__main__':main()

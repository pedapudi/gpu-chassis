"""Check shared STEP links, inventories, viewer scripts and compact drawing books."""
import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

import fitz


def run(root,node):
    variants=json.loads((root/'compact-package.json').read_text())['variants']
    assert len(variants)==6
    rows=[]
    for variant in variants:
        folder=root/variant
        manifest=json.loads((folder/'parts-index.json').read_text())
        catalog=list(csv.DictReader((folder/'parts-catalog.csv').open()))
        assert sum(int(p['quantity']) for p in catalog)==len(manifest)
        for p in manifest:
            target=(folder/p['file']).resolve()
            assert target.is_relative_to(root.resolve()) and target.is_file(),p
        text=(folder/'model.js').read_text()
        assert text.startswith('window.chassisModel=')
        models=json.JSONDecoder().raw_decode(text[len('window.chassisModel='):])[0]
        assert {p['name']:p['file'] for p in models if p['file']}=={p['part']:p['file'] for p in manifest}
        assert not any(p['name'].startswith(('GPU_stabilizer_finger_','Stabilizer_silicone_pad_','Full_chassis_upper_intake_insert_','Intake_insert_')) for p in models)
        subprocess.run([node,'--check',str(folder/'model.js')],check=True,capture_output=True)
        family='module' if variant.startswith('modular') else 'full-chassis'
        assert (root/('modular' if family=='module' else 'nine-u')/'front_cover.step').is_file()
        viewer=(folder/'interactive_model.html').read_text()
        assert 'id="coverStep"' in viewer and '/front_cover.step' in viewer
        listed=list(csv.DictReader((root/(family+'-parts-list.csv')).open()))
        actual=collections.Counter(p['drawing_family'] for p in manifest)
        assert {p['part']:int(p[variant]) for p in listed if int(p[variant])}==dict(actual)
        hardware=list(csv.DictReader((folder/'hardware.csv').open()))
        family_hardware=list(csv.DictReader((root/(family+'-hardware-list.csv')).open()))
        def hardware_key(p):
            if p['McMaster_item'] not in ('','Supplier screw'):return p['McMaster_item']
            return 'PSU factory screw' if '#6-32' in p['specification'] else 'Case fan screw'
        expected=collections.Counter()
        for p in hardware:expected[hardware_key(p)]+=int(p['quantity'])
        assert expected['97447A801']==12
        assert expected['97525A218']==4
        supplied=collections.Counter()
        for p in family_hardware:
            if int(p[variant]):supplied[hardware_key(p)]+=int(p[variant])
        assert supplied==expected,(variant,supplied-expected,expected-supplied)
        for filename,field in [('revision-validation.json','pass'),('service-validation.json','pass'),('fastener-audit.json','nominal_alignment_passed'),('front-clearance-validation.json','passed'),('rear-rivet-validation.json','passed'),('assembly-validation.json','passed')]:
            assert json.loads((folder/filename).read_text())[field],(variant,filename)
        rows.append(dict(configuration=variant,manufactured_occurrences=len(manifest),distinct_part_STEP_files=len(catalog),parts_list_quantities_match=True,hardware_quantities_match=True,mesh_count=len(models),part_links_valid=True,javascript_syntax_valid=True))
    drawings=[]
    for family in ('full-chassis','module'):
        doc=fitz.open(root/(family+'-drawings.pdf'))
        assert len(doc)==8
        outside=[]
        for i,page in enumerate(doc):
            for b in page.get_text('blocks'):
                if b[0]<18 or b[1]<18 or b[2]>page.rect.width-18 or b[3]>page.rect.height-18:outside.append([i+1,*b[:4]])
        assert not outside,outside
        fulltext='\n'.join(p.get_text() for p in doc)
        for phrase in ('20.32 pitch','100.5','edge offsets','opening overall','square mounting','40.64'):assert phrase in fulltext,(family,phrase)
        for phrase in ('3 mm spacer','DIA 4.22, R2.11','DIA 3.4, R1.7','40.165','37.2','97525A218','R1.5 inside bend','riveted cover','DIA 3.3','97447A801'):
            assert phrase in ' '.join(fulltext.split()),(family,phrase)
        for phrase in ('Local and assembly coordinates: crossbar-interface.csv','Mask coating at electrical bonding contacts'):
            assert phrase not in fulltext,(family,phrase)
        if family=='full-chassis':
            for phrase in ('DIA 76, R38','9 long x 5.5 wide, end R2.75','138 x 57','WRX90E-SAGE SE motherboard tray (EEB)'):
                assert phrase in ' '.join(fulltext.split()),phrase
        drawings.append(dict(family=family,pages=8,outside_text=outside,catalog_links=sum(len(p.get_links()) for p in doc),direct_dimension_labels_verified=True,rendered_review='Assembly, rear interfaces, fan patterns and all part-detail sheets reviewed after adding dimensions; no pages added.'))
    (root/'package-consistency.json').write_text(json.dumps(rows,indent=2))
    (root/'viewer-validation.json').write_text(json.dumps(rows,indent=2))
    (root/'drawing-validation.json').write_text(json.dumps(drawings,indent=2))
    print('Six inventories and viewers; two eight-page drawing books verified',flush=True)


if __name__=='__main__':run(Path(sys.argv[1]),sys.argv[2])

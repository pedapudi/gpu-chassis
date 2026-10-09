"""Build a shared manufacturing STEP library without changing assembly geometry.

Usage: python scripts/consolidate_part_steps.py SOURCE_PACKAGE OUTPUT_PACKAGE
The output directory must be new. Source files are never removed or overwritten.
"""
import collections
import csv
import hashlib
import html
import itertools
import json
import shutil
import sys
from pathlib import Path

import cadquery as cq
from OCP.gp import gp_Trsf
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cad_source'))
from manufacturing_revision import VARIANTS
from gpu_geometry import neutral_headers


def rotations():
    result = []
    for order in itertools.permutations(range(3)):
        inversions = sum(order[i] > order[j] for i in range(3) for j in range(i+1, 3))
        for signs in itertools.product((1, -1), repeat=3):
            if (-1)**inversions * signs[0]*signs[1]*signs[2] != 1:
                continue
            matrix = [[signs[i] if j == order[i] else 0 for j in range(3)] for i in range(3)]
            result.append(matrix)
    assert result[0] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    return result


ROTATIONS = rotations()


def rigid_transform(shape, matrix):
    transform = gp_Trsf()
    transform.SetValues(*[float(v) for row in matrix[:3] for v in row])
    return shape.transformShape(cq.Matrix(transform))


def normalize(shape, rotation):
    rotated = rigid_transform(shape, [row+[0] for row in rotation]+[[0, 0, 0, 1]])
    offset = exact_bounds(rotated)[:3]
    local = rotated.translate(tuple(-v for v in offset))
    inverse = [[rotation[j][i] for j in range(3)] for i in range(3)]
    translation = [sum(inverse[i][j]*offset[j] for j in range(3)) for i in range(3)]
    placement = [row+[translation[i]] for i, row in enumerate(inverse)]+[[0, 0, 0, 1]]
    return local, placement


def exact_bounds(shape):
    box = Bnd_Box()
    # STL tessellation must not change CAD equivalence or placement datums.
    BRepBndLib.AddOptimal_s(shape.wrapped, box, False, False)
    return box.Get()


def dimensions(shape):
    b = exact_bounds(shape)
    return tuple(b[i+3]-b[i] for i in range(3))


def difference(a, b):
    return a.cut(b).Volume()+b.cut(a).Volume()


def equivalent(a, b):
    if any(abs(x-y) > 1e-5 for x, y in zip(dimensions(a), dimensions(b))):
        return False
    if abs(a.Volume()-b.Volume()) > max(1e-4, a.Volume()*1e-9):
        return False
    if abs(a.Area()-b.Area()) > max(1e-4, a.Area()*1e-9):
        return False
    return difference(a, b) < max(1e-4, a.Volume()*1e-9)


def candidate_key(shape, row):
    # Keep purchased mesh stock and printed adapters distinct from steel sheet.
    material = 'printed' if row['group'] == 'printed_adapter' else 'sheet'
    return material, row.get('catalog', ''), tuple(round(v, 3) for v in sorted(dimensions(shape))), round(shape.Volume(), 3)


def write_csv(path, rows):
    with path.open('w') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def part_page(path, rows, parent):
    links = []
    for row in rows:
        stl = ' · <a href="'+html.escape(row['stl'])+'">Print STL</a>' if row.get('stl') else ''
        links.append('<li><a href="'+html.escape(row['file'])+'">'+html.escape(row['step_part'].replace('_', ' '))+'</a> — quantity '+str(row['quantity'])+(' (optional)' if row.get('optional') else '')+stl+'</li>')
    path.write_text('<!doctype html><meta charset="utf-8"><title>Chassis part STEP files</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px}li{margin:12px 0}a{color:#176483}</style><a href="'+parent+'">3D viewer and drawings</a><h1>Chassis part STEP files</h1><p>One file per distinct manufactured part. Quantities count installed occurrences, including optional parts. STEP files use local part coordinates; complete assemblies retain every installed position.</p><ul>'+''.join(links)+'</ul>')


def consolidate(source, output):
    assert source.resolve() != output.resolve()
    assert not output.exists(), 'Choose a fresh output directory'
    source_files = list(source.rglob('*.step'))
    assert source_files
    # A byte-for-byte retained source directory makes every omission reversible.
    source_hashes = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    def ignore(folder, names):
        rel = Path(folder).relative_to(source)
        if len(rel.parts) == 2 and rel.parts[0] in VARIANTS and rel.parts[1] == 'parts':
            return [n for n in names if n.endswith(('.step', '.stl'))]
        return []
    shutil.copytree(source, output, ignore=ignore)
    library = output/'parts'
    library.mkdir()
    buckets = collections.defaultdict(list)
    catalog = []
    names = set()
    manifests = {}
    max_error = 0.
    for variant in VARIANTS:
        rows = json.loads((source/variant/'parts-index.json').read_text())
        for row in rows:
            original = cq.importers.importStep(str(source/variant/row['file'])).val()
            key = candidate_key(original, row)
            match = None
            for rotation in ROTATIONS:
                if not buckets[key]:
                    break
                local, placement = normalize(original, rotation)
                match = next((entry for entry in buckets[key] if equivalent(entry['shape'], local)), None)
                if match is not None:
                    break
            if match is None:
                local, placement = normalize(original, ROTATIONS[0])
                name = row['part']
                for prefix, shared in [('GPU_stabilizer_finger_', 'GPU_stabilizer_finger'),
                                       ('GPU_tray_spot_welded_channel_', 'GPU_tray_stiffening_channel'),
                                       ('Tray_handhold_', 'Tray_handhold'),
                                       ('Crossbar_side_ledge_', 'Crossbar_side_ledge'),
                                       ('Rear_frame_external_angle_', 'Rear_frame_external_angle')]:
                    if name.startswith(prefix):
                        name = shared
                        break
                if name in names:
                    name = variant.replace('-', '_')+'_'+name
                assert name not in names, name
                names.add(name)
                match = dict(step_part=name, file='parts/'+name+'.step', shape=local, catalog=row.get('catalog', ''),
                             notes=row.get('notes', ''), occurrences=[], group=row['group'])
                catalog.append(match)
                buckets[key].append(match)
                cq.exporters.export(local, str(output/match['file']))
                if row['group'] == 'printed_adapter':
                    cq.exporters.export(local, str((output/match['file']).with_suffix('.stl')), tolerance=.05, angularTolerance=.1)
            restored = rigid_transform(match['shape'], placement)
            error = difference(original, restored)
            max_error = max(max_error, error)
            assert error < max(1e-4, original.Volume()*1e-9), (variant, row['part'], error)
            row.update(step_part=match['step_part'], file='../'+match['file'], assembly_from_part=placement)
            match['occurrences'].append(dict(variant=variant, part=row['part'], optional=row.get('optional', False)))
        manifests[variant] = rows
        (output/variant/'parts-index.json').write_text(json.dumps(rows, indent=2))
        csv_rows = [{**{k:r[k] for k in ('part', 'group', 'file', 'step_part', 'solid_count', 'catalog', 'notes')},
                     'assembly_from_part':json.dumps(r['assembly_from_part'], separators=(',', ':'))} for r in rows]
        write_csv(output/variant/'parts-index.csv', csv_rows)
        grouped = {}
        for row in rows:
            item = grouped.setdefault(row['step_part'], dict(step_part=row['step_part'], file=row['file'], quantity=0,
                                      optional=row.get('optional', False), catalog=row.get('catalog', ''), occurrences=[]))
            assert item['optional'] == row.get('optional', False)
            item['quantity'] += 1
            item['occurrences'].append(row['part'])
        inventory = [{**r, 'occurrences':'; '.join(r['occurrences'])} for r in grouped.values()]
        write_csv(output/variant/'parts-catalog.csv', inventory)
        page_rows = [{**r, 'file':'../'+r['file'],
                      'stl':'../'+r['file'][:-5]+'.stl' if r['step_part'].startswith('Printed_') else ''} for r in inventory]
        part_page(output/variant/'parts/index.html', page_rows, '../interactive_model.html')
        model_path = output/variant/'model.js'
        text = model_path.read_text()
        prefix, suffix = 'window.chassisModel=', ';window.modelReady();'
        assert text.startswith(prefix) and text.endswith(suffix)
        model = json.loads(text[len(prefix):-len(suffix)])
        links = {r['part']:r['file'] for r in rows}
        for part in model:
            if part['file'] is not None:
                part['file'] = links[part['name']]
        model_path.write_text(prefix+json.dumps(model, separators=(',', ':'))+suffix)
        report_path = output/variant/'manufacturing-changes.json'
        report = json.loads(report_path.read_text())
        report['part_STEP_count'] = len(grouped)
        report['manufactured_part_occurrences'] = len(rows)
        report['part_STEP_storage'] = '../parts shared library; placement matrices in parts-index.json'
        report_path.write_text(json.dumps(report, indent=2))
        print(variant, len(rows), 'occurrences,', len(grouped), 'distinct parts', flush=True)
    public_catalog = []
    for entry in catalog:
        exported = cq.importers.importStep(str(output/entry['file'])).val()
        assert exported.isValid() and equivalent(entry['shape'], exported), entry['file']
        public_catalog.append({k:v for k,v in entry.items() if k != 'shape'})
    (library/'catalog.json').write_text(json.dumps(public_catalog, indent=2))
    write_csv(library/'catalog.csv', [dict(step_part=e['step_part'], file=e['file'], catalog=e['catalog'],
              **{v:sum(o['variant']==v for o in e['occurrences']) for v in VARIANTS}) for e in catalog])
    # Family drawing tables retain assembly names; shared STEP paths make each row actionable.
    for family in ('full-chassis', 'module'):
        path = output/(family+'-parts-list.csv')
        with path.open() as f:
            rows = list(csv.DictReader(f))
        variants = VARIANTS[3:] if family == 'module' else VARIANTS[:3]
        for row in rows:
            for variant in variants:
                files = sorted({r['file'][3:] for r in manifests[variant] if r['drawing_family'] == row['part']})
                row[variant+'_STEP_files'] = '; '.join(files)
        write_csv(path, rows)
    neutral_headers(library)
    # Assemblies remain intact; file cleanup must not change assembly membership or placement.
    assemblies = []
    for variant in VARIANTS:
        for name in ('chassis_assembly.step', 'gpu_cartridge.step', 'front_cover.step'):
            rel = variant+'/'+name
            if rel not in source_hashes:
                assert name == 'front_cover.step'
                continue
            assert hashlib.sha256((output/rel).read_bytes()).hexdigest() == source_hashes[rel]
            assemblies.append(rel)
    assert all(hashlib.sha256((source/rel).read_bytes()).hexdigest()==digest for rel,digest in source_hashes.items())
    assert len(list(output.rglob('*.step'))) == len(catalog)+len(assemblies)
    result = dict(passed=True, manufactured_occurrences=sum(len(r) for r in manifests.values()),
                  unique_part_STEP_files=len(catalog), assembly_STEP_files=len(assemblies),
                  removed_redundant_exports=sum(len(r) for r in manifests.values())-len(catalog),
                  maximum_reconstruction_difference_mm3=max_error, reflections_allowed=False,
                  all_assembly_files_byte_identical=True, all_source_STEP_files_preserved=True)
    (output/'part-consolidation-validation.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    consolidate(*map(Path, sys.argv[1:3]))

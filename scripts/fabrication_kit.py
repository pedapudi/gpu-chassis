"""Assemble a fabricator-neutral kit from a CAD rebuild and drawing run.

Usage:
  python scripts/fabrication_kit.py BUILD OUT

BUILD is a `cad_source/rebuild.py --variant both` output directory with the
drawing sets generated. OUT receives `chassis-fabrication-kit/` containing one
formed STEP and one flat-pattern DXF per distinct sheet piece, a parts list
with quantities for every configuration, a hardware list, a tapped-thread
schedule, a SendCutSend compatibility review, the drawing PDFs and a README.
"""
import csv, io, json, pickle, re, shutil, sys, collections
from pathlib import Path
import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cad_source'))
from sheetmetal import sheet_parts, bounds  # noqa: E402

CONFIGS = {'nine-u': '9U, six 120 mm fans', 'nine-u-180': '9U, two 180 mm fans', 'nine-u-120': '9U, three 120 mm fans',
           'modular': 'Module, three 140 mm fans', 'modular-120-80': 'Module, three 120 mm + five 80 mm fans', 'modular-180': 'Module, two 180 mm fans'}
# Cold-rolled stock nearest each modeled thickness: (US gauge, inches, SendCutSend cold-rolled stock in mm or None).
STOCK = {1.0: ('20 ga', 0.036, None), 1.2: ('18 ga', 0.048, 1.22), 1.5: ('16 ga', 0.060, 1.50), 2.0: ('14 ga', 0.075, 1.88), 3.0: ('11 ga', 0.120, 3.02)}
SCS_FLAT_MIN, SCS_FLAT_MAX = (9.525, 38.1), (762.0, 1117.6)
# Joining instructions for pieces that are welded to another part.
JOINS = [('Rail_square_nut_guide_strip_', 'Weld to the underside of its longitudinal mount rail with a 7.2 mm gauge between the two strips.'),
         ('GPU_tray_spot_welded_channel_', 'Spot weld the channel crown to the underside of the GPU tray.'),
         ('Tray_handhold_', 'Weld the horizontal leg to the top of the GPU tray.'),
         ('Upper_bank_toe_receiver', 'Stitch weld to the GPU rear-panel web: 6 mm welds with 1 mm legs between notches, underside only.'),
         ('Lower_bank_toe_receiver', 'Stitch weld to the lower rear web: 6 mm welds with 1 mm legs between notches, underside only.'),
         ('Lower_bank_retention_flange', 'Weld to the back face of the lower rear web after extruding and tapping its eight #6-32 collars.'),
         ('Front_bearing_angle_spot_welded_to_side_angles', 'Spot weld each end to the side bearing angles.')]


def load(folder):
    parts = []
    for a in pickle.loads((folder / 'parts.brep.pickle').read_bytes()):
        a['shape'] = cq.Shape.importBrep(io.BytesIO(a.pop('brep'))); parts.append(a)
    return parts


def signature(record):
    """Pieces with equal signatures are interchangeable copies of one blank."""
    bends = tuple(sorted((b['direction'], round(b['length_mm'], 2), round(b['bend_allowance_mm'], 3)) for b in record['bends']))
    threads = tuple(sorted(collections.Counter(h['thread'] for h in record.get('tapped_holes', [])).items()))
    return (record['thickness_mm'], tuple(round(v, 2) for v in record['flat_size_mm']), round(record['flat_area_mm2'], 1), bends, threads)


def fastener_spec(name, shape):
    m = re.search(r'M(\d)x(\d+)', name)
    if 'captive_thumbscrew' in name: return 'M3 captive panel screw, 8 mm knurled head, press-fit ferrule for a 6.4 mm hole in 1.5 mm steel'
    if 'self_tapping_5x8' in name: return '5 x 8 mm self-tapping plastic fan screw'
    if '6_32_screw' in name or '6_32xquarter' in name: return '#6-32 UNC x 1/4 in pan-head machine screw'
    if m and 'nut' not in name and 'washer' not in name: return f'M{m.group(1)} x {m.group(2)} mm pan-head machine screw (ISO 7045)'
    if 'washer' in name: return 'M3 flat washer, 7 mm OD x 0.5 mm'
    if 'female_female_standoff' in name: return 'Harwin R30-1000802 M3 x 8 mm female-female hex spacer'
    if 'male_female_standoff' in name: return 'M3 x 8 mm male-female hex standoff, 5 mm across flats, 6 mm stud'
    if 'DIN562' in name: return 'DIN 562 M4 square thin nut'
    if 'nut' in name:
        b = bounds(shape); h = round(min(b[3] - b[0], b[4] - b[1], b[5] - b[2]), 2)
        return {2.4: 'M3 hex nut (ISO 4032)', 3.2: 'M4 hex nut (ISO 4032)', 2.78: '#6-32 UNC hex nut, 5/16 in across flats'}.get(h, f'nut, {h} mm thick')
    return None


def main(build, out):
    kit = out / 'chassis-fabrication-kit'
    if kit.exists(): shutil.rmtree(kit)
    for d in ('step', 'flat', 'drawings'): (kit / d).mkdir(parents=True)
    items = {}; hardware = collections.defaultdict(collections.Counter); threads = []; holds = collections.defaultdict(set)
    for config in CONFIGS:
        folder = build / config
        records = [r for r in json.loads((folder / 'flat_patterns/flat_patterns.json').read_text()) if r['developed']]
        checks = json.loads((folder / 'formed_part_checks.json').read_text())
        for h in checks['short_flanges']:
            holds[h['piece']].add(f"bend {h['bend']} outside flanges {h['outside_flange_lengths_mm']} mm, below the {h['minimum_mm']:g} mm press-brake guideline")
        for h in checks['holes_near_bends']:
            holds[h['piece']].add('cutouts closer than two thicknesses to a bend')
        pieces_per_part = collections.Counter(r['part'] for r in records)
        for r in records:
            if config in ('nine-u', 'modular'):
                threads += [dict(configuration=CONFIGS[config], piece=r['piece'], part=r['part'], thread=h['thread'],
                                 x=round(h['centre'][0], 2), y=round(h['centre'][1], 2), z=round(h['centre'][2], 2)) for h in r.get('tapped_holes', [])]
            key = signature(r)
            item = items.setdefault(key, dict(name=r['piece'], record=r, folder=folder, parts=set(), quantities=collections.Counter(), weldment=set()))
            item['quantities'][config] += 1; item['parts'].add(r['part'])
            if pieces_per_part[r['part']] > 1: item['weldment'].add(r['part'])
        parts = load(folder); sheets = sheet_parts(parts); sheet_names = {s['name'] for s in sheets}
        for p in parts:
            spec = None if p['name'] in sheet_names else fastener_spec(p['name'], p['shape'])
            if spec: hardware[spec][config] += 1
    rows = []
    for n, (key, item) in enumerate(sorted(items.items(), key=lambda kv: kv[1]['name']), 1):
        r = item['record']; t = r['thickness_mm']; gauge, inch, scs = STOCK.get(t, ('custom', t / 25.4, None))
        ident = f'SM{n:03d}'
        shutil.copy2(item['folder'] / 'flat_patterns' / r['dxf'], kit / 'flat' / f"{ident}_{item['name']}.dxf")
        shutil.copy2(item['folder'] / 'flat_patterns' / (r['piece'] + '.step'), kit / 'step' / f"{ident}_{item['name']}.step")
        joins = [text for prefix, text in JOINS if item['name'].startswith(prefix)]
        if item['weldment']: joins.append('Weld to the other pieces of ' + ', '.join(sorted(item['weldment'])) + ' per the drawing set.')
        counts = collections.Counter(h['thread'].replace('6-32', '#6-32 UNC-2B') for h in r.get('tapped_holes', []))
        tapping = ('; '.join(f'{n} x {t}' for t, n in sorted(counts.items())) + ' in extruded collars; extrude and tap after forming the adjacent bends') if counts else ''
        size = sorted(r['flat_size_mm'])
        scs_notes = []
        if scs is None or abs(scs - t) > .05: scs_notes.append(f'no {t:g} mm cold-rolled stock; nearest ' + ('0.76 or 1.22 mm' if t < 1.2 else '1.88 mm'))
        if size[0] < SCS_FLAT_MIN[0] or size[1] < SCS_FLAT_MIN[1]: scs_notes.append('below the 0.375 x 1.5 in minimum part size')
        if size[0] > SCS_FLAT_MAX[0] or size[1] > SCS_FLAT_MAX[1]: scs_notes.append('exceeds the 30 x 44 in maximum part size')
        if any(b['length_mm'] > 406.4 for b in r['bends']): scs_notes.append('bend longer than 16 in; confirm the thickness-specific bend-length limit')
        if holds.get(r['piece']): scs_notes.append('check bend feasibility against the supplier bend specifications')
        if tapping: scs_notes.append('extruded collars are not a standard option; extrude and tap in house, or substitute press-fit nuts')
        if joins: scs_notes.append('welding or in-house joining required')
        blocked = any('stock' in s or 'part size' in s for s in scs_notes)
        rows.append({'item': ident, 'piece': item['name'], 'used_in_parts': '; '.join(sorted(item['parts'])),
                     'configurations': '; '.join(CONFIGS[c] for c in CONFIGS if item['quantities'].get(c)),
                     'material': 'Cold-rolled low-carbon steel (1008/1010)', 'thickness_mm': f'{t:.1f}', 'nearest_gauge': f'{gauge} ({inch:.3f} in)',
                     'flat_size_mm': ' x '.join(f'{v:.2f}' for v in r['flat_size_mm']), 'bends': len(r['bends']),
                     'bend_inside_radius_mm': r['bends'][0]['inside_radius_mm'] if r['bends'] else '', 'k_factor': r['k_factor'] if r['bends'] else '',
                     **{f'qty_{c}': item['quantities'].get(c, 0) for c in CONFIGS},
                     'tapping': tapping, 'joining': ' '.join(joins),
                     'finish': 'Deburr; zinc plate or powder coat after welding; mask threads',
                     'fabrication_holds': '; '.join(sorted(holds.get(r['piece'], []))),
                     'sendcutsend': ('not suitable as drawn: ' if blocked else 'suitable with notes: ' if scs_notes else 'suitable') + '; '.join(scs_notes),
                     'step_file': f"step/{ident}_{item['name']}.step", 'dxf_file': f"flat/{ident}_{item['name']}.dxf"})
    with (kit / 'parts_list.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
    with (kit / 'hardware_list.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['hardware'] + [f'qty_{c}' for c in CONFIGS])
        for spec in sorted(hardware): w.writerow([spec] + [hardware[spec].get(c, 0) for c in CONFIGS])
    with (kit / 'tapped_thread_schedule.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, list(threads[0])); w.writeheader(); w.writerows(threads)
    for config in CONFIGS:
        pdf = next((build / config / 'drawings').glob('*.pdf'))
        shutil.copy2(pdf, kit / 'drawings' / f'{config}_{pdf.name}')
    shutil.copy2(Path(__file__).with_name('fabrication_kit_README.md'), kit / 'README.md')
    summary = collections.Counter(r['sendcutsend'].split(':')[0] for r in rows)
    (kit / 'kit_summary.json').write_text(json.dumps(dict(distinct_sheet_items=len(rows), sendcutsend=summary,
        pieces_per_configuration={c: sum(r[f'qty_{c}'] for r in rows) for c in CONFIGS}), indent=2))
    return rows, summary


if __name__ == '__main__':
    rows, summary = main(Path(sys.argv[1]), Path(sys.argv[2]))
    print(len(rows), 'distinct sheet items', dict(summary))

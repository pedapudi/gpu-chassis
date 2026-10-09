"""Selected metric assembly hardware; dimensions checked against the supplier catalog."""
import re

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

SCREWS = {
    ('M3', 3): '92005A111',
    ('M3', 5): '92005A114', ('M3', 6): '92005A116',
    ('M3', 8): '92005A118', ('M3', 12): '92005A122',
    ('M3', 16): '92005A126', ('M4', 8): '92005A218',
    ('M4', 10): '92005A220',
}
DESCRIPTIONS = {
    '97447A801': '3.2 mm blind rivet, 1.5-3.5 mm grip',
    '92010A116': 'M3 x 6 flat-head Phillips screw, 90 deg',
    '92871A003': '3 mm spacer, 6 OD, 3.2 bore',
    '92871A009': '6 mm spacer, 6 OD, 3.2 bore',
    '92871A011': '8 mm spacer, 6 OD, 3.2 bore',
    '94459A140': 'M3 heat-set insert, 5.7 long',
    '95185A530': 'M3 self-clinching nut',
    '95185A590': 'M4 self-clinching nut',
    '86235K311': 'Foam pad 20 x 12 x 1.5875 (cut stock)',
    '90965A130': 'M3 washer, 7 OD x 0.5 nominal',
    '91116A120': 'M3 large washer, 9 OD x 0.8 nominal',
    '92725T3': 'Perforated sheet, cut to drawing',
    **{sku: f'{thread} x {length} pan-head Phillips screw' for (thread, length), sku in SCREWS.items()},
}


def assign(parts):
    """Attach order numbers and normalize cached M3 screw heads to diameter 6."""
    for p in parts:
        if p['role'] not in ('fabricated', 'purchased'):
            continue
        match = re.search(r'M([34])x(\d+)', p['name'])
        if match:
            key = ('M'+match[1], int(match[2]))
            p['catalog'] = SCREWS[key]
            p['specification'] = DESCRIPTIONS[p['catalog']]
            if key[0] == 'M3':
                for face in p['shape'].Faces():
                    if face.geomType() != 'CYLINDER':
                        continue
                    cylinder = BRepAdaptor_Surface(face.wrapped).Cylinder()
                    if abs(cylinder.Radius()-2.8) > 1e-6:
                        continue
                    direction = cq.Vector(cylinder.Axis().Direction())
                    head = cq.Solid.makeCylinder(3, 2.4, face.Center()-direction*1.2, direction)
                    p['shape'] = p['shape'].fuse(head).clean()
                    assert p['shape'].isValid(), p['name']
                    break
        elif 'washer' in p['name'].lower():
            p['catalog'] = '91116A120' if 'large_washer' in p['name'] else '90965A130'
            p['specification'] = DESCRIPTIONS[p['catalog']]

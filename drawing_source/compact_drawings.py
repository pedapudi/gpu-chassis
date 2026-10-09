"""Human-readable A2 drawing books, shared across each chassis' fan options.

Each technical note sits beside the corresponding CAD contours. Exact
machine-readable feature centres supplement the drawings in a separate CSV.
"""
import collections
import csv
import json
import math
import sys
from pathlib import Path

import cadquery as cq
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.lib.pagesizes import A2, landscape

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from manufacturing_revision import load,step_shape
from sheetmetal import bounds, sheet_parts
from catalog_hardware import DESCRIPTIONS

W,H=landscape(A2)
INK=HexColor('#1b2c38');BLUE=HexColor('#165d78');GREY=HexColor('#a8b3ba')


def fmt(v):return f'{v:.2f}'.rstrip('0').rstrip('.')
def title(name):return name.replace('_',' ').replace('1p5mm','1.5 mm').replace('1p2mm','1.2 mm')


def edges(shape):
    for e in shape.Edges():
        n=1 if e.geomType()=='LINE' else min(96,max(20,int(e.Length()/2)))
        yield [e.positionAt(i/n).toTuple() for i in range(n+1)]


def lines(c,pts):
    if len(pts)<2:return
    p=c.beginPath();p.moveTo(*pts[0])
    for q in pts[1:]:p.lineTo(*q)
    c.drawPath(p)


def paragraph(c,text,x,y,width,size=10):
    c.setFont('Helvetica',size);c.setFillColor(INK)
    for line in simpleSplit(text,'Helvetica',size,width):c.drawString(x,y,line);y-=size*1.35
    return y-7


def dimension(c,a,b,text,vertical=False,offset=18):
    c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(.5);c.setFont('Helvetica',9)
    if vertical:
        x=min(a[0],b[0])-offset
        for p in (a,b):c.line(p[0]-3,p[1],x-3,p[1]);c.line(x-2,p[1]-2,x+2,p[1]+2)
        c.line(x,a[1],x,b[1]);c.saveState();c.translate(x-5,(a[1]+b[1])/2);c.rotate(90);c.drawCentredString(0,0,text);c.restoreState()
    else:
        y=min(a[1],b[1])-offset
        for p in (a,b):c.line(p[0],p[1]-3,p[0],y-3);c.line(p[0]-2,y-2,p[0]+2,y+2)
        c.line(a[0],y,b[0],y);c.drawCentredString((a[0]+b[0])/2,y-12,text)


def leader(c,p,text,x,y,width=250):
    c.setStrokeColor(BLUE);c.setLineWidth(.55);c.circle(*p,1.8,stroke=1,fill=0);c.line(*p,x-4,y+3)
    return paragraph(c,text,x,y,width,9)


def projection(c,shapes,rect,axis=None,face_only=False,reverse=False,dim=True):
    bbs=[bounds(s) for s in shapes];box=[min(b[i] for b in bbs) for i in range(3)]+[max(b[i+3] for b in bbs) for i in range(3)]
    if axis is None:
        def uv(p):return .866*(p[0]+p[1]),p[2]+.5*(p[1]-p[0])
    else:
        ij=[k for k in range(3) if k!=axis]
        def uv(p):return (-1 if reverse else 1)*p[ij[0]],p[ij[1]]
    points=[uv((x,y,z)) for x in (box[0],box[3]) for y in (box[1],box[4]) for z in (box[2],box[5])]
    lo=[min(p[k] for p in points) for k in (0,1)];hi=[max(p[k] for p in points) for k in (0,1)]
    x,y,w,h=rect;px,py=(80,65) if dim else (12,12)
    s=min((w-px)/max(hi[0]-lo[0],1),(h-py)/max(hi[1]-lo[1],1))
    ox=x+px/2+(w-px-(hi[0]-lo[0])*s)/2;oy=y+py/2+(h-py-(hi[1]-lo[1])*s)/2
    def mapper(p):q=uv(p);return ox+(q[0]-lo[0])*s,oy+(q[1]-lo[1])*s
    c.setStrokeColor(INK);c.setLineWidth(.5)
    for shape in shapes:
        if face_only:
            fs=[f for f in shape.Faces() if f.geomType()=='PLANE' and abs(f.normalAt().toTuple()[axis])>.999]
            if fs:shape=max(fs,key=lambda f:f.Area())
        for ee in edges(shape):lines(c,[mapper(p) for p in ee])
    if dim and axis is not None:
        a=(ox,oy);dimension(c,a,(ox+(hi[0]-lo[0])*s,oy),fmt(hi[0]-lo[0]));dimension(c,a,(ox,oy+(hi[1]-lo[1])*s),fmt(hi[1]-lo[1]),True)
    return mapper


def holes(shape):
    circles={}
    for e in shape.Edges():
        if e.geomType()!='CIRCLE' or abs(e.Length()-2*math.pi*e.radius())>1e-4:continue
        g=e._geomAdaptor().Circle();a=g.Axis().Direction();k=max(range(3),key=lambda i:abs((a.X(),a.Y(),a.Z())[i]))
        centre=g.Location();p=tuple(round(v,4) for v in (centre.X(),centre.Y(),centre.Z()))
        circles[(k,round(e.radius()*2,4),p)]=dict(axis=k,diameter=round(e.radius()*2,4),centre=p)
    return list(circles.values())


class Book:
    def __init__(self,path,name):
        self.c=canvas.Canvas(str(path),pagesize=(W,H));self.c.setTitle(name);self.c.setAuthor('');self.c.setCreator('');self.c._doc.info.producer='';self.name=name;self.n=0;self.index=[]
    def page(self,name):
        if self.n:self.c.showPage()
        self.n+=1;self.index.append(dict(page=self.n,title=name));c=self.c
        c.setStrokeColor(GREY);c.setLineWidth(.6);c.rect(20,25,W-40,H-45)
        c.setFillColor(INK);c.setFont('Helvetica-Bold',19);c.drawString(38,H-43,self.name+' | '+name)
        c.setFont('Helvetica',9);c.drawString(38,H-63,'ALL DIMENSIONS mm | Nominal formed geometry | Supplier interfaces marked provisional | Do not scale')
        c.setStrokeColor(GREY);c.line(30,H-75,W-30,H-75);c.line(30,48,W-30,48)
        c.setFont('Helvetica',9);c.drawString(38,34,'A2 landscape | Continuous outlines are CAD edges; blue leaders identify dimensions and assembly requirements.')
        c.drawRightString(W-38,34,f'Sheet {self.n}')
        return c
    def finish(self,path):
        self.c.save();Path(path).write_text(json.dumps(self.index,indent=2))


def assembly(book,parts,report,modular):
    c=book.page('Assembly and service access')
    shown=[p for p in sheet_parts(parts) if p['group'] not in ('lid','intake_grilles')]
    mp=projection(c,[p['shape'] for p in shown],(35,290,W*.65,H-395),dim=False)
    names=['GPU_tray_two_side_bends','Printed_backplane_adapter_left','Full_width_twenty_one_slot_rear_with_side_returns','Screw_mounted_3mm_rack_ear_left','Removable_chassis_crossbar']
    texts=['Lift-out steel GPU cartridge; unplug all signal and power leads first.',
           '8.5 mm printed adapter, supported on steel. Board hole pattern is replaceable.',
           '21 rear bracket positions at 20.32 mm pitch; keep the PCB seating datum fixed.',
           'Separate 3 mm rack ear; M4 side screws. Use rated rails or shelf for chassis weight.',
           'Remove four top M4 x 8 screws to lift the crossbar and optional fingers together. Fixed ledges remain ahead of the GPU extraction path.']
    for i,(name,text) in enumerate(zip(names,texts)):
        p=next(p for p in parts if p['name']==name);leader(c,mp(p['shape'].Center().toTuple()),text,W*.69,H-140-i*115,W*.26)
    y=235
    height=221.75 if modular else 399.25
    for text in [f'Envelope: body 440 W x 485 D x {height:g} H. Rack face 482.6 W. Removable mesh cover projects 8.21 mm ahead of the fan plate.',
        ('Assembly order: fit press nuts to bare panels; attach the lid adapter and fixed rear frame to the empty module before fitting bearing angles; prepare the cartridge on a bench; fit PCB and GPUs; seat the cartridge, connect cables, then fit crossbar, lid and front mesh.' if modular else 'Assembly order: fit press nuts to bare panels; assemble the body and fixed rear frame; install the PSU before its adjacent bearing angle; fit the motherboard tray before rear fans; prepare the GPU cartridge on a bench; fit PCB and GPUs, connect cables, then close covers.'),
        'Cartridge service: remove lid and crossbar, disconnect cables, release four front M4 and four rear-side M3 screws, then lift. Rear mesh frame, brush entry and their screws stay installed. For PCB service, remove GPUs and six top M3 x 16 screws; collect the loose 8 mm spacers.',
        ('OEM RM53-502 lid attachment remains a transfer-drill template. Measure the real lid and screw locations before drilling the adapter returns. Module mass requires independent rack support.' if modular else 'Motherboard installation: fit the board tray and its metric posts before the lower rear fans. Retimers and MCIO cables occupy the lower PCIe slots. External MCIO entry remains available.')]:
        y=paragraph(c,text,55,y,W-110,12)


def interfaces(book,parts,report,modular):
    c=book.page('Rear interfaces and backplane seating')
    rear=next(p for p in parts if p['name']=='Full_width_twenty_one_slot_rear_with_side_returns')
    b=bounds(rear['shape']);mp=projection(c,[rear['shape']],(35,530,W-540,520),axis=1,reverse=True)
    c.setFont('Helvetica-Bold',12);c.drawString(60,1055,'Exterior rear view: X decreases to the right. GPU slots are not mirrored.')
    for i,text in enumerate(['21 x aperture: 15.00 wide x 100.50 high; square cut corners R0 nominal.',
        'Slot pitch 20.32; dual-slot socket pitch 40.64. Preserve bracket/PCB alignment.',
        'Retention screw axes sit 5.08 behind the bracket plane. M3 x 5 screws.',
        'Integral upper shelf: 1.2 mm sheet, inside bend R1.2, 90 degrees.',
        'Toe receiver remains a separately joined comb: 10.79 wide x 1.30 deep notches. Fixture and stitch weld before installing cards.']):
        leader(c,mp((b[0]+(i+.5)*(b[3]-b[0])/5,b[1],b[2]+(25 if i<2 else b[5]-b[2]-8))),text,W-475,990-i*90,410)
    if not modular:
        lower=[p['shape'] for p in parts if p['name'].startswith(('Lower_rear_','Flat_1p2mm_IO_carrier','Lower_bank_retention','Lower_bank_toe'))]
        mp=projection(c,lower,(35,85,870,415),axis=1,reverse=True)
        paragraph(c,'Lower deck: 8 case apertures on 20.32 pitch; 15 x 103 openings. I/O shield aperture 158.75 x 44.45. Two 80 mm fan patterns: 71.5 square. PSU native screws retain the supplied thread.',935,380,680,13)
        paragraph(c,'The motherboard underside is at Z16.00 and its PCB is 1.57 thick. Standard 6 mm metric spacers plus 0.5 mm M3 washers sit on the tray top at Z9.50. M3 x 12 screws retain the board. Confirm the actual board hole pattern and I/O shield seating before fabrication.',935,255,680,12)
    else:
        adapter=next(p for p in parts if p['group']=='adapter')
        projection(c,[adapter['shape']],(35,85,870,415),axis=2)
        paragraph(c,'Replacement-lid adapter: 440 x 485 ring, 1.5 sheet. OEM side returns are intentionally undrilled. Six M3 module screws locate the upper body. Transfer only verified OEM hole positions.',935,365,680,13)
        paragraph(c,'Rear MCIO opening is 140 x 35 with its top cap removed. Disconnect external cables before extraction; the rear screen and entry frame stay installed. M3 x 3 base screws and M3 x 5 cap screws stay flush with or behind the inner frame face.',935,230,680,12)
    sup=report['backplane_support'];paragraph(c,f"GPU seating: tray top Z{fmt(sup['tray_top_z_mm'])} + 8.50 print + 8.00 spacer = PCB underside Z{fmt(sup['PCB_underside_z_mm'])}. Changing the printed hole pattern must not change this stack.",55,65,W-110,10)


def parts_list(book, variants, detail_parts, root, modular):
    """Count fabricated parts and catalog fasteners from each exported assembly."""
    c = book.page('Parts list and assembly identification')
    names = list(variants)
    labels = ['3x140', '3x120+5x80', '2x180'] if modular else ['6x120', '2x180', '3x120']
    counts = {name: collections.Counter(p.get('drawing_family',p['name']) for p in sheet_parts(pp)) for name, pp in variants.items()}
    unique = {}
    for pp in variants.values():
        for p in sheet_parts(pp):unique.setdefault(p.get('drawing_family',p['name']),p)
    sheet = {p['name']: 6 + i // 9 for i, p in enumerate(detail_parts)}
    for name in unique:
        if name.startswith('Printed_backplane_'): sheet[name] = 4
        elif name=='Full_width_twenty_one_slot_rear_with_side_returns':sheet[name]=3
        elif name.startswith('Stock_hex_rear_'):sheet[name]=sheet['Fixed_rear_mesh_frame']
        elif name not in sheet: sheet[name] = 5
    rows = []
    c.setFont('Helvetica-Bold', 12); c.drawString(45, H-103, 'Chassis parts: one selected fan configuration per build')
    c.setFont('Helvetica', 9)
    c.drawString(45, H-123, 'Item numbers identify this book. The accompanying parts-list CSV preserves the exact STEP part names.')
    xq = [728, 784, 846]
    def headings(y, description, right=False):
        c.setFillColor(INK); c.setFont('Helvetica-Bold', 9)
        if right:
            c.drawString(940, y, description)
            c.drawString(1320, y, 'McMaster-Carr')
            for xx, label in zip((1465, 1528, 1605), labels): c.drawCentredString(xx, y, label)
        else:
            c.drawString(45, y, 'Item'); c.drawString(77, y, description); c.drawString(565, y, 'McMaster-Carr'); c.drawString(670, y, 'Sheet')
            for xx, label in zip(xq, labels): c.drawCentredString(xx, y, label)
        c.setStrokeColor(GREY); c.line(935 if right else 45, y-8, W-45 if right else 878, y-8)
    headings(H-151, 'Part name')
    y = H-181
    item_numbers = {}
    for number, (name, part) in enumerate(unique.items(), 1):
        item_numbers[name] = number
        wrapped = simpleSplit(title(name), 'Helvetica', 9, 478)
        c.setFillColor(INK); c.setFont('Helvetica', 9)
        c.drawString(45, y, str(number))
        for j, line in enumerate(wrapped): c.drawString(77, y-j*11, line)
        sku=part.get('catalog','')
        c.drawString(565, y, sku or 'Custom part')
        if sku: c.linkURL('https://www.mcmaster.com/'+sku+'/',(565,y-2,655,y+10),relative=0)
        c.drawCentredString(683, y, str(sheet[name]))
        qty = [counts[n][name] for n in names]
        for xx, count in zip(xq, qty): c.drawCentredString(xx, y, (str(count)+('*' if part.get('optional') else '')) if count else '-')
        rows.append(dict(item=number, part=name, McMaster_item=sku or 'Custom part', supplier_url='https://www.mcmaster.com/'+sku+'/' if sku else '', drawing_sheet=sheet[name],optional=part.get('optional',False), **dict(zip(names, qty))))
        y -= max(21, len(wrapped)*11+5)
    assert y > 160, ('Parts list exceeds available height', y)
    c.setFont('Helvetica-Bold', 10); c.drawString(77, y, 'Total chassis parts, including cut stock mesh and printed adapters')
    for xx, name in zip(xq, names): c.drawCentredString(xx, y, str(sum(counts[name].values())))
    paragraph(c, 'Choose the matching fan-variant directory for STEP files. Totals include optional items marked *. Ten identical stabilizer fingers share one detail drawing. Omit these fingers if shroud contact lands are unverified. Stock mesh is McMaster 92725T3, cut to size.', 45, y-27, 830, 10)
    family = 'module' if modular else 'full-chassis'
    with (root / (family+'-parts-list.csv')).open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

    selected = ['GPU_tray_two_side_bends', 'Printed_backplane_adapter_left',
                'Full_width_twenty_one_slot_rear_with_side_returns', 'Screw_mounted_3mm_rack_ear_left']
    shown = [p for p in sheet_parts(variants[names[0]]) if p['group'] not in ('lid', 'intake_grilles')]
    mp = projection(c, [p['shape'] for p in shown], (940, 725, 450, 330), dim=False)
    for i, name in enumerate(selected):
        p = unique[name]
        leader(c, mp(p['shape'].Center().toTuple()), f"Item {item_numbers[name]}: "+title(name), 1400, 1030-i*71, 230)

    catalog_items = {}
    inventories = {}; optional_inventories = {}
    for name in names:
        inventory = collections.Counter()
        optional_inventory = collections.Counter()
        source_rows=[(row,False) for row in csv.DictReader((root/name/'hardware.csv').open())]
        optional_path=root/name/'optional-hardware.csv'
        if optional_path.exists():source_rows += [(row,True) for row in csv.DictReader(optional_path.open())]
        for row,optional in source_rows:
            spec = row['specification']; item = row['McMaster_item']
            if spec in ('ISO 7089 M3 washer, 7 mm OD x 0.5 mm', 'M3 washer, 7 mm OD x 0.5 mm'):
                spec = 'M3 washer, 7 OD x 0.5'
            elif item: spec = DESCRIPTIONS[item]
            elif spec.startswith('ISO 7093'): spec = 'M3 large washer, 9 OD x 0.8'
            elif spec.startswith('PSU factory'): spec = 'PSU factory #6-32 screw'
            elif spec.startswith('Short case-fan'): spec = 'Short plastic case-fan screw'
            catalog_items[spec] = item
            (optional_inventory if optional else inventory)[spec] += int(row['quantity'])
        inventories[name] = inventory
        optional_inventories[name] = optional_inventory
    hardware = list(dict.fromkeys(spec for inv in list(inventories.values())+list(optional_inventories.values()) for spec in inv))
    c.setFont('Helvetica-Bold', 12); c.drawString(940, 710, 'Installed fasteners and spacers')
    headings(687, 'Specification', right=True)
    yy = 661
    hardware_rows = []
    for spec in hardware:
        c.setFont('Helvetica', 9); c.drawString(940, yy, spec)
        sku=catalog_items[spec]
        c.drawString(1320, yy, sku or 'Supplier screw')
        if sku: c.linkURL('https://www.mcmaster.com/'+sku+'/',(1320,yy-2,1410,yy+10),relative=0)
        qty = [inventories[name][spec] for name in names]
        opt=[optional_inventories[name][spec] for name in names]
        for xx, count, extra in zip((1465, 1528, 1605), qty, opt):
            label=(str(count) if count else '')+('+' if count and extra else '')+(str(extra)+'*' if extra else '')
            c.drawCentredString(xx, yy, label or '-')
        hardware_rows.append(dict(specification=spec, McMaster_item=sku or 'Supplier screw', supplier_url='https://www.mcmaster.com/'+sku+'/' if sku else '', **dict(zip(names, qty)), **dict(zip((n+'_optional' for n in names),opt))))
        yy -= 21
    assert yy > 240, ('Hardware list exceeds available height', yy)
    with (root/(family+'-hardware-list.csv')).open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(hardware_rows[0])); writer.writeheader(); writer.writerows(hardware_rows)
    paragraph(c, '* Optional ten-GPU stabilizer kit. Add 20 M3 x 6 screws, 20 M3 press nuts and ten foam pads. Metric M3 x 0.5 / M4 x 0.7 threads. Four rear-frame screws have flush 90-degree heads; other machine screws have pan heads. Retain supplier threads for equipment.', 940, yy-10, 690, 10)
    paragraph(c, 'Scope: chassis structure and modeled assembly hardware. Fans, electronics, AIO mounting screws, brush seals, cable ties and rack rails require a separate installation kit. Fan sizes are given on sheet 5. GPU and backplane quantities are fit references, not a purchasing requirement.', 940, 155, 690, 10)
    paragraph(c, 'Each quantity column covers the complete chassis or module with the indicated GPU intake option. Lower AIO and rear fan mounting hardware is common to the full-chassis options where modeled.', 45, 105, 830, 10)


def adapter_hardware(book,parts,report):
    c=book.page('Printed adapter and catalog hardware')
    plates=[p for p in parts if p['group']=='printed_adapter'];mp=projection(c,[p['shape'] for p in plates],(40,480,930,575),axis=2)
    sup=report['backplane_support']
    for row,(i,(x,y)) in enumerate(sorted(enumerate(sup['PCB_points']),key=lambda p:(-p[1][1],p[1][0]))):
        leader(c,mp((x,y,sup['tray_top_z_mm'])),f'Insert {i+1}: X{fmt(x)}, Y{fmt(y)}',1000,1030-row*48,590)
    y=680
    for text in ['Two plates, each 209.5 x 240 x 8.5; 1 mm centre gap. A 5 mm brim gives a 219.5 x 250 footprint on a 256 x 256 print bed. Each half fastens independently to the steel tray. Six walls and solid material around insert bosses.',
        'Eight tray fixings: diameter 3.4 through the print at X25, 209.5, 230.5, 415 and Y220, 439. Steel tray holes diameter 4.22 for M3 press nuts. Coordinates use the assembly origin.',
        'M3 insert pilots: 4.0 diameter x 6.7 deep from the top; 5.7 installed insert length. Top surface must remain flat. Actual print shrinkage and insert fit require a coupon.',
        'Use unfilled flame-retardant PC with documented temperature capability. Conductive carbon-filled filament is unsuitable beneath exposed PCB circuitry. Hot creep and fire qualification are not established by CAD.',
        'Reprint the two adapters for a different verified PCB hole pattern. Keep the tray holes, 8.5 thickness and 8 mm spacer height. The illustrated six PCB holes are provisional photo estimates.']:
        y=paragraph(c,text,1000,y,600,11)
    z=sup['tray_top_z_mm'];x,y0=sup['PCB_points'][0]
    section=[p['shape'] for p in parts if p['name'].startswith(('Printed_backplane_adapter','Backplane_heat_insert_M3_1','Backplane_metric_spacer_8mm_1','Backplane_M3x16_screw_1','GPU_tray_two_side_bends','Miwin_MG_SW510B','Backplane_M3_washer_0'))]
    crop=box_section(x,y0,z)
    ss=[p.intersect(crop) for p in section];ss=[p for p in ss if p.Volume()>1e-6]
    mp=projection(c,ss,(55,155,470,290),axis=1)
    for value,text,yy in [(z+19.5,'M3 x 16, top-access',385),(z+12.5,'8 spacer',342),(z+4.25,'8.5 print',299),(z,'Steel tray datum',256)]:leader(c,mp((x,y0,value)),text,540,yy,250)
    y=420
    rows=[('94459A140','M3 x 0.5 brass heat-set insert, 5.7 installed length; six per adapter pair.'),
          ('92871A011','Metric unthreaded standoff: 8 long, 6 OD, 3.2 bore; six per backplane.'),
          ('95185A530 / 95185A590','M3 / M4 self-clinching nuts; 4.22 / 5.41 installation holes, +0.08/-0.00. Fit with a press before closing the assembly.'),
          ('92725T3','Pre-perforated steel: 0.9144 thick, hexagonal 6.35 openings, 79% nominal open area.'),
          ('92871A007','5 mm metric front-cover spacers with M3 large washers, 9 OD x 0.8. Cover screws M3 x 16.'),
          ('Metric screw families','ISO 7045 M3 panel screws; M4 rack-ear screws; M3 x 12 adapter screws. PSU and radiator factory threads are supplier-controlled exceptions.')]
    for a,b in rows:
        c.setFont('Helvetica-Bold',11);c.drawString(865,y,a);y=paragraph(c,b,865,y-17,740,10)


def box_section(x,y,z):return cq.Solid.makeBox(18,.2,25.5,cq.Vector(x-9,y-.1,z-1.5))


def fans(book,variants,modular):
    c=book.page('Fan plates, removable stock mesh and rack ears')
    columns=(W-90)/3
    for col,(name,parts) in enumerate(variants.items()):
        shown=[p for p in sheet_parts(parts) if p['name'].startswith(('Front_fan_carrier','Upper_module_front_carrier','Full_chassis_upper_intake'))]
        xx=35+col*columns
        c.setFont('Helvetica-Bold',13);c.drawString(xx+15,1045,name)
        mp=projection(c,[p['shape'] for p in shown],(xx,560,columns-15,470),axis=1,face_only=True)
        fans=[p for p in parts if p['group']=='fans'];sizes=collections.Counter(round(bounds(p['shape'])[3]-bounds(p['shape'])[0]) for p in fans)
        centres=collections.defaultdict(list)
        for p in fans:
            bb=bounds(p['shape']);centres[round((bb[2]+bb[5])/2,3)].append(round((bb[0]+bb[3])/2,3))
        text=' + '.join(f'{n} x {size} mm' for size,n in sizes.items())
        paragraph(c,text+'. Fan screw patterns: 120 -> 105 square; 140 -> 124.5 square; 180 -> 165 square; 80 -> 71.5 square.',xx+20,530,columns-55,11)
        paragraph(c,'Fan centres: '+'; '.join('Z'+fmt(z)+', X'+', '.join(fmt(x) for x in sorted(xs)) for z,xs in sorted(centres.items()))+'.',xx+20,448,columns-55,10)
        paragraph(c,'Direct case fans: short thread-forming screws through the carrier into plastic. Remove mesh for access. Radiator screws must match the cooler and the assumed 38 mm fan depth.',xx+20,386,columns-55,10)
        radii=sorted({round(q['diameter']/2,3) for p in shown for q in holes(p['shape'])})
        paragraph(c,'Circular cut radii R'+', R'.join(fmt(r) for r in radii[:12])+'. Slot end radii and spacing follow the actual cut paths in the part STEP.',xx+20,320,columns-55,9)
    parts=next(iter(variants.values()));cover=[p['shape'] for p in sheet_parts(parts) if p['group']=='intake_grilles']
    projection(c,cover,(40,65,510,240),axis=1,face_only=True)
    stock=next(p for p in parts if p['name'].startswith('Stock_hex_'))
    y=280
    for text in ['Cover construction: 1.5 mm full-face clamping frame, cut-to-size pre-perforated sheet, 5 mm spacers and 0.8 mm large washers. All mesh cut edges overlap the frame by 16 mm.',
        'Stock mesh blank '+ ' x '.join(fmt(v) for v in stock['blank_size_mm'])+' x 0.9144. Assembly holes diameter 3.4 at (X,Z): '+ '; '.join(', '.join(fmt(v) for v in pair) for pair in stock['mounting_holes_xz'])+'.',
        'The stock sheet has no controlled perforation origin. Drill only assembly holes. Do not quote individual mesh holes as laser cuts. Mask coating at electrical bonding contacts.',
        'Cover outer corners R12; opening corners R8; stock mesh corners R8. Rack ears are independent 3 mm folded parts, screwed to the side walls with M4 hardware. Fan plate and mesh do not carry rack loads.']:
        y=paragraph(c,text,590,y,W-650,12)


def card(c,p,rect):
    x,y,w,h=rect;shape=p['shape'];b=bounds(shape)
    c.setStrokeColor(GREY);c.setLineWidth(.4);c.rect(x,y,w,h)
    name=title(p['name']);yy=y+h-15
    c.setFillColor(INK);c.setFont('Helvetica-Bold',10)
    for line in simpleSplit(name,'Helvetica-Bold',10,w-22):c.drawString(x+10,yy,line);yy-=12
    faces=[f for f in shape.Faces() if f.geomType()=='PLANE']
    largest=max(faces,key=lambda f:f.Area());normal=largest.normalAt().toTuple();axis=max(range(3),key=lambda k:abs(normal[k]))
    if p.get('_drawing_mesh'):
        mp=projection(c,[shape],(x+5,y+h*.48,w*.58,h*.42),axis=1,face_only=True)
        stock=p['_drawing_mesh']
        projection(c,[step_shape(q) for q in stock],(x+5,y+28,w*.58,h*.37),axis=1,face_only=True)
        sb=bounds(stock[0]['shape'])
        paragraph(c,f'Mesh: {len(stock)} blank(s), each {fmt(sb[3]-sb[0])} x {fmt(sb[5]-sb[2])} x 0.9144; 92725T3. R3 outer corners; diameter 3.4 clamps. Upper outer notches: 22 x 11. Deburr.',x+12,y+h*.48-4,w*.54,8)
    else:mp=projection(c,[shape],(x+5,y+25,w*.58,h-58),axis=axis,face_only=True)
    if p['group']=='rack_ears':
        projection(c,[shape],(x+w*.39,y+31,w*.17,h-91),axis=1,face_only=True,dim=False)
        paragraph(c,'Rack face: R5 corners',x+w*.37,y+h-46,w*.22,8)
    c.setFont('Helvetica',8);c.drawString(x+18,y+8,'Face coordinates '+' / '.join('XYZ'[k] for k in range(3) if k!=axis)+'; dimensions in mm')
    tx=x+w*.6;tw=w*.38;yy=y+h-58
    yy=paragraph(c,'Formed envelope '+ ' x '.join(fmt(b[k+3]-b[k]) for k in range(3))+'.',tx,yy,tw,9)
    if p['name'].startswith('Crossbar_side_ledge_'):
        yy=paragraph(c,'Top hole axes: 9 apart. Wall hole axes: 12 apart. All four holes diameter 5.41 for M4 press nuts.',tx,yy,tw,9)
    if p['name']=='Removable_chassis_crossbar':
        yy=paragraph(c,'Top pairs: 9 apart, 9.5 from each end; Y offsets 10.5 / 19.5 from front edge.',tx,yy,tw,9)
        rear=cq.Workplane(obj=shape).faces('>Y').val()
        projection(c,[rear],(x+12,y+30,w*.56,90),axis=1,dim=False)
        paragraph(c,'Rear face: 20 holes diameter 4.22; pairs 12 apart, repeating at 40.64.',x+15,y+99,w*.55,8)
    # Hole family leaders annotate the face, while the full CSV retains every centre.
    fs=[f for f in faces if abs(f.normalAt().toTuple()[axis])>.999]
    station=largest.Center().toTuple()[axis]
    hh=[v for v in holes(shape) if v['axis']==axis and abs(v['centre'][axis]-station)<1e-4]
    families=collections.defaultdict(list)
    for item in hh:families[item['diameter']].append(item)
    for diameter,group in sorted(families.items())[:5]:
        label=f'{len(group)} x diameter {fmt(diameter)} (R{fmt(diameter/2)})'
        if abs(diameter-4.22)<.001:label=f'{len(group)} M3 press-nut holes: diameter 4.22 +0.08/-0.00'
        elif abs(diameter-5.41)<.001:label=f'{len(group)} M4 press-nut holes: diameter 5.41 +0.08/-0.00'
        elif abs(diameter-2.5)<.001:label=f'{len(group)} M3 x 0.5 tapped centres; diameter 2.5 pilot'
        elif p['name'].startswith('U_shaped_body') and diameter>15:label=f'{len(group)} formed boss bases diameter {fmt(diameter)}; M3 tapped centres. Do not drill the boss outline.'
        yy=leader(c,mp(group[0]['centre']),label,tx,yy,tw);yy-=2
    other=[e for e in largest.Edges() if e.geomType()=='CIRCLE' and abs(e.Length()-2*math.pi*e.radius())>1e-4]
    if other:yy=paragraph(c,'Arc/slot-end radii: '+', '.join('R'+fmt(v) for v in sorted(set(round(e.radius(),3) for e in other)))+'.',tx,yy,tw,9)
    if p.get('notes'):yy=paragraph(c,p['notes'],tx,yy,tw,9)
    if len(families)>5:yy=paragraph(c,'Additional features are defined in the part STEP and feature-centres.csv.',tx,yy,tw,9)
    # Small axonometric view restores folded side returns absent from the face view.
    if yy>y+75:projection(c,[shape],(tx,y+12,tw,min(yy-y-16,85)),dim=False)


def build(root,modular):
    names=('modular','modular-120-80','modular-180') if modular else ('nine-u','nine-u-180','nine-u-120')
    variants={name:load(root/name) for name in names};parts=variants[names[0]]
    for pp in variants.values():
        rear=next(p for p in pp if p['group']=='rear_vent')
        rear['_drawing_mesh']=[p for p in pp if p['group']=='rear_mesh']
    report=json.loads((root/names[0]/'manufacturing-changes.json').read_text())
    out=root/('module-drawings.pdf' if modular else 'full-chassis-drawings.pdf')
    book=Book(out,'RM53-502 upper module' if modular else '9U full chassis')
    allparts={}
    for name,pp in variants.items():
        for p in sheet_parts(pp):
            if p['name'].startswith(('Stock_hex_', 'Printed_backplane_', 'Front_full_face_', 'Front_fan_carrier', 'Upper_module_front_carrier', 'Full_chassis_upper_intake','Full_width_twenty_one_slot_rear_with_side_returns')):continue
            allparts.setdefault(p.get('drawing_family',p['name']),p)
    rows=list(allparts.values());cols=3;nr=3;cw=(W-70)/cols;ch=(H-155)/nr
    assembly(book,parts,report,modular)
    parts_list(book,variants,rows,root,modular)
    interfaces(book,parts,report,modular);adapter_hardware(book,parts,report);fans(book,variants,modular)
    feature_rows=[]
    for i in range(0,len(rows),cols*nr):
        c=book.page('Part details '+str(i//(cols*nr)+1))
        for j,p in enumerate(rows[i:i+cols*nr]):
            x=35+(j%cols)*cw;y=65+(nr-1-j//cols)*ch
            card(c,p,(x,y,cw-10,ch-8))
    for pp in variants.values():
        for p in sheet_parts(pp):
            for h in holes(step_shape(p)):feature_rows.append(dict(part=p['name'],normal_axis='XYZ'[h['axis']],diameter_mm=h['diameter'],radius_mm=h['diameter']/2,x_mm=h['centre'][0],y_mm=h['centre'][1],z_mm=h['centre'][2]))
    with (root/('module-feature-centres.csv' if modular else 'full-feature-centres.csv')).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(feature_rows[0]));w.writeheader();w.writerows(feature_rows)
    book.finish(out.with_suffix('.index.json'))
    print(out,book.n,'pages',flush=True)


if __name__=='__main__':
    root=Path(sys.argv[1]);build(root,False);build(root,True)

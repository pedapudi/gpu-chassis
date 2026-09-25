"""Dimensioned nominal formed-part drawings with coordinate schedules."""
from pathlib import Path
import sys,io,pickle,json,csv,math,collections,re
import cadquery as cq
import cadquery.occ_impl.exporters.svg as svg_export
from OCP.gp import gp_Ax2,gp_Dir
# Explicit horizontal axes prevent arbitrary rotation of orthographic views.
def engineering_axes(point,direction):
 x,y,z=direction.X(),direction.Y(),direction.Z()
 horizontal=gp_Dir(-y,x,0) if abs(x)+abs(y)>1e-8 else gp_Dir(1,0,0)
 return gp_Ax2(point,direction,horizontal)
svg_export.gp_Ax2=engineering_axes

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
variant=sys.argv[1];root=Path(sys.argv[2])/variant
out=root/'drawings';out.mkdir(exist_ok=True);(out/'coordinates').mkdir(exist_ok=True);(out/'views').mkdir(exist_ok=True)
parts=[]
for a in pickle.loads((root/'parts.brep.pickle').read_bytes()):
 a['shape']=cq.Shape.importBrep(io.BytesIO(a.pop('brep')));parts.append(a)
checks=json.loads((root/'validation.json').read_text())
mod=variant.startswith('modular');fan_size=checks.get('fan_size_mm',120);fan_rows=checks.get('fan_rows',[]);intake_label=' + '.join(f"{r['count']} × {r['size_mm']} × {r['depth_mm']} mm at Z{r['centre_z_mm']:g}" for r in fan_rows);intake_mode=checks.get('full_intake_mode');title='RM53-502 replacement-lid GPU module' if mod else '9U motherboard and GPU chassis'
pdf=out/('rm53-502-module-drawings.pdf' if mod else 'nine-u-chassis-drawings.pdf')
c=canvas.Canvas(str(pdf),pagesize=landscape(A3),pageCompression=1);c.setTitle(title+' | nominal formed geometry');c.setAuthor('');c.setCreator('');c.setProducer('');c.setSubject('Engineering review drawings; fabrication hold points apply')
W,H=landscape(A3);page=0;index=[]
page_audit=[];drawing_marks=0;table_count=0;inside_table=False
for method in ('drawPath','rect','circle'):
 original=getattr(c,method)
 def tracked(*args,_original=original,**kwargs):
  global drawing_marks
  if not inside_table:drawing_marks+=1
  return _original(*args,**kwargs)
 setattr(c,method,tracked)
def finish_sheet():
 if page:
  record=dict(page=page,title=index[-1][1],identity=index[-1][2],tables=table_count,geometry_marks=drawing_marks)
  page_audit.append(record)
  assert table_count==0 or drawing_marks>0 or index[-1][1]=='Fabricated-part drawing index',record

navy=HexColor('#183643');grey=HexColor('#647782');orange=HexColor('#925a26')
style=ParagraphStyle('text',fontName='Helvetica',fontSize=10,leading=14,textColor=navy)
def para(text,x,y,w,size=10):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.35);p=Paragraph(text,st);pw,ph=p.wrap(w,1000);assert y-ph>65,(page,text[:80],y,ph);p.drawOn(c,x,y-ph);return y-ph-10
def table(rows,x,y,widths,size=9):
 global table_count,inside_table
 table_count+=1;inside_table=True
 data=[[Paragraph(str(v),ParagraphStyle('t',parent=style,fontSize=size,leading=size*1.22)) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e6edf0')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.7,grey),('LINEBELOW',(0,1),(-1,-1),.25,HexColor('#cad4d9'))]));tw,th=t.wrap(sum(widths),10000);assert y-th>65,(page,'table overflow',th);t.drawOn(c,x,y-th);inside_table=False;return y-th-15
def new(heading,identity='Assembly'):
 global page,drawing_marks,table_count
 finish_sheet();drawing_marks=0;table_count=0
 if page:c.showPage()
 page+=1;index.append((page,heading,identity));c.setFillColor(navy);c.setFont('Helvetica-Bold',18);c.drawString(32,H-39,heading);c.setFont('Helvetica',9);c.setFillColor(grey);c.drawString(32,H-57,title);c.setStrokeColor(grey);c.setLineWidth(.6);c.line(32,59,W-32,59)
 c.setFont('Helvetica',8);c.drawString(32,43,'Units: mm | Nominal formed geometry | Do not scale | Annotated views and adjacent schedules define nominal geometry')
 c.drawRightString(W-32,43,f'Sheet {page} | 2026-09-22');c.setFillColor(orange);c.drawString(32,28,'ENGINEERING REVIEW — NOT RELEASED FOR FABRICATION');c.setFillColor(navy)
 c.bookmarkPage('page'+str(page));c.addOutlineEntry(heading,'page'+str(page),0)
def view(shape,rect,direction,label,key):
 x,y,w,h=rect;cached=out/'views'/(key+'.svg');svg=cached.read_text() if '--reuse-views' in sys.argv and cached.exists() else cq.exporters.getSVG(shape,{'width':w,'height':h-20,'marginLeft':12,'marginTop':12,'projectionDir':direction,'showAxes':False,'showHidden':True,'strokeWidth':-1,'hiddenColor':(175,184,189),'strokeColor':(24,54,67)})
 path=out/'views'/(key+'.svg');path.write_text(svg);d=svg2rlg(str(path));bx,by,ex,ey=d.getBounds();bw,bh=ex-bx,ey-by
 scale=min((w-80)/max(bw,.01),(h-65)/max(bh,.01));d.scale(scale,scale)
 left=x+40+(w-80-bw*scale)/2;bottom=y+40+(h-65-bh*scale)/2
 renderPDF.draw(d,c,left-bx*scale,bottom-by*scale)
 dd=dims(shape);sizes={(0,0,1):(dd[0],dd[1]),(0,-1,0):(dd[0],dd[2]),(0,1,0):(dd[0],dd[2]),(1,0,0):(dd[1],dd[2])}
 if direction in sizes:
  dw,dh=sizes[direction];right=left+bw*scale;top=bottom+bh*scale
  c.setStrokeColor(grey);c.setFillColor(navy);c.setLineWidth(.4);c.setFont('Helvetica',8)
  c.line(left,bottom-4,left,bottom-17);c.line(right,bottom-4,right,bottom-17);c.line(left,bottom-12,right,bottom-12)
  for xx in (left,right):c.line(xx-2,bottom-14,xx+2,bottom-10)
  c.drawCentredString((left+right)/2,bottom-23,f'{dw:.3f}')
  c.line(right+4,bottom,right+18,bottom);c.line(right+4,top,right+18,top);c.line(right+12,bottom,right+12,top)
  c.saveState();c.translate(right+23,(bottom+top)/2);c.rotate(90);c.drawCentredString(0,0,f'{dh:.3f}');c.restoreState()
 c.setFillColor(navy);c.setFont('Helvetica',9);c.drawString(x,y+5,label)
def bb(s):
 from OCP.BRepBndLib import BRepBndLib
 from OCP.Bnd import Bnd_Box
 box=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,box,False,False);return list(box.Get())
def dims(s):
 b=bb(s);return [b[i+3]-b[i] for i in range(3)]
def clean(n):
 return re.sub(r'(\d)mm',r'\1 mm',re.sub(r'(\d)p(\d)mm',r'\1.\2 mm',n.replace('_',' ')))
def csvwrite(p,fields,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
from annotated_geometry import context_pages, planar, mark, dim
api=(c,new,para,table,view,W,H,out)
new('Assembly release conditions')
y=H-85
y=para('Two serviceable sheet-metal assemblies share a removable twenty-one-position GPU cartridge. The 9U enclosure includes a motherboard layer; the replacement-lid module attaches above an existing RM53-502. The OEM chassis in the modular model is an external size reference only.',32,y,530,12)
rows=[['Dimension','Nominal value'],['Body width / depth','440 / 485'],['Rack face width','482.6'],['Height', f"{checks.get('combined_height_mm',0):.2f} total study envelope; {checks.get('module_height_mm',0):.2f} upper module (5U)" if mod else '399.25 (9 × 44.45 minus 0.80)'],['GPU tray floor Z','242.25' if mod else '170.00'],['Upper slots / card count','21 positions / 10 dual-slot GPUs + 1 single-width card'],['Slot pitch / populated GPU pitch','20.32 / 40.64'],['GPU fans',intake_label if mod else (f"{checks['upper_fan_count']} × {fan_size} × {checks['upper_fan_depth_mm']}, one row" if intake_mode else '6 × 120 × 38, two rows')],['Lower cooling','OEM installation to be measured' if mod else 'XE360-TR5 394 × 120 × 28; 38 mm fan allowance (supplied fans are 25 mm)'],['Backplane PCB','429 × 225 × 2.5; mechanical details from photographs']]
assembly_dimensions=rows[1:]
y=para('Datum: exported X=0 at the body left in the front view; Y=0 at the front-panel plane; Z=0 at the enclosure underside. Front view looks toward +Y. Rear view looks toward -Y. Coordinates in the schedules are assembly coordinates, not developed-blank coordinates.',32,y,530)
right=H-85
for head,body in [('OEM interface hold','The lid return-flange profile, seating width, screw centres and carrying capacity require measurement on the actual RM53-502. OEM side holes are deliberately absent. The adapter cannot yet be called a verified drop-in part.'),('Supplier-interface hold','Backplane hole locations, socket seating height, connector keepouts and latch access are photo estimates. Standard slot pitch is an explicit assumption. The GPU and power-connector envelopes require supplier CAD or a fit sample.'),('Sheet-metal release hold','Bends are formed with inside radius equal to sheet thickness, relief slots at partial bends, and flat patterns developed with K-factor 0.40. Confirm radii, K-factor and forming sequence with the fabricator before cutting blanks. Face-profile DXFs show formed faces; the flat-pattern DXFs are the developed blanks.'),('Qualification hold','No structural load, rail capacity, thermal, vibration or electrical certification is implied. A populated prototype is required. The PSU cable count does not establish a ten-GPU wiring plan.')]:
 right=para('<b>'+head+'</b><br/>'+body,610,right,540,11)
right=para('STEP is the analytic geometry master. OpenSCAD contains individual faceted solids and editable assembly controls. The interactive render uses STLs compiled from those OpenSCAD files. The coordinate schedules identify every analytic circular edge and straight edge in each fabricated part.',610,right,540)
def compound_group(label,selected):
 assert selected,label
 return label,cq.Compound.makeCompound([a['shape'] for a in selected])
assembly_context=[compound_group('Body and end panels',[a for a in parts if a['group']=='shell']),compound_group('GPU cartridge',[a for a in parts if a['group']=='cassette']),compound_group('Intake fans',[a for a in parts if a['group']=='fans']),compound_group('Backplane',[a for a in parts if a['group']=='backplane'])]
assembly_context.append(compound_group('Screw-mounted rack ears',[a for a in parts if a['group']=='rack_ears']))
if mod:assembly_context.append(compound_group('OEM body size reference',[a for a in parts if a['group']=='oem_reference']))
assembly_anchors=[(440,0,checks.get('module_base_z_mm',0)),(461.3,0,checks.get('module_base_z_mm',0)),(440,0,checks.get('combined_height_mm',399.25)),(220,300,242.25 if mod else 170),(220,469,374.46 if mod else 302.21),(220,469,374.46 if mod else 302.21),(220,2,fan_rows[0]['centre_z_mm'] if mod else 270),(220,20,222.25 if mod else 85),(220,330,260.25 if mod else 188)]
context_pages(api,'Assembly dimensions','Assembly',assembly_dimensions,'Nominal installed envelopes. The body and removable GPU tray use the common assembly datum. See component sheets for hole and cutout locations.',assembly_context,assembly_anchors)
new('Assembly projections and installation envelope')
struct=[a['shape'] for a in parts if a['role']=='fabricated' and a['group'] in ('shell','cassette','lid','rear_vent','adapter','rack_ears','intake_grilles')]
shape=cq.Compound.makeCompound(struct)
view(shape,(35,410,540,310),(0,-1,0),'Front | 440 body; 482.6 rack face','assembly_front')
view(shape,(610,410,540,310),(1,0,0),'Right side | 485 nominal body depth','assembly_side')
view(shape,(35,90,540,290),(0,0,1),'Top | lid shown; hidden edges grey','assembly_top')
view(shape,(610,90,540,290),(1,-1,1),'Isometric | schematic projection','assembly_iso')
new('Exterior rear view and component handedness')
rear_parts=[a['shape'] for a in parts if a['group'] in ('shell','cassette','rear_vent','psu','io_shield','retimers','brackets','exhaust','external_entry') and (a['shape'].Center().y>400 or a['group'] in ('psu','retimers','brackets','exhaust'))]
view(cq.Compound.makeCompound(rear_parts),(35,225,1100,485),(0,1,0),'EXTERIOR REAR: observer at +Y, looking toward -Y; left on this page is large X','assembly_rear_exterior')
para('Every rear-panel elevation uses an exterior viewpoint. The full chassis reads PSU at left, motherboard I/O and exhaust in the middle, and eight lower PCIe apertures at right. Looking at the inside face reverses that order. This is a change of viewpoint, not a reflected manufactured part.' if not mod else 'The twenty-one upper bracket positions face the exterior rear. The backplane, card brackets and retention flanges share the same assembly coordinates. The lower OEM body is only an external size reference.',40,205,1100,12)
para('Front elevations are viewed from -Y. Rear elevations are viewed from +Y. Top elevations are viewed from +Z, with the rear (+Y) toward the top of the page. Match the labeled viewpoint before comparing a drawing with a product photograph.',40,130,1100,11)
new('Assembly sequence and accessible fasteners')
steps=[('Prepare fabricated parts','Deburr passages and form panels and bosses. Extrude and tap every formed thread after the adjacent bends are made; the GPU shelf collars follow the shelf bend. Keep threads masked during finishing. Screw on the separate rack ears with M4 × 10 screws into the tapped body-wall threads.'),('Fit the motherboard tray','Screw the ten 8 mm M3 male–female standoffs into the tapped tray threads from above. Screw the tray down onto its four tapped floor bosses before fitting the motherboard and the lower exhaust fans; one fan covers a rear tray screw.'),('Fit lower hardware before the upper bearings','Install PSU from above before bolting the side bearing angle beside it. Install motherboard, pump/block, AIO, retimers and lower harnesses with the GPU cartridge removed. The PSU can be serviced by removing that bearing angle. For retimer screw access, remove the cartridge and external MCIO entry frame, brush strips and its two screws.'),('Prepare the GPU cartridge on the bench','Load standard DIN 562 M4 square nuts into the rail guides, then screw the rails onto the four tapped tray bosses. Secure posts to loose crossbars from below. Position crossbars with top-access M4 screws before installing the PCB.'),('Install backplane and GPUs','Position each crossbar/post beneath a verified mounting hole; support only permitted board locations. Attach the PCB with top M3 × 6 screws. Fit GPUs and rear #6-32 screws. Actual latch reach and release force require a physical board check.'),('Route and close','Route MCIO and GPU power through the wide forward passages, restrain bundles at the side angles, and leave service loops. Connect after the cartridge is seated. Fit the rear perforated cover and side-fastened lid last.'),('Remove cartridge','Power down and disconnect all cartridge cables. Loosen the four lid thumbscrews and the rear-cover thumbscrews, remove the lid and rear cover, then the four front hold-down screws and four rear side screws. Lift the cartridge vertically; do not pull it against connected hoses or cables.')]
if mod:
 steps[1]=('Transfer the OEM interface','Remove the original lid. Measure its seating profile and hole centres using the adapter measurement schedule. Verify rack-rail support and OEM load capacity before drilling the adapter or mounting a populated module.')
 steps[2]=('Attach adapter before upper components','Fix the adapter to the OEM body using the verified original interface. Attach the empty upper U-body to the adapter from above, into the tapped adapter threads. Install the bearing angles, rails, fans and cartridge only after these screws are tightened; the side bearing angles cover four of them.')
if mod:
 steps[-2]=('Route cables and close the rear entry','Internal MCIO and power enter through the floor. For external MCIO, remove the two upper cap screws and folded brush cap. Feed plugs through the 140 × 17.55 rear notch; refit the cap around the cables. Lower screws retain the U-frame.')
 steps[-1]=('Remove GPUs or cartridge','Disconnect external cables first. Remove lid and rear cover with its brush assembly. Disconnect and park internal harnesses. Release GPU brackets for individual cards, or the four front and four rear tray screws for cartridge lift.')
y=H-90
for i,(h,t) in enumerate(steps,1):y=para(f'<b>{i}. {h}</b><br/>{t}',36,y,W-80,12)
new('Catalog fasteners and standoff stack sections')
rows=[['Joint','Standard hardware','Nominal stack / access'],['Motherboard posts','M3 × 8 mm male–female hex standoff, 5 mm AF, 6 mm stud','Stud threads into an extruded M3 thread in the 2 mm tray: 3.5 engagement. Upper M3 × 5: 0.5 washer + 1.57 PCB → 2.93 engagement.'],['Backplane posts','Harwin R30-1000802; 8 mm, M3 female–female, 5 mm AF','Lower M3 × 6: 0.5 washer + 2 crossbar → 3.5 engagement. Upper M3 × 6: 0.5 washer + 2.5 PCB → 3.0 engagement. Tip gap 1.5.'],['Crossbar clamp','M4 × 8 pan-head; DIN 562 M4 square thin nut, 7 AF × 2.2','4 mm combined crossbar/rail, full 2.2 mm nut engagement. Nuts remain between guide strips. Tighten before the PCB is installed.'],['Rail boss','M4 × 6 pan-head','2 rail on a 4.5 mm boss formed in the GPU tray; 1.5 boss top + 1.5 extruded collar → 3.0 thread engagement.'],['PCIe retention','6-32 UNC × 1/4 in; no nuts','GPU shelf: integral 1.2 mm bend with 21 extruded collars tapped #6-32 UNC-2B, 2.5 thread length. Lower bank: separate 1.5 mm strip with eight extruded collars tapped #6-32 UNC-2B, 3.0 thread length. Tap drill 2.705.'],['Panels, brackets and lid','M3 and M4 pan-head screws into extruded tapped threads; captive knurled M3 thumbscrews for the lid and rear covers','Each former nut position is an extruded collar in the sheet that held the nut: M3 tap drill 2.5, M4 tap drill 3.3, collar one sheet thickness tall (1.5 maximum). Thumbscrew ferrules press into DIA6.4 holes in the body walls.'],['Chassis fan mounts','5 × 8 self-tapping plastic fan screws; no nuts','2 carrier leaves 6 mm nominal penetration into GPU fan plastic. Rear 1.2 panel leaves 6.8 mm. No inlet spacers. Grille access holes: 8.8 mm. Use fan-approved screws; AIO hardware is separate.']]
if mod:rows[-1]=['GPU fan mounts','5 × 8 self-tapping plastic fan screws; no nuts','Padded 120/140 mm fans: 2 carrier + 1 front pad leave 5 mm penetration. 80/180 mm fans: 2 carrier leaves 6 mm. '+'; '.join(f"{r['size_mm']} mm: {r['hole_pitch_mm']:g} square pitch" for r in fan_rows)+'. Use fan-approved screws.']
y=table(rows,32,H-85,[160,315,650],10)
y=para('Screw envelopes use the nominal major diameter; helical threads, drive recesses and weld beads are omitted. Every screw that fastens into sheet engages a formed thread, so no nut is held behind a sheet. The only loose nuts are the DIN 562 square nuts that slide in the backplane rail channels.',32,y,1125,11)
# Cross-section stack schematic with independent dimension labels.
for x,label,pcb,top in [(55,'Motherboard',1.57,5),(610,'GPU backplane',2.5,6)]:
 z0=90;scl=9;c.setFont('Helvetica-Bold',12);c.drawString(x,z0+165,label+' post stack')
 for level,thick,color,txt in [(0,2,'#aebbc6','2.00 sheet'),(2,8,'#b39a61','8.00 catalog post'),(10,pcb,'#216b55',f'{pcb:.2f} PCB'),(10+pcb,.5,'#647783','0.50 washer')]:
  c.setFillColor(HexColor(color));c.rect(x+25,z0+level*scl,110 if level!=2 else 38,thick*scl,fill=1,stroke=0);c.setFillColor(navy);c.setFont('Helvetica',10);c.drawString(x+155,z0+(level+thick/2)*scl,txt)

y=H-85
rows=[['Feature','Nominal value / constraint'],['Crossbar standoff X travel','32 to 408 in construction X, equivalent to exported X 408 to 32. Six posts selected; quantity/location must follow supplier board drawing.'],['Crossbar Y travel','169.5 to 390.5 construction Y, exported Y 222.7 to 443.7. End limits keep the 7 mm square nut fully inside the guide strips.'],['Selected crossbar Y','225.0, 318.5, 434.2 exported coordinates.'],['Rail nut guide gap','7.2 for nominal 7.0 square nut. Verify nut tolerance and coating allowance before release.'],['Populated socket centres','40.64 pitch, ten GPU positions; rear bracket pitch 20.32. A single-width socket lies 20.32 beyond each end GPU. The 21 rear positions align with all twelve sockets. Position 21 serves the leading socket; position 1 serves either the GPU 10 cooler side or the trailing socket.'],['Card/bracket relationship','Bracket centre offset 7.155 from card plane; retention screw 2.055 from card plane on the opposite side. Same datum used for sockets and chassis.'],['Bracket bearing height','374.46 in module; 302.21 in full chassis. Lower motherboard bracket bearing 129.28.'],['Backplane support heights','Tray underside is the datum. Tray top = datum +1.5; rail top = datum +8; crossbar top = datum +10; PCB underside = datum +18. See installed-level schedule.'],['PCB mounting details','Obround holes and component details are photo estimates. Sliding supports accommodate variable holes but do not correct a different socket-to-bracket datum.']]
context_pages(api,'Adjustable backplane supports','Assembly',rows[1:],'Set the board from the GPU bracket datum, then move supports to verified holes. Check underside component clearance and latch access on the physical board.',[(a['name'].replace('_',' '),a['shape']) for a in parts if 'Longitudinal_mount_rail' in a['name'] or 'Sliding_crossbar' in a['name'] or a['name'] in ('Miwin_MG_SW510B_429x225_PCB_photo_reference','Full_width_twenty_one_slot_rear_with_side_returns','M3_8mm_female_female_standoff_1')],[(220,226.75,252.25 if mod else 180),(420,318.5,250.25 if mod else 178),(220,318.5,252.25 if mod else 180),(420,300,246.45 if mod else 174.2),(389,350,262.75 if mod else 190.5),(22,474.08,374.46 if mod else 302.21),(220,474.08,374.46 if mod else 302.21),(357,225,260.25 if mod else 188),(357,225,262.75 if mod else 190.5)])
if not mod:
 new('Motherboard mounting coordinates — SSI EEB reference')
 y=para('Ten nominal SSI EEB locations are selected to match the ten holes circled in the ASUS WRX90E-SAGE SE manual (printed page 2-13). SSI EEB 2011 v1.0.1 Figure 2 gives the dimensional datum. The motherboard PCB underside is Z16.00; tray top Z8.00; standard posts 8.00. The hole map below uses the exported assembly datum.',32,H-85,1120,12)
 rows=[['SSI location','X','Y','Tray clearance bore']]+[[a['name'],f"{a['x']:.2f}",f"{a['y']:.2f}",'3.40'] for a in checks['motherboard_nominal_holes']]
 table(rows,32,y,[115,105,105,155],11)
 tray=next(a for a in parts if a['name']=='WRX90_board_specific_replaceable_tray')
 p,_,_=planar(c,tray['shape'],2,6,(565,205,580,440))
 for hole in checks['motherboard_nominal_holes']:
  xx,yy=p(hole['x'],hole['y']);c.setFont('Helvetica',8);c.drawString(xx+5,yy+5,hole['name'])
 para('The integrated I/O shield seating and the actual board tolerances remain fit checks. Do not add standoffs at unused ATX/EEB positions: an extra post can contact motherboard circuitry. Other motherboard formats require a separate verified tray and rear-interface check.',575,175,555,11)
 csvwrite(out/'motherboard_holes.csv',['name','x','y'],checks['motherboard_nominal_holes'])
else:
 new('RM53-502 OEM interface — measurement drawing')
 a=next(a for a in parts if a['group']=='adapter');view(a['shape'],(30,280,665,430),(1,-1,1),'Adapter ring; OEM side holes intentionally absent','adapter_measure')
 rows=[['Measurement required','Model status'],['Body seating width/depth','440 / 485 external reference only'],['Original lid thickness and return offset','Unmeasured; 1.5 sheet is a design assumption'],['Return-flange height / length','Unmeasured; model 15 / 445'],['Left and right OEM screw centres','Unmeasured; no OEM holes supplied'],['Tongues, hems, rebates and edge relief','Unmeasured; not represented'],['Lid seating plane / gasket compression','220 + 1.5 adapter + 0.75 gasket is provisional'],['Adapter carrying capacity / rail support','Unqualified; populated upper module requires load review']]
 table(rows,720,H-85,[200,230],11)
 para('Place the removed OEM cover on a flat datum. Record every side screw centre from its front edge and seating plane, separately for left and right. Record flange thickness, offset, engagement and all tabs. Transfer the verified pattern to the parameterized adapter source; do not drill from this provisional drawing.',32,240,660,12)
 para('The six module-to-adapter holes are design dimensions: X=10 and 430; Y=80, 242.5 and 410; diameter 3.4. Those are separate from the unknown OEM screws. Attach the empty module before its internal components obstruct these top-access screws.',720,225,430,11)

rows=[['Check','Result / limitation'],['Analytic solids','Every source solid must pass BRep validity and positive-volume checks. Exact solid intersections are listed in validation reports.'],['Part-to-part checks','All non-alternative parts are compared; intended reference contacts and OEM proxy overlap are recorded separately. Do not interpret excluded proxy volume as a verified OEM interior.'],['OpenSCAD / STEP agreement','Each SCAD part is compiled to STL. Watertightness, positive volume and bounds are compared against the source tessellation. Analytic STEP remains the dimensional master.'],['Service motion','Cartridge and card paths are sampled at the reported positions. Driver-access checks use the documented assembly order. These do not certify flexible cable bends or physical latch operation.'],['PSU clearance','Side bearing M3 × 6 screw tip to PSU nominal envelope: 0.5 mm. Tolerance-sensitive; verify before fabrication.'],['Fan / I/O carrier','80 mm exhaust bottom Z70; I/O carrier top Z68: 2.0 mm nominal.'],['GPU neighbor clearance','40.64 pitch minus 40.00 width = 0.64 mm nominal. Supplier dimensional tolerance required.'],['Single-width card clearance','CEM single-width envelope (2.67 secondary, 14.47 primary component height) to GPU 1: 1.61 mm nominal. Longer or thicker cards require a fit check.'],['Power cables','Forward connectors and a 35 mm straight lead are occupancy allowances. Select actual cables; check their bend radius, plug latch and connector approach.'],['Cooling','Selectable full-chassis intake: six 120 mm, two 180 mm or three 120 mm. Module: 3 × 140, 3 × 120 with five 80 mm above, or 2 × 180 mm. One full-face grille per fabricated front face, including the AIO area in 9U. Uniform 9 mm perforations on 10 mm staggered pitch; lands retained around fasteners. Thermal performance is unqualified.'],['Backplane / OEM measurements','Hole locations and plug/slot details from photos are not precision mechanical evidence. OEM lid holes/profile remain unmeasured.']]
if mod:
 rows=[row for row in rows if row[0] not in ('PSU clearance','Fan / I/O carrier')]
 rows.insert(4,['Fan intake',intake_label+'. Each option has its own carrier; frames clear adjacent frames, the lid and the carrier returns.'])
 rows.insert(5,['Rear MCIO plug',f"35 × 14 mm envelope passes with the upper cap removed. Lid gap 1.05 mm; GPU-envelope gap {checks['MCIO_opening_z_mm'][0]+2.5-checks['GPU_envelope_top_z_mm']:.2f} mm. Check physical latch and cable bend radius."])
clearance_rows=rows[1:]
clearance_shapes=[compound_group('GPU and single-width card envelopes',[a for a in parts if a['name'] in ('GPU_1_Max_Q_envelope','GPU_2_Max_Q_envelope','Auxiliary_socket_1_single_width_card_envelope')]),compound_group('Lid',[a for a in parts if a['group']=='lid']),compound_group('Front fans',[a for a in parts if a['group']=='fans']),compound_group('GPU power plugs and leads',[a for a in parts if a['group']=='power'])]
if not mod:
 clearance_shapes.extend([compound_group('PSU and bearing screw',[a for a in parts if a['group']=='psu' or a['name']=='Side_ledge_M3x6_1.5_390']),compound_group('Rear fans and I/O carrier',[a for a in parts if a['group']=='exhaust' or a['name']=='Flat_1p2mm_IO_carrier_with_clear_shield_lands'])])
else:clearance_shapes.append(compound_group('Rear cable entry',[a for a in parts if a['group']=='external_entry']))
clearance_anchors=[]
for label,_ in clearance_rows:
 if label=='PSU clearance':q=(434.25,443.2,158)
 elif label=='Fan / I/O carrier':q=(209,470,69)
 elif label=='GPU neighbor clearance':q=(369.015,300,330 if mod else 258)
 elif label=='Single-width card clearance':q=(410.14,300,330 if mod else 258)
 elif label=='Rear MCIO plug':q=(220,485,checks['lid_underside_z_mm']-1.5)
 elif label=='Fan intake' or label=='Cooling':q=(220,2,fan_rows[0]['centre_z_mm'] if mod else 270)
 elif label=='Power cables':q=(389,195,300 if mod else 228)
 else:q=(389,300,330 if mod else 258)
 clearance_anchors.append(q)
context_pages(api,'Nominal clearances and verification scope','Assembly',clearance_rows,'Numbered leaders locate the components involved in each check. Geometry shows installed positions; the nominal gap dimensions below still require supplier tolerances and physical validation.',clearance_shapes,clearance_anchors)
new('Engineering references')
sources=[('Motherboard hole selection','ASUS Pro WS WRX90E-SAGE SE manual, printed page 2-13','https://dlcdnets.asus.com/pub/ASUS/mb/SocketsTR5/Pro_WS_WRX90E-SAGE_SE/E22564_Pro_WS_WRX90E-SAGE_SE_EM_WEB.pdf'),('Motherboard dimensional datum','SSI EEB 2011 v1.0.1, Figure 2','https://www.snia.org/sites/default/files/SSIF/2018-05-31/SSI%20EEB%202011%201.0.1.pdf'),('Backplane standoff','Harwin R30-1000802; M3 through thread, 8 mm, 5 mm AF','https://www.harwin.com/products/R30-1000802'),('Fan spacing','ARCTIC P12 engineering drawing: 120 mm frame, 105 mm mounting pitch','https://support.arctic.de/p12'),('PSU envelope','ASUS Pro WS 3000P technical specifications','https://www.asus.com/my/motherboards-components/power-supply-units/workstation/asus-pro-ws-3000p/techspec/'),('Radiator envelope','SilverStone XE360-TR5 technical specifications','https://www.silverstonetek.com/en/product/info/coolers/xe360_tr5/'),('OEM body dimensions','SilverStone RM53-502; external envelope only','https://www.silverstonetek.com/en/product/info/computer-chassis/rm53_502/'),('Backplane reference','Miwin 12-slot PCIe 5.0 switch GPU expansion board; product photos and overall dimensions','https://www.miwinchina.com/product/12slot-pcie-50-switch-gpu-expansion-board.html')]
if mod:sources[3]=('Fan mounting envelope','Noctua NF-A14: 124.5 square; NF-A12x25: 105 square; NF-A8: 71.5 square; SilverStone AP183: 165 square. See the intake option schedule.','https://www.noctua.at/en/products/nv-fm1')
if intake_mode=='2x180':sources[3]=('Fan mounting envelope','SilverStone AP183: 180 × 180 × 32; 165 square pitch; DIA175 panel opening','https://www.silverstonetek.com/upload/goods_cable_define/fan-cable-define.pdf')
y=H-85
for h,t,url in sources:y=para(f'<b>{h}</b> — {t}<br/><link href="{url}" color="#17647b">{url}</link>',32,y,1120,10)
if mod:
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
 from build_modular import INTAKES,GRILLE_FIX
 fz=fan_rows[0]['centre_z_mm'];top=checks['combined_height_mm'];notch,lid=checks['MCIO_opening_z_mm']
 plug_gap=notch+2.5-checks['GPU_envelope_top_z_mm']
 carrier=next(a for a in parts if a['name'].startswith('Upper_module_front_carrier_'))
 rows=[['Interface','Dimensions and assembly'],['Upper module',f"440 wide × {checks['module_height_mm']:.2f} high (5U); base Z222.25; top Z{top:.2f}. GPU tray remains Z242.25. Clearance above the GPU envelopes {checks['clearance_above_GPU_envelope_mm']:.2f}."],['Fan rows',intake_label],['Mounting','5.5 wide clearance obrounds; axes closer than 25 share one slot. Short self-tapping screws through the carrier'+(' and front pads.' if any(r['padded_envelope_mm'] for r in fan_rows) else '.')],['Rear entry',f'Notch X150–290, Z{notch:.2f}–{lid:.2f}, top-open. Remove folded cap to expose the full aperture. Its return projects to Y494, 9 mm beyond the body.'],['Connector passage',f'35 × 14 plug, Z{notch+2.5:.2f}–{notch+16.5:.2f}. Nominal lid gap 1.05; GPU-envelope gap {plug_gap:.2f}. Larger plugs require a different entry.'],['Brush frame','Lower U-frame and upper folded cap are separate 1.5 mm sheet parts. Two lower M3 screws retain the base; two upper M3 screws release the cap.'],['GPU service','Disconnect and withdraw external cables; remove lid and complete rear cover/brush assembly before GPU or cartridge lift.'],['Airflow','Front contains only fan intake openings and mounting features. Fan selection and airflow distribution require thermal validation.']]
 r0=fan_rows[0];m0=r0['hole_pitch_mm']/2;x0=r0['centres_x_mm'][0]
 context_pages(api,'Intake option and rear cable entry','Assembly',rows[1:],'The front intake and rear cable opening use separate panels. Remove the brush cap to pass connectors; unplug cables before removing GPUs.',[(a['name'].replace('_',' '),a['shape']) for a in parts if a is carrier or a['name']=='Upper_module_rear_perforated_cover'],[(440,0,222.25),(220,0,fz),(x0+m0,0,fz+m0),(220,485,notch),(220,485,notch+9),(143,485,notch+9.5),(297,485,notch+9.5),(220,0,fz)])
 def row_text(r):return f"{len(r['xs'])} × {r['size']} × {r['depth']}; centres X{', '.join(f'{x:g}' for x in r['xs'])}; Z{r['z']:g}; {r['pitch']:g} square pitch; DIA{r['opening']:g} openings"
 rows=[['Option','Fan rows','Reference model']]+[[k.replace('_',' + '),'<br/>'.join(row_text(r) for r in v),', '.join(r['model'].replace('_',' ') for r in v)] for k,v in INTAKES.items()]
 new('Module intake options | carriers and fan rows','Assembly')
 para('Each intake option has its own removable front carrier, fastened by four M3 screws per side through the body into extruded tapped threads in the carrier returns. One full-face grille serves all options: it has 8.8 mm tool-access holes at every fan screw axis of every option and five M3 fixings on lands clear of all fan frames.',32,H-82,W-64,11)
 table(rows,32,H-150,[80,450,200],9)
 grille=next(a for a in parts if a['name']=='Upper_module_full_face_1mm_perforated_grille')
 planar(c,grille['shape'],1,-1,(790,330,380,380))
 c.setFont('Helvetica',9);c.drawString(800,320,'Common grille, front face: access holes for every option')
 para('To change option: remove the grille, unscrew the fans, remove the side screws and withdraw the carrier forward, then fit the other carrier, fans and grille. Padded 120 and 140 mm fans sit on 1 mm front pads, leaving 5 mm screw penetration into the plastic frame; 80 and 180 mm frames seat directly on the 2 mm carrier, leaving 6 mm. Confirm screw suitability with each fan supplier.',32,300,W-64,11)
 para('Grille fixings X/Z: '+'; '.join(f'({x:g}, {z:g})' for x,z in GRILLE_FIX)+'. The 80 mm row occupies Z361–441, directly below the Z442.5 lid underside. Front fans lie ahead of the GPU bodies, so their height is limited by the lid and floor only.',32,200,W-64,11)
 for r in fan_rows:
  new(f"Front carrier | {r['size_mm']} mm mounting pattern",carrier['name']+'::fan-pattern')
  p,lo,hi=planar(c,carrier['shape'],1,0,(35,150,760,530))
  x=r['centres_x_mm'][0];z=r['centre_z_mm'];m=r['hole_pitch_mm']/2
  dim(c,p(x-m,z-m),p(x+m,z-m),f"{r['hole_pitch_mm']:.3f} centres",offset=45)
  dim(c,p(x-m,z-m),p(x-m,z+m),f"{r['hole_pitch_mm']:.3f} centres",True,offset=-60)
  mark(c,p(x+m,z+m),f"{r['size_mm']} mm fan mounting axes",(830,580))
  para(f"{r['count']} fan centres: X{', '.join(f'{v:g}' for v in r['centres_x_mm'])}; Z{z:g}. Air openings DIA{r['air_opening_diameter_mm']:g}. The shared obrounds join adjacent fan screw positions. See the face feature sheets for all slot lengths, widths and radii.",830,530,310,11)
  para('Carrier viewed in X/Z assembly coordinates. Fan pattern centres are referenced to the actual cut contours.',35,125,1080,10)
from section_drawings import draw_sections,material_note
from interface_drawings import interface_details
from feature_drawings import draw_feature_pages
from rear_drawings import rear_details, enlarged_details
from flat_drawings import flat_pattern_pages
rear_details(parts,root,(c,new,para,table,view,W,H,out))
enlarged_details((c,new,para,table,view,W,H,out))
interface_details(parts,mod,(c,new,para,table,view,W,H,out))
if not mod:
 from drawing_annotations import lower_rear_sheet
 lower_rear_sheet(parts,(c,new,para,table,view,W,H,out))
 enlarged_details((c,new,para,table,view,W,H,out),lower=True)
if intake_mode:
 from drawing_annotations import intake_sheet
 intake_sheet(parts,checks,(c,new,para,table,view,W,H,out))
from clearance_drawings import clearance_details
clearance_details(parts,mod,api)
coverage=[]
# Each fabricated sheet-metal part receives a drawing and exact coordinate schedule.
fasttokens=('nut','screw','standoff','washer','M3','M4')
fabricated=[a for a in parts if a['role']=='fabricated' and a['group'] not in ('fasteners','intake_fasteners','adapter_fasteners','hold_downs','rear_release','partition_screws','lid_screws','lid_guides') and (not any(t in a['name'] for t in fasttokens) or '_guide_strip_' in a['name'])]
part_rows=[]
for idx,a in enumerate(fabricated):
 name=a['name'];s=a['shape'];b=bb(s);d=dims(s);new(clean(name),name)
 (root/'formed_parts').mkdir(exist_ok=True)
 if not (root/'formed_parts'/(name+'.step')).exists():cq.exporters.export(s,str(root/'formed_parts'/(name+'.step')))
 view(s,(35,412,530,300),(0,0,1),'Top (+Z) | hidden edges grey',name+'_top')
 rear_part=('rear' in name.lower() or 'IO_' in name or 'IO_carrier' in name)
 view(s,(610,412,540,300),(0,1,0) if rear_part else (0,-1,0),'Exterior rear (+Y) | looking toward -Y' if rear_part else 'Exterior front (-Y) | looking toward +Y',name+'_elevation')
 view(s,(35,95,530,280),(1,0,0),'Right (+X)',name+'_right')
 view(s,(610,95,540,280),(-1,1,1) if rear_part else (1,-1,1),'Isometric from exterior rear' if rear_part else 'Isometric from exterior front',name+'_iso')
 text=f'Overall X × Y × Z: {d[0]:.3f} × {d[1]:.3f} × {d[2]:.3f} mm. Datum minimum: ({b[0]:.3f}, {b[1]:.3f}, {b[2]:.3f}).'
 para(text,35,H-82,1120,10)
 radii=sorted({round(e.radius()*2,4) for e in s.Edges() if e.geomType()=='CIRCLE'})
 para('Reference edge diameters (not a hole schedule): '+(', '.join(f'{q:.3f}' for q in radii) if radii else 'none')+' mm. See following hole/cutout sheets for sizes, radii and centres.',35,H-99,1120,9)
 thickness=1.5
 if any(t in name for t in ('1p2mm','_guide_strip_')) or name=='Full_width_twenty_one_slot_rear_with_side_returns':thickness=1.2
 if any(t in name for t in ('Longitudinal_mount_rail','Sliding_crossbar','WRX90_board_specific','Front_fan_carrier','Upper_module_front_dual','Full_chassis_upper_intake_insert')):thickness=2.0
 if 'Screw_mounted_3mm' in name:thickness=3.0
 if '1mm_perforated_grille' in name or '1mm_blanking_plate' in name:thickness=1.0
 c.setFont('Helvetica',8);c.setFillColor(navy);c.drawString(35,389,'Feature coordinates: drawings/coordinates/'+name+'.csv')
 para(material_note(name),35,377,1120,9)
 features=[]
 for e in s.Edges():
  typ=e.geomType()
  if typ=='CIRCLE':
   curve=e._geomAdaptor();cc=curve.Circle();p=cc.Location();v=cc.Axis().Direction();features.append(dict(type='CIRCLE_OR_ARC',x=p.X(),y=p.Y(),z=p.Z(),radius=cc.Radius(),axis_x=v.X(),axis_y=v.Y(),axis_z=v.Z(),end_x='',end_y='',end_z='',length=e.Length()))
  elif typ=='LINE':
   p=e.startPoint();q=e.endPoint();features.append(dict(type='LINE',x=p.x,y=p.y,z=p.z,radius='',axis_x='',axis_y='',axis_z='',end_x=q.x,end_y=q.y,end_z=q.z,length=e.Length()))
 fields=['type','x','y','z','radius','axis_x','axis_y','axis_z','end_x','end_y','end_z','length'];csvwrite(out/'coordinates'/(name+'.csv'),fields,features)
 part_rows.append({'name':name,'drawing_sheet':page,'group':a['group'],'x_mm':d[0],'y_mm':d[1],'z_mm':d[2],'volume_mm3':s.Volume(),'analytic_edge_records':len(features)})
 draw_feature_pages(a,(c,new,para,table,view,W,H,out))
 record=draw_sections(a,(c,new,para,table,view,W,H,out))
 record['flat_pattern_sheets']=flat_pattern_pages(name,root,(c,new,para,table,view,W,H,out))
 coverage.append(record)
 print('Drawing',idx+1,'/',len(fabricated),name,flush=True)
# BOM lists every individual modeled item; bought items remain reference envelopes.
fields=['name','group','role','quantity','moves_with_cartridge'];bom=[{k:a[k] for k in ('name','group','role')}|{'quantity':1,'moves_with_cartridge':a['moving']} for a in parts if a['role']!='clearance' and a['group']!='board_alternatives'];csvwrite(out/'assembly_bom.csv',fields,bom)
csvwrite(out/'fabricated_part_schedule.csv',list(part_rows[0]),part_rows)
for start in range(0,len(part_rows),24):
 new('Fabricated-part drawing index')
 rows=[['Part identifier','Sheet','Group','Overall X × Y × Z']]+[[a['name'],a['drawing_sheet'],a['group'],' × '.join(f'{a[k]:.2f}' for k in ('x_mm','y_mm','z_mm'))] for a in part_rows[start:start+24]]
 table(rows,32,H-85,[640,55,140,285],9)
(out/'specificity_coverage.json').write_text(json.dumps(coverage,indent=2))
finish_sheet();(out/'diagram_completeness.json').write_text(json.dumps(page_audit,indent=2))
c.save();(out/'drawing_manifest.json').write_text(json.dumps({'pdf':pdf.name,'pages':page,'fabricated_parts':len(fabricated),'drawing_index':index,'status':'engineering review; fabrication holds apply'},indent=2));print('PDF',pdf,page,'pages',flush=True)

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad_source'))
from gpu_geometry import neutral_headers
neutral_headers(root)

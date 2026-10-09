"""Complete interchangeable 9U fan plates with common side mounting datums."""
import cadquery as cq
from mounting_hardware import box, cyl, union
from full_intake import settings, slot, GRILLE_FIXES


def apply(parts, report):
    inserts=[p for p in parts if p['name'].startswith('Full_chassis_upper_intake_insert_')]
    if not inserts:
        return report.get('complete_front_plate')
    assert len(inserts)==1
    mode=inserts[0]['name'].rsplit('_',1)[1]
    spec=settings(mode)
    carrier=next(p for p in parts if p['name']=='Front_fan_carrier_with_side_returns')
    original=carrier['shape']
    # Preserve the formed side angles, their nut seats and cover mounting stack.
    ends=[original.intersect(box(x,-1,-1,21,22,402)) for x in (0,419)]
    cuts=[cyl(x,-1,85,58,5,(0,1,0)) for x in (100,220,340)]
    for z in (32.5,137.5):
        cuts.extend(slot(x,-1,z,length,4.8,5) for x,length in ((47.5,9),(160,24),(280,24),(392.5,9)))
    cuts.extend(cyl(x,-1,270,spec['opening']/2,5,(0,1,0)) for x in spec['x_centres'])
    positions=((45.5,9),(220,24.5),(394.5,9)) if mode=='2x180' else ((47.5,9),(160,24),(280,24),(392.5,9))
    for z in (270-spec['pitch']/2,270+spec['pitch']/2):
        cuts.extend(slot(x,-1,z,length,5.5,5) for x,length in positions)
    cuts.extend(cyl(x,-1,z,2.11,6,(0,1,0)) for x,z in GRILLE_FIXES)
    face=box(0,0,0,440,2,399.25).cut(cq.Compound.makeCompound(cuts))
    carrier['shape']=union([face,*ends]).clean()
    assert carrier['shape'].isValid()
    carrier.pop('pieces',None)
    carrier['tapped']=[q for q in carrier.get('tapped',[]) if q['centre'][0] in (15.,425.)]
    report['panel_threads']=[q for q in report['panel_threads'] if not (q['host']==carrier['name'] and q['centre'][0] in (30.,410.))]
    carrier['notes']='Complete 440 x 399.25 fan plate; 2 mm face joined to 1.5 mm formed side angles. Ten M3 side joints and eight mesh-cover joints are common to all 9U fan configurations.'
    removed=[]
    for p in parts:
        n=p['name']
        is_insert=n.startswith(('Full_chassis_upper_intake_insert_','Intake_insert_'))
        is_nut=n.startswith('PEM_M3_Front_fan_carrier_with_side_returns_') and int(n.rsplit('_',1)[1])<=6
        if is_insert or is_nut:removed.append(n)
    assert len(removed)==13,removed
    parts[:]=[p for p in parts if p['name'] not in removed]
    report['complete_front_plate']=dict(mode=mode,face_size_mm=[440,399.25],face_thickness_mm=2,
        side_mount_centres_yz_mm=[[12,z] for z in (22,148,205,290,381.45)],
        side_thread='M3',mesh_fixings_xz_mm=GRILLE_FIXES,removed_parts=removed)
    return report['complete_front_plate']

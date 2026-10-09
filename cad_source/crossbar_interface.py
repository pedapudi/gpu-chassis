"""Attachment datums for custom printed supports on the removable crossbar."""
from sheetmetal import bounds


def describe(parts):
    bar=next(p for p in parts if p['name']=='Removable_chassis_crossbar')
    b=bounds(bar['shape'])
    nuts=[p for p in parts if p['name'].startswith('Custom_support_PEM_M3_')]
    assert len(nuts)==20
    points=[]
    for nut in nuts:
        n=bounds(nut['shape'])
        points.append([(n[0]+n[3])/2,b[4],(n[2]+n[5])/2])
    points.sort()
    local=[[round(point[i]-b[i],6) for i in range(3)] for point in points]
    return dict(thread='M3 x 0.5',press_nut='95185A530',quantity=20,
                pair_count=10,pair_spacing_mm=12,pair_pitch_mm=40.64,
                local_origin_assembly_mm=list(b[:3]),mounting_face='Rear face; screws enter toward decreasing Y',
                hole_centres_local_mm=local,hole_centres_assembly_mm=points,
                installed_nut_thread_depth='Verify against the purchased nut; choose screws for printed thickness and washer stack.',
                custom_supports_included=False,
                service='Remove the crossbar before GPU extraction. Check custom supports against cables, lid, GPU vents and the crossbar removal path.')

"""Complete the single-row full-chassis carrier's side mounting joints."""
from mounting_hardware import cyl
from sheetmetal import bounds


def apply(parts):
    if not any(p['name'].startswith('Full_chassis_upper_intake_insert_') for p in parts):
        return None
    carrier=next(p for p in parts if p['name']=='Front_fan_carrier_with_side_returns')
    if carrier.get('side_mounting_joints'):
        return carrier['side_mounting_joints']
    from manufacturing_revision import add,clinch_shape
    records=[]
    for z in (22.,148.,205.,290.,381.45):
        carrier['shape']=carrier['shape'].cut(cyl(-1,12,z,2.11,442,(1,0,0))).clean()
        for side,x,axis in [('left',3.,(-1,0,0)),('right',437.,(1,0,0))]:
            name=f'Front_carrier_side_PEM_M3_{side}_{z:g}'
            add(parts,name,clinch_shape((x,12,z),axis,'M3'),'fasteners',catalog='95185A530',thread_host=carrier['name'])
            candidates=[]
            for p in parts:
                if '_panel_M3x8_' not in p['name']:
                    continue
                b=bounds(p['shape'])
                if abs((b[1]+b[4])/2-12)<.01 and abs((b[2]+b[5])/2-z)<.01 and ((b[0]<0) == (side=='left')):
                    candidates.append(p)
            assert len(candidates)==1,(side,z,[p['name'] for p in candidates])
            candidates[0]['thread_host']=name
            record=dict(centre=[x,12,z],diameter=4.22,thread='M3',axis=axis)
            carrier.setdefault('press_fit_holes',[]).append(record)
            records.append(dict(**record,nut=name,screw=candidates[0]['name'],catalog='95185A530'))
    carrier['side_mounting_joints']=records
    carrier['notes']=carrier.get('notes','')+' Ten side joints use M3 press nuts in diameter 4.22 seats; install before attaching the carrier to the body.'
    return records

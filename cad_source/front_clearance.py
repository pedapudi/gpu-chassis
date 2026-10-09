"""Front-cover spacing and removable crossbar placement in assembly coordinates."""
from mounting_hardware import cyl, screw
from sheetmetal import bounds

COVER_SPACER_MM = 3.0
COVER_SPACER_CATALOG = '92871A003'
COVER_SCREW_MM = 12
CROSSBAR_FRONT_Y_MM = 133.2


def apply(parts, report):
    """Set cover and crossbar datums for fresh builds and retained CAD assemblies."""
    mesh = next(p for p in parts if p['name']=='Stock_hex_perforated_mesh_cut_to_size')
    offset = -COVER_SPACER_MM-.8-bounds(mesh['shape'])[4]
    for p in parts:
        name = p['name']
        if name in ('Stock_hex_perforated_mesh_cut_to_size', 'Front_full_face_mesh_clamping_frame') or name.startswith('Front_cover_M3_large_washer_'):
            p['shape'] = p['shape'].translate((0,offset,0))
        elif name.startswith('Front_cover_metric_'):
            b = bounds(p['shape']); x,z=(b[0]+b[3])/2,(b[2]+b[5])/2
            p['shape'] = cyl(x,-COVER_SPACER_MM,z,3,COVER_SPACER_MM,(0,1,0)).cut(cyl(x,-COVER_SPACER_MM-1,z,1.6,COVER_SPACER_MM+2,(0,1,0)))
            p['name'] = f'Front_cover_metric_3mm_spacer_{x:g}_{z:g}'
            p['catalog'] = COVER_SPACER_CATALOG
            p['specification'] = '3 mm spacer, 6 OD, 3.2 bore'
        elif name.startswith('Front_frame_M3x'):
            b = bounds(p['shape']); x,z=(b[0]+b[3])/2,(b[2]+b[5])/2
            p['shape'] = screw((x,-6.2144,z),(0,1,0),'M3',COVER_SCREW_MM)
            p['name'] = f'Front_frame_M3x12_{x:g}_{z:g}'
    report['front'].update(spacer_length_mm=COVER_SPACER_MM,spacer_catalog=COVER_SPACER_CATALOG,
        cover_screw='M3 x 12',mesh_back_to_carrier_mm=3.8,front_projection_mm=6.2144)

    bar = next(p for p in parts if p['name']=='Removable_chassis_crossbar')
    delta = CROSSBAR_FRONT_Y_MM-bounds(bar['shape'])[1]
    wall = next(p for p in parts if p['name'].startswith(('U_shaped_body_', 'Upper_module_U_body_')))
    if abs(delta)>1e-6:
        for p in parts:
            if p['name'].startswith('Crossbar_wall_M4x8_'):
                b=bounds(p['shape']); y,z=(b[1]+b[4])/2,(b[2]+b[5])/2
                x=0 if b[0]<0 else 438.5
                # Restore the original side-wall hole before cutting its new location.
                wall['shape']=wall['shape'].fuse(cyl(x,y,z,2.25,1.5,(1,0,0))).clean()
                wall['shape']=wall['shape'].cut(cyl(x-.1,y+delta,z,2.25,1.7,(1,0,0))).clean()
            if p['group'] in ('crossbar','crossbar_mounts'):
                p['shape']=p['shape'].translate((0,delta,0))
        service=report['service_crossbar']
        for key in ('span_y_mm','fixed_bracket_y_mm'):
            service[key]=[v+delta for v in service[key]]
        for point in service['top_fixing_points']:point[1]+=delta
    service=report['service_crossbar']
    renamed={}
    for p in parts:
        if p['name'].startswith(('Crossbar_ledge_PEM_M4_','Crossbar_release_M4x8_')):
            old=p['name']; b=bounds(p['shape'])
            location='front' if (b[1]+b[4])/2<CROSSBAR_FRONT_Y_MM+15 else 'rear'
            p['name']=old.rsplit('_',1)[0]+'_'+location
            renamed[old]=p['name']
    for p in parts:
        if p.get('thread_host') in renamed:p['thread_host']=renamed[p['thread_host']]
    service['crossbar_to_GPU_nose_y_clearance_mm']=service['gpu_nose_y_mm']-bounds(bar['shape'])[4]
    assert abs(service['crossbar_to_GPU_nose_y_clearance_mm']-37.2)<1e-5
    assert wall['shape'].isValid()

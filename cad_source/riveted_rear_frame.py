"""Permanent rear-frame attachment to integral side-wall returns."""
from mounting_hardware import box, cyl, union
from manufacturing_revision import add
from sheetmetal import bounds, fold


def apply(parts, report):
    frame = next(p for p in parts if p['group'] == 'rear_vent')
    if frame.get('integral_rivet_mount'):
        return
    wall = next(p for p in parts if p['name'].startswith(('U_shaped_body_', 'Upper_module_U_body_')))
    b = bounds(frame['shape']); bottom, top = b[2], b[5]
    points = [(x,z) for x in (8.,432.) for z in (bottom+12,top-12)]
    # Restore the former wall screw holes and remove separate angle hardware.
    for x in (0.,438.5):
        for z in (bottom+12,top-12):
            wall['shape'] = wall['shape'].fuse(cyl(x,478.2,z,1.26,1.5,(1,0,0))).clean()
    parts[:] = [p for p in parts if not p['name'].startswith((
        'Rear_frame_external_', 'Rear_frame_flush_', 'Rear_angle_wall_'))]
    for x,z in points:
        frame['shape'] = frame['shape'].fuse(cyl(x,b[1],z,3.16,2,(0,1,0))).clean()
        frame['shape'] = frame['shape'].cut(cyl(x,b[1]-.1,z,1.7,2.2,(0,1,0)))
    # Side-wall extensions bend inward behind the cartridge's rear limit.
    bends = []
    for left in (True,False):
        tab = union([box(0,485,bottom,1.5,6.5,top-bottom),
                     box(0,490,bottom,15,1.5,top-bottom)])
        tab = fold(tab,bends,'z',(0,491.5),(1,-1),1.5)
        if not left:
            tab = tab.mirror('YZ',(220,0,0))
        x = 8 if left else 432
        for z in (bottom+12,top-12):
            tab = tab.cut(cyl(x,489.9,z,1.7,1.7,(0,1,0)))
        wall['shape'] = wall['shape'].fuse(tab).clean()
    wall['rear_return_points_xz'] = points
    wall['notes'] = ('1.5 mm steel U-shaped body. Integral upper rear returns: 15 mm inward, '
        'R1.5 inside bends; front tangent Y488.5, rear mating face Y491.5. '
        'Four diameter 3.4 rivet holes at X8 and X432, 12 mm from return ends. '
        'Keep returns behind the cartridge rear limit Y483. Deburr all free edges.')
    moving_groups = {'rear_vent','rear_mesh'}
    for p in parts:
        if p['group'] in moving_groups or p['name'].startswith(('Rear_mesh_', 'Lid_rear_retention_', 'Rear_MCIO_')):
            p['shape'] = p['shape'].translate((0,7,0))
    lid = next(p for p in parts if p['group'] == 'lid'); lb = bounds(lid['shape'])
    tool = box(-5,484.5,lb[2]-1,450,30,lb[5]-lb[2]+2)
    tail = lid['shape'].intersect(tool)
    lid['shape'] = lid['shape'].cut(tool).fuse(tail.translate((0,7,0)),
        box(0,484.5,lb[5]-1.5,440,7,1.5)).clean()
    lid['notes'] = ('Rear tab outer face Y495; rear guide slots end at Y455. '
        'Two M3 x 3 rear retention screws. Slide rearward 10 mm, then lift.')
    for i,(x,z) in enumerate(points,1):
        rivet = union([cyl(x,493.5,z,3.25,.8,(0,1,0)),
                       cyl(x,490,z,1.6,3.5,(0,1,0)),
                       cyl(x,485.5,z,3.25,4.5,(0,1,0))])
        add(parts,f'Rear_frame_rivet_{i}',rivet,'rear_frame_mounts',catalog='97525A218',
            specification='3.2 mm stainless blind rivet, 3-5 mm grip; install from outside',
            notes='Factory head outside; formed tail inside. Tail shown as a diameter 6.5 x 4.5 clearance envelope, bounded by the unformed 8 mm rivet length minus the 3.5 mm stack. Set before installing the cartridge; verify the actual tail.')
    frame['integral_rivet_mount'] = True
    frame['rivet_holes_xz'] = points
    frame['notes'] = ('Flat 2 mm steel frame, front face Y491.5. Four diameter 3.4 holes '
        'join the integral body returns with 3.2 mm blind rivets. Other diameter 2.5 holes '
        'tap M3 x 0.5 for mesh, lid retention and cable entry hardware. '
        'The frame stays installed during cartridge removal.')
    for p in parts:
        if p['name']=='Rear_MCIO_lower_U_frame_140x35_entry':
            p['notes']='140 x 35 clear entry with cap removed. Two lower M3 x 3 and two cap M3 x 5 screws into the tapped rear frame; no screw tips forward of Y491.5.'
    report['fixed_rear_closure'].update(rear_frame_inner_y_mm=491.5,wall_screw_length_mm=None,
        attachment='Four blind rivets into integral rear-facing body returns',rivet_catalog='97525A218',
        rivet_holes_xz_mm=points,hole_diameter_mm=3.4,grip_stack_mm=3.5,
        return_inside_radius_mm=1.5,return_width_mm=15,rear_return_tangent_y_mm=488.5,
        rivet_tail_front_y_mm=485.5,lid_rear_y_mm=495,
        installation='Rivet from outside before fitting the rear mesh or cable cap. Use a stainless-rivet-rated tool. Verify formed tails stay within the diameter 6.5 x 4.5 inside envelope before installing the cartridge.')
    assert wall['shape'].isValid() and lid['shape'].isValid() and frame['shape'].isValid()

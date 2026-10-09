"""Orient the full-chassis PSU intake inward without changing its occupancy."""
from mounting_hardware import box
from component_models import psu_vent
from sheetmetal import bounds


def apply(parts):
    body=next((p for p in parts if p['name'].startswith('U_shaped_body_')),None)
    if body is None:return None
    if body.get('inward_psu'):return body['inward_psu']
    # Assembly X348..434, Z10..160: a half-turn around the depth axis.
    def turn(s):return s.rotate((391,0,85),(391,1,85),180)
    for p in parts:
        if p['group']=='psu' or p['name'].startswith('ATX_6_32xquarter_inch_screw_'):
            p['shape']=turn(p['shape'])
    vent=psu_vent(415.8).mirror('YZ',(220,0,0)).translate((0,53.2,0))
    skin=box(438.5,2,1.5,1.5,483,396.25)
    body['shape']=body['shape'].fuse(vent.intersect(skin)).clean()
    rear=next(p for p in parts if p['name']=='Lower_rear_1p2mm_IO_eight_slots_exhaust_side_returns')
    # Rotate the complete aperture and its four mounting tabs as one region.
    region=box(347,467,9,88,5,152)
    patch=rear['shape'].intersect(region)
    rear['shape']=rear['shape'].cut(region).fuse(turn(patch)).clean()
    cradle=next(p for p in parts if p['name']=='ASUS_3000P_folded_175mm_cradle')
    # Retain a 6 mm inner return along the fan; full-height ends locate the PSU.
    cradle['shape']=cradle['shape'].cut(box(344,313,16,3,138,8)).clean()
    cradle['notes']='1.5 mm steel. Inner return top Z16 from Y313 to Y451 clears the inward intake; remaining end returns retain height Z22. Floor top Z10 locates the PSU.'
    rear['notes']='PSU fan faces the chassis centre. Four diameter 3.9 clearance holes at (X,Z): (354,154), (354,16), (428,40), (418,154). Use PSU-supplied #6-32 screws. Pattern and aperture rotate together about X391/Z85; this is not a mirror.'
    body['notes']=body.get('notes','')+' Solid PSU-side wall; PSU draws from inside the chassis.'
    report=dict(rotation_degrees=180,rotation_axis='Y through X391/Z85',
                envelope_mm=[175,150,86],assembly_envelope_mm=[348,294,10,434,469,160],
                rear_clearance_holes_xz_mm=[(354,154),(354,16),(428,40),(418,154)],
                rear_hole_diameter_mm=3.9,native_thread='#6-32 UNC-2B',
                fan_face_x_mm=348,fan_intake_direction='toward decreasing X, into the chassis',
                clear_intake_box_mm=[332,314,17,348,450,153],
                closest_rear_fan_frame_gap_mm=17,
                references=['https://www.asus.com/motherboards-components/power-supply-units/workstation/asus-pro-ws-3000p/techspec/',
                            'https://scidyne.com/ftp/ref_info/atx_201.pdf'],
                qualification='Standard ATX screw pattern checked against Figure 9. Supplier rear details and fan position remain photo-derived. Verify the physical PSU; 16 mm nominal unobstructed intake depth is not a thermal-performance qualification.')
    body['inward_psu']=report
    return report

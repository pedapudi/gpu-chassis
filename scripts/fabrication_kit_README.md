# Chassis fabrication kit

This kit contains the files a sheet-metal fabricator needs to quote and make the fabricated parts of the GPU chassis. It covers all six configurations: the 9U full chassis with three upper-intake options, and the 5U replacement-lid module with three intake options. The design is at engineering review; it is not released for fabrication. Build and check a prototype before ordering production quantities.

## Contents

- `parts_list.csv`: one row per distinct sheet blank (item `SM###`). Each row gives the source piece name, the assemblies that use it, material, thickness, nearest gauge, developed blank size, bend count, inside radius, K-factor, quantity for each configuration, tapping, joining, finish, fabrication holds and a SendCutSend review.
- `step/`: one formed 3D STEP model per item, moved to its own origin. Most fabricators develop the blank from this file with their own bend tooling.
- `flat/`: one developed flat-pattern DXF per item, in millimetres. Cut geometry is solid; bend centrelines are dashed lines on the same layer. The flat patterns use inside radius equal to thickness and K-factor 0.40. A fabricator with different tooling must re-develop the blanks from the STEP files.
- `hardware_list.csv`: purchased fasteners, nuts, washers and standoffs, with quantities per configuration.
- `captive_nut_schedule.csv`: every captive nut, the sheet part that holds it and its position, for the 9U and module base configurations.
- `drawings/`: the complete drawing set for each configuration, including a flat-pattern sheet for every piece.
- `kit_summary.json`: item counts and the SendCutSend review totals.

Coordinates in the drawings and schedules use the assembly datum: X = 0 at the body left seen from the front, Y = 0 at the front plane, Z = 0 at the underside.

## Material, bends and finish

All sheet parts are cold-rolled low-carbon steel (1008/1010). Modeled thicknesses are 1.0, 1.2, 1.5, 2.0 and 3.0 mm; `parts_list.csv` gives the nearest US gauge. Every bend is 90 degrees with inside radius equal to the thickness. Partial bends have relief slots one thickness wide.

Deburr all edges. Weld joined assemblies before finishing, then zinc plate or powder coat. Mask tapped threads and captive-nut threads during finishing.

## Joining and hardware

`parts_list.csv` names every weld: the joined assemblies (front carriers, lids, lower rear panel, module rear sill and lid adapter), the stitch-welded toe-locator combs, the bridges, the tray channels and handholds, and the bearing-angle spot welds.

Captive nuts are standard hex nuts held against their sheet part. Tack weld or bond each nut before its joint becomes inaccessible. Self-clinching (PEM-type) press-fit nuts can replace most of them. A replacement needs the mounting-hole size and edge distance of the chosen nut, so check each location in `captive_nut_schedule.csv` before substituting.

The GPU rear-panel shelf carries 21 #6-32 UNC-2B threads in extruded collars. Each collar edge lies 0.63 mm from the shelf bend, inside the press-brake die footprint. Form the shelf first, then extrude and tap the collars.

## Fabrication holds

These items need fabricator agreement before production; `parts_list.csv` marks each affected item:

- Flanges shorter than the usual press-brake minimum of four thicknesses: the 4.0 mm lower lips of both rear covers and the 4.5 mm legs of the backplane-rail and motherboard-tray bridges. The surrounding height stack fixes these sizes. Form them oversize and trim, use dedicated tooling, or substitute bought spacers.
- Holes closer than two thicknesses to a bend line. The EIA-310 rack holes sit 3.05 mm from the rack-ear bend because the rack standard fixes their positions. The bridge screw holes sit 1.3 to 2.75 mm from their bends. The outermost GPU aperture sits 0.95 mm from a side-return bend.
- Several small parts fall below common minimum part sizes: the toe-locator combs of the motherboard bank (4 mm wide), the rail nut guide strips (3.8 mm wide), the bridges and the module sill return strips. Laser-cut them from a larger tab and separate them, or source them as stamped or bought parts.

## SendCutSend review

The `sendcutsend` column classes each item as `suitable`, `suitable with notes` or `not suitable as drawn`, based on SendCutSend's published bending and part-size requirements. Their cold-rolled stock matches the 1.2, 1.5 and 3.0 mm parts (1.22, 1.50 and 3.02 mm). It has no 1.0 or 2.0 mm stock. SendCutSend bends with fixed radii and K-factors per thickness, so upload the STEP files or re-develop the DXFs with their specifications. The 9U body blank (1230 × 483 mm) exceeds their 30 × 44 in maximum. Welding availability and scope must be confirmed per material.

## Not included

Purchased components (GPUs, backplane, motherboard, PSU, fans, cooler) and cables are not fabricated parts. Their reference envelopes and the assembly order are in the main engineering package and its drawing set.

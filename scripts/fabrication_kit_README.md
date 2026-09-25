# Chassis fabrication kit

This kit contains the files a sheet-metal fabricator needs to quote and make the fabricated parts of the GPU chassis. It covers all six configurations: the 9U full chassis with three upper-intake options, and the 5U replacement-lid module with three intake options. The design is at engineering review; it is not released for fabrication. Build and check a prototype before ordering production quantities.

## Contents

- `parts_list.csv`: one row per distinct sheet blank (item `SM###`). Each row gives the source piece name, the assemblies that use it, material, thickness, nearest gauge, developed blank size, bend count, inside radius, K-factor, quantity for each configuration, tapping, joining, finish, fabrication holds and a SendCutSend review.
- `step/`: one formed 3D STEP model per item, moved to its own origin. Most fabricators develop the blank from this file with their own bend tooling.
- `flat/`: one developed flat-pattern DXF per item, in millimetres. Cut geometry is solid; bend centrelines are dashed lines on the same layer. The flat patterns use inside radius equal to thickness and K-factor 0.40. A fabricator with different tooling must re-develop the blanks from the STEP files.
- `hardware_list.csv`: purchased screws, captive thumbscrews, locating studs, square nuts, washers and standoffs, with quantities per configuration.
- `tapped_thread_schedule.csv`: every formed thread, its size, the sheet piece that carries it and its position, for the 9U and module base configurations.
- `drawings/`: the complete drawing set for each configuration, including a flat-pattern sheet for every piece.
- `kit_summary.json`: item counts and the SendCutSend review totals.

Coordinates in the drawings and schedules use the assembly datum: X = 0 at the body left seen from the front, Y = 0 at the front plane, Z = 0 at the underside.

## Material, bends and finish

All sheet parts are cold-rolled low-carbon steel (1008/1010). Modeled thicknesses are 1.0, 1.2, 1.5, 2.0 and 3.0 mm; `parts_list.csv` gives the nearest US gauge. Every bend is 90 degrees with inside radius equal to the thickness. Partial bends have relief slots one thickness wide.

Deburr all edges. Weld joined assemblies before finishing, then zinc plate or powder coat. Mask the tapped threads during finishing. Press in the captive thumbscrews and locating studs afterward.

## Joining and hardware

`parts_list.csv` names every weld: the joined assemblies (front carriers, lids, lower rear panel, module rear sill and lid adapter), the stitch-welded toe-locator combs, the tray channels and handholds, and the bearing-angle spot welds.

Screws fasten into threads formed in the sheet; the chassis has no captive hex nuts. Each thread is an extruded collar, one sheet thickness tall up to 1.5 mm, on the side away from the screw head, tapped M3 (2.5 mm drill), M4 (3.3 mm drill) or #6-32 UNC-2B (2.705 mm drill). The flat DXFs show each thread at its tap-drill diameter; size the extrusion pierce for your tooling. The `tapping` column of `parts_list.csv` gives the count per item. Extrude and tap after forming the adjacent bends: the GPU rear-panel shelf collars, for example, lie 0.63 mm from the shelf bend, inside the press-brake die footprint. A supplier that cannot extrude can fit self-clinching (PEM-type) nuts instead; check the mounting-hole size and edge distance of the chosen nut at each location in `tapped_thread_schedule.csv`.

The body floor and GPU tray carry eight conical bosses, 20 mm at the base, 10 mm at the top and 4.5 mm high, each with a formed thread in its top. They need an embossing die; M3 and M4 press-in standoffs of the same height are a substitute.

The lid and rear cover are held by rear-facing M3 captive panel screws. Their ferrules press into 6.4 mm holes in the 1.5 mm lid tabs and cover web; they thread into the rear flanges folded inward from the body side walls. The lid front locates on four flush-head press-in studs, 4 mm diameter, in the body walls.

## Fabrication holds

These items need fabricator agreement before production; `parts_list.csv` marks each affected item:

- Flanges shorter than the usual press-brake minimum of four thicknesses: the 4.0 mm lower lips of both rear covers. The surrounding height stack fixes this size. Form them oversize and trim, or use dedicated tooling.
- Holes closer than two thicknesses to a bend line. The EIA-310 rack holes sit 3.05 mm from the rack-ear bend because the rack standard fixes their positions, and the rack-ear side-screw holes sit 5.7 mm from it. The outermost GPU aperture sits 0.95 mm from a side-return bend, and the GPU shelf tap-drill holes sit 1.33 mm from the shelf bend.
- Several small parts fall below common minimum part sizes: the toe-locator combs of the motherboard bank (4 mm wide), the rail nut guide strips (3.8 mm wide) and the module sill return strips. Laser-cut them from a larger tab and separate them, or source them as stamped or bought parts.

## SendCutSend review

The `sendcutsend` column classes each item as `suitable`, `suitable with notes` or `not suitable as drawn`, based on SendCutSend's published bending and part-size requirements. Their cold-rolled stock matches the 1.2, 1.5 and 3.0 mm parts (1.22, 1.50 and 3.02 mm). It has no 1.0 or 2.0 mm stock. SendCutSend bends with fixed radii and K-factors per thickness, so upload the STEP files or re-develop the DXFs with their specifications. The 9U body blank (1230 × 483 mm) exceeds their 30 × 44 in maximum. Welding availability and scope must be confirmed per material.

## Not included

Purchased components (GPUs, backplane, motherboard, PSU, fans, cooler) and cables are not fabricated parts. Their reference envelopes and the assembly order are in the main engineering package and its drawing set.

# Chassis construction and service

The manufacturing package contains a 9U full chassis and a 5U GPU module for the SilverStone RM53-502. The full chassis body measures 440 x 485 x 399.25 mm. The upper module measures 440 x 485 x 221.75 mm and starts at Z222.25 in the combined assembly. The GPU carrier retains twenty-one rear bracket positions, including ten dual-slot card positions and one single-width position.

Each chassis has one drawing book covering its fan variants. Drawings show complete part outlines, critical interface dimensions and hole-family callouts. The feature-centres CSV supplies exact circular-feature coordinates without hundreds of schedule pages. Nominal formed STEP geometry controls the remaining cut paths. Production tolerances, bend tooling and supplier interfaces require approval before cutting metal.

## Printed adapters replace the sliding backplane supports

Two **8.5 mm thick** printed adapters sit directly on the steel GPU tray. Each print measures **209.5 x 240 mm**, fitting a 256 x 256 mm bed. A 5 mm brim gives a 219.5 x 250 mm print footprint. A 1 mm gap separates the independently fastened halves; no printed joining feature carries the GPU load. Windows reduce material consumption while leaving broad webs beneath the six reference mounting points. The steel tray remains the structural support.

Standard **8 mm long metric spacers** stand between the print and the PCB. Each spacer has a 6 mm outside diameter and a 3.2 mm clearance bore. An M3 x 16 screw passes through a 0.5 mm washer, the 2.5 mm PCB and the spacer into an M3 brass heat-set insert. Nominal insert engagement is 5 mm. The 5.7 mm insert sits in a 6.7 mm deep blind pilot, leaving 1 mm below the insert.

The height stack is 8.5 + 8 = 16.5 mm above the tray. It preserves the PCB underside and socket seating datums. A different backplane requires a different printed hole pattern, with the same height stack. The illustrated board mounting holes remain photo-derived estimates; measure the actual board before printing.

Print flat using unfilled flame-retardant polycarbonate with documented temperature properties. Start with six perimeter walls and solid material around insert locations. The 4.0 mm pilot diameter is a catalog starting dimension; verify insert fit on a coupon made with the chosen printer and material. Carbon-filled filament can be electrically conductive and is unsuitable beneath exposed PCB circuitry. CAD does not establish printed-part fire performance, insertion strength or long-term creep under GPU heat.

Eight M3 x 12 screws attach the two adapters to press nuts installed in the steel tray. Install these screws before fitting the PCB. All screws are accessible from above after the PCB is removed. There are no sliding square nuts or underside standoff screws.

The motherboard uses standard 6 mm metric spacers over 0.5 mm M3 washers, giving the existing 6.5 mm seating height. M3 x 12 screws pass through upper washers and the board into the tray's formed threads. This stack uses catalog parts and preserves the motherboard-to-rear-panel alignment.

## A stock mesh cover protects the fan plate

The front consists of a steel fan carrier, separate screw-mounted rack ears, and a removable mesh cover. The fan carrier takes the fan loads. The mesh is cut from pre-perforated steel stock; its thousands of openings are not custom laser cuts.

A 1.5 mm perimeter frame overlaps all mesh edges by 16 mm. Standard 5 mm spacers and 0.8 mm large M3 washers hold the mesh behind the frame and clear the fan screw heads. M3 x 16 screws retain the cover. The frame projects 8.2144 mm forward of the carrier, excluding its screw heads. Remove the frame and mesh to reach the fan screws.

The stock specification is 0.9144 mm steel, 6.35 mm hexagonal openings and 79% nominal open area. This is purchased 20-gauge stock expressed in metric dimensions. Pattern phase at cut edges is illustrative in the viewer. Its STEP file defines the cut blank and assembly holes; the supplier's repeated perforations are specified by the stock number and drawing. Use the frame as an assembly-hole template; deburr the cut edges. Mask coating at the intended electrical bonding contacts.

The fan variants retain their existing mounting patterns: 120 mm fans use 105 mm square axes; 140 mm fans use 124.5 mm; 180 mm fans use 165 mm; 80 mm fans use 71.5 mm. Direct case fans use short manufacturer-compatible screws into the plastic frame. Radiator screws require the cooler's specified thread and penetration limit.

The frame fixes the screw positions. Stock perforations may already provide clearance at those positions; enlarge a web only where needed for a 3.4 mm minimum passage. Large washers bridge the perforations. Mesh holes are not precision locating features.

## Self-clinching nuts suit low-volume sheet fabrication

Self-clinching nuts create permanent threads with standard purchased hardware and a press operation. Extruded-and-tapped collars require forming tooling and tapping. For the service panels, press nuts are the preferred process where a complete seating land and installation-tool access exist.

The model converts supported panel collars to M3 or M4 self-clinching nuts. Interrupted seating lands and existing special interface threads remain explicit exceptions in `manufacturing-changes.json`; they must not be silently substituted on the shop floor. The GPU retention shelf and motherboard seating datums remain fixed. Press nuts must be installed before the assembly obstructs their reverse face.

M3 press-nut installation holes are 4.22 mm; M4 holes are 5.41 mm. Specify +0.08/-0.00 mm unless the purchased fastener drawing requires otherwise. The selected zinc-plated steel nuts require compatible sheet hardness. Confirm hole-to-edge distance, bend distance and press tooling with the fabricator. Hole preparation must follow the nut manufacturer's instructions; a clearance hole and a press-nut installation hole are different features.

All custom chassis joints use metric threads, principally M3 x 0.5 and M4 x 0.7. Existing PSU and radiator threads are supplier-controlled: retain their specified factory screws. An M3 screw must not be forced into a PSU's #6-32 hole. Fan thread-forming screws likewise follow the selected plastic frame.

## Catalog purchase specifications

| Function | McMaster-Carr item or selection | Quantity basis |
|---|---|---|
| PCB heat-set insert | [94459A140](https://www.mcmaster.com/94459A140/), M3 x 0.5, brass, 5.7 mm installed length | Six per carrier |
| PCB metric spacer | [92871A011](https://www.mcmaster.com/92871A011/), 8 mm long, 6 mm OD, 3.2 mm bore | Six per carrier |
| Motherboard metric spacer | [92871A009](https://www.mcmaster.com/92871A009/), 6 mm long, 6 mm OD, 3.2 mm bore; 0.5 mm M3 washer beneath | Ten per full chassis |
| M3 self-clinching nut | [95185A530](https://www.mcmaster.com/95185A530/), S-M3-1ZI | Counted in the assembly inventory |
| M4 self-clinching nut | [95185A590](https://www.mcmaster.com/95185A590/), S-M4-1ZI | Counted in the assembly inventory |
| Pre-perforated sheet | [92725T3](https://www.mcmaster.com/92725T3/), 0.9144 mm steel, 79% open hexagonal pattern | Cut to the drawing size |
| Front-cover metric spacer | [92871A007](https://www.mcmaster.com/92871A007/), 5 mm long, 6 mm OD, 3.2 mm bore | One per cover fixing |
| Machine screws and washers | [Metric machine screws](https://www.mcmaster.com/products/machine-screws/system-of-measurement~metric/) and [metric washers](https://www.mcmaster.com/products/washers/system-of-measurement~metric/); specified size, length and head in assembly inventory | Per configuration |

Catalog dimensions were checked on 2026-10-08. Stock availability changes. The M3 and M4 press nuts are described in the [manufacturer's self-clinching nut catalog](https://products.pemnet.com/sku/wp-content/uploads/sites/9/2023/11/cldata-5.pdf). The [perforated sheet catalog](https://www.mcmaster.com/products/perforated-steel/) and [metric spacer catalog](https://www.mcmaster.com/products/90138A216/) provide the selected stock dimensions. The specific spacer item numbers in the table identify the 6 mm OD series.

## Installation and inspection

1. Verify the purchased backplane mounting coordinates and the OEM lid interface. Fixture the rear slot bank to the PCB socket datums before fastening the adapter.
2. Cut and bend the panels. Install press nuts while both sheet faces are accessible. Assemble the body, side bearings and rack ears.
3. Fit the lower motherboard tray, board, PSU, cooler and retimers. Install the lower rear fans after the tray screws are tightened.
4. Prepare the GPU cartridge on a bench. Install the two printed adapters, inserts and six spacers, then the backplane. Fit the GPUs and rear bracket screws.
5. Seat the cartridge, secure it and connect the power and MCIO harnesses. Keep connectors and bend allowances clear of the cartridge lifting path.
6. Install the rear cover and lid, followed by the front mesh cover. Provide separately rated rack rails or a shelf. OEM lid screws locate the upper module; they do not establish its load capacity.

The STEP assemblies contain chassis structure and assembly hardware. Individual part files contain the manufactured chassis components and printed adapters. GPUs, motherboards, cables, hoses, fans and the OEM chassis are viewer-only fit references and have no individual STEP files in this package.

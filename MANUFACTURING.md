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

The 3 mm rack ears have R5 exposed front corners and R3 corners at the rear ends of their side flanges. Rack-hole centres and mounting flanges retain their specified positions. Deburr both sheet faces and break every exposed edge by 0.3-0.5 mm; corner radii alone do not remove sharp cut edges.

A 1.5 mm perimeter frame overlaps all mesh edges by 16 mm. Standard 5 mm spacers and 0.8 mm large M3 washers hold the mesh behind the frame and clear the fan screw heads. M3 x 16 screws retain the cover. The frame projects 8.2144 mm forward of the carrier, excluding its screw heads. Remove the frame and mesh to reach the fan screws.

The cover has R12 outside corners and an R8 opening. The stock mesh has R8 outside corners, maintaining a concealed cut edge behind the frame. These radii apply to the cut outline, not a rolled sheet edge. Deburr the mesh before clamping it.

The stock specification is 0.9144 mm steel, 6.35 mm hexagonal openings and 79% nominal open area. This is purchased 20-gauge stock expressed in metric dimensions. Pattern phase at cut edges is illustrative in the viewer. Its STEP file defines the cut blank and assembly holes; the supplier's repeated perforations are specified by the stock number and drawing. Use the frame as an assembly-hole template; deburr the cut edges. Mask coating at the intended electrical bonding contacts.

The fan variants retain their existing mounting patterns: 120 mm fans use 105 mm square axes; 140 mm fans use 124.5 mm; 180 mm fans use 165 mm; 80 mm fans use 71.5 mm. Direct case fans use short manufacturer-compatible screws into the plastic frame. Radiator screws require the cooler's specified thread and penetration limit.

The frame fixes the screw positions. Stock perforations may already provide clearance at those positions; enlarge a web only where needed for a 3.4 mm minimum passage. Large washers bridge the perforations. Mesh holes are not precision locating features.

## Self-clinching nuts suit low-volume sheet fabrication

Self-clinching nuts create permanent threads with standard purchased hardware and a press operation. Extruded-and-tapped collars require forming tooling and tapping. For the service panels, press nuts are the preferred process where a complete seating land and installation-tool access exist.

The model converts supported panel collars to M3 or M4 self-clinching nuts. Interrupted seating lands and existing special interface threads remain explicit exceptions in `manufacturing-changes.json`; they must not be silently substituted on the shop floor. The GPU retention shelf and motherboard seating datums remain fixed. Press nuts must be installed before the assembly obstructs their reverse face.

M3 press-nut installation holes are 4.22 mm; M4 holes are 5.41 mm. Specify +0.08/-0.00 mm unless the purchased fastener drawing requires otherwise. The selected zinc-plated steel nuts require compatible sheet hardness. Confirm hole-to-edge distance, bend distance and press tooling with the fabricator. Hole preparation must follow the nut manufacturer's instructions; a clearance hole and a press-nut installation hole are different features.

All custom chassis joints use metric threads, principally M3 x 0.5 and M4 x 0.7. Existing PSU and radiator threads are supplier-controlled: retain their specified factory screws. An M3 screw must not be forced into a PSU's #6-32 hole. Fan thread-forming screws likewise follow the selected plastic frame.

## The removable crossbar ties the side walls together

A 431 x 30 x 20 mm inverted channel spans the chassis at Y165 to Y195. It uses 1.5 mm steel and two bends with R1.5 inside radii. Two folded side ledges attach through the walls with M4 screws into self-clinching nuts. Install those ledges before placing the chassis in the rack. Four top-access M4 x 8 screws secure the crossbar to the ledges; routine crossbar removal needs no access outside or beneath the chassis.

The ledges end at Y191.5, ahead of the reference GPU noses at Y200.4. They remain outside the cards' vertical extraction path. Remove the lid, undo the four top screws and lift the crossbar with any fitted fingers. With the bar raised 40 mm, move it forward and lift clear. Disconnect signal and power cables and release card or cartridge screws before lifting. The fixed rear frame, stock mesh and entry hardware remain installed.

The crossbar ties the walls together but has no established lifting or transport load rating. Do not lift a populated chassis by this bar. Structural qualification requires a loaded prototype.

## The rear uses stock mesh on a fixed frame

A 2 mm steel perimeter frame carries the rear closure loads. Cut the rear screens from the same 0.9144 mm, 79% open-area stock as the front cover. The mesh itself has no structural duty. Two external folded angles fasten the frame to the walls; four M3 x 6 countersunk screws enter outward-facing press nuts. Flush inside heads preserve the cartridge lift path. The external angles place the frame 1.5 mm behind the carrier rear. Their bend radii clear the body rear edges.

M3 x 3 screws and 9 mm washers clamp the mesh into tapped frame holes. Mesh upper-corner notches clear the lid tabs. The module has two screen blanks separated by a 140 x 35 mm cable entry. Its folded removable cap restores a connection across the opening. Geometry alone does not establish torsional stiffness; qualify the frame and threaded joints with a loaded prototype.

The module has 61.14 mm from the GPU envelope top to the lid underside, so an 80 mm fan cannot fit above the cards. The full chassis has 88.64 mm. Five nominal 80 x 80 x 25 mm rear fan envelopes fit across the full chassis clear of the modeled component and cable references at Z310.5. Dedicated fan mounts and a suitable open frame would be required; rear GPU exhaust fans are not included in this package. Fixed internal fan bodies would also obstruct lifting the cartridge and would have to be removed for service. An external fan bracket could preserve the lift path but would add at least the fan depth behind the chassis; this option is not modeled.

The two tray handholds bolt to captive M3 tray nuts with four top-access M3 x 6 screws. Their grip openings are 18 x 18 mm with R3 corners; deburr all grip edges. They sit 6.2 mm ahead of the reference GPU noses and stay with the cartridge. Diameter 8 holes in the front bearing clear the captive nuts and screw tips. These handholds have no established lifting load rating.

## Optional padded fingers stabilize the GPU noses

Ten identical folded steel fingers attach to the crossbar's rear face. Each uses two M3 x 6 screws and captive M3 nuts. Parallel 3.4 x 11.4 mm slots permit 8 mm total vertical adjustment while preventing rotation about one screw. The fingers and their hardware are optional; the drawing parts list marks their quantities with an asterisk.

Each finger carries a 20 x 12 x 1.5875 mm adhesive-backed silicone foam pad cut from [McMaster 86235K311](https://www.mcmaster.com/86235K311/). The catalog identifies the foam as flame-retardant; that rating does not include its adhesive. The [catalog specification](https://www.mcmaster.com/products/flame-retardant-silicone-foam/) controls the purchased sheet.

The pads meet the nominal GPU envelope at zero compression. On the actual cards, identify a rigid shroud land clear of vents, fan blades, circuitry and connectors before using the kit. Adjust to light contact without bending a card or forcing its socket. The fingers limit upward movement at the nose; they do not replace rear bracket screws or provide a qualified shipping restraint. Omit the kit if the actual shroud has no suitable contact land.

The viewer has a GPU-stabilizer option. Its assembly download switches between the chassis with a bare crossbar and the chassis with the finger kit. The OpenSCAD `gpu_stabilizers` parameter controls the same option. Individual part files retain all optional fingers; one shared drawing describes their identical geometry.

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
| M3 x 3 pan-head Phillips screw | [92005A111](https://www.mcmaster.com/92005A111/) | Lid guides, rear retention and mesh clamps |
| M3 x 6 flat-head Phillips screw, 90 degrees | [92010A116](https://www.mcmaster.com/92010A116/) | Four rear-frame fixings |
| M3 x 5 pan-head Phillips screw | [92005A114](https://www.mcmaster.com/92005A114/) | Per configuration |
| M3 x 6 pan-head Phillips screw | [92005A116](https://www.mcmaster.com/92005A116/) | Per configuration; add 20 for stabilizers |
| M3 x 8 pan-head Phillips screw | [92005A118](https://www.mcmaster.com/92005A118/) | Per configuration |
| M3 x 12 pan-head Phillips screw | [92005A122](https://www.mcmaster.com/92005A122/) | Per configuration |
| M3 x 16 pan-head Phillips screw | [92005A126](https://www.mcmaster.com/92005A126/) | Per configuration |
| M4 x 8 pan-head Phillips screw | [92005A218](https://www.mcmaster.com/92005A218/) | Per configuration |
| M4 x 10 pan-head Phillips screw | [92005A220](https://www.mcmaster.com/92005A220/) | Per configuration |
| M3 washer, 3.2 ID x 7 OD | [90965A130](https://www.mcmaster.com/90965A130/), 316 stainless, 0.4-0.6 mm thick | Modeled at 0.5 mm nominal |
| M3 large washer, 3.2 ID x 9 OD | [91116A120](https://www.mcmaster.com/91116A120/), 18-8 stainless, 0.7-0.9 mm thick | Modeled at 0.8 mm nominal |
| Optional stabilizer foam | [86235K311](https://www.mcmaster.com/86235K311/), adhesive silicone foam, 1.5875 mm thick | Ten cut pads per kit |

The parts list on sheet 2 of each drawing book has a linked McMaster-Carr column. The companion CSVs include the same item numbers and supplier URLs. Quantities count installed pieces, not sales packs; round purchases to the catalog pack sizes. Custom sheet-metal and printed components are marked “Custom part.” PSU and plastic fan screws are marked “Supplier screw” because their threads and permitted penetration depend on the purchased equipment.

The selected zinc-plated Phillips screws use M3 x 0.5 and M4 x 0.7 threads. M3 head envelopes are 6 mm diameter x 2.4 mm high; M4 heads are 8 mm diameter x 3.1 mm high. Pan-head screw length is measured below the head. The four M3 x 6 flat-head rear-frame screws include the head in their 6 mm length. Their heads are 5.6 mm diameter x 1.65 mm high. Measure the motherboard height washers and select or shim them to the 6.5 mm seating datum; the catalog thickness tolerance is not an exact 0.5 mm height guarantee.

Catalog dimensions were checked on 2026-10-08. Stock availability changes. The M3 and M4 press nuts are described in the [manufacturer's self-clinching nut catalog](https://products.pemnet.com/sku/wp-content/uploads/sites/9/2023/11/cldata-5.pdf). The [perforated sheet catalog](https://www.mcmaster.com/products/perforated-steel/) and [metric spacer catalog](https://www.mcmaster.com/products/90138A216/) provide the selected stock dimensions. The specific spacer item numbers in the table identify the 6 mm OD series.

## Installation and inspection

1. Verify the purchased backplane mounting coordinates and the OEM lid interface. Fixture the rear slot bank to the PCB socket datums before fastening the adapter.
2. Cut and bend the panels. Install press nuts while both sheet faces are accessible. Assemble the body, fixed rear frame, stock rear mesh and rack ears. For the upper module, fasten the lid adapter to the empty body before fitting the bearing angles that cover four adapter screws.
3. In the full chassis, install the PSU before its adjacent bearing angle. Fit the motherboard tray, board, cooler and retimers. Install the lower rear fans after tightening the tray screws. Complete the GPU tray supports before inserting the cartridge.
4. Prepare the GPU cartridge on a bench. Install the two printed adapters, inserts and six spacers, then the backplane. Fit the GPUs and rear bracket screws.
5. Seat the cartridge, secure it and connect the power and MCIO harnesses. Keep connectors and bend allowances clear of the cartridge lifting path.
6. Install the crossbar after fitting cards and routing cables. If using the finger kit, adjust its pads on verified shroud lands before tightening the clamp screws. Fit the lid and front mesh cover; the fixed rear closure is already installed. Provide separately rated rack rails or a shelf. OEM lid screws locate the upper module; they do not establish its load capacity.

The STEP assemblies contain chassis structure and assembly hardware. Individual part files contain the manufactured chassis components and printed adapters. GPUs, motherboards, cables, hoses, fans and the OEM chassis are viewer-only fit references and have no individual STEP files in this package.

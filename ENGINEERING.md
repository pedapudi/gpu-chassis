# Chassis interfaces and qualification

The full chassis body is 440 x 485 x 399.25 mm. The RM53-502 upper module is 440 x 485 x 221.75 mm; its base starts at Z222.25 and its top is at Z444 in the combined assembly. The full chassis includes the ASUS WRX90E-SAGE SE motherboard, XE360-TR5 radiator and ASUS Pro WS 3000P fit references. Construction and purchased hardware are specified in [MANUFACTURING.md](MANUFACTURING.md).

## Coordinate system and handedness

Exported X0 is the body left in the front view. Y0 is the fan-carrier plane and Z0 is the full-chassis underside. The front view looks toward positive Y. The exterior rear view looks toward negative Y, so X decreases to the viewer's right. In that rear view the PSU is on the left, I/O and exhaust are central, and motherboard PCIe positions are on the right. Inside-face coordinate views use positive X to the right and are labeled accordingly.

The rack ears extend beyond the 440 mm body to a 482.6 mm rack face. The removable mesh cover projects 8.2144 mm forward of Y0, excluding screw heads. Rack rails or a rated shelf must support the populated chassis; the ears and OEM lid screws are not a qualified support by themselves.

## GPU interfaces

The reference Miwin MG-SW510B PCB measures 429 x 225 x 2.5 mm. Its twelve sockets span 406.4 mm: ten double-width positions on 40.64 mm pitch and one single-width socket 20.32 mm beyond each end. The carrier has twenty-one rear bracket positions on 20.32 mm pitch. Ten dual-slot GPUs occupy twenty positions; the leading single-width socket uses the remaining position. The trailing socket shares a rear position with the last GPU cooler and is usable only when that GPU is absent.

Each upper rear aperture is 15.000 x 100.500 mm, leaving a 5.320 mm web. These are chassis aperture dimensions, distinct from the 18.420 mm bracket width. The M3 retention axes are at Y474.080, each 9.210 mm in positive X from its bracket centre. Four side-return holes are diameter 3.400. The integral shelf uses 1.2 mm sheet with an R1.2 inside bend and R2.4 outside bend.

The shelf retains its formed M3 threads where standard press-nut edge distances cannot be met without changing the bracket interface. The nominal collar is 3.7 mm OD and extends 1.3 mm below the shelf. Its 2.5 mm tap-drill bore gives 2.5 mm total threaded length with the sheet. GPU bracket screws are M3 x 5. Qualify tightening torque and repeated service before release.

The separate 1.5 mm toe comb is 12 mm deep. Its notches measure 10.790 x 1.300 mm on 20.320 mm pitch. Against a 10.190 x 0.860 mm bracket toe this gives 0.600 mm total lateral and 0.440 mm fore-aft clearance. Fixture the comb to the bracket-bearing surface and stitch weld it before installing the rear assembly. Nominal welds are 6 mm long with 1 mm legs between the notches; distortion and strength require qualification.

The full-chassis GPU PCB underside remains at Z188. The tray top is Z171.5, followed by an 8.5 mm printed adapter and 8 mm metric spacer. The module raises these datums by 72.25 mm. Change the printed mounting pattern to match the purchased PCB without altering this height stack or the socket-to-bracket relationship.

Standard socket pitch is an explicit design assumption. PCB holes, component locations, connector keepouts, socket seating depth and latch-release access remain supplier-verification items. Miwin's electrical slot assignments must also be confirmed; a physical socket count does not establish which sockets accept GPUs.

## GPU stabilization and service

The removable crossbar sits ahead of the GPU noses. Its fixed ledges end at Y191.5; reference cards start at Y200.4. Remove the crossbar and optional padded fingers before vertical card or cartridge extraction. Four top-access M4 screws release the bar. Crossbar stiffness and permissible pad force require physical qualification. The optional fingers must contact verified shroud lands; the card envelopes do not define a qualified contact surface.

## Lower motherboard, PSU and cooling

The lower rear has eight case apertures on 20.32 mm pitch. Its I/O shield opening is 158.75 x 44.45 mm. The ten motherboard mounting positions follow the SSI EEB layout and the selected holes in the ASUS manual. Confirm them against the physical motherboard, including its integrated I/O shield.

The motherboard underside is Z16.00, above a tray top at Z9.50. Standard 6 mm metric spacers and 0.5 mm M3 washers provide the 6.5 mm seating height. PCB thickness is 1.57 mm. M3 x 12 screws pass through upper washers, the board and spacers into the existing formed threads in the tray. The motherboard tray sits on four embossed floor bosses. The GPU tray has no embossed rail bosses or sliding nut tracks.

The PSU envelope is 175 x 150 x 86 mm, oriented with its fan facing the side intake. Its native rear pattern and supplied #6-32 screws remain supplier-controlled exceptions to the metric chassis joints. Install the PSU before the adjacent bearing angle; remove that angle for PSU replacement.

The AIO reserves a 394 x 120 x 28 mm radiator and 38 mm fan depth. Verify radiator thread, screw length, penetration and hose routing against the actual cooler. The selected PSU has four native GPU 16-pin cables and four 8-pin GPU cables; the ten modeled GPU power routes are service envelopes, not a qualified power-distribution plan.

## Cable routing and removal

Internal MCIO cables run from lower PCIe retimers through the two 195 x 65 mm forward deck openings to the backplane's long-edge connector bank. Power harnesses use the same service region with side restraints. No cable-support shelf crosses the GPU extraction path. Disconnect and park cables before lifting the cartridge.

The full chassis retains its lower external MCIO entry. The module has a 140 x 35 mm top-open rear notch from Z407.50 to Z442.50. Remove two M3 x 5 screws and the brush cap to pass connectors. The folded cap bridges the opening after installation. Verify actual plugs, cable bend radii and brush selection. The cap extends 10.5 mm behind the body.

The rear cover stays installed during cartridge extraction. Remove the lid, crossbar, four front M4 cartridge screws and four rear-side M3 cartridge screws; disconnect and park every connected cable. The carrier rear ends at Y483.00 and the fixed rear frame starts at Y484.50, giving 1.50 mm nominal separation throughout a vertical lift. Four flush flat-head screws fasten the frame to external angles; their nuts lie outside the lift path. Manufacturing tolerances must preserve positive clearance.

The lid has four M3 x 3 wall guide screws and two M3 x 3 rear retention screws. The rear guide pair and matching lid slots sit at Y455, behind the PCB edge at Y443.7. Remove the rear screws, slide the lid 10 mm rearward and lift. Its rear tab outer face is Y488, 3 mm aft of the body rear, clearing the 2 mm frame. Short screw lengths control inward projection; do not substitute longer screws. Guide threads remain tapped in 1.5 mm sheet. Lower retimer screw access still requires removal of the lower external MCIO frame and brushes.

Two screw-mounted handholds have 18 x 18 mm openings with R3 corners. Four top-access M3 x 6 screws enter tray press nuts. Diameter 8 bearing relief holes clear these nuts during cartridge removal. The handholds end 6.2 mm ahead of the GPU noses. They remain attached during service, but their load capacity is unqualified.

Install the module adapter and empty upper body before the side bearings, which cover four module-to-adapter screws. The OEM return profiles and screw positions are transfer-drill templates; measure the actual RM53-502 lid and check OEM internal interference before making them.

## Manufacturing and validation limits

The formed steel models use inside bend radius equal to sheet thickness. Existing developed geometry assumes K-factor 0.40; regenerate production blanks for the chosen stock and tooling. Some rear lips require special tooling or forming oversize and trimming. PCIe apertures near side bends, welded toe combs and the motherboard floor bosses require fabricator review.

The manufacturing pass converts service-panel threads to self-clinching nuts only where the seating annulus and edge allowance fit. Remaining formed threads are listed in the package report or described above. Installation pressure, sheet hardness, coating, grounding and hardware torque require process qualification.

CAD checks cover nominal solid validity, changed-part intersections, preserved interface locations, individual and assembly STEP round trips, screw access and sampled service motions. Conservative swept prisms check the complete 300 mm vertical cartridge path against the retained rear closure, lid guides and their fasteners. Sampled checks include the remaining fixed parts. They do not establish load capacity, acceptable printed-part creep, thermal performance, cable bend radius, electrical safety or a flawless physical installation. Use an unpowered fit prototype before powered qualification.

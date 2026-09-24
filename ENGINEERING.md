# Motherboard and GPU chassis engineering package

This package contains a 9U full enclosure and an upper GPU module proposed as a replacement lid for the SilverStone RM53-502. Both use a 440 × 485 mm body footprint and a removable GPU cartridge with twenty-one rear bracket positions. The full enclosure reserves a lower layer for the ASUS WRX90E-SAGE SE motherboard, XE360-TR5 AIO and ASUS Pro WS 3000P power supply.

**Status: engineering review, not released for fabrication.** The nominal assemblies can be inspected and their modeled geometry checked. The OEM lid interface, supplier backplane details, latch access and production sheet-metal forming remain unresolved. A flawless physical installation cannot be established from photographs and nominal envelopes.

## Files

Each design folder contains an assembly STEP, individual formed-part STEP files, OpenSCAD sources, a drawing PDF, coordinate schedules, a bill of materials, developed flat-pattern DXFs with bend tables, and validation reports. `interactive_model.html` displays meshes compiled from the individual OpenSCAD sources. It runs locally without network dependencies. A vector engineering-drawing pane sits beside the 3D model. Select a sheet, zoom, or select a fabricated component to open its matching drawing; Open PDF accesses the complete drawing set.

The STEP files preserve analytic surfaces. The OpenSCAD files describe faceted part solids with editable visibility, placement and cartridge-lift controls. They are not fully dimension-parametric recreations of every manufactured part. Rebuild dimension changes with the supplied Python CAD sources. The modular folder also includes a native constructive-solid-geometry adapter template with parameters for measured OEM hole coordinates and return profiles.

The drawing PDFs include formed-part views, cross-sections, dimensioned sheet-face views, sheet thicknesses, hole and cutout schedules, location diagrams and row-by-row coordinates. Dedicated interface sheets dimension open-edge notches, the stepped PSU opening, lid returns, adapter seating and the installed rail-height stack. Round holes show diameter and radius. Obround slots show overall length, width, end radius and length axis. Hole counts distinguish separate flanges along the normal axis. Feature JSON schedules accompany the analytic edge CSVs. An edge CSV is a geometry record, not a hole list. Face-profile DXFs record formed faces. Developed blanks are the separate flat-pattern DXFs described under drawing interpretation and manufacture.

## Datum and hardware

Exported X=0 is the body left in the front view. Y=0 is the front-panel plane; Z=0 is the chassis underside. Front view looks toward +Y. Rear elevations look toward -Y from outside the rear (+Y). The PSU is at the left, I/O and exhaust in the middle, and motherboard PCIe slots at the right in that exterior view. An inside-face view reverses this order. Rack ears extend beyond X=0 and X=440. Dimensions are millimetres.

PCIe bracket positions use 20.32 mm pitch; populated GPU sockets use 40.64 mm pitch. The board reference is the Miwin MG-SW510B 12-slot switch backplane. It has ten double-width sockets at 40.64 mm pitch and one single-width socket 20.32 mm beyond each end. The GPU carrier has twenty-one rear bracket positions:

- Ten dual-slot GPUs occupy two positions each.
- One position serves the leading single-width socket. The model reserves a PCIe CEM single-width card envelope there: 2.67 mm secondary-side and 14.47 mm primary-side component height, 1.61 mm from the first GPU envelope.
- The trailing single-width socket lies beneath the tenth GPU cooler and shares a rear position with that GPU's second bracket. It can hold a card only when the tenth GPU is absent.

The twelve sockets span 406.4 mm, twenty 20.32 mm pitches, so the twenty-one openings align with every socket. A twenty-second opening would fall outside the 436.4 mm rear panel.

Miwin lists four x16 slots per switch, eight in total. Photo labels suggest that the two end double-width sockets and both single-width sockets connect to host or NIC connectors. Confirm slot wiring with the supplier before assigning cards. Standard socket spacing on the Miwin board is an explicit assumption. Slot seating height, board-to-bracket relationship, latch geometry and connector keepouts still require supplier drawings or a physical fit sample.

Motherboard locations follow the SSI EEB dimensional drawing and the ten selected mounting holes in the ASUS manual. Use only those ten posts. The board has seven PCIe 5.0 x16 slots; one runs in x8 mode, which limits the retimer in that slot. The posts are catalog Harwin R30-1000802 M3 female–female spacers, 8 mm long and 5 mm across flats. The same posts support the backplane.

The motherboard tray and backplane crossbars are prepared on the bench with screws entering the posts from below. No nut is placed behind a standoff in the installed chassis. Backplane crossbars clamp from above into standard DIN 562 M4 square thin nuts captured between sheet guide strips. Load those nuts before fixing the rails to the tray. Set the posts and crossbars before fitting the PCB.

GPU bracket screws are standard #6-32 × 1/4 in screws that thread into the integral 1.2 mm rear-panel shelf. The shelf has a 90-degree outward bend with R1.2 inside and R2.4 outside. Its bearing height and screw axes match the brackets. Each screw axis has an extruded collar, 4.1 mm outside diameter and 1.3 mm below the shelf, tapped #6-32 UNC-2B from a 2.705 mm (#36) drill. Shelf and collar give 2.5 mm of thread. No nuts sit beneath the shelf, so the rear web needs no nut reliefs and every web between apertures joins the bend. Each collar edge lies 0.63 mm from the bend tangent, inside the press-brake die footprint, so the shelf is formed first and the collars are extruded and tapped afterward. Qualify thread strength for tightening torque and repeated GPU service. The lower motherboard bank keeps its separate 1.5 mm retention strip with captive hex nuts.

## Assembly and service

1. Form and deburr panels. Fit the rack-ear captive M4 nuts inside the sidewalls before installing components. Bolt each separate 3 mm rack ear to the body with M4 × 10 screws. The ears are not welded. Install captive nuts and welded sheet bridges before closing their joints. Apply a finish compatible with the chosen hardware and protect the threads.
2. Prepare motherboard posts and the bare motherboard tray on the bench. Install and fasten the empty tray in the chassis, then the motherboard. Fit the lower exhaust fans after the tray; one fan covers a rear tray screw.
3. Install the PSU before the adjacent upper bearing angle. Fit the AIO, motherboard cooler and retimers with the GPU cartridge removed. PSU replacement requires removing that bearing angle; it does not require reaching behind a board-mounted nut.
4. Prepare GPU rail nuts, crossbars and posts on the bench. Clamp crossbars from above, attach the backplane, then install the GPUs, the single-width card and their rear retention screws.
5. Seat and fasten the cartridge. Route internal MCIO and GPU power through the two forward passages. Connect and restrain bundles at the side brackets. The optional external entry accepts preterminated plugs after its removable insert is removed.
6. To service lower retimer retention screws, remove the GPU cartridge and the external MCIO entry frame, brush strips and its two fixing screws first. These removable parts otherwise obstruct a vertical screwdriver.
7. Install the perforated rear cover, then the side-fastened lid. To remove the cartridge, disconnect its cables and remove the lid, rear cover and cartridge hold-down screws first.

For the RM53-502 module, measure the original cover and establish a rated rack support arrangement before fabrication. Attach the adapter and empty upper body before installing the bearing angles, fans, rails or the cartridge; the side bearing angles cover four of the six module-to-adapter screws. The OEM lid screws are locating fasteners, not a qualified support for ten GPUs. The supplied OEM lower body is only an external size proxy; internal OEM interference has not been modeled.

## Front grille and rack ears

One full-width 440 mm removable grille covers the full fabricated front face. The 9U grille spans the AIO and both GPU fan rows. The module grille covers the 5U module face for all three intake options; the existing OEM lower fascia remains outside the module design. The front MCIO opening is absent. The perforation field uses 9 mm holes on 10 mm staggered pitch, with solid lands at fasteners. The module MCIO entry is in the rear cover.

The grille has independent M3 fasteners. Its 8.8 mm fan-head access holes allow removal without loosening the GPU fans. Chassis fans use short 5 × 8 mm self-tapping screws that form threads in the plastic frame. The 9U GPU fans seat directly against the 2 mm carrier, leaving 6 mm nominal penetration including the tapered lead. In the module, padded 120 and 140 mm fans sit on 1 mm front corner pads, leaving 5 mm penetration into plastic; 80 and 180 mm frames seat on the 2 mm carrier, leaving 6 mm. Each fan uses four screws and no nuts. The 9U rear exhaust fans use the same screw through the 1.2 mm rear panel, leaving 6.8 mm penetration. GPU and rear fan slots are 5.5 mm wide; the AIO mounting slots and fasteners retain their separate specification. Screw heads are modeled as 8.5 mm diameter. Select fan-approved screws and confirm the actual plastic lug depth; these dimensions are nominal procurement envelopes.

Each 3 mm rack ear has a 64 mm side leg and two rows of M4 mounting screws. The 9U ear has six side screws; the module ear has four. Standard M4 hex nuts are captured at the sidewall before internal hardware is fitted. Screw tips and nut envelopes are included in static checks. Rack rails or a rated shelf carry the loaded chassis; the ear joints still require structural qualification.

## Module rear MCIO entry

The module front is reserved for fan intake. External MCIO enters through a 140 mm-wide, top-open notch at the top of the rear cover, Z424.95–442.5, above the GPU brackets. Remove the two upper M3 screws and folded brush cap to expose a 17.55 mm-high passage. The lower U-frame remains on its two lower M3 screws. Refit the cap after feeding plugs, so the split brushes close around the cables. The cap return extends 9 mm behind the 485 mm body.

The tested connector envelope is 35 × 14 mm at Z427.45–441.45 mm. Nominal clearance is 1.05 mm below the lid and 46.09 mm above the GPU envelopes. The lid gap requires the actual connector tolerance to be checked. The optional cable route runs above the GPU bank and descends in the forward service bay; the internal motherboard connections retain their floor passages.

Before removing a GPU or the cartridge, disconnect and withdraw the external cables. Remove the lid and rear cover with its attached brush assembly, then disconnect and park internal cables. No cable-support shelf crosses the GPU extraction path.

## Verification limits

The reports distinguish analytic solid validity, static intersections, sampled removal paths, driver access and OpenSCAD mesh agreement. These are nominal geometry checks, not a production tolerance analysis or a physical assembly trial. Flexible cable routes are occupancy envelopes; they do not certify bend radius, connector strain or available harness length.

The 9U model offers six upper 120 × 38 mm fans in two rows, two 180 × 32 mm fans, or three 120 × 38 mm fans. Each option reserves 38 mm depth for the three AIO fans; the XE360-TR5 is supplied with 25 mm fans, so the allowance also accepts thicker replacements. Fan mounting pitch is 105 × 105 mm, referenced to the ARCTIC P12 engineering drawing; the P12 itself is a 25 mm fan. Select and verify the actual 38 mm fan. The two lower exhaust fans use the nominal 80 mm / 71.5 mm mounting pattern. The module intake options are described under the upper-module fan options below.

The AIO model reserves a 394 × 120 × 28 mm radiator. Radiator screw thread, allowable penetration and supplied screw lengths must be verified with the cooler hardware before release, particularly with 38 mm fans. Radiator mounting screws remain procurement/interface details rather than qualified component models. Chassis fan screws follow the [Noctua self-tapping installation method](https://www.noctua.at/en/support/faqs/how-do-i-install-a-case-fan); an [ARCTIC case-fan screw](https://www.arctic.de/en/Case-Fan-Screw/C-S-50-080B00) is a commercially available reference. The nominal screw model does not replace the selected fan supplier specification.

Assembly STEP files omit the routed cable envelopes for GPU power, backplane auxiliary power and MCIO; connector plug envelopes remain. `cable_routes.json` records the route centrelines, and the interactive viewer can display them.

Photo-derived backplane holes and component positions do not establish manufacturing accuracy. Flexible supports accommodate different hole positions within their travel, but they cannot compensate for a different PCIe socket-to-bracket datum. The alternative backplane outline is a fit envelope, not a qualified interchangeable installation.

The selected PSU has four native GPU 16-pin cables and four 8-pin GPU cables. Ten modeled GPU power routes do not establish sufficient connectors or a qualified electrical power budget. Thermal, structural, rack-rail, vibration and grounding requirements also need a populated prototype and engineering review.

## Fabrication release requirements

- Measure RM53-502 cover returns, seating profile, tabs and left/right screw centres. Enter the measurements into the adapter template and check the actual OEM interior.
- Obtain backplane mechanical drawings or measure the board, including mounting holes, socket seating height, underside keepouts and latch release access.
- Verify GPU dimensions, plug positions, fan model and cooler fasteners using the actual selected components.
- Confirm sheet material, finish, inside bend radii and K-factor with the fabricator's tooling, then regenerate the flat patterns. Specify welds and tolerances.
- Resolve the flanges shorter than the usual press-brake minimum of four thicknesses (6 mm for 1.5 mm steel): the 4.0 mm lower lips of both rear covers and the 4.5 mm legs of the backplane-rail and motherboard-tray bridges. The surrounding height stack fixes these sizes. Form them oversize and trim, use dedicated tooling, or substitute bought channels and spacers.
- Accept or relocate holes closer than two thicknesses to a bend line. The EIA-310 rack holes sit 3.05 mm from the rack-ear bend because the rack standard fixes their positions. The bridge screw holes sit 2.75 mm (rail bridges) and 1.3 mm (motherboard-tray bridges) from their bends. On the GPU rear panel, the outermost aperture sits 0.95 mm from the side-return bend; the backplane socket pitch fixes it, and the board leaves only 1 mm of side clearance for a shift. The tapped-collar holes sit 0.95 mm from the shelf bend, which is acceptable only because the collars are extruded after bending. `formed_part_checks.json` lists every case.
- Build an unpowered fit prototype, check every installation and removal step, then qualify load, cooling and electrical operation.


## Upper-module fan options

The replacement-lid module is 5U: 221.75 mm tall from its base at Z222.25 to its top at Z444.0, so the combined study envelope is 10U. The lid underside is 61.1 mm above the GPU envelopes. Three front intake options are available, each on its own removable front carrier with matching air openings and mounting slots:

| Option | Fan rows (centres X; centre Z) | Screw pattern | Air openings | Screw penetration |
| --- | --- | --- | --- | --- |
| 3 × 140 mm | 140 × 25: X78, 220, 362; Z330 | 124.5 square | DIA136 | 5 mm through 1 mm pad |
| 3 × 120 mm + 5 × 80 mm | 120 × 25: X78, 220, 362; Z299. 80 × 25: X52, 136, 220, 304, 388; Z401 | 105 square; 71.5 square | DIA116; DIA76 | 5 mm (120 mm, padded); 6 mm (80 mm) |
| 2 × 180 mm | 180 × 32: X128, 312; Z330 | 165 square | DIA175 | 6 mm |

The 120 mm row spans Z239–359, below and across the GPU bodies (Z269.6–381.4). The 80 mm row spans Z361–441 and blows rearward through the space above the GPUs, 1.5 mm below the lid underside. Front fans lie ahead of the GPU bodies, so the floor and lid limit their height. Rear 80 mm exhaust fans do not fit in 5U: a fan inside the rear cover overlaps the GPU rear ends in depth and would need the module top at about Z465.

Mounting slots are 5.5 mm wide obrounds with R2.75 ends. Screw axes closer than 25 mm share one slot of length equal to their spacing plus 9 mm; other axes have 9 mm slots. The shared slots are 26.5 mm for the 140 mm row, 21.5 mm for the 80 mm row and 28 mm for the 180 mm pair; the 120 mm row has only 9 mm slots. Each carrier fastens with four M3 screws per side through the body into captive nuts on its side returns. One full-face grille serves all three carriers. It has 8.8 mm tool-access holes at every fan screw axis of every option and five M3 fixings at X/Z (20, 231), (220, 231), (420, 231), (7.5, 425) and (432.5, 425), on carrier lands clear of all fan frames.

To change option, remove the grille, unscrew the fans, remove the carrier side screws and withdraw the carrier forward. Fit the other carrier, its fans and the grille. All fans use short 5 × 8 mm self-tapping screws without nuts; confirm screw suitability and retention torque with each fan supplier.

Fan references: the Noctua NF-A14 industrialPPC (140 × 140 × 25 mm, 141 × 141 × 27 mm padded) and NF-A12x25 PWM (120 × 120 × 25 mm, 27 mm padded) use 124.5 and 105 mm square patterns. The 80 mm reference is a 80 × 80 × 25 mm frame on the standard 71.5 mm square pattern, such as the Noctua NF-A8. The 180 mm reference is the SilverStone AP183 (180 × 180 × 32 mm, 165 mm square). Pad outlines and rotors are simplified references. Frame gaps are 1 mm between padded 140 mm fans, 22 mm between 120 mm fans, 4 mm between 80 mm fans and 4 mm between 180 mm fans.

Sources: [Noctua mounting-hole standards](https://www.noctua.at/en/products/nv-fm1), [140 mm fan dimensions](https://www.noctua.at/en/products/nf-a14-industrialppc-3000-pwm/specifications), [180 mm fan](https://www.silverstonetek.com/en/product/info/fans/AP183/), [SilverStone panel reference](https://www.silverstonetek.com/en/product/info/computer-chassis/rm53_502/).

## GPU rear-panel dimensions and retained toe strip

The twenty-one main rear apertures are 15.000 × 100.500 mm on 20.320 mm centres. Their top edges stop 2.63 mm below the shelf bend tangent, clear of the forming zone, leaving a nominal 5.320 mm web. These opening dimensions are chassis design choices. They are distinct from the 18.420 mm bracket width and the 40.640 mm spacing between populated GPU sockets.

The retention shelf has twenty-one tapped #6-32 UNC-2B holes at Y474.080, each 9.210 mm in positive X from its bracket centre. The bend runs uninterrupted from X3.500 to X436.045. Four side-return holes are 3.400 mm diameter (R1.700). Dedicated drawing sheets provide the position schedule, section dimensions and enlarged aperture details. The schedule names the card served by each position: exported position 21, at the largest X, serves the single-width card, and GPU 10 occupies positions 1 and 2.

The toe receiver remains a separate 1.5 mm flat comb, 12 mm deep for stiffness and weld access. Its twenty-one notches are 10.790 × 1.300 mm on 20.320 mm centres. The reference bracket toe is 10.190 × 0.860 mm, giving 0.600 mm total lateral clearance and 0.440 mm total fore-aft clearance. The locator lies above the rear web's lower edge; a simple bottom return would not reach its datum. Keeping the comb avoids individual lanced and formed tabs.

The proposed factory attachment uses twenty underside stitch fillet welds, each 6 mm long with a nominal 1 mm leg, between adjacent toe notches. Fixture the comb relative to the bracket-bearing surface and weld before rear-panel installation and coating. The strip stays on the cartridge during GPU insertion and vertical removal. Weld distortion, strength and bracket-gauge acceptance remain prototype checks. Rack ears remain screw-mounted.

## Drawing interpretation and manufacture

Formed-part views label exterior orientation. Feature-location diagrams instead use positive coordinate axes: the first listed axis increases right and the second increases up. Opposite walls have separate face views, each labeled with its normal-axis station. The complete analytic contour appears on every feature-location page. Dense coordinate schedules highlight the corresponding rows on an adjacent face view. Numbered leaders connect interface table entries to physical features.

Every bent sheet part is modeled as formed cold-rolled mild steel: each 90-degree bend has an inside radius equal to the sheet thickness and an outside radius of twice the thickness, and every flat face keeps its nominal position. Bends that stop short of a panel edge have relief slots one thickness wide and 0.5 mm deeper than the bend zone. On the GPU rear panel, each side return ends one thickness below the shelf bend, and a relief slot separates the two bends.

Each fabricated sheet piece has a developed flat pattern in `flat_patterns/`: a DXF of the blank with every hole and cutout, and `flat_patterns.json` with the blank size and a bend table giving each bend line, direction, inside radius and bend allowance. Development uses K-factor 0.40, so a 90-degree bend adds π/2 × (R + 0.4 T) to the blank. Joined assemblies, such as the front carriers, lids, lower rear panel and lid adapter, are developed piece by piece. The GPU shelf flat pattern marks each extruded collar at its 2.705 mm tap-drill diameter; the extrusion pierce size depends on the fabricator's tooling. `formed_part_checks.json` records the development results and checks every fastener against the formed parts. `assembly_overlaps.json` lists every overlapping pair of solids; the build fails unless each overlap is thread engagement or a cable or hose routing envelope. Parts that sit in the body's floor-to-wall corners stop clear of its inside bend radius. The GPU tray stiffening channels have 14 mm crowns so each bend has a formable flat between them. All dimensions are nominal; the radii and K-factor are defaults to confirm with the fabricator before blanks are cut, and production tolerances, material grade and finish are not yet released.

The front carriers combine 2 mm faces with 1.5 mm side angles. On the 9U carrier, grille mounting bores pass through 3.5 mm where sheets overlap. The lower rear panel and module rear sill combine 1.2 mm webs with 1.5 mm returns. Their drawings identify these as joined sheet assemblies. Side-angle attachment and weld qualification remain part of fabrication detailing.

The lower eight-position bank uses 15 × 103 mm apertures on 20.32 mm centres. Its separate toe strip has eight 10.79 × 1.30 mm edge-open notches. Seven proposed underside fillet welds, each 6 mm long with a nominal 1 mm leg, sit between the notches. The drawing gives their coordinates. Nominal weld envelopes clear the modeled hardware; strength, distortion and bracket-gauge acceptance require qualification.

The drawing coverage report accounts for all fabricated parts in both chassis and all six intake configurations. Flat plates have overall dimensions and opening schedules. Non-flat parts also have formed sections and planar surface extents. Open-edge details supplement closed-hole schedules. Section coordinates define nominal formed geometry; they do not supply a qualified bend allowance or developed blank.

## Full-chassis single-row intake options

The two single-row options use a common front carrier and full-face grille with interchangeable 390 × 220 × 2 mm inserts. Body height remains 399.25 mm and GPU tray height remains Z 170. These options do not establish that a shorter enclosure fits the hardware or cools adequately.

| Upper intake | Fan centres X / Z | Frame depth | Mounting pitch | Air opening |
| --- | --- | --- | --- | --- |
| Two 180 mm fans | 128, 312 /270 | 32 | 165 square | Diameter 175 |
| Three 120 mm fans | 100, 220, 340 /270 | 38 allowance | 105 square | Diameter 116 |

The 180 mm reference is the [SilverStone AP183 engineering drawing](https://www.silverstonetek.com/upload/goods_cable_define/fan-cable-define.pdf). It specifies a 180 ×180 ×32 frame, 165 mm square mounting, 4.5 mm fan bores and a recommended 175 mm panel aperture. Fan frame and rotor details remain simplified reference envelopes. Do not assume another 180 mm model uses the same pattern.

Both inserts have horizontal clearance slots 5.5 mm wide with R 2.75 ends. Outer slots are 9 mm long. Shared slots are 24.5 mm long for the 180 mm pair and 24 mm for the 120 mm row. Four nominal 5 ×8 self-tapping screws per fan penetrate 6 mm into plastic, including the tip. Confirm the selected fan's approved screw and retention torque.

The carrier has a 392 ×222 opening, leaving 1 mm clearance at each insert edge. A factory-attached 398 ×240 ×2 mm backing ring provides a 370 ×200 clear window behind it. Six M3 ×8 screws enter from the front and engage standard M3 nuts captured behind the ring before installation. The modeled joint has 4 mm of sheet and 2.4 mm of nut, with 1.6 mm nominal tip projection. The ring remains fixed when the insert is removed; qualify its attachment strength and distortion before fabrication.

For service, remove the full-face grille, disconnect fan leads and remove the six insert screws. Pull the insert and its fans straight forward. The two 180 mm frames occupy 364 mm across the 370 mm backing opening, giving 3 mm clearance per side; the 120 mm row leaves 5 mm per side. Fan leads need disconnectable service length. The original six-fan option uses its separate two-row carrier; changing between that carrier and the single-row carrier requires front-panel replacement.

`full_intake_checks.json` records validity, changed-part intersections, mounting and airflow gauges, and sampled forward removal. It also compares the 539 common parts with the six-fan chassis by analytic volume, bounds and face and edge counts. OpenSCAD mesh checks accompany each single-row option. Static geometry checks do not establish comparative airflow, acoustic performance or GPU temperature.

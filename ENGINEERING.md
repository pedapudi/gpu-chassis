# Motherboard and GPU chassis engineering package

This package contains a 9U full enclosure and an upper GPU module proposed as a replacement lid for the SilverStone RM53-502. Both use a 440 × 485 mm body footprint and a removable twenty-position GPU cartridge. The full enclosure reserves a lower layer for the ASUS WRX90E-SAGE SE motherboard, XE360-TR5 AIO and ASUS Pro WS 3000P power supply.

**Status: engineering review, not released for fabrication.** The nominal assemblies can be inspected and their modeled geometry checked. The OEM lid interface, supplier backplane details, latch access and production sheet-metal forming remain unresolved. A flawless physical installation cannot be established from photographs and nominal envelopes.

## Files

Each design folder contains an assembly STEP, individual formed-part STEP files, OpenSCAD sources, a drawing PDF, coordinate schedules, a bill of materials, and validation reports. `interactive_model.html` displays meshes compiled from the individual OpenSCAD sources. It runs locally without network dependencies. A vector engineering-drawing pane sits beside the 3D model. Select a sheet, zoom, or select a fabricated component to open its matching drawing; Open PDF accesses the complete drawing set.

The STEP files preserve analytic surfaces. The OpenSCAD files describe faceted part solids with editable visibility, placement and cartridge-lift controls. They are not fully dimension-parametric recreations of every manufactured part. Rebuild dimension changes with the supplied Python CAD sources. The modular folder also includes a native constructive-solid-geometry adapter template with parameters for measured OEM hole coordinates and return profiles.

The drawing PDFs show nominal formed geometry. Their coordinate CSVs list analytic line endpoints and circle/arc centres in the assembly coordinate system. A circle record can represent a hole, a boss or an arc; compare it with the part drawing and STEP. Face-profile DXFs are not developed sheet-metal blanks. Do not send them directly to a laser cutter as flat patterns.

## Datum and hardware

Exported X=0 is the body left in the front view. Y=0 is the front-panel plane; Z=0 is the chassis underside. Front view looks toward +Y. Rear elevations look toward -Y from outside the rear (+Y). The PSU is at the left, I/O and exhaust in the middle, and motherboard PCIe slots at the right in that exterior view. An inside-face view reverses this order. Rack ears extend beyond X=0 and X=440. Dimensions are millimetres.

PCIe bracket positions use 20.32 mm pitch; populated GPU sockets use 40.64 mm pitch. The board reference is the Miwin MG-SW510B 12-slot switch backplane, modeled with ten GPU sockets plus two auxiliary end sockets. The GPU carrier remains twenty rear bracket positions for ten dual-slot GPUs; selecting the 12-slot board does not add rear openings. Standard spacing on the Miwin board is an explicit assumption. Slot seating height, board-to-bracket relationship, latch geometry and connector keepouts still require supplier drawings or a physical fit sample.

Motherboard locations follow the SSI EEB dimensional drawing and the ten selected mounting holes in the ASUS manual. Use only those ten posts. The posts are catalog Harwin R30-1000802 M3 female–female spacers, 8 mm long and 5 mm across flats. The same posts support the backplane.

The motherboard tray and backplane crossbars are prepared on the bench with screws entering the posts from below. No nut is placed behind a standoff in the installed chassis. Backplane crossbars clamp from above into standard DIN 562 M4 square thin nuts captured between sheet guide strips. Load those nuts before fixing the rails to the tray. Set the posts and crossbars before fitting the PCB.

PCIe retention uses standard #6-32 screws and hex nuts captured during fabrication. Local rear-sheet reliefs clear the nut corners. Captive ordinary nuts are trapped or tack-welded before panels close access; weld details and production fixtures must be specified by the fabricator. Catalog hardware is not replaced by machined custom screw or standoff parts.

## Assembly and service

1. Form and deburr panels. Fit the rack-ear captive M4 nuts inside the sidewalls before installing components. Bolt each separate 3 mm rack ear to the body with M4 × 10 screws. The ears are not welded. Install captive nuts and welded sheet bridges before closing their joints. Apply a finish compatible with the chosen hardware and protect the threads.
2. Prepare motherboard posts and the bare motherboard tray on the bench. Install the empty tray in the chassis, then the motherboard.
3. Install the PSU before the adjacent upper bearing angle. Fit the AIO, motherboard cooler and retimers with the GPU cartridge removed. PSU replacement requires removing that bearing angle; it does not require reaching behind a board-mounted nut.
4. Prepare GPU rail nuts, crossbars and posts on the bench. Clamp crossbars from above, attach the backplane, then install GPUs and their rear retention screws.
5. Seat and fasten the cartridge. Route internal MCIO and GPU power through the two forward passages. Connect and restrain bundles at the side brackets. The optional external entry accepts preterminated plugs after its removable insert is removed.
6. To service lower retimer retention screws, remove the GPU cartridge and the external MCIO entry frame, brush strips and its two fixing screws first. These removable parts otherwise obstruct a vertical screwdriver.
7. Install the perforated rear cover, then the side-fastened lid. To remove the cartridge, disconnect its cables and remove the lid, rear cover and cartridge hold-down screws first.

For the RM53-502 module, measure the original cover and establish a rated rack support arrangement before fabrication. Attach the adapter and empty upper body before installing fans, rails or the cartridge. The OEM lid screws are locating fasteners, not a qualified support for ten GPUs. The supplied OEM lower body is only an external size proxy; internal OEM interference has not been modeled.

## Front grille and rack ears

One full-width 440 mm removable grille covers the full fabricated front face. The 9U grille spans the AIO and both GPU fan rows. The module grille covers either three 140 mm fans or three 120 mm fans across its upper front face; the existing OEM lower fascia remains outside the module design. The front MCIO opening is absent. The perforation field uses 9 mm holes on 10 mm staggered pitch, with solid lands at fasteners. The module MCIO entry is in the rear cover.

The grille has independent M3 fasteners. Its 8.8 mm fan-head access holes allow removal without loosening the GPU fans. Chassis fans use short 5 × 8 mm self-tapping screws that form threads in the plastic frame. The 9U GPU fans seat directly against the 2 mm carrier, leaving 6 mm nominal penetration including the tapered lead. The module uses a 1 mm front corner pad, leaving 5 mm penetration into plastic with 140 mm fans, or 4 mm with the 120 mm blanking plates installed. Each fan uses four screws and no nuts. The 9U rear exhaust fans use the same screw through the 1.2 mm rear panel, leaving 6.8 mm penetration. GPU and rear fan slots are 5.5 mm wide; the AIO mounting slots and fasteners retain their separate specification. Screw heads are modeled as 8.5 mm diameter. Select fan-approved screws and confirm the actual plastic lug depth; these dimensions are nominal procurement envelopes.

Each 3 mm rack ear has a 64 mm side leg and two rows of M4 mounting screws. The 9U ear has six side screws; the module ear has four. Standard M4 hex nuts are captured at the sidewall before internal hardware is fitted. Screw tips and nut envelopes are included in static checks. Rack rails or a rated shelf carry the loaded chassis; the ear joints still require structural qualification.

## Module rear MCIO entry

The module front is reserved for fan intake. External MCIO enters through a 140 mm-wide, top-open rear notch above the GPU brackets. Remove the two upper M3 screws and folded brush cap to expose a 17.55 mm-high passage. The lower U-frame remains on its two lower M3 screws. Refit the cap after feeding plugs, so the split brushes close around the cables. The cap return extends 9 mm behind the 485 mm body.

The tested connector envelope is 35 × 14 mm at Z383–397 mm. Nominal clearance is 1.05 mm below the lid and 1.64 mm above the GPU envelopes. These small gaps require actual connector and GPU tolerances to be checked. The optional cable route runs above the GPU bank and descends in the forward service bay; the internal motherboard connections retain their floor passages.

Before removing a GPU or the cartridge, disconnect and withdraw the external cables. Remove the lid and rear cover with its attached brush assembly, then disconnect and park internal cables. No cable-support shelf crosses the GPU extraction path.

## Verification limits

The reports distinguish analytic solid validity, static intersections, sampled removal paths, driver access and OpenSCAD mesh agreement. These are nominal geometry checks, not a production tolerance analysis or a physical assembly trial. Flexible cable routes are occupancy envelopes; they do not certify bend radius, connector strain or available harness length.

The 9U model provides six upper 120 × 38 mm fans and three assumed 38 mm AIO fans. Fan mounting pitch is 105 × 105 mm, referenced to the ARCTIC P12 engineering drawing; the P12 itself is a 25 mm fan. Select and verify the actual 38 mm fan. The two lower exhaust fans use the nominal 80 mm / 71.5 mm mounting pattern. The module uses the [Noctua NF-A14 industrialPPC mounting reference](https://www.noctua.at/en/products/nf-a14-industrialppc-3000-pwm/specifications): 140 × 140 × 25 mm bare, 141 × 141 × 27 mm padded, and 124.5 mm square hole pitch. Centres are X78, 220 and 362 mm at Z310.9 mm. Pads have nominal corner outlines within the published envelope. The 142 mm centre pitch leaves 1 mm gaps between padded fans.

The AIO model reserves a 394 × 120 × 28 mm radiator. Radiator screw thread, allowable penetration and supplied screw lengths must be verified with the cooler hardware before release, particularly with 38 mm fans. Radiator mounting screws remain procurement/interface details rather than qualified component models. Chassis fan screws follow the [Noctua self-tapping installation method](https://www.noctua.at/en/support/faqs/how-do-i-install-a-case-fan); an [ARCTIC case-fan screw](https://www.arctic.de/en/Case-Fan-Screw/C-S-50-080B00) is a commercially available reference. The nominal screw model does not replace the selected fan supplier specification.

Photo-derived backplane holes and component positions do not establish manufacturing accuracy. Flexible supports accommodate different hole positions within their travel, but they cannot compensate for a different PCIe socket-to-bracket datum. The alternative backplane outline is a fit envelope, not a qualified interchangeable installation.

The selected PSU has four native GPU 16-pin cables and four 8-pin GPU cables. Ten modeled GPU power routes do not establish sufficient connectors or a qualified electrical power budget. Thermal, structural, rack-rail, vibration and grounding requirements also need a populated prototype and engineering review.

## Fabrication release requirements

- Measure RM53-502 cover returns, seating profile, tabs and left/right screw centres. Enter the measurements into the adapter template and check the actual OEM interior.
- Obtain backplane mechanical drawings or measure the board, including mounting holes, socket seating height, underside keepouts and latch release access.
- Verify GPU dimensions, plug positions, fan model and cooler fasteners using the actual selected components.
- Specify sheet material, finish, bend radius, reliefs, bend allowance, welds and tolerances. Produce developed blanks from the qualified formed geometry.
- Build an unpowered fit prototype, check every installation and removal step, then qualify load, cooling and electrical operation.


## Upper-module fan options

The replacement-lid module accepts either three 140 mm fans or three 120 mm fans on the same front carrier and full-face grille. Both configurations keep the centres at X78, 220 and 362 mm, Z310.9 mm. The default 140 mm option uses the full 136 mm carrier openings. The 120 mm option adds three 140 × 140 × 1 mm flat blanking plates behind the carrier, each with a 116 mm opening and four 5.5 mm clearance holes on a 105 mm square. The plates close the exposed portions of the larger openings and are retained by the fan screws; there are no adapter nuts or separate adapter screws.

The 140 mm pattern is 124.5 × 124.5 mm. Its outer slots are 9 × 5.5 mm and shared adjacent-screw slots are 27 × 5.5 mm. The 120 mm pattern is 105 × 105 mm. Its outer slots are 7 × 5.5 mm and shared slots are 44 × 5.5 mm. Shared slots connect the two neighbouring fans' screw positions; their length is not the fan mounting pitch. The common grille has access holes for both patterns.

The 120 mm option has a 2 mm carrier, 1 mm blanking plate and 1 mm front pad ahead of the plastic frame. A 5 × 8 mm fan screw therefore enters the plastic by 4 mm including its tapered tip; the 140 mm option has 5 mm penetration. Confirm screw suitability and retention torque with the chosen fan. Both configurations use short self-tapping screws without nuts. To change size, remove the grille, unscrew the fans from the front, add or remove the blanking plates, and install the selected fans and grille.

The 120 mm fan reference is the Noctua NF-A12x25 PWM: 120 × 120 × 25 mm bare, 120 × 120 × 27 mm with pads, and 105 × 105 mm mounting pitch. The 140 mm fan reference is the Noctua NF-A14 industrialPPC: 140 × 140 × 25 mm bare, 141 × 141 × 27 mm with pads, and 124.5 × 124.5 mm mounting pitch. Pad outlines and rotors are simplified references. The 120 mm option retains 22 mm gaps between fan frames; its blanking plates retain 2 mm gaps. The mounting patterns are based on manufacturer specifications, not measurements scaled from photographs.

Sources: [120 mm fan dimensions](https://www.noctua.at/en/products/nf-a12x25-pwm/specifications), [140 mm fan dimensions](https://www.noctua.at/en/products/nf-a14-industrialppc-3000-pwm/specifications), [SilverStone panel reference](https://www.silverstonetek.com/en/product/info/computer-chassis/rm53_502/).

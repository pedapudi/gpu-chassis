# Drawing coverage

The drawing sets cover both chassis and both intake options for the RM53-502 module. Counts below include shared parts repeated in each configuration. Dimensions describe the nominal CAD geometry; they do not establish manufacturing tolerances or measured supplier fit.

| Configuration | Fabricated parts | Drawing sheets | Formed-section sheets | Surface-extent sheets |
| --- | ---: | ---: | ---: | ---: |
| 9U full chassis | 44 | 211 | 28 | 28 |
| Module, three 140 mm fans | 36 | 176 | 24 | 24 |
| Module, three 120 mm fans | 39 | 185 | 24 | 24 |

Every fabricated part has an overall drawing and analytic edge coordinates. Closed openings receive diameter, radius, length, width and position schedules as applicable. Non-flat parts also receive cross-sections and planar surface extents. Dedicated interface sheets dimension open-edge contours and assemblies that a closed-hole list cannot describe.

## Interface details

- Both GPU carriers: twenty 15 × 103 mm apertures on 20.32 mm centres, retention screw axes, reliefs, integral R1.2 shelf bend and separate toe-comb engagement.
- 9U lower rear: eight bracket apertures, nut reliefs, toe notches and proposed weld locations, I/O shield datum, fan openings and stepped PSU cutout with a complete vertex schedule.
- Front carriers and rear panels: joined sheet thicknesses are identified where webs and returns differ. Surface tables locate return ends and overlap lands.
- Module cable entry: rear-cover notch, lower U-frame, removable cap, fastening order and connector passage.
- Lids and adapter: return length, depth, end setbacks, screw axes and seating levels. The adapter's OEM fastening holes remain undrilled pending measurement.
- Adjustable supports: X and Y travel, rail guide gap, catalog spacer attachment and installed Z levels from tray underside through PCB top.
- Rack ears: screw-mounted joints and the 9U open-edge circular clearance notch.

## Verification evidence

The coverage audit accounts for all 119 fabricated-part entries and checks 4,311 closed-feature records across the three drawing sets. It checks positive sizes, sheet-face stations, circular diameter/radius agreement, obround end radii, section coverage and continuous page numbering. Section cuts through the GPU tray, lid and retention shelf are explicitly placed within their folds.

Twenty-five additional geometry checks verify lower-bank aperture and toe-notch gauges, proposed toe-weld envelopes, rear contact and the finished I/O shield opening. Weld checks establish geometric clearance only. The PDFs are rendered page by page and checked for text outside page boundaries and missing glyphs; independent reviews inspect interface dimensions and added formed sections.

The STEP and OpenSCAD geometry is unchanged by this drawing revision. The package preserves those files byte for byte and retains their existing geometry, interference and service-access reports. The drawing audit does not extend those reports to unmodeled cables, production tolerances or physical hardware.

## Fabrication requirements

The drawings retain explicit requirements for measured OEM lid fit, supplier backplane interfaces, material grade, finish, production tolerances, bend tooling and developed blanks. Most fixed sheet joints still require qualified weld specifications. Proposed toe welds and captive-nut attachment need strength, distortion, torque and service-cycle qualification. Detailed nominal dimensions do not close these requirements.

The machine-readable `specificity_audit.json` lists coverage for every part. Each design's `drawings/specificity_coverage.json` identifies its sections and surface tables. `nine-u/drawing_interface_checks.json` records the additional geometric checks, and `pdf_quality.json` records page-boundary checks.

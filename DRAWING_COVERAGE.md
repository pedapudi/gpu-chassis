# Drawing coverage

The full chassis and replacement-lid module include complete part views with dimensions and linked schedules. The five configurations repeat shared parts; counts describe each complete drawing set.

| Configuration | Fabricated parts | Sheets | Section sheets | Face sheets |
| --- | ---: | ---: | ---: | ---: |
| 9U, six 120 mm fans | 44 | 219 | 28 | 39 |
| 9U, two 180 mm fans | 45 | 224 | 28 | 39 |
| 9U, three 120 mm fans | 45 | 224 | 28 | 39 |
| Module, three 140 mm fans | 36 | 190 | 24 | 35 |
| Module, three 120 mm fans | 39 | 196 | 24 | 35 |

Feature-location sheets show complete physical face contours, including actual holes and open-edge cuts. Opposite walls have separate views. Circular holes use analytic circles; leaders specify counts, diameters, radii, and slot dimensions. Dense coordinate tables share the page with the face outline and highlighted hole rows. Complex cutouts retain their actual contours.

Interface tables use numbered leaders tied to specific features. Rear elevations directly dimension PCIe apertures and pitch; enlarged details show retention bores, toe notches, and the integral retention bend. Additional CAD sections illustrate the adjacent-GPU gap, PSU screw-tip clearance, lower exhaust/I/O clearance, and installed backplane support height. Fan-option drawings dimension mounting pitch on the carrier geometry.

Formed sections carry overall dimensions directly on the profile, with coordinate levels beside the diagram. Face sheets show the actual surface perimeter and coordinate limits. Drawing indexes remain separate navigation tables.

Each drawing set includes a diagram-completeness report. The generator rejects technical table pages without drawing geometry. The coverage audit checks fabricated-part coverage, feature dimensions, diameter/radius agreement, slot radii, section coverage, and page numbering. Every PDF page is rendered and checked for missing glyphs and text outside the page. Independent visual reviews inspect contours, feature correspondence, annotation spacing, and viewpoint labels.

This revision changes drawings and viewer drawing indexes. STEP and OpenSCAD geometry remain byte-for-byte unchanged. Nominal dimensions do not establish production tolerances or physical supplier fit. Backplane measurements, OEM lid interfaces, unspecified bend radii, developed blanks, fixed-joint strength, cooling, and power qualification remain release requirements.

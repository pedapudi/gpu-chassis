# Drawing coverage

The full chassis and replacement-lid module include complete part views with dimensions and linked schedules. The six configurations repeat shared parts; counts describe each complete drawing set. Joined assemblies have one flat-pattern sheet per sheet piece, so flat-pattern sheets can outnumber fabricated parts.

| Configuration | Fabricated parts | Sheets | Section sheets | Face sheets | Flat-pattern sheets |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9U, six 120 mm fans | 36 | 258 | 20 | 48 | 42 |
| 9U, two 180 mm fans | 37 | 265 | 20 | 48 | 44 |
| 9U, three 120 mm fans | 37 | 265 | 20 | 48 | 44 |
| Module, three 140 mm fans | 32 | 233 | 20 | 46 | 40 |
| Module, three 120 mm + five 80 mm fans | 32 | 235 | 20 | 46 | 40 |
| Module, two 180 mm fans | 32 | 233 | 20 | 46 | 40 |

Feature-location sheets show complete physical face contours, including actual holes and open-edge cuts. Opposite walls have separate views. Circular holes use analytic circles; leaders specify counts, diameters, radii, and slot dimensions. Dense coordinate tables share the page with the face outline and highlighted hole rows. Complex cutouts retain their actual contours.

Interface tables use numbered leaders tied to specific features. Rear elevations directly dimension PCIe apertures and pitch; enlarged details show tapped retention holes, toe notches, and the integral retention bend. Each bracket position in the rear schedule names the card it serves. Additional CAD sections illustrate the adjacent-GPU gap, PSU screw-tip clearance, lower exhaust/I/O clearance, and installed backplane support height. Fan-option drawings dimension mounting pitch on the carrier geometry.

Every sheet piece also has a flat-pattern sheet drawn from its developed DXF, with dashed bend centrelines and a bend table giving direction, inside radius, bend allowance, length and flange lengths.

Formed sections carry overall dimensions directly on the profile, with coordinate levels beside the diagram. Face sheets show the actual surface perimeter and coordinate limits. Drawing indexes remain separate navigation tables.

Each drawing set includes a diagram-completeness report. The generator rejects technical table pages without drawing geometry. `specificity_coverage.json` records each fabricated part and its section and face sheets. Every PDF page is converted to a vector sheet for the viewer. The structural checks do not detect every annotation collision; inspect rendered sheets before release.

Nominal dimensions do not establish production tolerances or physical supplier fit. Backplane measurements, OEM lid interfaces, fabricator confirmation of bend radii and K-factor, fixed-joint strength, cooling, and power qualification remain release requirements.

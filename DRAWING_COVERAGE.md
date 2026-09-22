# Drawing coverage

Both chassis include direct geometry annotations and coordinate schedules. The five configurations repeat shared parts; counts describe each complete drawing set.

| Configuration | Fabricated parts | Sheets | Section sheets | Surface sheets |
| --- | ---: | ---: | ---: | ---: |
| 9U, six 120 mm fans | 44 | 213 | 28 | 28 |
| 9U, two 180 mm fans | 45 | 218 | 28 | 28 |
| 9U, three 120 mm fans | 45 | 218 | 28 | 28 |
| Module, three 140 mm fans | 36 | 176 | 24 | 24 |
| Module, three 120 mm fans | 39 | 185 | 24 | 24 |

PCIe rear elevations carry aperture width, height and centre-spacing dimensions directly on the CAD profile. Enlarged details dimension retention bores, their offset from bracket centres, and toe-notch width and depth. The lower rear elevation identifies the 164 × 50 mm web clearance separately from the smaller I/O shield reference. Rear elevations preserve exterior handedness.

Every closed-hole family has a leader with count, diameter and radius, or slot length, width and end radius. Complex profile bounds are explicitly labeled; exact edges remain on the formed view and STEP. Coordinate tables locate every repeat and distinguish coincident projections of separate flanges. Boundaries at joined-sheet steps are labeled as boundaries rather than through-holes. Open-edge contours, formed sections, sheet thicknesses, support heights and fastening sequences have dedicated details.

The two single-row intake drawings dimension fan mounting pitch, opening diameter, insert screws and slot sizes. The six-fan carrier and module carriers retain their own hole schedules and view annotations.

The coverage audit checks every fabricated part, positive dimensions, diameter/radius agreement, slot radii, section coverage and page numbering. All PDF pages are rendered and checked for text outside page boundaries. Independent visual reviews inspect the updated leaders, rear dimensions and fan-pattern details. Nominal dimensions do not establish production tolerances or physical supplier fit.

The single-row full-chassis variants additionally pass changed-part intersection checks, mounting and airflow gauges, sampled front removal, STEP round trips and compiled OpenSCAD mesh checks. Their 558 common analytic parts match the six-fan chassis. Manufacturer backplane measurements, OEM lid interfaces, forming allowances, fixed-joint strength, cooling and power qualification remain release requirements.

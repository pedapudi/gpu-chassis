# Generate annotated engineering drawings

The generator reads analytic part snapshots and validation metadata from the CAD rebuild directory. Use the CAD virtual environment and the dependencies in `drawing_source/requirements.txt`.

Run the drawing generator for each available configuration:

```sh
python drawing_source/make_drawings.py nine-u scratch
python drawing_source/make_drawings.py nine-u-180 scratch
python drawing_source/make_drawings.py nine-u-120 scratch
python drawing_source/make_drawings.py modular scratch
python drawing_source/make_drawings.py modular-120 scratch
```

Each command writes a PDF, feature JSON, edge CSV, bill of materials, drawing index, and diagram-completeness report beneath the configuration's `drawings/` directory. Existing STEP files remain unchanged. Use a fresh rebuild directory after changing CAD geometry. `--reuse-views` requires unchanged geometry and projection settings.

Every feature-location page shows the complete physical face, including its outer contour, holes, and open-edge cuts. Opposite walls have separate views. Circular holes use analytic circles. Leaders give feature counts, diameters, slot dimensions, and radii beside the corresponding geometry. Dense coordinate schedules share the page with a complete face view and highlight the rows listed in the schedule.

Formed sections carry dimensions on the profile. The adjacent tables record coordinate levels and step sizes. Sheet-face pages show actual contours and coordinate limits, including returns and joined sheet components. Interface schedules use numbered leaders to identify the features described by each row. Enlarged sections illustrate retention bends, GPU clearances, PSU screw clearance, and backplane support height.

`diagram_completeness.json` records table and geometry counts for every sheet. The generator rejects a technical table page without drawing geometry. Drawing indexes are navigation tables and are exempt. `specificity_coverage.json` records every fabricated part and its section coverage. Render every PDF page and inspect the resulting images before publication; the structural checks do not detect all annotation collisions or incorrect leaders.

Dimensions describe nominal formed geometry. Supplier interfaces, production tolerances, unspecified bend radii, developed blanks, fixed-joint strength, and thermal performance still require qualification.

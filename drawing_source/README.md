# Generate dimensioned drawings

The drawing generator reads analytic part snapshots and validation metadata from the CAD rebuild directory. Use the same virtual environment as the CAD rebuild and install `drawing_source/requirements.txt` there.

After `python cad_source/rebuild.py --out scratch --variant both`, run:

```sh
python drawing_source/make_drawings.py nine-u scratch
python drawing_source/make_drawings.py modular scratch
python drawing_source/make_drawings.py modular-120 scratch
```

Each command writes the PDF, feature JSON, edge CSV, bill of materials and drawing index under its design's `drawings/` directory. Use a fresh rebuild directory for geometry changes. `--reuse-views` is only valid when geometry and projection settings are unchanged.

Hole schedules distinguish opposing sheet faces and omit solid flange-root boundaries. Round holes specify diameter and radius; slots specify overall length, width, end radius and orientation. Part-specific interface sheets dimension open-edge contours that are absent from closed-hole schedules.

Formed sections show the cross-sectional steps and thicknesses of non-flat parts. Sheet-face extent tables locate return ends and joined sheet components in the assembly datum. These tables enclose each planar surface; they do not replace its hole or notch schedule. Section planes pass through the defining folds of the tray, lid and GPU retention shelf. The matching JSON files record section edges and surface extents.

`specificity_coverage.json` accounts for every fabricated part in each drawing set. Flat parts use their overall and opening schedules; non-flat parts also receive sections and surface-coordinate tables. Dimensions come from analytic geometry. These drawings describe nominal formed parts; tooling, production tolerances, supplier interfaces and developed blanks still require qualification.

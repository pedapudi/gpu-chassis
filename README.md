# GPU chassis

Sheet-metal models and interactive engineering viewers for a 9U full chassis and a 5U upper module for the SilverStone RM53-502. Both retain a twenty-one-position GPU cartridge referenced to the twelve-socket Miwin backplane. Replaceable 8.5 mm printed adapters and standard 8 mm metric spacers locate the PCB. Separate fan carriers, screw-mounted rack ears and a removable stock-mesh cover simplify fabrication.

- [Open both viewers](https://pedapudi.github.io/gpu-chassis/)
- [Construction, metric hardware and assembly](MANUFACTURING.md)
- [Interface dimensions and qualification limits](ENGINEERING.md)
- [Drawing coverage](DRAWING_COVERAGE.md)

Each chassis has one compact drawing book covering its fan options. Shared parts appear once. Individual STEP files contain manufactured chassis parts and printed adapters; assembly STEP files contain chassis structure and hardware. GPUs, motherboards, fans, cables and hoses remain optional viewer references and have no separate STEP exports. Select a part in the viewer to download its STEP.

Each adapter half measures 209.5 x 240 x 8.5 mm. Both fit separately on a 256 x 256 mm print bed with a 5 mm brim. The halves fasten independently to the steel tray.

The full chassis offers six 120 mm, two 180 mm or three 120 mm intake fans. The upper module offers three 140 mm, three 120 mm with five 80 mm fans, or two 180 mm fans. Fan toggles preserve the camera position.

**Engineering review only.** Measure the OEM lid interface and backplane mounting holes before fabrication. Verify printed-material temperature performance, structural loads, production tolerances, cooling and electrical integration with a physical prototype.

## Build the manufacturing package

Use a virtual environment with `cad_source/requirements.txt` and `drawing_source/requirements.txt`. Build into fresh directories:

```sh
python cad_source/rebuild.py --out work/baseline --variant both
python scripts/build_manufacturing_revision.py work/baseline work/package
python scripts/validate_manufacturing_revision.py work/baseline work/package
python drawing_source/compact_drawings.py work/package
python scripts/build_compact_viewers.py work/package path/to/local/threejs-libraries
```

The viewer builder expects `three.min.js` and `OrbitControls.js` in the library directory. It writes static pages with local assets and vector drawing sheets. The analytic Python sources control dimensions. Individual part STEP files preserve assembly coordinates; printed STL files are placed on the print bed at Z0.

The baseline generator supplies the established chassis interfaces. The manufacturing pass replaces PCB rails, rail bosses and front grilles, and substitutes catalog press nuts where their seating and edge requirements fit. Its reports list remaining formed-thread exceptions. Do not use baseline parts as substitutes for manufacturing-package parts.

## Publish

GitHub Pages deploys through `.github/workflows/pages.yml`. `bundle.json` identifies a release ZIP and its SHA-256. `scripts/prepare_pages.py` verifies the archive before publishing the viewers, compact PDFs and downloadable CAD parts. Package files live under a `chassis-engineering/` archive root.

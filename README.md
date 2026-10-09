# GPU chassis

Sheet-metal models and interactive engineering viewers for a 9U full chassis and a 5U upper module for the SilverStone RM53-502. Both retain a twenty-one-position GPU cartridge referenced to the twelve-socket Miwin backplane. Replaceable 8.5 mm printed adapters and standard 8 mm metric spacers locate the PCB. Separate fan carriers, screw-mounted rack ears and a riveted frame-and-mesh front cover simplify fabrication. The cover removes as one assembly using five screws on the module or eight on the full chassis.

- [Open both viewers](https://pedapudi.github.io/gpu-chassis/)
- [Construction, metric hardware and assembly](MANUFACTURING.md)
- [Interface dimensions and qualification limits](ENGINEERING.md)
- [Drawing coverage](DRAWING_COVERAGE.md)

Each chassis has one compact drawing book covering its fan options. Shared parts appear once. Individual STEP files contain manufactured chassis parts and printed adapters; assembly STEP files contain chassis structure and hardware. GPUs, motherboards, fans, cables and hoses remain optional viewer references and have no separate STEP exports. Select a part in the viewer to download its STEP. Each viewer also links to a front-cover assembly STEP, including the frame, mesh, rivets and backing washers.

Each eight-page book has a parts list on sheet 2 beside an annotated assembly view. The list gives drawing references, linked McMaster-Carr item numbers and quantities for each fan option, including modeled fasteners and catalog spacers. Matching parts-list and hardware-list CSV files include supplier URLs. Custom parts and equipment-supplied screws are identified separately. Electronics, cooling equipment and installation consumables require a separate kit.

Rounded mesh-cover corners and rack-ear corners remove sharp plan-view points; all exposed sheet edges still require deburring. A removable crossbar ties the side walls together with four top-access M4 screws. Twenty captive M3 threads on the crossbar accept custom printed GPU supports. The package defines the mounting interface; support shape, material, padding and screw length depend on the actual GPU. Remove the bar before GPU or cartridge service. The rear stock-mesh frame and its screws remain installed during cartridge extraction. Screw-mounted tray handholds remain attached; their load capacity requires qualification.

Each adapter half measures 209.5 x 240 x 8.5 mm. Both fit separately on a 256 x 256 mm print bed with a 5 mm brim. The halves fasten independently to the steel tray.

The full chassis offers three complete interchangeable fan plates for six 120 mm, two 180 mm or three 120 mm intake fans. Each includes the lower AIO mounting pattern. The upper module offers three 140 mm, three 120 mm with five 80 mm fans, or two 180 mm fans. Fan toggles preserve the camera position.

**Engineering review only.** Measure the OEM lid interface and backplane mounting holes before fabrication. Verify printed-material temperature performance, structural loads, production tolerances, cooling and electrical integration with a physical prototype.

## Build the manufacturing package

Use a virtual environment with `cad_source/requirements.txt` and `drawing_source/requirements.txt`. Build into fresh directories:

```sh
python cad_source/rebuild.py --out work/baseline --variant both
python scripts/build_manufacturing_revision.py work/baseline work/package
python scripts/validate_manufacturing_revision.py work/baseline work/package
python scripts/validate_front_clearance.py work/package/nine-u work/package/nine-u-180 work/package/nine-u-120 work/package/modular work/package/modular-120-80 work/package/modular-180
python scripts/validate_service_crossbar.py work/package/nine-u work/package/nine-u-180 work/package/nine-u-120 work/package/modular work/package/modular-120-80 work/package/modular-180
python scripts/audit_fastener_access.py work/package/nine-u work/package/nine-u-180 work/package/nine-u-120 work/package/modular work/package/modular-120-80 work/package/modular-180
python scripts/validate_inward_psu.py work/package/nine-u work/package/nine-u-180 work/package/nine-u-120
python drawing_source/compact_drawings.py work/package
python scripts/build_compact_viewers.py work/package path/to/local/threejs-libraries
python scripts/consolidate_part_steps.py work/package work/consolidated
python scripts/build_compact_viewers.py work/consolidated
python scripts/validate_fan_plates.py work/consolidated
python scripts/validate_compact_package.py work/consolidated path/to/node
```

The viewer builder expects `three.min.js` and `OrbitControls.js` in the library directory. It writes static pages with local assets and vector drawing sheets. The analytic Python sources control dimensions. The consolidation step writes one STEP file per distinct manufactured geometry into a shared `parts/` library, using local part coordinates. Printed STL files sit at Z0. Assembly STEP files retain every installed part and its position.

Each configuration has a `parts-catalog.csv` with quantities and shared STEP links. Its `parts-index.json` records each assembly occurrence and a 4 x 4 `assembly_from_part` matrix mapping local part coordinates to assembly coordinates. The parts index remains an occurrence list; it is not the number of distinct parts to manufacture. Consolidation allows translations and proper rotations, never reflections. The handed power-side and signal-side cable restraint angles remain separate parts.

The baseline generator supplies the established chassis interfaces. The manufacturing pass replaces PCB rails, rail bosses and front grilles, and substitutes catalog press nuts where their seating and edge requirements fit. Its reports list remaining formed-thread exceptions. Do not use baseline parts as substitutes for manufacturing-package parts.

## Publish

GitHub Pages deploys through `.github/workflows/pages.yml`. `bundle.json` identifies a release ZIP and its SHA-256. `scripts/prepare_pages.py` verifies the archive before publishing the viewers, compact PDFs and downloadable CAD parts. Package files live under a `chassis-engineering/` archive root.

# GPU chassis

Sheet-metal GPU chassis models, engineering drawings and interactive viewers for a 9U full enclosure and a removable GPU module above a SilverStone RM53-502. The GPU carrier has twenty-one rear bracket positions: ten dual-slot GPUs plus one single-width card, matching the usable sockets of a 12-slot Miwin switch-backplane reference. The full-chassis viewer offers six 120 mm fans, two 180 mm fans or three 120 mm fans. The 5U module viewer toggles between three 140 mm fans, three 120 mm fans with five 80 mm fans above them, and two 180 mm fans; each option has its own front carrier. The toggle updates intake hardware, engineering drawings and CAD links while preserving the camera position.

- [Open the interactive viewers](https://pedapudi.github.io/gpu-chassis/)
- [Download the complete engineering package and fabrication kit](https://github.com/pedapudi/gpu-chassis/releases/tag/rear-thumbscrews-2026-09-25)
- [Assembly, hardware and fabrication notes](ENGINEERING.md)
- [Analytic CAD sources](cad_source/)
- [Dimensioned drawing sources](drawing_source/)

The viewers show a 3D model beside selectable, zoomable engineering drawing sheets. Selecting a fabricated component opens its corresponding drawing. The release includes STEP assemblies and individual parts, OpenSCAD geometry, PDF drawings, coordinate schedules and validation reports. Drawing views directly label PCIe aperture width, height and pitch, tapped retention holes, toe-notch size, and repeated hole/slot families. Drawing schedules specify hole diameters and radii, slot lengths and end radii, local sheet thickness and feature positions. Dedicated interface sheets dimension the GPU and motherboard rear banks, toe locators, stepped PSU opening, cable-entry contours, lid returns and rail-height stack. Complete face contours accompany hole schedules and coordinate tables. Numbered leaders connect interface notes to the corresponding features. Formed sections and dimensioned face views locate folds and joined sheet components. The [drawing coverage report](DRAWING_COVERAGE.md) accounts for every fabricated part in all six configurations.

The release also carries a fabrication kit for sheet-metal suppliers: one formed STEP and one flat-pattern DXF with dashed bend lines per distinct blank, a parts list with quantities for every configuration, a hardware list, a tapped-thread schedule and a SendCutSend compatibility review. Build it with `python scripts/fabrication_kit.py BUILD OUT` after the drawings.

**Engineering review only.** OEM lid attachment dimensions and supplier backplane interfaces require physical verification. Nominal geometry checks do not establish fabrication readiness, thermal performance or structural qualification.

## Publish the viewer

GitHub Pages deploys through `.github/workflows/pages.yml` when the main branch is updated or the workflow is run manually. `bundle.json` selects the release asset and its SHA-256 digest. The deployment verifies that digest before extracting the viewer and linked engineering files. Raw projection intermediates and compiled mesh duplicates remain in the downloadable bundle and are omitted from Pages. Published vector sheets use lossless gzip compression; the viewer decompresses them in the browser.

To preview locally, download the release ZIP to this directory and run:

```sh
python3 scripts/prepare_pages.py chassis-engineering-annotated-drawings.zip --out _site
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. The static viewers require no external rendering service.

For CAD changes, follow [the rebuild instructions](cad_source/README.md) in a virtual environment, then [regenerate the dimensioned drawings](drawing_source/README.md) for all six configurations. Then assemble the package. The previous package supplies the viewer page layout, and an OpenSCAD executable compiles the part meshes:

```sh
python scripts/build_package.py scratch previous/chassis-engineering . package/chassis-engineering /path/to/openscad
```

The script writes the OpenSCAD parts and assembly, checks every compiled mesh, rebuilds the viewer data and drawing sheets, and rewrites the checksums. Zip the `chassis-engineering` folder, upload it as a release asset, and update `bundle.json` with its release tag, file name and SHA-256 digest in the same commit.

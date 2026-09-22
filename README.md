# GPU chassis

Sheet-metal GPU chassis models, engineering drawings and interactive viewers for a 9U full enclosure and a removable GPU module above a SilverStone RM53-502. The GPU carrier has twenty rear bracket positions for ten dual-slot GPUs, with a 12-slot Miwin switch-backplane reference. The full-chassis viewer offers six 120 mm fans, two 180 mm fans or three 120 mm fans. The module viewer toggles between three 140 mm and three 120 mm intake fans. The toggle updates intake hardware, engineering drawings and CAD links while preserving the camera position.

- [Open the interactive viewers](https://pedapudi.github.io/gpu-chassis/)
- [Download the complete engineering package](https://github.com/pedapudi/gpu-chassis/releases/tag/fan-options-dimensioned-2026-09-22)
- [Assembly, hardware and fabrication notes](ENGINEERING.md)
- [Analytic CAD sources](cad_source/)
- [Dimensioned drawing sources](drawing_source/)

The viewers show a 3D model beside selectable, zoomable engineering drawing sheets. Selecting a fabricated component opens its corresponding drawing. The release includes STEP assemblies and individual parts, OpenSCAD geometry, PDF drawings, coordinate schedules and validation reports. Drawing views directly label PCIe aperture width, height and pitch, retention-bore diameter, toe-notch size, and repeated hole/slot families. Drawing schedules specify hole diameters and radii, slot lengths and end radii, local sheet thickness and feature positions. Dedicated interface sheets dimension the GPU and motherboard rear banks, toe locators, stepped PSU opening, cable-entry contours, lid returns and rail-height stack. Formed sections and surface tables locate folds and joined sheet components. The [drawing coverage report](DRAWING_COVERAGE.md) accounts for every fabricated part in all five configurations.

**Engineering review only.** OEM lid attachment dimensions and supplier backplane interfaces require physical verification. Nominal geometry checks do not establish fabrication readiness, thermal performance or structural qualification.

## Publish the viewer

GitHub Pages deploys through `.github/workflows/pages.yml` when the main branch is updated or the workflow is run manually. `bundle.json` selects the release asset and its SHA-256 digest. The deployment verifies that digest before extracting the viewer and linked engineering files. Raw projection intermediates and compiled mesh duplicates remain in the downloadable bundle and are omitted from Pages. Published vector sheets use lossless gzip compression; the viewer decompresses them in the browser.

To preview locally, download the release ZIP to this directory and run:

```sh
python3 scripts/prepare_pages.py chassis-engineering-fan-options.zip --out _site
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. The static viewers require no external rendering service.

For CAD changes, follow [the rebuild instructions](cad_source/README.md) in a virtual environment, then [regenerate the dimensioned drawings](drawing_source/README.md). The interactive viewer also requires refreshed part meshes and drawing sheets. Publish a consistent validated bundle and update `bundle.json` together.

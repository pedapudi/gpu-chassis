# Rebuild analytic geometry

Create a virtual environment and install `requirements.txt` there. Run `python cad_source/rebuild.py --out scratch --variant both` from the package directory. The output directory must be a disposable build directory. The script exports analytic STEP geometry and serialized part snapshots; it does not regenerate drawing PDFs or the interactive viewer.

Lengths are millimetres. The source uses a construction X axis that is reflected into the exported right-handed assembly coordinates. See the package datum definition before editing hardware locations.

The native OpenSCAD assembly is in each design folder. Its per-part modules are faceted geometry. `modular/openscad/lid_adapter_parametric.scad` is an editable CSG template for the provisional OEM interface. OEM verification is false by default.

The full chassis supports `nine-u` (six 120 mm upper fans), `nine-u-180` (two 180 mm fans), and `nine-u-120` (three 120 mm fans). The 5U module supports `modular` (three 140 mm fans), `modular-120-80` (three 120 mm fans with five 80 mm fans above) and `modular-180` (two 180 mm fans); each has its own front carrier. `both` builds all six configurations. The single-row variants derive from the same full-chassis assembly and replace its front intake hardware. `full_intake.py` defines their analytic geometry in exported assembly coordinates.

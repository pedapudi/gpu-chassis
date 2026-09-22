# Rebuild analytic geometry

Create a virtual environment and install `requirements.txt` there. Run `python cad_source/rebuild.py --out scratch --variant both` from the package directory. The output directory must be a disposable build directory. The script exports analytic STEP geometry and serialized part snapshots; it does not regenerate drawing PDFs or the interactive viewer.

Lengths are millimetres. The source uses a construction X axis that is reflected into the exported right-handed assembly coordinates. See the package datum definition before editing hardware locations.

The native OpenSCAD assembly is in each design folder. Its per-part modules are faceted geometry. `modular/openscad/lid_adapter_parametric.scad` is an editable CSG template for the provisional OEM interface. OEM verification is false by default.

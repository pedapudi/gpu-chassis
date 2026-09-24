"""Build a self-contained static viewer site from a verified engineering bundle."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil
import zipfile
import gzip,re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('bundle', type=Path)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
config = json.loads((ROOT / 'bundle.json').read_text())
digest = hashlib.file_digest(args.bundle.open('rb'), 'sha256').hexdigest()
if digest != config['sha256']:
    raise SystemExit('Engineering bundle SHA-256 does not match bundle.json')
if args.out.exists():
    raise SystemExit('Output directory already exists; choose a fresh directory')
args.out.mkdir(parents=True)
with zipfile.ZipFile(args.bundle) as archive:
    for item in archive.infolist():
        path = PurePosixPath(item.filename)
        if '..' in path.parts or path.is_absolute() or path.parts[0] != 'chassis-engineering':
            raise SystemExit('Unexpected archive path: ' + item.filename)
        relative = PurePosixPath(*path.parts[1:])
        if not relative.parts or item.is_dir():
            continue
        # These duplicate intermediate representations are not linked by the viewer.
        if ('drawings', 'views') == relative.parts[1:3] or ('openscad', 'compiled') == relative.parts[1:3]:
            continue
        if relative.parts[0] in ('cad_source', 'drawing_source') or relative.name == 'SHA256SUMS.json':
            continue
        destination = args.out.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(item) as src, destination.open('wb') as dst:
            shutil.copyfileobj(src, dst)
from combine_module_viewer import combine_module_viewer
combine_module_viewer(args.out, ROOT)
from combine_full_viewer import combine_full_viewer
combine_full_viewer(args.out, ROOT)
shutil.copy2(ROOT / 'site/index.html', args.out / 'index.html')
(args.out / '.nojekyll').touch()
for variant in ('nine-u', 'nine-u-180', 'nine-u-120', 'modular', 'modular-120-80', 'modular-180'):
    folder = args.out / variant
    manifest = json.loads((folder / 'drawings/drawing_manifest.json').read_text())
    required = [folder / 'interactive_model.html', folder / 'drawings' / manifest['pdf'], folder / 'openscad/assembly.scad']
    required += [folder / 'drawings/sheets' / f'sheet-{row[0]:03d}.svg' for row in manifest['drawing_index']]
    required += [folder / ('double_deck_assembly.step' if variant.startswith('nine-u') else 'modular_assembly.step')]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit('Missing viewer files: ' + ', '.join(missing))
    print(f'{variant}: viewer, CAD links and {manifest["pages"]} drawing sheets verified')
# Compress vector sheets without changing their geometry or text outlines.
# The download bundle retains the original SVG files for offline use.
for path in args.out.glob('*/drawings/sheets/*.svg'):
    original=path.read_bytes();encoded=gzip.compress(original,compresslevel=9,mtime=0)
    assert gzip.decompress(encoded)==original
    path.with_suffix('.svg.gz').write_bytes(encoded);path.unlink()
for variant in ('nine-u','modular'):
    path=args.out/variant/'interactive_model.html';html=path.read_text()
    pattern=r"drawingImage\.src=(fanAssetBase\+'drawings/sheets/[^;]+);"
    html,count=re.subn(pattern,r'loadDrawingVector(\1);',html)
    assert count==1,(variant,count)
    marker='const sheetSelect='
    assert html.count(marker)==1
    html=html.replace(marker,(ROOT/'site/svg_loader.js').read_text()+'\n'+marker,1)
    path.write_text(html)
size = sum(p.stat().st_size for p in args.out.rglob('*') if p.is_file())
if size >= 1_000_000_000:
    raise SystemExit('Site exceeds the publication size budget')
print(f'Static site prepared: {size / 1_000_000:.1f} MB')

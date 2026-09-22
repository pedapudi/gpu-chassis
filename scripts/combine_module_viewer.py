"""Combine the released module fan meshes in a single interactive viewer."""
import json
from pathlib import Path
import re


def replace_once(text, source, target):
    if text.count(source) != 1:
        raise ValueError(f'Expected one viewer source marker: {source[:90]}')
    return text.replace(source, target, 1)


def value(html, name):
    marker = f'const {name}='
    start = html.index(marker) + len(marker)
    return json.JSONDecoder().raw_decode(html[start:])[0]


def section(html, title):
    return re.search(r'<section><h2>' + re.escape(title) + r'</h2>.*?</section>', html).group()


def fan_part(part):
    return part['group'] in ('fans', 'fan_pads', 'fan_adapters') or part['name'].startswith('Upper_fan_self_tapping_')


def combine_module_viewer(folder, root):
    sources = {size: (folder / variant / 'interactive_model.html').read_text()
               for size, variant in ((140, 'modular'), (120, 'modular-120'))}
    scenes = {size: value(html, 'dataset') for size, html in sources.items()}
    common = [{p['name']: p for p in scenes[size]['parts'] if not fan_part(p)} for size in (140, 120)]
    if common[0] != common[1]:
        raise ValueError('Module configurations differ outside their intake hardware')
    options = {}
    for size, html in sources.items():
        options[size] = {
            'parts': [p for p in scenes[size]['parts'] if fan_part(p)],
            'parameters': scenes[size]['parameters'],
            'details': value(html, 'partDetails'),
            'drawings': value(html, 'drawingIndex'),
            'interfaces': section(html, 'Mechanical interfaces'),
            'files': section(html, 'Design files'),
            'base': '' if size == 140 else '../modular-120/',
        }
    html = sources[140]
    html = replace_once(html, section(html, 'Intake configuration'), '')
    # The selector remains accessible when the responsive layout hides the sidebar.
    control = '''<fieldset id="fan-choice"><legend>Module intake fans</legend>
<label><input type="radio" name="fan-size" value="140" checked>3 × 140 mm</label>
<label><input type="radio" name="fan-size" value="120">3 × 120 mm</label>
<span id="fan-status" aria-live="polite">140 mm fans</span></fieldset>'''
    html = replace_once(html, '</h1>', '</h1>' + control)
    html = replace_once(html, '</style>', '''[hidden]{display:none!important}#fan-choice{display:flex;flex-wrap:wrap;align-items:center;gap:14px;border:0;margin:8px 0 0;padding:0;font-size:13px}#fan-choice legend{float:left;margin-right:14px;color:#526875}#fan-choice label{cursor:pointer;white-space:nowrap}#fan-choice input{accent-color:#146b82}#fan-status{font-size:12px;color:#526875}body{display:flex;flex-direction:column;height:100vh;overflow:hidden}header{height:auto;flex:none}main{flex:1;min-height:0;height:auto}#viewlabel{bottom:28px}@media(max-width:650px){body{height:auto;overflow:auto}main{flex:none;height:auto}}
</style>''')
    for title, identity in (('Mechanical interfaces', 'fan-interfaces'), ('Design files', 'fan-files')):
        original = section(html, title)
        html = replace_once(html, original, original.replace('<section>', f'<section id="{identity}">', 1))
    marker = '<label><input type="checkbox" data-group="fans" checked>Three 140 × 25 mm GPU intake fans</label>'
    html = replace_once(html, marker, marker + '<label hidden id="fan-adapter-label"><input type="checkbox" data-group="fan_adapters" checked>Three 120 mm fan blanking plates</label>')
    # Reuse the existing mesh constructor for both configurations.
    start = html.index('for(const p of dataset.parts){\n const geom=')
    end = html.index('\nconst cables=', start)
    loop = html[start:end]
    constructor = replace_once(loop, 'for(const p of dataset.parts){', 'function addViewerPart(p){')
    constructor = constructor[:-1] + ' return parent;\n}'
    html = replace_once(html, loop, constructor + '\nfor(const p of dataset.parts)addViewerPart(p);')
    html = replace_once(html, 'const holder=', 'let fanAssetBase="";\nconst holder=')
    for source, target in (("link.href='drawings/'", "link.href=fanAssetBase+'drawings/'"),
                           ("step.href='formed_parts/'", "step.href=fanAssetBase+'formed_parts/'"),
                           ("drawingImage.src='drawings/sheets/", "drawingImage.src=fanAssetBase+'drawings/sheets/"),
                           ("getElementById('drawing-pdf').href='drawings/'", "getElementById('drawing-pdf').href=fanAssetBase+'drawings/'")):
        html = replace_once(html, source, target)
    payload = json.dumps(options, separators=(',', ':')).replace('</', '<\\/')
    script = (root / 'site/fan_toggle.js').read_text()
    html = replace_once(html, '</html>', '<script>\nconst moduleFanOptions=' + payload + ';\n' + script + '\n</script></html>')
    # Source strings remain in memory until both output files have been written.
    (folder / 'modular/interactive_model.html').write_text(html)
    (folder / 'modular-120/interactive_model.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>GPU module viewer</title>
<meta http-equiv="refresh" content="0;url=../modular/interactive_model.html?fan=120">
<p><a href="../modular/interactive_model.html?fan=120">Open the module viewer with 120 mm fans</a></p></html>''')
    print(f'Module fan toggle: {len(common[0])} shared parts, {len(options[140]["parts"])} / {len(options[120]["parts"])} intake parts')

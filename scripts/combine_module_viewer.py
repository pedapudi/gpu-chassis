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


MODES = {'3x140': 'modular', '3x120_80': 'modular-120-80', '2x180': 'modular-180'}
LABELS = {'3x140': '3 × 140 mm', '3x120_80': '3 × 120 mm + 5 × 80 mm', '2x180': '2 × 180 mm'}


def fan_part(part):
    return (part['group'] in ('fans', 'fan_pads') or part['name'].startswith('Upper_fan_self_tapping_')
            or part['name'].startswith('Upper_module_front_carrier_'))


def combine_module_viewer(folder, root):
    sources = {mode: (folder / variant / 'interactive_model.html').read_text() for mode, variant in MODES.items()}
    scenes = {mode: value(html, 'dataset') for mode, html in sources.items()}
    common = [{p['name']: p for p in scenes[mode]['parts'] if not fan_part(p)} for mode in MODES]
    if any(c != common[0] for c in common[1:]):
        raise ValueError('Module configurations differ outside their intake hardware')
    options = {}
    for mode, html in sources.items():
        options[mode] = {
            'label': LABELS[mode],
            'parts': [p for p in scenes[mode]['parts'] if fan_part(p)],
            'parameters': scenes[mode]['parameters'],
            'details': value(html, 'partDetails'),
            'drawings': value(html, 'drawingIndex'),
            'interfaces': section(html, 'Mechanical interfaces'),
            'files': section(html, 'Design files'),
            'base': '' if mode == '3x140' else '../' + MODES[mode] + '/',
        }
    html = sources['3x140']
    html = replace_once(html, section(html, 'Intake configuration'), '')
    # The selector remains accessible when the responsive layout hides the sidebar.
    control = '<fieldset id="fan-choice"><legend>Module intake</legend>' + ''.join(
        f'<label><input type="radio" name="intake-mode" value="{mode}"{" checked" if mode == "3x140" else ""}>{label}</label>'
        for mode, label in LABELS.items()) + '<span id="fan-status" aria-live="polite"></span></fieldset>'
    html = replace_once(html, '</h1>', '</h1>' + control)
    html = replace_once(html, '</style>', '''[hidden]{display:none!important}#fan-choice{display:flex;flex-wrap:wrap;align-items:center;gap:14px;border:0;margin:8px 0 0;padding:0;font-size:13px}#fan-choice legend{float:left;margin-right:14px;color:#526875}#fan-choice label{cursor:pointer;white-space:nowrap}#fan-choice input{accent-color:#146b82}#fan-status{font-size:12px;color:#526875}body{display:flex;flex-direction:column;height:100vh;overflow:hidden}header{height:auto;flex:none}main{flex:1;min-height:0;height:auto}#viewlabel{bottom:28px}@media(max-width:650px){body{height:auto;overflow:auto}main{flex:none;height:auto}}
</style>''')
    for title, identity in (('Mechanical interfaces', 'fan-interfaces'), ('Design files', 'fan-files')):
        original = section(html, title)
        html = replace_once(html, original, original.replace('<section>', f'<section id="{identity}">', 1))
    # Reuse the existing mesh constructor for every configuration.
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
    # Source strings remain in memory until every output file has been written.
    (folder / 'modular/interactive_model.html').write_text(html)
    for mode, variant in MODES.items():
        if mode == '3x140':
            continue
        (folder / variant / 'interactive_model.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>GPU module viewer</title>
<meta http-equiv="refresh" content="0;url=../modular/interactive_model.html?intake={mode}">
<p><a href="../modular/interactive_model.html?intake={mode}">Open the module viewer with {LABELS[mode]} fans</a></p></html>''')
    print(f'Module intake toggle: {len(common[0])} shared parts; intake parts ' + ' / '.join(str(len(o['parts'])) for o in options.values()))

"""Combine three upper-intake configurations in the full-chassis viewer."""
import json
from combine_module_viewer import replace_once,value,section


def intake_part(p):
    return p['group'] in ('fans','intake_fasteners','intake_grilles') or p['name']=='Front_fan_carrier_with_side_returns' or p['name'].startswith('Full_chassis_upper_intake_insert_')


def combine_full_viewer(folder,root):
    variants={'6x120':'nine-u','2x180':'nine-u-180','3x120':'nine-u-120'}
    sources={k:(folder/v/'interactive_model.html').read_text() for k,v in variants.items()}
    scenes={k:value(h,'dataset') for k,h in sources.items()};options={}
    common={p['name']:p for p in scenes['6x120']['parts'] if not intake_part(p)}
    for mode,h in sources.items():
        other={p['name']:p for p in scenes[mode]['parts'] if not intake_part(p)}
        if set(other)!=set(common):raise ValueError('Common full-chassis parts differ')
        # The derivative CAD validation proves unchanged analytic solids.
        if mode!='6x120':
            report=json.loads((folder/variants[mode]/'full_intake_checks.json').read_text())
            if not report['passed']:raise ValueError('Unvalidated intake')
        options[mode]={'parts':[p for p in scenes[mode]['parts'] if intake_part(p)],'parameters':scenes[mode]['parameters'],'details':value(h,'partDetails'),'drawings':value(h,'drawingIndex'),'interfaces':section(h,'Mechanical interfaces'),'files':section(h,'Design files'),'base':'' if mode=='6x120' else '../'+variants[mode]+'/'}
    h=sources['6x120']
    control='''<fieldset id="intake-choice"><legend>Upper intake</legend>
<label><input type="radio" name="intake-mode" value="6x120" checked>6 × 120 mm</label>
<label><input type="radio" name="intake-mode" value="2x180">2 × 180 mm</label>
<label><input type="radio" name="intake-mode" value="3x120">3 × 120 mm</label>
<span id="intake-status" aria-live="polite"></span></fieldset>'''
    h=replace_once(h,'</h1>','</h1>'+control)
    h=replace_once(h,'</style>','''#intake-choice{display:flex;flex-wrap:wrap;align-items:center;gap:14px;border:0;margin:8px 0 0;padding:0;font-size:13px}#intake-choice legend{float:left;margin-right:14px;color:#526875}#intake-choice label{cursor:pointer;white-space:nowrap}#intake-choice input{accent-color:#146b82}#intake-status{font-size:12px;color:#526875}body{display:flex;flex-direction:column;height:100vh;overflow:hidden}header{height:auto;flex:none}main{flex:1;min-height:0;height:auto}@media(max-width:650px){body{height:auto;overflow:auto}main{flex:none;height:auto}}</style>''')
    for title,identity in (('Mechanical interfaces','intake-interfaces'),('Design files','intake-files')):
        old=section(h,title);h=replace_once(h,old,replace_once(old,'<section>',f'<section id="{identity}">'))
    start=h.index('for(const p of dataset.parts){\n const geom=');end=h.index('\nconst cables=',start);loop=h[start:end]
    constructor=replace_once(loop,'for(const p of dataset.parts){','function addViewerPart(p){');constructor=constructor[:-1]+' return parent;\n}'
    h=replace_once(h,loop,constructor+'\nfor(const p of dataset.parts)addViewerPart(p);')
    h=replace_once(h,'const holder=','let fanAssetBase="";\nconst holder=')
    for a,b in (("link.href='drawings/'","link.href=fanAssetBase+'drawings/'"),("step.href='formed_parts/'","step.href=fanAssetBase+'formed_parts/'"),("drawingImage.src='drawings/sheets/","drawingImage.src=fanAssetBase+'drawings/sheets/"),("getElementById('drawing-pdf').href='drawings/'","getElementById('drawing-pdf').href=fanAssetBase+'drawings/'")):
        h=replace_once(h,a,b)
    payload=json.dumps(options,separators=(',',':')).replace('</','<\\/')
    h=replace_once(h,'</html>','<script>const fullIntakeOptions='+payload+';\n'+(root/'site/full_intake_toggle.js').read_text()+'\n</script></html>')
    (folder/'nine-u/interactive_model.html').write_text(h)
    for mode in ('2x180','3x120'):
        (folder/variants[mode]/'interactive_model.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Full chassis viewer</title><meta http-equiv="refresh" content="0;url=../nine-u/interactive_model.html?intake={mode}"><p><a href="../nine-u/interactive_model.html?intake={mode}">Open full chassis with {mode} intake</a></p></html>')
    print('Full-chassis intake options: '+', '.join(options))

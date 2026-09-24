"""Neutral STEP export headers."""
from pathlib import Path
import re
def neutral_headers(out):
 for p in Path(out).rglob('*.step'):
  s=p.read_text();m=re.search(r"FILE_NAME\('[^']*','([^']*)'",s);assert m
  start=s.index('FILE_DESCRIPTION(');end=s.index('FILE_SCHEMA(');assert start<end
  s=s[:start]+"FILE_DESCRIPTION(('Mechanical assembly'),'2;1');\n"+f"FILE_NAME('{p.name}','{m.group(1)}',(''),(''),'','','');\n"+s[end:]
  p.write_text(s)


def cable_route(part):
    """Routed cable occupancy tubes; assembly STEP files omit them, cable_routes.json keeps them."""
    return part['group'] in ('power','mcio','external_route') and ('_route' in part['name'] or '_stub' in part['name'])

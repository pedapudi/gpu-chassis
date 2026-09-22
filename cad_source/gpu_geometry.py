"""Neutral STEP export headers."""
from pathlib import Path
import re
def neutral_headers(out):
 for p in Path(out).rglob('*.step'):
  s=p.read_text();m=re.search(r"FILE_NAME\('[^']*','([^']*)'",s);assert m
  s,n=re.subn(r'FILE_DESCRIPTION\(.*?;',"FILE_DESCRIPTION(('Mechanical assembly'),'2;1');",s,count=1,flags=re.S);assert n==1
  s,n=re.subn(r'FILE_NAME\(.*?;',f"FILE_NAME('{p.name}','{m.group(1)}',(''),(''),'','','');",s,count=1,flags=re.S);assert n==1
  p.write_text(s)

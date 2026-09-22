function isFullIntake(p){return ['fans','intake_fasteners','intake_grilles'].includes(p.group)||p.name==='Front_fan_carrier_with_side_returns'||p.name.startsWith('Full_chassis_upper_intake_insert_');}
let activeIntake='6x120';
function setFullIntake(mode){
 const option=fullIntakeOptions[mode];if(!option)return;
 const previousSheet=drawingIndex.find(row=>row[0]===drawingPage),previousSelection=selected?.name;
 if(mode!==activeIntake){
  const visible={};for(const group of ['shell','fans','intake_fasteners','intake_grilles'])visible[group]=(groups[group]||[]).some(p=>p.visible);
  for(let i=all.length-1;i>=0;i--){const part=all[i];if(!isFullIntake(part.userData))continue;scene.remove(part);all.splice(i,1);pickables.splice(pickables.indexOf(part.children[0]),1);const members=groups[part.userData.group];members.splice(members.indexOf(part),1);for(const child of part.children){child.geometry.dispose();child.material.dispose();}}
  dataset.parts=dataset.parts.filter(p=>!isFullIntake(p)).concat(option.parts);dataset.parameters=option.parameters;
  for(const data of option.parts){const part=addViewerPart(data);part.visible=visible[data.group];part.children[1].visible=document.getElementById('engineering').checked;part.children[1].material.opacity=.45;if(document.getElementById('section-cut').checked)for(const child of part.children)child.material.clippingPlanes=[cutPlane];}
  ghost(document.getElementById('ghost').checked);
 }
 activeIntake=mode;fanAssetBase=option.base;
 for(const key of Object.keys(partDetails))delete partDetails[key];Object.assign(partDetails,option.details);
 drawingIndex.splice(0,drawingIndex.length,...option.drawings);sheetSelect.replaceChildren();
 for(const [page,title]of drawingIndex){const item=document.createElement('option');item.value=page;item.textContent=page+' · '+title;sheetSelect.appendChild(item);}
 document.getElementById('intake-interfaces').innerHTML=option.interfaces.slice(9,-10);document.getElementById('intake-files').innerHTML=option.files.slice(9,-10);
 for(const link of document.querySelectorAll('#intake-files a[href]')){const href=link.getAttribute('href');if(!href.startsWith('../'))link.setAttribute('href',fanAssetBase+href);}
 const label=mode==='2x180'?'Two 180 × 32 mm GPU intake fans':mode==='3x120'?'Three 120 × 38 mm GPU intake fans':'Six 120 × 38 mm GPU intake fans';
 document.querySelector('[data-group="fans"]').parentElement.lastChild.textContent=label;
 document.getElementById('intake-status').textContent=mode==='6x120'?'Two rows · 9U':'One row · front-removable insert · 9U';
 for(const input of document.querySelectorAll('[name="intake-mode"]'))input.checked=input.value===mode;
 const url=new URL(location.href);url.searchParams.set('intake',mode);history.replaceState(null,'',url);sync();filterParts();
 const match=previousSheet&&drawingIndex.find(row=>previousSheet[2]==='Assembly'?row[1]===previousSheet[1]:row[2]===previousSheet[2]);showDrawing(match?match[0]:Math.min(drawingPage,drawingIndex.length));
 if(previousSelection&&partDetails[previousSelection])describe(all.find(p=>p.userData.name===previousSelection).userData);
 else if(previousSelection){selected=null;focusedPart=false;document.getElementById('picked').textContent='Click a component for dimensions and its engineering drawing.';}
}
for(const input of document.querySelectorAll('[name="intake-mode"]'))input.addEventListener('change',()=>setFullIntake(input.value));
setFullIntake(new URLSearchParams(location.search).get('intake')||'6x120');

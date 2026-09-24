function isIntakePart(p) {
  return ['fans', 'fan_pads'].includes(p.group) || p.name.startsWith('Upper_fan_self_tapping_') || p.name.startsWith('Upper_module_front_carrier_');
}
let activeIntake = '3x140';
function setIntake(mode) {
  const option = moduleFanOptions[mode];
  if (!option) return;
  const previousSheet = drawingIndex.find(row => row[0] === drawingPage);
  const previousSelection = selected?.name;
  if (mode !== activeIntake) {
    const visible = {};
    for (const group of ['fans', 'fan_pads', 'intake_fasteners', 'shell']) {
      visible[group] = all.some(p => isIntakePart(p.userData) && p.userData.group === group && p.visible);
    }
    for (let i = all.length - 1; i >= 0; i--) {
      const part = all[i];
      if (!isIntakePart(part.userData)) continue;
      scene.remove(part);
      all.splice(i, 1);
      pickables.splice(pickables.indexOf(part.children[0]), 1);
      const members = groups[part.userData.group];
      members.splice(members.indexOf(part), 1);
      for (const child of part.children) { child.geometry.dispose(); child.material.dispose(); }
    }
    dataset.parts = dataset.parts.filter(p => !isIntakePart(p)).concat(option.parts);
    dataset.parameters = option.parameters;
    for (const data of option.parts) {
      const part = addViewerPart(data);
      part.visible = visible[data.group] ?? true;
      if (data.moving) part.position.z = 360 * Number(document.getElementById('explode').value);
      part.children[1].visible = document.getElementById('engineering').checked;
      part.children[1].material.opacity = .45;
      if (document.getElementById('section-cut').checked) {
        for (const child of part.children) child.material.clippingPlanes = [cutPlane];
      }
    }
  }
  activeIntake = mode;
  fanAssetBase = option.base;
  for (const key of Object.keys(partDetails)) delete partDetails[key];
  Object.assign(partDetails, option.details);
  drawingIndex.splice(0, drawingIndex.length, ...option.drawings);
  sheetSelect.replaceChildren();
  for (const [page, title] of drawingIndex) {
    const item = document.createElement('option');
    item.value = page; item.textContent = page + ' · ' + title; sheetSelect.appendChild(item);
  }
  document.getElementById('fan-interfaces').innerHTML = option.interfaces.slice(9, -10);
  document.getElementById('fan-files').innerHTML = option.files.slice(9, -10);
  for (const link of document.querySelectorAll('#fan-files a[href]')) {
    const href = link.getAttribute('href');
    if (!href.startsWith('../')) link.setAttribute('href', fanAssetBase + href);
  }
  document.querySelector('[data-group="fans"]').parentElement.lastChild.textContent = option.label + ' GPU intake fans';
  const pads = document.querySelector('[data-group="fan_pads"]');
  if (pads) pads.parentElement.hidden = !option.parts.some(p => p.group === 'fan_pads');
  document.getElementById('fan-status').textContent = 'Own front carrier; common grille';
  document.querySelector('h1').textContent = 'RM53-502 GPU module';
  document.title = `RM53-502 GPU module · ${option.label}`;
  for (const input of document.querySelectorAll('[name="intake-mode"]')) input.checked = input.value === mode;
  const url = new URL(location.href); url.searchParams.set('intake', mode); history.replaceState(null, '', url);
  sync(); filterParts();
  const match = previousSheet && drawingIndex.find(row => previousSheet[2] === 'Assembly' ? row[1] === previousSheet[1] : row[2] === previousSheet[2]);
  showDrawing(match ? match[0] : Math.min(drawingPage, drawingIndex.length));
  if (previousSelection && partDetails[previousSelection]) {
    describe(all.find(p => p.userData.name === previousSelection).userData);
  } else if (previousSelection) {
    selected = null; focusedPart = false;
    document.getElementById('picked').textContent = 'Click a component for dimensions and its engineering drawing.';
  }
}
for (const input of document.querySelectorAll('[name="intake-mode"]')) {
  input.addEventListener('change', () => setIntake(input.value));
}
setIntake(new URLSearchParams(location.search).get('intake') in moduleFanOptions ? new URLSearchParams(location.search).get('intake') : '3x140');

let drawingLoadToken=0,drawingBlobURL=null;
async function loadDrawingVector(url){
 const token=++drawingLoadToken;
 try{
  const response=await fetch(url+'.gz');if(!response.ok)throw new Error('Drawing asset unavailable');
  let bytes=await response.arrayBuffer();const signature=new Uint8Array(bytes,0,Math.min(2,bytes.byteLength));
  if(signature[0]===31&&signature[1]===139){const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));bytes=await new Response(stream).arrayBuffer();}
  const blob=new Blob([bytes],{type:'image/svg+xml'});
  if(token!==drawingLoadToken)return;
  if(drawingBlobURL)URL.revokeObjectURL(drawingBlobURL);
  drawingBlobURL=URL.createObjectURL(blob);drawingImage.src=drawingBlobURL;
 }catch(error){if(token===drawingLoadToken)document.getElementById('drawing-caption').textContent='Drawing image unavailable. Open PDF contains the complete vector sheet.';}
}

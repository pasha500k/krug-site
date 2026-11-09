'use strict';
const scope=self.registration.scope;
const appPrefix='krug-app:'+scope+':';
const APP=appPrefix+'v15',BOOKS='krug-books:'+scope+':v1';
const shell=['index.html','tasks.html','reader.html','about.html','support.html','archives.html','schools.html','permissions.html','learn-numbers.html','contents.html',
  'assets/site.css','assets/site.js','assets/archive.js','assets/locale.js','assets/offline.js','assets/pdf-local.js','assets/text-local.js','assets/geometry.svg','assets/mark.svg',
  'catalog/library.json','catalog/archives.json','catalog/book-documents.json','catalog/support.json','catalog/permissions.json'];
const urlOf=path=>new URL(path,scope).href;
const isPDF=path=>/^(?:books\/[a-z0-9-]+|__krug\/(?:pdf|translated)\/[0-9a-f]{64})\.pdf$/.test(path);
self.addEventListener('install',e=>e.waitUntil(caches.open(APP).then(c=>c.addAll(shell.map(path=>new Request(urlOf(path),{cache:'reload'})))).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil((async()=>{
  const app=await caches.open(APP);
  const tasks=urlOf('catalog/tasks.json');
  for(const key of await caches.keys())if(key.startsWith(appPrefix)&&key!==APP){
    const old=await caches.open(key);
    const saved=await old.match(tasks);
    if(saved&&!(await app.match(tasks)))await app.put(tasks,saved);
    await caches.delete(key);
  }
  const books=await caches.open(BOOKS);
  await Promise.all((await books.keys()).filter(request=>request.url.startsWith(urlOf('__krug/'))).map(async request=>{
    try{
      const response=await fetch(request.url,{method:'HEAD',cache:'no-store'});
      if(response.status===410)await books.delete(request);
    }catch{/* Keep the offline copy if the server cannot be reached. */}
  }));
  await self.clients.claim();
})()));
const pending=new Map();
async function savedBook(url){
  const cache=await caches.open(BOOKS);
  const saved=await cache.match(url);
  if(saved)return [saved,true];
  if(!pending.has(url))pending.set(url,(async()=>{
    try{
      const response=await fetch(url);
      if(response.ok&&response.status===200&&response.headers.get('Content-Type')?.includes('pdf')){
        try{await cache.put(url,response.clone());}catch{/* Reading still works if offline storage is full. */}
      }
      return response;
    }finally{pending.delete(url);}
  })());
  return [(await pending.get(url)).clone(),false];
}
async function byteRange(request,response){
  const value=request.headers.get('Range');
  if(!value)return response;
  const match=/^bytes=(\d*)-(\d*)$/.exec(value);
  const bytes=await response.arrayBuffer();
  if(!match||(!match[1]&&!match[2]))return new Response(null,{status:416,headers:{'Content-Range':'bytes */'+bytes.byteLength}});
  const start=match[1]?Number(match[1]):Math.max(0,bytes.byteLength-Number(match[2]));
  const end=match[1]&&match[2]?Math.min(bytes.byteLength-1,Number(match[2])):bytes.byteLength-1;
  if(start>end||start>=bytes.byteLength)return new Response(null,{status:416,headers:{'Content-Range':'bytes */'+bytes.byteLength}});
  return new Response(bytes.slice(start,end+1),{status:206,headers:{'Content-Type':'application/pdf','Accept-Ranges':'bytes',
    'Content-Range':'bytes '+start+'-'+end+'/'+bytes.byteLength,'Content-Length':String(end-start+1)}});
}
async function serveBook(request,url){
  const cache=await caches.open(BOOKS);
  const existing=await cache.match(url);
  if(existing)return byteRange(request,existing);
  if(request.headers.has('Range'))return fetch(request);
  return (await savedBook(url))[0];
}
async function appResponse(request,relative){
  const cache=await caches.open(APP);
  const target=urlOf(relative||'index.html');
  try{
    const response=await fetch(request);
    if(response.ok){try{await cache.put(target,response.clone());}catch{}}
    return response;
  }catch{
    return await cache.match(target)||new Response('Offline. Save the catalogue while connected.',{status:503});
  }
}
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET'||!e.request.url.startsWith(scope))return;
  const parsed=new URL(e.request.url);
  const relative=parsed.href.slice(scope.length).split(/[?#]/,1)[0];
  if(isPDF(relative))e.respondWith(serveBook(e.request,urlOf(relative)));
  else if(relative===''||shell.includes(relative)||relative==='catalog/tasks.json')e.respondWith(appResponse(e.request,relative));
});
self.addEventListener('message',e=>{
  const {type,path}=e.data||{};
  if(!e.ports[0])return;
  const send=value=>e.ports[0].postMessage(value);
  e.waitUntil((async()=>{
    try{
      if(type==='save-catalogue'){
        const cache=await caches.open(APP);
        const url=urlOf('catalog/tasks.json');
        const existing=await cache.match(url);
        if(!existing)await cache.add(url);
        send({ok:true,existing:!!existing});
      }else if(type==='save-book'&&typeof path==='string'&&isPDF(path)){
        const url=urlOf(path);
        const [,existing]=await savedBook(url);
        send({ok:!!(await (await caches.open(BOOKS)).match(url)),existing});
      }else send({ok:false});
    }catch{send({ok:false});}
  })());
});

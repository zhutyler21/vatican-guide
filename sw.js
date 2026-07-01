const CACHE='vatican-guide-v5';
const CORE=[
  './','./index.html','./data.js','./manifest.json','./icon.png'
];
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>Promise.all(
    CORE.map(u=>c.add(u).catch(()=>null))
  )));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE&&k!=='vatican-guide-cn-core-v1').map(k=>caches.delete(k))
  )).then(()=>self.clients.claim()));
});
function shouldRuntimeCache(req){
  const u=new URL(req.url);
  return req.method==='GET'&&(u.pathname.includes('/images/')||u.pathname.includes('/audio/')||u.pathname.endsWith('/data.js'));
}
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(
    caches.match(e.request).then(cached=>{
      if(cached)return cached;
      return fetch(e.request).then(resp=>{
        if(resp&&resp.ok&&shouldRuntimeCache(e.request)){
          const cp=resp.clone();
          caches.open(CACHE).then(c=>c.put(e.request,cp)).catch(()=>{});
        }
        return resp;
      }).catch(()=>cached);
    })
  );
});

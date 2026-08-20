// v9：完整展示作品图片，并清理仍缓存旧页面样式的手动缓存。
const CACHE='italy-guide-v9';
const CORE=['./','./index.html','./data.js','./manifest.json','./icon.png','./images/placeholder.svg'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>Promise.all(CORE.map(u=>c.add(u).catch(()=>null)))))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE&&k!=='italy-guide-manual-v3').map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);const cacheable=u.pathname.includes('/images/')||u.pathname.endsWith('/data.js');e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok&&cacheable)caches.open(CACHE).then(c=>c.put(e.request,r.clone()));return r}).catch(()=>hit)))});

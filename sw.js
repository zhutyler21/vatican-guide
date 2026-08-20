// v8：隐私清理后只缓存页面、数据与图片，并删除旧版手动缓存中的预录音频。
const CACHE='italy-guide-v8';
const CORE=['./','./index.html','./data.js','./manifest.json','./icon.png','./images/placeholder.svg'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>Promise.all(CORE.map(u=>c.add(u).catch(()=>null)))))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE&&k!=='italy-guide-manual-v2').map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);const cacheable=u.pathname.includes('/images/')||u.pathname.endsWith('/data.js');e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok&&cacheable)caches.open(CACHE).then(c=>c.put(e.request,r.clone()));return r}).catch(()=>hit)))});

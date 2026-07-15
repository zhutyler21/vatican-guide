// v7：斗兽场节点图片改为版本化文件名，安装时清除旧的 v6 图片/数据缓存。
const CACHE='italy-guide-v7';
const CORE=['./','./index.html','./data.js','./manifest.json','./icon.png','./images/placeholder.svg'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>Promise.all(CORE.map(u=>c.add(u).catch(()=>null)))))});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE&&!k.startsWith('italy-guide-manual-')).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);const cacheable=u.pathname.includes('/images/')||u.pathname.includes('/audio/')||u.pathname.endsWith('/data.js');e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok&&cacheable)caches.open(CACHE).then(c=>c.put(e.request,r.clone()));return r}).catch(()=>hit)))});

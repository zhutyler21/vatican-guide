const CACHE='vatican-guide-v1';
const ASSETS=[
  './','./index.html','./data.js','./manifest.json','./icon.png',
  'images/laocoon.jpg','images/apollo_belvedere.jpg','images/belvedere_torso.jpg',
  'images/animal_hall.jpg','images/sala_rotonda.jpg','images/gallery_candelabra.jpg',
  'images/gallery_tapestries.jpg','images/gallery_maps.jpg','images/raphael_school_athens.jpg',
  'images/raphael_disputa.jpg','images/raphael_heliodorus.jpg','images/raphael_fire_borgo.jpg',
  'images/borgia_apartment.jpg','images/sistine_ceiling.jpg','images/creation_adam.jpg',
  'images/last_judgment.jpg','images/sistine_keys.jpg','images/transfiguration.jpg',
  'images/leonardo_jerome.jpg','images/caravaggio_deposition.jpg','images/pieta.jpg',
  'images/st_peters_baldachin.jpg','images/madonna_foligno.jpg','images/bramante_staircase.jpg'
];
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>Promise.all(
    ASSETS.map(u=>c.add(u).catch(()=>null))
  )));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(
    ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))
  )).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(
    caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{
      const cp=resp.clone();
      caches.open(CACHE).then(c=>c.put(e.request,cp)).catch(()=>{});
      return resp;
    }).catch(()=>r))
  );
});

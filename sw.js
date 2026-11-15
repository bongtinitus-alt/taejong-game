/* 태종 이방원 service worker — 캐시 이름은 버전과 함께 바뀌어 새 판이 오면 갱신됩니다. */
const SWV="v0.9.6";
const CACHE="tj-"+SWV;
const PRE=[
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png",
  "./img/act0.svg",
  "./img/act1.svg",
  "./img/act2.svg",
  "./img/end.svg",
  "./img/rain.svg"
];
self.addEventListener("install",e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(PRE)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",e=>{
  e.waitUntil((async()=>{
    const ks=await caches.keys();
    await Promise.all(ks.filter(k=>k!==CACHE&&k.startsWith("tj-")).map(k=>caches.delete(k)));
    await self.clients.claim();
  })());
});
self.addEventListener("message",e=>{if(e.data==="skipWaiting")self.skipWaiting()});
self.addEventListener("fetch",e=>{
  const req=e.request;
  if(req.method!=="GET")return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin)return;
  if(url.pathname.endsWith("stats-config.json"))return; // always network
  const nav=req.mode==="navigate"||(req.headers.get("accept")||"").includes("text/html");
  if(nav){
    e.respondWith((async()=>{
      try{
        const fresh=await fetch(req);
        const c=await caches.open(CACHE);
        c.put("./index.html",fresh.clone());
        return fresh;
      }catch(err){
        return (await caches.match("./index.html"))||(await caches.match(req))||Response.error();
      }
    })());
    return;
  }
  e.respondWith((async()=>{
    const hit=await caches.match(req);
    if(hit)return hit;
    try{
      const fresh=await fetch(req);
      if(fresh && fresh.ok){const c=await caches.open(CACHE);c.put(req,fresh.clone())}
      return fresh;
    }catch(err){
      return hit||Response.error();
    }
  })());
});

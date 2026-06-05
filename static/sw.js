const CACHE = 'cybercafe-erp-v1';
const ASSETS = ['/', '/static/css/app.css', '/static/js/app.js', '/static/icons/icon-192.png', '/static/icons/icon-512.png', '/manifest.webmanifest'];
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS).catch(()=>{}))); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Network-first for HTML/dynamic; cache-first for static assets
  if (url.pathname.startsWith('/static/') || url.pathname === '/manifest.webmanifest') {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => { const cl=res.clone(); caches.open(CACHE).then(c=>c.put(req,cl)); return res; })));
  } else {
    e.respondWith(fetch(req).catch(() => caches.match(req).then(r => r || caches.match('/'))));
  }
});

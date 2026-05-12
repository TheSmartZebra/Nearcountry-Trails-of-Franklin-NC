const CACHE_NAME = 'nearcountry-trails-v2';
const ASSETS_TO_CACHE = [
  '/Nearcountry-Trails-of-Franklin-NC/',
  '/Nearcountry-Trails-of-Franklin-NC/index.html',
  '/Nearcountry-Trails-of-Franklin-NC/background.jpg',
  '/Nearcountry-Trails-of-Franklin-NC/manifest.json',
  'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,400,0,0'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys
        .filter(key => key.startsWith('nearcountry-trails-') && key !== CACHE_NAME)
        .map(key => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);

    try {
      const networkResponse = await fetch(event.request);
      if (event.request.url.startsWith(self.location.origin)) {
        cache.put(event.request, networkResponse.clone());
      }
      return networkResponse;
    } catch (error) {
      const cachedResponse = await cache.match(event.request);
      if (cachedResponse) return cachedResponse;

      if (event.request.mode === 'navigate') {
        const fallback = await cache.match('/Nearcountry-Trails-of-Franklin-NC/index.html');
        if (fallback) return fallback;
      }

      throw error;
    }
  })());
});

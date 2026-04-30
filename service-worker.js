const CACHE_NAME = 'nearcountry-trails-v1';
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
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
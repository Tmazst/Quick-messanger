const CACHE_NAME = 'bizchat-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/css/bs_stylesheet.css',
  '/static/icons/logo-avator.png',
  // Add more assets as needed
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
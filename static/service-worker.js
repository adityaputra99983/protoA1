const CACHE_NAME = 'ted-v4';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map(k => caches.delete(k)));
    })
  );
  self.clients.claim();
});

// Disable all interception to fix Map loading issues
self.addEventListener('fetch', (event) => {
  // Do nothing, let browser handle everything
});
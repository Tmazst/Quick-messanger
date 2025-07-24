const CACHE_NAME = 'bizchat-cache-v2';
const urlsToCache = [
  '/static/css/styles.css',
  // '/static/css/bs_stylesheet.css',
  // Add more assets as needed
];

// Install: cache new files
// self.addEventListener('install', event => {
//   self.skipWaiting();
//   event.waitUntil(
//     caches.open(CACHE_NAME)
//       .then(cache => cache.addAll(urlsToCache))
//   );
// });

// Activate: delete old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});


// ✅ Safe Fetch Handler
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then(response => {
        return response;
      })
      .catch(async error => {
        console.log('Fetch request for:', event.request.url);
        console.warn('Fetch failed; returning fallback (if any):', error);

         // Tell the client (main thread) to unregister the SW
        // const allClients = await self.clients.matchAll({ includeUncontrolled: true });
        // for (const client of allClients) {
        //   client.postMessage({ action: 'UNREGISTER_SERVICE_WORKER' });
        // }

        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(event.request);
        if (cached) return cached;

        // Optional: Return a simple fallback if no match found
        if (event.request.mode === 'navigate') {
          return new Response('<h1>You are offline</h1>', {
            headers: { 'Content-Type': 'text/html' }
          });
        }

        return new Response('', { status: 200 }); // Always return a valid response
      })
  );
});


self.addEventListener('push', function(event) {
  // console.log("Push Event Called2!");
    let data = {};
    if (event.data) {
      data = event.data.json();
    }

    const options = {
      body: data.body || 'You have a new message!',
      icon: '/static/icons/512x512.png',
      badge: '/static/icons/192x192.png',
      data: {
        url: data.url || '/', // Where to go when clicked
        messageId: data.body,
        username: data.username
      },
      actions: [
      {action: 'reply', title: 'Open'}
    ]
    };

    event.waitUntil(
      self.registration.showNotification(data.title || 'New Message', options)
    );

    // console.log(">>>>");
    self.clients.matchAll({type: 'window'}).then(function(clients) {
      // console.log("Custom PUSH_NOTIFICATION Data: ", data);
      // console.log("CLIENTS: ", clients);
      clients.forEach(function(client) {
        // console.log("Custom PUSH_NOTIFICATION Data: ", data);
        client.postMessage({type: 'PUSH_NOTIFICATION', data: data});
      });
  });
});


// let clients;
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  // console.log("Username @Push: ",event.notification.data.url);
  // Extract username or other params from notification data
  const username = event.notification.data && event.notification.data.username;
  let getMessagesUrl = event.notification.data.url;
  // = username ? `/get_messages?key=${encodeURIComponent(username)}` : '/';

  // Mini window URL for reply unit
  const openPWA = event.notification.data.url;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      if (clientList.length > 0) {
        // Do not open mini window if it is an app update 
        if(openPWA === "/"){
          return;
        }
        // App is open: focus and send message to redirect
        for (var i = 0; i < clientList.length; i++) {
          var client = clientList[i];
          if ('focus' in client) {
            client.focus();
            // Send a message to the client to redirect to get_messages
            client.postMessage({ type: 'REDIRECT_TO_MESSAGES', url: getMessagesUrl });
            return;
          }
        }
      } else {
        // App is not open: open the mini-window only
        if (clients.openWindow) {
          // Open the mini reply window (not the main app)
          return clients.openWindow(openPWA);
        }
      }
    })
  );
});
// const CACHE_NAME = 'bizchat-cache-v2';
// const urlsToCache = [
//   // '/',
//   // '/static/css/styles.css',
//   '/static/css/bs_stylesheet.css',
//   // '/static/icons/logo-avator.png',
//   // Add more assets as needed
// ];

self.addEventListener('install', event => {
  self.skipWaiting();
  // event.waitUntil(
  //   caches.open(CACHE_NAME)
  //     .then(cache => cache.addAll(urlsToCache))
  // );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});



self.addEventListener('push', function(event) {
  console.log("Push Event Called2!");
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
      {action: 'reply', title: 'Reply'}
    ]
    };
    event.waitUntil(
      self.registration.showNotification(data.title || 'New Message', options)
    );
    console.log(">>>>");
    self.clients.matchAll({type: 'window'}).then(function(clients) {
      console.log("Custom PUSH_NOTIFICATION Data: ", data);
      console.log("CLIENTS: ", clients);
      clients.forEach(function(client) {
        console.log("Custom PUSH_NOTIFICATION Data: ", data);
        client.postMessage({type: 'PUSH_NOTIFICATION', data: data});
      });
  });
});


// let clients;

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  console.log("Username @Push: ",event.notification.data.url);
  // Extract username or other params from notification data
  const username = event.notification.data && event.notification.data.username;
  const getMessagesUrl = username ? `/get_messages?key=${encodeURIComponent(username)}` : '/';

  // Mini window URL for reply unit
  const openPWA = event.notification.data.url;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
      if (clientList.length > 0) {
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
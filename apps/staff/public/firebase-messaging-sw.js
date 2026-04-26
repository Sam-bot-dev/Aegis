/* eslint-disable */
// Firebase Messaging service worker (background push handler).
// Uses the compat CDN SDK — ES module imports are not supported in SW scope.
// The main app sends the Firebase config via postMessage after registration.

importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js");

self.addEventListener("message", (event) => {
  if (event.data?.type !== "AEGIS_FCM_INIT") return;
  if (firebase.apps.length > 0) return; // idempotent
  firebase.initializeApp(event.data.config);
  const messaging = firebase.messaging();

  messaging.onBackgroundMessage((payload) => {
    const { title = "Aegis Alert", body = "" } = payload.notification ?? {};
    const data = payload.data ?? {};
    self.registration.showNotification(title, {
      body,
      icon: "/icon.svg",
      badge: "/icon.svg",
      tag: data.dispatch_id ?? "aegis-alert",
      renotify: true,
      requireInteraction: true,
      data: { url: data.incident_id ? `/incident/${data.incident_id}` : "/" },
    });
  });
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data?.url ?? "/";
  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((list) => {
        const existing = list.find((c) => "focus" in c);
        if (existing) {
          existing.navigate(url);
          return existing.focus();
        }
        return clients.openWindow(url);
      }),
  );
});

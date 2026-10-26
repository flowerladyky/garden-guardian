/* Garden Guardian: offline app shell and Firebase background push */
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js');
firebase.initializeApp({apiKey:'AIzaSyALfkQ630T8Z3FHGkY36j3G9XlzpwjVPZE',authDomain:'garden-guardian-e6178.firebaseapp.com',projectId:'garden-guardian-e6178',storageBucket:'garden-guardian-e6178.firebasestorage.app',messagingSenderId:'800247417656',appId:'1:800247417656:web:f93741ab9a61b9bd158fcd'});
const messaging=firebase.messaging();
messaging.onBackgroundMessage(payload=>{
  // FCM automatically displays messages with a notification payload in the background.
  // Only manually display data-only messages to avoid duplicate notifications.
  if(payload.notification)return;
  const data=payload.data||{};
  self.registration.showNotification(data.title||'Garden Guardian 🌿',{body:data.body||'Your plants need attention.',icon:'./icon-192.png',badge:'./icon-192.png',data:{url:'./index.html'}});
});
self.addEventListener('notificationclick',event=>{event.notification.close();event.waitUntil(clients.openWindow('./index.html'));});
const CACHE='garden-guardian-v2';
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'])));self.skipWaiting();});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))));self.clients.claim();});
self.addEventListener('fetch',event=>{if(event.request.method==='GET'&&new URL(event.request.url).origin===location.origin){event.respondWith(fetch(event.request).catch(()=>caches.match(event.request)));}});

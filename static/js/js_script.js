//
//// Function to handle the scroll event
//function handleScroll() {
//
////      // console.log("Scroll Called1");
//      // Get the navigation menu element
//
//      // Store the last known scroll position
//      let lastScrollTop = 0;
//
//      // Get the height of the window
//      const windowHeight = window.innerHeight;
//
//      // Get the current scroll position
//      const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
//
//      // Determine the scroll direction
//      const scrollDirection = currentScroll > lastScrollTop ? 'down' : 'up';
//
//
//       if (window.innerWidth <= 768){
//          // If the user is scrolling down and the navigation is not already at the bottom
//          if (scrollDirection === 'down' && (windowHeight + currentScroll) >= document.body.offsetHeight-4000) {
//            // console.log("Scroll Called",currentScroll,scrollDirection);
//          } else {
//            //write code
//          }
//          // Update the known scroll position
//          lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
//
//    }else{
//
//          var scrollingElement = document.getElementById("section-last");
//          // Distance from the top of the document to the top of the scrolling element
//          var elementOffset = scrollingElement.offsetTop;
//          // Viewport (window) top position
//          var windowTop = window.pageYOffset || document.documentElement.scrollTop;
//
//          if (windowTop > elementOffset) {
////              scrollingElement.style.position = "fixed";
////              scrollingElement.style.top = "0";
//              } else {
////                scrollingElement.style.position = "relative";
//              }
//
//    }
//}
//window.onscroll = function() {handleScroll()};

navigator.serviceWorker.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'OPEN_REPLY_UI') {
    // Open the mini window
    openMiniReplyWindow();
  }
});

window.addEventListener('DOMContentLoaded', function() {
  const params = new URLSearchParams(window.location.search);
  if (params.has('openReply')) {
    openMiniReplyWindow();
  }

});

document.querySelector("#main-logo").addEventListener("click",function(){
    window.location.reload();
});

function openMiniReplyWindow() {
  const miniWidth = 350;
  const miniHeight = 600;
  const screenW = window.screen.availWidth;
  const screenH = window.screen.availHeight;
  const left = screenW - miniWidth;
  const top = screenH - miniHeight;
  window.open(
    '/reply_unit',
    'ReplyUnit',
    `width=${miniWidth},height=${miniHeight},left=${left},top=${top},resizable=yes,scrollbars=yes`
  );
}

const replyBtn = document.getElementById('open-reply-unit');
if(replyBtn){
    replyBtn.addEventListener('click', function() {
        const miniWidth = 350;
        const miniHeight = 600;
        // Get the available screen size
        const screenW = window.screen.availWidth;
        const screenH = window.screen.availHeight;
        // Calculate left and top for bottom right
        const left = screenW - miniWidth;
        const top = screenH - miniHeight;
        // Open the window
        window.open(
            '/reply_unit',
            'ReplyUnit',
            `width=${miniWidth},height=${miniHeight},left=${left},top=${top},resizable=yes,scrollbars=yes`
        );
    });
};

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistration().then(function(reg) {
    if (reg) reg.update();
  });
}

// Register service worker and subscribe to push
// if ('serviceWorker' in navigator && 'PushManager' in window) {
//     // console.log("Notification Subscription in progress...");
//     // if (Notification.permission === "denied") {
//     //         // Optionally, show a message to the user:
//     //         alert("You have blocked notifications for this site. Please enable them in your browser settings if you want to receive notifications.");
//     //     }
//     navigator.serviceWorker.register('service-worker.js')
//     .then(function(registration) {
//         // console.log("Notification Subscription in progress...Request Permission");
//         // Request notification permission
//         //  if (confirm("We'd like to notify you about new messages in your Quick Messanger's inbox. Allow?")) {
        
//             if (Notification.permission !== 'granted') {
//                 Notification.requestPermission().then(function(permission) {
//                     if (permission === 'granted') {
//                         subscribeUser(registration);
//                     }
//                 });
//             } else {
//                 subscribeUser(registration);
//             }
//     // }
//     });
// }

// Register service worker and handle push notification permission
if ('serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window) {
    navigator.serviceWorker.register('service-worker.js')
        .then(function (registration) {
            // Check current permission state
            if (Notification.permission === 'granted') {
                // Already allowed — subscribe user to push
                subscribeUser(registration);
            } else if (Notification.permission === 'default') {
                // Not yet asked — explain first or ask directly
                // You can show a UI prompt here before calling this line:
                Notification.requestPermission().then(function (permission) {
                    if (permission === 'granted') {
                        subscribeUser(registration);
                    } else {
                        alert("Notifications were not allowed. You can enable them later in your browser settings.");
                    }
                });
            } else if (Notification.permission === 'denied') {
                    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

                    const lastShown = localStorage.getItem('notificationDeniedAlert');
                    const now = Date.now();

                    // Check if 24 hours (86,400,000 ms) have passed
                    if (!lastShown || now - parseInt(lastShown) > 86400000) {
                        // Show alert only once per day
                        if (isMobile) {
                            alert(
                                "You’ve blocked notifications for Quick Messanger.\n\nTo enable on Android:\n" +
                                "1. Tap the 3-dot menu (⋮) in your browser.\n" +
                                "2. Choose 'Site settings'.\n" +
                                "3. Tap 'Notifications' and allow them.\n" +
                                "4. Reload the page."
                            );
                        } else {
                            alert(
                                "You’ve blocked notifications for Quick Messanger.\n\nTo enable:\n" +
                                "1. Click the padlock icon (🔒) in the address bar.\n" +
                                "2. Go to 'Site settings'.\n" +
                                "3. Allow notifications.\n" +
                                "4. Reload the page."
                            );
                        }

                        // Update last shown time
                        localStorage.setItem('notificationDeniedAlert', now.toString());
                    }
                }
        })
        .catch(function (error) {
            console.error('Service Worker registration failed:', error);
        });
}


function closeRefresh(){
    document.getElementById('recovery-modal').style.display='none';
    window.location.reload();
} 

// Handle standard JS runtime errors
window.onerror = function (msg, url, lineNo, columnNo, error) {
    if (msg && msg.toString().includes("A listener indicated an asynchronous response")) {
        return true;  // Suppress this known harmless error
    }
    return false; // Let other errors show up normally
};

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", function (event) {
    if (event.reason && event.reason.message &&
        event.reason.message.includes("message channel closed")) {
        event.preventDefault(); // Suppress extension-related issue
    } else {
        console.error("Unhandled rejection:", event.reason);
    }
});


function urlBase64ToUint8Array(base64String) {
    // Helper for VAPID public key
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function subscribeUser(registration) {
    // Replace with your actual VAPID public key from Flask config
    const res = await fetch("/vpid");
    const data = await res.json();
    const vapidPublicKey = data.vpkey;
    const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

    registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey
    })
    .then(function(subscription) {
        // Send subscription to Flask backend
        fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subscription)
        });
    })
    .catch(function(err) {
        console.error('Failed to subscribe the user: ', err);
    });
}

navigator.serviceWorker.addEventListener('message', function(event) {
    // console.log("1. We Got message from the service worker js...");
  if (event.data && event.data.type === 'PUSH_NOTIFICATION') {
    // console.log("2...its a push notification");
    showNotification({
      id: Date.now(),
      title: event.data.data.title,
      message: event.data.data.body
    });
  }
});

function showNotification({ id, title, message }) {
    // console.log("3...Display the Notification");
    const container = document.getElementById('notification-container');
    if (!container) return;

    // Prevent duplicate notifications by id
    if (document.getElementById('notif-' + id)) return;

    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.id = 'notif-' + id;

    notif.innerHTML = `
        <button class="notif-close" title="Dismiss">&times;</button>
        <div style="font-weight:600;font-size:1.1em;">${title}</div>
        <div style="font-size:1em;">${message}</div>
        <div class="notif-actions">
            <button onclick="window.location.href='/reply_unit'" class="notif-btn notif-reply">Reply</button>
            <button class="notif-btn notif-delete">Dismiss</button>
        </div>
    `;


    // Close button
    notif.querySelector('.notif-close').onclick = function() {
        notif.remove();
    };

    // Close button
    notif.querySelector('.notif-delete').onclick = function() {
        notif.remove();
    };

    // Reply button
    // notif.querySelector('.notif-reply').onclick = function() {
    //     if (onReply) onReply(id);
    //     notif.remove();
    // };

    // // Delete button
    // notif.querySelector('.notif-delete').onclick = function() {
    //     if (onDelete) onDelete(id);
    //     notif.remove();
    // };

    container.appendChild(notif);
}

// Function to subscribe to push notifications
async function subscribeToPush() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: 'BF-IKMwncA7cR08RWECfzfmYHFCeXFx97-P2_ZFxd5DDHHryXyjBC6bzKa5oYkmN-DhjNYtyoEP4yYCQ38aIVjI'
        });
        // Send subscription to your server via fetch/AJAX
        await fetch('/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subscription)
        });
        document.getElementById('push-subscribe-modal').style.display = 'none';
        alert('Notifications enabled!');
    }
}

navigator.serviceWorker.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'OPEN_REPLY_UI') {
    // Show your custom reply modal/sidebar
    openReplySidebar(event.data.messageId);
  }
});

// If the app is opened via URL with ?replyTo=...
window.addEventListener('DOMContentLoaded', function() {
  const params = new URLSearchParams(window.location.search);
  if (params.has('replyTo')) {
    openReplySidebar(params.get('replyTo'));
  }
});

function openReplySidebar(messageId) {
  // Show a sidebar/modal on the right side of the screen
  // Pre-fill with the message to reply to, etc.
  // Example:
  const sidebar = document.getElementById('reply-sidebar');
  sidebar.style.display = 'block';
  // Load message data, focus input, etc.
}

function openAndCloseMsgs(){
    var msgMainCont = document.querySelector("#navlink-message");
    var msgCont = document.querySelector(".messages-container");
    // var closeBtn = document.querySelector(".close-msg-btn");

    msgMainCont.classList.toggle('change-height');
    msgCont.classList.toggle('display-messages');

}

const paragraph = document.querySelectorAll('.sel-tag');

paragraph.forEach(function(pTag){
    const words = pTag.innerText.split(' ').map(word => `<span>${word}</span>`);
    pTag.innerHTML = words.join(' ');
    pTag.classList.toggle('.sel-tag');
    });
//function pop(){
//    // console.log('Mouse Over');
//}
var container = document.querySelector(".app-dowload-container");
var containerTwo = document.querySelector("#download-icon-2");
// var containerThree = document.querySelector("#download-icon-3");
// var noBgBtn = document.querySelector(".no-bg-btn");
// var installBtn = document.querySelector("#pwa-install-btn");
// Check if the browser supports service workers and PWA installation
if ('serviceWorker' in navigator && 'BeforeInstallPromptEvent' in window) {
    // console.log("PWA installation is supported.");
}

let deferredPrompt;

window.addEventListener('load', () => {
    
    function isAppInstalled() {
        return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    const isFirefox = navigator.userAgent.toLowerCase().includes('firefox');

    if ('serviceWorker' in navigator) {
        // console.log("Service worker supported");

        if (!isAppInstalled()) {
            if ('BeforeInstallPromptEvent' in window) {
                window.addEventListener('beforeinstallprompt', (e) => {
                    // console.log('A2HS event fired');
                    e.preventDefault();
                    deferredPrompt = e;
                    container.style.display = "flex";
                    containerTwo.style.display = "flex";
                    // containerThree.style.display = "flex";
                    // containerTwo.style.display = "flex";
                    const installBtn = document.getElementById('pwa-install-btn');
                    var sidenavBgBtn = document.getElementById("download-icon-2");
                    // var sidenavBgBtnP = document.getElementById("download-icon-3");
                    
                    if (installBtn) {
                        installBtn.addEventListener('click', () => {
                            deferredPrompt.prompt();
                            deferredPrompt.userChoice.then((choiceResult) => {
                                if (choiceResult.outcome === 'accepted') {
                                    // console.log('User accepted A2HS prompt');
                                } else {
                                    // console.log('User dismissed A2HS prompt');
                                }
                                deferredPrompt = null;
                            });
                        });
                    };
                    if (sidenavBgBtn) {
                        sidenavBgBtn.addEventListener('click', () => {
                            deferredPrompt.prompt();
                            deferredPrompt.userChoice.then((choiceResult) => {
                                if (choiceResult.outcome === 'accepted') {
                                    // console.log('User accepted A2HS prompt');
                                } else {
                                    // console.log('User dismissed A2HS prompt');
                                }
                                deferredPrompt = null;
                            });
                        });
                    }
                    // if (sidenavBgBtnP) {
                    //     noBgBtn.addEventListener('click', () => {
                    //         deferredPrompt.prompt();
                    //         deferredPrompt.userChoice.then((choiceResult) => {
                    //             if (choiceResult.outcome === 'accepted') {
                    //                 // console.log('User accepted A2HS prompt');
                    //             } else {
                    //                 // console.log('User dismissed A2HS prompt');
                    //             }
                    //             deferredPrompt = null;
                    //         });
                    //     });
                    // }

                });
            } else if (isFirefox) {
                // console.log("Firefox detected, showing manual install tip.");
                container.style.display = "flex";
                container.innerHTML = `
                    <div class="firefox-tip">
                        Click the install icon in the address bar to add this app.
                    </div>
                `;
            }
        }
    }
});

function openQMenu(){
    var menu = document.querySelector(".mobile-quick-menu");
    menu.classList.toggle("drop-menu");
};

function closeQMenu(){
    var menu = document.querySelector(".mobile-quick-menu");
    menu.classList.toggle("drop-menu");
};

document.addEventListener('DOMContentLoaded', () => {
var manualInstall = document.querySelector("manual-install");


if(manualInstall){
manualInstall.addEventListener('click', () => {
    
    function isAppInstalled() {
        return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    const isFirefox = navigator.userAgent.toLowerCase().includes('firefox');

    if ('serviceWorker' in navigator) {
        // console.log("Service worker supported");

        if (!isAppInstalled()) {
            if ('BeforeInstallPromptEvent' in window) {
                window.addEventListener('beforeinstallprompt', (e) => {
                    // console.log('A2HS event fired');
                    e.preventDefault();
                    deferredPrompt = e;
                    
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then((choiceResult) => {
                            if (choiceResult.outcome === 'accepted') {
                                // console.log('User accepted A2HS prompt');
                            } else {
                                // console.log('User dismissed A2HS prompt');
                            }
                            deferredPrompt = null;
                        });
                    });

                }
            } else if (isFirefox) {
                // console.log("Firefox detected, showing manual install tip.");
                container.style.display = "flex";
                container.innerHTML = `
                    <div class="firefox-tip">
                        Click the install icon in the address bar to add this app.
                    </div>
                `;
            }
        }
    
    });
}
});



var sections = document.querySelectorAll(".profile-sections");
var currentSectionIndex = 0;
var firstSection = sections[0];
var noSections = sections.length;
var progressCont = document.querySelectorAll(".progress-cont");
var progressCount = document.querySelectorAll(".progress-no");
let indexList = [];


function changeProgressColor(){

    for (var sect=0;sect<noSections;sect++){
        // Create Divs
        var progressCountIncr = document.createElement("div");
        var progressCircle = document.createElement("div");
        var progressLineSep = document.createElement("div");

        if (indexList.includes(sect)) {
            // Skip creating the progress element since it exists
            continue;
        }

        // Do not start from zero
        progressCountIncr.innerText = (sect+1);
        //  // console.log("Current Index Outside:" + currentSectionIndex);
        //  // console.log("Current Sect: Outside" + sect);
        //  Make current progress count coral in color

        if(currentSectionIndex == sect){
            // Assign Classes to divs
            progressCountIncr.classList.add("progress-no-c");
            progressCircle.classList.add("progress-incr-c");
            progressLineSep.classList.add("progress-line-sep-c");

            // Append to parents div
            progressCircle.appendChild(progressCountIncr);
            progressCont[currentSectionIndex].appendChild(progressLineSep);
            progressCont[currentSectionIndex].appendChild(progressCircle);

        }else{

//            // console.log("Current Index Else:" + currentSectionIndex);
//            if (!indexList.includes(currentSectionIndex)){

                //Assign Classes to divs
                progressCircle.classList.add("progress-incr");
                progressLineSep.classList.add("progress-line-sep");
                progressCountIncr.classList.add("progress-no");

                // console.log("List Indexes: ",indexList);
                }

                // Append to parents div
                progressCircle.appendChild(progressCountIncr);
                progressCont[currentSectionIndex].appendChild(progressLineSep);
                progressCont[currentSectionIndex].appendChild(progressCircle);

                indexList.push(sect);

        }

    };


const popup = document.querySelector('.pop-up');
var quoteBtns = document.querySelectorAll('.item');
var popCont = document.querySelectorAll('.pop-cont');


quoteBtns.forEach(function(btn){
    btn.addEventListener('click', function(event){
//    // console.log("Contains Poster Quote: ",event.target);
     if(event.target.id === 'logo_quote_btn'){
        var popScrnLogo = document.getElementById("logo_quote");
        popScrnLogo.classList.toggle("show-popup");
        popup.classList.toggle("show-popup");

        }else if(event.target.id === 'poster_quote_btn'){
            var popScrnPoster = document.getElementById("poster_quote");
//            // console.log("Contains Poster Quote: ")
            popScrnPoster.classList.toggle("show-popup");
            popup.classList.toggle("show-popup");
        }else if(event.target.id === 'flyer_quote_btn'){
            var popScrnPoster = document.getElementById("flyer_quote");
            // console.log("Contains Poster Quote: ")
            popScrnPoster.classList.toggle("show-popup");
            popup.classList.toggle("show-popup");
            }
     })
});


//#Menu
//const navSlide = () => {
const burger = document.querySelector(".menu-icon");
const otherNav = document.querySelector(".other-nav");
const navlinks = document.querySelectorAll(".nav-link");
//const navLinks = document.querySelectorAll(".nav-links a");

// function openMenuFunc(){
//     var menuSection = document.querySelector(".app-nav-bar-left");
//     menuSection.classList.toggle("open");
//   };

//  //
//};
//}
//navSlide();

//function openPopup(event){
//     // console.log("Contains Poster Quote")
//};

//    const popCont = document.querySelector('.pop-cont');
//    popup.classList.add("show-popup");

//Read Form
$(document).ready(function(){

    $('.pop-btns').click(function(){
//        // console.log('Cleicked');
        $('form').serializeArray();
        $('form').submit();
    })
});


function closePopup(){
    popup.classList.remove("show-popup");
    popCont.forEach(function(div){
        div.classList.remove("show-popup");
    })
}

//function boolOptionsFunc(){

// var boolOpts = document.querySelectorAll(".bool-options");

// boolOpts.forEach(function(elem){

//     elem.addEventListener('click', function(event){

//         if (event.target.classList.contains("activate-options")){
// //              // console.log("Clicked: ",event.target.style.color);
//               elem.classList.remove("activate-options");
//               elem.classList.add("bool-options");
//         }else{
// //            // console.log("Click: ",event.target);
//             elem.classList.add("activate-options");
//             elem.classList.remove("bool-options");
//         }
//     });

// });

//}

//window.addEventListener('click', function(event){
//    if(popup){
//        if(event.target != popCont){
//           popup.classList.remove(".show");
//        }
//    }
//});

// if (currentSectionIndex == 0){
//     firstSection.style.display = "block";

//     changeProgressColor()

//     }else{
//         firstSection.style.display = "none";
// };


// function showNextSection() {

//     //Prevents Current Page From Reloading
//     event.preventDefault();

//     sections[currentSectionIndex].style.display = "none"; // Hide current section
//     currentSectionIndex++; // Move to the next section

//     if (currentSectionIndex < sections.length) {
//         sections[currentSectionIndex].style.display = "block"; // Show next section
//         changeProgressColor()
//         };

//     };







//If Other in web type is selected do the following...
var otherCategory = document.querySelector("#otherType");
if(otherCategory){
otherCategory.addEventListener('change',function(e){

        if (this.selectedIndex == 5){
            var anInput = document.createElement('input');
            var otherLabel = document.createElement('label');
            var parent = this.parentNode;
            //Assign IDs
            anInput.id = 'other-opt-input';
            otherLabel.id = 'other-opt-label';
            // Label description
            otherLabel.innerHTML = '<span> Please Specify: </span> '
            //Add Class
            anInput.classList.add('form-control-other');
            parent.appendChild(otherLabel);
            this.parentNode.appendChild(anInput);

        }else{
            //If these Elements are defined/present, remove them
            if(document.querySelector("#other-opt-input") != "undefined"){
                document.querySelector("#other-opt-input").remove();
                document.querySelector("#other-opt-label").remove();
            }

        }

    });
};

    //If Other in web type is selected do the following...
var checkBoxBox = document.querySelector("#checkbox-opt");
if(checkBoxBox){
checkBoxBox.addEventListener('change',function(){

        if (this.checked){
            var anInput = document.createElement('input');
            var otherLabel = document.createElement('label');
            var parent = this.parentNode;
            //Assign IDs
            anInput.id = 'doc-upload-id';
            anInput.type = 'file';
            otherLabel.id = 'doc-upload-label';
            // Label description
            otherLabel.innerHTML = '<br><br><span> Please Upload Document below: </span> <br><br> '
            //Add Class
            //anInput.classList.add('form-control-other');
            parent.appendChild(otherLabel);
            this.parentNode.appendChild(anInput);

        }else{
            //If these Elements are defined/present, remove them
            if(document.querySelector("#doc-upload-id") != "undefined"){
                document.querySelector("#doc-upload-id").remove();
                document.querySelector("#doc-upload-label").remove();
            }

        }

    }
    );
};

var $message = $('.sel-tag');

$(window).on('mousemove', function(e) {
    if(e.clientX > e.clientY) {
        $message.text('top right triangle');
    } else {
        $message.text('bottom left triangle');
    }
});


self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      // Serve from cache if available
      if (response) return response;
      // Otherwise, fetch from network
      return fetch(event.request).then(function(networkResponse) {
        // Only cache valid, non-redirected responses
        if (
          !networkResponse || 
          networkResponse.status !== 200 || 
          networkResponse.type !== 'basic'
        ) {
          return networkResponse;
        }
        // Optionally, cache the response here if you want
        // let responseToCache = networkResponse.clone();
        // caches.open(CACHE_NAME).then(function(cache) {
        //   cache.put(event.request, responseToCache);
        // });
        return networkResponse;
      });
    })
  );
});
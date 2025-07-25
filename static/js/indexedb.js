

let db;
let Keys = {};

 function getTCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    };
// Create or Check if db created 
//...if db found return the instance using the promise
function initDB() {
  return new Promise((resolve, reject) => {
    if (db) return resolve(db); // Already initialized

    const request = indexedDB.open("QMessangerDB4", 4);

    request.onupgradeneeded = (event) => {
        db = event.target.result;
        if(!db.objectStoreNames.contains("keys")){
            const store = db.createObjectStore("keys",{
                keyPath: "Usernames",
                autoIncrement:true
            });
            // console.log("DB Created for Keys");
        };

    };//onupgraneeded

    request.onsuccess = (event) =>{
        db = event.target.result;
        // console.log("IndexedDB opened @initDB");
        resolve(db);
        // preRegister();
    };//onsuccess

    request.onerror = (event) => {
        console.error("IndexedDB error:", event.target.error);
        reject(event.target.error);
    };

});//promise
}//db


async function encryptMessage() {
    var messageField = document.querySelector("#message");
    var form = document.getElementById('message-form');
    var replyForm = document.getElementById('reply-form');
    var submitBtn = document.getElementById('submit-form');
    var customerSubmitBtn = document.getElementById('submit-form-mobile');
    var recPKey = document.querySelector("#recipient-pkey");
    var recDuplicatedMsg = document.querySelector("#rec-duplicated-msg");
    var message = messageField.value;
    // var sampleMsg = "Hi How are you Today?"
    // console.log("@encryptMessage");
    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const pKey = request.result[0].publicKey;
            const prKey = request.result[0].privateKey;
            // console.log("Username: ",myUsrname);
            // console.log("Private Key: ",pKey );

            const pubKey = await window.crypto.subtle.importKey("jwk",pKey,{ name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["encrypt"]
                    );

            // console.log("IMported pKey: ",pubKey);

            // // Encrypt the message using the recipient's public key
            const encrypted = await window.crypto.subtle.encrypt(
                { name: "RSA-OAEP" }, pubKey, new TextEncoder().encode(message)
            );

            // Convert the encrypted message to a base64 string for transmission
            const encryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(encrypted)));

            // console.log("Encrypted Message: ",encryptedBase64);
            messageField.value = "";
            
            messageField.value = encryptedBase64;
           

 
            // receiver 
            //..I am using the receiver public key to encrypt the message
            //..so that the receiver can decrypt it using their private key
            //..I am sending 2 versions of the messageField 1 for the sender and 1 for the receiver to be able to decrypt it with thier own private key
            // console.log("Recipient Public Key: ", recPKey.value);
            // Convert the recipient's public key from base64 to JWK object
            const recPKeyJson = atob(recPKey.value);
            const recPKeyJwk = JSON.parse(recPKeyJson);

            const recPubKey = await window.crypto.subtle.importKey("jwk", recPKeyJwk, { name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["encrypt"]
                    );

            const recEncrypted = await window.crypto.subtle.encrypt(
                { name: "RSA-OAEP" }, recPubKey, new TextEncoder().encode(message)
            );

            // Convert the encrypted message to a base64 string for transmission
            const recEncryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(recEncrypted)));

            recDuplicatedMsg.value = recEncryptedBase64;
            // console.log("Recipient Encrypted Message: ",recEncryptedBase64);

            if(submitBtn){
                setTimeout(() => {
                    submitBtn.click();
                    // console.log("Encrypted Message set to-:", messageField.value);
                }, 500);
            }else if(customerSubmitBtn)  {
                console.log("Submit Button not found");
                setTimeout(() => {
                    customerSubmitBtn.click();
                    // console.log("Encrypted Message set to-:", messageField.value);
                }, 500);
            }

        
        }else{
            // console.log("Error @encryptMessage");
        }
    }

}


async function encryptMessageChat(event) {
    if (event) event.preventDefault();
    var form = event.target;
    var messageField =  form.elements['reply-message']; //document.querySelector("#reply-message");
    var replyForm = form //document.getElementById('reply-form');
    var submitBtn = document.getElementById('chat_submit');
    var receiverPKey =  form.elements['recipient_pkey'];//document.querySelector("#recipient_pkey");
    var recDuplicatedMsg = form.elements['rec_encrypted-msg'];  //document.querySelector("#rec-duplicated-msg");
    var message = messageField.value;
    // console.log("@encryptMessage Chat");
    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const pKey = request.result[0].publicKey;
            const prKey = request.result[0].privateKey;
            // console.log("Username Chat: ",myUsrname);
            // console.log("Private Key Chat: ",pKey );

            const pubKey = await window.crypto.subtle.importKey("jwk",pKey,{ name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["encrypt"]
                    );

            // console.log("IMported pKey Chat: ",pubKey);
            // console.log("Message Chat: ",message);
            let encrypted;

            // try {
                // console.log("About to encrypt. pubKey:", pubKey, "message:", message);
                const encodedMsg = new TextEncoder().encode(message);
                // console.log("Encoded message:", encodedMsg);
                encrypted = await window.crypto.subtle.encrypt(
                    { name: "RSA-OAEP" }, pubKey, encodedMsg
                );
                // console.log("Encrypted result:", encrypted);
            // } catch (e) {
            //     console.error("Encryption failed:", e);
            // }

            // // Encrypt the message using the recipient's public key
            // const encrypted = await window.crypto.subtle.encrypt(
            //     { name: "RSA-OAEP" }, pubKey, new TextEncoder().encode(message)
            // );

            // // console.log("Encrypted Message Chat: ",encryptedBase64);
            // Convert the encrypted message to a base64 string for transmission
            const encryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(encrypted)));

            
            messageField.value = "";
            
            messageField.value = encryptedBase64;
        
 
            // receiver 
            //..I am using the receiver public key to encrypt the message
            //..so that the receiver can decrypt it using their private key
            //..I am sending 2 versions of the messageField 1 for the sender and 1 for the receiver to be able to decrypt it with thier own private key
            var recPKey = receiverPKey;
            // console.log("Recipient Public Key Chat: ", recPKey.value);
            // console.log("Recipient Public Key Chat: ", recPKey.value);
            // Convert the recipient's public key from base64 to JWK object
            const recPKeyJson = atob(recPKey.value);
            const recPKeyJwk = JSON.parse(recPKeyJson);

            const recPubKey = await window.crypto.subtle.importKey("jwk", recPKeyJwk, { name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["encrypt"]
                    );

            const recEncrypted = await window.crypto.subtle.encrypt(
                { name: "RSA-OAEP" }, recPubKey, new TextEncoder().encode(message)
            );

            // Convert the encrypted message to a base64 string for transmission
            const recEncryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(recEncrypted)));

            recDuplicatedMsg.value = recEncryptedBase64;
            // console.log("Recipient Encrypted Message Chat: ",recEncryptedBase64);

            replyForm.submit();

            // if(submitBtn){
            //     setTimeout(() => {
                    
            //         // console.log("Encrypted Message set to-:", messageField.value);
            //     }, 500);
            // }else{
            //     // console.log("Submit Button not found");
            // }

        
        }else{
            // console.log("Error @encryptMessage");
        }
    }

}

sendForm = async () => {
    // console.log("Send Form Called");
    // var submitBtn = document.getElementById('submit-form');
    
    // e.preventDefault();
    console.dir(form);
    // form.submit();
    // form.reset();
}


document.addEventListener("DOMContentLoaded", function () {
    // Navigation Messages Buttons
    document.querySelectorAll(".nav-message-text").forEach(function(elmsgDiv){
        var encryptedBase64 = elmsgDiv.getAttribute("data-encrypted");
        if (encryptedBase64) {
            // console.log("Encrypted Base64: ", encryptedBase64);
            decryptNavMessage(encryptedBase64, elmsgDiv).then(() => {
                // console.log("Decryption completed");
            }).catch((error) => {
                console.error("Decryption failed:", error);
            });
        } else {
            // console.log("No encrypted message found.");
        }

    })

    // Mini Window Messages 
    document.querySelectorAll(".message-text").forEach(function(elmsgDiv){
        var encryptedBase64 = elmsgDiv.getAttribute("data-encrypted");
        if (encryptedBase64) {
            // console.log("Encrypted Base64: ", encryptedBase64);
            decryptMessage(encryptedBase64, elmsgDiv).then(() => {
                // console.log("Decryption completed");
            }).catch((error) => {
                console.error("Decryption failed:", error);
            });
        } else {
            // console.log("No encrypted message found.");
        }

    })

    // Main Chat Messages 
     document.querySelectorAll(".message-body").forEach(function(msgBdyDiv){
        var encryptedBase64 = msgBdyDiv.getAttribute("data-message");
        if (encryptedBase64) {
            // console.log("Encrypted Base64: ", encryptedBase64);
            decryptMessageBody(encryptedBase64, msgBdyDiv).then(() => {
                // console.log("Decryption completed");
            }).catch((error) => {
                console.error("Decryption failed:", error);
            });
        } else {
            // console.log("No encrypted message found.");
        }

    })
});

// Decrypt the message using the recipient's private key - Navigation Messages
async function decryptNavMessage(encryptedBase64,elmsgDiv) {
     if (!db) {
        // If db is not initialized, wait for it
        // console.log("DB not initialized, calling initDB");
        db = await initDB();
    }
    // console.log("@decryptMessage");
    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const pKey = request.result[0].publicKey;
            const prKey = request.result[0].privateKey;
            // console.log("Username: ",myUsrname);
            // console.log("Private Key: ",pKey );

            const privKey = await window.crypto.subtle.importKey("jwk",prKey,{ name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["decrypt"]
                    );

            // console.log("IMported prKey: ",privKey);

            // Convert the base64 string back to an ArrayBuffer
            const encryptedBuffer = new Uint8Array(atob(encryptedBase64).split("").map(c => c.charCodeAt(0)));

            // Decrypt the message using the recipient's private key
            const decrypted = await window.crypto.subtle.decrypt(
                { name: "RSA-OAEP" }, privKey, encryptedBuffer
            );

            // Convert the decrypted message back to a string
            const decryptedMessage = new TextDecoder().decode(decrypted);
            elmsgDiv.innerHTML = ""; // Clear the existing content
            // elmsgDiv.innerHTML = decryptedMessage; // Display the decrypted message in the element

            msgLength = decryptedMessage.length;
            if (msgLength >= 20){
                elmsgDiv.innerHTML = decryptedMessage.substring(0,20) + "...";
            }else{
                elmsgDiv.innerHTML = decryptedMessage;
            };
            
            

            // console.log("Decrypted Message: ",decryptedMessage);

        }else{
            // console.log("Error @decryptMessage");
        }
    }
    
}

// Decrypt the message using the recipient's private key - Mini Window Messages
async function decryptMessage(encryptedBase64,elmsgDiv) {
     if (!db) {
        // If db is not initialized, wait for it
        // console.log("DB not initialized, calling initDB");
        db = await initDB();
    }
    // console.log("@decryptMessage");
    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const pKey = request.result[0].publicKey;
            const prKey = request.result[0].privateKey;
            // console.log("Username: ",myUsrname);
            // console.log("Private Key: ",pKey );

            const privKey = await window.crypto.subtle.importKey("jwk",prKey,{ name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["decrypt"]
                    );

            // console.log("IMported prKey: ",privKey);

            // Convert the base64 string back to an ArrayBuffer
            const encryptedBuffer = new Uint8Array(atob(encryptedBase64).split("").map(c => c.charCodeAt(0)));

            // Decrypt the message using the recipient's private key
            const decrypted = await window.crypto.subtle.decrypt(
                { name: "RSA-OAEP" }, privKey, encryptedBuffer
            );

            // Convert the decrypted message back to a string
            const decryptedMessage = new TextDecoder().decode(decrypted);
            elmsgDiv.innerHTML = ""; // Clear the existing content
            // elmsgDiv.innerHTML = decryptedMessage; // Display the decrypted message in the element

            msgLength = decryptedMessage.length;
            
            elmsgDiv.innerHTML = decryptedMessage;
            

            // console.log("Decrypted Message: ",decryptedMessage);

        }else{
            // console.log("Error @decryptMessage");
        }
    }
    
}

// Decrypt the message using the recipient's private key - Main Chat Window
async function decryptMessageBody(encryptedBase64,elmsgDiv) {
     if (!db) {
        // If db is not initialized, wait for it
        // console.log("DB not initialized, calling initDB");
        db = await initDB();
    }
    // console.log("@decryptMessage2:", encryptedBase64);
    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const pKey = request.result[0].publicKey;
            const prKey = request.result[0].privateKey;
            // // console.log("Username: ",myUsrname);
            // // console.log("Private Key: ",pKey );

            const privKey = await window.crypto.subtle.importKey("jwk",prKey,{ name: "RSA-OAEP", hash: "SHA-256" },
                        true,
                        ["decrypt"]
                    );

            // // console.log("IMported prKey2: ",privKey);

            // Convert the base64 string back to an ArrayBuffer
            const encryptedBuffer = new Uint8Array(atob(encryptedBase64).split("").map(c => c.charCodeAt(0)));

            // Decrypt the message using the recipient's private key
            const decrypted = await window.crypto.subtle.decrypt(
                { name: "RSA-OAEP" }, privKey, encryptedBuffer
            );

            // Convert the decrypted message back to a string
            const decryptedMessage = new TextDecoder().decode(decrypted);
            elmsgDiv.innerHTML = ""; // Clear the existing content
            // elmsgDiv.innerHTML = decryptedMessage; // Display the decrypted message in the element

            
            elmsgDiv.innerHTML = decryptedMessage;
           

            // // console.log("Decrypted Message2: ",decryptedMessage);

        }else{
            // console.log("Error @decryptMessage");
        }
    }
    
}

function saveUsername(user){
    // // console.log("Save Is Called: ",user);
}

async function preRegister(){
    
    var modal = document.querySelector("#alert-confirm");
    var userNameField = document.querySelector("#user-name");
    var loginId = document.querySelector("#login");
    var goRegister = document.querySelector("#go-register");
    var currentFromServ = document.querySelector("#cuser-ref");
    // // console.log("CURRENT FROM SERVER: ", currentFromServ.textContent);

    if (modal.style.display === "flex") {
        modal.style.display = "none";
        // console.log("Turn OFF Alert Box");
        return;
    };

    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        // // console.log("Request Success: ", store);
        if (request.result && request.result.length > 0) {
            const { Usernames: myUsrname, publicKey: Pkey, privateKey: Prkey } = request.result[0];
            // console.log("CURRENT FROM BROWSER: ", myUsrname);

            if (!myUsrname) {
                // console.log("Username Not Found from Browser");
                return;
            }

            if (myUsrname !== currentFromServ.textContent) {
                if (currentFromServ.textContent === "") {
                    // console.log("No Username Found on Server");
                    return;
                    // proceed to open login modal 
                } else {
                    // console.log("Alert!! Username Mismatch");
                    autoRecoverKeysModal();
                    return;
                }
                
            }

            
            if (currentFromServ.textContent === "") {
                    // // console.log("No Username Found on Server 2");
                    return;
                    // proceed to open login modal 
                } 
                
    
            // Username matches
            // // console.log("Username matching: ","IndexedDB: ", myUsrname, ",Server Side: ", currentFromServ.textContent);

            if (currentFromServ.textContent === myUsrname) {
                // // console.log("Username matches, proceeding to register new keys");
                fetch('/api/is_logged_in')
                .then(res => res.json())
                .then(data => {
                    if (data.logged_in) {
                        // // console.log("User is logged in",data.logged_in);
                        if(document.querySelector("#login-mobile").textContent === "login"){
                            // console.log("Turn ON Alert Box");
                            modal.style.display = "flex";
                            loginId.href = "/login?id=" + myUsrname;
                        }
                    } else {
                        // // console.log("User is NOT logged in");
                        // // console.log("Turn ON Alert Box");
                        modal.style.display = "flex";
                        loginId.href = "/login?id=" + myUsrname;
                    }
                });
            }

            // Check recovery status from server
            const response = await fetch("/auto_recovery_checker", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json','X-CSRFToken': getTCSRFToken() },
                body: JSON.stringify({ username: myUsrname })
            });

            const data = await response.json();
            // console.log("---Rec_Status_Check: ", data.status);

            if (data.status === "False") {
                autoRecoverCheck({ myUsrname, Pkey, Prkey });
            } else {
                if(currentFromServ.textContent===""){
                    // console.log("Turn ON Alert Box");
                    modal.style.display = "flex";
                    loginId.href = "/login?id=" + myUsrname;
                }else{
                    return;
                }
            }
        } else {
            if (currentFromServ.textContent === "") {
                    // console.log("No Username Found on Server 3");
                } else {
                    // console.log("Alert!! Username Mismatch");
                    autoRecoverKeysModal();
                }
                return;
        }
    };
    // // console.log("preRegister Called");
};


function saveKeysinCloud(){
    password = document.querySelector("#password_rec").value;

    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");
    const request = store.getAll();

    request.onsuccess = async function() {
        if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].Usernames;// Get the username from the first record
            const Pkey = request.result[0].publicKey;
            const Prkey = request.result[0].privateKey;
            AutoSaveKeys({myUsrname,Pkey,Prkey},password);
        }
    };
};

function closeRecModal(){
    document.getElementById('restore-modal').style.display='none';
    window.location.href = "/";
}


async function registerNewKeys(){

    var currentFromServ = document.querySelector("#cuser-ref");

    if( currentFromServ.textContent === "") {
        // console.log("Your username is not set on the server");
        alert("Your username is not set on the server. Please contact support.");
        return;
    };

    // Example usage
    const myUsername = currentFromServ.textContent; // Generate a 10-character base32 string
    // console.log("Random Base32 String:", myUsername);

    // Open the IndexedDB database
    const request = indexedDB.open("QMessangerDB4", 4);

    request.onsuccess = async function (event) {
            db = event.target.result;
            // console.log("Database opened @register");

            // Step 1: Generate RSA key pair
            const keyPair = await window.crypto.subtle.generateKey(
                {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]), // 65537
                hash: "SHA-256",
                },
                true, // extractable: true (allows export)
                ["encrypt", "decrypt"]
            );

            Keys.publicKey = keyPair.publicKey;
            // Keys.privateKey = keyPair.privateKey;

            // Step 2: Export the public key as JWK
            const exportedPublicKey = await window.crypto.subtle.exportKey("jwk", keyPair.publicKey);
            const exportedPrivateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
            // console.log("Exported public key JWK: @register", exportedPublicKey);

            // Step 3: Save it
            savePublicKey(myUsername, exportedPublicKey, exportedPrivateKey);

            // Prepare to send to server 
        
            function toBase64(str) {
            const bytes = new TextEncoder().encode(str);
            let binary = '';
            for (let b of bytes) {
                binary += String.fromCharCode(b);
            }
            return btoa(binary);
            }

            const pubJson = JSON.stringify(exportedPublicKey);
            const pubBase64 = toBase64(pubJson); // Convert the public key to a base64 string for transmission
            
            fetch("/register_new_keys", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getTCSRFToken()
                },
                body: JSON.stringify({ 
                    username: myUsername, 
                    newPkey: pubBase64
                })
            })
            .then(response => response.json())
            .then(data => {
                // console.log("Server Response:", data);
                if (data.success) {
                    alert("Keys registered successfully!");
                    window.location.href = "/login?id=" + myUsername;
                } else {
                    alert("Failed to register keys: " + data.message);
                }
            })
        }
};

// Register 
async function register() {
    // console.log("Register")

    var modal = document.querySelector("#alert-confirm");
    modal.style.display = "none";

    // Generate 5 random numbers
    function generateRandomBase32String(length) {
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; // Base32 character set
        let result = "";
        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * chars.length);
            result += chars[randomIndex];
        }
        return result;
    }

    // Example usage
    const myUsername = generateRandomBase32String(10); // Generate a 10-character base32 string
    // console.log("Random Base32 String:", myUsername);

    // Open the IndexedDB database
    const request = indexedDB.open("QMessangerDB4", 4);

    request.onsuccess = async function (event) {
        db = event.target.result;
        // console.log("Database opened @register");

        // Step 1: Generate RSA key pair
        const keyPair = await window.crypto.subtle.generateKey(
            {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]), // 65537
            hash: "SHA-256",
            },
            true, // extractable: true (allows export)
            ["encrypt", "decrypt"]
        );

        Keys.publicKey = keyPair.publicKey;
        // Keys.privateKey = keyPair.privateKey;

        // Step 2: Export the public key as JWK
        const exportedPublicKey = await window.crypto.subtle.exportKey("jwk", keyPair.publicKey);
        const exportedPrivateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
        // console.log("Exported public key JWK: @register", exportedPublicKey);

        // Step 3: Save it
        savePublicKey(myUsername, exportedPublicKey, exportedPrivateKey);
        // Temporarily store the data
        // let tempData = { myUsername, exportedPublicKey, exportedPrivateKey };

        // Prepare to send to server 
        
        function toBase64(str) {
          const bytes = new TextEncoder().encode(str);
          let binary = '';
          for (let b of bytes) {
            binary += String.fromCharCode(b);
          }
          return btoa(binary);
        }

        const pubJson = JSON.stringify(exportedPublicKey);
        const pubBase64 = toBase64(pubJson); // Convert the public key to a base64 string for transmission
        var pKey = document.querySelector("#pKey");
        var usrName= document.querySelector("#username");
        //const pubBase64 = btoa(String.fromCharCode(...new Uint8Array(jwk)));// Convert the public key to a base64 string for transmission
        // console.log("Base64 Public Key:", pubBase64);
        setTimeout(() => {
            usrName.value = "";
            pKey.value = pubBase64;
            usrName.value = myUsername;
            // console.log("Username set to-:", usrName.value);
            // sendEncryptedWelcomeMessage(myUsername, exportedPublicKey);
        }, 500);

        var username = myUsername;

        // var response = await fetch("/recovery_status_reg",{
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({ username: username })
        // });
        // var data = await response.json();
        // // console.log("Rec_Status_Rec: ",data.res);

        // Optional: Use MutationObserver to monitor changes and override them
        // const observer = new MutationObserver(() => {
        // if (usrName.value !== myUsername) {
        //     usrName.value = "";
        //     usrName.value = myUsername;
        //     usrName.setAttribute('value', myUsername);
        //     // console.log("Username corrected to:", usrName.value);
        // }
    // });

    observer.observe(usrName, { attributes: true, childList: true, subtree: true });  
    };
};


document.addEventListener("DOMContentLoaded", async function () {
    try{
        initDB();

        const tx = db.transaction("keys","readwrite");
        const store = tx.objectStore("keys");
        const request = store.getAll();

        request.onsuccess = async function() {
            if (request.result && request.result.length > 0) {
                const username = request.result[0].Usernames;// Get the username from the first record
                const pKey = request.result[0].publicKey;

                // console.log("Testing Auto Message.....: ",username);
                const welcomeText = "Hello and welcome to Quick Messanger! Start connecting and growing your business today. Should you have any enquiries, please feel free to use this platform for a prompt response.";

                // Import the user's public key
                const pubKey = await window.crypto.subtle.importKey(
                    "jwk",
                    pKey,
                    { name: "RSA-OAEP", hash: "SHA-256" },
                    true,
                    ["encrypt"]
                );

                // Encrypt the message
                const encrypted = await window.crypto.subtle.encrypt(
                    { name: "RSA-OAEP" },
                    pubKey,
                    new TextEncoder().encode(welcomeText)
                );

                // Convert to base64
                const encryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(encrypted)));

                // Send to backend
                const welcomeMsg = {
                    to: username,
                    subject: "Welcome to Quick Messanger!",
                    message: encryptedBase64
                };
                try {
                    // console.log("Testing Auto Message.....:2 ",welcomeMsg);
                    const response = await fetch("/send_message", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(welcomeMsg)
                    });
                    const result = await response.json();
                    // console.log("Welcome message sent:", result);
                } catch (err) {
                    console.error("Failed to send welcome message:", err);
                }
            };
        }
    }catch (err){
        console.log("Failed to run DB");
    }
});

function processLoginModal(id,username){
    var userNameField = document.querySelector("user-name");
    var userLinkField = document.querySelector("login");
    var modalBg = document.querySelector('login-modal-bg');

    userNameField.innerHTML = username;
    userLinkField.href = "/login?id="+id;
    modalBg.style.display = 'block';
}

//Save Function
function savePublicKey(username, publicJwk, privateJwk) {


    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");

    // Iterate through all entries and delete them
    const getAllRequest = store.getAll();

    getAllRequest.onsuccess = async () =>{
        // console.log("DB Output: @savePublicKey", getAllRequest.result);

        // Extract and log the IDs of the keys
        const keyIds = getAllRequest.result.map(entry => entry.Usernames);
        // console.log("Key IDs:", keyIds);   

        const keys = getAllRequest.result;
        // Delete all keys if the user confirms
        const deleteTx = db.transaction("keys", "readwrite");
        const deleteStore = deleteTx.objectStore("keys");
        if (keys.length >= 1) {
        // console.log("Keys to delete: ", keys)
        keys.forEach((key) => {
            // console.log("Almost Deleted");
            deleteStore.delete(key.Usernames);
        });
        };
    };

    // Add the new entry after deleting all old ones
    store.put({ 
      "Usernames":username,
      publicKey: publicJwk,
      privateKey: privateJwk
    });

    tx.oncomplete = () => // console.log("JWK saved for", username);
    tx.onerror = (e) => console.error("Save failed:", e.target.error);
};



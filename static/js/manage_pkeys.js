let db;
let Keys = {};
let userName;

function initDB() {
  return new Promise((resolve, reject) => {
    if (db) return resolve(db); // Already initialized

    const request = indexedDB.open("BusinessChatDB", 2);

    request.onupgradeneeded = (event) => {
      db = event.target.result;
      if (!db.objectStoreNames.contains("keys")) {
        db.createObjectStore("keys", { keyPath: "username" });
        console.log("Object store created");
      }
    };

    request.onsuccess = (event) => {
      db = event.target.result;
      console.log("IndexedDB opened");
      resolve(db);
      // This script for messages waits for db to open first 
    async function preStartReadingMsgs() {
        // const myUsrname = await myUserName();
        console.log("Script 3 pre-test ");
        const tx = db.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const request = store.getAll();

        request.onsuccess = () => {
          if (request.result && request.result.length > 0) {
            const myUsrname = request.result[0].username;// Get the username from the first record
            const key = request.result[0].publicKey;
            console.log("Script 3 pre-test: ",myUsrname);
            if (myUsrname) {
              startReadingMsg(myUsrname);
            };
          };
        }
        
      };preStartReadingMsgs();
    
    };

    request.onerror = (event) => {
      console.error("IndexedDB error:", event.target.error);
      reject(event.target.error);
    };
  });
}

let user;


function myUserName() {
  console.log("myUserName==Called" );
  if (!userName){
    return new Promise((resolve, reject) => {
      const tx = db.transaction("keys", "readonly");
      const store = tx.objectStore("keys");
      const request = store.getAll();

      request.onsuccess = () => {
        if (request.result && request.result.length > 0) {
          const myUsrname = request.result[0].username;// Get the username from the first record
          const key = request.result[0].publicKey;
          userName = myUsrname;
          console.log("PublicKey: ",key);
          // alert("Usernames: " + request.result[0].username);
          resolve(myUsrname);

          //send username to flask app
          async function importAndUseKey(jwk) {
            try {
              // Import the JWK as a CryptoKey
              const publicKey = await window.crypto.subtle.importKey(
                "jwk", // Format of the key
                jwk, // The JWK object
                { name: "RSA-OAEP", hash: "SHA-256" }, // Algorithm details
                true, // Whether the key is extractable
                ["encrypt"] // Key usage
              );
              const jwkString = JSON.stringify(jwk);
              // Encode the JSON string to Base64
              const base64Key = btoa(jwkString);
              console.log("Key:::::::::::",base64Key)
              const response =await fetch(`/username/${myUsrname}/${base64Key}`);
              const result = await response.json();
              console.log("Result: ", result);
              if (result.User === "Success") {
                console.log("User successfully processed.");
              } else {
                const tx = db.transaction("keys", "readwrite");
                const store = tx.objectStore("keys");
              
                // Iterate through all entries and delete them
                const getAllRequest = store.getAllKeys();
              
                getAllRequest.onsuccess = async () => {
                  const keys = getAllRequest.result;
                  // Delete all keys if the user confirms
                  const deleteTx = db.transaction("keys", "readwrite");
                  const deleteStore = deleteTx.objectStore("keys");
                  if (keys.length >= 1) {
                    console.log("Keys to delete: ", keys)
                    keys.forEach((key) => {
                      console.log("Almost Deleted");
                      // deleteStore.delete(key);
                    });
                  };
                };

                // location.reload();

                console.error("Error processing user:", result);
              }
            } catch (error) {
              console.error("Error importing or using the public key:", error);
            }
          };

          importAndUseKey(key);

        } else {
          console.warn("No user found in IndexedDB");
          alert("No user found. Please register first.");
          resolve(null);
        }
        
      };

      request.onerror = (e) => {
        console.error("Failed to retrieve user:", e.target.error);
        reject(e.target.error);
      };
    });
  }else{
    console.log("User is Defined: ", userName);
  }
};


  // document.addEventListener('DOMContentLoaded', 
async function startReadingMsg(myUsrname){
    console.log("Script is working 2");
    var messages = document.querySelectorAll(".message-text");

    // Ensure myUsrname is defined
    // const myUsrname = await myUserName(); // Assuming myUserName() is defined elsewhere
    // if (!myUsrname) {
    //     console.error("No username found. Please register first.");
    //     return;
    //     }

    messages.forEach(function (msg) {
          // Ensure the loop does not re-trigger itself
        if (msg.dataset.processed) return; // Skip already processed messages
        msg.dataset.processed = true; // Mark as processed
        
        console.log("Script is working 3");
        var messege = msg.textContent; // Ensure this is the correct source of the message
        var sender = document.querySelectorAll('.message-item-name');
        // console.log("Raw message value:", messege);

        async function getPKey() {
            const privateKey = await loadPrivateKeyFromIndexedDB(myUsrname);
            if (!privateKey) {
                console.error("No private key found in storage.");
                alert("No key found. Please register first. @getKey");
                return;
            }

            try {
                // If the message is not valid Base64, encode it to Base64
                if (!/^[A-Za-z0-9+/=]+$/.test(messege)) {
                    console.warn("Message is not valid Base64. Encoding it to Base64.");
                    messege = btoa(messege);
                }

                const binary = Uint8Array.from(atob(messege), c => c.charCodeAt(0));
                try {
                    const decrypted = await window.crypto.subtle.decrypt(
                        { name: "RSA-OAEP" }, privateKey, binary
                    );
                    const text = new TextDecoder().decode(decrypted);
                    if (text.length >= 20) {
                        msg.innerHTML = text.substring(0, 20) + ".."; // Update the message content
                    } else {
                        msg.innerHTML = text; // Update the message content
                    }
                } catch (decryptionError) {
                    console.warn("Failed to decrypt message. Skipping this message:", decryptionError);
                };
    
                sender.forEach(function(Name){
                    if(Name.textContent.length >= 12) {
                        Name.innerHTML = Name.textContent.substring(0,12)+"..";
                        console.log("Text Content Calc: "+ Name.textContent)
                    };
                  
              });
                
            } catch (error) {
                console.error("Error decrypting message:",  error);
            }
        }

        getPKey();
       
    });

    };


window.addEventListener('load', () => {
  initDB().then(() => {
    console.log("Database ready");
    
    // Get Username from IndexedDB after the database is ready
    myUserName().then((myUsrname) => {
      if (myUsrname) {  
        var usernameField = document.getElementById("username-label");
        usernameField.innerHTML = myUsrname; // Set the username field to the retrieved username
        console.log("1 My username is: " + myUsrname);
      }
    }).catch((error) => {
      location.reload(); //reload if is in the case of first registration
      // console.error("Error retrieving username:");
    });
  }).catch((error) => {
    console.error("Error initializing database:", error);
  });

});

// Check IF the username already exists in the database 
async function usernameExists(username) {
  return new Promise((resolve) => {
    const tx = db.transaction("keys", "readonly");
    const store = tx.objectStore("keys");
    const request = store.get(username);
    request.onsuccess = () => resolve(!!request.result);
    request.onerror = () => resolve(false);
  });
}

async function register() {

    let myUsername = document.getElementById('username').value;
    if (!myUsername) {
      alert("Please enter a username.");
      return;
    }

    // Open the IndexedDB database
    const request = indexedDB.open("BusinessChatDB", 2);

    request.onupgradeneeded = function (event) {
      db = event.target.result;
      // This event is triggered when the database is created or upgraded
      if (!db.objectStoreNames.contains("keys")) {//
          db.createObjectStore("keys", { keyPath: "username" }); // Create an object store for public keys with username as the key path
          console.log("Object store created");
      }else {
          console.log("Object store already exists");
      }
    };
    
    request.onsuccess = async function (event) {
      console.log("Registering user...");
        db = event.target.result;
        console.log("Database opened");

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
        Keys.privateKey = keyPair.privateKey;

        // Step 2: Export the public key as JWK
        const exportedPublicKey = await window.crypto.subtle.exportKey("jwk", keyPair.publicKey);
        const exportedPrivateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
        console.log("Exported public key JWK:", jwk);

        // Step 3: Save it
        savePublicKey(myUsername, exportedPublicKey, exportedPrivateKey);
        let name = document.querySelector('#name').value;
        let email = document.querySelector('#email').value;
        let password = document.querySelector('#password').value;
        let company = document.querySelector('#company_name').value;

        function toBase64(str) {
          const bytes = new TextEncoder().encode(str);
          let binary = '';
          for (let b of bytes) {
            binary += String.fromCharCode(b);
          }
          return btoa(binary);
        }

        const pubJson = JSON.stringify(jwk);
        const pubBase64 = toBase64(pubJson); // Convert the public key to a base64 string for transmission

        //const pubBase64 = btoa(String.fromCharCode(...new Uint8Array(jwk)));// Convert the public key to a base64 string for transmission
        console.log("Base64 Public Key:", pubBase64);
        // Step 4: Send the public key to the server
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: myUsername, publicKey: pubBase64 , name:name, email:email, password:password,company:company})
        });
        console.log("Well they are registered!")
        // alert("Registered");
        // location.reload();
        result = await response.json();
        
        
    }
};

async function sendMessage() {
    const recipient = document.getElementById('recipient').value;
    const message = document.getElementById('message').value;
    const subject = document.getElementById('subject').value;

    const res = await fetch(`/public_key/${encodeURIComponent(recipient)}`);
    const result = await res.json();

    const { publicKey: pubBase64 } = result;

    if (!pubBase64) {
      alert("No Public Key found for " + result.error);
      return
    }
    console.log("Base64 Public Key From Server:", pubBase64);
    function  fromBase64(pubBase64) {
      const binary = atob(pubBase64); // Decode the base64 public key
      const binaryDer = Uint8Array.from(binary, c => c.charCodeAt(0));// Convert the base64 string to a binary array
      return new TextDecoder().decode(binaryDer);
      }
    const binary = fromBase64(pubBase64); // Get the JSON string back
    const jwk = JSON.parse(binary); // Parse to JWK object

    //Import the public key from JWK format
    const pubKey = await window.crypto.subtle.importKey(
      "jwk", jwk, { name: "RSA-OAEP", hash: "SHA-256" }, true, ["encrypt"]
    );

    // Encrypt the message using the recipient's public key
    const encrypted = await window.crypto.subtle.encrypt(
      { name: "RSA-OAEP" }, pubKey, new TextEncoder().encode(message)
    );

    // Convert the encrypted message to a base64 string for transmission
    const encryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(encrypted)));

    console.log("Sending message to: " + recipient);
    console.log("Encrypted MSG: " + encryptedBase64);
    fromMe = await myUserName(); 
    console.log("From: " + fromMe);
    const sent = await fetch('/send_message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to: recipient, message: encryptedBase64, sender: fromMe, subject:subject })
    });
    const sentResult = await sent.json();
    if (sentResult) {
      alert("MSG: " + sentResult.status);
    } else {
      alert("Failed to send message: " + sentResult.error);
    }

    await sendMessageWithMyKey(); 
}


function getPublicKeyAsync(user){
  return new Promise((resolve, reject) => {
    getPublicKey(user, (publicKey) => {
      if (publicKey){
        resolve(publicKey);
      }else{
        reject("No Public Key Found for ${user}")
      }
    })
  })
}

async function sendMessageWithMyKey() {

  console.log(" Send Me Message")
  const recipient = document.getElementById('recipient').value;
  const message = document.getElementById('message').value;
  let pubKey;

  try {
      const user = await myUserName();
      console.log("Check Local Key for", user);
      pubKey = await getPublicKeyAsync(user);
      console.log("Local key Resolved", pubKey);
  
      if (!pubKey) {  
        console.error("No public key found in storage.");
        alert("No key found.");
        return;
      }
  } catch (error) {
      console.error("Error retrieving username or resolving key:", error);
      return;
  }

  try{
    const convPubKey = await window.crypto.subtle.importKey(
      "jwk", pubKey, 
      {name: "RSA-OAEP", hash: "SHA-256"},
      true,
      ["encrypt"]
    );

    // Encrypt the message using the recipient's public key
    const encrypted = await window.crypto.subtle.encrypt(
      { name: "RSA-OAEP" }, convPubKey, new TextEncoder().encode(message)
    );

    // Convert the encrypted message to a base64 string for transmission
    const encryptedBase64 = btoa(String.fromCharCode(...new Uint8Array(encrypted)));

    console.log("Sending message to: " + recipient);
    console.log("Encrypted MSG: " + encryptedBase64);
    fromMe = await myUserName(); 
    console.log("From: " + fromMe);
    const sent = await fetch('/sendme_message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to: recipient, message: encryptedBase64, sender: fromMe })
    });
    const sentResult = await sent.json();
    if (sentResult) {
      alert("Send Me MSG: " + sentResult.status);
    } else {
      alert("Failed to send message: " + sentResult.error);
    }

  }catch(error){
    console.error("Error during encryption or sending: ", error);
  }
}

async function loadPrivateKeyFromIndexedDB(username) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("keys", "readonly");
    const store = tx.objectStore("keys");
    const request = store.get(username);

    request.onsuccess = async () => {
      const record = request.result;
      if (!record || !record.privateKey) {
        reject("Private key not found in IndexedDB.");
        return;
      }

      try {
        const privateKey = await window.crypto.subtle.importKey(
          "jwk",
          record.privateKey,
          { name: "RSA-OAEP", hash: "SHA-256" },
          true,
          ["decrypt"]
        );
        resolve(privateKey);
      } catch (err) {
        reject("Failed to import private key: " + err);
      }
    };

    request.onerror = (e) => {
      reject("Failed to retrieve key: " + e.target.error);
    };
  });
}

async function loadMessages(sender,receiver) {
  // Load content from the route into the page
  const html = await (await fetch("/message_blueprint")).text();
  var blueprint = document.querySelector(".displaying-section").innerHTML = html;
  // blueprint.style.vissibilty = "hidden";
  // Then, continue with the messaging logic
  await receiveMessages(sender,receiver, html);
}

async function receiveMessages(sender,receiver,html) {
  console.log("receiveMessages===Check Sender: ",sender, "& ", receiver,userName);
  let myUsrname = userName;
   const tx = db.transaction("keys", "readonly");
  const store = tx.objectStore("keys");
  const request = store.getAll();

    request.onsuccess = () => {
      console.warn("Checking user found");
      if (request.result && request.result.length > 0) {
        const myUsrname = request.result[0].username;// Get the username from the first record
        const key = request.result[0].publicKey;
        console.log("Script 3 pre-test:@receiveMessages ",myUsrname);
        if (myUsrname) {
          startReadingMsg(myUsrname);
        };
      };
    }

    // let myUsrname = await myUserName(); // Get the username from IndexedDB
    if (!myUsrname) {
        console.warn("No user found");
        alert("Please register first. @receiveMesasages");
        return;
    }

    console.log("receiveMessages===Receiving messages for: " + myUsrname);
    let messages = null; 
    try {
      const res = await fetch(`/get_messages/${sender}/${receiver}/${myUsrname}`);
      if (!res.ok) {
        throw new Error(`Failed to fetch messages: ${res.statusText}`);
      }
      const response = await res.json();
      messages = response.messages;
      console.log("receiveMessages===Messages received:", messages);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }

    const privateKey = await loadPrivateKeyFromIndexedDB(myUsrname); 
      if (!privateKey) {
          console.error("No private key found in storage.");
          alert("No key found. Please register first.");
          return;
      }

    var msgField = document.querySelector(".message");

    msgField.innerHTML = "";
    if (!messages || messages.length === 0) {
        msgField.innerHTML = "<p>No messages found.</p>";
        return;
    }

    for (let msg of messages) {
        console.log("receiveMessages===Received message:", msg);
          // let text = null;
          try {
            console.log("Starting decryption...");
            const binary = Uint8Array.from(atob(msg["message"]), c => c.charCodeAt(0));
            console.log("Binary data created:", binary);
          try { 
                const decrypted = await window.crypto.subtle.decrypt(
                    { name: "RSA-OAEP" }, privateKey, binary
                );
                console.log("receiveMessages===Decryption succeeded:", decrypted);
            
                const text = new TextDecoder().decode(decrypted);
                console.log("receiveMessages===Decrypted message:", text);

                const tempContainer = document.createElement("div");
                tempContainer.innerHTML = html;
        
                const messageField = tempContainer.querySelector(".message");
                const titleField = tempContainer.querySelector(".sender-name");
                const companyNameField = tempContainer.querySelector(".company_name");
                const senderEmailField = tempContainer.querySelector(".email-field");
                const subjectField = tempContainer.querySelector(".subject-field");
                const postalAddressField = tempContainer.querySelector(".postal_address_field");
                const companyContactsField = tempContainer.querySelector(".company_contacts_field");
                const websiteField = tempContainer.querySelector(".website_field");

                if (messageField) {
                  var userData = await fetchUserData(msg.sender);
                  console.log("receiveMessages===User Data: ", userData);

                    messageField.innerHTML += `${text}`;
                    // From Server 
                    titleField.innerHTML = `${userData.info['name']}`;
                    senderEmailField.innerHTML = `${userData.info['email']}`;
                    companyNameField.innerHTML = `${userData.info['company_name']}`;
                    if (userData.info['postal_address']){postalAddressField.innerHTML = `${userData.info['postal_address']}`};
                    if (userData.info['company_contacts']){companyContactsField.innerHTML = `${userData.info['company_contacts']}`};
                    if (userData.info['website']){websiteField.innerHTML = `${userData.info['website']}`};
                    if (msg['subject']){subjectField.innerHTML = `${msg['subject']}`};
                    
                };
                if (msg.sender === myUsrname){
                  console.log("Sender:", msg.sender, " Username:",myUsrname);
                  tempContainer.classList.add("move-left");
                };
        
                document.querySelector(".displaying-section").innerHTML += tempContainer.innerHTML;
            } catch (decryptionError) {
                    console.warn("Failed to decrypt message. Skipping this message:", decryptionError);
            };
        

        } catch (error) {
            // console.error("Error decrypting message:", msg, error);
            console.error("receiveMessages===Decryption failed for message:", msg["message"]);
        }

    }
}

async function fetchUserData(user) {
  try {
    const res = await fetch('/fetch_user_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usernm: user })
    });

    if (!res.ok) {
      console.error(`Server responded with status: ${res.status}`);
      return null; // Handle error appropriately
    }

    const serverResponse = await res.json();
    return serverResponse;
  } catch (error) {
    console.error('Error fetching user data:', error);
    return null; // Handle error appropriately
  }
}

function savePublicKey(username, publicJwk, privateJwk) {
  console.log("New User Details: ",username)
  const tx = db.transaction("keys", "readwrite");
  const store = tx.objectStore("keys");

  // Iterate through all entries and delete them
  const getAllRequest = store.getAllKeys();

  getAllRequest.onsuccess = async () => {
    const keys = getAllRequest.result;
    // Delete all keys if the user confirms
    const deleteTx = db.transaction("keys", "readwrite");
    const deleteStore = deleteTx.objectStore("keys");
    if (keys.length >= 1) {
      console.log("Keys to delete: ", keys)
      // keys.forEach((key) => {
      //   deleteStore.delete(key);
      // });
    };


    console.log("Deleted old keys:", keys);
    // Add the new entry after deleting all old ones
    store.put({ 
      username,
      publicKey: publicJwk,
      privateKey: privateJwk
    });

    deleteTx.oncomplete = () => console.log("Old keys deleted successfully.");
    deleteTx.onerror = (e) => console.error("Failed to delete keys:", e.target.error);

    location.reload();
  };

  getAllRequest.onerror = (e) => console.error("Failed to retrieve keys for deletion:", e.target.error);

  tx.oncomplete = () => console.log("JWK saved for", username);
  tx.onerror = (e) => console.error("Save failed:", e.target.error);
}

// Example usage of getPublicKey function
function fetchAndUsePublicKey(username) {
  getPublicKey(username, (publicKey) => {
    if (publicKey) {
      console.log(`Public key for ${username}:`, publicKey);
      // You can now use the public key for encryption or other purposes
    } else {
      console.warn(`No public key found for ${username}`);
    }
  });
}

// Example call
// fetchAndUsePublicKey("exampleUsername");

function getPublicKey(username, callback) {
  const tx = db.transaction("keys", "readonly");
  const store = tx.objectStore("keys");
  const request = store.get(username);

  request.onsuccess = () => {
    if (request.result) {
      callback(request.result.publicKey);
    } else {
      console.warn("No key found for", username);
      callback(null);
    }
  };

  request.onerror = (e) => console.error("Get failed:", e.target.error);
}

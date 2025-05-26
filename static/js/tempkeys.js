

let Keys = {};
let db;

async function keyGen(){
   
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

    let pKey = document.querySelector('#pKey');

    // Step 2: Export the public key as JWK
    const exportedPublicKey = await window.crypto.subtle.exportKey("jwk", keyPair.publicKey);
    const exportedPrivateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);

    Keys.publicKey = exportedPublicKey;
    Keys.privateKey = exportedPrivateKey;

    let tempDataSave = { exportedPublicKey, exportedPrivateKey };

    localStorage.setItem('tempData', JSON.stringify(tempDataSave));
    

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

    console.log("Base64 Public Key:", pubBase64);
    pKey.value = pubBase64;

    return new Promise((resolve, reject) => {
        if(Keys){
            resolve(Keys);
        }else{
            reject();
        };
      });

};

var submitBtn = document.querySelector("#submit-btn");
submitBtn.addEventListener('click', function(){
    initTempDB();
    console.log("Saved to TempFiles✔")
});


function initTempDB() {
  return new Promise((resolve, reject) => {
    if (db) return resolve(db); // Already initialized

    const request = indexedDB.open("TempFiles", 4);

    request.onupgradeneeded = (event) => {
        db = event.target.result;
        if(!db.objectStoreNames.contains("temp")){
            const store = db.createObjectStore("temp",{
                keyPath: "Usernames",
                autoIncrement:true
            });
            console.log("DB Created for Temp Keys");
        };

    };//onupgraneeded

    request.onsuccess = (event) =>{
        var username = document.querySelector('#username').value;
        console.log("Got username Value: ", username);
        db = event.target.result;
        console.log("IndexedDB opened @initTempDB");
        resolve(db);

        const tempData = JSON.parse(localStorage.getItem('tempData'));
        console.log("Check Keys Before Saveing: ",tempData.exportedPrivateKey);
        saveTempKeys(db,username, tempData.exportedPublicKey, tempData.exportedPrivateKey);
    };//onsuccess

    request.onerror = (event) => {
        console.error("IndexedDB error:", event.target.error);
        reject(event.target.error);
    };

});//promise
}//db


//Save Function
function saveTempKeys(db, username, publicJwk, privateJwk) {


    const tx = db.transaction("keys","readwrite");
    const store = tx.objectStore("keys");

    // Iterate through all entries and delete them
    const getAllRequest = store.getAll();

    getAllRequest.onsuccess = async () =>{
        console.log("DB Output: @savePublicKey", getAllRequest.result);

        // Extract and log the IDs of the keys
        const keyIds = getAllRequest.result.map(entry => entry.Usernames);
        console.log("Key IDs:", keyIds);   

        const keys = getAllRequest.result;
        // Delete all keys if the user confirms
        const deleteTx = db.transaction("keys", "readwrite");
        const deleteStore = deleteTx.objectStore("keys");
        if (keys.length >= 1) {
        console.log("Keys to delete: ", keys)
        keys.forEach((key) => {
            console.log("Almost Deleted");
            deleteStore.delete(key);
        });
        };
    };

    // Add the new entry after deleting all old ones
    store.put({ 
      "Usernames":username,
      publicKey: publicJwk,
      privateKey: privateJwk
    });

    tx.oncomplete = () => console.log("JWK saved for", username);
    tx.onerror = (e) => console.error("Save failed:", e.target.error);
};

async function loadTempKeysFromIndexedDB(username) {
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
        const publicKey = await window.crypto.subtle.importKey(
          "jwk",
          record.publicKey,
          { name: "RSA-OAEP", hash: "SHA-256" },
          true,
          ["encrypt"] // Corrected usage for public key
        );
        resolve({ privateKey, publicKey }); // Wrap keys in an object
      } catch (err) {
        reject("Failed to import private key: " + err);
      }
    };

    request.onerror = (e) => {
      reject("Failed to retrieve key: " + e.target.error);
    };
  });
}
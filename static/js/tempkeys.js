


// --- Crypto Helper Functions ---

// Encrypts a JSON object with a password using AES-GCM
async function encryptData(dataObj, password) {
    const enc = new TextEncoder();
    const iv = window.crypto.getRandomValues(new Uint8Array(12)); // 96-bit IV
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw", enc.encode(password), {name: "PBKDF2"}, false, ["deriveKey"]
    );
    const key = await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: iv,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
    const encoded = enc.encode(JSON.stringify(dataObj));
    const ciphertext = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encoded
    );
    // Return base64-encoded IV + ciphertext
    return {
        iv: btoa(String.fromCharCode(...iv)),
        data: btoa(String.fromCharCode(...new Uint8Array(ciphertext)))
    };
}

// Decrypts the encrypted recovery file with the password
async function decryptData(encryptedObj, password) {
    const enc = new TextEncoder();
    const dec = new TextDecoder();
    const iv = Uint8Array.from(atob(encryptedObj.iv), c => c.charCodeAt(0));
    const ciphertext = Uint8Array.from(atob(encryptedObj.data), c => c.charCodeAt(0));
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw", enc.encode(password), {name: "PBKDF2"}, false, ["deriveKey"]
    );
    const key = await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: iv,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
    const decrypted = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv },
        key,
        ciphertext
    );
    return JSON.parse(dec.decode(decrypted));
}

// --- Registration: Show Recovery Modal and Download File ---

// Call this function after successful registration
async function showRecoveryModal(userObj) {
    // userObj = {username, publicKey, privateKey}
    // Generate a random recovery key
    const recoveryKey = Array.from(crypto.getRandomValues(new Uint8Array(16)))
        .map(b => b.toString(16).padStart(2, '0')).join('');
    // Encrypt user data
    const encrypted = await encryptData(userObj, recoveryKey);
    // Show modal
    document.getElementById('recovery-modal').style.display = 'flex';
    document.getElementById('recovery-key').textContent = recoveryKey;

    // Download file handler
    document.getElementById('download-recovery-file').onclick = function() {
        const blob = new Blob([JSON.stringify(encrypted)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'qm-businessconnect-recovery.json';
        a.click();
        URL.revokeObjectURL(url);

        //Call the updateRecoveryStatus function
        updateRecoveryStatus(userObj.myUsrname);
    };

    // Copy key handler
    document.getElementById('copy-recovery-key').onclick = function() {
        navigator.clipboard.writeText(recoveryKey);
        alert('Recovery key copied!');
    };
}

async function updateRecoveryStatus(usrname){
    console.log("1. Recovery Status Username", usrname);
    var response = await fetch("/recovery_status_update",{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: usrname })
            });
    var data = await response.json();
    console.log("2. Recovery Status", data.res);
    };

  
// Example usage after registration:
// showRecoveryModal({username: 'alice', publicKey: '...', privateKey: '...'});

function viewRecoryModal(){
    var restoreModal = document.querySelector("#restore-modal");
    restoreModal.style.display = "flex";
}

// --- Restore Flow ---
var recBtn = document.getElementById('restore-account-btn');

if(recBtn){
  recBtn.onclick = async function() {
      const fileInput = document.getElementById('recovery-file-input');
      const keyInput = document.getElementById('restore-key-input');
      const statusDiv = document.getElementById('restore-status');
      statusDiv.textContent = '';
      if (!fileInput.files.length || !keyInput.value) {
          statusDiv.textContent = 'Please select a file and enter your recovery key.';
          return;
      }
      const file = fileInput.files[0];
      const key = keyInput.value.trim();
      try {
          const fileText = await file.text();
          const encryptedObj = JSON.parse(fileText);
          const userObj = await decryptData(encryptedObj, key);
          // Save to IndexedDB (replace with your own logic)
          await saveCredentialsToIndexedDB(userObj);
          statusDiv.style.color = 'green';
          statusDiv.textContent = 'Account restored! You can now log in.';
          // Optionally, auto-login or reload
      } catch (e) {
          statusDiv.style.color = 'red';
          statusDiv.textContent = 'Failed to restore account. Check your key and file.'+ e;
      }
  };
}

// Example IndexedDB save function (replace with your own logic)
async function saveCredentialsToIndexedDB(userObj) {
    console.log("Parse Obj: ",userObj);
    var myUsername = userObj.myUsrname;
    var exportedPublicKey = userObj.Pkey;
    var exportedPrivateKey = userObj.Prkey;
    savePublicKey(myUsername, exportedPublicKey, exportedPrivateKey);
    // Use your existing IndexedDB logic here
    // Example with idb-keyval (https://github.com/jakearchibald/idb-keyval)
    // await idbKeyval.set('user', userObj);
    // For custom logic, use indexedDB API to store userObj
    // ...
    console.log('Saving to IndexedDB:', userObj);
}
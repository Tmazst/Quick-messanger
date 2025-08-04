

function openMenuFunc(){
  var navLabel = document.querySelectorAll(".nav-label");
  var menuSection = document.querySelector(".app-nav-bar-left");
  menuSection.classList.toggle("open");

  navLabel.forEach((label) => {
    label.classList.toggle("nav-label-display");
  });
};

function openClose(event){
  // window.location.href = "/message_blueprint";

  


  var navLinkMsg = document.querySelector("#navlink-message");
  var messageSection = document.querySelector(".messages-container");
  var scrollabelDiv = document.querySelector(".scorllable-messages");

  navLinkMsg.classList.toggle("max-content-height");
  messageSection.classList.toggle("display-messages");
  scrollabelDiv.classList.toggle("max-height-60vh");

  
}

document.addEventListener("DOMContentLoaded", function() {
  //   function toggleUserModal() {
  //   console.log("User button for mobile found");
  // }
  var userButton = document.querySelector("#user-button");

  if(userButton) {
    userButton.addEventListener("click", function() {
      console.log("User button for mobile found");
      var userModal = document.querySelector(".user-modal");
      userModal.classList.toggle("show-user-modal");
    });
  }

  var userButtonMobile = document.querySelector("#login-mobile");

  if(userButtonMobile) {
    
    userButtonMobile.addEventListener("click", function() {
      var userModal = document.querySelector(".user-modal-mobile");
      userModal.classList.toggle("show-user-modal");
    });
  }


  const toggle = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('password');

  if (toggle && passwordInput) {
      toggle.addEventListener('click', function () {
          const isPassword = passwordInput.getAttribute('type') === 'password';
          passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
          toggle.textContent = isPassword ? '🙈' : '👁️';  // Update icon
      });
  }


  // Save form data on input, excluding sensitive fields
  var form = document.querySelector('form');
  if (form) {
    form.addEventListener('input', () => {
      const data = {};
      const excludedKeys = ['password', 'pKey', 'username', 'new_passowrd', 'confirm_password', 'code','csrf_token'];

      new FormData(form).forEach((value, key) => {
        if (!excludedKeys.includes(key)) {
          console.log(`Saving ${key} with value: ${value}`);
          data[key] = value;
        }
      });

      localStorage.setItem('formData', JSON.stringify(data));
    });
  }


});


// Populate form on page load
window.addEventListener('load', () => {
  const data = JSON.parse(localStorage.getItem('formData'));
  if (data) {
    Object.keys(data).forEach(key => {
      if (document.querySelector(`[name="${key}"]`)) {
        console.log(`Populating ${key} with value: ${data[key]}`);
        document.querySelector(`[name="${key}"]`).value = data[key];
      }
    });
  }
});




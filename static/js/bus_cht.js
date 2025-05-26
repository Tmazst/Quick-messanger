

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



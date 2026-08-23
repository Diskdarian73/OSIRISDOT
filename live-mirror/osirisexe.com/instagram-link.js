(function () {
  function mountInstagramLink() {
    if (document.getElementById("osiris-instagram-link")) return;

    var style = document.createElement("style");
    style.textContent =
      "#osiris-instagram-link:hover,#osiris-instagram-link:focus-visible{" +
      "border-color:#00ff46;color:#d8d2c4;outline:none;" +
      "box-shadow:0 0 14px rgba(0,255,70,.18)}";
    document.head.appendChild(style);

    var link = document.createElement("a");
    link.id = "osiris-instagram-link";
    link.href = "https://www.instagram.com/diskdarian/";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Disk Darián on Instagram");
    link.textContent = "INSTAGRAM // @DISKDARIAN";
    link.style.cssText =
      "position:fixed;left:0;top:50%;z-index:99998;" +
      "transform:translateY(-50%);writing-mode:vertical-rl;" +
      "font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10px;" +
      "line-height:1;letter-spacing:.16em;text-transform:uppercase;" +
      "color:#00ff46;background:rgba(1,1,3,.9);text-decoration:none;" +
      "border:1px solid #0a8a2e;border-left:0;padding:10px 7px;" +
      "transition:border-color .15s,color .15s,box-shadow .15s;";
    document.body.appendChild(link);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountInstagramLink, {
      once: true,
    });
  } else {
    mountInstagramLink();
  }
})();

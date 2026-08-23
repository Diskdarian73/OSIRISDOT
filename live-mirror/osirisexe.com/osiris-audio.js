/* ============================================================
   OSIRIS.EXE — KillerTape Network audio for static artifact pages.

   Every refresh selects a fresh random track from the public SoundCloud
   profile. Override the profile on any page with:
     <script src="/osiris-audio.js"
       data-soundcloud="https://soundcloud.com/artist-name"></script>

   The edge-mounted control shares its mute preference with the archive and
   stays clear of page navigation. Browsers that decline autoplay arm the
   selected track on the first real interaction.
   ============================================================ */
(function () {
  var script = document.currentScript;
  var soundCloudUrl =
    (script && script.getAttribute("data-soundcloud")) ||
    "https://soundcloud.com/killertapenetwork";
  var widgetApi = "https://w.soundcloud.com/player/api.js";
  var playerUrl = "https://w.soundcloud.com/player/";
  var pref = "osiris.sound";

  function silenced() {
    try {
      return sessionStorage.getItem(pref) === "0";
    } catch {
      return false;
    }
  }

  function remember(on) {
    try {
      sessionStorage.setItem(pref, on ? "1" : "0");
    } catch {
      // Storage can be unavailable in privacy-restricted contexts.
    }
  }

  function boot() {
    var widget = null;
    var ready = false;
    var playing = false;
    var wantsPlayback = !silenced();

    var iframe = document.createElement("iframe");
    iframe.title = "OSIRIS.EXE KillerTape Network SoundCloud audio";
    iframe.allow = "autoplay";
    iframe.tabIndex = -1;
    iframe.setAttribute("aria-hidden", "true");
    iframe.style.cssText =
      "position:fixed;width:1px;height:1px;left:-9999px;bottom:0;" +
      "border:0;opacity:0;pointer-events:none";
    iframe.src =
      playerUrl +
      "?url=" +
      encodeURIComponent(soundCloudUrl) +
      "&auto_play=false&hide_related=true&show_comments=false" +
      "&show_user=false&show_reposts=false&visual=false";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "SOUND: OFF";
    btn.setAttribute("aria-label", "Toggle KillerTape Network SoundCloud audio");
    btn.style.cssText =
      "position:fixed;right:0;top:50%;bottom:auto;z-index:99999;" +
      "transform:translateY(-50%);writing-mode:vertical-rl;cursor:pointer;" +
      "font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10px;" +
      "letter-spacing:.18em;color:#00ff46;background:rgba(1,1,3,.9);" +
      "border:1px solid #0a8a2e;border-right:0;padding:10px 6px;";

    function sync() {
      btn.textContent = playing ? "SOUND: ON" : "SOUND: OFF";
      btn.setAttribute("aria-pressed", playing ? "true" : "false");
    }

    function labelCurrentTrack() {
      if (!widget || typeof widget.getCurrentSound !== "function") return;
      widget.getCurrentSound(function (sound) {
        if (sound && sound.title) {
          btn.title = "KILLERTAPE NETWORK // " + sound.title;
        }
      });
    }

    function playSelected() {
      if (!ready || !widget || !wantsPlayback) return;
      widget.setVolume(35);
      widget.play();
    }

    function connect() {
      if (!window.SC || !window.SC.Widget) return;
      widget = window.SC.Widget(iframe);
      var events = window.SC.Widget.Events;

      widget.bind(events.READY, function () {
        widget.getSounds(function (sounds) {
          var count = Array.isArray(sounds) ? sounds.length : 0;
          var randomIndex = count > 1 ? Math.floor(Math.random() * count) : 0;
          if (count > 0) widget.skip(randomIndex);

          window.setTimeout(function () {
            ready = true;
            if (wantsPlayback) playSelected();
            else widget.pause();
            labelCurrentTrack();
          }, 0);
        });
      });

      widget.bind(events.PLAY, function () {
        playing = true;
        labelCurrentTrack();
        sync();
      });
      widget.bind(events.PAUSE, function () {
        playing = false;
        sync();
      });
      if (events.FINISH) {
        widget.bind(events.FINISH, function () {
          playing = false;
          sync();
        });
      }
    }

    btn.addEventListener("click", function (event) {
      event.stopPropagation();
      if (playing) {
        wantsPlayback = false;
        remember(false);
        if (widget) widget.pause();
      } else {
        wantsPlayback = true;
        remember(true);
        playSelected();
      }
      sync();
    });

    document.body.appendChild(iframe);
    document.body.appendChild(btn);
    sync();

    var existing = document.querySelector('script[src="' + widgetApi + '"]');
    if (window.SC && window.SC.Widget) {
      connect();
    } else if (existing) {
      existing.addEventListener("load", connect, { once: true });
    } else {
      var apiScript = document.createElement("script");
      apiScript.src = widgetApi;
      apiScript.async = true;
      apiScript.addEventListener("load", connect, { once: true });
      document.head.appendChild(apiScript);
    }

    var arm = function () {
      if (wantsPlayback) playSelected();
    };
    window.addEventListener("pointerdown", arm, { passive: true });
    window.addEventListener("keydown", arm, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();

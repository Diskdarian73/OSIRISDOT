/* ============================================================
   OSIRIS.EXE #1 — MOTION COMIC CONFIG
   Edit this file to change page order, captions, motion, and
   signal color. The player (index.html) reads this at load.
   signal: "neutral" | "green" | "green-red" | "red"
   pan:    starting focal point for the Ken Burns move
   ============================================================ */
window.OSIRIS_ISSUE = {
  title: "OSIRIS.EXE",
  issue: "ARCHIVE 01",
  tagline: "MEMORY IS THE OLDEST FORM OF RESISTANCE",
  assetDir: "pages/",
  ext: "webp",              // still image / poster format
  videoExt: "mp4",          // motion clip format (pages with motion:true)
  audio: "/audio/acetate-01.mp3",  // soundtrack — starts on launch when the
                                  // browser allows; otherwise on first touch.
                                  // Always mutable from the on-screen control.
  pages: [
    { file:"00_cover",        signal:"neutral",   pan:"center", hold:true,
      motion:true, label:"COVER" },
    { file:"01_cold_open",    signal:"green",     pan:"top",
      motion:true, label:"CHICAGO. YEAR UNKNOWN." },
    { file:"02_room",         signal:"neutral",   pan:"center",
      motion:true, label:"2:47 AM" },
    { file:"03_static",       signal:"green",     pan:"bottom",
      motion:true, label:"THE STATIC WASN'T RANDOM." },
    { file:"04_dead_devices", signal:"green-red", pan:"center",
      motion:true, label:"DEAD. NO BATTERY. IMPOSSIBLE." },
    { file:"05_reception",    signal:"green-red", pan:"center",
      motion:true, label:"I HEAR YOU." },
    { file:"06_seen",         signal:"red",       pan:"top", finale:true,
      motion:true, label:"WE SEE YOU, SKYE." }
  ]
};

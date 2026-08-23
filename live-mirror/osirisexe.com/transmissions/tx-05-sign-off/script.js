// ── PALETTE / CHANNELS — OSIRIS COLOR SYSTEM ─────────────────────
const CHANNELS = [
  { ch:  1, name: 'Duat',         hex: '#010103', r:1,   g:1,   b:3,   desc:'the underlayer at rest'         },
  { ch:  2, name: 'Midnight',     hex: '#0B1226', r:11,  g:18,  b:38,  desc:'the lake that remembers'        },
  { ch:  3, name: 'Indigo',       hex: '#1B2A5E', r:27,  g:42,  b:94,  desc:'deep water, deeper record'      },
  { ch:  4, name: 'Phosphor',     hex: '#00FF46', r:0,   g:255, b:70,  desc:'the signal, live'               },
  { ch:  5, name: 'Dim',          hex: '#0A8A2E', r:10,  g:138, b:46,  desc:'the signal, waiting'            },
  { ch:  6, name: 'Crimson',      hex: '#FF3A1A', r:255, g:58,  b:26,  desc:'the network, looking'           },
  { ch:  7, name: 'Ember',        hex: '#7A1A0C', r:122, g:26,  b:12,  desc:'the network, banked'            },
  { ch:  8, name: 'Sovereign',    hex: '#FFC93C', r:255, g:201, b:60,  desc:'the apex interface'             },
  { ch:  9, name: 'Resurrection', hex: '#C9A227', r:201, g:162, b:39,  desc:'gold that came back'            },
  { ch: 10, name: 'Violet',       hex: '#6B3FA0', r:107, g:63,  b:160, desc:'the quantum seam'               },
  { ch: 11, name: 'Bone',         hex: '#D8D2C4', r:216, g:210, b:196, desc:'what the record is written on'  },
  { ch: 12, name: 'Cream',        hex: '#D5CDB8', r:213, g:205, b:184, desc:'paper before the toner'         },
];

// ── CANVAS SETUP ─────────────────────────────────────────────────
const tvScreen = document.getElementById('tvScreen');
const canvas   = document.getElementById('screen');
const ctx      = canvas.getContext('2d');
const glow     = document.getElementById('glow');

let CW, CH;
function resizeCanvas() {
  const rect = tvScreen.getBoundingClientRect();
  CW = canvas.width  = rect.width;
  CH = canvas.height = rect.height;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// ── STATE ─────────────────────────────────────────────────────────
let currentCh   = 0;
let staticNoise  = null;
let noiseAge     = 0;
let staticBurst  = 0;
let switching    = false;
let scanOffset   = 0;
let glitchTimer  = 0;
let ticker       = 0;

// ── BUILD CHANNEL BUTTONS ─────────────────────────────────────────
const strip = document.getElementById('channelStrip');
CHANNELS.forEach((ch, i) => {
  const btn = document.createElement('button');
  btn.className = 'ch-btn' + (i === 0 ? ' active' : '');
  btn.textContent = String(ch.ch).padStart(2, '0');
  btn.style.setProperty('--ch-color', ch.hex);
  btn.addEventListener('click', () => switchTo(i));
  strip.appendChild(btn);
});

function updateButtons(idx) {
  document.querySelectorAll('.ch-btn').forEach((b, i) => {
    b.classList.toggle('active', i === idx);
  });
}

// ── PHOSPHOR GLOW ─────────────────────────────────────────────────
function setGlow(ch) {
  const { r, g, b } = ch;
  const brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255;
  const a = 0.25 + brightness * 0.3;
  glow.style.boxShadow = `
    0 0 18px rgba(${r},${g},${b},${a}),
    0 0 45px rgba(${r},${g},${b},${a * 0.6}),
    0 0 90px rgba(${r},${g},${b},${a * 0.3})
  `;
}

// ── NOISE BUFFER ──────────────────────────────────────────────────
function makeNoiseBuffer() {
  const off = document.createElement('canvas');
  off.width = CW; off.height = CH;
  const oc = off.getContext('2d');
  const id = oc.createImageData(CW, CH);
  const d  = id.data;
  for (let i = 0; i < d.length; i += 4) {
    const v = Math.random() * 255 | 0;
    d[i] = d[i+1] = d[i+2] = v;
    d[i+3] = 255;
  }
  oc.putImageData(id, 0, 0);
  return off;
}

// ── DRAW SCREEN ───────────────────────────────────────────────────
function drawScreen(ch, staticAlpha) {
  const { r, g, b, hex, name, desc, ch: chNum } = ch;
  ticker++;

  // Base color fill
  ctx.fillStyle = hex;
  ctx.fillRect(0, 0, CW, CH);

  // CRT vignette darkening
  const vg = ctx.createRadialGradient(CW/2, CH/2, CH*0.1, CW/2, CH/2, CH*0.72);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(0,0,0,0.38)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, CW, CH);

  // Phosphor warmth glow from center
  const luma = (r*0.299 + g*0.587 + b*0.114) / 255;
  const pgA  = 0.12 + luma * 0.15;
  const pg   = ctx.createRadialGradient(CW/2, CH/2, 0, CW/2, CH/2, CH*0.55);
  pg.addColorStop(0, `rgba(255,255,255,${pgA})`);
  pg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = pg;
  ctx.fillRect(0, 0, CW, CH);

  // Moving scanline band
  scanOffset = (scanOffset + 0.4) % CH;
  ctx.fillStyle = 'rgba(255,255,255,0.025)';
  for (let y = scanOffset % 80; y < CH; y += 80) {
    ctx.fillRect(0, y, CW, 2);
  }

  // Occasional glitch line
  glitchTimer++;
  if (glitchTimer > 180 && Math.random() < 0.03) {
    glitchTimer = 0;
    const gy = Math.random() * CH | 0;
    ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.4})`;
    ctx.fillRect(0, gy, CW, (Math.random() * 3 + 1) | 0);
  }

  // Text color based on background luminance
  const textLight = `rgba(216,210,196,0.92)`;
  const textDark  = `rgba(1,1,3,0.80)`;
  const subLight  = `rgba(216,210,196,0.65)`;
  const subDark   = `rgba(1,1,3,0.55)`;
  const dimLight  = `rgba(216,210,196,0.40)`;
  const dimDark   = `rgba(1,1,3,0.38)`;
  const mainColor = luma < 0.45 ? textLight : textDark;
  const subColor  = luma < 0.45 ? subLight  : subDark;
  const dimColor  = luma < 0.45 ? dimLight  : dimDark;

  // Channel number — top left
  ctx.font = `bold ${CW * 0.075}px 'VT323', monospace`;
  ctx.textAlign = 'left';
  ctx.fillStyle = `rgba(0,0,0,0.2)`;
  ctx.fillText(`CH ${String(chNum).padStart(2, '0')}`, CW*0.05 + 1, CW*0.1 + 1);
  ctx.fillStyle = mainColor.replace('0.92','0.15').replace('0.80','0.12');
  ctx.fillText(`CH ${String(chNum).padStart(2, '0')}`, CW*0.05, CW*0.1);

  // Color name — large centered
  const nameSize = CW * 0.155;
  ctx.font = `${nameSize}px 'VT323', monospace`;
  ctx.textAlign = 'center';
  // drop shadow
  ctx.fillStyle = 'rgba(0,0,0,0.22)';
  ctx.fillText(name.toUpperCase(), CW/2 + 2, CH/2 + nameSize*0.34 + 2);
  ctx.fillStyle = mainColor;
  ctx.fillText(name.toUpperCase(), CW/2, CH/2 + nameSize*0.34);

  // Hex code
  ctx.font = `${CW * 0.055}px 'Share Tech Mono', monospace`;
  ctx.fillStyle = subColor;
  ctx.fillText(hex.toUpperCase(), CW/2, CH/2 + nameSize*0.34 + CW*0.075);

  // Description
  ctx.font = `${CW * 0.038}px 'Share Tech Mono', monospace`;
  ctx.fillStyle = dimColor;
  ctx.fillText(desc, CW/2, CH/2 + nameSize*0.34 + CW*0.13);

  // RGB bars at bottom
  const barY = CH - CW*0.085;
  const barH = CW*0.025;
  const barW = CW*0.65;
  const barX = (CW - barW) / 2;
  const segments = [
    { label:'R', val:r, color:'rgba(255,58,26,0.7)'  },
    { label:'G', val:g, color:'rgba(0,255,70,0.7)'   },
    { label:'B', val:b, color:'rgba(107,63,160,0.85)' },
  ];
  ctx.font = `${CW * 0.032}px 'Share Tech Mono', monospace`;
  segments.forEach((seg, i) => {
    const by = barY + i * (barH + CW*0.018);
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.beginPath();
    ctx.roundRect(barX, by, barW, barH, barH/2);
    ctx.fill();
    ctx.fillStyle = seg.color;
    ctx.beginPath();
    ctx.roundRect(barX, by, barW * (seg.val/255), barH, barH/2);
    ctx.fill();
    ctx.textAlign = 'right';
    ctx.fillStyle = dimColor;
    ctx.fillText(`${seg.label} ${seg.val}`, barX - CW*0.016, by + barH*0.82);
  });
  ctx.textAlign = 'left';

  // Static overlay
  if (staticAlpha > 0.01) {
    if (!staticNoise || noiseAge++ > 3) {
      staticNoise = makeNoiseBuffer();
      noiseAge = 0;
    }
    ctx.globalAlpha = staticAlpha;
    ctx.drawImage(staticNoise, 0, 0);
    ctx.globalAlpha = 1;
  }
}

// ── SWITCH CHANNEL ────────────────────────────────────────────────
function switchTo(idx) {
  if (switching) return;
  switching    = true;
  currentCh    = ((idx % CHANNELS.length) + CHANNELS.length) % CHANNELS.length;
  staticBurst  = 1.0;

  updateButtons(currentCh);
  setGlow(CHANNELS[currentCh]);

  tvScreen.classList.add('switching');
  setTimeout(() => {
    tvScreen.classList.remove('switching');
    switching = false;
  }, 500);
}

function next() { switchTo(currentCh + 1); }
function prev() { switchTo(currentCh - 1); }

// ── INPUT ─────────────────────────────────────────────────────────
document.getElementById('nextKnob').addEventListener('click', next);
document.getElementById('prevKnob').addEventListener('click', prev);
tvScreen.addEventListener('click', next);

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowUp') { e.preventDefault(); next(); }
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowDown')                { e.preventDefault(); prev(); }
  const n = parseInt(e.key);
  if (!isNaN(n) && n >= 1 && n <= 9) switchTo(n - 1);
  if (e.key === '0') switchTo(9);
});

// Auto-advance
let autoTimer = setInterval(next, 6000);
tvScreen.addEventListener('click', () => {
  clearInterval(autoTimer);
  autoTimer = setInterval(next, 8000);
});

// ── RENDER LOOP ───────────────────────────────────────────────────
setGlow(CHANNELS[currentCh]);

function loop() {
  staticBurst = staticBurst > 0.01 ? staticBurst * 0.82 : 0;
  drawScreen(CHANNELS[currentCh], staticBurst);
  requestAnimationFrame(loop);
}

loop();
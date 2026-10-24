// cut3d — 3D cut-away jaw engine for the clinic's 1-minute "But → So" Reels.
// An episode (videos/<slug>/scene3d.js) imports this module as L and exports frame(t, L) and cover(t, L).
// Coordinates: x across the jaw, y up (gum top = GUM_TOP = 1.2, bone below 0), z toward the camera; the cut face is z = 0.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
export { THREE, mergeGeometries, RoundedBoxGeometry };

export const W = 1080, H = 1920;
const QS = new URLSearchParams(location.search);
const RS = QS.get('rs') ? +QS.get('rs') : 1;
export const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('c'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(Math.round(W * RS), Math.round(H * RS), false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.92;
renderer.outputColorSpace = THREE.SRGBColorSpace;
export const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---------------------------------------------------------------- math helpers
let seed = 7; export const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const ease = k => (k = clamp(k), k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
export const eout = k => (k = clamp(k), 1 - Math.pow(1 - k, 3));
export const ein = k => (k = clamp(k), k * k * k);
export const back = k => { k = clamp(k); const c = 1.9; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }

// ---------------------------------------------------------------- world
scene.background = canvasTex(16, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#5fb2e6'); gr.addColorStop(.55, '#bfe3f5'); gr.addColorStop(1, '#f6e7d6'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
scene.fog = new THREE.Fog('#cfe8f4', 70, 160);
scene.add(new THREE.HemisphereLight('#eaf6ff', '#c99a86', 0.55));
export const sun = new THREE.DirectionalLight('#fff3e2', 3.4);
sun.position.set(14, 26, 22); sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024);
Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 20, bottom: -14, near: 1, far: 80 }); sun.shadow.bias = -0.0006; sun.shadow.radius = 4;
scene.add(sun);

export const GUM_TOP = 1.2, SP = 3.75;           // gum top height, tooth spacing (teeth at x = i*SP)
const X0 = -22, X1 = 22, ZB = -26, BONE_BOT = -16;
const boneTex = canvasTex(2048, 1024, (g, w, h) => {
  g.fillStyle = '#e7d1a4'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 2600; i++) { const x = rnd() * w, y = 40 + rnd() * (h - 40), r = 4 + rnd() * 18 * (0.4 + y / h);
    g.fillStyle = rnd() < .5 ? 'rgba(176,136,84,.6)' : 'rgba(214,160,128,.5)'; g.beginPath(); g.ellipse(x, y, r * 1.3, r, rnd() * 3, 0, 7); g.fill();
    g.strokeStyle = 'rgba(255,250,235,.7)'; g.lineWidth = 3; g.stroke(); }
  const gr = g.createLinearGradient(0, 0, 0, 60); gr.addColorStop(0, '#fffaf0'); gr.addColorStop(1, 'rgba(255,250,240,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, 60);
});
const gumTex = canvasTex(1024, 128, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#f28aa0'); gr.addColorStop(1, '#d9667f'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 400; i++) { g.fillStyle = 'rgba(255,255,255,.08)'; g.beginPath(); g.arc(rnd() * w, rnd() * h, 2 + rnd() * 6, 0, 7); g.fill(); } });
const boneSide = new THREE.MeshStandardMaterial({ color: '#d9c093', roughness: .9 });
const boneFront = new THREE.MeshStandardMaterial({ map: boneTex, roughness: .85 });
export const bone = new THREE.Mesh(new THREE.BoxGeometry(X1 - X0, -BONE_BOT, -ZB), [boneSide, boneSide, boneSide, boneSide, boneFront, boneSide]);
bone.position.set(0, BONE_BOT / 2, ZB / 2); bone.receiveShadow = true; scene.add(bone);
export const gumMatTop = new THREE.MeshPhysicalMaterial({ color: '#ee8399', roughness: .45, clearcoat: .6, clearcoatRoughness: .3 });
const gumMatFront = new THREE.MeshStandardMaterial({ map: gumTex, roughness: .5 });
export const gum = new THREE.Mesh(new THREE.BoxGeometry(X1 - X0, GUM_TOP, -ZB), [gumMatTop, gumMatTop, gumMatTop, gumMatTop, gumMatFront, gumMatTop]);
gum.position.set(0, GUM_TOP / 2, ZB / 2); gum.receiveShadow = true; scene.add(gum);
// red inflamed patch on the gum around x=0 (set .material.opacity, and .position.x to move it)
export const inflam = new THREE.Mesh(new THREE.CircleGeometry(2.3, 40), new THREE.MeshStandardMaterial({ color: '#e0475f', transparent: true, opacity: 0, roughness: .5 }));
inflam.rotation.x = -Math.PI / 2; inflam.position.set(0, GUM_TOP + .02, -1.6); inflam.scale.set(1, .8, 1); scene.add(inflam);
export const inflamF = new THREE.Mesh(new THREE.PlaneGeometry(4.2, GUM_TOP), new THREE.MeshStandardMaterial({ color: '#e0475f', transparent: true, opacity: 0 }));
inflamF.position.set(0, GUM_TOP / 2, 0.01); scene.add(inflamF);

// ---------------------------------------------------------------- teeth
export const enamel = new THREE.MeshPhysicalMaterial({ color: '#fbf8f1', roughness: .22, clearcoat: 1, clearcoatRoughness: .15, sheen: .3 });
export const rootMat = new THREE.MeshStandardMaterial({ color: '#f1e2bd', roughness: .6 });
function crownGeo() {
  const pts = [[0, -.6], [1.3, -.6], [1.32, 0], [1.6, .7], [1.74, 1.6], [1.68, 2.35], [1.45, 2.8], [1.0, 3.0], [.4, 2.86], [0, 2.9]].map(p => new THREE.Vector2(p[0], p[1]));
  const g = new THREE.LatheGeometry(pts, 48); const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i); const a = Math.atan2(z, x);
    if (y > 2.2) p.setY(i, y + .22 * Math.cos(2 * a) * clamp((y - 2.2) / .6) * clamp(Math.hypot(x, z) / .8)); p.setZ(i, z * .86); }
  g.computeVertexNormals(); return g;
}
export const CROWN = crownGeo();                 // molar crown, base at y=-0.6, cusps at y≈3
function rootGeo() {
  const parts = [-.72, .72].map((dx, i) => { const g = new THREE.CylinderGeometry(.72, .18, 6, 24, 8); g.translate(0, -3, 0);
    const p = g.attributes.position; for (let k = 0; k < p.count; k++) { const y = p.getY(k); p.setX(k, p.getX(k) + dx * (1 + (-y) * .05) + Math.sin(-y * .5) * .1 * (i ? 1 : -1)); }
    g.translate(0, .1, 0); return g; });
  const m = mergeGeometries(parts); m.computeVertexNormals(); return m;
}
export const ROOT = rootGeo();
/** a tooth group at x (crown + optional roots). Standing position: y = 0.7. Returns the group (children[0] = crown mesh). */
export function tooth(x, withRoot = true, mat = enamel) {
  const g = new THREE.Group(); const c = new THREE.Mesh(CROWN, mat); c.castShadow = true; g.add(c);
  if (withRoot) { const r = new THREE.Mesh(ROOT, rootMat); r.castShadow = true; g.add(r); }
  g.position.set(x, .7, 0); scene.add(g); return g;
}
export const neighbors = [-3, -2, -1, 1, 2, 3].map(i => tooth(i * SP));   // always-present teeth
export const centerTooth = tooth(0);             // the natural tooth at x=0 (visible by default; hide/animate it)
export const looseCrownMat = new THREE.MeshPhysicalMaterial({ color: '#f3efe2', roughness: .4, clearcoat: .4 });
export const looseCrown = tooth(0, false, looseCrownMat);   // a crown with no roots (fake tooth / denture tooth)
export const newCrown = tooth(0, false);         // a bright new crown (implant crown, filling result…)

// upper jaw: gum slab + 7 upper teeth. upper.position.y: 11 = open (default), 3.2 = bite on lower crowns
export const upper = new THREE.Group(); scene.add(upper);
{ const ugum = new THREE.Mesh(new THREE.BoxGeometry(X1 - X0, 3, -ZB + 2), gumMatTop); ugum.position.set(0, 4.5, ZB / 2 + 1); ugum.castShadow = true; upper.add(ugum);
  [-3, -2, -1, 0, 1, 2, 3].forEach(i => { const c = new THREE.Mesh(CROWN, enamel); c.rotation.x = Math.PI; c.position.set(i * SP, 3.3, 0); c.castShadow = true; upper.add(c); }); }
export const food = new THREE.Mesh(new THREE.SphereGeometry(1.3, 32, 20), new THREE.MeshStandardMaterial({ color: '#d98c3f', roughness: .6 }));
food.castShadow = true; scene.add(food);

// ---------------------------------------------------------------- implant parts (titanium)
export const titanium = new THREE.MeshStandardMaterial({ color: '#c3c9d1', metalness: 1, roughness: .26 });
function implantGeo() {
  const L = 5.2, rT = .85, rB = .55;
  const core = new THREE.CylinderGeometry(rT, rB, L, 40); core.translate(0, -L / 2, 0);
  const tip = new THREE.ConeGeometry(rB, .6, 40); tip.rotateX(Math.PI); tip.translate(0, -L - .3, 0);
  const plat = new THREE.CylinderGeometry(.9, .88, .35, 40); plat.translate(0, .1, 0);
  const pts = []; const turns = 9;
  for (let i = 0; i <= 600; i++) { const k = i / 600, y = -.35 - k * (L - .5), r = lerp(rT, rB, (-y) / L) + .02, a = k * turns * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r)); }
  const thread = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 900, .14, 8, false);
  const m = mergeGeometries([core, tip, plat, thread].map(g => g.index ? g.toNonIndexed() : g)); m.computeVertexNormals(); return m;
}
export const implant = new THREE.Mesh(implantGeo(), titanium); implant.castShadow = true; scene.add(implant);   // top at y=0 when seated
export const abut = new THREE.Group(); scene.add(abut);                                                    // seated at y=0.05
{ const a1 = new THREE.Mesh(new THREE.CylinderGeometry(.58, .82, 2.3, 40), titanium); a1.position.y = 1.15; a1.castShadow = true; abut.add(a1);
  const a2 = new THREE.Mesh(new THREE.CylinderGeometry(.82, .9, .25, 40), titanium); a2.position.y = .12; abut.add(a2); }
export const glow = new THREE.Mesh(new THREE.CylinderGeometry(1.25, .95, 5.6, 40, 1, true), new THREE.MeshBasicMaterial({ color: '#fff0a8', transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
glow.position.set(0, -2.6, 0); scene.add(glow);
export const warn = new THREE.Mesh(new THREE.TorusGeometry(2.2, .12, 12, 60), new THREE.MeshBasicMaterial({ color: '#ff3b47', transparent: true, opacity: 0 }));
warn.position.set(0, 1.5, .6); scene.add(warn);   // pulsing red warning ring (set opacity)

// bone cells that gather around the implant: each has userData.from / userData.to / userData.d (stagger 0..0.5)
export const cells = []; const cellMat = new THREE.MeshStandardMaterial({ color: '#f3d9a6', roughness: .55, emissive: '#3a2a10', emissiveIntensity: .15 });
{ const cellGeo = new THREE.IcosahedronGeometry(.22, 2);
  for (let i = 0; i < 70; i++) { const m = new THREE.Mesh(cellGeo, cellMat); const y = -.4 - rnd() * 4.9; const r = lerp(.95, .7, (-y) / 5.2); const a = (rnd() * .95 + .025) * Math.PI;
    m.userData = { from: new THREE.Vector3((rnd() < .5 ? -1 : 1) * (2.5 + rnd() * 6), -1 - rnd() * 9, .25 + rnd() * .6), to: new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r), d: rnd() * .5 };
    scene.add(m); cells.push(m); } }

// germs: userData.from (sky) / userData.to (around the gum line at x=0) / d (stagger) / ph (phase)
export const germMat = new THREE.MeshStandardMaterial({ color: '#7bd64a', roughness: .5, emissive: '#2c6a10', emissiveIntensity: .3 });
export const germGeo = (() => { const parts = [new THREE.IcosahedronGeometry(.3, 1).toNonIndexed()]; for (let i = 0; i < 10; i++) { const c = new THREE.ConeGeometry(.07, .22, 6).toNonIndexed(); const v = new THREE.Vector3(rnd() - .5, rnd() - .5, rnd() - .5).normalize(); c.translate(0, .36, 0); c.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), v)); parts.push(c); } return mergeGeometries(parts); })();
export const germs = [];
for (let i = 0; i < 26; i++) { const m = new THREE.Mesh(germGeo, germMat); const a = (rnd() * 1.2 - .1) * Math.PI;
  m.userData = { to: new THREE.Vector3(Math.cos(a) * (1.1 + rnd() * .9), GUM_TOP + .15 + rnd() * .9, Math.sin(a) * (1.0 + rnd() * .5) + .3), from: new THREE.Vector3((rnd() - .5) * 18, 9 + rnd() * 6, 2 + rnd() * 3), d: rnd() * .6, ph: rnd() * 6 };
  scene.add(m); germs.push(m); }
/** move germs from the sky to the gum line between t0 and t0+1.2 (with stagger), bobbing */
export function germsArrive(t, t0) { germs.forEach(g => { const k = eout(seg(t, t0 + g.userData.d, t0 + 1.2 + g.userData.d)); g.visible = true; g.position.lerpVectors(g.userData.from, g.userData.to, k);
  g.position.y += Math.sin(t * 6 + g.userData.ph) * .06; g.rotation.set(t * 2 + g.userData.ph, t * 1.5, 0); g.scale.setScalar(1 + .1 * Math.sin(t * 9 + g.userData.ph)); }); }
/** germs pop away one by one between t0 and t1 */
export function germsClear(t, t0, t1) { germs.forEach((g, j) => { const kill = t0 + (j / germs.length) * (t1 - t0); const k = 1 - eout(seg(t, kill, kill + .25)); g.visible = k > 0; g.position.copy(g.userData.to); g.scale.setScalar(k); g.rotation.set(t * 2, t, 0); }); }

// toothbrush (bristles face -z, toward the teeth); place with brush.position, sweep x
export const brush = new THREE.Group(); scene.add(brush);
{ const hm = new THREE.MeshPhysicalMaterial({ color: '#2EC4B6', roughness: .3, clearcoat: 1 });
  const h = new THREE.Mesh(new THREE.CapsuleGeometry(.38, 9, 8, 16), hm); h.rotation.z = Math.PI / 2; h.position.set(5.6, 0, 0); h.castShadow = true; brush.add(h);
  const head = new THREE.Mesh(new RoundedBoxGeometry(2.6, .9, .45, 4, .2), hm); brush.add(head);
  const bm = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .6 }); const bb = new THREE.MeshStandardMaterial({ color: '#7fd3ff', roughness: .6 });
  for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.09, .09, 1.0, 6), (i + j) % 3 ? bm : bb); b.rotation.x = Math.PI / 2; b.position.set(-1.1 + i * .31, -.3 + j * .3, -.7); brush.add(b); } }

// confetti + sparkles + halo
export const conf = []; const confCols = ['#FF5A5F', '#FFE14D', '#2EC4B6', '#7FD3FF', '#B892FF'];
for (let i = 0; i < 120; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(.35, .2), new THREE.MeshBasicMaterial({ color: confCols[i % 5], side: THREE.DoubleSide }));
  m.userData = { x: (rnd() - .5) * 22, z: rnd() * 6 - 1, v: 3 + rnd() * 3, s: rnd() * 6, ph: rnd() * 7 }; scene.add(m); conf.push(m); }
/** confetti falling since t0 */
export function confetti(t, t0) { conf.forEach(c => { const u = c.userData; const tt = t - t0; c.visible = tt > 0; c.position.set(u.x + Math.sin(tt * 2 + u.ph) * .6, 16 - tt * u.v, u.z); c.rotation.set(tt * u.s, tt * 2, u.ph); }); }
const starTex = canvasTex(128, 128, (g) => { g.translate(64, 64); g.fillStyle = '#fff'; g.beginPath(); for (let i = 0; i < 8; i++) { const r = i % 2 ? 12 : 60, a = i * Math.PI / 4; g.lineTo(Math.cos(a) * r, Math.sin(a) * r); } g.fill(); });
const stars = []; for (let i = 0; i < 10; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: starTex, color: '#fffbe0', transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })); scene.add(s); stars.push(s); }
/** a ring of sparkles bursting from (cx,cy,cz); k = 0..1 progress */
export function sparkleAt(cx, cy, cz, k, R = 2.6) { stars.forEach((s, i) => { const a = i / stars.length * Math.PI * 2 + .3; const kk = clamp(k * 1.2 - (i % 3) * .1); s.visible = kk > 0 && kk < 1;
  const r = R * eout(kk); s.position.set(cx + Math.cos(a) * r, cy + Math.sin(a) * r, cz + 1.5); const sc = Math.sin(kk * Math.PI) * (i % 2 ? .9 : 1.4); s.scale.set(sc, sc, 1); }); }
const glowTex = canvasTex(256, 256, (g) => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,248,200,1)'); gr.addColorStop(.4, 'rgba(255,230,140,.45)'); gr.addColorStop(1, 'rgba(255,230,140,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); });
export const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0 })); halo.scale.set(14, 14, 1); scene.add(halo);

// ---------------------------------------------------------------- camera
export const cam = new THREE.PerspectiveCamera(38, W / H, .1, 300);
/** named shots: [eye, target]. Episodes may add their own: L.SHOTS.myShot = [[x,y,z],[x,y,z]] */
export const SHOTS = {
  wide: [[14, 11, 46], [0, 0.5, 0]],      // whole jaw, upper jaw at the top
  high: [[8, 16, 34], [0, 2, 0]],
  gap: [[6, 7.5, 24], [0, 2, 0]],         // the x=0 tooth slot and its neighbours
  bite: [[9, 6.5, 26], [0, 3.4, 0]],      // chewing
  bone: [[6, 2.5, 25], [0, -1.8, 0]],     // inside the bone
  boneC: [[4.5, 0.5, 18], [0, -2.4, 0]],  // bone close-up
  neck: [[5.5, 5.5, 18], [0, 2, 0]],      // crown + gum line + top of the root
  crown: [[-5.5, 7, 19], [0, 2.6, 0]],
  gumline: [[4.5, 5, 14], [0, 2.2, 0]],
  ortho: [[0, 6, 42], [0, 1, 0]],         // flat front view
};
const v3 = a => new THREE.Vector3(...a);
/** blend from shot a to shot b by k (0..1); optional shake amplitude */
export function setCam(a, b, k, shake = 0, t = 0) {
  const A = SHOTS[a], B2 = SHOTS[b]; const e = v3(A[0]).lerp(v3(B2[0]), k), g = v3(A[1]).lerp(v3(B2[1]), k);
  if (shake) { e.x += Math.sin(t * 61) * shake; e.y += Math.cos(t * 47) * shake; }
  cam.position.copy(e); cam.lookAt(g);
}

// ---------------------------------------------------------------- DOM overlays
const capEl = document.getElementById('cap'), chipsEl = document.getElementById('chips'), calEl = document.getElementById('cal'), calN = calEl.querySelector('.n'), calHd = calEl.querySelector('.hd');
const flashEl = document.getElementById('flash'), endEl = document.getElementById('end'), canvasEl = document.getElementById('c'), coverEl = document.getElementById('cover');
const rays = document.getElementById('rays'); for (let i = 0; i < 16; i++) { const r = document.createElement('div'); r.className = 'ray'; rays.appendChild(r); }
const chipPool = {};
/** a pill label at screen y (px), shown from t0 to t1. cls: '' (white) | dark | red | green | yel */
export function chip(id, text, cls, y, t, t0, t1 = 1e9, rot = 0) {
  let el = chipPool[id]; if (!el) { el = document.createElement('div'); el.className = 'chip ' + cls; el.textContent = text; chipsEl.appendChild(el); chipPool[id] = el; }
  const on = t >= t0 && t < t1 + .25; el.style.display = on ? 'block' : 'none'; if (!on) return;
  const s = t < t1 ? back(seg(t, t0, t0 + .35)) : 1 - ein(seg(t, t1, t1 + .25));
  el.style.top = y + 'px'; el.style.transform = `translate(-50%,0) scale(${s}) rotate(${rot}deg)`;
}
/** calendar/counter widget at the top: header text, number, pop scale */
export function calendar(header, n, scale = 1) { calEl.style.display = 'block'; calHd.textContent = header; calN.textContent = n; calEl.style.transform = `scale(${scale})`; }
function caption(t) {
  let cur = null;
  for (const b of T.beats) for (const c of b.chunks) if (t >= c.t && t < c.end) cur = c;
  if (!cur) { capEl.textContent = ''; return; }
  capEl.textContent = cur.text; capEl.className = cur.key ? 'key' : '';
  capEl.style.transform = `scale(${1 + .22 * (1 - eout(seg(t, cur.t, cur.t + .12)))})`;
}

// ---------------------------------------------------------------- timeline access
export let T = null, B = null, EP = null;
export const bs = i => B[i].start, be = i => B[i].start + B[i].dur;
/** time of a named mark in beat i (from episode.json "marks"), else start + def * duration */
export const mk = (i, name, def = 0) => (B[i].marks && B[i].marks[name] != null) ? B[i].marks[name] : bs(i) + def * B[i].dur;
/** which beat is t in (index), or B.length when in the end card */
export const beatAt = t => { for (let i = 0; i < B.length; i++) if (t < be(i)) return i; return B.length; };

const resets = [];
/** register a function that resets episode-made objects at the start of each frame */
export const onReset = fn => resets.push(fn);
function hideAll() {
  [looseCrown, implant, abut, newCrown, food, brush].forEach(o => o.visible = false);
  cells.forEach(c => c.visible = false); germs.forEach(g => g.visible = false); conf.forEach(c => c.visible = false); stars.forEach(s => s.visible = false);
  centerTooth.visible = true; centerTooth.position.set(0, .7, 0); centerTooth.rotation.set(0, 0, 0);
  [looseCrown, newCrown].forEach(o => { o.position.set(0, .7, 0); o.rotation.set(0, 0, 0); });
  food.position.set(0, 5.8, .2); food.scale.set(1.25, .8, 1);
  upper.position.set(0, 11, 0); glow.material.opacity = 0; warn.material.opacity = 0; inflam.material.opacity = 0; inflamF.material.opacity = 0; halo.material.opacity = 0;
  implant.rotation.set(0, 0, 0); implant.position.set(0, 0, 0); abut.position.set(0, .05, 0); abut.rotation.set(0, 0, 0);
  calEl.style.display = 'none'; coverEl.style.display = 'none';
  Object.values(chipPool).forEach(e => e.style.display = 'none');
  resets.forEach(f => f());
}

export async function init(epDir) {
  T = await (await fetch('/' + epDir + '/.work/timeline.json')).json(); B = T.beats;
  EP = await (await fetch('/' + epDir + '/episode.json')).json();
  const c = EP.cover || {};
  coverEl.querySelector('.tag').textContent = c.tag || ''; coverEl.querySelector('.h1').textContent = c.title || '';
  coverEl.querySelector('.h2').textContent = c.title2 || ''; coverEl.querySelector('.sub').textContent = c.sub || '⏱ เข้าใจใน 1 นาที';
  if (!c.tag) coverEl.querySelector('.tag').style.display = 'none';
  if (c.titleSize) coverEl.querySelector('.h1').style.fontSize = c.titleSize + 'px';
  document.getElementById('e6').querySelector('.pill').textContent = EP.endcta || 'ปรึกษาทันตแพทย์ ทักมาได้เลย!';
  await document.fonts.ready; await new Promise(r => { const im = document.querySelector('#end img'); im.complete ? r() : im.onload = r; });
}

/** episode frame(t, L) sets the scene + camera for time t and may return {blur, flash, filter} (filter = CSS filter for the 3D layer, e.g. an X-ray look); the end card is drawn on top automatically */
export function runFrame(t, epFrame) {
  hideAll();
  const fx = epFrame(t) || {};
  renderer.render(scene, cam);
  canvasEl.style.filter = [fx.filter || '', fx.blur > .3 ? `blur(${fx.blur.toFixed(1)}px)` : ''].join(' ').trim() || 'none';
  flashEl.style.opacity = fx.flash || 0;
  caption(t);
  const endA = seg(t, T.end.start, T.end.start + .35);
  endEl.style.opacity = endA;
  if (endA > 0) {
    capEl.textContent = ''; Object.values(chipPool).forEach(e => e.style.display = 'none'); calEl.style.display = 'none';
    const te = t - T.end.start;
    [...rays.children].forEach((r, j) => r.style.transform = `rotate(${j * 22.5 + te * 12}deg)`);
    document.querySelector('#end .logo').style.transform = `scale(${back(seg(te, .15, .6))}) rotate(${Math.sin(te * 2) * 2}deg)`;
    [['e1', .5], ['e2', .7], ['e3', 1.1], ['e4', 1.4], ['e5', 1.7], ['e6', 2.2]].forEach(([id, d0]) => { document.getElementById(id).style.transform = `scale(${back(seg(te, d0, d0 + .4))})`; });
  }
}
/** episode cover(t, L) poses the scene + camera and returns labels [{text, at:[x,y,z], dx, dy}] (max 4) */
export function runCover(t, epCover) {
  hideAll();
  const labs = epCover(t) || [];
  renderer.render(scene, cam); canvasEl.style.filter = 'none';
  capEl.textContent = ''; endEl.style.opacity = 0; flashEl.style.opacity = 0; coverEl.style.display = 'block';
  ['l1', 'l2', 'l3', 'l4'].forEach((id, i) => { const el = document.getElementById(id); const L0 = labs[i]; el.style.display = L0 ? 'block' : 'none'; if (!L0) return;
    el.textContent = L0.text; const v = v3(L0.at).project(cam); el.style.left = ((v.x + 1) / 2 * W + (L0.dx ?? 60)) + 'px'; el.style.top = ((1 - v.y) / 2 * H + (L0.dy ?? 0)) + 'px'; });
  coverEl.querySelector('.h1').style.transform = `scale(${1 + .03 * Math.sin(t * 4)})`;
}

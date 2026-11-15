// ep28 สูบบุหรี่ เหงือกพังไม่รู้ตัว? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the jaw cut-away (as ep19) + a lit cigarette above the teeth puffing smoke, blood vessels drawn on the gum's cut
// face. Smoking "just stains teeth"? -> nicotine narrows the gum's blood vessels, less blood reaches the gum -> plaque +
// calculus, germs -> gingivitis -> but a smoker's gum bleeds little and is not very red, so it goes unnoticed ->
// periodontitis: bone loss + wobble, smokers twice the risk (CDC) -> dentist: scaling + root planing (calculus under the gum)
// -> but still smoking: slow healing, treatment works less well (CDC) -> quit (cigarette snaps), gum recovers, quitline 1600
// -> myth: no bleeding = healthy gum? no, smoking hides the signs -> payoff: pink gums.
let rings = [], bridges = [], paps = [], papMat, calcMat, pocket = [], pocketMat, scaler, mist = [], chunks = [];
let cig, cigA, cigB, ember, emberMat, puffs = [], vessels = [], vesselMat, flow = [], flowMat, sub = [], subMat, veil;
const PLAQUE = '#f3e27a', CALC = '#c7a35a', GUM = '#ee8399', GUMRED = '#d9364f', GUMPALE = '#c99aa0', WHITE = '#fbf8f1', STAIN = '#dcc08a';
const CIG = [3.2, 6.6, 2.2];   // ember position (cigarette lies toward +x)

function bumpy(THREE, geo, amt, seed) {
  const p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const n = 1 + amt * (Math.sin(x * 7.1 + seed) * Math.sin(z * 6.3 + seed * 2) + .6 * Math.sin(y * 9.7 + x * 3 + seed));
    p.setXYZ(i, x * n, y * (1 + (n - 1) * .6), z * n); }
  geo.computeVertexNormals(); return geo;
}

export function setup(L) {
  const { THREE, scene, SP, GUM_TOP, canvasTex, rnd, titanium } = L;
  calcMat = new THREE.MeshStandardMaterial({ color: PLAQUE, roughness: .85, transparent: true, opacity: 1 });
  const hosts = [L.neighbors[2], L.centerTooth, L.neighbors[3]];
  hosts.forEach((h, i) => { const g = bumpy(THREE, new THREE.TorusGeometry(1.5, .3, 14, 64), .14, i * 1.7); const m = new THREE.Mesh(g, calcMat);
    m.rotation.x = Math.PI / 2; m.scale.set(1, .86, .8); m.position.y = GUM_TOP + .22 - .7; m.castShadow = true; h.add(m); rings.push(m); });
  [-1.5, -.5, .5, 1.5].forEach((k, i) => { const m = new THREE.Mesh(bumpy(THREE, new THREE.SphereGeometry(.62, 28, 18), .16, i * 2.3), calcMat);
    m.position.set(k * SP, GUM_TOP + .45, .35); m.scale.set(1, .95, 1.1); m.castShadow = true; scene.add(m); bridges.push(m); });
  // calculus under the gum, on the root surface (shown on the cut face, removed by root planing)
  subMat = new THREE.MeshStandardMaterial({ color: '#8f6a35', roughness: .9 });
  [-1, 1].forEach(s => [0, 1, 2].forEach(j => { const m = new THREE.Mesh(bumpy(THREE, new THREE.SphereGeometry(.2, 14, 10), .2, j + s), subMat);
    m.position.set(s * (1.28 - j * .08), .9 - j * .45, .12); m.scale.set(.8, 1.3, .5); scene.add(m); sub.push(m); }));
  papMat = new THREE.MeshPhysicalMaterial({ color: GUM, roughness: .45, clearcoat: .6, clearcoatRoughness: .3 });
  [-1.5, -.5, .5, 1.5].forEach(k => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20, 0, Math.PI * 2, 0, Math.PI / 2), papMat);
    m.position.set(k * SP, GUM_TOP - .02, .1); m.receiveShadow = true; scene.add(m); paps.push(m); });
  pocketMat = new THREE.MeshStandardMaterial({ color: '#8a4a3c', transparent: true, opacity: 0, roughness: .8, side: THREE.DoubleSide, depthWrite: false });
  [-1, 1].forEach(s => { const sh = new THREE.Shape(); sh.moveTo(s * .95, .02); sh.lineTo(s * 2.4, .02); sh.lineTo(s * 1.05, -1); sh.closePath();
    const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), pocketMat); m.position.z = .03; scene.add(m); pocket.push(m); });
  // blood vessels on the cut face of the gum + bone (a wavy main vessel with branches up into the gum)
  vesselMat = new THREE.MeshStandardMaterial({ color: '#e2203c', roughness: .4, emissive: '#7a0010', emissiveIntensity: .35 });
  const tube = (pts, r) => { const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(...p))), 80, r, 10, false), vesselMat); scene.add(m); vessels.push(m); return m; };
  const main = []; for (let i = 0; i <= 24; i++) { const x = -14 + i * 28 / 24; main.push([x, -.55 + Math.sin(x * .9) * .18, .05]); }
  tube(main, .16);
  [-2.5, -1.5, -.5, .5, 1.5, 2.5].forEach(k => { const x = k * SP; tube([[x - .3, -.5, .05], [x - .1, .2, .05], [x + .15, .7, .05], [x, 1.05, .05]], .09); });
  vessels.forEach(v => { v.userData.base = 1; });
  // red blood cells flowing along the main vessel
  flowMat = new THREE.MeshStandardMaterial({ color: '#ff4a62', roughness: .3, emissive: '#a0001a', emissiveIntensity: .5 });
  for (let i = 0; i < 22; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.13, 12, 8), flowMat); m.scale.set(1.3, .7, .7); m.userData = { u: i / 22 }; scene.add(m); flow.push(m); }
  // pale veil over the gum (a smoker's gum: less red, hides the signs)
  veil = new THREE.Mesh(new THREE.PlaneGeometry(16, GUM_TOP + .9), new THREE.MeshBasicMaterial({ color: '#d8c6c8', transparent: true, opacity: 0, depthWrite: false }));
  veil.position.set(0, GUM_TOP / 2 + .3, .5); scene.add(veil);
  // ultrasonic scaler
  scaler = new THREE.Group(); scene.add(scaler);
  { const grip = new THREE.MeshPhysicalMaterial({ color: '#7FD3FF', roughness: .3, clearcoat: 1 });
    const h = new THREE.Mesh(new THREE.CapsuleGeometry(.42, 6.5, 8, 20), grip); h.position.y = 5.6; h.castShadow = true; scaler.add(h);
    const n = new THREE.Mesh(new THREE.CylinderGeometry(.2, .42, 1.4, 20), titanium); n.position.y = 1.9; scaler.add(n);
    const t1 = new THREE.Mesh(new THREE.CylinderGeometry(.07, .17, 1.4, 12), titanium); t1.position.set(0, .75, 0); t1.rotation.z = .25; scaler.add(t1);
    const t2 = new THREE.Mesh(new THREE.CylinderGeometry(.04, .07, .6, 10), titanium); t2.position.set(.12, .12, 0); t2.rotation.z = -.5; scaler.add(t2); }
  const mistMat = new THREE.MeshStandardMaterial({ color: '#bfe9ff', transparent: true, opacity: .8, roughness: .1 });
  for (let i = 0; i < 18; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.08 + rnd() * .07, 10, 8), mistMat); m.userData = { a: rnd() * 6.28, v: 1.5 + rnd() * 2, ph: rnd() }; scene.add(m); mist.push(m); }
  for (let i = 0; i < 26; i++) { const m = new THREE.Mesh(bumpy(THREE, new THREE.IcosahedronGeometry(.18 + rnd() * .16, 1), .2, i), calcMat);
    const x0 = [-SP, -SP / 2, 0, SP / 2, SP][i % 5] + (rnd() - .5) * .8;
    m.userData = { p: new THREE.Vector3(x0, GUM_TOP + .3 + rnd() * .4, .9 + rnd() * .4), v: new THREE.Vector3((rnd() - .5) * 7, 4 + rnd() * 4, 2 + rnd() * 3), d: rnd() * .5, r: rnd() * 9 };
    m.castShadow = true; scene.add(m); chunks.push(m); }
  // cigarette: two halves (so it can snap), lying along x, ember at the -x end (group origin)
  cig = new THREE.Group(); scene.add(cig);
  const paper = new THREE.MeshStandardMaterial({ color: '#f7f4ee', roughness: .7 }), filt = new THREE.MeshStandardMaterial({ color: '#e59a4a', roughness: .6 });
  cigA = new THREE.Group(); cigB = new THREE.Group(); cig.add(cigA); cig.add(cigB);
  { const a = new THREE.Mesh(new THREE.CylinderGeometry(.32, .32, 3, 24), paper); a.rotation.z = Math.PI / 2; a.position.x = 1.5; a.castShadow = true; cigA.add(a);
    const ash = new THREE.Mesh(new THREE.CylinderGeometry(.31, .31, .35, 24), new THREE.MeshStandardMaterial({ color: '#8b8580', roughness: .95 })); ash.rotation.z = Math.PI / 2; ash.position.x = .1; cigA.add(ash);
    emberMat = new THREE.MeshStandardMaterial({ color: '#ff6a1a', emissive: '#ff3a00', emissiveIntensity: 1.6, roughness: .6 });
    ember = new THREE.Mesh(new THREE.SphereGeometry(.31, 20, 12), emberMat); ember.scale.set(.35, 1, 1); ember.position.x = -.08; cigA.add(ember);
    const b = new THREE.Mesh(new THREE.CylinderGeometry(.32, .32, 2, 24), paper); b.rotation.z = Math.PI / 2; b.position.x = 1; b.castShadow = true; cigB.add(b);
    const f = new THREE.Mesh(new THREE.CylinderGeometry(.33, .33, 1.7, 24), filt); f.rotation.z = Math.PI / 2; f.position.x = 2.85; cigB.add(f); }
  // smoke puffs (soft grey sprites)
  const sTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 4, 64, 64, 64); gr.addColorStop(0, 'rgba(235,235,240,.9)'); gr.addColorStop(.6, 'rgba(200,200,210,.45)'); gr.addColorStop(1, 'rgba(200,200,210,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  for (let i = 0; i < 34; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: sTex, color: '#e4e2ea', transparent: true, depthWrite: false, opacity: 0 }));
    s.userData = { ph: i / 34, dx: (rnd() - .5) * 2, sw: rnd() * 6 }; scene.add(s); puffs.push(s); }
  Object.assign(L.SHOTS, {
    front: [[0, 4.4, 15.5], [0, 2.7, 0]],
    front2: [[2.5, 5.2, 13], [0, 2.9, 0]],
    pocket: [[4, 1.2, 17], [0, -.6, 0]],
    vessel: [[2.5, 0.9, 12], [0, -.1, 0]],
    smoke: [[3.5, 6.2, 17], [1.2, 4, 0]],
  });
  L.onReset(() => {
    rings.forEach(r => { r.visible = false; r.scale.set(1, .86, .8); }); bridges.forEach(b => { b.visible = false; b.scale.set(1, .95, 1.1); });
    calcMat.color.set(PLAQUE); calcMat.opacity = 1; sub.forEach(s => { s.visible = false; s.scale.set(.8, 1.3, .5); });
    paps.forEach(p => p.scale.set(.85, .32, 1.1)); papMat.color.set(GUM); L.gumMatTop.color.set('#ee8399');
    pocketMat.opacity = 0; pocket.forEach(p => p.scale.set(1, 1, 1));
    scaler.visible = false; scaler.rotation.set(0, 0, 0); mist.forEach(m => m.visible = false); chunks.forEach(c => c.visible = false);
    L.enamel.color.set(WHITE);
    vessels.forEach(v => { v.visible = true; v.scale.set(1, 1, 1); }); vesselMat.color.set('#e2203c'); vesselMat.emissiveIntensity = .35; flow.forEach(f => f.visible = false);
    veil.material.opacity = 0;
    cig.visible = false; cig.position.set(...CIG); cig.rotation.set(0, -.35, .12); cigA.position.set(0, 0, 0); cigA.rotation.set(0, 0, 0); cigB.position.set(3, 0, 0); cigB.rotation.set(0, 0, 0); emberMat.emissiveIntensity = 1.6;
    puffs.forEach(p => { p.visible = false; p.material.opacity = 0; });
  });
}

function calculus(L, grow, hard, shrink = 0) {
  const s = L.clamp(grow) * (1 - L.clamp(shrink)); if (s <= 0) return;
  calcMat.color.set(PLAQUE).lerp(new L.THREE.Color(CALC), L.clamp(hard)); calcMat.opacity = .55 + .45 * L.clamp(hard);
  rings.forEach(r => { r.visible = true; r.scale.set(.92 + .08 * s, .86 * s, .8 * (.4 + .6 * s)); });
  bridges.forEach(b => { b.visible = hard > .05; const k = L.clamp(hard) * s; b.scale.set(k, .95 * k, 1.1 * k); });
}
function subCalc(L, k) { if (k <= 0) return; sub.forEach(s => { s.visible = true; s.scale.set(.8 * k, 1.3 * k, .5 * k); }); }
// red 0..1 (inflamed), pale 0..1 (a smoker's muted colour)
function papillae(L, swell, red, pale = 0, shrunk = 0) {
  paps.forEach(p => p.scale.set(.85 + .35 * swell - .15 * shrunk, .32 + 1.05 * swell - .1 * shrunk, 1.1 + .3 * swell));
  papMat.color.set(GUM).lerp(new L.THREE.Color(GUMRED), red).lerp(new L.THREE.Color(GUMPALE), pale);
  L.gumMatTop.color.set('#ee8399').lerp(new L.THREE.Color(GUMPALE), pale * .8);
}
// vessels: narrow 0..1 (contracted, darker), flowing speed
function blood(L, t, narrow, flowOn = 1) {
  // TubeGeometry can't scale its radius per axis, so fake thinning by scaling around the vessel's own line in y/z
  vessels.forEach((v, i) => { if (i === 0) { const s = 1 - .6 * narrow; v.scale.set(1, s, s); v.position.set(0, -.55 * (1 - s), .05 * (1 - s)); } else { const s = 1 - .55 * narrow; v.scale.set(s, 1, s); v.position.set(v.userData.cx * (1 - s), 0, .05 * (1 - s)); } });
  vesselMat.color.set('#e2203c').lerp(new L.THREE.Color('#8a3a48'), narrow); vesselMat.emissiveIntensity = .35 * (1 - narrow);
  if (flowOn <= 0) return;
  const n = Math.round(flow.length * (1 - .65 * narrow));
  flow.forEach((f, i) => { f.visible = i < n; const u = (f.userData.u + t * .07 * (1 - .6 * narrow)) % 1; const x = -14 + u * 28;
    f.position.set(x, -.55 + Math.sin(x * .9) * .18, .22); f.scale.set(1.3, .7, .7).multiplyScalar(1 - .45 * narrow); });
}
function smoke(L, t, amt, src) {
  puffs.forEach(p => { const u = p.userData; const k = (t * .35 + u.ph) % 1; p.visible = amt > 0; if (!p.visible) return;
    p.position.set(src[0] - k * 3.4 + u.dx * k + Math.sin(t * 1.5 + u.sw) * .4 * k, src[1] - k * 2.2 + Math.sin(k * 4 + u.sw) * .3, src[2] - k * 1.2);
    const s = .5 + k * 2.0; p.scale.set(s, s, 1); p.material.opacity = amt * .38 * Math.sin(Math.PI * k); });
}
function scalerAt(L, t, x, y, on) {
  scaler.visible = true; const j = on ? .05 : 0;
  scaler.position.set(x + Math.sin(t * 90) * j, y + Math.cos(t * 77) * j, 1.25); scaler.rotation.set(-.35, 0, -.55);
  if (on) mist.forEach(m => { const u = m.userData; const k = ((t * 1.6 + u.ph) % 1); m.visible = true;
    m.position.set(x + Math.cos(u.a) * k * u.v * .7, y + .2 + Math.sin(u.a) * k * u.v * .5 + k * .6, 1.4 + k * .8); m.scale.setScalar(1 - k); });
}
function cigOn(L, t, k = 1) { cig.visible = k > 0; const e = L.eout(k); cig.position.set(CIG[0] + 7 * (1 - e), CIG[1] + Math.sin(t * 1.6) * .1, CIG[2]); emberMat.emissiveIntensity = 1.3 + .6 * Math.sin(t * 5); }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, lerp, clamp, GUM_TOP, setCam, chip, sparkleAt, centerTooth: ct, inflam, inflamF, warn, halo } = L;
  if (!vessels[1].userData.cx) vessels.forEach((v, i) => { v.userData.cx = i ? [-2.5, -1.5, -.5, .5, 1.5, 2.5][i - 1] * L.SP : 0; });
  let blur = 0, flash = 0;
  const redOn = k => { inflam.material.opacity = .5 * k; inflamF.material.opacity = .4 * k; };
  const whip = a => t < a + .35 ? (1 - seg(t, a, a + .35)) * 13 : 0;
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const stain = k => L.enamel.color.set(WHITE).lerp(new L.THREE.Color(STAIN), k);
  const narrowT = mk(1, 'shrink', .3);

  if (t < be(0)) {                       // hook: a lit cigarette slides in, teeth turn yellowish — "the gums are fine?"
    const a = bs(0), d = B[0].dur, cg = mk(0, 'cig', .05), yl = mk(0, 'yellow', .2), gm = mk(0, 'gum', .5), ask = mk(0, 'ask', .85);
    cigOn(L, t, seg(t, cg, cg + .6)); smoke(L, t, seg(t, cg + .3, cg + 1), CIG);
    stain(.8 * ease(seg(t, yl, yl + 1.2)));
    if (t > gm) { halo.material.opacity = .22 * eout(seg(t, gm, gm + .5)); halo.position.set(0, GUM_TOP + .6, 1); halo.scale.set(9, 5, 1); }
    setCam('wide', 'smoke', ease(seg(t, a, a + d * .6)));
    if (t > gm) setCam('smoke', 'front2', ease(seg(t, gm - .1, gm + .9)));
    chip('h1', '🚬 แค่ฟันเหลือง?', 'dark', 190, t, yl + .2, be(0) - .1);
    chip('h2', 'เหงือกไม่เป็นไร ?', 'green', 330, t, gm + .2, be(0) - .1, -2);
  } else if (t < be(1)) {                // nicotine: the gum's blood vessels narrow, less blood reaches the gum
    const a = bs(1), d = B[1].dur, sm = mk(1, 'smoke', .05), nc = mk(1, 'nic', .15), ls = mk(1, 'less', .75);
    stain(.8); cigOn(L, t); smoke(L, t, 1, CIG);
    const nk = ease(seg(t, narrowT, narrowT + 1.4)); blood(L, t, nk);
    papillae(L, 0, 0, .35 * seg(t, ls, ls + .8));
    if (t > narrowT) { warn.material.opacity = .8 * Math.exp(-(t - narrowT) * 1.2); warn.position.set(0, .3, .5); warn.scale.set(1.6, .6, 1); }
    flash = hit(narrowT, .15);
    blur = whip(a);
    setCam('front2', 'vessel', ease(seg(t, a, nc + .8)));
    chip('nc', '💨 นิโคติน (Nicotine)', 'dark', 190, t, nc, be(1) - .1);
    chip('sh', '🩸 เส้นเลือดในเหงือก หดตัว', 'red', 320, t, narrowT + .2, be(1) - .1, -2);
    chip('ls', '⬇ เลือดไปเลี้ยงเหงือกน้อยลง', 'yel', 450, t, ls, be(1) - .1, 2);
  } else if (t < be(2)) {                // plaque + calculus, germs -> gingivitis
    const a = bs(2), d = B[2].dur, pl = mk(2, 'plaque', .1), ca = mk(2, 'calc', .3), gr = mk(2, 'germ', .55), tm = mk(2, 'term', .8);
    stain(.8); blood(L, t, 1);
    calculus(L, eout(seg(t, pl, pl + .8)), seg(t, ca, ca + 1));
    if (t > gr) L.germsArrive(t, gr - .3);
    const sw = eout(seg(t, tm - .4, tm + .8)); papillae(L, sw, sw, .35 * (1 - sw)); redOn(sw);
    blur = whip(a);
    setCam('vessel', 'front', ease(seg(t, a, a + 1)));
    if (t > gr) setCam('front', 'gumline', ease(seg(t, gr, tm + .6)));
    chip('pl', 'คราบจุลินทรีย์ + หินปูน', 'yel', 190, t, pl + .2, be(2) - .1);
    chip('gi', '🔥 เหงือกอักเสบ (Gingivitis)', 'red', 320, t, tm, be(2) - .1, 2);
  } else if (t < be(3)) {                // but a smoker's gum: little bleeding, not very red -> unnoticed
    const a = bs(3), d = B[3].dur, bl = mk(3, 'bleed', .25), co = mk(3, 'color', .5), hd = mk(3, 'hidden', .75);
    stain(.8); blood(L, t, 1); calculus(L, 1, 1); L.germsArrive(t, a - 5);
    const pk = ease(seg(t, co - .2, co + 1)); papillae(L, 1, 1 - .25 * pk, .85 * pk); redOn(1 - .85 * pk);
    veil.material.opacity = .28 * ease(seg(t, hd, hd + .8));
    cigOn(L, t, seg(t, a, a + .6)); smoke(L, t, seg(t, a, a + .8), CIG);
    blur = whip(a);
    setCam('gumline', 'front', ease(seg(t, a, a + d)) * .6);
    chip('s0', '🚬 เหงือกคนสูบบุหรี่', 'dark', 190, t, a + .2, be(3) - .1);
    chip('s1', '🩸 เลือดออกน้อย', 'yel', 320, t, bl + .2, be(3) - .1, -2);
    chip('s2', 'สีไม่ค่อยแดง', 'yel', 440, t, co + .1, be(3) - .1, 2);
    chip('s3', '😶 ไม่รู้ตัวว่าป่วย!', 'red', 570, t, hd + .2, be(3) - .1, -3);
  } else if (t < be(4)) {                // periodontitis: bone loss + wobble; smokers twice the risk
    const a = bs(4), d = B[4].dur, dp = mk(4, 'deep', .1), bn = mk(4, 'bone', .2), tm = mk(4, 'term', .6), rk = mk(4, 'risk', .7), tw = mk(4, 'two', .9);
    stain(.8); blood(L, t, 1); calculus(L, 1, 1); papillae(L, 1, .75, .85); redOn(.15); veil.material.opacity = .2;
    L.germsArrive(t, a - 5);
    const pkk = eout(seg(t, bn, bn + 1.6)); pocketMat.opacity = .85 * pkk; pocket.forEach(p => p.scale.set(1, .2 + 2.6 * pkk, 1));
    L.germs.forEach((g, i) => { if (i % 2) { g.position.y -= 2.4 * eout(seg(t, dp, dp + 1.4)) * (.5 + (i % 5) * .15); g.position.z = .5; } });
    const wob = tm - .2; const w = t > wob ? Math.sin((t - wob) * 20) * .07 * clamp((t - wob) * 3) : 0; ct.rotation.z = w; ct.position.x = -w * 2;
    warn.material.opacity = t > wob ? .85 * (.5 + .5 * Math.sin((t - wob) * 14)) : 0; warn.position.set(0, 1.5, .6); warn.scale.setScalar(1);
    flash = hit(tw, .2);
    blur = whip(a);
    setCam('front', 'pocket', ease(seg(t, a, bn + 1)), t > wob && t < rk ? .06 : 0, t);
    chip('bl', 'กระดูกรอบรากฟันถูกทำลาย', 'red', 190, t, bn + .3, tm - .05);
    chip('pe', 'โรคปริทันต์ (Periodontitis)', 'dark', 190, t, tm, be(4) - .1);
    chip('wb', '⚠ ฟันอาจโยก', 'red', 320, t, tm + .4, tw - .1, -3);
    chip('x2', '🚬 เสี่ยงโรคเหงือก ×2', 'yel', 320, t, tw - .05, be(4) - .1, 2);
    chip('cdc', 'ข้อมูล: CDC สหรัฐฯ', 'dark', 450, t, tw + .3, be(4) - .1);
  } else if (t < be(5)) {                // dentist: scaling + root planing (calculus under the gum too)
    const a = bs(5), d = B[5].dur, sc = mk(5, 'scale', .2), pn = mk(5, 'plane', .4), un = mk(5, 'under', .7);
    stain(.8 - .5 * seg(t, sc, pn)); blood(L, t, 1);
    const sh = seg(t, sc + .2, sc + 1.1); calculus(L, 1, 1, sh); subCalc(L, 1 - seg(t, un, un + 1));
    papillae(L, 1 - .3 * sh, .75 - .3 * sh, .85); redOn(.15); veil.material.opacity = .2 * (1 - sh);
    pocketMat.opacity = .85; pocket.forEach(p => p.scale.set(1, 2.8, 1));
    L.germsClear(t, sc + .2, un + .8);
    const on = t > sc; const ki = eout(seg(t, a + .1, sc));
    const sweep = t < pn ? Math.sin(seg(t, sc, pn) * Math.PI * 3) * 1.9 : 0;
    const dive = t > pn ? eout(seg(t, pn, pn + .5)) : 0;
    scalerAt(L, t, lerp(7, 0, ki) + sweep + 1.35 * dive + (t > pn ? Math.sin(t * 9) * .12 : 0), lerp(9, GUM_TOP + .55, ki) - 1.1 * dive + (t > pn ? Math.sin(t * 7) * .25 : 0), on);
    chunks.forEach(c => { const u = c.userData; const tt = t - sc - .3 - u.d; c.visible = tt > 0 && tt < 1.4;
      if (c.visible) { c.position.set(u.p.x + u.v.x * tt, u.p.y + u.v.y * tt - 9 * tt * tt, u.p.z + u.v.z * tt); c.rotation.set(tt * u.r, tt * 5, 0); } });
    flash = hit(sc + .3, .2);
    blur = whip(a);
    setCam('pocket', 'front', ease(seg(t, a, a + .9)), on ? .04 : 0, t);
    if (t > pn - .2) setCam('front', 'neck', ease(seg(t, pn - .2, pn + .6)), .04, t);
    chip('dt', '👩‍⚕️ ทันตแพทย์', 'dark', 190, t, a + .2, sc - .05);
    chip('sc', 'ขูดหินปูน (Scaling)', 'green', 190, t, sc, be(5) - .1);
    chip('rp', '+ เกลารากฟัน (Root planing)', 'green', 320, t, pn, be(5) - .1, -2);
    chip('un', '↓ หินปูนใต้เหงือก', 'yel', 450, t, un, be(5) - .1, 2);
  } else if (t < be(6)) {                // still smoking: slow healing, treatment works less well
    const a = bs(6), d = B[6].dur, sl = mk(6, 'slow', .3), ls = mk(6, 'less', .6);
    stain(.3); blood(L, t, 1); pocketMat.opacity = .7; pocket.forEach(p => p.scale.set(1, 2.6, 1));
    cigOn(L, t, seg(t, a + .1, a + .7)); smoke(L, t, seg(t, a + .3, a + 1), CIG);
    // slow healing: the swelling goes down only a little, then stalls
    const hk = .25 * eout(seg(t, sl, sl + 2.5)); papillae(L, .7 - hk, .45, .6); redOn(.25);
    if (t > ls) { warn.material.opacity = .7 * (.5 + .5 * Math.sin((t - ls) * 10)); warn.position.set(0, 1.4, .6); warn.scale.setScalar(1); }
    blur = whip(a);
    setCam('neck', 'smoke', ease(seg(t, a, a + .8)) * .7);
    if (t > sl) setCam('smoke', 'front', ease(seg(t, sl, sl + .8)));
    chip('st', '🚬 ยังสูบต่อ', 'dark', 190, t, a + .3, be(6) - .1);
    chip('sl', '🐢 เหงือกหายช้า', 'yel', 320, t, sl + .1, be(6) - .1, -2);
    chip('l6', '📉 รักษาได้ผลน้อยลง', 'red', 450, t, ls + .1, be(6) - .1, 2);
  } else if (t < be(7)) {                // quit: the cigarette snaps, vessels widen, gum turns pink; quitline 1600
    const a = bs(7), d = B[7].dur, qt = mk(7, 'quit', .05) + .35, hl = mk(7, 'heal', .2), cl = mk(7, 'call', .5), nm = mk(7, 'num', .75);
    stain(.3); pocketMat.opacity = .7 * (1 - .3 * seg(t, hl, hl + 1.5)); pocket.forEach(p => p.scale.set(1, 2.6, 1));
    cigOn(L, t); const sn = seg(t, qt, qt + 1.2);
    if (t > qt) { emberMat.emissiveIntensity = 1.4 * (1 - seg(t, qt, qt + .3));
      cigA.rotation.z = .9 * eout(sn); cigA.position.set(-1.2 * sn, -4 * ein(sn), 0); cigB.rotation.z = -.9 * eout(sn); cigB.position.set(3 + 1.6 * sn, -4.5 * ein(sn), 0); }
    smoke(L, t, 1 - seg(t, qt, qt + .5), CIG);
    const hk = ease(seg(t, hl, hl + 1.6)); blood(L, t, 1 - hk); papillae(L, .45 * (1 - hk), .45 * (1 - hk), .6 * (1 - hk)); redOn(.25 * (1 - hk));
    if (t > hl + .8) sparkleAt(0, GUM_TOP + .6, .8, seg(t, hl + .8, hl + 1.6), 3.4);
    flash = hit(qt, .3);
    blur = whip(a);
    setCam('front', 'smoke', ease(seg(t, a, a + .5)) * .5);
    if (t > hl) setCam('smoke', 'vessel', ease(seg(t, hl, hl + 1)) * .7);
    chip('qt', '🚭 เลิกบุหรี่', 'green', 190, t, qt - .1, be(7) - .1);
    chip('hl', '🌱 เหงือกฟื้นตัวได้ดีขึ้น', 'green', 320, t, hl + .2, be(7) - .1, -2);
    chip('cl', '📞 สายด่วนเลิกบุหรี่ 1600', 'yel', 450, t, nm - .3, be(7) - .1, 2);
  } else if (t < be(8)) {                // myth: no bleeding = healthy gum? no — smoking hides the signs
    const a = bs(8), d = B[8].dur, nb = mk(8, 'nobleed', .2), no = mk(8, 'no', .6), hd = mk(8, 'hide', .75);
    // flashback to the smoker's hidden state
    stain(.8); blood(L, t, 1); calculus(L, 1, 1); papillae(L, 1, .75, .85); redOn(.15); veil.material.opacity = .25 * (1 - seg(t, hd, hd + .6));
    pocketMat.opacity = t > no ? .85 * (.6 + .4 * Math.sin((t - no) * 8)) : 0; pocket.forEach(p => p.scale.set(1, 2.8, 1));
    if (t > no) { L.germsArrive(t, no - .9); warn.material.opacity = .8 * (.5 + .5 * Math.sin((t - no) * 12)); warn.position.set(0, -.2, .6); warn.scale.setScalar(1.1); }
    if (t > hd) redOn(.15 + .5 * seg(t, hd, hd + .6));
    flash = hit(no, .25);
    blur = whip(a);
    setCam('front', 'front2', ease(seg(t, a, a + .8)) * .5);
    if (t > no - .2) setCam('front2', 'pocket', ease(seg(t, no - .2, no + .8)), t > no && t < no + .3 ? .1 : 0, t);
    chip('m1', 'ไม่มีเลือดออก = เหงือกดี ?', 'dark', 190, t, nb, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', 190, t, no, be(8) - .1, -4);
    chip('m3', '🙈 บุหรี่แค่ซ่อนอาการไว้', 'yel', 330, t, hd + .1, be(8) - .1, 2);
  } else if (t < be(9)) {                // payoff: quit, pink healthy gums, bright smile
    const a = bs(9), d = B[9].dur;
    stain(.15); blood(L, t, 0); papillae(L, 0, 0);
    L.confetti(t, a); sparkleAt(0, 3, 0, seg(t, a, a + .9), 3.8);
    L.upper.position.y = 11 - 7.4 * Math.pow(Math.max(0, Math.sin((t - a) * 2 * Math.PI)), 2) * clamp((t - a) * 2);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
    chip('y1', '🚭 เลิกบุหรี่', 'green', 190, t, mk(9, 'quit', .3), be(9) - .1);
    chip('y2', '💗 เหงือกชมพู แข็งแรง', 'dark', 320, t, mk(9, 'pink', .55), be(9) - .1, -2);
  } else { stain(.15); blood(L, t, 0); setCam('wide', 'wide', 0); }
  return { blur, flash };
}

// cover: the cigarette's smoke drifting over stained teeth and a pale, swollen gum
export function cover(t, L) {
  const { cam, GUM_TOP, halo, lerp, clamp } = L;
  if (!vessels[1].userData.cx) vessels.forEach((v, i) => { v.userData.cx = i ? [-2.5, -1.5, -.5, .5, 1.5, 2.5][i - 1] * L.SP : 0; });
  L.upper.position.y = 40;
  L.enamel.color.set(WHITE).lerp(new L.THREE.Color(STAIN), .8);
  calculus(L, 1, 1); papillae(L, .8, .6, .7); blood(L, t, 1);
  cigOn(L, t); cig.position.set(2.2, 5.4, 3.2); smoke(L, t + 1.5, .8, [2.2, 5.4, 3.2]);
  halo.material.opacity = .2; halo.position.set(0, GUM_TOP + 1.5, -1);
  const k = clamp(t / 2);
  cam.position.set(lerp(4.5, 4.2, k), lerp(7.2, 7, k), lerp(19.5, 18, k)); cam.lookAt(0.6, 4.4, 0);
  return [
    { text: 'บุหรี่', at: [3.6, 5.4, 3.2], dx: 0, dy: 50 },
    { text: 'เหงือก', at: [-1.875, GUM_TOP + .9, .9], dx: 30, dy: 40 },
    { text: 'เส้นเลือด', at: [1.9, -.45, .2], dx: -40, dy: 40 },
  ];
}

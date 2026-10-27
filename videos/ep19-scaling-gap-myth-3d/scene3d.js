// ep19 ขูดหินปูนทำให้ฟันห่าง จริงไหม? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the jaw cut-away. Plaque (yellow film) at the necks of the 3 middle teeth hardens into calculus (tartar) that also
// bridges the spaces between the teeth -> swollen red gum papillae (gingivitis) -> bone loss pocket + wobble (periodontitis)
// -> ultrasonic scaler shatters the calculus -> swelling goes down and the spaces that the calculus filled show ->
// myth twist: the gaps were already there, hidden by calculus -> brush / floss / check-ups -> payoff.
let rings = [], bridges = [], paps = [], papMat, calcMat, pocket = [], pocketMat, scaler, mist = [], chunks = [], mouth, gapGlow = [], ghostMat, ghosts = [];
const PLAQUE = '#f3e27a', CALC = '#c7a35a', GUM = '#ee8399', GUMRED = '#d9364f';
const GX = [-1.875, 1.875];   // interdental spaces either side of the x=0 tooth

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
  // calculus rings around the necks of the teeth at x = -SP, 0, +SP (parented so they move with the tooth)
  const hosts = [L.neighbors[2], L.centerTooth, L.neighbors[3]];
  hosts.forEach((h, i) => { const g = bumpy(THREE, new THREE.TorusGeometry(1.5, .3, 14, 64), .14, i * 1.7); const m = new THREE.Mesh(g, calcMat);
    m.rotation.x = Math.PI / 2; m.scale.set(1, .86, .8); m.position.y = GUM_TOP + .22 - .7; m.castShadow = true; h.add(m); rings.push(m); });
  // calculus bridges that fill the spaces between the teeth
  [-1.5, -.5, .5, 1.5].forEach((k, i) => { const m = new THREE.Mesh(bumpy(THREE, new THREE.SphereGeometry(.62, 28, 18), .16, i * 2.3), calcMat);
    m.position.set(k * SP, GUM_TOP + .45, .35); m.scale.set(1, .95, 1.1); m.castShadow = true; scene.add(m); bridges.push(m); });
  // gum papillae between the teeth (swell when inflamed, shrink back after cleaning)
  papMat = new THREE.MeshPhysicalMaterial({ color: GUM, roughness: .45, clearcoat: .6, clearcoatRoughness: .3 });
  [-1.5, -.5, .5, 1.5].forEach(k => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20, 0, Math.PI * 2, 0, Math.PI / 2), papMat);
    m.position.set(k * SP, GUM_TOP - .02, .1); m.receiveShadow = true; scene.add(m); paps.push(m); });
  // periodontal pocket: dark wedges in the bone either side of the x=0 root (bone being lost)
  pocketMat = new THREE.MeshStandardMaterial({ color: '#8a4a3c', transparent: true, opacity: 0, roughness: .8, side: THREE.DoubleSide, depthWrite: false });
  [-1, 1].forEach(s => { const sh = new THREE.Shape(); sh.moveTo(s * .95, .02); sh.lineTo(s * 2.4, .02); sh.lineTo(s * 1.05, -1); sh.closePath();
    const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), pocketMat); m.position.z = .03; scene.add(m); pocket.push(m); });
  // ultrasonic scaler: handle + thin bent tip (tip at the group origin)
  scaler = new THREE.Group(); scene.add(scaler);
  { const grip = new THREE.MeshPhysicalMaterial({ color: '#7FD3FF', roughness: .3, clearcoat: 1 });
    const h = new THREE.Mesh(new THREE.CapsuleGeometry(.42, 6.5, 8, 20), grip); h.position.y = 5.6; h.castShadow = true; scaler.add(h);
    const n = new THREE.Mesh(new THREE.CylinderGeometry(.2, .42, 1.4, 20), titanium); n.position.y = 1.9; scaler.add(n);
    const t1 = new THREE.Mesh(new THREE.CylinderGeometry(.07, .17, 1.4, 12), titanium); t1.position.set(0, .75, 0); t1.rotation.z = .25; scaler.add(t1);
    const t2 = new THREE.Mesh(new THREE.CylinderGeometry(.04, .07, .6, 10), titanium); t2.position.set(.12, .12, 0); t2.rotation.z = -.5; scaler.add(t2); }
  const mistMat = new THREE.MeshStandardMaterial({ color: '#bfe9ff', transparent: true, opacity: .8, roughness: .1 });
  for (let i = 0; i < 18; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.08 + rnd() * .07, 10, 8), mistMat); m.userData = { a: rnd() * 6.28, v: 1.5 + rnd() * 2, ph: rnd() }; scene.add(m); mist.push(m); }
  // calculus chunks that fly off
  for (let i = 0; i < 26; i++) { const m = new THREE.Mesh(bumpy(THREE, new THREE.IcosahedronGeometry(.18 + rnd() * .16, 1), .2, i), calcMat);
    const x0 = [-SP, -SP / 2, 0, SP / 2, SP][i % 5] + (rnd() - .5) * .8;
    m.userData = { p: new THREE.Vector3(x0, GUM_TOP + .3 + rnd() * .4, .9 + rnd() * .4), v: new THREE.Vector3((rnd() - .5) * 7, 4 + rnd() * 4, 2 + rnd() * 3), d: rnd() * .5, r: rnd() * 9 };
    m.castShadow = true; scene.add(m); chunks.push(m); }
  // dark mouth backdrop + yellow glows that show the spaces between the teeth
  mouth = new THREE.Mesh(new THREE.PlaneGeometry(12, 3.4), new THREE.MeshBasicMaterial({ color: '#4a1d2a', transparent: true, opacity: 0, depthWrite: false }));
  mouth.position.set(0, GUM_TOP + 1.7, -2.3); scene.add(mouth);
  const gTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 20, 64, 64, 64); gr.addColorStop(0, 'rgba(255,225,77,0)'); gr.addColorStop(.6, 'rgba(255,225,77,.95)'); gr.addColorStop(1, 'rgba(255,225,77,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  GX.forEach(x => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: gTex, transparent: true, depthWrite: false, opacity: 0 })); s.position.set(x, GUM_TOP + .55, 1.2); s.scale.set(1.8, 1.8, 1); scene.add(s); gapGlow.push(s); });
  // ghost calculus (myth twist: "it was there all along, hiding the gap")
  ghostMat = new THREE.MeshStandardMaterial({ color: CALC, transparent: true, opacity: 0, roughness: .7, depthWrite: false });
  GX.forEach((x, i) => { const m = new THREE.Mesh(bridges[1 + i].geometry, ghostMat); m.position.copy(bridges[1 + i].position); m.scale.copy(bridges[1 + i].scale); scene.add(m); ghosts.push(m); });
  L.onReset(() => {
    rings.forEach(r => { r.visible = false; r.scale.set(1, .86, .8); }); bridges.forEach(b => { b.visible = false; b.scale.set(1, .95, 1.1); });
    calcMat.color.set(PLAQUE); calcMat.opacity = 1;
    paps.forEach(p => p.scale.set(.85, .32, 1.1)); papMat.color.set(GUM);
    pocketMat.opacity = 0; pocket.forEach(p => p.scale.set(1, 1, 1));
    scaler.visible = false; scaler.rotation.set(0, 0, 0); mist.forEach(m => m.visible = false); chunks.forEach(c => c.visible = false);
    mouth.material.opacity = 0; gapGlow.forEach(g => g.material.opacity = 0); ghostMat.opacity = 0;
  });
}

// set the calculus state: grow 0..1 (plaque film appears), hard 0..1 (yellow plaque -> brown calculus), shrink 0..1 (scaled away)
function calculus(L, grow, hard, shrink = 0) {
  const s = L.clamp(grow) * (1 - L.clamp(shrink)); if (s <= 0) return;
  calcMat.color.set(PLAQUE).lerp(new L.THREE.Color(CALC), L.clamp(hard)); calcMat.opacity = .55 + .45 * L.clamp(hard);
  rings.forEach(r => { r.visible = true; r.scale.set(.92 + .08 * s, .86 * s, .8 * (.4 + .6 * s)); });
  bridges.forEach(b => { b.visible = hard > .05; const k = L.clamp(hard) * s; b.scale.set(k, .95 * k, 1.1 * k); });
}
// papillae: swell 0..1, red 0..1, shrunk 0..1 (smaller than normal: the spaces show)
function papillae(L, swell, red, shrunk = 0) {
  paps.forEach(p => p.scale.set(.85 + .35 * swell - .2 * shrunk, .32 + 1.05 * swell - .14 * shrunk, 1.1 + .3 * swell));
  papMat.color.set(GUM).lerp(new L.THREE.Color(GUMRED), red);
}
function scalerAt(L, t, x, y, on) {
  scaler.visible = true; const j = on ? .05 : 0;
  scaler.position.set(x + Math.sin(t * 90) * j, y + Math.cos(t * 77) * j, 1.25); scaler.rotation.set(-.35, 0, -.55);
  if (on) mist.forEach(m => { const u = m.userData; const k = ((t * 1.6 + u.ph) % 1); m.visible = true;
    m.position.set(x + Math.cos(u.a) * k * u.v * .7, y + .2 + Math.sin(u.a) * k * u.v * .5 + k * .6, 1.4 + k * .8); m.scale.setScalar(1 - k); });
}

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, lerp, clamp, GUM_TOP, setCam, chip, sparkleAt, centerTooth: ct, inflam, inflamF, brush, SHOTS } = L;
  SHOTS.front = [[0, 4.4, 15.5], [0, 2.7, 0]];
  SHOTS.front2 = [[2.5, 5.2, 13], [0, 2.9, 0]];
  SHOTS.pocket = [[4, 1.2, 17], [0, -.6, 0]];
  let blur = 0, flash = 0;
  const hardT = mk(1, 'hard', .55), swellT = mk(3, 'swell', .3), boneT = mk(4, 'bone', .35), wobT = mk(4, 'wobble', .85);
  const breakT = mk(5, 'break', .7), shrinkT = mk(6, 'shrink', .3), gapT = mk(6, 'gap', .55);
  const redOn = k => { inflam.material.opacity = .5 * k; inflamF.material.opacity = .4 * k; };
  const whip = a => t < a + .35 ? (1 - seg(t, a, a + .35)) * 13 : 0;
  // persistent state after each stage
  const afterScale = () => { papillae(L, 0, 0, 1); pocketMat.opacity = .55; };

  if (t < be(0)) {                       // hook: "scaling makes gaps?" — the scaler hovers, a question
    const a = bs(0), d = B[0].dur; papillae(L, 0, 0);
    const k = eout(seg(t, a + .1, a + .9));
    scalerAt(L, t, lerp(6, 1.6, k), lerp(9, 2.2, k) + .15 * Math.sin(t * 4), false);
    const q = mk(0, 'q', .6);
    if (t > q) { const kk = ease(seg(t, q, q + .5)); scaler.position.x += 5 * kk; scaler.position.y += 4 * kk; }
    setCam('wide', 'front2', ease(seg(t, a + .3, a + d)));
    chip('h1', 'ขูดหินปูน = ฟันห่าง ?', 'dark', 190, t, a + .5, be(0) - .1);
  } else if (t < be(1)) {                // plaque film -> hardens to calculus
    const a = bs(1), d = B[1].dur; papillae(L, 0, 0);
    const pl = mk(1, 'plaque', .3);
    calculus(L, eout(seg(t, pl, pl + 1)), seg(t, hardT, hardT + 1.2));
    blur = whip(a);
    if (t > hardT + 1.2) sparkleAt(0, GUM_TOP + .5, 1, seg(t, hardT + 1.2, hardT + 1.8), 2.4);
    setCam('front2', 'front', ease(seg(t, a, a + d)));
    chip('pl', 'คราบจุลินทรีย์ (Plaque)', 'yel', 190, t, pl + .2, hardT + .1);
    chip('ca', 'หินปูน (Calculus)', 'dark', 190, t, hardT + .3, be(1) - .1);
  } else if (t < be(2)) {                // brush harder… calculus stays
    const a = bs(2), d = B[2].dur; papillae(L, 0, 0); calculus(L, 1, 1);
    const bk = seg(t, mk(2, 'brush', 0) + .1, be(2) - .3);
    brush.visible = bk > 0 && bk < 1; brush.position.set(Math.sin(bk * Math.PI * 7) * 2.8, GUM_TOP + 1.6, 2.1); brush.rotation.set(0, 0, Math.sin(t * 34) * .06);
    const fail = mk(2, 'fail', .7);
    setCam('front', 'front', 0, bk > 0 && bk < 1 ? .06 : 0, t);
    chip('b1', '🪥 แปรงแรงๆ', 'green', 190, t, mk(2, 'brush', 0) + .1, mk(2, 'but', .45) - .05);
    chip('b2', '✕ แปรงไม่ออก!', 'red', 190, t, fail, be(2) - .1, -3);
  } else if (t < be(3)) {                // germs -> swollen red gums (gingivitis)
    const a = bs(3), d = B[3].dur; calculus(L, 1, 1);
    L.germsArrive(t, mk(3, 'germ', .1));
    const sw = eout(seg(t, swellT, swellT + 1.2)); papillae(L, sw, sw); redOn(sw);
    blur = whip(a);
    setCam('front', 'gumline', ease(seg(t, a, a + d * .8)));
    chip('gi', 'เหงือกอักเสบ (Gingivitis)', 'red', 190, t, mk(3, 'term', .75), be(3) - .1, 2);
  } else if (t < be(4)) {                // deeper: bone loss pocket + wobble (periodontitis)
    const a = bs(4), d = B[4].dur; calculus(L, 1, 1); papillae(L, 1, 1); redOn(1);
    L.germsArrive(t, a - 5);
    const pk = eout(seg(t, boneT, boneT + 1.4)); pocketMat.opacity = .85 * pk; pocket.forEach(p => p.scale.set(1, .2 + 2.6 * pk, 1));
    L.germs.forEach((g, i) => { if (i % 2) { g.position.y -= 2.4 * pk * (.5 + (i % 5) * .15); g.position.z = .5; } });
    const w = t > wobT - .1 ? Math.sin((t - wobT) * 20) * .07 * clamp((t - wobT + .1) * 3) : 0; ct.rotation.z = w; ct.position.x = -w * 2;
    L.warn.material.opacity = t > wobT ? .85 * (.5 + .5 * Math.sin((t - wobT) * 14)) : 0; L.warn.position.set(0, 1.5, .6);
    blur = whip(a);
    setCam('gumline', 'pocket', ease(seg(t, a, boneT + 1)), t > wobT ? .06 : 0, t);
    chip('bl', 'กระดูกรอบรากถูกทำลาย', 'red', 190, t, boneT + .3, mk(4, 'term', .6) - .05);
    chip('pe', 'โรคปริทันต์ (Periodontitis)', 'dark', 190, t, mk(4, 'term', .6), be(4) - .1);
    chip('wb', '⚠ ฟันโยก!', 'red', 330, t, wobT, be(4) - .1, -3);
  } else if (t < be(5)) {                // ultrasonic scaling shatters the calculus
    const a = bs(5), d = B[5].dur; pocketMat.opacity = .85 - .3 * seg(t, breakT, be(5)); pocket.forEach(p => p.scale.set(1, 2.8, 1));
    const sh = seg(t, breakT, breakT + 1.1);
    calculus(L, 1, 1, sh); const rd = 1 - .5 * sh; papillae(L, 1 - .3 * sh, rd); redOn(rd);
    L.germsClear(t, breakT, breakT + 1);
    const usT = mk(5, 'us', .35), on = t > usT;
    const ki = eout(seg(t, a + .2, usT)); const sweep = Math.sin(seg(t, usT, be(5)) * Math.PI * 3);
    scalerAt(L, t, lerp(7, 0, ki) + 1.9 * sweep, lerp(9, GUM_TOP + .55, ki), on);
    chunks.forEach(c => { const u = c.userData; const tt = t - breakT - u.d; c.visible = tt > 0 && tt < 1.4;
      if (c.visible) { c.position.set(u.p.x + u.v.x * tt, u.p.y + u.v.y * tt - 9 * tt * tt, u.p.z + u.v.z * tt); c.rotation.set(tt * u.r, tt * 5, 0); } });
    if (t > breakT) flash = .25 * Math.exp(-(t - breakT) * 10);
    blur = whip(a);
    setCam('pocket', 'front', ease(seg(t, a, a + 1.2)), on ? .05 : 0, t);
    chip('sc', 'ขูดหินปูน (Scaling)', 'green', 190, t, usT - .1, be(5) - .1);
    chip('us', '〰 อัลตราโซนิก', 'dark', 320, t, usT + .3, be(5) - .1);
  } else if (t < be(6)) {                // swelling goes down -> the spaces show
    const a = bs(6), d = B[6].dur; pocketMat.opacity = .55;
    const sk = eout(seg(t, shrinkT, shrinkT + 1.3)); papillae(L, .7 * (1 - sk), .5 * (1 - sk), sk); redOn(.5 * (1 - sk));
    const gk = seg(t, gapT, gapT + .6);
    gapGlow.forEach(g => g.material.opacity = gk * (.65 + .35 * Math.sin(t * 8)));
    setCam('front', 'front2', ease(seg(t, a, a + d)) * .35);
    chip('sh', 'เหงือกยุบ = หายบวม', 'green', 190, t, shrinkT + .2, be(6) - .1);
    chip('gp', '👀 เห็นช่องระหว่างฟัน', 'yel', 330, t, gapT + .2, be(6) - .1);
  } else if (t < be(7)) {                // myth twist: the gap was always there, calculus hid it
    const a = bs(7), d = B[7].dur; afterScale();
    const no = mk(7, 'no', .45), hid = mk(7, 'hidden', .65);
    gapGlow.forEach(g => g.material.opacity = t < no ? .5 + .3 * Math.sin(t * 8) : .2);
    const gh = t > hid ? Math.sin(seg(t, hid, be(7) - .1) * Math.PI) : 0; ghostMat.opacity = .7 * Math.min(1, gh * 2.5);
    ghosts.forEach(m => m.scale.setScalar(.6 + .4 * eout(seg(t, hid, hid + .4))));
    blur = whip(a);
    setCam('ortho', 'front', ease(seg(t, a, a + 1.2)), t > no && t < no + .3 ? .1 : 0, t);
    chip('m1', 'ขูดแล้วฟันห่าง ?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่จริง!', 'red', 190, t, no, hid - .05, -4);
    chip('m3', 'ช่องมีอยู่แล้ว หินปูนบังไว้', 'green', 190, t, hid, be(7) - .1);
  } else if (t < be(8)) {                // brush + floss + check-ups -> healthy pink gums
    const a = bs(8), d = B[8].dur; afterScale();
    const bk = seg(t, a + .1, a + d * .45);
    brush.visible = bk > 0 && bk < 1; brush.position.set(Math.sin(bk * Math.PI * 4) * 3.2, GUM_TOP + 1.6, 2.1); brush.rotation.set(0, 0, Math.sin(t * 30) * .04);
    if (bk >= 1) sparkleAt(0, GUM_TOP + 1.2, 1, seg(t, a + d * .45, a + d * .45 + .7), 3.4);
    setCam('front', 'wide', ease(seg(t, a + d * .4, a + d)) * .5);
    chip('c1', '🪥 แปรงวันละ 2 ครั้ง', 'green', 170, t, mk(8, 'c1', 0), be(8) - .1);
    chip('c2', '🧵 ใช้ไหมขัดฟัน', 'dark', 300, t, mk(8, 'c2', .4), be(8) - .1);
    chip('c3', '🦷 ตรวจฟันทุก 6 เดือน', 'yel', 430, t, mk(8, 'c3', .62), be(8) - .1);
  } else if (t < be(9)) {                // payoff
    const a = bs(9), d = B[9].dur; afterScale();
    L.confetti(t, a); sparkleAt(0, 3, 0, seg(t, a, a + .9), 3.8);
    L.upper.position.y = 11 - 7.4 * Math.pow(Math.max(0, Math.sin((t - a) * 2 * Math.PI)), 2) * clamp((t - a) * 2);
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
    chip('ok', '💪 เหงือกแข็งแรง', 'green', 190, t, a + .4, be(9) - .1);
  } else { afterScale(); setCam('wide', 'wide', 0); }
  return { blur, flash };
}

// cover: close-up of the neck of the tooth with a ring of calculus, swollen gum, the scaler coming in
export function cover(t, L) {
  const { cam, GUM_TOP, halo, sparkleAt, lerp, clamp } = L;
  L.upper.position.y = 40;
  calculus(L, 1, 1); papillae(L, .8, .7); L.inflam.material.opacity = .4; L.inflamF.material.opacity = .3;
  scalerAt(L, t, 1.6 + .2 * Math.sin(t * 3), GUM_TOP + 1.4 + .2 * Math.sin(t * 2.2), true);
  halo.material.opacity = .25; halo.position.set(0, GUM_TOP + 1.5, -1);
  sparkleAt(1.5, GUM_TOP + 1.5, 0, (t * .7) % 1, 3);
  const k = clamp(t / 2);
  cam.position.set(lerp(4.5, 4, k), lerp(7.5, 7.2, k), lerp(19, 17, k)); cam.lookAt(0, 4.6, 0);
  return [
    { text: 'เหงือกบวม', at: [-1.875, GUM_TOP + .9, .9] },
    { text: 'หินปูน', at: [.2, GUM_TOP + .15, 1.4], dy: 10 },
  ];
}

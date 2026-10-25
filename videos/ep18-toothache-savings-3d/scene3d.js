// ep18 ปวดฟันแล้วปล่อยไว้ เงินเก็บอาจหายหมด! — cut3d episode (L = tools/cut3d/lib.js)
// Set: the x=0 tooth is cut in half (back half 3D, front = a flat cross-section showing enamel, dentin, pulp + canals).
// A cavity grows to the pulp -> pulp inflamed -> abscess at the root tip -> infection spreads -> extraction + implant.
// A "เงินเก็บ" (savings) meter on the left drains at every stage, and refills when the cavity is caught early.
let ct, sec = {}, cav, cav3, fil, fil3, pill, ghost, abscess, absGlow, spread = [], canalGerms = [], wallet, rope, hud, P;
const PULP = { ok: '#f0788a', hot: '#e3203f', dead: '#8d7f7c' };

function outline(THREE) {
  const R = [[0.18, -1.3], [0.54, -5.9], [0.72, -6.05], [0.9, -5.9], [1.12, -3], [1.38, -0.6], [1.32, 0], [1.6, 0.7], [1.74, 1.6], [1.68, 2.35], [1.5, 2.85], [1.15, 3.18], [0.7, 2.95], [0.25, 2.82]];
  const pts = [[0, -1.1], ...R, [0, 2.8], ...R.slice().reverse().map(([x, y]) => [-x, y])];
  return pts;
}
const shapeOf = (THREE, pts) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y)); s.closePath(); return s; };
function blobGeo(THREE, seed) { const g = new THREE.CircleGeometry(1, 48); const p = g.attributes.position;
  for (let i = 1; i < p.count; i++) { const a = Math.atan2(p.getY(i), p.getX(i)); const r = 1 + .13 * Math.sin(5 * a + seed) + .08 * Math.sin(9 * a + seed * 2); p.setXY(i, Math.cos(a) * r, Math.sin(a) * r); }
  return g; }

export function setup(L) {
  const { THREE, scene, tooth, canvasTex, rnd, RoundedBoxGeometry } = L;
  L.renderer.localClippingEnabled = true;
  P = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);          // keep z <= 0 (the back half)
  const en = L.enamel.clone(); en.clippingPlanes = [P]; en.clipShadows = true; en.side = THREE.DoubleSide;
  const rm = L.rootMat.clone(); rm.clippingPlanes = [P]; rm.clipShadows = true; rm.side = THREE.DoubleSide;
  ct = tooth(0, true, en); ct.children[1].material = rm;
  // ---- the cross-section face (children of the tooth, local coords)
  const O = outline(THREE);
  const flat = (pts, color, z) => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), new THREE.MeshStandardMaterial({ color, roughness: .55, side: THREE.DoubleSide })); m.position.z = z; ct.add(m); return m; };
  sec.base = flat(O, '#efdcae', .006);
  const crownPts = O.filter(([x, y]) => y > .25); crownPts.unshift([1.45, .3]); crownPts.push([-1.45, .3]);
  sec.enamel = flat(crownPts.sort((a, b) => Math.atan2(a[1] - 1.2, a[0]) - Math.atan2(b[1] - 1.2, b[0])), '#fbf8f1', .010);
  const dent = O.map(([x, y]) => y > -0.6 ? [x * .82, y > 2 ? 2 + (y - 2) * .72 : y] : [Math.sign(x) * (.72 + (Math.abs(x) - .72) * .62), y * .975]);
  sec.dentin = flat(dent, '#f2d9a4', .014);
  const pulpPts = [[-0.55, 0.1], [-0.62, 1.2], [-0.5, 1.8], [-0.25, 1.45], [0, 1.5], [0.25, 1.45], [0.5, 1.8], [0.62, 1.2], [0.55, 0.1]];
  const pm = new THREE.MeshStandardMaterial({ color: PULP.ok, roughness: .45, emissive: '#000000', side: THREE.DoubleSide });
  sec.pulpMat = pm;
  [pulpPts, [[-0.62, 0.2], [-0.32, 0.2], [-0.69, -5.6], [-0.77, -5.6]], [[0.62, 0.2], [0.32, 0.2], [0.69, -5.6], [0.77, -5.6]]]
    .forEach(pts => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), pm); m.position.z = .018; ct.add(m); });
  // cavity on the section + a dark patch on the chewing surface; the filling likewise
  cav = new THREE.Mesh(blobGeo(THREE, 1.3), new THREE.MeshStandardMaterial({ color: '#4a2c16', roughness: .8, side: THREE.DoubleSide })); cav.position.z = .024; ct.add(cav);
  cav3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), cav.material); ct.add(cav3);
  fil = new THREE.Mesh(blobGeo(THREE, 2.1), new THREE.MeshPhysicalMaterial({ color: '#9fd0ff', roughness: .25, clearcoat: 1, side: THREE.DoubleSide })); fil.position.z = .028; ct.add(fil);
  fil3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), fil.material); ct.add(fil3);
  // painkiller capsule
  pill = new THREE.Group(); scene.add(pill);
  { const a = new THREE.Mesh(new THREE.CapsuleGeometry(.42, .6, 8, 20), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .25, clearcoat: 1 })); a.position.y = -.3; a.scale.y = .5;
    const b = new THREE.Mesh(new THREE.CapsuleGeometry(.42, .6, 8, 20), new THREE.MeshPhysicalMaterial({ color: '#ff5a5f', roughness: .25, clearcoat: 1 })); b.position.y = .3; b.scale.y = .5;
    pill.add(a, b); pill.rotation.z = .9; }
  // ghost crown = "you would also need a crown"
  ghost = tooth(0, false, new THREE.MeshPhysicalMaterial({ color: '#9fd8ff', transparent: true, opacity: .45, roughness: .2, clearcoat: 1, depthWrite: false }));
  ghost.children[0].scale.set(1.08, 1.05, 1.08);
  // abscess at the root tip + red glows
  abscess = new THREE.Mesh(new THREE.SphereGeometry(.85, 32, 20), new THREE.MeshPhysicalMaterial({ color: '#e9cf5a', roughness: .3, clearcoat: .8, transparent: true, opacity: .9, emissive: '#7a5a00', emissiveIntensity: .25 }));
  abscess.position.set(.75, -5.6, .35); scene.add(abscess);
  const redTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,50,70,.95)'); gr.addColorStop(1, 'rgba(255,50,70,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  const glow = () => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: redTex, transparent: true, depthWrite: false })); scene.add(s); return s; };
  absGlow = glow();
  for (let i = 0; i < 12; i++) { const s = glow(); s.userData = { dir: i % 2 ? 1 : -1, d: Math.floor(i / 2) * .16, y: -1.5 + (i % 3) * 1.2 }; spread.push(s); }
  // germs travelling down the canals
  const gm = new THREE.Mesh(L.germGeo, L.germMat);
  for (let i = 0; i < 10; i++) { const m = gm.clone(); m.userData = { side: i % 2 ? 1 : -1, d: (i >> 1) * .14, ph: rnd() * 6 }; scene.add(m); canalGerms.push(m); }
  // wallet (cover + payoff): leather body, strap, gold snap, banknotes; pink rope (cover)
  wallet = new THREE.Group(); scene.add(wallet);
  { const lea = new THREE.MeshPhysicalMaterial({ color: '#8b5a2b', roughness: .55, clearcoat: .3 });
    const body = new THREE.Mesh(new RoundedBoxGeometry(4.2, 3, .8, 4, .28), lea); body.castShadow = true; wallet.add(body);
    const strap = new THREE.Mesh(new RoundedBoxGeometry(1.5, 1.1, .2, 3, .08), new THREE.MeshPhysicalMaterial({ color: '#6e4420', roughness: .5 })); strap.position.set(1.45, 0, .45); wallet.add(strap);
    const snap = new THREE.Mesh(new THREE.CylinderGeometry(.2, .2, .12, 24), new THREE.MeshStandardMaterial({ color: '#e8c25a', metalness: 1, roughness: .25 })); snap.rotation.x = Math.PI / 2; snap.position.set(1.85, 0, .58); wallet.add(snap);
    const nm = new THREE.MeshStandardMaterial({ color: '#7fcf8f', roughness: .7, side: THREE.DoubleSide });
    [-.6, 0, .55].forEach((x, i) => { const n = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.1), nm); n.position.set(x - .6, 1.75, .05 - i * .12); n.rotation.z = (i - 1) * .18; wallet.add(n); }); }
  const ropeMat = new THREE.MeshStandardMaterial({ color: '#e0457b', roughness: .6 });
  rope = new THREE.Group(); scene.add(rope);
  [-1.1, -.2, .7].forEach((x, i) => { const pts = [];
    for (let k = 0; k <= 40; k++) { const a = k / 40 * Math.PI * 2; pts.push(new THREE.Vector3(x + Math.sin(a * 3) * .05 + i * .05, Math.cos(a) * 1.62, Math.sin(a) * .55)); }
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 80, .1, 8, true), ropeMat); m.rotation.z = (i - 1) * .12; rope.add(m); });
  rope.userData.mat = ropeMat;
  // ---- the savings meter (DOM, left edge)
  hud = document.createElement('div');
  hud.style.cssText = 'position:absolute;left:28px;top:290px;width:150px;text-align:center;display:none;transform-origin:50% 0;z-index:5';
  hud.innerHTML = `<div style="font-size:40px;color:#fff;-webkit-text-stroke:11px #16324F;paint-order:stroke fill">เงินเก็บ</div>
    <div class="ic" style="font-size:72px;line-height:86px">💰</div>
    <div style="position:relative;margin:0 auto;width:74px;height:380px;border:8px solid #16324F;border-radius:44px;background:rgba(255,255,255,.9);overflow:hidden;box-shadow:0 10px 0 rgba(22,50,79,.35)">
      <div class="f" style="position:absolute;left:0;right:0;bottom:0;height:100%;background:#2EC4B6"></div>
      <div style="position:absolute;left:12px;top:14px;width:14px;bottom:14px;border-radius:8px;background:rgba(255,255,255,.35)"></div></div>`;
  document.body.appendChild(hud);
  hud.f = hud.querySelector('.f'); hud.ic = hud.querySelector('.ic'); hud.fly = [];
  for (let i = 0; i < 6; i++) { const s = document.createElement('div'); s.textContent = '💸'; s.style.cssText = 'position:absolute;font-size:60px;display:none;z-index:6'; document.body.appendChild(s); hud.fly.push(s); }
  Object.assign(L.SHOTS, {
    secW: [[2.2, 0.3, 19.5], [0, -0.9, 0]],      // whole cut tooth, crown in the upper part
    secC: [[1.6, 2.4, 12], [0, 1.2, 0]],         // crown + pulp chamber
    tip: [[2.4, -3.8, 13], [0.5, -4.4, 0]],      // root tip + abscess
    out: [[6, 5, 30], [0, 0, 0]],                // wide, a bit lower than 'wide'
  });
  L.onReset(() => {
    L.centerTooth.visible = false;
    ct.visible = true; ct.position.set(0, .7, 0); ct.rotation.set(0, 0, 0);
    [cav, cav3, fil, fil3, pill, ghost, abscess, absGlow, wallet, rope, ...spread, ...canalGerms].forEach(o => o.visible = false);
    sec.pulpMat.color.set(PULP.ok); sec.pulpMat.emissive.set('#000000');
    abscess.scale.setScalar(1); absGlow.material.opacity = 1;
    wallet.position.set(0, 0, 0); wallet.rotation.set(0, 0, 0); wallet.scale.setScalar(1);
    hud.style.display = 'none'; hud.fly.forEach(s => s.style.display = 'none');
  });
}

// cavity stage k: 0 = tiny pit in the enamel, ~.5 = into the dentin, 1 = touching the pulp horn
function setCavity(L, k) {
  cav.visible = cav3.visible = k > 0;
  const r = L.lerp(.2, .7, k); cav.position.set(L.lerp(-0.98, -0.56, k), L.lerp(2.72, 2.12, k), .024); cav.scale.set(r, r, 1);
  cav3.position.set(-.85, 2.93, -.5); cav3.scale.set(L.lerp(.25, .6, k), .1, L.lerp(.2, .45, k));
}
function setFilling(L, k) { fil.visible = fil3.visible = k > 0; const s = L.back(k);
  fil.position.set(-0.98, 2.72, .028); fil.scale.set(.3 * s, .3 * s, 1); fil3.position.set(-.85, 2.95, -.5); fil3.scale.set(.3 * s, .11, .25 * s); }

function money(t, L, K) {
  const { seg, eout, lerp, clamp } = L;
  let lv = K[0][1], lastDrop = -1;
  for (let i = 1; i < K.length; i++) { const k = eout(seg(t, K[i][0], K[i][0] + .6)); if (K[i][1] < K[i - 1][1] && t >= K[i][0]) lastDrop = K[i][0]; lv = lerp(lv, K[i][1], k); }
  hud.style.display = 'block';
  hud.f.style.height = (lv * 100).toFixed(1) + '%';
  hud.f.style.background = lv > .6 ? '#2EC4B6' : lv > .3 ? '#FFC93C' : '#FF5A5F';
  const shake = lv < .12 ? Math.sin(t * 38) * 5 : 0;
  hud.style.transform = `translateX(${shake}px) scale(${1 + (lastDrop >= 0 ? .08 * Math.exp(-(t - lastDrop) * 4) * Math.sin((t - lastDrop) * 20) : 0)})`;
  hud.ic.textContent = lv < .12 ? '😱' : '💰';
  if (lastDrop >= 0) hud.fly.forEach((s, j) => { const p = (t - lastDrop - j * .1) / 1.1; s.style.display = p > 0 && p < 1 ? 'block' : 'none'; if (p <= 0 || p >= 1) return;
    const y0 = 290 + 126 + (1 - lv) * 380; s.style.left = (70 + p * 160 + j * 22) + 'px'; s.style.top = (y0 - p * 300 + Math.sin(p * 9 + j) * 12) + 'px'; s.style.opacity = 1 - p * p; s.style.transform = `rotate(${(j % 2 ? 1 : -1) * p * 40}deg)`; });
  return lv;
}

export function frame(t, L) {
  const { bs, be, mk, B, T, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, warn, halo, inflam, inflamF, implant, abut, newCrown, cells } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const pulpT = mk(2, 'pulp', .45), zingT = mk(2, 'zing', .75), costT = mk(3, 'cost', .8), absT = mk(4, 'abs', .55);
  const hospT = mk(5, 'hosp', .75), outT = mk(6, 'out', .25), implT = mk(6, 'impl', .8), fill8 = mk(8, 'fill', .75);
  if (t < T.end.start) money(t, L, [[0, 1], [zingT, .95], [costT, .62], [absT, .5], [hospT, .32], [outT + .3, .2], [implT, .06], [fill8 + .2, .93], [bs(9) + .2, 1]]);
  const LB = 1150, LB2 = 1290, LB3 = 1430;                       // chip rows under the caption (the crown is at the top of the frame)

  if (t < be(0)) {                                   // hook: aching tooth, a painkiller, pain gone... leave it?
    const a = bs(0), d = B[0].dur, pt = mk(0, 'pill', .3);
    setCavity(L, .08);
    const calm = seg(t, pt + .6, pt + 1.2);
    warn.material.opacity = (1 - calm) * .85 * (.5 + .5 * Math.sin(t * 13)); warn.position.set(0, 2.6, 2); warn.scale.setScalar(1.05 + .06 * Math.sin(t * 13));
    if (t > pt) { pill.visible = t < pt + 1.1; const k = seg(t, pt, pt + .9); pill.position.set(lerp(3, 0, k), lerp(9, 4.5, eout(k)), 2.5); pill.rotation.set(0, k * 6, .9 + k * 4); pill.scale.setScalar(1 - ein(seg(t, pt + .7, pt + 1.1))); if (k > .75) sparkleAt(0, 4, 2, seg(t, pt + .7, pt + 1.3), 2); }
    setCam('gap', 'neck', ease(seg(t, a + .2, a + d)), (1 - calm) * .12, t);
    chip('ache', '⚡ ปวดฟัน!', 'red', 190, t, a + .2, pt + .55, -3);
    chip('ok', 'กินยาแล้ว หายปวด 😌', 'green', 190, t, pt + .9, be(0) - .1);
  } else if (t < be(1)) {                            // the drug only masks it — the cavity keeps digging
    const a = bs(1), d = B[1].dur;
    setCavity(L, lerp(.08, .5, ease(seg(t, mk(1, 'deep', .4), be(1)))));
    blur = whip(1);
    setCam('neck', 'secW', ease(seg(t, a, a + d * .7)));
    chip('mask', 'ยาแค่ระงับปวด', 'dark', LB, t, a + .3, be(1) - .1);
    chip('dig', 'ฟันผุยังลามลึกลงไป ⬇', 'red', LB2, t, mk(1, 'deep', .4) + .2, be(1) - .1);
  } else if (t < be(2)) {                            // shallow = one filling; deep = pulp -> throbbing pain
    const a = bs(2), d = B[2].dur;
    setCavity(L, lerp(.5, 1, ease(seg(t, pulpT, pulpT + 1))));
    const hot = seg(t, pulpT + .7, zingT);
    sec.pulpMat.color.set(PULP.ok).lerp(new L.THREE.Color(PULP.hot), hot); sec.pulpMat.emissive.set('#ff0020'); sec.pulpMat.emissiveIntensity = hot * (.25 + .25 * Math.sin(t * 14));
    if (t > zingT) { warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - zingT) * 16)); warn.position.set(0, 1.9, .6); warn.scale.setScalar(.75 + .05 * Math.sin(t * 16)); flash = .25 * Math.exp(-(t - zingT) * 10); }
    setCam('secW', 'secC', ease(seg(t, pulpT - .3, pulpT + .8)), t > zingT ? .1 : 0, t);
    chip('shal', 'ผุตื้น = อุดครั้งเดียว ✓', 'green', LB, t, a + .2, pulpT - .05);
    chip('deep', 'ผุถึงโพรงประสาท', 'red', LB, t, pulpT + .5, be(2) - .1);
    chip('zing', '⚡ ปวดจี๊ดทั้งคืน', 'dark', LB2, t, zingT, be(2) - .1, -3);
  } else if (t < be(3)) {                            // bill #1: root canal (several visits) + crown
    const a = bs(3), d = B[3].dur, cr = mk(3, 'crown', .45);
    setCavity(L, 1); sec.pulpMat.color.set(PULP.hot); sec.pulpMat.emissive.set('#ff0020'); sec.pulpMat.emissiveIntensity = .2 + .2 * Math.sin(t * 14);
    if (t > cr) { ghost.visible = true; const k = seg(t, cr, cr + .6); ghost.position.set(0, lerp(8, 1.2, eout(k)) + .15 * Math.sin(t * 3), 0); ghost.children[0].material.opacity = .45 * k; }
    blur = whip(3);
    setCam('secC', 'secW', ease(seg(t, a, a + d * .6)));
    L.calendar('ครั้งที่', Math.min(3, 1 + Math.floor(seg(t, a + .3, cr) * 2.99)), t > be(3) - .3 ? 1 - seg(t, be(3) - .3, be(3)) : back(seg(t, a + .15, a + .5)));
    chip('rc', '🧾 รักษารากฟัน', 'dark', LB, t, a + .3, be(3) - .1);
    chip('cr', '🧾 + ครอบฟัน', 'dark', LB2, t, cr + .1, be(3) - .1);
    chip('x', '💸 ค่าใช้จ่ายเพิ่มหลายเท่า', 'red', LB3, t, costT, be(3) - .1, -2);
  } else if (t < be(4)) {                            // germs down the canals -> abscess in the bone, swollen gum
    const a = bs(4), d = B[4].dur, g0 = mk(4, 'germ', .2);
    setCavity(L, 1); sec.pulpMat.color.set(PULP.hot).lerp(new L.THREE.Color('#7a1f2a'), seg(t, g0, absT));
    canalGerms.forEach(g => { const k = seg(t, g0 + g.userData.d, g0 + 1.4 + g.userData.d); g.visible = k > 0 && k < 1; const s = g.userData.side;
      g.position.set(s * lerp(.45, .74, k), lerp(1.7, -5.3, ein(k * .7 + k * k * .3)), .45); g.scale.setScalar(.55); g.rotation.set(t * 3, t * 2 + g.userData.ph, 0); });
    const ab = eout(seg(t, absT, absT + .9));
    abscess.visible = ab > 0; abscess.scale.setScalar(ab * (1 + .05 * Math.sin(t * 8)));
    absGlow.visible = ab > 0; absGlow.position.set(.75, -5.6, .5); absGlow.scale.setScalar(4 * ab); absGlow.material.opacity = .7;
    const sw = seg(t, mk(4, 'swell', .8), mk(4, 'swell', .8) + .6); inflam.material.opacity = .55 * sw; inflamF.material.opacity = .5 * sw;
    blur = whip(4);
    setCam('secW', 'tip', ease(seg(t, g0, absT + .4)));
    chip('ger', 'เชื้อลงไปถึงปลายราก', 'dark', 190, t, g0 + .2, be(4) - .1);
    chip('abs', 'ฝีหนองในกระดูก!', 'red', 330, t, absT + .3, be(4) - .1, 2);
  } else if (t < be(5)) {                            // infection spreads to the cheek -> hospital
    const a = bs(5), d = B[5].dur, sp = mk(5, 'spread', .3);
    setCavity(L, 1); sec.pulpMat.color.set('#7a1f2a');
    abscess.visible = true; abscess.scale.setScalar(1 + .06 * Math.sin(t * 8)); absGlow.visible = true; absGlow.position.set(.75, -5.6, .5); absGlow.scale.setScalar(4);
    inflam.material.opacity = .55; inflamF.material.opacity = .5; inflam.scale.set(1 + 2.5 * seg(t, sp, sp + 1.5), .8, 1); inflamF.scale.set(1 + 2.5 * seg(t, sp, sp + 1.5), 1, 1);
    spread.forEach(s => { const k = eout(seg(t, sp + s.userData.d, sp + 1.2 + s.userData.d)); s.visible = k > 0; s.position.set(s.userData.dir * (1 + k * 8), s.userData.y, 1); s.scale.setScalar(3 + 3 * k); s.material.opacity = .75 * (.75 + .25 * Math.sin(t * 6)); });
    blur = whip(5);
    setCam('tip', 'out', ease(seg(t, a, a + d * .6)), .03, t);
    chip('face', 'ลามไปที่แก้ม หน้าบวม', 'red', 190, t, mk(5, 'face', .5), be(5) - .1, -2);
    chip('hosp', '🏥 ต้องรีบไปโรงพยาบาล', 'dark', 330, t, hospT, be(5) - .1);
  } else if (t < be(6)) {                            // can't be saved -> extraction -> a replacement tooth (implant)
    const a = bs(6), d = B[6].dur, gp = mk(6, 'gap', .45);
    setCavity(L, 1); sec.pulpMat.color.set('#7a1f2a');
    const ko = seg(t, outT, outT + 1.0);
    ct.position.set(lerp(0, -4, ein(ko)), .7 + 15 * eout(ko), lerp(0, 3, ko)); ct.rotation.set(ko * 2, 0, -ko * 3); ct.visible = ko < 1;
    abscess.visible = ko < .6; abscess.scale.setScalar(1 - seg(ko, 0, .6)); absGlow.visible = abscess.visible; absGlow.position.set(.75, -5.6, .5); absGlow.scale.setScalar(4 * (1 - ko));
    if (ko > 0 && ko < .4) flash = .3 * (1 - ko / .4);
    const ik = seg(t, implT - .9, implT);
    implant.visible = ik > 0; implant.position.y = lerp(13, 0, eout(ik)); implant.rotation.y = -ik * 24;
    if (t > implT) { abut.visible = true; const k = seg(t, implT, implT + .5); abut.position.y = lerp(8, .05, eout(k)); newCrown.visible = t > implT + .4; newCrown.position.set(0, lerp(9, .9, ein(seg(t, implT + .4, implT + .9))), 0);
      if (t > implT + .9) sparkleAt(0, 3, 0, seg(t, implT + .9, implT + 1.6), 3.2); }
    blur = whip(6);
    setCam('out', 'gap', ease(seg(t, a, outT + .6)));
    chip('ext', '🧾 ถอนฟัน', 'dark', 190, t, outT + .3, be(6) - .1);
    chip('imp', '🧾 + ใส่ฟันใหม่ (รากฟันเทียม)', 'dark', 330, t, gp + .2, be(6) - .1);
  } else if (t < be(7)) {                            // myth: no more pain = healed? the nerve may be dead, the germs are not
    const a = bs(7), d = B[7].dur, no = mk(7, 'no', .4), dd = mk(7, 'dead', .6);
    setCavity(L, 1); sec.pulpMat.color.set(t > dd ? PULP.dead : '#7a1f2a');
    if (t > dd) { abscess.visible = true; abscess.scale.setScalar(1 + .06 * Math.sin(t * 8)); absGlow.visible = true; absGlow.position.set(.75, -5.6, .5); absGlow.scale.setScalar(4); }
    blur = whip(7);
    setCam('secW', 'secW', 0);
    chip('m1', 'หายปวด = หายแล้ว?', 'dark', LB, t, a + .2, no - .05);
    chip('m2', '✕ ไม่ใช่!', 'red', LB2, t, no, be(7) - .1, -4);
    chip('m3', 'ประสาทตาย แต่เชื้อยังอยู่', 'red', LB, t, dd + .3, be(7) - .1, 2);
  } else if (t < be(8)) {                            // rewind: see the dentist early -> a small filling
    const a = bs(8), d = B[8].dur;
    if (t < fill8) setCavity(L, .1); else setFilling(L, seg(t, fill8, fill8 + .45));
    if (t > fill8) { sparkleAt(-1.0, 3.5, 0, seg(t, fill8 + .3, fill8 + 1), 1.8); }
    if (t < a + .3) flash = .6 * (1 - seg(t, a, a + .3));
    setCam('secW', 'secC', ease(seg(t, a, fill8)));
    chip('rw', '⏪ ย้อนเวลา', 'yel', 190, t, a + .1, mk(8, 'c1', .3) - .05);
    chip('c1', '🦷 ปวดเมื่อไหร่ รีบหาหมอ', 'green', LB, t, mk(8, 'c1', .2), be(8) - .1);
    chip('c2', '📅 ตรวจทุก 6 เดือน', 'dark', LB2, t, mk(8, 'c2', .5), be(8) - .1);
    chip('c3', 'ผุเล็กๆ อุดก็จบ ✓', 'yel', LB3, t, fill8 + .2, be(8) - .1);
  } else if (t < be(9)) {                            // payoff: the tooth and the savings are safe
    const a = bs(9), d = B[9].dur, sv = mk(9, 'safe', .45);
    setFilling(L, 1); L.confetti(t, a);
    if (t > sv) { wallet.visible = true; const k = seg(t, sv, sv + .6); wallet.position.set(2.5, lerp(12, 5.6, eout(k)) + .2 * Math.sin(t * 3), 3); wallet.rotation.set(-.15, -.45 + .1 * Math.sin(t * 2), .08); wallet.scale.setScalar(.7);
      sparkleAt(2.5, 5.6, 3, (seg(t, sv + .3, be(9)) * 1.6) % 1, 3); }
    setCam('secC', 'gap', ease(seg(t, a, a + d * .8)));
    chip('yay', '💰 ฟันรอด เงินเก็บก็รอด!', 'green', 190, t, sv, be(9) - .1);
  } else {                                           // under the end card
    setFilling(L, 1); setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: the wallet tied with a pink rope, pulled by an aching tooth (homage to the "money tied up" ad look)
export function cover(t, L) {
  const { lerp, clamp, upper, cam, warn, sparkleAt, THREE } = L;
  upper.position.y = 40;
  setCavity(L, .9); sec.pulpMat.color.set(PULP.hot); sec.pulpMat.emissive.set('#ff0020'); sec.pulpMat.emissiveIntensity = .3 + .2 * Math.sin(t * 12);
  warn.material.opacity = .8 * (.5 + .5 * Math.sin(t * 10)); warn.position.set(0, 1.9, .6); warn.scale.setScalar(.8);
  const tug = .25 * Math.sin(t * 3.2);
  wallet.visible = true; wallet.position.set(3.9 - tug, 2.4, 3.2); wallet.rotation.set(-.2, -.5, .12 + tug * .2); wallet.scale.setScalar(.85);
  rope.visible = true; rope.position.copy(wallet.position); rope.rotation.copy(wallet.rotation); rope.scale.setScalar(.85);
  // the pulling strand: from the wallet's left edge to the tooth's crown
  if (!rope.userData.line) { const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(1, 0, 0)), 4, .1, 8), rope.userData.mat); L.scene.add(m); rope.userData.line = m; L.onReset(() => m.visible = false); }
  const ln = rope.userData.line; ln.visible = true;
  const A = new THREE.Vector3(2.2 - tug, 2.5, 3.4), Bv = new THREE.Vector3(.6, 3.2, .4);
  ln.position.copy(Bv); const dv = A.clone().sub(Bv); ln.scale.set(dv.length(), 1, 1); ln.quaternion.setFromUnitVectors(new THREE.Vector3(1, 0, 0), dv.normalize());
  sparkleAt(3.9, 2.4, 3.2, (t * .6) % 1, 3.2);
  const k = clamp(t / 2);
  cam.position.set(lerp(3.4, 3.1, k), lerp(3.4, 3.2, k), lerp(23.5, 22, k)); cam.lookAt(2.0, 5.4, 0);
  return [
    { text: 'ฟันผุ ปวด!', at: [0.6, -0.6, 0.3], dx: 50 },
    { text: 'เงินเก็บ', at: [3.9, 0.8, 3.2], dx: -80, dy: 30 },
  ];
}

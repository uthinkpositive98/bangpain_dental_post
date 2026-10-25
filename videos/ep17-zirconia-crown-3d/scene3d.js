// ep17 ครอบฟันเซอร์โคเนีย ใครต้องทำ? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the natural tooth at x=0 gets a big cavity -> big filling -> crack -> metal-ceramic crown (grey margin)
// -> zirconia shown -> tooth trimmed + scanned -> temporary crown -> zirconia crown seated.
let cavity, filling, crack, pfm, collar, zir, zirMat, scanBeam, dust = [], marginRing;
const CX = 0;

function crownR(y) {           // radius of the lathe crown profile at local y (see lib.js crownGeo)
  const P = [[-.6, 1.3], [0, 1.32], [.7, 1.6], [1.6, 1.74], [2.35, 1.68], [2.8, 1.45], [3.0, 1.0]];
  for (let i = 1; i < P.length; i++) if (y <= P[i][0]) { const k = (y - P[i - 1][0]) / (P[i][0] - P[i - 1][0]); return P[i - 1][1] + (P[i][1] - P[i - 1][1]) * k; }
  return 1.0;
}

export function setup(L) {
  const { THREE, scene, tooth, CROWN, rnd } = L;
  // cavity: a dark pit on the chewing surface; filling: a tooth-coloured blob in the same place
  cavity = new THREE.Mesh(new THREE.SphereGeometry(.95, 32, 16), new THREE.MeshStandardMaterial({ color: '#3b2414', roughness: .85 }));
  cavity.position.set(CX, 3.66, .2); scene.add(cavity);
  filling = new THREE.Mesh(new THREE.SphereGeometry(1.0, 32, 16), new THREE.MeshPhysicalMaterial({ color: '#cfdcea', roughness: .25, clearcoat: 1 }));
  filling.position.set(CX, 3.64, .15); scene.add(filling);
  // crack: a zig-zag line down the front of the crown
  const pts = [];
  for (let i = 0; i <= 14; i++) { const ly = 2.85 - i * .17; const x = (i % 2 ? .18 : -.12) + .1; const r = crownR(ly); pts.push(new THREE.Vector3(CX + x, ly + .7, Math.sqrt(Math.max(0, r * r - x * x)) * .86 + .04)); }
  crack = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, .06, 6, false), new THREE.MeshBasicMaterial({ color: '#2a1608' }));
  scene.add(crack);
  // metal-ceramic crown: porcelain shell + a grey metal collar that shows at the gum line
  pfm = new THREE.Group(); scene.add(pfm);
  const por = new THREE.MeshPhysicalMaterial({ color: '#f6f1e4', roughness: .3, clearcoat: .7 });
  const shell = new THREE.Mesh(CROWN, por); shell.scale.set(1.07, 1.04, 1.07); shell.castShadow = true; pfm.add(shell);
  collar = new THREE.Mesh(new THREE.TorusGeometry(1.66, .11, 12, 64), new THREE.MeshStandardMaterial({ color: '#4a4d55', metalness: .9, roughness: .35 }));
  collar.rotation.x = Math.PI / 2; collar.scale.set(1, .88, 1); collar.position.y = .56; pfm.add(collar);
  // zirconia crown: bright, glossy, slightly pearly
  zirMat = new THREE.MeshPhysicalMaterial({ color: '#fffdf8', roughness: .14, clearcoat: 1, clearcoatRoughness: .08, sheen: .6, sheenColor: new THREE.Color('#dff2ff'), emissive: '#ffffff', emissiveIntensity: 0 });
  zir = tooth(CX, false, zirMat); zir.children[0].scale.set(1.04, 1.02, 1.04);
  // scanner beam: a thin glowing blue sheet that sweeps across the trimmed tooth
  scanBeam = new THREE.Mesh(new THREE.BoxGeometry(.12, 7, 6), new THREE.MeshBasicMaterial({ color: '#46c8ff', transparent: true, opacity: .55, depthWrite: false, blending: THREE.AdditiveBlending }));
  scene.add(scanBeam);
  // trimming dust
  const dm = new THREE.MeshStandardMaterial({ color: '#f4eedd', roughness: .7 });
  for (let i = 0; i < 24; i++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(.07 + rnd() * .07, 0), dm); m.userData = { a: rnd() * Math.PI * 2, v: 2 + rnd() * 3, up: 2 + rnd() * 3, d: rnd() }; scene.add(m); dust.push(m); }
  // red ring at the crown margin (myth beat)
  marginRing = new THREE.Mesh(new THREE.TorusGeometry(1.62, .1, 10, 64), new THREE.MeshBasicMaterial({ color: '#ff3b47', transparent: true, opacity: 0 }));
  marginRing.rotation.x = Math.PI / 2; marginRing.scale.set(1, .86, 1); marginRing.position.set(CX, 1.32, 0); scene.add(marginRing);
  Object.assign(L.SHOTS, {
    top: [[3.2, 8, 14.5], [0, 3.4, 0]],
    front: [[2.5, 4.2, 13], [0, 2.4, 0]],
    margin: [[2.5, 2.6, 10], [0, 1.6, 0]],
    show: [[6, 8, 22], [0, 5.2, 0]],
  });
  L.onReset(() => {
    [cavity, filling, crack, pfm, zir, scanBeam, ...dust].forEach(o => o.visible = false);
    cavity.scale.set(1.1, .3, .9); filling.scale.set(1, .2, .85);
    pfm.position.set(CX, .7, 0); pfm.rotation.set(0, 0, 0); collar.visible = true; collar.scale.set(1, .88, 1);
    zir.position.set(CX, .7, 0); zir.rotation.set(0, 0, 0); zirMat.emissiveIntensity = 0;
    L.centerTooth.children[0].scale.set(1, 1, 1); L.centerTooth.children[0].position.y = 0;
    marginRing.material.opacity = 0;
  });
}

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, centerTooth: tooth, looseCrown: temp, upper, food, inflam, inflamF, warn, halo, brush } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  // ---- persistent state (what has been built so far)
  const fillT = mk(0, 'fill', .55), crackT = mk(1, 'crack', .75), pfmT = mk(2, 'so', .1);
  const darkT = mk(3, 'dark', .5), zirT = mk(4, 'so', .2), trimT = mk(5, 'so', .45), scanT = mk(5, 'scan', .75);
  const tempT = mk(6, 'temp', .3), realT = mk(6, 'real', .7);
  const trimmed = eout(seg(t, trimT + .1, trimT + 1.0));
  const crown = tooth.children[0];
  crown.scale.set(lerp(1, .74, trimmed), lerp(1, .8, trimmed), lerp(1, .74, trimmed)); crown.position.y = lerp(0, -.15, trimmed);
  if (t < trimT + .6 && (t < pfmT + .7 || t > zirT + .3)) {
    if (t < fillT + .25) { cavity.visible = true; { const k = eout(seg(t, bs(0) + .2, bs(0) + .7)); cavity.scale.set(1.1 * k, .3, .9 * k); } }
    if (t > fillT) { filling.visible = true; const k = back(seg(t, fillT, fillT + .45)); filling.scale.set(k * 1.12, .26, .92 * k); }
    if (t > crackT) { crack.visible = true; crack.scale.set(1, clamp(seg(t, crackT, crackT + .35)), 1); crack.position.y = (1 - clamp(seg(t, crackT, crackT + .35))) * 3.5; }
  }
  const seatedZir = () => { zir.visible = true; zir.position.set(CX, .7, 0); };
  const seatPfm = () => { pfm.visible = true; pfm.position.set(CX, .7, 0); };

  if (t < be(0)) {                                   // hook: a big cavity -> just fill it?
    const a = bs(0), d = B[0].dur; upper.position.y = 40;
    if (t > fillT) sparkleAt(CX, 3.9, .5, seg(t, fillT + .3, fillT + 1), 2.2);
    setCam('wide', 'top', ease(seg(t, a + .3, a + d * .8)));
    chip('hole', 'ฟันผุเป็นหลุมใหญ่', 'red', 190, t, a + .5, fillT - .05, -2);
    chip('fill', 'อุดเต็มหลุม ✓', 'green', 190, t, fillT + .2, be(0) - .1);
  } else if (t < be(1)) {                            // bite hard -> crack
    const a = bs(1);
    const hit = mk(1, 'chew', .45) + .45;
    const down = ein(seg(t, a + .2, hit)), up = eout(seg(t, hit + .2, hit + .9));
    upper.position.y = lerp(11, 3.4, down) + (t > hit ? lerp(0, 7.6, up) : 0);
    food.visible = t < hit + .05; food.position.set(CX, Math.min(5.8, upper.position.y - .55), .3); food.scale.set(1.25, .8 * clamp((upper.position.y - .55 - 3.6) / 2.2, .3, 1), 1);
    flash = t > hit ? .3 * Math.exp(-(t - hit) * 12) : 0;
    warn.material.opacity = t > crackT ? .85 * (.5 + .5 * Math.sin((t - crackT) * 14)) : 0; warn.position.set(CX, 2.6, 1.8); warn.scale.setScalar(1.05);
    blur = whip(1);
    setCam('bite', 'front', ease(seg(t, hit + .2, hit + 1.2)), t > hit && t < hit + .5 ? .4 * (1 - seg(t, hit, hit + .5)) : 0, t);
    chip('thin', 'เนื้อฟันรอบๆ บางมาก', 'dark', 190, t, a + .4, crackT - .05);
    chip('crk', '⚠ ฟันร้าว!', 'red', 190, t, crackT, be(1) - .1, -3);
  } else if (t < be(2)) {                            // crown = a helmet for the tooth
    const a = bs(2), d = B[2].dur;
    pfm.visible = true; collar.visible = false; const k = seg(t, pfmT, pfmT + .7);
    pfm.position.set(CX, lerp(11, .7, ein(k)), 0); pfm.rotation.y = (1 - k) * 4;
    if (k >= 1) { sparkleAt(CX, 3.2, 0, seg(t, pfmT + .7, pfmT + 1.4), 3.4); flash = .3 * Math.exp(-(t - pfmT - .7) * 10); }
    blur = whip(2);
    setCam('front', 'crown', ease(seg(t, a, a + d * .8)), k >= 1 && t < pfmT + 1 ? .12 : 0, t);
    chip('helm', '🪖 หมวกกันน็อกของฟัน', 'dark', 190, t, pfmT + .5, be(2) - .1);
    chip('term', 'ครอบฟัน (Crown)', 'yel', 330, t, mk(2, 'term', .78), be(2) - .1);
  } else if (t < be(3)) {                            // metal inside -> grey line at the gum
    const a = bs(3), d = B[3].dur; seatPfm();
    const r = eout(seg(t, mk(3, 'recede', .4), darkT + .3));
    collar.position.y = .56; collar.scale.set(lerp(.9, 1, r), .88, 1); collar.visible = r > .02;
    if (t > darkT) { halo.material.opacity = .25 + .15 * Math.sin((t - darkT) * 10); halo.position.set(CX, 1.3, 2); halo.scale.set(5, 5, 1); }
    setCam('crown', 'margin', ease(seg(t, a, a + d * .7)));
    chip('metal', 'ข้างในเป็นโลหะ', 'dark', 190, t, a + .3, darkT - .05);
    chip('grey', 'ขอบเทาดำตรงเหงือก', 'red', 330, t, darkT, be(3) - .1, 2);
    if (t < mk(3, 'recede', .4)) collar.visible = false;
  } else if (t < be(4)) {                            // zirconia: no metal, tooth-coloured
    const a = bs(4), d = B[4].dur;
    if (t < zirT + .5) { seatPfm(); const k = seg(t, zirT - .1, zirT + .5); pfm.position.set(CX + lerp(0, 12, ein(k)), .7 + 6 * Math.sin(k * Math.PI), 0); pfm.rotation.set(k * 5, 0, -k * 6); }
    if (t > zirT) { zir.visible = true; const k = seg(t, zirT, zirT + .8); zir.position.set(CX, lerp(12, 5.6, eout(k)) + .2 * Math.sin(t * 2.5), 0); zir.rotation.y = t * 1.3;
      zirMat.emissiveIntensity = .12 + .06 * Math.sin(t * 4); halo.material.opacity = .45 * eout(k); halo.position.set(CX, 6.6, -1.2); halo.scale.set(10, 10, 1);
      sparkleAt(CX, 6.6, 0, (seg(t, zirT + .5, be(4)) * 2) % 1, 3.8); }
    blur = whip(4);
    setCam('margin', 'show', ease(seg(t, a, a + d * .6)));
    chip('zr', 'เซอร์โคเนีย (Zirconia)', 'yel', 190, t, zirT + .3, be(4) - .1);
    chip('nm', '✕ ไม่มีโลหะ', 'green', 330, t, mk(4, 'nometal', .55), be(4) - .1);
    chip('col', 'สีใกล้เคียงฟันจริง', 'dark', 460, t, mk(4, 'nometal', .55) + .9, be(4) - .1);
  } else if (t < be(5)) {                            // trim the tooth a little, then scan it
    const a = bs(5), d = B[5].dur; upper.position.y = 40;
    if (t > trimT && t < trimT + 1.3) dust.forEach(m => { const tt = t - trimT - m.userData.d * .4; m.visible = tt > 0 && tt < .9;
      m.position.set(CX + Math.cos(m.userData.a) * (1.4 + tt * m.userData.v), 3.3 + tt * m.userData.up - 5 * tt * tt, .6 + Math.sin(m.userData.a) * tt * 1.5); });
    if (t > scanT) { const k = seg(t, scanT, scanT + 1.3); scanBeam.visible = k < 1; scanBeam.position.set(CX - 3 + 6 * ease(k), 3.0, .4); }
    blur = whip(5);
    setCam('top', 'front', ease(seg(t, a, a + d * .5)));
    chip('room', 'ต้องมีที่ให้ครอบ', 'dark', 190, t, a + .3, trimT - .05);
    chip('trim', 'กรอแต่งฟันนิดหน่อย', 'yel', 190, t, trimT + .2, scanT - .05);
    chip('scan', '📡 สแกนฟัน 3 มิติ', 'green', 190, t, scanT + .1, be(5) - .1);
  } else if (t < be(6)) {                            // temporary crown -> next visit, the real one
    const a = bs(6), d = B[6].dur;
    if (t > tempT && t < realT + .6) { temp.visible = true; const kin = seg(t, tempT, tempT + .5), kout = seg(t, realT, realT + .6);
      temp.position.set(CX + lerp(0, -12, ein(kout)), lerp(10, .7, eout(kin)) + 6 * Math.sin(kout * Math.PI), 0); temp.rotation.z = kout * 6; }
    if (t > realT + .3) { zir.visible = true; const k = seg(t, realT + .3, realT + .9); zir.position.set(CX, lerp(10, .7, ein(k)), 0);
      if (k >= 1) { sparkleAt(CX, 3.2, 0, seg(t, realT + .9, realT + 1.6), 3.4); flash = .35 * Math.exp(-(t - realT - .9) * 10); } }
    const cn = t < realT ? 1 : 2;
    L.calendar('นัดครั้งที่', cn, t > be(6) - .3 ? 1 - seg(t, be(6) - .3, be(6)) : (t < realT ? back(seg(t, a + .2, a + .55)) : 1 + .25 * Math.sin(seg(t, realT, realT + .4) * Math.PI)));
    setCam('front', 'crown', ease(seg(t, realT, realT + 1.2)), t > realT + .9 && t < realT + 1.2 ? .12 : 0, t);
    chip('tmp', 'ครอบชั่วคราว', 'dark', 500, t, tempT + .3, realT - .05);
    chip('real', 'ครอบเซอร์โคเนีย ✓', 'green', 500, t, realT + .9, be(6) - .1);
  } else if (t < be(7)) {                            // who should get a crown?
    const a = bs(7), d = B[7].dur; seatedZir();
    const c1 = mk(7, 'c1', .3), c2 = mk(7, 'c2', .55), c3 = mk(7, 'c3', .75);
    const pulse = (x, t0, t1) => { if (t > t0 && t < t1) { halo.material.opacity = .55 * Math.sin(seg(t, t0, t1) * Math.PI); halo.position.set(x, 3, 1); halo.scale.set(7, 7, 1); } };
    pulse(-L.SP, c1, c2); pulse(CX, c2, c3); pulse(L.SP, c3, be(7));
    blur = whip(7);
    setCam('ortho', 'gap', ease(seg(t, a, a + d * .9)));
    chip('q', 'ใครควรครอบ?', 'dark', 170, t, a + .2, be(7) - .1);
    chip('w1', '✓ ฟันที่รักษารากแล้ว', 'green', 300, t, c1, be(7) - .1);
    chip('w2', '✓ ฟันอุดใหญ่', 'green', 420, t, c2, be(7) - .1);
    chip('w3', '✓ ฟันร้าว / สึกมาก', 'green', 540, t, c3, be(7) - .1);
  } else if (t < be(8)) {                            // myth: a crowned tooth can't decay? -> the margin still can
    const a = bs(8), d = B[8].dur; seatedZir();
    const no = mk(8, 'no', .5), edge = mk(8, 'edge', .75);
    L.germsArrive(t, a + .3);
    if (t > edge) { marginRing.material.opacity = .85 * (.5 + .5 * Math.sin((t - edge) * 12)); const inf = seg(t, edge, edge + .6); inflam.material.opacity = .4 * inf; inflamF.material.opacity = .3 * inf; }
    blur = whip(8);
    setCam('crown', 'neck', ease(seg(t, a, edge)));
    chip('m1', 'ครอบแล้ว ไม่ผุอีก?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่จริง!', 'red', 330, t, no, be(8) - .1, -4);
    chip('m3', 'ขอบครอบยังผุได้', 'red', 190, t, edge, be(8) - .1, 2);
  } else if (t < be(9)) {                            // brush, floss, check-ups
    const a = bs(9), d = B[9].dur; seatedZir();
    const bk = seg(t, a + .1, a + d * .45);
    brush.visible = bk > 0 && bk < 1; brush.position.set(CX + Math.sin(bk * Math.PI * 4) * 3.2, L.GUM_TOP + 1.4, 2.0); brush.rotation.set(0, 0, Math.sin(t * 30) * .04);
    L.germsClear(t, a + .25, a + .25 + d * .4);
    const inf = 1 - seg(t, a + .2, a + d * .45); inflam.material.opacity = .4 * inf; inflamF.material.opacity = .3 * inf;
    if (bk >= 1) sparkleAt(CX, 3, 0, seg(t, a + d * .45, a + d * .45 + .7), 3.6);
    setCam('gumline', 'crown', ease(seg(t, a + d * .4, a + d)));
    chip('b1', '🪥 แปรงวันละ 2 ครั้ง', 'green', 170, t, mk(9, 'c1', 0), be(9) - .1);
    chip('b2', '🧵 ใช้ไหมขัดฟัน', 'dark', 300, t, mk(9, 'c2', .4), be(9) - .1);
    chip('b3', '🦷 ตรวจทุก 6 เดือน', 'yel', 430, t, mk(9, 'c3', .62), be(9) - .1);
  } else if (t < be(10)) {                           // payoff: chew comfortably, confetti
    const a = bs(10), d = B[10].dur; seatedZir();
    const ch = mk(10, 'chew', .35);
    const bump = seg(t, ch, ch + 1.2);
    upper.position.y = lerp(11, 3.4, Math.sin(bump * Math.PI));
    food.visible = bump > 0 && bump < .55; food.position.set(CX, Math.min(5.8, upper.position.y - .55), .3); food.scale.set(1.25, .8 * clamp((upper.position.y - .55 - 3.6) / 2.2, .3, 1), 1);
    L.confetti(t, a);
    zirMat.emissiveIntensity = .08;
    sparkleAt(CX, 3, 0, seg(t, a, a + .9), 3.8);
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
    chip('yay', '😁 เคี้ยวได้สบาย', 'green', 190, t, ch, be(10) - .1);
  } else {                                           // under the end card
    seatedZir(); setCam('wide', 'wide', 0);
  }
  return { blur, flash };
}

// cover: a gleaming zirconia crown floating above the trimmed tooth
export function cover(t, L) {
  const { lerp, clamp, centerTooth, halo, upper, cam, sparkleAt } = L;
  upper.position.y = 40;
  const c = centerTooth.children[0]; c.scale.set(.74, .8, .74); c.position.y = -.15;
  const f = Math.sin(t * 2.2);
  zir.visible = true; zir.position.set(CX, 5.4 + .25 * f, 0); zir.rotation.set(0, t * .8 - .3, 0); zirMat.emissiveIntensity = .12;
  halo.material.opacity = .4; halo.position.set(CX, 6.2, -1.5); halo.scale.set(12, 12, 1);
  sparkleAt(CX, 6.4, 0, (t * .7) % 1, 4.0);
  const k = clamp(t / 2);
  cam.position.set(lerp(6, 5.4, k), lerp(7.4, 7, k), lerp(25, 23, k)); cam.lookAt(0, 7.7, 0);
  return [
    { text: 'ครอบเซอร์โคเนีย', at: [0.2, zir.position.y + .6, 0], dx: 40 },
    { text: 'ฟันที่กรอแต่ง', at: [1.3, 2.4, 0] },
  ];
}

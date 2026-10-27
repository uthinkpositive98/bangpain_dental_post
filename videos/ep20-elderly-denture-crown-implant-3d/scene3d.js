// ep20 ผู้สูงอายุ เลือกฟันปลอม ครอบฟัน หรือรากฟันเทียม? — cut3d episode (L = tools/cut3d/lib.js)
// Story on one jaw: a decayed tooth gets a crown -> the three middle teeth are lost -> a removable partial denture
// (pink base + 3 teeth + metal clasps) -> it rocks while chewing, the ridge shrinks over the years -> three implants
// with crowns -> what implants need (bone, controlled health, months) -> whole arch lost: a full denture snapped onto
// two implants (overdenture) -> myth: "too old for implants" -> cleaning + check-ups -> payoff.
let cav, den, fullDen, imps = [], abuts = [], crowns = [], odImps = [], balls = [];
const MID = [];                       // the 3 middle teeth: neighbors[2] (x=-SP), centerTooth (x=0), neighbors[3] (x=+SP)

function denture(L, xs, halfW) {
  const { THREE, CROWN, RoundedBoxGeometry, SP } = L;
  const g = new THREE.Group(); L.scene.add(g);
  const pink = new THREE.MeshPhysicalMaterial({ color: '#f07f98', roughness: .35, clearcoat: .8, clearcoatRoughness: .2 });
  const base = new THREE.Mesh(new RoundedBoxGeometry(halfW * 2, .95, 3.5, 5, .4), pink); base.position.set(0, 1.62, 0); base.castShadow = true; g.add(base);
  const dt = new THREE.MeshPhysicalMaterial({ color: '#fbf6ea', roughness: .25, clearcoat: .8 });
  xs.forEach(x => { const c = new THREE.Mesh(CROWN, dt); c.position.set(x, .78, 0); c.scale.set(.97, .98, .97); c.castShadow = true; g.add(c); });
  g.userData.base = base; return g;
}

export function setup(L) {
  const { THREE, scene, SP, GUM_TOP, tooth, titanium, implant, abut } = L;
  MID.push(L.neighbors[2], L.centerTooth, L.neighbors[3]);
  // cavity on top of the natural x=0 tooth (child, so it moves with the tooth)
  cav = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 14), new THREE.MeshStandardMaterial({ color: '#3b2414', roughness: .85 }));
  cav.position.set(-.2, 2.96, .2); cav.scale.set(.95, .3, .8); L.centerTooth.add(cav);
  // partial denture over the 3-tooth gap, with metal clasps hugging the teeth at x = ±2SP
  den = denture(L, [-SP, 0, SP], 5.55);
  const clMat = new THREE.MeshStandardMaterial({ color: '#cfd5dc', metalness: 1, roughness: .25 });
  [-1, 1].forEach(s => { const arc = new THREE.Mesh(new THREE.TorusGeometry(1.72, .08, 8, 40, Math.PI), clMat); arc.rotation.x = Math.PI / 2; arc.rotation.z = s > 0 ? 0 : 0;
    arc.position.set(s * 2 * SP, 2.35, 0); den.add(arc);
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 1.0, 8), clMat); arm.rotation.z = Math.PI / 2; arm.position.set(s * (2 * SP - 1.95), 2.1, 1.0); den.add(arm); });
  // full denture for the whole lower arch (7 teeth)
  fullDen = denture(L, [-3, -2, -1, 0, 1, 2, 3].map(i => i * SP), 13.3);
  // three implants + abutments + crowns in the gap (index 1 reuses the engine's own implant/abutment)
  [-SP, 0, SP].forEach((x, i) => {
    const m = i === 1 ? implant : new THREE.Mesh(implant.geometry, titanium); if (i !== 1) { m.castShadow = true; scene.add(m); } imps.push(m);
    const a = i === 1 ? abut : abut.clone(true); if (i !== 1) scene.add(a); abuts.push(a);
    crowns.push(tooth(x, false)); });
  // two implants with ball attachments for the overdenture (x = ±2SP)
  [-2 * SP, 2 * SP].forEach(x => { const m = new THREE.Mesh(implant.geometry, titanium); m.castShadow = true; scene.add(m); odImps.push(m);
    const b = new THREE.Group(); const neck = new THREE.Mesh(new THREE.CylinderGeometry(.42, .55, .9, 24), titanium); neck.position.y = .45; b.add(neck);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(.5, 24, 16), titanium); ball.position.y = 1.15; b.add(ball); b.position.x = x; scene.add(b); balls.push(b); });
  Object.assign(L.SHOTS, {
    gap3: [[6, 6.2, 40], [0, 2.2, 0]],
    arch: [[0, 7, 44], [0, 0.6, 0]],
    opts: [[0, 6, 28], [0, 4.6, 0]],
    den: [[5, 7, 22], [0, 2.2, 0]],
    boneW: [[6, 1.5, 32], [0, -2.4, 0]],
  });
  L.onReset(() => {
    L.neighbors.forEach(n => { n.visible = true; n.position.y = .7; n.position.z = 0; n.rotation.set(0, 0, 0); });
    L.neighbors.forEach((n, i) => n.position.x = [-3, -2, -1, 1, 2, 3][i] * SP);
    L.centerTooth.children[0].scale.set(1, 1, 1); cav.visible = false;
    [den, fullDen, ...balls, ...odImps, ...crowns].forEach(o => o.visible = false);
    [1, 0, 2].forEach(i => { imps[i].visible = false; imps[i].position.set([-SP, 0, SP][i], 0, 0); imps[i].rotation.set(0, 0, 0);
      abuts[i].visible = false; abuts[i].position.set([-SP, 0, SP][i], .05, 0); abuts[i].rotation.set(0, 0, 0);
      crowns[i].position.set([-SP, 0, SP][i], .9, 0); crowns[i].rotation.set(0, 0, 0); });
    den.position.set(0, 0, 0); den.rotation.set(0, 0, 0); den.scale.setScalar(1);
    fullDen.position.set(0, 0, 0); fullDen.rotation.set(0, 0, 0);
    odImps.forEach((m, i) => { m.position.set((i ? 2 : -2) * SP, 0, 0); m.rotation.set(0, 0, 0); }); balls.forEach(b => b.position.y = 0);
    [...imps, ...abuts, ...crowns, L.newCrown].forEach(o => o.scale.setScalar(1));
  });
}

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, SP, GUM_TOP, setCam, chip, sparkleAt, centerTooth: ct, newCrown, upper, food, glow, warn, halo, brush, neighbors } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const lostT = mk(2, 'lost', .2), crT = mk(1, 'so', .55);
  const gapOn = () => { MID.forEach(m => m.visible = false); };
  const implSet = () => { gapOn(); [0, 1, 2].forEach(i => { imps[i].visible = true; abuts[i].visible = true; crowns[i].visible = true; }); };
  const chewDown = (t0, dur = 1.1) => { const b = seg(t, t0, t0 + dur); upper.position.y = lerp(11, 3.5, Math.sin(b * Math.PI));
    food.visible = b > 0 && b < .5; food.position.set(0, Math.min(5.8, upper.position.y - .55), .3); food.scale.set(1.25, .8 * clamp((upper.position.y - .55 - 3.6) / 2.2, .3, 1), 1); return b; };

  if (t < be(0)) {                                   // hook: the three options float over the jaw
    const a = bs(0), d = B[0].dur;
    const pop = (o, t0, x, y) => { const k = back(seg(t, t0, t0 + .45)); o.visible = k > 0; o.position.set(x, y + .2 * Math.sin(t * 2.4 + x), 2); o.scale.setScalar(Math.max(.001, k) * (o === den ? .5 : 1)); };
    upper.position.y = 40;
    pop(den, mk(0, 'den', .35), -3.7, 4.2); den.scale.multiplyScalar(.6); den.rotation.set(.45, .5 + t * .3, 0);
    if (t > mk(0, 'cr', .55)) { newCrown.visible = true; const k = back(seg(t, mk(0, 'cr', .55), mk(0, 'cr', .55) + .45)); newCrown.position.set(0, 4.3 + .2 * Math.sin(t * 2.4), 2.5); newCrown.scale.setScalar(Math.max(.001, k)); newCrown.rotation.y = t * .8; }
    const ik = seg(t, mk(0, 'imp', .8), mk(0, 'imp', .8) + .45);
    if (ik > 0) { imps[2].visible = abuts[2].visible = crowns[2].visible = true; const s = Math.max(.001, back(ik)), y = 6.0 + .2 * Math.sin(t * 2.4 + 3);
      imps[2].position.set(3.7, y, 2.5); imps[2].scale.setScalar(s * .55); abuts[2].position.set(3.7, y + .03, 2.5); abuts[2].scale.setScalar(s * .55); crowns[2].position.set(3.7, y + .2, 2.5); crowns[2].scale.setScalar(s * .55);
      [imps[2], abuts[2], crowns[2]].forEach(o => o.rotation.y = t * .8); }
    setCam('opts', 'opts', 0); if (t > be(0) - .5) { setCam('opts', 'gap3', ease(seg(t, be(0) - .5, be(0)))); }
    chip('o1', '🦷 ฟันปลอม', 'dark', 190, t, mk(0, 'den', .35) + .1, be(0) - .1);
    chip('o2', '👑 ครอบฟัน', 'yel', 320, t, mk(0, 'cr', .55) + .1, be(0) - .1);
    chip('o3', '🔩 รากฟันเทียม', 'green', 450, t, mk(0, 'imp', .8) + .1, be(0) - .1);
  } else if (t < be(1)) {                            // tooth still there, big decay, root OK -> crown
    const a = bs(1), d = B[1].dur, dk = mk(1, 'decay', .15);
    [imps[2], abuts[2], crowns[2]].forEach(o => o.scale.setScalar(1));
    cav.visible = t < crT + .55; const ck = eout(seg(t, dk, dk + .6)); cav.scale.set(.95 * ck + .01, .3, .8 * ck + .01);
    const trim = eout(seg(t, crT - .2, crT + .3)); ct.children[0].scale.set(lerp(1, .8, trim), lerp(1, .84, trim), lerp(1, .8, trim));
    if (t > crT) { newCrown.visible = true; newCrown.scale.setScalar(1); const k = seg(t, crT, crT + .55); newCrown.position.set(0, lerp(10, .7, ein(k)), 0);
      if (k >= 1) { sparkleAt(0, 3.2, 0, seg(t, crT + .55, crT + 1.2), 3.2); flash = .3 * Math.exp(-(t - crT - .55) * 10); } }
    glow.material.opacity = t > dk + .6 && t < crT ? .25 : 0;
    blur = whip(1);
    setCam('neck', 'crown', ease(seg(t, crT - .3, crT + 1)));
    chip('c1', 'ผุใหญ่ / แตก', 'red', 190, t, dk + .1, be(1) - .1, -2);
    chip('c2', '✓ รากยังดี', 'green', 320, t, dk + .9, be(1) - .1);
    chip('c3', '👑 ครอบฟัน ห่อซี่เดิม', 'yel', 450, t, crT + .4, be(1) - .1);
  } else if (t < be(2)) {                            // teeth already lost -> nothing to crown
    const a = bs(2), d = B[2].dur;
    newCrown.visible = true; newCrown.position.set(0, .7, 0);
    MID.forEach((m, j) => { const t0 = lostT + j * .18, k = seg(t, t0, t0 + .9); const dir = [-1, 0, 1][j];
      m.position.set(m.position.x + dir * 3 * k, .7 + 13 * eout(k) - 5 * k * k, 2.5 * k); m.rotation.set(k * 5, 0, dir * k * 4 + k);
      if (j === 1) { newCrown.position.copy(m.position); newCrown.rotation.copy(m.rotation); newCrown.visible = k < 1; }
      if (k >= 1) m.visible = false; });
    if (t > lostT) ct.children[0].scale.set(.8, .84, .8);
    if (t > lostT + .6) { halo.material.opacity = .25 * seg(t, lostT + .6, lostT + 1.2); halo.position.set(0, 2, 1); halo.scale.set(9, 6, 1); }
    blur = whip(2);
    setCam('gap', 'gap3', ease(seg(t, a, a + d * .8)));
    chip('l1', 'ฟันหลุดไปแล้ว', 'red', 190, t, lostT + .3, be(2) - .1, -2);
    chip('l2', 'ไม่มีซี่ให้ครอบ ✕', 'dark', 320, t, lostT + 1.0, be(2) - .1);
    chip('l3', 'ต้องหาฟันมาแทน', 'yel', 450, t, mk(2, 'so', .7) + .1, be(2) - .1);
  } else if (t < be(3)) {                            // option 1: removable denture
    const a = bs(3), d = B[3].dur, dt = mk(3, 'den', .1);
    gapOn();
    if (t > dt) { den.visible = true; const k = seg(t, dt, dt + .7); den.position.set(0, lerp(9, 0, ein(k)), 0); den.rotation.y = (1 - k) * 1.5;
      if (k >= 1) { sparkleAt(0, 3.2, 0, seg(t, dt + .7, dt + 1.4), 4.5); if (t < dt + 1) flash = .25 * Math.exp(-(t - dt - .7) * 10); } }
    blur = whip(3);
    setCam('gap3', 'den', ease(seg(t, dt, dt + 1.4)));
    chip('d1', 'ฟันปลอมถอดได้', 'dark', 190, t, dt + .4, be(3) - .1);
    chip('d2', '✓ ไม่ต้องผ่าตัด', 'green', 320, t, mk(3, 'nosurg', .45), be(3) - .1);
    chip('d3', '✓ แทนได้หลายซี่ / ทั้งปาก', 'green', 450, t, mk(3, 'many', .7), be(3) - .1);
  } else if (t < be(4)) {                            // but: it can rock while chewing; the ridge shrinks over the years
    const a = bs(4), d = B[4].dur, lo = mk(4, 'loose', .25), bn = mk(4, 'bone', .55), ad = mk(4, 'adj', .8);
    gapOn(); den.visible = true;
    const b = chewDown(lo - .5, 1.2);
    const rock = t > lo - .1 && t < lo + 1.6 ? Math.sin((t - lo) * 20) * .07 * (1 - seg(t, lo, lo + 1.6)) : 0;
    den.rotation.z = rock; den.position.x = rock * 3;
    if (t > lo && t < lo + 1.4) { warn.material.opacity = .8 * (.5 + .5 * Math.sin((t - lo) * 14)); warn.position.set(0, 2.4, 2.2); warn.scale.set(2.4, 1.4, 1); }
    const sink = eout(seg(t, bn, bn + 1.6));
    if (t > bn) { halo.material.opacity = .3 * sink; halo.position.set(0, 1.3, 1.5); halo.scale.set(10, 3, 1); }
    den.position.y = -.42 * sink + (t > ad ? .42 * eout(seg(t, ad + .2, ad + .9)) * 0 : 0);
    if (t > ad) { den.position.y = lerp(-.42, -.1, eout(seg(t, ad + .2, ad + .9))); }
    if (t > bn && t < ad + .4) L.calendar('ปีที่', Math.max(1, Math.min(5, 1 + Math.floor(seg(t, bn, bn + 1.6) * 4.99))), back(seg(t, bn, bn + .35)));
    blur = whip(4);
    setCam('bite', 'den', ease(seg(t, lo + .6, bn + .4)), rock ? .06 : 0, t);
    chip('w1', '⚠ หลวม ขยับเวลาเคี้ยว', 'red', 500, t, lo + .1, be(4) - .1, -2);
    chip('w2', '⬇ กระดูกค่อยๆ ยุบ', 'dark', 630, t, bn + .2, be(4) - .1);
    chip('w3', '🔧 ต้องปรับเป็นระยะ', 'yel', 760, t, ad, be(4) - .1);
    if (t > ad + .4) L.calendar('ปีที่', 5, 1 - seg(t, ad + .4, ad + .7));
  } else if (t < be(5)) {                            // option 2: implants in the bone, firm, no removing
    const a = bs(5), d = B[5].dur, so = mk(5, 'so', .1), ch = mk(5, 'chew', .75);
    gapOn();
    if (t < so + .6) { den.visible = true; const k = seg(t, so - .1, so + .6); den.position.set(lerp(0, 14, ein(k)), lerp(0, 7, eout(k)), 0); den.rotation.z = -k * 1.2; }
    [0, 1, 2].forEach(i => { const t0 = so + .3 + i * .25, k = seg(t, t0, t0 + 1.1); imps[i].visible = k > 0; imps[i].position.y = lerp(13, 0, eout(k)); imps[i].rotation.y = -k * 24;
      const ta = t0 + 1.2, ka = seg(t, ta, ta + .4); abuts[i].visible = ka > 0; abuts[i].position.y = lerp(8, .05, eout(ka));
      const tc = t0 + 1.5, kc = seg(t, tc, tc + .45); crowns[i].visible = kc > 0; crowns[i].position.y = lerp(9, .9, ein(kc)); if (kc >= 1 && i === 1) sparkleAt(0, 3, 0, seg(t, tc + .45, tc + 1.1), 4.4); });
    const b = chewDown(ch, 1.1); if (b > .45 && b < .55) flash = .15;
    blur = whip(5);
    setCam('gap3', 'den', ease(seg(t, a + d * .4, a + d)));
    chip('i1', '🔩 รากฟันเทียม ฝังในกระดูก', 'dark', 190, t, so + .5, be(5) - .1);
    chip('i2', '✓ แน่น ไม่ต้องถอด', 'green', 320, t, mk(5, 'firm', .5), be(5) - .1);
    chip('i3', '✓ เคี้ยวได้มั่นคง', 'green', 450, t, ch, be(5) - .1);
  } else if (t < be(6)) {                            // what implants need: enough bone, controlled health, months
    const a = bs(6), d = B[6].dur, bo = mk(6, 'bone', .1), he = mk(6, 'health', .45), tm = mk(6, 'time', .75);
    implSet();
    glow.material.opacity = .14 * Math.sin(seg(t, bo, bo + 1.4) * Math.PI);
    if (t > tm) L.calendar('เดือนที่', Math.max(1, Math.min(6, 1 + Math.floor(seg(t, tm, be(6) - .4) * 5.99))), t > be(6) - .3 ? 1 - seg(t, be(6) - .3, be(6)) : back(seg(t, tm, tm + .35)));
    blur = whip(6);
    setCam('gap3', 'boneW', ease(seg(t, a, bo + .8)));
    chip('r1', '✓ กระดูกพอ', 'green', 500, t, bo + .2, be(6) - .1);
    chip('r2', '✓ โรคประจำตัวควบคุมได้', 'green', 630, t, he, be(6) - .1);
    chip('r3', '⏳ ใช้เวลาหลายเดือน', 'dark', 760, t, tm + .2, be(6) - .1);
  } else if (t < be(7)) {                            // whole arch lost + loose full denture -> two implants hold it (overdenture)
    const a = bs(7), d = B[7].dur, so = mk(7, 'so', .4), lk = mk(7, 'lock', .7);
    MID.forEach(m => m.visible = false); neighbors.forEach(n => n.visible = false);
    fullDen.visible = true;
    if (t < so) { const r = Math.sin((t - a) * 16) * .035 * seg(t, a + .3, a + .6); fullDen.rotation.z = r; fullDen.position.set(r * 4, Math.abs(r) * 4, 0); }
    else { const up = eout(seg(t, so, so + .5)), dn = seg(t, lk, lk + .55); fullDen.position.set(0, lerp(0, 2.6, up) - lerp(0, 2.6, ein(dn)), lerp(0, 3, up) - lerp(0, 3, ein(dn))); fullDen.rotation.x = .35 * (up - dn); }
    odImps.forEach((m, i) => { const t0 = so + .3 + i * .3, k = seg(t, t0, t0 + 1.0); m.visible = k > 0; m.position.y = lerp(13, 0, eout(k)); m.rotation.y = -k * 22;
      const kb = seg(t, t0 + 1.05, t0 + 1.4); balls[i].visible = kb > 0; balls[i].position.y = lerp(6, 0, eout(kb)); });
    if (t > lk + .55) { sparkleAt(-2 * SP, 2.4, 0, seg(t, lk + .55, lk + 1.2), 2.6); flash = .3 * Math.exp(-(t - lk - .55) * 10); }
    if (t < so && t > a + .4) { warn.material.opacity = .7 * (.5 + .5 * Math.sin(t * 14)); warn.position.set(0, 2.4, 2.4); warn.scale.set(5.5, 1.6, 1); }
    blur = whip(7);
    setCam('arch', 'arch', 0, t < so ? .05 : 0, t);
    chip('f1', 'ฟันหายทั้งปาก + ฟันปลอมหลวม', 'red', 190, t, a + .3, be(7) - .1, -2);
    chip('f2', '🔩 รากเทียม 2 ตัว', 'dark', 320, t, so + .5, be(7) - .1);
    chip('f3', '✓ ฟันปลอมยึดรากเทียม แน่นขึ้น', 'green', 450, t, lk + .5, be(7) - .1);
  } else if (t < be(8)) {                            // myth: too old for implants? no — health + bone, not the number
    const a = bs(8), d = B[8].dur, no = mk(8, 'no', .45), hl = mk(8, 'health', .7);
    implSet();
    blur = whip(8);
    setCam('ortho', 'gap3', ease(seg(t, a, a + d)));
    chip('m1', 'อายุมาก ทำรากเทียมไม่ได้?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่จริง!', 'red', 330, t, no, be(8) - .1, -4);
    chip('m3', '✓ ดูที่สุขภาพ + กระดูก', 'green', 190, t, hl, be(8) - .1);
    chip('m4', 'ไม่ใช่ตัวเลขอายุ', 'yel', 460, t, hl + .7, be(8) - .1);
  } else if (t < be(9)) {                            // whatever you choose: clean daily + check every 6 months
    const a = bs(9), d = B[9].dur; implSet();
    const bk = seg(t, a + .1, a + d * .5);
    brush.visible = bk > 0 && bk < 1; brush.position.set(Math.sin(bk * Math.PI * 4) * 5, GUM_TOP + 1.4, 2.0); brush.rotation.set(0, 0, Math.sin(t * 30) * .04);
    if (bk >= 1) sparkleAt(0, 3, 0, seg(t, a + d * .5, a + d * .5 + .7), 4.4);
    setCam('gumline', 'gap3', ease(seg(t, a + d * .3, a + d)));
    chip('k1', '🪥 ทำความสะอาดทุกวัน', 'green', 190, t, mk(9, 'c1', .2), be(9) - .1);
    chip('k2', '🦷 ตรวจทุก 6 เดือน', 'yel', 320, t, mk(9, 'c2', .6), be(9) - .1);
  } else if (t < be(10)) {                           // payoff: chewing happily
    const a = bs(10), d = B[10].dur; implSet();
    chewDown(mk(10, 'chew', .3), 1.2);
    L.confetti(t, a); sparkleAt(0, 3, 0, seg(t, a, a + .9), 4.2);
    setCam('gap3', 'wide', ease(seg(t, a, a + d * .8)));
    chip('y', '😁 เคี้ยวอร่อย ยิ้มได้เต็มที่', 'green', 190, t, a + .3, be(10) - .1);
  } else {                                           // under the end card
    implSet(); setCam('wide', 'wide', 0);
  }
  return { blur, flash };
}

// cover: denture, crown and implant floating side by side over the jaw
export function cover(t, L) {
  const { lerp, clamp, upper, cam, newCrown, halo, sparkleAt } = L;
  upper.position.y = 40;
  const f = k => .25 * Math.sin(t * 2.2 + k);
  den.visible = true; den.scale.setScalar(.3); den.position.set(-3.7, 4.2 + f(0), 2.5); den.rotation.set(.45, .5 + t * .3, 0);
  newCrown.visible = true; newCrown.position.set(0, 4.3 + f(1), 2.5); newCrown.rotation.set(.2, t * .6, 0);
  [imps[2], abuts[2], crowns[2]].forEach(o => { o.visible = true; o.scale.setScalar(.55); o.rotation.set(0, t * .6, 0); });
  const y = 6.0 + f(2); imps[2].position.set(3.7, y, 2.5); abuts[2].position.set(3.7, y + .03, 2.5); crowns[2].position.set(3.7, y + .2, 2.5);
  halo.material.opacity = .35; halo.position.set(0, 5.0, 0); halo.scale.set(13, 8, 1);
  sparkleAt(0, 5.2, 2.5, (t * .6) % 1, 5);
  const k = clamp(t / 2);
  cam.position.set(0, lerp(4.6, 4.4, k), lerp(29, 27.5, k)); cam.lookAt(0, 7.6, 0);
  return [
    { text: 'ฟันปลอม', at: [-3.7, 3.2, 2.5], dx: -110, dy: 20 },
    { text: 'ครอบฟัน', at: [0, 3.3, 2.5], dx: -100, dy: 40 },
    { text: 'รากเทียม', at: [3.7, 3.0, 2.5], dx: -110, dy: 40 },
  ];
}

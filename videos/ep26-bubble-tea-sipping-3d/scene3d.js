// ep26 จิบชานมทั้งวัน ฟันว่าไง? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the x=0 tooth cut in half (back half 3D, front = flat cross-section: enamel, dentin, pulp), as in ep25, plus a
// bubble-tea cup floating at the top right. Every sip -> plaque germs eat the sugar and release acid on the enamel ->
// saliva washes the acid and remineralises -> sipping non-stop: acid again and again, saliva can't keep up -> chalky
// white spot (early decay) -> drink it with a meal, then plain water -> but sticky pearls stay in the gap and feed germs
// -> fluoride toothpaste + floss -> but regular sweetness may exceed the daily sugar -> order less sweet (กรมอนามัย ≤ 6
// teaspoons a day) -> myth: small sips are better than drinking at once? no — more sips = more acid attacks -> payoff.
let ct, sec = {}, spot, spot3, plaque, P, cup, tea, cupPearls = [], drops = [], spit = [], cubes = [], pearls = [], floss, teaDrops = [], paste;

function outline() {
  const R = [[0.18, -1.3], [0.54, -5.9], [0.72, -6.05], [0.9, -5.9], [1.12, -3], [1.38, -0.6], [1.32, 0], [1.6, 0.7], [1.74, 1.6], [1.68, 2.35], [1.5, 2.85], [1.15, 3.18], [0.7, 2.95], [0.25, 2.82]];
  return [[0, -1.1], ...R, [0, 2.8], ...R.slice().reverse().map(([x, y]) => [-x, y])];
}
const shapeOf = (THREE, pts) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y)); s.closePath(); return s; };
function blobGeo(THREE, seed) { const g = new THREE.CircleGeometry(1, 48); const p = g.attributes.position;
  for (let i = 1; i < p.count; i++) { const a = Math.atan2(p.getY(i), p.getX(i)); const r = 1 + .13 * Math.sin(5 * a + seed) + .08 * Math.sin(9 * a + seed * 2); p.setXY(i, Math.cos(a) * r, Math.sin(a) * r); }
  return g; }
const CUP = [2.7, 5.6, 0.6];                         // cup base position (upper right of the cut tooth)

export function setup(L) {
  const { THREE, scene, tooth, rnd, RoundedBoxGeometry } = L;
  L.renderer.localClippingEnabled = true;
  P = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  const en = L.enamel.clone(); en.clippingPlanes = [P]; en.clipShadows = true; en.side = THREE.DoubleSide;
  const rm = L.rootMat.clone(); rm.clippingPlanes = [P]; rm.clipShadows = true; rm.side = THREE.DoubleSide;
  ct = tooth(0, true, en); ct.children[1].material = rm;
  const O = outline();
  const flat = (pts, color, z) => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), new THREE.MeshStandardMaterial({ color, roughness: .55, side: THREE.DoubleSide, emissive: '#000000' })); m.position.z = z; ct.add(m); return m; };
  sec.base = flat(O, '#efdcae', .006);
  const crownPts = O.filter(([x, y]) => y > .25); crownPts.unshift([1.45, .3]); crownPts.push([-1.45, .3]);
  sec.enamel = flat(crownPts.sort((a, b) => Math.atan2(a[1] - 1.2, a[0]) - Math.atan2(b[1] - 1.2, b[0])), '#fbf8f1', .010);
  const dent = O.map(([x, y]) => y > -0.6 ? [x * .82, y > 2 ? 2 + (y - 2) * .72 : y] : [Math.sign(x) * (.72 + (Math.abs(x) - .72) * .62), y * .975]);
  sec.dentin = flat(dent, '#f2d9a4', .014);
  const pulpPts = [[-0.55, 0.1], [-0.62, 1.2], [-0.5, 1.8], [-0.25, 1.45], [0, 1.5], [0.25, 1.45], [0.5, 1.8], [0.62, 1.2], [0.55, 0.1]];
  const pm = new THREE.MeshStandardMaterial({ color: '#f0788a', roughness: .45, side: THREE.DoubleSide });
  [pulpPts, [[-0.62, 0.2], [-0.32, 0.2], [-0.69, -5.6], [-0.77, -5.6]], [[0.62, 0.2], [0.32, 0.2], [0.69, -5.6], [0.77, -5.6]]]
    .forEach(pts => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), pm); m.position.z = .018; ct.add(m); });
  // early lesion: chalky white spot (section + chewing surface)
  const spotMat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, transparent: true, opacity: 1, side: THREE.DoubleSide, emissive: '#ffffff', emissiveIntensity: .25 });
  spot = new THREE.Mesh(blobGeo(THREE, .7), spotMat); spot.position.set(-0.95, 2.86, .026); spot.scale.set(.34, .2, 1); ct.add(spot);
  spot3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), spotMat); spot3.position.set(-.85, 2.96, -.5); spot3.scale.set(.42, .06, .32); ct.add(spot3);
  sec.spotMat = spotMat;
  // plaque film over the crown
  const plm = new THREE.MeshPhysicalMaterial({ color: '#f2d35a', roughness: .6, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }); plm.clippingPlanes = [P];
  plaque = new THREE.Mesh(L.CROWN, plm); plaque.scale.set(1.05, 1.03, 1.05); ct.add(plaque);

  // bubble-tea cup: clear cup, milk tea (scale.y = fill level), pearls at the bottom, dome lid, pink straw
  cup = new THREE.Group(); scene.add(cup);
  { const body = new THREE.Mesh(new THREE.CylinderGeometry(1.15, .88, 3.2, 40, 1, true), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .05, transmission: .6, transparent: true, opacity: .35, side: THREE.DoubleSide, depthWrite: false }));
    body.position.y = 1.6; cup.add(body);
    const bot = new THREE.Mesh(new THREE.CircleGeometry(.88, 40), body.material); bot.rotation.x = -Math.PI / 2; cup.add(bot);
    const tg = new THREE.CylinderGeometry(1.08, .83, 2.9, 40); tg.translate(0, 1.45, 0);
    tea = new THREE.Mesh(tg, new THREE.MeshStandardMaterial({ color: '#c99566', roughness: .5 })); tea.position.y = .05; cup.add(tea);
    const pmat = new THREE.MeshPhysicalMaterial({ color: '#2b1a12', roughness: .15, clearcoat: 1 });
    for (let i = 0; i < 14; i++) { const p = new THREE.Mesh(new THREE.SphereGeometry(.2, 16, 12), pmat); const a = i * 2.4, r = i < 7 ? .55 : .25; p.position.set(Math.cos(a) * r, .22 + (i > 9 ? .3 : 0), Math.sin(a) * r + .1); cup.add(p); cupPearls.push(p); }
    const lid = new THREE.Mesh(new THREE.SphereGeometry(1.17, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2), body.material); lid.scale.y = .45; lid.position.y = 3.2; cup.add(lid);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(1.17, .07, 10, 48), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .3, clearcoat: 1 })); rim.rotation.x = Math.PI / 2; rim.position.y = 3.2; cup.add(rim);
    const straw = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, 5.4, 20), new THREE.MeshPhysicalMaterial({ color: '#ff5fa2', roughness: .25, clearcoat: 1 }));
    straw.position.set(-.35, 3.0, 0); straw.rotation.z = .35; cup.add(straw); }
  // sweet milk-tea drops (from the cup to the tooth)
  const tdm = new THREE.MeshPhysicalMaterial({ color: '#c99566', roughness: .2, clearcoat: 1 });
  for (let i = 0; i < 8; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.2, 14, 10), tdm); d.userData = { x: -1.2 + rnd() * 2.2, z: -.9 + rnd() * .8, d: i * .07 }; scene.add(d); teaDrops.push(d); }
  // acid drops
  const am = new THREE.MeshPhysicalMaterial({ color: '#c6f04a', roughness: .1, clearcoat: 1, transparent: true, opacity: .85, emissive: '#5a7a00', emissiveIntensity: .3 });
  for (let i = 0; i < 12; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), am); d.scale.set(1, 1.35, 1); d.userData = { x: -1.4 + rnd() * 2.6, z: -.9 + rnd() * .8, d: i * .06 }; scene.add(d); drops.push(d); }
  // saliva / water drops (blue)
  const sm = new THREE.MeshPhysicalMaterial({ color: '#8fd8ff', roughness: .05, clearcoat: 1, transparent: true, opacity: .75, emissive: '#1a5a8a', emissiveIntensity: .25 });
  for (let i = 0; i < 18; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.24, 16, 12), sm); d.userData = { x: -2.2 + rnd() * 4.4, z: -1 + rnd() * 1.6, d: i * .05, w: rnd() * 6 }; scene.add(d); spit.push(d); }
  // sugar cubes
  const cm = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .7, sheen: .5, emissive: '#ffffff', emissiveIntensity: .08 });
  for (let i = 0; i < 12; i++) { const c = new THREE.Mesh(new RoundedBoxGeometry(.62, .62, .62, 2, .08), cm); c.castShadow = true; scene.add(c); cubes.push(c); }
  // sticky pearls that get stuck (gap at x≈1.9, chewing groove)
  const pm2 = new THREE.MeshPhysicalMaterial({ color: '#2b1a12', roughness: .15, clearcoat: 1 });
  [[1.9, 3.35, .25], [1.95, 2.85, -.4], [-.5, 3.72, -.55], [-1.9, 3.3, -.2]].forEach(p => { const m = new THREE.Mesh(new THREE.SphereGeometry(.34, 20, 14), pm2); m.userData.to = new THREE.Vector3(...p); scene.add(m); pearls.push(m); });
  // dental floss: thin thread across the gap (along z)
  floss = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 7, 8), new THREE.MeshStandardMaterial({ color: '#e8fbff', emissive: '#4fc3f7', emissiveIntensity: .7 })); floss.rotation.x = Math.PI / 2; scene.add(floss);
  // toothpaste on the brush
  paste = new THREE.Mesh(new THREE.CapsuleGeometry(.35, 1.8, 8, 16), new THREE.MeshPhysicalMaterial({ color: '#dff4ff', roughness: .3, clearcoat: 1 })); paste.rotation.z = Math.PI / 2; L.brush.add(paste); paste.position.set(0, 0, -1.25);
  Object.assign(L.SHOTS, {
    cupW: [[2.6, 6.2, 22], [1.1, 4.1, 0]],       // tooth + cup above it
    secC: [[1.6, 2.4, 12], [0, 1.2, 0]],
    enam: [[0.4, 4.2, 8.5], [-0.4, 3.0, 0]],
    top: [[1.5, 8.5, 12], [0, 3.4, -.3]],
    gapR: [[4.2, 6.2, 11], [1.2, 3.0, -.2]],      // the gap between the cut tooth and its right neighbour
    sky: [[2.2, 5.0, 17], [0.4, 3.8, 0]],         // sugar cubes above the tooth
  });
  L.onReset(() => {
    L.centerTooth.visible = false;
    ct.visible = true; ct.position.set(0, .7, 0); ct.rotation.set(0, 0, 0);
    [spot, spot3, paste, floss, ...drops, ...spit, ...cubes, ...pearls, ...teaDrops].forEach(o => o.visible = false);
    cup.visible = false; cup.position.set(...CUP); cup.rotation.set(0, 0, 0); cup.scale.setScalar(1); tea.scale.y = 1; cupPearls.forEach(p => p.visible = true);
    plaque.material.opacity = 0; spotMat.opacity = 1;
    sec.enamel.material.emissive.set('#000000');
    L.brush.rotation.set(0, 0, 0); L.brush.scale.setScalar(1);
  });
}

function setSpot(k) { spot.visible = spot3.visible = k > .01; sec.spotMat.opacity = k; spot.scale.set(.34 * (.6 + .4 * k), .2 * (.6 + .4 * k), 1); }
// the cup does a "sip": tilts toward the tooth and sweet drops fly to the crown; k = 0..1 progress of one sip
function sip(L, t, t0, dur = .9) {
  const k = L.seg(t, t0, t0 + dur); if (k <= 0 || k >= 1) return;
  cup.rotation.z += .35 * Math.sin(k * Math.PI);
  teaDrops.forEach(d => { const kk = L.seg(k, .15 + d.userData.d, .75 + d.userData.d); d.visible = kk > 0 && kk < 1;
    d.position.set(L.lerp(CUP[0] - .8, d.userData.x, kk), L.lerp(CUP[1] + 3.2, 3.7, kk) + Math.sin(kk * Math.PI) * 1.4, L.lerp(CUP[2], d.userData.z, kk)); });
}
function acidRain(L, t, t0, n = 12) { drops.forEach((dp, i) => { if (i >= n) return; const k = L.seg(t, t0 + dp.userData.d, t0 + .6 + dp.userData.d); dp.visible = k > 0 && k < 1; dp.position.set(dp.userData.x, L.lerp(6.5, 3.6, L.ein(k)), dp.userData.z); }); }
function salivaWash(L, t, t0) { spit.forEach(d => { const k = L.seg(t, t0 + d.userData.d, t0 + 1.1 + d.userData.d); d.visible = k > 0 && k < 1;
  d.position.set(d.userData.x + Math.sin(k * 6 + d.userData.w) * .3, L.lerp(7, 1.6, L.ease(k)), d.userData.z); d.scale.setScalar(1 - .5 * k); }); }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, setCam, chip, sparkleAt, warn, halo, brush } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const LB = 1150, LB2 = 1290, LB3 = 1430;
  const bob = () => { cup.position.y = CUP[1] + Math.sin(t * 2.2) * .12; cup.rotation.y = Math.sin(t * .8) * .3; };
  L.upper.position.y = 40;

  if (t < be(0)) {                                   // hook: one bubble tea, sipped all day... fine?
    const a = bs(0), d = B[0].dur, tm = mk(0, 'tea', .05), sp = mk(0, 'sip', .35), ask = mk(0, 'ask', .85);
    L.upper.position.y = lerp(11, 40, ease(seg(t, a, a + d * .5)));
    cup.visible = true; cup.scale.setScalar(back(seg(t, tm, tm + .5))); bob();
    for (let k = 0; k < 3; k++) sip(L, t, sp + k * 1.0, .8);
    if (t > ask) sparkleAt(CUP[0], CUP[1] + 1.8, CUP[2], seg(t, ask, ask + .8), 2.4);
    setCam('wide', 'cupW', ease(seg(t, a, a + d * .55)));
    chip('h1', '🧋 จิบไปเรื่อยๆ ทั้งวัน', 'dark', LB, t, sp, be(0) - .1);
    chip('h2', '= ไม่เป็นไร ?', 'green', LB2, t, mk(0, 'ok', .6), be(0) - .1, -2);
  } else if (t < be(1)) {                            // each sip: plaque germs eat the sugar and release acid
    const a = bs(1), d = B[1].dur, sp = mk(1, 'sip', .1), gm = mk(1, 'germ', .2), sg = mk(1, 'sugar', .45), ac = mk(1, 'acid', .6), bt = mk(1, 'bite', .85);
    cup.visible = t < ac; bob(); sip(L, t, sp - .2, .8);
    if (t > gm) L.germsArrive(t, gm);
    plaque.material.opacity = .55 * seg(t, gm + .3, gm + 1.2);
    cubes.forEach((c, i) => { if (i > 4) return; const k = seg(t, sg + i * .08, sg + .6 + i * .08); c.visible = k > 0 && t < ac + .3; c.position.set(lerp(CUP[0] - .6, -1 + i * .5, k), lerp(CUP[1] + 2, 3.9, eout(k)), lerp(CUP[2], -.3, k)); c.rotation.set(t * 2 + i, t * 3, 0); c.scale.setScalar(.6 * (1 - ein(seg(t, ac, ac + .3)))); });
    if (t > ac) acidRain(L, t, ac);
    if (t > bt) { warn.material.opacity = .8 * Math.exp(-(t - bt) * 1.4); warn.position.set(-.8, 3.6, .2); warn.scale.setScalar(.6); }
    flash = hit(bt, .2);
    blur = whip(1);
    setCam('cupW', 'top', ease(seg(t, a + .3, ac)));
    chip('pl', '🦠 คราบจุลินทรีย์', 'yel', LB, t, gm, be(1) - .1);
    chip('su', '🍬 กินน้ำตาล', 'dark', LB2, t, sg, ac - .05);
    chip('ac', '💧 ปล่อยกรด กัดเคลือบฟัน', 'red', LB2, t, ac, be(1) - .1, -2);
  } else if (t < be(2)) {                            // saliva washes the acid off and remineralises
    const a = bs(2), d = B[2].dur, sl = mk(2, 'saliva', .05), ws = mk(2, 'wash', .2), fx = mk(2, 'fix', .4), tm = mk(2, 'term', .8);
    plaque.material.opacity = .55 * (1 - .6 * seg(t, ws, fx));
    if (t < ws + .6) L.germsArrive(t, a - 3); else L.germsClear(t, ws + .6, fx + .8);
    salivaWash(L, t, sl); if (t > ws) salivaWash(L, t, ws + .6);
    if (t > fx) { sparkleAt(-.4, 3.6, .3, ((t - fx) * 1.3) % 1, 1.8); sec.enamel.material.emissive.setRGB(0, .12, .32 * (.6 + .4 * Math.sin(t * 6))); }
    blur = whip(2);
    setCam('top', 'enam', ease(seg(t, a, a + d * .6)));
    chip('sl', '💦 น้ำลาย ล้างกรด', 'dark', LB, t, sl + .2, be(2) - .1);
    chip('fx', 'ซ่อมผิวฟันคืน ✨', 'green', LB2, t, fx, tm - .05);
    chip('tm', 'การคืนแร่ธาตุ (Remineralization)', 'green', LB2, t, tm, be(2) - .1);
  } else if (t < be(3)) {                            // sipping non-stop: acid again and again, saliva can't keep up -> white spot
    const a = bs(3), d = B[3].dur, sp = mk(3, 'sip', .05), ag = mk(3, 'again', .2), lt = mk(3, 'late', .35), wh = mk(3, 'white', .55), er = mk(3, 'early', .85);
    cup.visible = false;
    const per = .62, n = Math.max(1, Math.min(9, 1 + Math.floor((t - sp) / per)));
    for (let k = 0; k < 9; k++) { sip(L, t, sp + k * per, .55); }
    for (let k = 0; k < 8; k++) if (t > ag + k * per) acidRain(L, t, ag + k * per, 6);
    if (t > lt) salivaWash(L, t, lt);
    plaque.material.opacity = .45;
    setSpot(ease(seg(t, wh, wh + 1)));
    if (t > wh) { halo.material.opacity = .08 * eout(seg(t, wh, wh + .4)); halo.position.set(-.9, 3.6, .5); halo.scale.set(2.5, 2.5, 1); }
    if (t > sp) L.calendar('จิบครั้งที่', String(n), t > be(3) - .3 ? 1 - seg(t, be(3) - .3, be(3)) : 1 + .12 * (1 - seg(t, sp + (n - 1) * per, sp + (n - 1) * per + .2)));
    if (t > er) { warn.material.opacity = .7 * Math.exp(-(t - er) * 1.2); warn.position.set(-.9, 3.6, .3); warn.scale.setScalar(.55); }
    blur = whip(3);
    setCam('enam', 'top', ease(seg(t, a, a + .8)));
    if (t > wh - .3) setCam('top', 'enam', ease(seg(t, wh - .3, wh + .8)));
    chip('ag', '🔁 กรดมาซ้ำๆ', 'red', LB, t, ag, be(3) - .1);
    chip('lt', '💦 น้ำลายซ่อมไม่ทัน', 'dark', LB2, t, lt, be(3) - .1, -2);
    chip('ws', '⚪ จุดขาวขุ่น = ฟันผุระยะแรก', 'yel', LB3, t, wh + .4, be(3) - .1, 2);
  } else if (t < be(4)) {                            // fix: finish it with a meal, then drink plain water
    const a = bs(4), d = B[4].dur, dr = mk(4, 'drink', .05), ml = mk(4, 'meal', .3), wt = mk(4, 'water', .6);
    cup.visible = t < wt + .3; bob(); setSpot(1);
    tea.scale.y = Math.max(.02, 1 - ease(seg(t, dr + .2, ml + .6)));
    cupPearls.forEach((p, i) => p.visible = i / cupPearls.length > seg(t, dr + .4, ml + .6));
    cup.scale.setScalar(1 - ein(seg(t, wt, wt + .3)));
    if (t > wt) { salivaWash(L, t, wt); sparkleAt(-.2, 3.8, .3, seg(t, wt + .6, wt + 1.4), 2); }
    flash = t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0;
    setCam('enam', 'cupW', ease(seg(t, a, a + .7)));
    if (t > wt - .2) setCam('cupW', 'top', ease(seg(t, wt - .2, wt + .8)));
    chip('dm', '🍽 ดื่มให้หมดพร้อมมื้ออาหาร', 'green', LB, t, ml - .1, be(4) - .1);
    chip('wt', '💧 แล้วดื่มน้ำเปล่าตาม', 'dark', LB2, t, wt, be(4) - .1);
  } else if (t < be(5)) {                            // but sticky pearls stay in the gap and feed the germs
    const a = bs(5), d = B[5].dur, pr = mk(5, 'pearl', .05), st = mk(5, 'stick', .25), fd = mk(5, 'food', .5);
    setSpot(1);
    pearls.forEach((p, i) => { const k = seg(t, pr + i * .15, pr + .7 + i * .15); p.visible = k > 0; const to = p.userData.to;
      p.position.set(lerp(to.x + 1.5, to.x, k), lerp(9, to.y, eout(k)), to.z); const sq = t > st ? 1 + .12 * Math.sin((t - st) * 9) * Math.exp(-(t - st) * 2) : 1; p.scale.set(sq, 1 / sq, sq); });
    if (t > fd) L.germsArrive(t, fd);
    plaque.material.opacity = .3 * seg(t, fd, fd + 1);
    if (t > st) { warn.material.opacity = .7 * Math.exp(-(t - st) * 1.2); warn.position.set(1.9, 3.2, .4); warn.scale.setScalar(.5); }
    flash = hit(st, .2);
    blur = whip(5);
    setCam('top', 'gapR', ease(seg(t, a, a + .9)));
    chip('pr', '⚫ ไข่มุกหนึบ ติดร่องฟัน', 'dark', LB, t, st, be(5) - .1);
    chip('fd', '🦠 อาหารของเชื้อโรค', 'red', LB2, t, fd, be(5) - .1, -2);
  } else if (t < be(6)) {                            // fix: fluoride toothpaste + floss out the pearls
    const a = bs(6), d = B[6].dur, br = mk(6, 'brush', .05), fl = mk(6, 'fluor', .2), fs = mk(6, 'floss', .45), cl = mk(6, 'clean', .75);
    setSpot(1 - .7 * ease(seg(t, fl, cl + .6)));
    pearls.forEach((p, i) => { const gone = i < 2 ? cl + i * .2 : fl + .3 + (i - 2) * .25; const k = 1 - ein(seg(t, gone, gone + .3)); p.visible = k > 0; p.position.copy(p.userData.to); p.scale.setScalar(k); if (t > gone) p.position.y += 2 * seg(t, gone, gone + .3); });
    if (t < fs) { L.germsClear(t, br + .3, fs); plaque.material.opacity = .3 * (1 - seg(t, br + .3, fs)); }
    if (t < fs + .2) { brush.visible = true; paste.visible = t < fl + .8; paste.scale.setScalar(1 - .7 * seg(t, fl, fl + .8));
      brush.position.set(lerp(-6, 0, eout(seg(t, br, br + .4))) + (t > br + .4 ? Math.sin(t * 14) * .9 : 0), 4.9, -.4); brush.rotation.set(Math.PI / 2, 0, 0);
      if (t > fs - .2) brush.position.x += ein(seg(t, fs - .2, fs + .2)) * 12; }
    if (t > fs) { floss.visible = true; const k = seg(t, fs, fs + .5); floss.position.set(1.88, lerp(6.5, 3.7, eout(k)) + (k >= 1 ? .35 * Math.sin((t - fs) * 10) : 0), Math.sin(t * 16) * .6); }
    if (t > cl) sparkleAt(1.9, 3.4, .3, seg(t, cl + .3, cl + 1), 1.6);
    blur = whip(6);
    setCam('gapR', 'top', ease(seg(t, a, br + .4)));
    if (t > fs - .3) setCam('top', 'gapR', ease(seg(t, fs - .3, fs + .5)));
    chip('fl', '🪥 ยาสีฟันฟลูออไรด์', 'green', LB, t, fl, be(6) - .1);
    chip('fs', '🧵 ไหมขัดฟัน', 'dark', LB2, t, fs + .1, be(6) - .1, -2);
  } else if (t < be(7)) {                            // regular sweetness may exceed -> order less sweet; ≤ 6 teaspoons a day
    const a = bs(7), d = B[7].dur, sw = mk(7, 'sweet', .05), ov = mk(7, 'over', .15), ls = mk(7, 'less', .45), dh = mk(7, 'doh', .6), sx = mk(7, 'six', .8);
    setSpot(.3);
    cubes.forEach((c, i) => { const r = Math.floor(i / 4), col = i % 4; const k = back(seg(t, ov + i * .07, ov + .4 + i * .07)); const gone = i >= 6 ? 1 - ein(seg(t, ls + (11 - i) * .08, ls + .3 + (11 - i) * .08)) : 1;
      c.visible = k > 0 && gone > 0; c.position.set(-1.65 + col * 1.1 + (r % 2) * .3, 4.9 + r * .85, -.2); c.scale.setScalar(1.15 * k * gone); c.rotation.set(0, .3 + i, 0); });
    if (t > ls) { cubes.slice(0, 6).forEach((c, i) => { if (t > sx) c.position.y += Math.abs(Math.sin((t - sx) * 6 + i)) * .15 * Math.exp(-(t - sx)); }); }
    if (t > dh) L.calendar('น้ำตาล/วัน', '≤6', back(seg(t, dh, dh + .4)) * (t > be(7) - .3 ? 1 - seg(t, be(7) - .3, be(7)) : 1));
    if (t > sx) sparkleAt(0, 5.6, .3, seg(t, sx, sx + .9), 2.6);
    flash = hit(ls, .2);
    blur = whip(7);
    setCam('top', 'sky', ease(seg(t, a, ov + .5)));
    chip('sw', '😋 หวานปกติ', 'dark', LB, t, sw, ls - .05);
    chip('ov', 'น้ำตาลอาจเกิน!', 'red', LB2, t, ov + .2, ls - .05, -2);
    chip('ls', '✓ สั่งหวานน้อย', 'green', LB, t, ls, be(7) - .1);
    chip('dh', 'กรมอนามัย: ไม่เกินวันละ 6 ช้อนชา', 'yel', LB2, t, sx - .3, be(7) - .1);
  } else if (t < be(8)) {                            // myth: small sips better than drinking at once? no — more sips, more acid
    const a = bs(8), d = B[8].dur, th = mk(8, 'think', .2), no = mk(8, 'no', .5), of = mk(8, 'often', .7);
    cup.visible = true; bob(); setSpot(.3);
    if (t > of) { for (let k = 0; k < 6; k++) { sip(L, t, of + k * .45, .4); if (t > of + .3 + k * .45) acidRain(L, t, of + .3 + k * .45, 5); }
      warn.material.opacity = .7 * (.5 + .5 * Math.sin((t - of) * 12)); warn.position.set(-.4, 3.7, .3); warn.scale.setScalar(.6); }
    flash = hit(no, .25);
    blur = whip(8);
    setCam('top', 'cupW', ease(seg(t, a, a + .8)));
    chip('m1', 'จิบทีละนิด ดีกว่าดื่มรวดเดียว?', 'dark', LB, t, th, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', LB, t, no, be(8) - .1, -4);
    chip('m3', 'ยิ่งจิบบ่อย = โดนกรดบ่อย', 'yel', LB2, t, of, be(8) - .1, 2);
  } else if (t < be(9)) {                            // payoff
    const a = bs(9), d = B[9].dur;
    L.upper.position.y = lerp(40, 11, eout(seg(t, a + .5, a + 1.5)));
    L.confetti(t, a); sparkleAt(0, 4, 1, seg(t, a, a + .9), 3);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, 3, -1);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('cupW', 'gap', ease(seg(t, a, a + d * .8)));
    chip('y1', '🎉 ดื่มเป็นเวลา', 'green', 190, t, mk(9, 'time', .3), be(9) - .1);
    chip('y2', '😁 ฟันแข็งแรง ยิ้มสวย', 'dark', 330, t, mk(9, 'smile', .6), be(9) - .1);
  } else {
    L.upper.position.y = 11; setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: the cut tooth, a bubble tea above it sending sweet drops; acid already on the enamel
export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt } = L;
  L.upper.position.y = 40;
  cup.visible = true; cup.position.set(2.7, 4.5, .6); cup.rotation.set(0, .3, .2);
  plaque.material.opacity = .4; setSpot(.8);
  drops.forEach((dp, i) => { if (i > 6) return; dp.visible = true; dp.position.set(dp.userData.x, 4.2 + (i % 3) * .5, dp.userData.z + .4); });
  sparkleAt(2.7, 6.4, .6, (t * .8) % 1, 2);
  const k = clamp(t / 2);
  cam.position.set(lerp(2.6, 2.4, k), lerp(6.4, 6.2, k), lerp(18, 17, k)); cam.lookAt(0.9, 5.9, 0);
  return [
    { text: 'ชานมไข่มุก', at: [1.6, 5.8, 0.6], dx: -330, dy: 0 },
    { text: 'กรด!', at: [0.6, 4.6, 0.3], dx: 90, dy: -10 },
    { text: 'เคลือบฟัน', at: [-0.8, 3.4, 0.05], dx: 140, dy: 90 },
  ];
}

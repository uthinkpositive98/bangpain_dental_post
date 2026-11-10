// ep25 ไม่ปวด แปลว่าไม่ผุ จริงไหม? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the x=0 tooth cut in half (back half 3D, front = flat cross-section: enamel, dentin, pulp + canals), as in ep18.
// Sweets -> plaque germs make acid -> enamel has no nerves: a painless white spot -> fluoride toothpaste remineralises it ->
// if missed, the cavity reaches the dentin (sensitive) -> the dentist drills + fills -> if still left, it reaches the pulp
// (throbbing, root canal) -> check-ups every 6 months find it before it hurts -> myth: pain gone = healed? no, the pulp may
// be dead but germs remain -> payoff: found early, small filling.
let ct, sec = {}, cav, cav3, fil, fil3, spot, spot3, plaque, candy, drops = [], paste, iceCube, drill, scan, canalGerms = [], tipGlow, P;
const PULP = { ok: '#f0788a', hot: '#e3203f', dead: '#8d7f7c' };

function outline() {
  const R = [[0.18, -1.3], [0.54, -5.9], [0.72, -6.05], [0.9, -5.9], [1.12, -3], [1.38, -0.6], [1.32, 0], [1.6, 0.7], [1.74, 1.6], [1.68, 2.35], [1.5, 2.85], [1.15, 3.18], [0.7, 2.95], [0.25, 2.82]];
  return [[0, -1.1], ...R, [0, 2.8], ...R.slice().reverse().map(([x, y]) => [-x, y])];
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
  const O = outline();
  const flat = (pts, color, z) => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), new THREE.MeshStandardMaterial({ color, roughness: .55, side: THREE.DoubleSide, emissive: '#000000' })); m.position.z = z; ct.add(m); return m; };
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
  // early lesion: chalky white spot (section + chewing surface)
  const spotMat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, transparent: true, opacity: 1, side: THREE.DoubleSide, emissive: '#ffffff', emissiveIntensity: .25 });
  spot = new THREE.Mesh(blobGeo(THREE, .7), spotMat); spot.position.set(-0.95, 2.86, .026); spot.scale.set(.34, .2, 1); ct.add(spot);
  spot3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), spotMat); spot3.position.set(-.85, 2.96, -.5); spot3.scale.set(.42, .06, .32); ct.add(spot3);
  // cavity + filling
  cav = new THREE.Mesh(blobGeo(THREE, 1.3), new THREE.MeshStandardMaterial({ color: '#4a2c16', roughness: .8, side: THREE.DoubleSide })); cav.position.z = .024; ct.add(cav);
  cav3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), cav.material); ct.add(cav3);
  fil = new THREE.Mesh(blobGeo(THREE, 2.1), new THREE.MeshPhysicalMaterial({ color: '#9fd0ff', roughness: .25, clearcoat: 1, side: THREE.DoubleSide })); fil.position.z = .028; ct.add(fil);
  fil3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), fil.material); ct.add(fil3);
  // plaque film over the crown (yellow, see-through)
  const plm = new THREE.MeshPhysicalMaterial({ color: '#f2d35a', roughness: .6, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }); plm.clippingPlanes = [P];
  plaque = new THREE.Mesh(L.CROWN, plm); plaque.scale.set(1.05, 1.03, 1.05); ct.add(plaque);
  // a wrapped candy
  candy = new THREE.Group(); scene.add(candy);
  { const cm = new THREE.MeshPhysicalMaterial({ color: '#ff5fa2', roughness: .2, clearcoat: 1 });
    const b = new THREE.Mesh(new THREE.SphereGeometry(.75, 28, 18), cm); b.scale.set(1.2, .9, .9); candy.add(b);
    const wm = new THREE.MeshPhysicalMaterial({ color: '#ffe14d', roughness: .3, clearcoat: .6 });
    [-1, 1].forEach(s => { const w = new THREE.Mesh(new THREE.ConeGeometry(.5, .8, 16), wm); w.rotation.z = s * Math.PI / 2; w.position.x = s * 1.2; candy.add(w); }); }
  // acid drops
  const am = new THREE.MeshPhysicalMaterial({ color: '#c6f04a', roughness: .1, clearcoat: 1, transparent: true, opacity: .85, emissive: '#5a7a00', emissiveIntensity: .3 });
  for (let i = 0; i < 12; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), am); d.scale.set(1, 1.35, 1); d.userData = { x: -1.4 + rnd() * 2.6, z: -.9 + rnd() * .8, d: i * .09 }; scene.add(d); drops.push(d); }
  // toothpaste blob (fluoride) on the brush
  paste = new THREE.Mesh(new THREE.CapsuleGeometry(.35, 1.8, 8, 16), new THREE.MeshPhysicalMaterial({ color: '#dff4ff', roughness: .3, clearcoat: 1 })); paste.rotation.z = Math.PI / 2; L.brush.add(paste); paste.position.set(0, 0, -1.25);
  // ice cube
  iceCube = new THREE.Mesh(new RoundedBoxGeometry(1.2, 1.2, 1.2, 3, .2), new THREE.MeshPhysicalMaterial({ color: '#bfeaff', roughness: .05, clearcoat: 1, transparent: true, opacity: .7 })); scene.add(iceCube);
  // dental drill (handpiece head + bur)
  drill = new THREE.Group(); scene.add(drill);
  { const ti = L.titanium;
    const head = new THREE.Mesh(new THREE.CylinderGeometry(.5, .5, .8, 24), new THREE.MeshPhysicalMaterial({ color: '#e9eef3', roughness: .25, clearcoat: 1 })); head.position.y = 1.9; drill.add(head);
    const neck = new THREE.Mesh(new THREE.CapsuleGeometry(.32, 5, 8, 16), head.material); neck.rotation.z = Math.PI / 2; neck.position.set(2.9, 1.95, 0); drill.add(neck);
    const shank = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 1.3, 12), ti); shank.position.y = .95; drill.add(shank);
    const bur = new THREE.Mesh(new THREE.SphereGeometry(.2, 16, 12), new THREE.MeshStandardMaterial({ color: '#d9b24a', metalness: 1, roughness: .3 })); bur.position.y = .2; drill.add(bur); drill.userData.bur = bur; }
  // check-up scan sweep
  scan = new THREE.Mesh(new THREE.BoxGeometry(5, .08, 3), new THREE.MeshBasicMaterial({ color: '#5ff0ff', transparent: true, opacity: .55, depthWrite: false, blending: THREE.AdditiveBlending })); scene.add(scan);
  // germs that stay in the canals (myth beat) + a red glow at the root tip
  for (let i = 0; i < 8; i++) { const m = new THREE.Mesh(L.germGeo, L.germMat); m.userData = { side: i % 2 ? 1 : -1, k: (i >> 1) / 4 + .1, ph: rnd() * 6 }; scene.add(m); canalGerms.push(m); }
  const redTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,50,70,.95)'); gr.addColorStop(1, 'rgba(255,50,70,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  tipGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: redTex, transparent: true, depthWrite: false })); scene.add(tipGlow);
  Object.assign(L.SHOTS, {
    secW: [[2.2, 0.3, 19.5], [0, -0.9, 0]],      // whole cut tooth, crown in the upper part
    secC: [[1.6, 2.4, 12], [0, 1.2, 0]],         // crown + pulp chamber
    enam: [[0.4, 4.2, 8.5], [-0.4, 3.0, 0]],     // close on the enamel / white spot
    top: [[1.5, 8.5, 12], [0, 3.4, -.3]],             // looking down at the chewing surface (brush, drill)
    cov: [[3.4, 3.2, 14.5], [0.2, 1.6, 0]],
  });
  L.onReset(() => {
    L.centerTooth.visible = false;
    ct.visible = true; ct.position.set(0, .7, 0); ct.rotation.set(0, 0, 0);
    [cav, cav3, fil, fil3, spot, spot3, candy, iceCube, drill, scan, tipGlow, paste, ...drops, ...canalGerms].forEach(o => o.visible = false);
    plaque.material.opacity = 0; plaque.visible = true; spotMat.opacity = 1;
    sec.pulpMat.color.set(PULP.ok); sec.pulpMat.emissive.set('#000000'); sec.enamel.material.emissive.set('#000000'); sec.dentin.material.emissive.set('#000000');
    L.brush.rotation.set(0, 0, 0); L.brush.scale.setScalar(1);
  });
  sec.spotMat = spotMat;
}

// cavity stage k: 0 = pit in the enamel, ~.5 = into the dentin, 1 = touching the pulp horn
function setCavity(L, k) {
  cav.visible = cav3.visible = k > 0;
  const r = L.lerp(.2, .7, k); cav.position.set(L.lerp(-0.98, -0.56, k), L.lerp(2.72, 2.12, k), .024); cav.scale.set(r, r, 1);
  cav3.position.set(-.85, 2.93, -.5); cav3.scale.set(L.lerp(.25, .6, k), .1, L.lerp(.2, .45, k));
}
// filling sized for cavity stage k, pop-in progress s
function setFilling(L, s, k) { fil.visible = fil3.visible = s > 0; const b = L.back(s), r = L.lerp(.2, .7, k) * 1.08;
  fil.position.set(L.lerp(-0.98, -0.56, k), L.lerp(2.72, 2.12, k), .028); fil.scale.set(r * b, r * b, 1);
  fil3.position.set(-.85, 2.95, -.5); fil3.scale.set(L.lerp(.27, .62, k) * b, .11, L.lerp(.22, .47, k) * b); }
function setSpot(k) { spot.visible = spot3.visible = k > .01; sec.spotMat.opacity = k; }

export function frame(t, L) {
  const { bs, be, mk, B, T, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, warn, halo, brush, germs } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const LB = 1150, LB2 = 1290, LB3 = 1430;           // chip rows under the caption (the crown sits in the upper half)
  const enamelGlow = k => sec.enamel.material.emissive.setRGB(.25 * k, .2 * k, 0);

  if (t < be(0)) {                                   // hook: no pain at all... so no cavity?
    const a = bs(0), d = B[0].dur;
    L.upper.position.y = lerp(11, 40, ease(seg(t, a, a + d * .6)));
    setCam('wide', 'secC', ease(seg(t, a + .2, a + d)));
    if (t > mk(0, 'ask', .7)) sparkleAt(0, 4.2, .8, seg(t, mk(0, 'ask', .7), mk(0, 'ask', .7) + .8), 2.4);
    chip('ok', '😌 ไม่ปวดเลย', 'green', LB, t, a + .2, be(0) - .1);
    chip('q', '= ไม่มีฟันผุ ?', 'dark', LB2, t, mk(0, 'ok', .4), be(0) - .1, -2);
  } else if (t < be(1)) {                            // sweets -> plaque germs -> acid attacks the enamel
    const a = bs(1), d = B[1].dur, sw = mk(1, 'sweet', .1), gm = mk(1, 'germ', .25), ac = mk(1, 'acid', .6), bt = mk(1, 'bite', .85);
    L.upper.position.y = 40;
    if (t > sw) { candy.visible = t < sw + 1.4; const k = seg(t, sw, sw + .8); candy.position.set(lerp(-3, 1.6, k), lerp(7, 4.4, eout(k)) + Math.sin(k * Math.PI) * 1.2, 1); candy.rotation.set(t * 2, t * 3, 0); candy.scale.setScalar(.8 * (1 - ein(seg(t, sw + 1, sw + 1.4)))); }
    if (t > gm) L.germsArrive(t, gm);
    plaque.material.opacity = .55 * seg(t, gm + .3, gm + 1.2);
    if (t > ac) drops.forEach(dp => { const k = seg(t, ac + dp.userData.d, ac + .7 + dp.userData.d); dp.visible = k > 0 && k < 1; dp.position.set(dp.userData.x, lerp(6.5, 3.6, ein(k)), dp.userData.z); });
    if (t > bt) { setSpot(.6 * seg(t, bt, bt + .6)); warn.material.opacity = .8 * Math.exp(-(t - bt) * 1.4); warn.position.set(-.8, 3.6, .2); warn.scale.setScalar(.6); }
    flash = hit(bt, .2);
    blur = whip(1);
    setCam('secC', 'top', ease(seg(t, a + .2, ac)));
    chip('sw', '🍬 กินหวาน', 'dark', LB, t, sw, gm - .05);
    chip('pl', '🦠 คราบจุลินทรีย์', 'yel', LB, t, gm, be(1) - .1);
    chip('ac', '💧 กรด กัดเคลือบฟัน', 'red', LB2, t, ac, be(1) - .1, -2);
  } else if (t < be(2)) {                            // enamel has no nerves -> no pain; only a chalky white spot
    const a = bs(2), d = B[2].dur, nv = mk(2, 'nerve', .1), wh = mk(2, 'white', .75);
    plaque.material.opacity = .35;
    if (t < a + 1) L.germsArrive(t, a - 2);
    enamelGlow(t > nv + .2 && t < wh ? .6 + .4 * Math.sin(t * 8) : 0);
    setSpot(lerp(.6, 1, seg(t, wh, wh + .5)));
    if (t > wh) { halo.material.opacity = .18 * eout(seg(t, wh, wh + .4)); halo.position.set(-.9, 3.6, .5); halo.scale.set(3, 3, 1); }
    blur = whip(2);
    setCam('top', 'enam', ease(seg(t, a, a + d * .5)));
    chip('nv', 'เคลือบฟัน = ไม่มีเส้นประสาท', 'dark', LB, t, nv + .2, be(2) - .1);
    chip('np', '😶 ไม่เจ็บสักนิด', 'green', LB2, t, mk(2, 'here', .4), be(2) - .1);
    chip('ws', '⚪ จุดขาวขุ่น = ผุระยะแรก', 'yel', LB3, t, wh, be(2) - .1, 2);
  } else if (t < be(3)) {                            // fluoride toothpaste twice a day -> remineralisation repairs the spot
    const a = bs(3), d = B[3].dur, br = mk(3, 'brush', .05), fl = mk(3, 'fluor', .3), fx = mk(3, 'fix', .5), tm = mk(3, 'term', .85);
    plaque.material.opacity = .35 * (1 - seg(t, br + .3, fl));
    L.germsClear(t, br + .2, fl);
    brush.visible = true; paste.visible = t < fx + .3; paste.scale.setScalar(1 - seg(t, fl, fx));
    brush.position.set(lerp(-6, 0, eout(seg(t, br, br + .5))) + (t > br + .5 ? Math.sin(t * 14) * .9 : 0), 4.9, -.4); brush.rotation.set(Math.PI / 2, 0, 0);
    brush.visible = t < tm + .4; if (t > tm) brush.position.x += ein(seg(t, tm, tm + .4)) * 12;
    setSpot(1 - ease(seg(t, fx, tm + .4)));
    if (t > fx) { sparkleAt(-.9, 3.6, .3, ((t - fx) * 1.4) % 1, 1.6); sec.enamel.material.emissive.setRGB(0, .12 * (1 - seg(t, tm, be(3))), .3 * (1 - seg(t, tm, be(3)))); }
    blur = whip(3);
    setCam('enam', 'top', ease(seg(t, a, br + .6)));
    if (t > fx + .4) setCam('top', 'enam', ease(seg(t, fx + .4, tm)));
    chip('b2', '🪥 แปรงฟันวันละ 2 ครั้ง', 'dark', LB, t, br + .1, fx - .05);
    chip('fl', 'ยาสีฟันฟลูออไรด์', 'green', LB2, t, fl, fx - .05);
    chip('fx', 'ซ่อมผิวฟันระยะแรก ✨', 'dark', LB, t, fx, be(3) - .1);
    chip('tm', 'การคืนแร่ธาตุ (Remineralization)', 'green', LB2, t, tm, be(3) - .1);
  } else if (t < be(4)) {                            // missed -> the cavity reaches the dentin -> sensitive to sweet / cold
    const a = bs(4), d = B[4].dur, sp = mk(4, 'spread', .25), zg = mk(4, 'zing', .7);
    setCavity(L, lerp(.05, .55, ease(seg(t, sp, sp + 1.6))));
    if (t < sp) setSpot(seg(t, a, a + .4));
    sec.dentin.material.emissive.setRGB(t > sp + .8 && t < zg ? .18 : 0, t > sp + .8 && t < zg ? .1 : 0, 0);
    if (t > zg - .6) { iceCube.visible = t < zg + .5; iceCube.position.set(-.8, lerp(9, 4.3, ein(seg(t, zg - .6, zg))), -.4); iceCube.rotation.set(t * 2, t * 3, 0); iceCube.scale.setScalar(1 - seg(t, zg + .2, zg + .5)); }
    if (t > zg) { warn.material.opacity = .9 * Math.exp(-(t - zg) * 1.2); warn.position.set(-.6, 2.9, .6); warn.scale.setScalar(.7 + .05 * Math.sin(t * 20)); ct.position.x = t < zg + .5 ? Math.sin(t * 50) * .04 : 0; }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(zg, .3));
    setCam('enam', 'secC', ease(seg(t, a + .2, sp + 1)), t > zg && t < zg + .4 ? .1 : 0, t);
    chip('rw', '⏩ ถ้าไม่รู้ตัว ปล่อยไว้…', 'yel', 190, t, a + .1, sp + 1.2);
    chip('dn', 'ผุลามถึงเนื้อฟัน', 'red', LB, t, sp + .5, be(4) - .1);
    chip('zg', '🥶 เสียว! หวาน / เย็น', 'dark', LB2, t, zg, be(4) - .1, -3);
  } else if (t < be(5)) {                            // dentist drills out the decay and fills it
    const a = bs(5), d = B[5].dur, dr = mk(5, 'drill', .2), fl = mk(5, 'fill', .5), se = mk(5, 'seal', .8);
    const k = .55;
    if (t < fl) setCavity(L, k); else setFilling(L, seg(t, fl, fl + .45), k);
    if (t > dr - .5 && t < fl + .3) { drill.visible = true; const kd = eout(seg(t, dr - .5, dr)) * (1 - ein(seg(t, fl - .1, fl + .3)));
      drill.position.set(-.8 + Math.sin(t * 40) * .03, lerp(9, 3.0, kd), -.35); drill.userData.bur.rotation.y = t * 50; }
    if (t > dr && t < fl) cav.material.color.setRGB(.29 + .3 * seg(t, dr, fl), .17 + .3 * seg(t, dr, fl), .09 + .3 * seg(t, dr, fl)); else cav.material.color.set('#4a2c16');
    if (t > fl) sparkleAt(-.8, 3.5, .3, seg(t, fl + .3, fl + 1), 1.8);
    flash = hit(se, .2);
    blur = whip(5);
    setCam('secC', 'top', ease(seg(t, a, dr)));
    if (t > fl) setCam('top', 'secC', ease(seg(t, fl, fl + .9)));
    chip('dr', '👩‍⚕️ กรอส่วนที่ผุออก', 'dark', LB, t, dr, be(5) - .1);
    chip('fl5', '✓ อุดฟัน ปิดรูให้แน่น', 'green', LB2, t, fl + .2, be(5) - .1);
  } else if (t < be(6)) {                            // left even longer -> the pulp -> throbbing pain -> root canal
    const a = bs(6), d = B[6].dur, pp = mk(6, 'pulp', .15), th = mk(6, 'throb', .45), rc = mk(6, 'rc', .8);
    setCavity(L, lerp(.55, 1, ease(seg(t, pp, pp + 1.4))));
    const hot = seg(t, pp + .8, th);
    sec.pulpMat.color.set(PULP.ok).lerp(new L.THREE.Color(PULP.hot), hot); sec.pulpMat.emissive.set('#ff0020'); sec.pulpMat.emissiveIntensity = hot * (.25 + .25 * Math.sin(t * 14));
    if (t > th) { warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - th) * 12)); warn.position.set(0, 1.9, .6); warn.scale.setScalar(.75 + .07 * Math.sin(t * 12)); }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(th, .25));
    setCam('secC', 'secW', ease(seg(t, rc - .4, rc + .6)), t > th && t < rc ? .06 : 0, t);
    chip('rw6', '⏩ ถ้ายังไม่ไปหาหมอ…', 'yel', 190, t, a + .1, pp + 1);
    chip('pp', 'ผุถึงโพรงประสาท', 'red', LB, t, pp + .6, be(6) - .1);
    chip('th', '⚡ ปวดตุ๊บๆ นอนไม่หลับ', 'dark', LB2, t, th, be(6) - .1, -3);
    chip('rc', 'อาจต้องรักษารากฟัน', 'red', LB3, t, rc, be(6) - .1, 2);
  } else if (t < be(7)) {                            // rewind: check-ups every 6 months find it before it hurts
    const a = bs(7), d = B[7].dur, ck = mk(7, 'check', .25), fd = mk(7, 'find', .55);
    setSpot(t < fd + .9 ? 1 : 1 - seg(t, fd + .9, fd + 1.3)); setCavity(L, t < fd + .9 ? .02 : 0);
    if (t > fd + .9) setFilling(L, seg(t, fd + .9, fd + 1.3), .02);
    if (t > ck) { scan.visible = t < fd + .1; scan.position.set(0, lerp(5, -1, seg(t, ck, fd)), -.3); }
    if (t > fd) { halo.material.opacity = .45 * eout(seg(t, fd, fd + .4)); halo.position.set(-.9, 3.6, .5); halo.scale.set(4, 4, 1); sparkleAt(-.9, 3.6, .3, seg(t, fd + 1, fd + 1.7), 1.6); }
    L.calendar('ตรวจทุก', '6', t > be(7) - .3 ? 1 - seg(t, be(7) - .3, be(7)) : back(seg(t, ck, ck + .35)));
    if (t < ck) L.calendar('ตรวจทุก', '6', 0);
    flash = t < a + .3 ? .6 * (1 - seg(t, a, a + .3)) : 0;
    setCam('secW', 'secC', ease(seg(t, a, a + d * .6)));
    chip('rw7', '⏪ ย้อนเวลา', 'yel', 470, t, a + .1, ck - .05);
    chip('w', 'อย่ารอให้ปวด!', 'dark', LB, t, a + .2, be(7) - .1);
    chip('mo', '📅 ตรวจฟันทุก 6 เดือน', 'green', LB2, t, ck + .2, be(7) - .1);
    chip('fd', '🔍 เจอตั้งแต่ยังไม่เจ็บ', 'yel', LB3, t, fd, be(7) - .1, 2);
  } else if (t < be(8)) {                            // myth: the pain went away = healed? no — dead pulp, germs still there
    const a = bs(8), d = B[8].dur, no = mk(8, 'no', .45), dd = mk(8, 'dead', .6), st = mk(8, 'still', .85);
    setCavity(L, 1);
    const dk = seg(t, dd, dd + .8); sec.pulpMat.color.set(PULP.hot).lerp(new L.THREE.Color(PULP.dead), dk); sec.pulpMat.emissive.set('#000000');
    if (t < dd) { sec.pulpMat.emissive.set('#ff0020'); sec.pulpMat.emissiveIntensity = .2 * (1 - seg(t, a, no)); }
    canalGerms.forEach(g => { const k = back(seg(t, st - .2 + g.userData.k * .3, st + .2 + g.userData.k * .3)); g.visible = k > 0; const s = g.userData.side;
      const y = lerp(1.2, -4.9, g.userData.k + .05); g.position.set(s * lerp(.5, .73, g.userData.k), y + .7 + Math.sin(t * 5 + g.userData.ph) * .06, .45); g.scale.setScalar(.5 * k); g.rotation.set(t * 3, t * 2 + g.userData.ph, 0); });
    if (t > st) { tipGlow.visible = true; tipGlow.position.set(0, -5.2, .5); tipGlow.scale.setScalar(3.5 * eout(seg(t, st, st + .6))); tipGlow.material.opacity = .55 + .2 * Math.sin(t * 6); }
    flash = hit(no, .25);
    blur = whip(8);
    setCam('secC', 'secW', ease(seg(t, dd - .3, dd + .8)));
    chip('m1', 'ปวดหายเอง = หายแล้ว?', 'dark', LB, t, a + .3, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', LB, t, no, be(8) - .1, -4);
    chip('m3', '💀 ประสาทฟันอาจตายแล้ว', 'dark', LB2, t, dd + .3, be(8) - .1);
    chip('m4', '🦠 แต่เชื้อยังอยู่', 'red', LB3, t, st, be(8) - .1, 2);
  } else if (t < be(9)) {                            // payoff: found early, easy fix
    const a = bs(9), d = B[9].dur;
    setFilling(L, 1, .02);
    L.upper.position.y = lerp(40, 11, eout(seg(t, a + .5, a + 1.5)));
    L.confetti(t, a); sparkleAt(0, 4, 1, seg(t, a, a + .9), 3);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, 3, -1);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('secC', 'gap', ease(seg(t, a, a + d * .8)));
    chip('y1', '🎉 เจอเร็ว ซ่อมง่าย', 'green', 190, t, mk(9, 'fast', .3), be(9) - .1);
    chip('y2', '😁 ยิ้มได้สบายใจ', 'dark', 330, t, mk(9, 'smile', .6), be(9) - .1);
  } else {                                           // under the end card
    setFilling(L, 1, .02); L.upper.position.y = 11; setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: the cut tooth looks fine from outside, but a cavity has already reached the dentin inside
export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt } = L;
  L.upper.position.y = 40;
  setCavity(L, .5);
  sec.enamel.material.emissive.setRGB(0, 0, 0);
  sparkleAt(-.6, 3.0, .3, (t * .8) % 1, 1.6);
  const k = clamp(t / 2);
  cam.position.set(lerp(3.0, 2.6, k), lerp(5.4, 5.2, k), lerp(15.5, 14.5, k)); cam.lookAt(0.2, 4.5, 0);
  return [
    { text: 'ฟันผุซ่อนอยู่!', at: [-0.7, 3.1, 0.1], dx: -380, dy: 70 },
    { text: 'เคลือบฟัน', at: [1.4, 3.6, 0.05], dx: -60, dy: -120 },
    { text: 'โพรงประสาท', at: [0.3, 2.0, 0.05], dx: 90, dy: 30 },
  ];
}

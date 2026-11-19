// ep30 เสียวฟันหลังอุด ปกติไหม? — cut3d episode (L = tools/cut3d/lib.js); set copied from ep25 (tooth cut in half).
// New filling, still sensitive -> drilling irritates the pulp, cold = sharp zing -> desensitising toothpaste, soft brush,
// avoid very hot/cold, usually better in a few weeks -> pain on biting: filling a bit high -> articulating paper + trim =
// bite adjustment -> deep cavity: lingering / spontaneous throbbing -> pulp inflamed, exam + X-ray, some need a root canal ->
// rule: quick zing that fades = normal, lingering or spontaneous = see the dentist -> myth: sensitive = bad filling, redo?
// not always — the pulp is adjusting -> payoff: chewing comfortably.
let bump, bump3, mark3, paper, ct, sec = {}, cav, cav3, fil, fil3, spot, spot3, plaque, candy, drops = [], paste, iceCube, drill, scan, canalGerms = [], tipGlow, P;
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
  // high spot on the new filling (section + chewing surface), blue mark from the articulating paper, the paper itself
  bump = new THREE.Mesh(blobGeo(THREE, 3.1), fil.material); bump.position.set(-.85, 2.98, .03); ct.add(bump);
  bump3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), fil.material); bump3.position.set(-.85, 3.05, -.5); ct.add(bump3);
  mark3 = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), new THREE.MeshStandardMaterial({ color: '#2340d8', roughness: .6 })); mark3.position.set(-.85, 3.12, -.5); ct.add(mark3);
  paper = new THREE.Mesh(new THREE.BoxGeometry(5.5, .04, 2.6), new THREE.MeshStandardMaterial({ color: '#3b6cff', roughness: .7, side: THREE.DoubleSide })); scene.add(paper);
  L.SHOTS.biteC = [[2.2, 3.4, 15], [0, 2.0, 0]];
  fil.material.color.set('#4fa8ff');
  L.onReset(() => { [bump, bump3, mark3, paper].forEach(o => o.visible = false); paper.rotation.set(0, 0, 0); });
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

const FK = .3;                                     // normal filling depth (cavity stage)
function setBump(k) { bump.visible = bump3.visible = k > .01; bump.scale.set(.34 * k, .16 * k, 1); bump3.scale.set(.36 * k, .2 * k, .3 * k); }
function pulp(L, hot, glow) { sec.pulpMat.color.set(PULP.ok).lerp(new L.THREE.Color(PULP.hot), hot); sec.pulpMat.emissive.set('#ff2a2a'); sec.pulpMat.emissiveIntensity = glow; }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, setCam, chip, sparkleAt, warn, halo, brush } = L;
  let blur = 0, flash = 0, filter = '';
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const LB = 1150, LB2 = 1290, LB3 = 1430;
  cav.material.color.set('#4a2c16');
  const ice = (t0, t1) => { if (t > t0 && t < t1 + .4) { iceCube.visible = true; iceCube.position.set(-.6, lerp(9, 4.4, ein(seg(t, t0, t0 + .5))), -.4); iceCube.rotation.set(t * 2, t * 3, 0); iceCube.scale.setScalar(1 - seg(t, t1, t1 + .4)); } };
  const zap = (h, x = -.5, y = 2.6) => { if (t > h) { warn.material.opacity = .9 * Math.exp(-(t - h) * 1.4); warn.position.set(x, y, .6); warn.scale.setScalar(.7 + .05 * Math.sin(t * 20)); ct.position.x = t < h + .45 ? Math.sin(t * 50) * .04 : 0; } };
  const upperY = y => { L.upper.position.y = y; };

  if (t < be(0)) {                                   // hook: just got a filling... still sensitive -> bad filling?
    const a = bs(0), d = B[0].dur, zg = mk(0, 'zing', .35), ask = mk(0, 'ask', .65);
    upperY(lerp(11, 40, ease(seg(t, a, a + d * .5))));
    setFilling(L, 1, FK);
    if (t < zg) sparkleAt(-.8, 3.6, .3, seg(t, a + .3, a + 1.1), 1.8);
    ice(zg - .5, be(0) - .3); zap(zg); pulp(L, 0, t > zg ? .35 * Math.exp(-(t - zg) * 1.5) : 0);
    flash = hit(zg, .3);
    setCam('wide', 'secC', ease(seg(t, a + .1, a + d * .7)));
    chip('dn', '✓ เพิ่งอุดฟันเสร็จ', 'green', LB, t, a + .2, be(0) - .1);
    chip('zg', '🥶 แต่ยังเสียว…', 'red', LB2, t, zg, be(0) - .1, -2);
    chip('q', '= อุดไม่ดี ?', 'dark', LB3, t, ask, be(0) - .1, 2);
  } else if (t < be(1)) {                            // drilling irritates the pulp -> cold = sharp zing
    const a = bs(1), dr = mk(1, 'drill', .1), nv = mk(1, 'nerve', .35), cd = mk(1, 'cold', .7), zg = mk(1, 'zing', .82);
    upperY(40);
    const fl = nv - .2;
    if (t < fl) setCavity(L, FK); else setFilling(L, seg(t, fl, fl + .4), FK);
    if (t > a && t < fl + .3) { drill.visible = true; const kd = eout(seg(t, a, dr + .2)) * (1 - ein(seg(t, fl - .1, fl + .3)));
      drill.position.set(-.85 + Math.sin(t * 40) * .03, lerp(9, 3.2, kd), -.4); drill.userData.bur.rotation.y = t * 50; }
    const irr = seg(t, nv, nv + .4);
    pulp(L, .35 * irr, irr * (.15 + .12 * Math.sin(t * 10)) + (t > zg ? .5 * Math.exp(-(t - zg) * 2) : 0));
    ice(cd, be(1) - .2); zap(zg, -.2, 2.2);
    flash = Math.max(hit(zg, .3), whip(1) ? 0 : 0);
    blur = whip(1);
    setCam('secC', 'top', ease(seg(t, a, dr + .3)));
    if (t > fl) setCam('top', 'secC', ease(seg(t, fl, fl + .8)));
    chip('dr', '👩‍⚕️ กรอส่วนที่ผุออก', 'dark', LB, t, dr, nv - .05);
    chip('nv', 'ประสาทฟันระคายเคือง', 'yel', LB, t, nv, be(1) - .1);
    chip('zg1', '🧊 เจอเย็น เสียวแปล๊บ!', 'red', LB2, t, cd + .2, be(1) - .1, -3);
  } else if (t < be(2)) {                            // desensitising toothpaste, soft brush, avoid very hot/cold -> usually better in weeks
    const a = bs(2), d = B[2].dur, pa = mk(2, 'paste', .05), so = mk(2, 'soft', .3), av = mk(2, 'avoid', .45), wk = mk(2, 'weeks', .7);
    upperY(40); setFilling(L, 1, FK);
    brush.visible = t < av + .3; paste.visible = t < so + .8; paste.scale.setScalar(1 - seg(t, so, so + .8));
    brush.position.set(lerp(-7, 0, eout(seg(t, pa, pa + .5))) + (t > pa + .5 ? Math.sin(t * 9) * .7 : 0), 4.9, -.4); brush.rotation.set(Math.PI / 2, 0, 0);
    if (t > av - .1) brush.position.x += ein(seg(t, av - .1, av + .3)) * 12;
    pulp(L, .35 * (1 - seg(t, so, wk + 1)), .2 * (1 - seg(t, a, wk)));
    if (t > wk) { halo.material.opacity = .15 * eout(seg(t, wk, wk + .4)); halo.position.set(0, 2.2, .5); halo.scale.set(4, 4, 1); sparkleAt(0, 2.4, .3, ((t - wk) * 1.2) % 1, 2.2); }
    blur = whip(2);
    setCam('secC', 'top', ease(seg(t, a, pa + .5)));
    if (t > av) setCam('top', 'secW', ease(seg(t, av, wk)));
    chip('tp', '🪥 ยาสีฟันลดอาการเสียวฟัน', 'green', LB, t, pa + .1, av - .05);
    chip('sb', 'แปรงขนนุ่ม', 'dark', LB2, t, so, av - .05);
    chip('av', '🚫 ร้อนจัด / เย็นจัด', 'red', LB, t, av, be(2) - .1);
    chip('wk', '📅 ส่วนใหญ่ดีขึ้นในไม่กี่สัปดาห์', 'yel', LB2, t, wk, be(2) - .1, 2);
  } else if (t < be(3)) {                            // pain on biting -> the filling is a bit too high
    const a = bs(3), bi = mk(3, 'bite', .1), ou = mk(3, 'ouch', .25), hi = mk(3, 'high', .6);
    setFilling(L, 1, FK); setBump(back(seg(t, a, a + .5)));
    const bk = seg(t, bi - .3, ou);              // bite down, stopped by the high spot
    upperY(t < ou ? lerp(9, 3.62, ein(bk)) : lerp(3.62, 4.6, eout(seg(t, ou + .1, ou + .5))));
    if (t > ou + 1.3) upperY(lerp(4.6, 3.62, ein(seg(t, ou + 1.3, ou + 1.6))));
    if (t > ou + 1.7) upperY(lerp(3.62, 5, eout(seg(t, ou + 1.7, ou + 2.1))));
    zap(ou, -.7, 3.4); pulp(L, .2, t > ou ? .35 * Math.exp(-(t - ou) * 2) : 0);
    if (t > hi) { halo.material.opacity = .5 * eout(seg(t, hi, hi + .3)); halo.position.set(-.85, 3.9, -.2); halo.scale.set(2.6, 2.6, 1); }
    flash = Math.max(hit(ou, .3), t < a + .3 ? .4 * (1 - seg(t, a, a + .3)) : 0);
    setCam('secC', 'biteC', ease(seg(t, a, bi)), t > ou && t < ou + .4 ? .08 : 0, t);
    chip('rw', '⏩ แต่ถ้ากัดทีไร…', 'yel', 190, t, a + .1, ou);
    chip('ou', '😣 เจ็บจี๊ดทุกที', 'red', LB, t, ou, be(3) - .1, -3);
    chip('hi', '⬆ ที่อุดสูงเกินไปนิด', 'dark', LB2, t, hi, be(3) - .1);
  } else if (t < be(4)) {                            // articulating paper -> blue mark -> trim = bite adjustment
    const a = bs(4), pp = mk(4, 'paper', .15), tr = mk(4, 'trim', .45), tm = mk(4, 'term', .75);
    setFilling(L, 1, FK);
    setBump(1 - ease(seg(t, tr + .2, tr + 1.1)));
    if (t > pp - .4 && t < tr) { paper.visible = true; paper.position.set(lerp(-9, 0, eout(seg(t, pp - .4, pp + .1))), 3.78, -.3); if (t > pp + .9) paper.position.x = lerp(0, 9, ein(seg(t, pp + .9, pp + 1.3))); }
    let uy = 5;
    if (t > pp + .1 && t < pp + 1) uy = lerp(5, 3.66, Math.sin(seg(t, pp + .1, pp + .9) * Math.PI));
    if (t > tm - .5) uy = lerp(5, 3.3, eout(seg(t, tm - .5, tm)));
    if (t > tm + 1) uy = lerp(3.3, 5, seg(t, tm + 1, tm + 1.4));
    upperY(uy);
    mark3.visible = t > pp + .5 && t < tr + 1.1; mark3.scale.set(.2 * (1 - seg(t, tr + .2, tr + 1.1)), .05, .16 * (1 - seg(t, tr + .2, tr + 1.1)));
    if (t > tr - .3 && t < tr + 1.3) { drill.visible = true; const kd = eout(seg(t, tr - .3, tr + .1)) * (1 - ein(seg(t, tr + 1, tr + 1.3)));
      drill.position.set(-.85 + Math.sin(t * 40) * .03, lerp(9, 3.45, kd), -.45); drill.userData.bur.rotation.y = t * 50; }
    if (t > tm) sparkleAt(-.6, 3.7, .3, seg(t, tm, tm + .8), 1.8);
    blur = whip(4);
    setCam('biteC', 'top', ease(seg(t, a, pp)));
    if (t > tm - .6) setCam('top', 'biteC', ease(seg(t, tm - .6, tm)));
    chip('pa', '🟦 เช็กด้วยกระดาษกัด', 'dark', LB, t, pp, tr - .05);
    chip('tr', '👩‍⚕️ กรอแต่งให้พอดี', 'dark', LB, t, tr, be(4) - .1);
    chip('tm4', 'การปรับการสบฟัน ✓', 'green', LB2, t, tm, be(4) - .1, 2);
  } else if (t < be(5)) {                            // deep cavity: lingering sensitivity or spontaneous throbbing
    const a = bs(5), dp = mk(5, 'deep', .1), lg = mk(5, 'linger', .3), th = mk(5, 'throb', .65);
    upperY(lerp(5, 40, ease(seg(t, a, a + .6))));
    const k = lerp(FK, .92, ease(seg(t, dp, dp + .9)));
    setFilling(L, 1, k);
    const hot = seg(t, lg, th);
    pulp(L, hot, hot * .3 + (t > th ? .25 * (.5 + .5 * Math.sin((t - th) * 12)) : 0));
    if (t > lg - .4 && t < th) { iceCube.visible = true; iceCube.position.set(-.6, lerp(9, 4.4, ein(seg(t, lg - .4, lg + .1))), -.4); iceCube.scale.setScalar(1 - seg(t, lg + .9, th)); }
    if (t > lg) { warn.material.opacity = .7; warn.position.set(0, 2.0, .6); warn.scale.setScalar(.75 + .05 * Math.sin(t * 6)); }
    if (t > th) { warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - th) * 12)); warn.scale.setScalar(.8 + .08 * Math.sin(t * 12)); }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(th, .25));
    setCam('biteC', 'secW', ease(seg(t, a, dp + .8)), t > th ? .05 : 0, t);
    chip('rw5', '⏩ ถ้าผุลึกมาก…', 'yel', 190, t, a + .1, be(5) - .1);
    chip('lg', '⏳ เสียวค้างนาน', 'red', LB, t, lg, be(5) - .1);
    chip('th', '⚡ ปวดตุ๊บๆ เอง', 'dark', LB2, t, th, be(5) - .1, -3);
  } else if (t < be(6)) {                            // pulp inflamed -> exam + X-ray -> some need a root canal
    const a = bs(6), pu = mk(6, 'pulp', .1), xr = mk(6, 'xray', .3), rc = mk(6, 'rc', .75);
    upperY(40); setFilling(L, 1, .92);
    pulp(L, 1, .25 + .2 * Math.sin(t * 10));
    if (t > xr && t < rc - .2) { filter = 'grayscale(1) invert(1) contrast(1.25)'; scan.visible = true; scan.position.set(0, lerp(5, -5.5, seg(t, xr, rc - .4)), .3); }
    if (t > rc) { tipGlow.visible = false; halo.material.opacity = .2 * eout(seg(t, rc, rc + .4)); halo.position.set(0, -1.5, .6); halo.scale.set(4, 8, 1); sparkleAt(0, -1.6, .3, seg(t, rc, rc + .8), 2.6); }
    flash = Math.max(hit(xr, .5), t < a + .3 ? .4 * (1 - seg(t, a, a + .3)) : 0);
    blur = whip(6);
    setCam('secW', 'secW', 0);
    chip('pu', '🔥 ประสาทฟันอักเสบ', 'red', 190, t, pu, be(6) - .1);
    chip('xr', '🩻 ตรวจ + เอกซเรย์', 'dark', LB, t, xr, be(6) - .1);
    chip('rc6', 'บางรายอาจต้องรักษารากฟัน', 'red', LB2, t, rc, be(6) - .1, 2);
  } else if (t < be(7)) {                            // the rule: quick zing that fades = normal; lingering / spontaneous = see the dentist
    const a = bs(7), ok = mk(7, 'ok', .1), bd = mk(7, 'bad', .45), go = mk(7, 'go', .75);
    upperY(40); setFilling(L, 1, t < bd ? FK : .92);
    ice(ok - .3, ok + 1.0);
    if (t < bd) { zap(ok + .2, -.2, 2.2); pulp(L, 0, t > ok + .2 ? .45 * Math.exp(-(t - ok - .2) * 2.5) : 0); }
    else { pulp(L, seg(t, bd, bd + .5), .25 + .2 * Math.sin(t * 10)); warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - bd) * 10)); warn.position.set(0, 2.0, .6); warn.scale.setScalar(.8); }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(bd, .3));
    setCam('secC', 'secW', ease(seg(t, bd - .3, bd + .5)));
    chip('h7', '📌 จำง่ายๆ', 'yel', 190, t, a + .1, be(7) - .1);
    chip('ok7', '✓ เสียวแปล๊บแล้วหาย = ปกติ', 'green', LB, t, ok + .2, be(7) - .1);
    chip('bd7', '⚠ เสียวค้าง / ปวดเอง', 'red', LB2, t, bd, be(7) - .1, -2);
    chip('go7', '🏃 รีบไปหาหมอนะคะ', 'dark', LB3, t, go, be(7) - .1, 2);
  } else if (t < be(8)) {                            // myth: sensitive = bad filling, redo? not always — the pulp is adjusting
    const a = bs(8), my = mk(8, 'myth', .1), no = mk(8, 'no', .45), ad = mk(8, 'adapt', .65);
    upperY(40); setFilling(L, 1, FK);
    if (t > my && t < no) { warn.material.opacity = .6 + .3 * Math.sin(t * 10); warn.position.set(-.7, 3.3, .6); warn.scale.setScalar(.55); }
    pulp(L, 0, 0);
    if (t > ad) { halo.material.opacity = .18 * eout(seg(t, ad, ad + .5)); halo.position.set(0, 2.2, .5); halo.scale.set(3.5, 3.5, 1); sparkleAt(0, 2.3, .3, ((t - ad) * 1.1) % 1, 1.6); }
    flash = hit(no, .3);
    blur = whip(8);
    setCam('secW', 'secC', ease(seg(t, a, my + 1)));
    chip('m1', 'เสียว = อุดไม่ดี ต้องรื้อ?', 'dark', LB, t, my + .2, no - .05);
    chip('m2', '✕ ไม่ใช่เสมอไปนะ!', 'red', LB, t, no, be(8) - .1, -4);
    chip('m3', '🌱 ประสาทฟันกำลังปรับตัว', 'green', LB2, t, ad, be(8) - .1);
  } else if (t < be(9)) {                            // payoff: no more zing, chewing comfortably
    const a = bs(9), d = B[9].dur, ch = mk(9, 'chew', .35);
    setFilling(L, 1, FK);
    let uy = lerp(40, 11, eout(seg(t, a, a + .8)));
    if (t > ch) uy = lerp(11, 3.6, .5 - .5 * Math.cos(seg(t, ch, ch + 1.6) * Math.PI * 4));
    upperY(uy);
    L.confetti(t, a); sparkleAt(0, 4, 1, seg(t, a, a + .9), 3);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, 3, -1);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('secC', 'gap', ease(seg(t, a, a + d * .6)));
    chip('y1', '🎉 หายเสียว', 'green', 190, t, a + .3, be(9) - .1);
    chip('y2', '😋 เคี้ยวได้สบาย', 'dark', 330, t, ch, be(9) - .1);
  } else {                                           // under the end card
    setFilling(L, 1, FK); upperY(11); setCam('gap', 'gap', 0);
  }
  return { blur, flash, filter };
}

// cover: the filled tooth cut in half, an ice cube coming down, a red zing ring
export function cover(t, L) {
  const { lerp, clamp, cam, warn } = L;
  L.upper.position.y = 40;
  setFilling(L, 1, .45);
  pulp(L, .4, .25);
  warn.material.opacity = .85; warn.position.set(-.2, 2.3, .6); warn.scale.setScalar(.8 + .04 * Math.sin(t * 12));
  const k = clamp(t / 2);
  cam.position.set(lerp(3.0, 2.6, k), lerp(5.4, 5.2, k), lerp(15.5, 14.5, k)); cam.lookAt(0.2, 4.5, 0);
  return [
    { text: 'ที่อุดฟัน', at: [-0.7, 3.1, 0.1], dx: -330, dy: 60 },
    { text: 'โพรงประสาท', at: [0.3, 2.0, 0.05], dx: 90, dy: 30 },
    { text: '⚡ เสียว!', at: [0.6, 3.0, 0.05], dx: 80, dy: -60 },
  ];
}

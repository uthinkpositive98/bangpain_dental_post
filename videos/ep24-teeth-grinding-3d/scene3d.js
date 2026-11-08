// ep24 นอนกัดฟัน เรื่องเล็กจริงไหม? — cut3d episode (L = tools/cut3d/lib.js)
// Night grinding: the upper jaw grinds side to side -> enamel wears flat (dentin shows) -> cold sensitivity ->
// jaw muscle works all night (masseter glows) -> crack + a filling pops off -> night guard (occlusal splint) wears instead ->
// guard protects but does not cure: less stress / caffeine -> clean the guard every morning (germs brushed off) ->
// myth: "grinding = worms" (a cute worm poofs) -> payoff.
let CP, lowEn, caps = [], crack, crackGlow, fill, hole, guard, scratches = [], muscle, muscMat, cup, worm, drop;
const TIP = 3.92, H0 = 4.1, H1 = 3.25;                    // lower cusp tips (world y); clip height: none -> fully worn
const clamp01 = k => Math.min(1, Math.max(0, k));

function crackTube(L, grp, xf, top, bot, r, mat, n = 120) {
  const { THREE } = L; grp.updateMatrixWorld(true);
  const rc = new THREE.Raycaster(), pts = [];
  for (let i = 0; i <= n; i++) {
    const y = L.lerp(top, bot, i / n), x = grp.position.x + xf(y);
    rc.set(new THREE.Vector3(x, y, 9), new THREE.Vector3(0, 0, -1));
    const h = rc.intersectObjects(grp.children.filter(c => c.isMesh), false)[0];
    if (h) { const p = h.point.clone(); p.z += .035; pts.push(grp.worldToLocal(p)); }
  }
  const segs = 200, rad = 6;
  const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), segs, r, rad, false), mat); grp.add(m); m.userData.seg = segs * rad * 6; return m;
}
const reveal = (m, k) => { m.visible = k > 0.002; m.geometry.setDrawRange(0, Math.floor(clamp01(k) * m.userData.seg / 36) * 36); };

export function setup(L) {
  const { THREE, scene, RoundedBoxGeometry, canvasTex, rnd, SP } = L;
  L.renderer.localClippingEnabled = true;
  CP = new THREE.Plane(new THREE.Vector3(0, -1, 0), 99);      // keeps y <= constant (wear)
  lowEn = L.enamel.clone(); lowEn.clippingPlanes = [CP]; lowEn.clipShadows = true;
  const lower = [...L.neighbors, L.centerTooth];
  const capMat = new THREE.MeshStandardMaterial({ color: '#f0cf8c', roughness: .5, side: THREE.DoubleSide, emissive: '#5a3a00', emissiveIntensity: .08 });
  lower.forEach(g => { g.children[0].material = lowEn;
    const c = new THREE.Mesh(new THREE.CircleGeometry(1, 40), capMat); c.rotation.x = -Math.PI / 2; g.add(c); caps.push(c); });
  // crack on the x=0 crown
  const ct = L.centerTooth;
  const xf = y => .25 + .18 * Math.sin(y * 4.3) + .05 * Math.sin(y * 13);
  crack = crackTube(L, ct, xf, 3.2, 1.0, .055, new THREE.MeshStandardMaterial({ color: '#3b2a22', roughness: .7 }));
  crackGlow = crackTube(L, ct, xf, 3.2, 1.0, .16, new THREE.MeshBasicMaterial({ color: '#ff3b47', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  // a filling on the right neighbour + the hole it leaves
  fill = new THREE.Mesh(new THREE.SphereGeometry(1, 28, 14), new THREE.MeshPhysicalMaterial({ color: '#9fd0ff', roughness: .25, clearcoat: 1 })); fill.castShadow = true; scene.add(fill);
  hole = new THREE.Mesh(new THREE.CircleGeometry(.62, 32), new THREE.MeshStandardMaterial({ color: '#5a3a22', roughness: .8 })); hole.rotation.x = -Math.PI / 2; scene.add(hole);
  // night guard (occlusal splint): clear blue shell over the lower crowns, with wear scratches on top
  guard = new THREE.Group(); scene.add(guard);
  { const m = new THREE.Mesh(new RoundedBoxGeometry(26.5, 1.4, 4.0, 4, .5), new THREE.MeshPhysicalMaterial({ color: '#8fd8ff', roughness: .1, clearcoat: 1, transparent: true, opacity: .55, depthWrite: false })); guard.add(m);
    const sm = new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, opacity: .85 });
    for (let i = 0; i < 14; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(1, .03, .07), sm); s.position.set((i - 6.5) * 1.8 + rnd() * .6, .72, (rnd() - .5) * 2.4); s.rotation.y = (rnd() - .5) * .5; guard.add(s); scratches.push(s); } }
  // jaw muscle (masseter) on the left, between the jaws
  const stripes = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#e8707f'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(150,30,50,.45)'; g.lineWidth = 3; for (let x = 4; x < w; x += 12) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } });
  muscMat = new THREE.MeshPhysicalMaterial({ map: stripes, color: '#ffffff', roughness: .45, clearcoat: .5, emissive: '#000000' });
  { const pts = []; for (let i = 0; i <= 20; i++) { const k = i / 20; pts.push(new THREE.Vector2(.35 + 1.55 * Math.sin(k * Math.PI), (k - .5) * 9.5)); }
    muscle = new THREE.Mesh(new THREE.LatheGeometry(pts, 40), muscMat); muscle.castShadow = true; muscle.position.set(-16.2, 2.3, 1.2); muscle.rotation.z = -.12; scene.add(muscle); }
  // coffee cup
  cup = new THREE.Group(); scene.add(cup);
  { const w = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .25, clearcoat: 1 });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(1.1, .85, 2, 32), w); cup.add(body);
    const cof = new THREE.Mesh(new THREE.CircleGeometry(1.0, 32), new THREE.MeshStandardMaterial({ color: '#6b3e1f', roughness: .4 })); cof.rotation.x = -Math.PI / 2; cof.position.y = .9; cup.add(cof);
    const hd = new THREE.Mesh(new THREE.TorusGeometry(.5, .14, 12, 24), w); hd.position.set(1.15, .05, 0); cup.add(hd); }
  // a cute worm (myth beat)
  worm = new THREE.Group(); scene.add(worm);
  { const wm = new THREE.MeshPhysicalMaterial({ color: '#f2a7c3', roughness: .35, clearcoat: .6 });
    for (let i = 0; i < 6; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(i === 5 ? .62 : .5 - i * .02, 20, 14), wm); s.userData.i = i; worm.add(s); }
    const em = new THREE.MeshBasicMaterial({ color: '#16324F' });
    [-.22, .22].forEach(dx => { const e = new THREE.Mesh(new THREE.SphereGeometry(.1, 10, 8), em); e.position.set(dx, .15, .55); worm.children[5].add(e); }); }
  drop = new THREE.Mesh(new THREE.SphereGeometry(.45, 24, 16), new THREE.MeshPhysicalMaterial({ color: '#7fd3ff', roughness: .05, clearcoat: 1, transparent: true, opacity: .85 })); scene.add(drop);
  Object.assign(L.SHOTS, {
    worn: [[2.6, 8.6, 13], [0, 3.0, 0]],          // looking down on the worn chewing surfaces
    musc: [[-10.5, 4.5, 23], [-14.2, 2.6, 0]],       // the jaw muscle + left teeth
    gd: [[3, 10.5, 21], [0, 7.2, 0]],             // the lifted guard
    side: [[-9.5, 6.5, 27], [-12.4, 3.2, 0]],         // cover: bite + muscle
  });
  L.onReset(() => {
    CP.constant = 99; caps.forEach(c => c.visible = false);
    reveal(crack, 0); reveal(crackGlow, 0); crackGlow.material.opacity = 0;
    [fill, hole, guard, cup, worm, drop].forEach(o => o.visible = false);
    fill.position.set(SP, 3.9, .1); fill.scale.set(.75, .2, .55); fill.rotation.set(0, 0, 0);
    guard.position.set(0, 3.2, 0); guard.rotation.set(0, 0, 0); scratches.forEach(s => s.scale.x = .001);
    muscle.scale.set(1, 1, 1); muscMat.emissive.set('#000000');
    upper.position.x = 0; L.warn.scale.setScalar(1); L.warn.position.set(0, 1.5, .6);
  });
  upper = L.upper;
}
let upper;

// wear w: 0 = intact, 1 = flat; returns the clip height
function wear(L, w) {
  const h = L.lerp(H0, H1, w); CP.constant = h;
  const loc = h - .7;                                   // tooth-local height of the cut
  const r = loc > 2.8 ? L.lerp(1.45, 1.0, (loc - 2.8) / .2) : L.lerp(1.68, 1.45, (loc - 2.35) / .45);
  caps.forEach(c => { c.visible = w > .3; c.position.set(0, loc - .005, 0); c.scale.set(r * .93, r * .8, 1); });
  if (fill.visible) fill.position.y = Math.min(3.9, h + .02);
  return h;
}
const biteY = (h, onGuard = false) => 3.4 - Math.max(0, TIP - h) * .9 + (onGuard ? .75 : 0);
function grind(t, amp, speed = 9) { upper.position.x = Math.sin(t * speed) * amp; }
function wormPose(L, t, x, y, z, s) { worm.visible = s > .01; worm.position.set(x, y, z); worm.scale.setScalar(s);
  worm.children.forEach((b, i) => { if (!b.isMesh) return; b.position.set((i - 2.5) * .62, Math.sin(t * 6 - i * .9) * .28 + (i === 5 ? .2 : 0), 0); }); }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, warn, halo, SP, germs, brush } = L;
  let blur = 0, flash = 0;
  const wb = a => t < a + .35 ? (1 - seg(t, a, a + .35)) * 13 : 0;
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const crackT = mk(4, 'crack', .3), popT = mk(4, 'pop', .75), fixT = mk(5, 'so', .05), guardT = mk(5, 'guard', .35);
  // persistent state: wear, filling, crack
  const w = t < bs(1) ? 0 : t < bs(2) ? .15 * seg(t, bs(1), be(1)) : .15 + .85 * ease(seg(t, mk(2, 'wear', .1), mk(2, 'zing', .7)));
  const h = wear(L, w);
  const filled = t < popT || t > fixT + .3;
  fill.visible = filled; if (filled) fill.position.y = h + .02;
  hole.visible = !filled && t > popT + .6; hole.position.set(SP, h + .01, .1);
  const ck = t > crackT ? (t < fixT ? eout(seg(t, crackT, crackT + .7)) : 1) : 0; reveal(crack, ck); reveal(crackGlow, ck);
  if (t > fixT) crack.visible = crackGlow.visible = t < fixT + .8 && Math.floor(t * 12) % 2 === 0; // fades out (fixed by the dentist)
  const guardOn = t > guardT;
  if (guardOn) { guard.visible = true; guard.position.set(0, h - .15, 0); }
  const scr = k => scratches.forEach((s, i) => s.scale.x = clamp(k * 1.4 - i * .03) * 1.6 + .001);

  if (t < be(0)) {                                   // hook: grinding all night — just noise?
    const a = bs(0), d = B[0].dur, cl = eout(seg(t, a + .1, a + .6));
    upper.position.y = lerp(11, biteY(h), cl); grind(t, .32 * cl, 10);
    blur = 0;
    setCam('wide', 'bite', ease(seg(t, a + .1, a + d * .8)), cl > .9 ? .03 : 0, t);
    chip('zz', '🌙 หลับอยู่… Zzz', 'dark', 190, t, a + .1, mk(0, 'noise', .4) - .05);
    chip('grr', 'กรอดๆ! 🔊', 'yel', 190, t, mk(0, 'noise', .4), be(0) - .1, -4);
    chip('small', 'เรื่องเล็กน่า?', 'dark', 320, t, mk(0, 'small', .7), be(0) - .1);
  } else if (t < be(1)) {                            // grinding back and forth, force > chewing
    const a = bs(1), d = B[1].dur, gt = mk(1, 'grind', .35), ft = mk(1, 'force', .65);
    upper.position.y = biteY(h); grind(t, t > gt ? .5 : .3, t > gt ? 13 : 9);
    if (t > ft) { sparkleAt(Math.sin(t * 13) * 1.5, 3.7, .6, (t * 2.5) % 1, 2); }
    warn.material.opacity = t > ft ? .7 * (.5 + .5 * Math.sin(t * 12)) : 0; warn.position.set(0, 3.6, 1.2); warn.scale.setScalar(1.3);
    flash = hit(ft, .2);
    blur = wb(a);
    setCam('bite', 'neck', ease(seg(t, a, a + d)), t > ft ? .06 : .02, t);
    chip('grind', '↔ บดไปมาทั้งคืน', 'dark', 190, t, gt, be(1) - .1);
    chip('force', '💪 แรงกว่าตอนเคี้ยวข้าว', 'red', 320, t, ft, be(1) - .1, -2);
  } else if (t < be(2)) {                            // enamel wears flat, dentin shows -> sensitive to cold
    const a = bs(2), d = B[2].dur, zt = mk(2, 'zing', .7);
    const op = eout(seg(t, a, a + .5)); upper.position.y = lerp(biteY(h), 11, op); grind(t, .4 * (1 - op), 12);
    if (t > zt - .5) { drop.visible = t < zt + .1; drop.position.set(0, lerp(8, h + .4, ein(seg(t, zt - .5, zt))), .2); }
    warn.material.opacity = t > zt ? .9 * Math.exp(-(t - zt) * 1.2) : 0; warn.position.set(0, h + .3, .9); warn.scale.setScalar(1.05 + .08 * Math.sin(t * 20));
    L.centerTooth.position.x = t > zt && t < zt + .5 ? Math.sin(t * 50) * .04 : 0;
    flash = hit(zt, .3);
    blur = wb(a);
    setCam('neck', 'worn', ease(seg(t, a, a + d * .5)), t > zt && t < zt + .4 ? .1 : 0, t);
    chip('wear', 'ฟันสึก ยอดฟันแบนราบ', 'dark', 190, t, mk(2, 'flat', .35), be(2) - .1);
    chip('dent', 'เนื้อฟันโผล่ 🟡', 'yel', 320, t, mk(2, 'flat', .35) + .6, be(2) - .1);
    chip('zing', '🥶 เสียวฟัน!', 'red', 450, t, zt, be(2) - .1, -3);
  } else if (t < be(3)) {                            // the jaw muscle works all night -> sore jaw, headache
    const a = bs(3), d = B[3].dur, mt = mk(3, 'muscle', .2), wk = mk(3, 'wake', .6);
    upper.position.y = lerp(11, biteY(h), eout(seg(t, a, a + .5))); grind(t, .4, 11);
    const pump = .5 + .5 * Math.sin(t * 11);
    muscle.scale.set(1 + .18 * pump, 1 - .04 * pump, 1 + .18 * pump);
    const tired = seg(t, mt, wk); muscMat.emissive.setRGB(.45 * tired * (.6 + .4 * pump), 0, .05 * tired);
    warn.material.opacity = t > wk ? .85 * pump : 0; warn.position.set(-16.2, 4.5, 3.4); warn.scale.setScalar(1.25);
    blur = wb(a);
    setCam('bite', 'musc', ease(seg(t, a, mt + .4)));
    chip('mus', 'กล้ามเนื้อบดเคี้ยว', 'dark', 190, t, mt, be(3) - .1);
    chip('sore', '😣 ตื่นมาเมื่อยกราม', 'red', 320, t, wk, be(3) - .1, -2);
    chip('head', '⚡ ปวดขมับ', 'yel', 450, t, mk(3, 'head', .8), be(3) - .1, 3);
  } else if (t < be(4)) {                            // a crack, and a filling pops off
    const a = bs(4), d = B[4].dur;
    upper.position.y = lerp(biteY(h), 11, eout(seg(t, a, a + .5))); grind(t, .3 * (1 - seg(t, a, a + .5)), 11);
    crackGlow.material.opacity = t > crackT ? .5 + .3 * Math.sin(t * 10) : 0;
    if (t > popT && t < popT + 1.2) { fill.visible = true; const tt = t - popT; fill.position.set(SP + tt * 3.5, h + .2 + tt * 7 - 7 * tt * tt, .1 + tt * 2); fill.rotation.set(tt * 8, tt * 5, 0); }
    if (t > popT && t > crackT) { warn.material.opacity = .85 * Math.exp(-(t - popT) * 1.2); warn.position.set(SP, h + .3, .9); warn.scale.setScalar(1.1); }
    else { warn.material.opacity = t > crackT ? .8 * Math.exp(-(t - crackT) * 1.5) : 0; warn.position.set(0, 2.6, 1.2); warn.scale.setScalar(1.1); }
    flash = Math.max(hit(crackT, .3), hit(popT, .3));
    blur = wb(a);
    setCam('neck', 'gap', ease(seg(t, popT - .6, popT + .3)), (t > crackT && t < crackT + .3) || (t > popT && t < popT + .3) ? .12 : 0, t);
    chip('crack', '⚠ ฟันร้าว / บิ่น', 'red', 190, t, crackT + .1, be(4) - .1, -3);
    chip('pop', 'ที่อุดหลุด!', 'red', 320, t, popT, be(4) - .1, 3);
  } else if (t < be(5)) {                            // the dentist makes a night guard — it wears instead of the teeth
    const a = bs(5), d = B[5].dur, it = mk(5, 'inst', .75);
    if (t > fixT && t < fixT + .9) sparkleAt(SP, h + .4, .6, seg(t, fixT, fixT + .9), 2);
    if (guardOn) { const k = seg(t, guardT, guardT + .6); guard.position.y = lerp(10, h - .15, eout(k)); if (k >= 1) sparkleAt(0, h + 1, 1.8, seg(t, guardT + .6, guardT + 1.3), 5); }
    const cl = eout(seg(t, guardT + .7, guardT + 1.2)); upper.position.y = lerp(11, biteY(h, true), cl); if (t > guardT + 1) grind(t, .4, 11);
    if (t > it) scr(seg(t, it, be(5)));
    flash = hit(guardT + .6, .25);
    blur = wb(a);
    setCam('gap', 'bite', ease(seg(t, guardT + .5, guardT + 1.5)));
    chip('doc', '👩‍⚕️ คุณหมอพิมพ์ปาก', 'dark', 190, t, fixT + .1, guardT + .5);
    chip('term', 'เฝือกสบฟัน (Night Guard)', 'green', 190, t, guardT + .5, be(5) - .1);
    chip('inst', '✓ สึกที่เฝือก แทนฟัน', 'dark', 320, t, it, be(5) - .1);
  } else if (t < be(6)) {                            // protects, does not cure -> less stress, avoid coffee before bed
    const a = bs(6), d = B[6].dur, so = mk(6, 'so', .45), cf = mk(6, 'coffee', .65);
    scr(1); upper.position.y = biteY(h, true); grind(t, t < so ? .4 : .4 * (1 - .6 * seg(t, so, be(6))), 10);
    if (t > so - .2) { cup.visible = true; const k = eout(seg(t, so - .2, so + .4)); const out = ein(seg(t, cf + .5, cf + 1.1));
      cup.position.set(3.2, lerp(14, 7.6, k) + .2 * Math.sin(t * 3) + out * 3, 2); cup.rotation.set(.25, t * .8 + out * 6, .15); cup.scale.setScalar(1 - out); }
    if (t > cf + .5) sparkleAt(3.2, 8, 2, seg(t, cf + .5, cf + 1.2), 2);
    blur = wb(a);
    setCam('bite', 'high', ease(seg(t, so - .3, so + .6)));
    chip('not', 'ปกป้องฟัน ≠ หายกัด', 'red', 190, t, mk(6, 'not', .2), so - .05);
    chip('calm', '🧘 ลดความเครียด', 'green', 190, t, so, be(6) - .1);
    chip('cof', '☕ เลี่ยงกาแฟก่อนนอน', 'green', 320, t, cf, be(6) - .1);
  } else if (t < be(7)) {                            // germs can live on the guard -> brush it every morning
    const a = bs(7), d = B[7].dur, gm = mk(7, 'germ', .2), br = mk(7, 'brush', .6);
    scr(1); upper.position.y = lerp(biteY(h, true), 11, eout(seg(t, a, a + .5)));
    const lift = eout(seg(t, a + .2, a + .9)); guard.position.set(0, lerp(h - .15, 7, lift), lerp(0, 1.5, lift)); guard.rotation.x = .25 * lift;
    const gy = guard.position.y + .9;
    germs.slice(0, 14).forEach((g, j) => { const x0 = (j - 6.5) * 1.7, k = eout(seg(t, gm + j * .04, gm + .6 + j * .04));
      const bx = lerp(-14, 14, seg(t, br, br + 1.6)); const gone = t > br && bx > x0 ? 1 - eout(seg(t, br + (x0 + 14) / 28 * 1.6, br + (x0 + 14) / 28 * 1.6 + .2)) : 1;
      g.visible = k > 0 && gone > 0; g.position.set(x0, lerp(gy + 6, gy + .1 * Math.sin(t * 6 + j), k), guard.position.z + (j % 3 - 1) * .8); g.scale.setScalar(1.6 * gone); g.rotation.set(t * 2 + j, t, 0); });
    if (t > br - .3) { brush.visible = t < br + 2; brush.position.set(lerp(-14, 14, seg(t, br, br + 1.6)), gy + .9, guard.position.z + 2.3); brush.rotation.set(-1.2, 0, 0); }
    if (t > br + 1.6) sparkleAt(0, gy, guard.position.z + 1, seg(t, br + 1.6, br + 2.3), 5);
    blur = wb(a);
    setCam('bite', 'gd', ease(seg(t, a, a + .9)));
    chip('germ', '🦠 เชื้อโรคเกาะเฝือก', 'red', 190, t, gm, br - .05, -2);
    chip('wash', '🪥 ล้างทุกเช้า', 'green', 190, t, br - .1, be(7) - .1);
    chip('soft', 'แปรงขนนุ่ม + น้ำเปล่า', 'dark', 320, t, br + .3, be(7) - .1);
  } else if (t < be(8)) {                            // myth: grinding is caused by worms? no — stress and sleep
    const a = bs(8), d = B[8].dur, wt = mk(8, 'worm', .3), no = mk(8, 'no', .5), rl = mk(8, 'real', .7);
    scr(1); const back0 = eout(seg(t, a, a + .6)); guard.position.set(0, lerp(7, h - .15, back0), lerp(1.5, 0, back0)); guard.rotation.x = .25 * (1 - back0);
    const s = t < no ? back(seg(t, a + .2, a + .7)) : 1 - ein(seg(t, no, no + .3));
    wormPose(L, t, 0, 6.4, 3.5, s * 1.2);
    if (t > no) sparkleAt(0, 6.4, 3.5, seg(t, no, no + .7), 2.5);
    flash = hit(no, .25);
    blur = wb(a);
    setCam('high', 'gap', ease(seg(t, a, a + .8)));
    chip('m1', 'นอนกัดฟัน เพราะมีพยาธิ?', 'dark', 190, t, a + .3, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', 190, t, no, be(8) - .1, -4);
    chip('m3', '😣 ความเครียด + 😴 การนอน', 'yel', 320, t, rl, be(8) - .1);
  } else if (t < be(9)) {                            // payoff: teeth have armour, wake up with a relaxed jaw
    const a = bs(9), d = B[9].dur;
    scr(1); upper.position.y = lerp(11, biteY(h, true), eout(seg(t, a + .3, a + 1)));
    L.confetti(t, a); sparkleAt(0, h + 1, 1.8, seg(t, a, a + .9), 6);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, h + .5, -2);
    muscle.scale.set(.95, 1, .95);
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
    chip('arm', '🛡 ฟันมีเกราะป้องกัน', 'green', 190, t, mk(9, 'armor', .3), be(9) - .1);
    chip('ok', '😊 ตื่นมาสบายกราม', 'dark', 320, t, mk(9, 'wake', .6), be(9) - .1);
  } else {                                           // under the end card
    scr(1); upper.position.y = biteY(h, true); setCam('wide', 'wide', 0);
  }
  return { blur, flash };
}

// cover: jaws closed and grinding, worn yellow tops on the right, glowing jaw muscle on the left
export function cover(t, L) {
  const { warn, sparkleAt } = L;
  const h = wear(L, .7);
  upper.position.y = biteY(h) + 3.2; grind(t, .45, 10);
  muscle.scale.set(1.12, 1, 1.12); muscMat.emissive.setRGB(.35 + .1 * Math.sin(t * 9), 0, .03);
  sparkleAt(-7.5, 3.6, .8, (t * 1.6) % 1, 2.4);
  warn.material.opacity = .7 * (.5 + .5 * Math.sin(t * 10)); warn.position.set(-16.2, 4.5, 3.4); warn.scale.setScalar(1.3);
  L.setCam('side', 'side', 0);
  return [
    { text: 'ฟันสึก', at: [-7.5, 3.3, 1.4], dx: -230, dy: 90 },
    { text: 'กล้ามเนื้อกราม', at: [-15.5, -1.5, 2.6], dx: 40, dy: 40 },
  ];
}
const SPx = L => L.SP;

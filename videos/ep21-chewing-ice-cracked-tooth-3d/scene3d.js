// ep21 เคี้ยวน้ำแข็ง ฟันร้าวได้ไหม? — cut3d episode (L = tools/cut3d/lib.js)
// Ice crunch -> a hairline crack on the x=0 molar -> "zing" on release (cracked tooth) -> the crack does not heal and grows ->
// X-ray look: crack reaches the pulp, pulp inflamed -> root canal -> crown holds the tooth together ->
// what-if on the right neighbour: the tooth splits in two -> prevention (no ice, no hard objects, night guard) ->
// myth: a crack may be too small to see (magnifier) -> payoff.
let ice, shards = [], crack, crackGlow, ctEn, ctRoot, pulpCh, canalMat, chMat, halves = [], planes = [], guard, mag, hair, crownMat;
const CRACK_TOP = 3.55, CRACK_BOT = -4.6;
const crackK = y => (CRACK_TOP - y) / (CRACK_TOP - CRACK_BOT);       // reveal fraction that reaches world height y

function crackTube(L, grp, xf, top, bot, r, mat, n = 160) {
  const { THREE } = L; grp.updateMatrixWorld(true);
  const rc = new THREE.Raycaster(), pts = [];
  for (let i = 0; i <= n; i++) {
    const y = L.lerp(top, bot, i / n), x = grp.position.x + xf(y);
    rc.set(new THREE.Vector3(x, y, 9), new THREE.Vector3(0, 0, -1));
    const h = rc.intersectObjects(grp.children.filter(c => c.isMesh), false)[0];
    if (h) { const p = h.point.clone(); p.z += .035; pts.push(grp.worldToLocal(p)); }
  }
  const segs = 240, rad = 6;
  const geo = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), segs, r, rad, false);
  const m = new THREE.Mesh(geo, mat); grp.add(m); m.userData.seg = segs * rad * 6; return m;
}
const reveal = (m, k) => { m.visible = k > 0.002; m.geometry.setDrawRange(0, Math.floor(L_clamp(k) * m.userData.seg / 36) * 36); };
const L_clamp = k => Math.min(1, Math.max(0, k));

export function setup(L) {
  const { THREE, scene, centerTooth: ct, RoundedBoxGeometry, rnd, SP } = L;
  L.renderer.localClippingEnabled = true;
  // own (fadeable) materials for the x=0 tooth
  ctEn = L.enamel.clone(); ctEn.transparent = true; ct.children[0].material = ctEn;
  ctRoot = L.rootMat.clone(); ctRoot.transparent = true; ct.children[1].material = ctRoot;
  // pulp chamber + two canals (children of the tooth, shown in the X-ray beats)
  chMat = new THREE.MeshStandardMaterial({ color: '#f0788a', roughness: .45, emissive: '#000000' });
  canalMat = new THREE.MeshStandardMaterial({ color: '#f0788a', roughness: .45, emissive: '#000000' });
  pulpCh = new THREE.Group(); ct.add(pulpCh);
  { const g = new THREE.LatheGeometry([[0, -.4], [.78, -.3], [.88, .6], [.74, 1.45], [.35, 1.7], [0, 1.6]].map(p => new THREE.Vector2(p[0], p[1])), 32);
    const ch = new THREE.Mesh(g, chMat); ch.scale.z = .8; pulpCh.add(ch);
    [-.72, .72].forEach(dx => { const c = new THREE.Mesh(new THREE.CylinderGeometry(.2, .07, 5.4, 16), canalMat); c.position.set(dx * 1.1, -3.0, 0); c.rotation.z = dx * .035; pulpCh.add(c); }); }
  // the crack on the x=0 tooth (front surface, crown -> root) + its glow
  const cm = new THREE.MeshStandardMaterial({ color: '#3b2a22', roughness: .7 });
  const xf = y => y > .9 ? .18 + .2 * Math.sin(y * 4.1) + .06 * Math.sin(y * 13) : L.lerp(.18 + .2 * Math.sin(.9 * 4.1), .62, L_clamp((.9 - y) / 1.6)) + .07 * Math.sin(y * 9);
  crack = crackTube(L, ct, xf, CRACK_TOP, CRACK_BOT, .055, cm);
  crackGlow = crackTube(L, ct, xf, CRACK_TOP, CRACK_BOT, .16, new THREE.MeshBasicMaterial({ color: '#ff3b47', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  // crown material (a touch bluer/brighter so the new crown reads as a restoration)
  crownMat = new THREE.MeshPhysicalMaterial({ color: '#f4fbff', roughness: .15, clearcoat: 1, clearcoatRoughness: .1, sheen: .4 });
  L.newCrown.children[0].material = crownMat; L.newCrown.children[0].scale.set(1.07, 1.05, 1.07);
  // ice cube + shards
  const iceMat = new THREE.MeshPhysicalMaterial({ color: '#d4f1ff', roughness: .05, clearcoat: 1, transparent: true, opacity: .72, emissive: '#5fb2e6', emissiveIntensity: .12 });
  ice = new THREE.Mesh(new RoundedBoxGeometry(2.4, 2.4, 2.4, 4, .32), iceMat); ice.castShadow = true; scene.add(ice);
  for (let i = 0; i < 12; i++) { const s = new THREE.Mesh(new RoundedBoxGeometry(.5 + rnd() * .4, .4 + rnd() * .4, .5 + rnd() * .3, 2, .1), iceMat);
    const a = (i / 12) * Math.PI * 2; s.userData = { v: new THREE.Vector3(Math.cos(a) * (3 + rnd() * 3), 3 + rnd() * 4, Math.sin(a) * 2 + 2.5), r: rnd() * 8 }; scene.add(s); shards.push(s); }
  // the right neighbour (x = SP) split into two clipped halves (what-if beat)
  [[-1, 1], [1, -1]].forEach(([nx]) => { const P = new THREE.Plane(new THREE.Vector3(nx, 0, 0), 0); planes.push(P);
    const en = L.enamel.clone(); en.clippingPlanes = [P]; en.side = THREE.DoubleSide;
    const rm = L.rootMat.clone(); rm.clippingPlanes = [P]; rm.side = THREE.DoubleSide;
    const h = L.tooth(SP, true, en); h.children[1].material = rm; halves.push(h); });
  // night guard: a clear blue shell over the lower crowns
  guard = new THREE.Mesh(new RoundedBoxGeometry(26.5, 1.5, 4.0, 4, .5), new THREE.MeshPhysicalMaterial({ color: '#8fd8ff', roughness: .1, clearcoat: 1, transparent: true, opacity: .5, depthWrite: false }));
  scene.add(guard);
  // magnifier
  mag = new THREE.Group(); scene.add(mag);
  { const navy = new THREE.MeshPhysicalMaterial({ color: '#16324F', roughness: .3, clearcoat: 1 });
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.5, .2, 16, 48), navy); mag.add(ring);
    const glass = new THREE.Mesh(new THREE.CircleGeometry(1.5, 40), new THREE.MeshPhysicalMaterial({ color: '#dff4ff', transparent: true, opacity: .25, roughness: 0, clearcoat: 1, depthWrite: false })); mag.add(glass);
    const handle = new THREE.Mesh(new THREE.CapsuleGeometry(.26, 2.4, 6, 16), navy); handle.position.set(1.9, -1.9, 0); handle.rotation.z = Math.PI / 4; mag.add(handle); }
  // a hairline crack on the left neighbour (x = -SP), only visible under the magnifier
  const nb = L.neighbors[2];
  hair = crackTube(L, nb, y => -.1 + .12 * Math.sin(y * 5), 3.4, 1.4, .07, new THREE.MeshBasicMaterial({ color: '#ffe14d', transparent: true, opacity: 0, depthWrite: false }));
  Object.assign(L.SHOTS, {
    tc: [[2.6, 4.4, 12.5], [0, 2.6, 0]],           // the x=0 crown, close
    xr: [[2.6, 0.4, 21.5], [0, -0.9, 0]],          // whole tooth incl. roots
    nbR: [[SP + 3, 4.6, 15.5], [SP, 1.8, 0]],      // the right neighbour
    nbL: [[-SP - 2.4, 4.2, 11.5], [-SP, 2.5, 0]],  // the left neighbour, close
  });
  L.onReset(() => {
    [ice, ...shards, guard, mag, ...halves].forEach(o => o.visible = false);
    ice.position.set(0, 5, .2); ice.rotation.set(.3, .5, .1); ice.scale.setScalar(1); shards.forEach(s => s.scale.setScalar(1));
    reveal(crack, 0); reveal(crackGlow, 0); crackGlow.material.opacity = 0; hair.material.opacity = 0;
    ctEn.opacity = 1; ctEn.depthWrite = true; ctRoot.opacity = 1; ctRoot.depthWrite = true; pulpCh.visible = false;
    chMat.color.set('#f0788a'); chMat.emissive.set('#000000'); canalMat.color.set('#f0788a'); canalMat.emissive.set('#000000');
    L.neighbors[3].visible = true; warnAt(L, 0, 1.5, .6, 1);
  });
}
function warnAt(L, x, y, z, s) { L.warn.position.set(x, y, z); L.warn.scale.setScalar(s); }
function xray(L, k) { ctEn.opacity = 1 - .72 * k; ctRoot.opacity = 1 - .72 * k; const d = k < .5; ctEn.depthWrite = d; ctRoot.depthWrite = d; pulpCh.visible = k > .05; }
function hot(L, k, t) { chMat.color.set('#f0788a').lerp(new L.THREE.Color('#e3203f'), k); canalMat.color.copy(chMat.color); const e = k * (.35 + .25 * Math.sin(t * 12)); chMat.emissive.setRGB(e, 0, .05 * e); canalMat.emissive.copy(chMat.emissive); }
function treated(L, k) { chMat.color.set('#e3203f').lerp(new L.THREE.Color('#f5f2ea'), k); canalMat.color.set('#e3203f').lerp(new L.THREE.Color('#e8925a'), k); chMat.emissive.set('#000000'); canalMat.emissive.set('#000000'); }
function split(L, g) {   // open the right neighbour by g (0 = whole)
  L.neighbors[3].visible = false; const SP = L.SP;
  halves.forEach((h, i) => { h.visible = true; const s = i ? 1 : -1; h.position.set(SP + s * g / 2, .7 - g * .25, 0); h.rotation.set(0, 0, -s * g * .12); });
  planes[0].constant = SP - g / 2; planes[1].constant = -(SP + g / 2);
}

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, GUM_TOP, setCam, chip, sparkleAt, centerTooth: ct, newCrown, upper, food, warn, SP } = L;
  let blur = 0, flash = 0;
  const wb = (a) => t < a + .35 ? (1 - seg(t, a, a + .35)) * 13 : 0;
  const crownT = mk(6, 'so', .5);
  const crowned = () => { newCrown.visible = true; newCrown.position.set(0, .7, 0); };
  const hitFlash = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;

  if (t < be(0)) {                         // hook — an ice cube drops on the molar, the upper jaw crunches it
    const a = bs(0), d = B[0].dur, cr = mk(0, 'crunch', .4);
    const drop = eout(seg(t, a + .05, a + .6));
    if (t < cr + .05) { ice.visible = true; ice.position.set(0, lerp(13, 4.95, drop), .2); ice.rotation.set(.3 + (1 - drop) * 3, .5, .1); }
    const down = ein(seg(t, cr - .45, cr)), up = eout(seg(t, cr + .25, cr + .9));
    upper.position.y = lerp(11, 5.4, down) - (t > cr ? 2 * Math.sin(seg(t, cr, cr + .25) * Math.PI / 2) : 0) + (t > cr ? 7.6 * up : 0);
    if (t > cr) shards.forEach(s => { const tt = t - cr; s.visible = tt < 1.6; s.position.set(s.userData.v.x * tt * .7, 4.9 + s.userData.v.y * tt - 6 * tt * tt, .2 + s.userData.v.z * tt * .5); s.rotation.set(tt * s.userData.r, tt * 3, 0); });
    flash = hitFlash(cr);
    setCam('bite', 'gap', ease(seg(t, cr + .3, be(0))), t > cr && t < cr + .4 ? .25 : 0, t);
    chip('crunch', 'กรุบ! 🧊', 'yel', 230, t, cr, mk(0, 'hard', .7) - .05, -4);
    chip('hard', 'ฟันแข็งจะตาย?', 'dark', 230, t, mk(0, 'hard', .7), be(0) - .1);
  } else if (t < be(1)) {                  // brittle: repeated cold + bite -> a hairline crack appears
    const a = bs(1), d = B[1].dur, bt = mk(1, 'bites', .4), ck = mk(1, 'crack', .75);
    const ph = clamp((t - bt) / 1.5); const bob = t > bt && t < bt + 1.5 ? Math.pow(Math.sin(ph * 3 * Math.PI), 2) : 0;
    upper.position.y = lerp(11, 3.6, bob);
    if (t > bt && t < bt + 1.5) { food.visible = false; shards.slice(0, 5).forEach((s, i) => { const tt = (t - bt - i * .25); s.visible = tt > 0 && tt < .8; s.position.set((i - 2) * .9, 4.2 + tt * 3 - 6 * tt * tt, 1.2); s.rotation.set(tt * 6, tt * 4, 0); s.scale.setScalar(.6); }); }
    reveal(crack, crackK(2.75) * eout(seg(t, ck, ck + .8)));
    crackGlow.material.opacity = t > ck ? .7 * Math.exp(-(t - ck) * 2.5) : 0; reveal(crackGlow, crackK(2.75) * eout(seg(t, ck, ck + .8)));
    blur = wb(a);
    setCam('gap', 'tc', ease(seg(t, ck - .6, ck + .5)), bob > .9 ? .08 : 0, t);
    chip('brittle', 'ผิวเคลือบฟัน แข็งแต่เปราะ', 'dark', 190, t, mk(1, 'brittle', .2), be(1) - .1);
    chip('crack', 'รอยร้าว', 'yel', 330, t, ck + .2, be(1) - .1, -3);
    shards.forEach(s => s.scale.setScalar(.6));
  } else if (t < be(2)) {                  // bite = ok, release = ZING -> cracked tooth
    const a = bs(2), bt = mk(2, 'bite', .1), rl = mk(2, 'rel', .35), z = mk(2, 'zing', .5);
    upper.position.y = t < rl ? lerp(11, 3.35, eout(seg(t, bt, bt + .5))) : lerp(3.35, 11, eout(seg(t, rl + .1, z)));
    const k = lerp(crackK(2.75), crackK(2.2), seg(t, z, z + .4)); reveal(crack, k); reveal(crackGlow, k);
    crackGlow.material.opacity = t > z ? .9 * Math.exp(-(t - z) * 1.4) * (.6 + .4 * Math.sin((t - z) * 30)) : 0;
    warn.material.opacity = t > z ? .9 * Math.exp(-(t - z) * 1.2) : 0; warnAt(L, 0, 3, .9, 1.1 + .1 * Math.sin(t * 20));
    flash = hitFlash(z, .4);
    setCam('tc', 'neck', ease(seg(t, a, rl)), t > z && t < z + .45 ? .14 : 0, t);
    chip('ok', 'กดลง… ไม่เท่าไหร่', 'green', 190, t, bt, rl - .05);
    chip('zing', '⚡ แปล๊บ! ตอนปล่อย', 'red', 190, t, z, be(2) - .1, -3);
    chip('term', 'ภาวะฟันร้าว (Cracked Tooth)', 'dark', 330, t, mk(2, 'term', .8), be(2) - .1);
  } else if (t < be(3)) {                  // chew on the other side? the crack does not heal and creeps deeper
    const a = bs(3), so = mk(3, 'so', .05), dp = mk(3, 'deep', .7);
    food.visible = t < mk(3, 'nohe', .5); food.position.set(-2 * SP, GUM_TOP + 2.9, .2);
    upper.position.y = t < mk(3, 'nohe', .5) ? 11 - 6.6 * Math.pow(Math.max(0, Math.sin((t - so) * 2.6 * Math.PI)), 2) * clamp((t - so) * 3) : 11;
    if (t < mk(3, 'nohe', .5)) food.scale.y = .8 * (1 - .3 * clamp((11 - upper.position.y) / 6.6));
    const k = lerp(crackK(2.2), crackK(1.0), eout(seg(t, dp, dp + 1.4))); reveal(crack, k); reveal(crackGlow, k);
    crackGlow.material.opacity = t > dp ? .5 + .2 * Math.sin(t * 8) : 0;
    blur = wb(a);
    setCam('wide', 'neck', ease(seg(t, mk(3, 'nohe', .5) - .4, mk(3, 'nohe', .5) + .6)));
    chip('other', 'เคี้ยวอีกข้างแทน?', 'dark', 190, t, so, mk(3, 'nohe', .5) - .05);
    chip('nohe', '✕ รอยร้าวไม่หายเอง', 'red', 190, t, mk(3, 'nohe', .5), be(3) - .1, -2);
    chip('deep', '⬇ ลามลึกขึ้น', 'yel', 330, t, dp, be(3) - .1);
  } else if (t < be(4)) {                  // X-ray: the crack reaches the pulp -> pain, cold sensitivity, pulp inflamed
    const a = bs(4), d = B[4].dur, inf = mk(4, 'inf', .7);
    xray(L, eout(seg(t, a, a + .5)));
    const k = lerp(crackK(1.0), crackK(-.2), eout(seg(t, a + .3, a + 1.4))); reveal(crack, k); reveal(crackGlow, k);
    crackGlow.material.opacity = .55 + .25 * Math.sin(t * 9);
    hot(L, seg(t, mk(4, 'pain', .3), inf + .3), t);
    const p = t > mk(4, 'pain', .3) ? .5 + .5 * Math.sin(t * 9) : 0;
    ct.position.x = t > mk(4, 'pain', .3) ? Math.sin(t * 40) * .03 : 0;
    warn.material.opacity = t > inf ? .8 * p : 0; warnAt(L, 0, 1.6, .9, 1.25 + .06 * p);
    blur = wb(a);
    setCam('neck', 'xr', ease(seg(t, a, a + d * .45)));
    chip('pulp', 'ร้าวถึงโพรงประสาท', 'dark', 190, t, a + .5, be(4) - .1);
    chip('cold', '🥶 ปวดตุ๊บๆ เสียวน้ำเย็น', 'yel', 320, t, mk(4, 'pain', .3), be(4) - .1);
    chip('inf', 'ประสาทฟันอักเสบ', 'red', 450, t, inf, be(4) - .1, 2);
  } else if (t < be(5)) {                  // root canal treatment: clean the pulp space, then seal it
    const a = bs(5), d = B[5].dur, cl = mk(5, 'clean', .3), sl = mk(5, 'seal', .7);
    xray(L, 1 - ein(seg(t, be(5) - .55, be(5))));
    reveal(crack, crackK(-.2)); reveal(crackGlow, crackK(-.2)); crackGlow.material.opacity = .25;
    hot(L, 1 - seg(t, a, cl), t); if (t > cl) treated(L, eout(seg(t, cl, sl + .3)));
    if (t > cl && t < sl + .3) sparkleAt(0, lerp(2.3, -4.5, seg(t, cl, sl)), .6, (t * 2.2) % 1, 1.4);
    if (t > sl + .3) sparkleAt(0, 2.4, .6, seg(t, sl + .3, sl + 1), 2.6);
    flash = hitFlash(sl + .3, .2);
    setCam('xr', 'xr', 0);
    chip('rct', 'รักษารากฟัน', 'green', 190, t, mk(5, 'so', .05) + .1, be(5) - .1);
    chip('seal', 'ทำความสะอาด → อุดปิด ✓', 'dark', 320, t, sl, be(5) - .1);
  } else if (t < be(6)) {                  // still may break further -> a crown holds it together
    const a = bs(6), mr = mk(6, 'more', .25);
    reveal(crack, crackK(-.2)); reveal(crackGlow, crackK(-.2));
    const shake = t > mr && t < crownT ? Math.sin(t * 34) * .05 : 0; ct.rotation.z = shake; ct.position.x = shake * 2;
    crackGlow.material.opacity = t > mr && t < crownT ? .6 + .3 * Math.sin(t * 14) : 0;
    if (t > crownT) { newCrown.visible = true; const k = seg(t, crownT, crownT + .55); newCrown.position.set(0, lerp(10, .7, ein(k)), 0);
      if (k >= 1) { sparkleAt(0, 3, .5, seg(t, crownT + .55, crownT + 1.3), 3.4); flash = .35 * Math.exp(-(t - crownT - .55) * 10); crack.visible = false; crackGlow.visible = false; } }
    setCam('neck', 'crown', ease(seg(t, crownT - .3, crownT + 1.2)), t > crownT + .55 && t < crownT + .9 ? .12 : 0, t);
    chip('more', '⚠ อาจแตกต่อ', 'red', 190, t, mr, crownT - .05, -3);
    chip('crown', 'ครอบฟัน', 'green', 190, t, crownT + .5, be(6) - .1);
    chip('hold', 'รัดซี่ไว้ ไม่ให้แยก', 'dark', 320, t, mk(6, 'hold', .8), be(6) - .1);
  } else if (t < be(7)) {                  // what-if: a crack down the root splits the right neighbour in two
    const a = bs(7), sp = mk(7, 'split', .4);
    crowned();
    const g = t > sp ? 1.3 * back(seg(t, sp, sp + .6)) : 0; split(L, g);
    if (t > sp - .8 && t < sp) halves.forEach((h, i) => h.position.x += Math.sin(t * 45) * .04);
    warn.material.opacity = t > sp ? .85 * (.5 + .5 * Math.sin((t - sp) * 12)) : 0; warnAt(L, SP, 2.6, 1.2, 1.4);
    flash = hitFlash(sp, .3);
    blur = wb(a);
    setCam('gap', 'nbR', ease(seg(t, a, a + .9)), t > sp && t < sp + .4 ? .14 : 0, t);
    chip('if', 'ถ้าปล่อยไว้…', 'dark', 190, t, a + .15, be(7) - .1);
    chip('split', 'ฟันแยกเป็นสองซีก', 'red', 320, t, sp + .1, be(7) - .1, -2);
    chip('lost', 'เก็บไว้ไม่ได้ ✕', 'red', 450, t, mk(7, 'lost', .75), be(7) - .1, 2);
  } else if (t < be(8)) {                  // prevention: no ice, no hard objects, night guard for grinders
    const a = bs(8), d = B[8].dur, c1 = mk(8, 'c1', .2), c2 = mk(8, 'c2', .4), gd = mk(8, 'guard', .75);
    crowned();
    if (t < a + .45) split(L, 1.3 * (1 - eout(seg(t, a, a + .45))));
    if (t > c1 - .3 && t < c2 + .6) { ice.visible = true; const k = seg(t, c1 - .3, c1 + .2); ice.position.set(0, lerp(12, 6.6, eout(k)) + .2 * Math.sin(t * 4), .5); ice.rotation.set(t, t * 1.3, 0);
      ice.scale.setScalar(1 - ein(seg(t, c2, c2 + .6))); }
    if (t > gd) { guard.visible = true; const k = seg(t, gd, gd + .6); guard.position.set(0, lerp(9, 3.3, eout(k)), 0); if (k >= 1) sparkleAt(0, 3.6, 1.5, seg(t, gd + .6, gd + 1.3), 5); }
    blur = wb(a);
    setCam('nbR', 'gap', ease(seg(t, a, a + .8)));
    if (t > gd - .3) setCam('gap', 'high', ease(seg(t, gd - .3, gd + .6)));
    chip('c1', '✕ เคี้ยวน้ำแข็ง', 'red', 190, t, c1, be(8) - .1, -2);
    chip('c2', '✕ ใช้ฟันกัดของแข็ง', 'red', 300, t, c2, be(8) - .1, 2);
    chip('c3', '🌙 นอนกัดฟัน? ใส่เฝือกสบฟัน', 'green', 410, t, mk(8, 'c3', .6), be(8) - .1);
  } else if (t < be(9)) {                  // myth: cracks are always visible? no — a crack can be too small to see
    const a = bs(9), d = B[9].dur, no = mk(9, 'no', .45), tn = mk(9, 'tiny', .7);
    crowned();
    mag.visible = t > no; const mk0 = eout(seg(t, no, no + .6));
    mag.position.set(lerp(-SP - 7, -SP + .1, mk0) + (t > tn ? .25 * Math.sin((t - tn) * 3) : 0), lerp(6, 2.7, mk0), 2.2);
    hair.material.opacity = t > tn ? .95 * eout(seg(t, tn, tn + .5)) : 0;
    blur = wb(a);
    setCam('wide', 'nbL', ease(seg(t, a, a + d * .5)));
    chip('m1', 'ฟันร้าว ต้องเห็นชัด?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', 190, t, no, be(9) - .1, -4);
    chip('m3', 'รอยร้าวอาจเล็กจนมองไม่เห็น', 'yel', 320, t, tn, be(9) - .1);
  } else if (t < be(10)) {                 // congratulations — chewing happily, confetti
    const a = bs(10), d = B[10].dur, ch = mk(10, 'chew', .45);
    crowned(); L.confetti(t, a);
    sparkleAt(0, 3, .5, seg(t, a, a + .9), 3.8);
    const bob = t > ch ? Math.pow(Math.max(0, Math.sin((t - ch) * 2.4 * Math.PI)), 2) : 0;
    food.visible = true; food.position.set(0, GUM_TOP + 2.9, .2); food.scale.set(1.25, .8 * (1 - .35 * bob), 1);
    upper.position.y = 11 - 6.4 * bob;
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
    chip('yay', '🦷 ฟันยังอยู่ครบ!', 'green', 190, t, a + .3, be(10) - .1);
  } else {                                 // under the end card
    crowned(); setCam('wide', 'wide', 0);
  }
  return { blur, flash };
}

// cover: an ice cube over the molar, a glowing crack running down the tooth
export function cover(t, L) {
  const { lerp, clamp, upper, cam, warn, sparkleAt } = L;
  upper.position.y = 40;
  reveal(crack, crackK(.6)); reveal(crackGlow, crackK(.6)); crackGlow.material.opacity = .6 + .3 * Math.sin(t * 10);
  ice.visible = true; ice.position.set(1.6, 6.2 + .25 * Math.sin(t * 2.2), 2.5); ice.rotation.set(.5 + t * .3, .7 + t * .5, .2);
  shards.slice(0, 4).forEach((s, i) => { s.visible = true; s.scale.setScalar(.7); const a = i * 1.6 + t; s.position.set(1.6 + Math.cos(a) * 2.4, 6.1 + Math.sin(a) * 1.1, 2.5 + Math.sin(a) * .5); s.rotation.set(t * 2 + i, t, 0); });
  warn.material.opacity = .7 * (.5 + .5 * Math.sin(t * 10)); warnAt(L, .3, 2.6, 1.2, 1.15);
  sparkleAt(1.6, 6.2, 2.5, (t * .7) % 1, 3);
  const k = clamp(t / 2);
  cam.position.set(lerp(3.4, 3.1, k), lerp(7.0, 6.8, k), lerp(27, 25.5, k)); cam.lookAt(.9, 6.9, 0);
  return [
    { text: 'น้ำแข็ง', at: [2.9, 6.6, 2.5], dx: 60 },
    { text: 'รอยร้าว', at: [.5, 1.6, 1.4], dx: 60 },
  ];
}

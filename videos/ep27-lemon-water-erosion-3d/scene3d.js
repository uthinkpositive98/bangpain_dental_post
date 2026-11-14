// ep27 น้ำมะนาวตอนเช้า ฟันว่าไง? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the x=0 tooth cut in half (back half 3D, front = flat cross-section: enamel, dentin, pulp), as in ep25/ep26, plus a
// glass of warm lemon water at the top right. Lemon is acidic -> acid etches the enamel directly, no germs needed
// (dental erosion) -> drink through a straw + rinse with plain water -> but brushing right away scrubs the softened
// enamel off -> wait about an hour (ADA) so saliva re-hardens it, then brush -> but acid every day: enamel thins, the
// tooth looks yellow, cold drinks zap -> fluoride toothpaste + soft brush, gently -> but eroded enamel never grows back:
// sensitive often -> see the dentist -> myth: rubbing lemon on teeth whitens them? no — thinner enamel, more yellow -> payoff.
let ct, sec = {}, P, glass, liquid, slice, straw, acid = [], water = [], flakes = [], bolts = [], paste, mirror, rubSlice, ghost, en, pulpMat;

function outline() {
  const R = [[0.18, -1.3], [0.54, -5.9], [0.72, -6.05], [0.9, -5.9], [1.12, -3], [1.38, -0.6], [1.32, 0], [1.6, 0.7], [1.74, 1.6], [1.68, 2.35], [1.5, 2.85], [1.15, 3.18], [0.7, 2.95], [0.25, 2.82]];
  return [[0, -1.1], ...R, [0, 2.8], ...R.slice().reverse().map(([x, y]) => [-x, y])];
}
const shapeOf = (THREE, pts) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y)); s.closePath(); return s; };
const CUP = [2.9, 5.5, 0.6];                         // glass base position (upper right of the cut tooth)
const WHITE = '#fbf8f1', YEL = '#ead08c';

function sliceTex(L) {
  return L.canvasTex(256, 256, (g) => { g.translate(128, 128);
    g.fillStyle = '#f2d43a'; g.beginPath(); g.arc(0, 0, 124, 0, 7); g.fill();
    g.fillStyle = '#fffbe6'; g.beginPath(); g.arc(0, 0, 108, 0, 7); g.fill();
    for (let i = 0; i < 10; i++) { const a0 = i / 10 * Math.PI * 2 + .05, a1 = (i + 1) / 10 * Math.PI * 2 - .05;
      g.fillStyle = '#ffe15a'; g.beginPath(); g.moveTo(Math.cos((a0 + a1) / 2) * 10, Math.sin((a0 + a1) / 2) * 10); g.arc(0, 0, 100, a0, a1); g.closePath(); g.fill(); }
    g.fillStyle = '#fffbe6'; g.beginPath(); g.arc(0, 0, 12, 0, 7); g.fill(); });
}

export function setup(L) {
  const { THREE, scene, tooth, rnd, RoundedBoxGeometry } = L;
  L.renderer.localClippingEnabled = true;
  P = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  en = L.enamel.clone(); en.clippingPlanes = [P]; en.clipShadows = true; en.side = THREE.DoubleSide;
  const rm = L.rootMat.clone(); rm.clippingPlanes = [P]; rm.clipShadows = true; rm.side = THREE.DoubleSide;
  ct = tooth(0, true, en); ct.children[1].material = rm;
  const O = outline();
  const flat = (pts, color, z) => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), new THREE.MeshStandardMaterial({ color, roughness: .55, side: THREE.DoubleSide, emissive: '#000000' })); m.position.z = z; ct.add(m); return m; };
  sec.base = flat(O, '#efdcae', .006);
  const crownPts = O.filter(([x, y]) => y > .25); crownPts.unshift([1.45, .3]); crownPts.push([-1.45, .3]);
  sec.enamel = flat(crownPts.sort((a, b) => Math.atan2(a[1] - 1.2, a[0]) - Math.atan2(b[1] - 1.2, b[0])), WHITE, .010);
  const dent = O.map(([x, y]) => y > -0.6 ? [x * .82, y > 2 ? 2 + (y - 2) * .72 : y] : [Math.sign(x) * (.72 + (Math.abs(x) - .72) * .62), y * .975]);
  sec.dentin = flat(dent, '#f2d9a4', .014);
  const pulpPts = [[-0.55, 0.1], [-0.62, 1.2], [-0.5, 1.8], [-0.25, 1.45], [0, 1.5], [0.25, 1.45], [0.5, 1.8], [0.62, 1.2], [0.55, 0.1]];
  pulpMat = new THREE.MeshStandardMaterial({ color: '#f0788a', roughness: .45, side: THREE.DoubleSide, emissive: '#ff2040', emissiveIntensity: 0 });
  [pulpPts, [[-0.62, 0.2], [-0.32, 0.2], [-0.69, -5.6], [-0.77, -5.6]], [[0.62, 0.2], [0.32, 0.2], [0.69, -5.6], [0.77, -5.6]]]
    .forEach(pts => { const m = new THREE.Mesh(new THREE.ShapeGeometry(shapeOf(THREE, pts)), pulpMat); m.position.z = .018; ct.add(m); });
  // ghost of the original enamel (shown when the enamel has thinned: "it never grows back")
  ghost = new THREE.Mesh(L.CROWN, new THREE.MeshBasicMaterial({ color: '#ff5a6a', wireframe: true, transparent: true, opacity: 0, depthWrite: false }));
  ghost.scale.set(1.04, 1.03, 1.04); ct.add(ghost);

  // glass of warm lemon water: clear tumbler, pale lemon liquid (scale.y = level), lemon slice on the rim
  glass = new THREE.Group(); scene.add(glass);
  { const gm = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .05, transmission: .6, transparent: true, opacity: .32, side: THREE.DoubleSide, depthWrite: false });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(1.1, .9, 3.3, 40, 1, true), gm); body.position.y = 1.65; glass.add(body);
    const bot = new THREE.Mesh(new THREE.CylinderGeometry(.9, .9, .2, 40), gm); bot.position.y = .1; glass.add(bot);
    const lg = new THREE.CylinderGeometry(1.03, .86, 2.6, 40); lg.translate(0, 1.3, 0);
    liquid = new THREE.Mesh(lg, new THREE.MeshPhysicalMaterial({ color: '#f6e27a', roughness: .1, transparent: true, opacity: .75, clearcoat: 1 })); liquid.position.y = .2; glass.add(liquid);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(1.1, .05, 10, 48), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .2, clearcoat: 1 })); rim.rotation.x = Math.PI / 2; rim.position.y = 3.3; glass.add(rim);
    const tex = sliceTex(L);
    const sm = [new THREE.MeshStandardMaterial({ color: '#e9c52c', roughness: .5 }), new THREE.MeshStandardMaterial({ map: tex, roughness: .4 }), new THREE.MeshStandardMaterial({ map: tex, roughness: .4 })];
    slice = new THREE.Mesh(new THREE.CylinderGeometry(.95, .95, .16, 40), sm); slice.rotation.set(Math.PI / 2, 0, .2); slice.position.set(.9, 3.4, .35); glass.add(slice);
    straw = new THREE.Mesh(new THREE.CylinderGeometry(.14, .14, 5.2, 20), new THREE.MeshPhysicalMaterial({ color: '#46c7a8', roughness: .25, clearcoat: 1 }));
    straw.position.set(-.35, 3.0, 0); straw.rotation.z = .4; glass.add(straw); }
  // a loose lemon slice for the myth (rubbing on the tooth)
  rubSlice = new THREE.Mesh(new THREE.CylinderGeometry(.95, .95, .16, 40), slice.material); scene.add(rubSlice);
  // acid drops (yellow-green)
  const am = new THREE.MeshPhysicalMaterial({ color: '#d8f04a', roughness: .1, clearcoat: 1, transparent: true, opacity: .85, emissive: '#6a7a00', emissiveIntensity: .3 });
  for (let i = 0; i < 14; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.17, 14, 10), am); d.scale.set(1, 1.35, 1); d.userData = { x: -1.5 + rnd() * 2.8, z: -.9 + rnd() * .8, d: i * .05 }; scene.add(d); acid.push(d); }
  // water / saliva drops (blue)
  const wm = new THREE.MeshPhysicalMaterial({ color: '#8fd8ff', roughness: .05, clearcoat: 1, transparent: true, opacity: .75, emissive: '#1a5a8a', emissiveIntensity: .25 });
  for (let i = 0; i < 18; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.24, 16, 12), wm); d.userData = { x: -2.2 + rnd() * 4.4, z: -1 + rnd() * 1.6, d: i * .05, w: rnd() * 6 }; scene.add(d); water.push(d); }
  // enamel flakes scrubbed off by brushing too early
  const fm = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .4, side: THREE.DoubleSide });
  for (let i = 0; i < 16; i++) { const f = new THREE.Mesh(new THREE.CircleGeometry(.14, 5), fm); f.userData = { x: -1.4 + rnd() * 2.8, vx: (rnd() - .5) * 3, vy: 1 + rnd() * 2, d: rnd() * .6, s: rnd() * 8 }; scene.add(f); flakes.push(f); }
  // cold "zap" bolts from the chewing surface down to the pulp
  const bm = new THREE.MeshBasicMaterial({ color: '#7fe3ff', transparent: true, opacity: 1 });
  [[-0.9, 3.0, -0.35, 1.6], [0.9, 3.0, 0.35, 1.6]].forEach(([x0, y0, x1, y1]) => { const pts = []; for (let k = 0; k <= 6; k++) { const u = k / 6; pts.push(new THREE.Vector3(L.lerp(x0, x1, u) + (k % 2 ? .18 : -.18) * (k > 0 && k < 6), L.lerp(y0, y1, u), .05)); }
    const b = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0), 40, .06, 6, false), bm); ct.add(b); bolts.push(b); });
  sec.boltMat = bm;
  // ice cube (cold drink)
  sec.ice = new THREE.Mesh(new RoundedBoxGeometry(1.1, 1.1, 1.1, 3, .15), new THREE.MeshPhysicalMaterial({ color: '#dff6ff', roughness: .05, transmission: .5, transparent: true, opacity: .8, clearcoat: 1 })); scene.add(sec.ice);
  // fluoride toothpaste on the brush
  paste = new THREE.Mesh(new THREE.CapsuleGeometry(.35, 1.8, 8, 16), new THREE.MeshPhysicalMaterial({ color: '#dff4ff', roughness: .3, clearcoat: 1 })); paste.rotation.z = Math.PI / 2; L.brush.add(paste); paste.position.set(0, 0, -1.25);
  // dental mirror (dentist check)
  mirror = new THREE.Group(); scene.add(mirror);
  { const steel = new THREE.MeshStandardMaterial({ color: '#d5dbe2', metalness: 1, roughness: .2 });
    const h = new THREE.Mesh(new THREE.CylinderGeometry(.16, .2, 7, 16), steel); h.position.y = 3.8; mirror.add(h);
    const disc = new THREE.Mesh(new THREE.CylinderGeometry(.75, .75, .12, 32), steel); disc.rotation.x = Math.PI / 2; mirror.add(disc);
    const face = new THREE.Mesh(new THREE.CircleGeometry(.66, 32), new THREE.MeshStandardMaterial({ color: '#cfe9ff', metalness: 1, roughness: .02 })); face.position.z = .07; mirror.add(face); }
  Object.assign(L.SHOTS, {
    cupW: [[2.8, 6.2, 22], [1.2, 4.1, 0]],       // tooth + glass above it
    secC: [[1.4, 2.6, 11.5], [0, 1.4, 0]],       // section close-up (enamel, dentin, pulp)
    enam: [[0.4, 4.2, 8.5], [-0.4, 3.0, 0]],
    top: [[1.5, 8.5, 12], [0, 3.4, -.3]],
    sky: [[2.2, 5.0, 17], [0.4, 3.8, 0]],
  });
  L.onReset(() => {
    L.centerTooth.visible = false;
    ct.visible = true; ct.position.set(0, .7, 0); ct.rotation.set(0, 0, 0);
    [paste, mirror, rubSlice, sec.ice, ...acid, ...water, ...flakes, ...bolts].forEach(o => o.visible = false);
    glass.visible = false; glass.position.set(...CUP); glass.rotation.set(0, 0, 0); glass.scale.setScalar(1); liquid.scale.y = 1; straw.visible = false;
    setThin(0); en.color.set(WHITE); sec.enamel.material.emissive.set('#000000'); sec.enamel.material.emissiveIntensity = 1;
    pulpMat.emissiveIntensity = 0; ghost.material.opacity = 0;
    L.brush.rotation.set(0, 0, 0); L.brush.scale.setScalar(1);
  });
}

// enamel thinning (0..1): the section's enamel rim shrinks toward the dentin, the crown turns yellowish
function setThin(k) { const s = 1 - .085 * k; sec.enamel.scale.set(s, s, 1); sec.enamel.position.y = 1.6 * (1 - s); en.color.set(WHITE).lerp(new en.color.constructor(YEL), k); sec.enamel.material.color.set(WHITE).lerp(new en.color.constructor('#f3e6c2'), k); }
const bob = (t) => { glass.position.y = CUP[1] + Math.sin(t * 2.2) * .12; glass.rotation.y = Math.sin(t * .8) * .3; };
// a sip from the glass: tilts toward the tooth and acid drops fall onto the crown
function acidRain(L, t, t0, n = 14) { acid.forEach((dp, i) => { if (i >= n) return; const k = L.seg(t, t0 + dp.userData.d, t0 + .6 + dp.userData.d); dp.visible = k > 0 && k < 1; dp.position.set(dp.userData.x, L.lerp(6.5, 3.6, L.ein(k)), dp.userData.z); }); }
function wash(L, t, t0) { water.forEach(d => { const k = L.seg(t, t0 + d.userData.d, t0 + 1.1 + d.userData.d); d.visible = k > 0 && k < 1;
  d.position.set(d.userData.x + Math.sin(k * 6 + d.userData.w) * .3, L.lerp(7, 1.6, L.ease(k)), d.userData.z); d.scale.setScalar(1 - .5 * k); }); }
function softGlow(t, k) { sec.enamel.material.emissive.setRGB(.35 * k, .22 * k, 0); sec.enamel.material.emissiveIntensity = .6 + .4 * Math.sin(t * 8); }
function hardGlow(t, k) { sec.enamel.material.emissive.setRGB(0, .12 * k, .34 * k); sec.enamel.material.emissiveIntensity = .7 + .3 * Math.sin(t * 6); }
function scrub(L, t, t0, t1, y = 4.9) { const { brush, seg, eout, ein, lerp } = L; brush.visible = true; brush.rotation.set(Math.PI / 2, 0, 0);
  brush.position.set(lerp(-6, 0, eout(seg(t, t0, t0 + .4))) + (t > t0 + .4 ? Math.sin(t * 14) * .9 : 0) + ein(seg(t, t1 - .3, t1)) * 12, y, -.4); }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, setCam, chip, sparkleAt, warn, halo, brush } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const LB = 1150, LB2 = 1290, LB3 = 1430;
  L.upper.position.y = 40;

  if (t < be(0)) {                                   // hook: warm lemon water in the morning — healthy, teeth love it too?
    const a = bs(0), d = B[0].dur, gl = mk(0, 'glass', .05), hl = mk(0, 'health', .4), ask = mk(0, 'ask', .7);
    L.upper.position.y = lerp(11, 40, ease(seg(t, a, a + d * .5)));
    glass.visible = true; glass.scale.setScalar(back(seg(t, gl, gl + .5))); bob(t);
    if (t > hl) sparkleAt(CUP[0], CUP[1] + 1.8, CUP[2], seg(t, hl, hl + .8), 2.4);
    if (t > ask) { halo.material.opacity = .25 * eout(seg(t, ask, ask + .5)); halo.position.set(0, 3.6, .5); halo.scale.set(6, 6, 1); }
    setCam('wide', 'cupW', ease(seg(t, a, a + d * .55)));
    chip('h1', '🍋 น้ำมะนาวอุ่น ตอนเช้า', 'dark', LB, t, mk(0, 'morning', .2), be(0) - .1);
    chip('h2', '= ดีต่อฟันด้วย ?', 'green', LB2, t, ask, be(0) - .1, -2);
  } else if (t < be(1)) {                            // sour = acid, etches the enamel directly, no germs needed: erosion
    const a = bs(1), d = B[1].dur, so = mk(1, 'sour', .05), ac = mk(1, 'acid', .2), bt = mk(1, 'bite', .35), ng = mk(1, 'nogerm', .6), tm = mk(1, 'term', .85);
    glass.visible = true; bob(t); glass.rotation.z = .4 * Math.sin(Math.PI * seg(t, so, so + 1.2));
    acidRain(L, t, ac); if (t > bt) acidRain(L, t, bt + .4); if (t > ng) acidRain(L, t, ng);
    if (t > bt) softGlow(t, seg(t, bt, bt + .8));
    if (t > bt) { warn.material.opacity = .8 * Math.exp(-(t - bt) * 1.4); warn.position.set(-.6, 3.6, .2); warn.scale.setScalar(.6); }
    flash = hit(bt, .2);
    blur = whip(1);
    setCam('cupW', 'enam', ease(seg(t, a + .3, bt + .3)));
    chip('ac', '🍋 เปรี้ยวจัด = กรด', 'yel', LB, t, ac, be(1) - .1);
    chip('ng', 'กัดเคลือบฟันโดยตรง ไม่ต้องรอเชื้อโรค', 'red', LB2, t, bt, be(1) - .1, -2);
    chip('tm', 'ฟันกร่อน (Dental erosion)', 'red', LB3, t, tm, be(1) - .1);
  } else if (t < be(2)) {                            // fix: drink through a straw, then rinse with plain water
    const a = bs(2), d = B[2].dur, sw = mk(2, 'straw', .05), ls = mk(2, 'less', .3), rn = mk(2, 'rinse', .55), ws = mk(2, 'wash', .8);
    glass.visible = true; bob(t); softGlow(t, 1 - .5 * seg(t, rn, ws));
    straw.visible = t > sw; if (t > sw) { const k = back(seg(t, sw, sw + .5)); straw.position.y = lerp(7, 3.0, k); }
    liquid.scale.y = 1 - .5 * ease(seg(t, ls, rn));
    if (t > rn) { wash(L, t, rn); sparkleAt(-.3, 3.7, .3, seg(t, ws, ws + .9), 2); }
    blur = whip(2);
    setCam('enam', 'cupW', ease(seg(t, a, a + .7)));
    if (t > rn - .2) setCam('cupW', 'enam', ease(seg(t, rn - .2, rn + .8)));
    chip('sw', '🥤 ดื่มผ่านหลอด', 'green', LB, t, sw + .1, be(2) - .1);
    chip('rn', '💧 บ้วนปากด้วยน้ำเปล่า', 'dark', LB2, t, rn, be(2) - .1, -2);
  } else if (t < be(3)) {                            // but brushing right away scrubs the softened enamel off
    const a = bs(3), d = B[3].dur, br = mk(3, 'brush', .2), sf = mk(3, 'soft', .5), wr = mk(3, 'wear', .75);
    softGlow(t, seg(t, sf, sf + .5));
    if (t > br) scrub(L, t, br, be(3) + 1);
    if (t > wr) flakes.forEach(f => { const u = f.userData, tt = t - wr - u.d; f.visible = tt > 0 && tt < 1.4; f.position.set(u.x + u.vx * tt, 3.4 + u.vy * tt - 4 * tt * tt, .3); f.rotation.set(tt * u.s, tt * 3, 0); });
    setThin(.25 * seg(t, wr, be(3)));
    if (t > wr) { warn.material.opacity = .7 * Math.exp(-(t - wr) * 1.2); warn.position.set(0, 3.6, .3); warn.scale.setScalar(.6); }
    flash = hit(wr, .2);
    blur = whip(3);
    setCam('enam', 'top', ease(seg(t, a, a + .8)));
    if (t > sf - .3) setCam('top', 'enam', ease(seg(t, sf - .3, sf + .6)));
    chip('br', '🪥 แปรงทันที', 'dark', LB, t, br, be(3) - .1);
    chip('sf', 'เคลือบฟันนิ่มจากกรด', 'yel', LB2, t, sf, be(3) - .1, -2);
    chip('wr', '⚠ สึกไปกับแปรง', 'red', LB3, t, wr, be(3) - .1, 2);
  } else if (t < be(4)) {                            // fix: wait about an hour, saliva re-hardens the surface, then brush
    const a = bs(4), d = B[4].dur, wt = mk(4, 'wait', .05), hr = mk(4, 'hour', .2), sl = mk(4, 'saliva', .45), hd = mk(4, 'hard', .6), th = mk(4, 'then', .85);
    setThin(.25);
    const mins = Math.round(60 * ease(seg(t, hr, sl + .8)));
    if (t > wt) L.calendar('รอก่อน (นาที)', String(mins), (t > be(4) - .3 ? 1 - seg(t, be(4) - .3, be(4)) : 1) * (1 + .1 * Math.sin(t * 12) * (mins < 60)));
    if (t < sl) softGlow(t, 1); else hardGlow(t, seg(t, sl, hd + .5));
    if (t > sl) wash(L, t, sl);
    if (t > hd) sparkleAt(-.3, 3.7, .3, ((t - hd) * 1.3) % 1, 1.8);
    if (t > th) scrub(L, t, th, be(4) + 1, 4.9);
    blur = whip(4);
    setCam('enam', 'secC', ease(seg(t, a, a + .9)));
    if (t > th - .3) setCam('secC', 'top', ease(seg(t, th - .3, th + .5)));
    chip('hr', '⏰ รอประมาณ 1 ชั่วโมง', 'green', LB, t, hr, be(4) - .1);
    chip('hd', '💦 น้ำลายช่วยให้ผิวฟันแข็งขึ้น', 'dark', LB2, t, hd, be(4) - .1, -2);
    chip('th', '✓ แล้วค่อยแปรง', 'green', LB3, t, th, be(4) - .1, 2);
  } else if (t < be(5)) {                            // but acid every day: enamel thins, tooth looks yellow, cold drinks zap
    const a = bs(5), d = B[5].dur, dy = mk(5, 'daily', .05), tn = mk(5, 'thin', .3), yl = mk(5, 'yellow', .5), cd = mk(5, 'cold', .7), zp = mk(5, 'zap', .85);
    for (let k = 0; k < 4; k++) if (t > dy + k * .6) acidRain(L, t, dy + k * .6, 6);
    setThin(lerp(.25, 1, ease(seg(t, tn, yl + .6))));
    if (t > cd) { sec.ice.visible = true; const k = eout(seg(t, cd, cd + .5)); sec.ice.position.set(lerp(3.5, 1.1, k), lerp(7, 4.6, k), .6); sec.ice.rotation.set(t * 1.5, t, 0); }
    if (t > zp) { const z = .5 + .5 * Math.sin((t - zp) * 30); bolts.forEach(b => b.visible = z > .3); pulpMat.emissiveIntensity = .9 * z; }
    flash = hit(zp, .3);
    blur = whip(5);
    setCam('enam', 'secC', ease(seg(t, a, tn + .5)));
    chip('tn', '📉 เคลือบฟันบางลง', 'red', LB, t, tn, be(5) - .1);
    chip('yl', '🟡 ฟันดูเหลือง', 'yel', LB2, t, yl, be(5) - .1, -2);
    chip('zp', '🥶 ดื่มเย็น เสียวจี๊ด!', 'dark', LB3, t, zp, be(5) - .1, 2);
  } else if (t < be(6)) {                            // fix: fluoride toothpaste + soft brush, gently
    const a = bs(6), d = B[6].dur, ps = mk(6, 'paste', .05), sf = mk(6, 'soft', .35), gn = mk(6, 'gentle', .55), st = mk(6, 'strong', .8);
    setThin(1);
    brush.visible = true; paste.visible = t < st; paste.scale.setScalar(1 - .7 * seg(t, gn, st));
    brush.rotation.set(Math.PI / 2, 0, 0);
    brush.position.set(lerp(-7, 0, eout(seg(t, ps, ps + .5))) + (t > gn ? Math.sin(t * 6) * .6 : 0), 4.9, -.4);
    if (t > sf) { const s = 1 + .08 * Math.sin((t - sf) * 10) * Math.exp(-(t - sf) * 2); brush.scale.setScalar(s); }
    if (t > gn) hardGlow(t, seg(t, gn, st));
    if (t > st) sparkleAt(-.2, 3.7, .3, seg(t, st, st + .9), 2.2);
    blur = whip(6);
    setCam('secC', 'top', ease(seg(t, a, ps + .6)));
    chip('ps', '🪥 ยาสีฟันฟลูออไรด์', 'green', LB, t, ps + .1, be(6) - .1);
    chip('sb', '+ แปรงขนนุ่ม แปรงเบาๆ', 'dark', LB2, t, sf, be(6) - .1, -2);
    chip('st', '💪 เคลือบฟันแข็งแรง', 'green', LB3, t, st, be(6) - .1, 2);
  } else if (t < be(7)) {                            // but eroded enamel never grows back -> sensitive often: see the dentist
    const a = bs(7), d = B[7].dur, gn = mk(7, 'gone', .05), nv = mk(7, 'never', .3), sn = mk(7, 'sens', .55), dt = mk(7, 'dentist', .75);
    setThin(1);
    ghost.material.opacity = .3 * seg(t, gn + .2, nv) * (t > sn ? 1 - seg(t, sn, sn + .4) : 1);
    if (t > nv && t < sn) { warn.material.opacity = .7 * (.5 + .5 * Math.sin((t - nv) * 10)); warn.position.set(0, 3.6, .3); warn.scale.setScalar(.65); }
    if (t > sn) { const z = .5 + .5 * Math.sin((t - sn) * 26); bolts.forEach(b => b.visible = z > .4 && t < dt + .4); pulpMat.emissiveIntensity = t < dt + .4 ? .7 * z : 0; }
    if (t > dt) { mirror.visible = true; const k = eout(seg(t, dt, dt + .6)); mirror.position.set(lerp(6, 1.9, k), lerp(8, 4.6, k), 1.4); mirror.rotation.set(-.4, -.5, lerp(-.8, -.35, k) + .05 * Math.sin(t * 3));
      halo.material.opacity = .22 * eout(seg(t, dt + .3, dt + .8)); halo.position.set(0, 3.4, .5); halo.scale.set(6, 6, 1); }
    blur = whip(7);
    setCam('top', 'enam', ease(seg(t, a, a + .9)));
    if (t > dt - .3) setCam('enam', 'cupW', ease(seg(t, dt - .3, dt + .7)) * .45);
    chip('gn', 'เคลือบฟันที่กร่อนไปแล้ว', 'dark', LB, t, gn + .1, sn - .3);
    chip('nv', '✕ ไม่งอกคืน', 'red', LB2, t, nv, sn - .3, -3);
    chip('sn', 'เสียวฟันบ่อย?', 'yel', LB, t, sn, be(7) - .1);
    chip('dt', '👩‍⚕️ ให้ทันตแพทย์ตรวจ', 'green', LB2, t, dt, be(7) - .1, 2);
  } else if (t < be(8)) {                            // myth: rubbing lemon on teeth whitens them? no — thinner enamel, more yellow
    const a = bs(8), d = B[8].dur, th = mk(8, 'think', .1), rb = mk(8, 'rub', .25), no = mk(8, 'no', .55), tn = mk(8, 'thin', .75);
    setThin(1);
    if (t > rb && t < no + .4) { rubSlice.visible = true; const k = eout(seg(t, rb, rb + .4)); rubSlice.position.set(lerp(4, 0, k) + (t > rb + .4 ? Math.sin(t * 13) * .9 : 0), lerp(8, 3.9, k), 1.9); rubSlice.rotation.set(Math.PI / 2 - .25, 0, t * 2);
      rubSlice.scale.setScalar(1 - ein(seg(t, no, no + .4))); acidRain(L, t, rb + .4, 8); }
    if (t > no) { en.color.set(YEL).lerp(new en.color.constructor('#dcb860'), .6 * seg(t, tn, tn + .8)); }
    if (t > tn) { warn.material.opacity = .7 * (.5 + .5 * Math.sin((t - tn) * 12)); warn.position.set(0, 3.6, .3); warn.scale.setScalar(.6); }
    flash = hit(no, .25);
    blur = whip(8);
    setCam('secC', 'enam', ease(seg(t, a, a + .8)));
    chip('m1', 'มะนาวถูฟัน = ฟันขาว?', 'dark', LB, t, rb, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', LB, t, no, be(8) - .1, -4);
    chip('m3', 'เคลือบฟันบาง → ยิ่งดูเหลือง', 'yel', LB2, t, tn, be(8) - .1, 2);
  } else if (t < be(9)) {                            // payoff
    const a = bs(9), d = B[9].dur;
    L.upper.position.y = lerp(40, 11, eout(seg(t, a + .5, a + 1.5)));
    glass.visible = true; straw.visible = true; bob(t); glass.position.x = CUP[0] + 1.2;
    L.confetti(t, a); sparkleAt(0, 4, 1, seg(t, a, a + .9), 3);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, 3, -1); halo.scale.set(14, 14, 1);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('top', 'gap', ease(seg(t, a, a + d * .8)));
    chip('y1', '🍋 ดื่มมะนาวได้', 'green', 190, t, mk(9, 'drink', .3), be(9) - .1);
    chip('y2', '😁 ฟันปลอดภัย ยิ้มสวย', 'dark', 330, t, mk(9, 'smile', .6), be(9) - .1);
  } else {
    L.upper.position.y = 11; setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: the cut tooth with a glass of lemon water above it, acid drops falling on the enamel
export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt } = L;
  L.upper.position.y = 40;
  glass.visible = true; glass.position.set(2.7, 4.5, .6); glass.rotation.set(0, .3, .2);
  softGlow(t, .8);
  acid.forEach((dp, i) => { if (i > 6) return; dp.visible = true; dp.position.set(dp.userData.x, 4.2 + (i % 3) * .5, dp.userData.z + .4); });
  sparkleAt(2.7, 6.4, .6, (t * .8) % 1, 2);
  const k = clamp(t / 2);
  cam.position.set(lerp(2.6, 2.4, k), lerp(6.4, 6.2, k), lerp(18, 17, k)); cam.lookAt(0.9, 5.9, 0);
  return [
    { text: 'น้ำมะนาว', at: [1.6, 5.8, 0.6], dx: -300, dy: 0 },
    { text: 'กรด!', at: [0.6, 4.6, 0.3], dx: 90, dy: -10 },
    { text: 'เคลือบฟัน', at: [-0.8, 3.4, 0.05], dx: 140, dy: 90 },
  ];
}

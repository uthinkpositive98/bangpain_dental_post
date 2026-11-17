// ep29 ฟันน้ำนมผุ ไม่ต้องรักษา เดี๋ยวก็หลุด? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the jaw cut in half; at x=0 a small baby molar (ฟันน้ำนม) and, deep in the bone under it, the permanent tooth bud
// (หน่อฟันแท้) in its sac. Chain: "it'll fall out anyway?" -> a permanent bud waits underneath, baby molars stay until ~12
// -> thin enamel: decay reaches the pulp fast, pain -> filling / baby-tooth pulp treatment -> if left: infection at the root
// tip (pus) may affect the bud -> extracted too early: neighbours tip into the gap, the bud has no room -> space maintainer
// -> myth: no fluoride for small kids? no — from the first tooth, a smear -> payoff: the permanent tooth erupts straight.
let baby, babyCrown, babyMat, cav, cavF, fil, filF, bud, budRoot, sac, abscess, sm, paste, xMark, rootGerms = [], P0 = {};
const BS = 0.8;            // baby molar scale
const BUD_Y = -7.0;        // bud resting height (inside the bone)

export function setup(L) {
  const { THREE, scene, tooth, canvasTex, rnd } = L;
  // baby molar: a little whiter/bluish enamel, scaled down; emissive used for the "pain" pulse
  babyMat = new THREE.MeshPhysicalMaterial({ color: '#fdfbff', roughness: .22, clearcoat: 1, clearcoatRoughness: .15, emissive: '#000000' });
  baby = tooth(0, true, babyMat); babyCrown = baby.children[0];
  baby.children[1].scale.set(1, .78, 1);                       // shorter roots
  // cavity (top + front) and filling (same places)
  const cm = new THREE.MeshStandardMaterial({ color: '#3d2412', roughness: .85 });
  cav = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 14), cm); baby.add(cav);
  cavF = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 14), cm); baby.add(cavF);
  const fm = new THREE.MeshPhysicalMaterial({ color: '#a8dcff', roughness: .2, clearcoat: 1 });
  fil = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 14), fm); baby.add(fil);
  filF = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 14), fm); baby.add(filF);
  // permanent tooth bud (a full tooth whose root grows at the payoff) + its sac on the cut face
  bud = tooth(0, true); budRoot = bud.children[1];
  sac = new THREE.Mesh(new THREE.CircleGeometry(1, 48), new THREE.MeshStandardMaterial({ color: '#c99878', roughness: .8, transparent: true, opacity: .9 }));
  sac.position.set(0, BUD_Y + 1.1, .012); sac.scale.set(2.5, 2.4, 1); scene.add(sac);
  // abscess glow at the root tip (soft yellow-red, not gory)
  const abTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,214,90,.95)'); gr.addColorStop(.45, 'rgba(255,90,80,.7)'); gr.addColorStop(1, 'rgba(255,60,70,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  abscess = new THREE.Sprite(new THREE.SpriteMaterial({ map: abTex, transparent: true, depthWrite: false })); scene.add(abscess);
  for (let i = 0; i < 8; i++) { const m = new THREE.Mesh(L.germGeo, L.germMat); m.userData = { side: i % 2 ? 1 : -1, d: (i >> 1) * .18, ph: rnd() * 6 }; scene.add(m); rootGerms.push(m); }
  // space maintainer: a steel band around the right neighbour + a wire loop reaching across the gap
  sm = new THREE.Group(); scene.add(sm);
  { const steel = new THREE.MeshStandardMaterial({ color: '#d5dbe2', metalness: 1, roughness: .22 });
    const band = new THREE.Mesh(new THREE.CylinderGeometry(1.78, 1.72, 1.1, 40, 1, true), steel); band.scale.z = .88; band.material.side = THREE.DoubleSide; band.position.set(L.SP, 1.9, 0); sm.add(band);
    const pts = [[L.SP - 1.6, 1.9, 1.0], [1.0, 1.95, 1.25], [-1.3, 1.95, 1.0], [-L.SP + 1.75, 1.9, .5], [-L.SP + 1.75, 1.9, -.5], [-1.3, 1.95, -1.0], [1.0, 1.95, -1.25], [L.SP - 1.6, 1.9, -1.0]].map(p => new THREE.Vector3(...p));
    const wire = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, .13, 10, false), steel); sm.add(wire); }
  // toothpaste smear (thin film on the bristles)
  paste = new THREE.Mesh(new THREE.BoxGeometry(2.2, .12, .5), new THREE.MeshPhysicalMaterial({ color: '#dff4ff', roughness: .3, clearcoat: 1 }));
  L.brush.add(paste); paste.position.set(0, 0, -1.25);
  // a red "X" above the bud (blocked)
  xMark = new THREE.Group(); scene.add(xMark);
  { const xm = new THREE.MeshBasicMaterial({ color: '#ff3b47' }); [1, -1].forEach(s => { const b = new THREE.Mesh(new THREE.BoxGeometry(2.4, .45, .2), xm); b.rotation.z = s * Math.PI / 4; xMark.add(b); }); }
  Object.assign(L.SHOTS, {
    hook: [[5, 6.0, 22], [0, -0.4, 0]],
    all: [[5, -1, 36], [0, -2.4, 0]],         // baby molar + bud together
    budC: [[3.5, -5, 16], [0, -6.6, 0]],
    crownC: [[3.8, 7.5, 17], [0, 0.2, 0]],
    top: [[1.5, 9.5, 12], [0, 1.0, -.3]],
    rootC: [[4, -1, 24], [0, -1.5, 0]],
    row: [[7, 6.5, 30], [0, 0, 0]],             // the three middle teeth, for tipping / maintainer
    cov: [[4, 1.5, 24], [0, -2.2, 0]],
  });
  P0.nl = L.neighbors[2]; P0.nr = L.neighbors[3];
  L.onReset(() => {
    L.centerTooth.visible = false;
    baby.visible = true; baby.position.set(0, .7, 0); baby.rotation.set(0, 0, 0); baby.scale.setScalar(BS);
    babyMat.emissive.set('#000000'); babyMat.emissiveIntensity = 1;
    bud.visible = true; bud.position.set(0, BUD_Y, 0); bud.scale.setScalar(.9); bud.rotation.set(0, 0, 0); budRoot.visible = false; budRoot.scale.set(1, 1, 1);
    sac.visible = true; sac.material.opacity = .9; sac.position.y = BUD_Y + 1.1;
    [cav, cavF, fil, filF, abscess, sm, xMark, paste, ...rootGerms].forEach(o => o.visible = false);
    [P0.nl, P0.nr].forEach((n, i) => { n.rotation.set(0, 0, 0); n.position.set((i ? 1 : -1) * L.SP, .7, 0); });
    L.brush.rotation.set(0, 0, 0); L.brush.scale.setScalar(1);
  });
}

// cavity stage k: 0 = small pit, 1 = deep (pulp)
function setCavity(L, k) {
  cav.visible = cavF.visible = k > 0;
  const r = L.lerp(.35, .95, k);
  cav.position.set(-.35, 2.85, .2); cav.scale.set(r, .35 + .25 * k, r * .8);
  cavF.position.set(-.3, L.lerp(2.25, 1.6, k), 1.32); cavF.scale.set(L.lerp(.3, .75, k), L.lerp(.3, .9, k), .25);
}
function setFilling(L, s, k) {
  fil.visible = filF.visible = s > 0; const b = L.back(s), r = L.lerp(.35, .95, k) * 1.06;
  fil.position.set(-.35, 2.88, .2); fil.scale.set(r * b, (.36 + .25 * k) * b, r * .8 * b);
  filF.position.set(-.3, L.lerp(2.25, 1.6, k), 1.34); filF.scale.set(L.lerp(.32, .78, k) * b, L.lerp(.32, .92, k) * b, .25 * b);
}
// neighbours tip into the gap (k 0..1)
function tip(L, k) { P0.nl.rotation.z = -.32 * k; P0.nl.position.x = -L.SP + .9 * k; P0.nr.rotation.z = .32 * k; P0.nr.position.x = L.SP - .9 * k; }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, warn, halo, brush } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const hit = (h, a = .3) => t > h ? a * Math.exp(-(t - h) * 10) : 0;
  const T1 = 190, T2 = 330, T3 = 470, LB = 1150, LB2 = 1290, LB3 = 1430;
  const budHalo = (k, col) => { halo.material.opacity = k; halo.position.set(0, BUD_Y + 1.3, 1); halo.scale.set(7, 7, 1); halo.material.color.set(col || '#ffffff'); };
  halo.material.color.set('#ffffff');

  if (t < be(0)) {                                   // hook: baby tooth decay — it'll fall out anyway?
    const a = bs(0), d = B[0].dur, cv = mk(0, 'cav', .2), fa = mk(0, 'fall', .5), nw = mk(0, 'new', .7);
    setCavity(L, .25 * eout(seg(t, cv, cv + .6)));
    if (t > fa && t < nw + .2) { baby.rotation.z = Math.sin((t - fa) * 18) * .06 * (1 - seg(t, nw - .2, nw + .2)); }
    L.upper.position.y = lerp(11, 40, ease(seg(t, a, a + 1.2)));
    setCam('wide', 'hook', ease(seg(t, a, a + d * .55)));
    if (t > nw) sparkleAt(0, 4.4, .8, seg(t, nw, nw + .8), 2.4);
    chip('h1', '🦷 ฟันน้ำนมผุ', 'dark', LB, t, cv, be(0) - .1);
    chip('h2', 'เดี๋ยวก็หลุด ไม่ต้องรักษา?', 'yel', LB2, t, fa, be(0) - .1, -2);
  } else if (t < be(1)) {                            // a permanent bud waits under it; baby molars stay until ~12
    const a = bs(1), d = B[1].dur, bd = mk(1, 'bud', .3), hd = mk(1, 'hide', .45), ml = mk(1, 'molar', .6), ag = mk(1, 'age', .85);
    L.upper.position.y = 40; setCavity(L, .25);
    blur = whip(1);
    setCam('hook', 'all', ease(seg(t, a, bd + .3)));
    if (t > bd) { budHalo(.5 * eout(seg(t, bd, bd + .4)) * (1 - .4 * seg(t, ml, ml + .5))); bud.scale.setScalar(.9 * (1 + .06 * Math.sin((t - bd) * 9) * (1 - seg(t, bd, bd + 1.5)))); sparkleAt(0, BUD_Y + 1.3, 1, seg(t, bd, bd + .9), 2.6); }
    if (t > ml) { babyMat.emissive.setRGB(.12 * (1 - seg(t, ag + .6, ag + 1.2)), .1 * (1 - seg(t, ag + .6, ag + 1.2)), 0); }
    if (t > ag) L.calendar('อายุราว', '12', back(seg(t, ag, ag + .35)) * (1 - seg(t, be(1) - .25, be(1))));
    chip('b1', '🌱 หน่อฟันแท้ ซ่อนอยู่ข้างใต้', 'green', 1440, t, bd + .1, be(1) - .1);
    chip('b2', 'ฟันกรามน้ำนม อยู่ถึงราว 12 ขวบ', 'dark', 1580, t, ag, be(1) - .1, -2);
  } else if (t < be(2)) {                            // thin enamel -> decay reaches the pulp fast -> pain
    const a = bs(2), d = B[2].dur, th = mk(2, 'thin', .15), sp = mk(2, 'spread', .4), pn = mk(2, 'pain', .7);
    L.upper.position.y = 40;
    setCavity(L, lerp(.25, 1, ease(seg(t, sp, sp + 1.6))));
    if (t > th && t < sp) babyMat.emissive.setRGB(0, .1 + .08 * Math.sin(t * 10), .2 + .1 * Math.sin(t * 10));
    if (t > pn) { const p = .5 + .5 * Math.sin((t - pn) * 11); babyMat.emissive.setRGB(.45 * p, 0, .05 * p);
      warn.material.opacity = .9 * p; warn.position.set(0, 2.2, 1.4); warn.scale.setScalar(.8 + .06 * p); baby.position.x = Math.sin(t * 45) * .05; }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(pn, .3));
    setCam('all', 'crownC', ease(seg(t, a, a + 1.1)), t > pn ? .08 : 0, t);
    chip('c1', 'เคลือบฟันน้ำนม บางกว่า', 'dark', LB, t, th, be(2) - .1);
    chip('c2', 'ผุลามถึงโพรงประสาท เร็ว!', 'red', LB2, t, sp + .3, be(2) - .1, -2);
    chip('c3', '😣 ปวด กินไม่ได้ นอนไม่หลับ', 'yel', LB3, t, pn, be(2) - .1, 2);
  } else if (t < be(3)) {                            // fix: filling / baby-tooth pulp treatment -> keep chewing
    const a = bs(3), d = B[3].dur, fl = mk(3, 'fill', .15), pp = mk(3, 'pulp', .4), kp = mk(3, 'keep', .7);
    if (t < fl + .3) setCavity(L, 1); else setFilling(L, seg(t, fl + .3, fl + .7), 1);
    if (t > fl + .3) sparkleAt(-.3, 3.2, 1.2, seg(t, fl + .4, fl + 1.2), 2);
    if (t > pp) { babyMat.emissive.setRGB(0, .18 * (1 - seg(t, pp + .8, kp)), .12 * (1 - seg(t, pp + .8, kp))); }
    // chew: the upper jaw comes down onto food
    L.upper.position.y = t < kp ? lerp(40, 11, eout(seg(t, a, a + .6))) : lerp(11, 3.3 + .6, (1 + Math.sin((t - kp) * 9 - Math.PI / 2)) / 2);
    blur = whip(3);
    setCam('crownC', 'top', ease(seg(t, a, fl + .2)));
    if (t > pp) setCam('top', 'hook', ease(seg(t, pp, kp)));
    chip('f1', '👩‍⚕️ อุดฟัน', 'green', LB, t, fl, be(3) - .1);
    chip('f2', 'รักษาโพรงประสาทฟันน้ำนม', 'dark', LB2, t, pp + .1, be(3) - .1);
    chip('f3', '😋 เก็บฟันไว้เคี้ยวต่อ', 'yel', LB3, t, kp, be(3) - .1, 2);
  } else if (t < be(4)) {                            // if left: germs down to the root tip -> pus -> may affect the bud
    const a = bs(4), d = B[4].dur, gm = mk(4, 'germ', .2), ps = mk(4, 'pus', .55), ht = mk(4, 'hit', .75);
    L.upper.position.y = 40; setCavity(L, 1);
    babyMat.emissive.setRGB(.25, 0, .03);
    rootGerms.forEach(g => { const k = seg(t, gm + g.userData.d, gm + 1.3 + g.userData.d); g.visible = k > 0; const s = g.userData.side;
      g.position.set(s * lerp(.4, .75, k), lerp(2.0, -3.4, eout(k)) + Math.sin(t * 6 + g.userData.ph) * .05, .9); g.scale.setScalar(.45); g.rotation.set(t * 3, t * 2 + g.userData.ph, 0); });
    if (t > ps) { abscess.visible = true; const k = eout(seg(t, ps, ps + .9)); abscess.position.set(0, -3.7 - 1.2 * seg(t, ht, ht + .8), 1.0); abscess.scale.setScalar(lerp(.5, 4.2, k) * (1 + .05 * Math.sin(t * 8))); }
    if (t > ht) { warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - ht) * 10)); warn.position.set(0, BUD_Y + 1.3, 1.2); warn.scale.setScalar(1.1); budHalo(.25, '#ff6070'); }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(ht, .2));
    setCam('crownC', 'rootC', ease(seg(t, a, gm + 1)));
    chip('r0', '⏩ ถ้าปล่อยไว้…', 'yel', T1, t, a + .1, gm + .8);
    chip('r1', 'เป็นหนองที่ปลายราก', 'red', T1, t, ps, be(4) - .1);
    chip('r2', '⚠️ อาจกระทบหน่อฟันแท้', 'dark', T2, t, ht, be(4) - .1, -2);
  } else if (t < be(5)) {                            // extracted too early -> neighbours tip in -> no room -> crowding
    const a = bs(5), d = B[5].dur, ot = mk(5, 'out', .2), tl = mk(5, 'tilt', .4), bl = mk(5, 'block', .65), cr = mk(5, 'crowd', .85);
    L.upper.position.y = 40; setCavity(L, 1);
    // the baby tooth gently lifts out and floats away (no blood)
    const ko = ease(seg(t, ot + .2, ot + 1.1)); baby.position.y = .7 + ko * 13; baby.visible = ko < .98; baby.rotation.z = ko * .5;
    if (t > ot + .2 && t < ot + 1.3) sparkleAt(0, 2, 1, seg(t, ot + .2, ot + 1.1), 2.4);
    tip(L, ease(seg(t, tl + .3, tl + 1.5)));
    if (t > bl) { const k = seg(t, bl, bl + .5); bud.position.y = BUD_Y + 1.6 * Math.sin(Math.PI * clamp(k)) * (k < 1 ? 1 : 0); }
    if (t > bl + .3) { xMark.visible = true; xMark.position.set(0, -1.8, 1.5); xMark.scale.setScalar(back(seg(t, bl + .3, bl + .65))); xMark.rotation.z = Math.sin(t * 7) * .05; }
    flash = Math.max(hit(tl + 1.2, .2), hit(bl + .3, .25));
    blur = whip(5);
    setCam('hook', 'row', ease(seg(t, a, ot + 1)));
    if (t > bl - .4) setCam('row', 'all', ease(seg(t, bl - .4, bl + .4)), t > bl + .3 && t < bl + .7 ? .1 : 0, t);
    chip('e1', 'ถอนฟันน้ำนม ก่อนเวลา', 'dark', T1, t, ot, be(5) - .1);
    chip('e2', '↘ ฟันข้างๆ ล้มปิดช่อง ↙', 'red', T2, t, tl + .3, be(5) - .1, -2);
    chip('e3', 'ฟันแท้ไม่มีที่ขึ้น → ซ้อนเก', 'yel', LB3, t, cr - .3, be(5) - .1, 2);
  } else if (t < be(6)) {                            // fix: space maintainer keeps the room
    const a = bs(6), d = B[6].dur, s0 = mk(6, 'sm', .3), sv = mk(6, 'save', .7);
    L.upper.position.y = 40; baby.visible = false;
    tip(L, 1 - ease(seg(t, a, s0)));
    if (t > s0) { sm.visible = true; const k = back(seg(t, s0, s0 + .5)); sm.scale.setScalar(1); sm.position.y = (1 - k) * 6; }
    if (t > sv) { budHalo(.45 * eout(seg(t, sv, sv + .4)), '#a8ffda'); sparkleAt(0, 1.5, 1.2, seg(t, sv, sv + .9), 2.8); bud.position.y = BUD_Y + .6 * eout(seg(t, sv, sv + .8)); }
    flash = Math.max(t < a + .3 ? .5 * (1 - seg(t, a, a + .3)) : 0, hit(s0 + .3, .2));
    setCam('all', 'row', ease(seg(t, a, s0 + .3)));
    if (t > sv - .2) setCam('row', 'all', ease(seg(t, sv - .2, sv + .8)));
    chip('s1', 'เครื่องมือกันช่องว่าง', 'green', T1, t, s0, be(6) - .1);
    chip('s2', '(Space maintainer)', 'dark', T2, t, s0 + .3, be(6) - .1);
    chip('s3', '🅿️ จองที่ไว้ให้ฟันแท้', 'yel', LB3, t, sv, be(6) - .1, 2);
  } else if (t < be(7)) {                            // myth: no fluoride toothpaste for small kids? no — from the first tooth, a smear
    const a = bs(7), d = B[7].dur, no = mk(7, 'no', .4), fs = mk(7, 'first', .55), smr = mk(7, 'smear', .8);
    L.upper.position.y = 40;                         // rewind: a healthy baby tooth again
    brush.visible = t > fs - .3; paste.visible = true;
    brush.position.set(lerp(-9, 0, eout(seg(t, fs - .3, fs + .3))) + (t > fs + .3 ? Math.sin(t * 14) * .7 : 0), 3.9, -.3); brush.rotation.set(Math.PI / 2, 0, 0); brush.scale.setScalar(.85);
    if (t > smr) sparkleAt(0, 3.5, 1, ((t - smr) * 1.3) % 1, 2);
    flash = Math.max(t < a + .3 ? .6 * (1 - seg(t, a, a + .3)) : 0, hit(no, .25));
    blur = whip(7);
    setCam('hook', 'top', ease(seg(t, fs - .4, fs + .5)));
    chip('m1', 'เด็กเล็ก ห้ามใช้ฟลูออไรด์?', 'dark', LB, t, a + .3, no - .05);
    chip('m2', '✕ ไม่ใช่นะ!', 'red', LB, t, no, be(7) - .1, -4);
    chip('m3', '🪥 ใช้ได้ตั้งแต่ฟันซี่แรก', 'green', LB2, t, fs, be(7) - .1);
    chip('m4', 'แค่แตะขนแปรงพอเปียก', 'yel', LB3, t, smr, be(7) - .1, 2);
  } else if (t < be(8)) {                            // payoff: healthy baby tooth -> it sheds, the permanent tooth erupts straight
    const a = bs(8), d = B[8].dur, er = mk(8, 'erupt', .45);
    const ko = ease(seg(t, er - .2, er + .5)); baby.position.y = .7 + ko * 13; baby.visible = ko < .98;
    const ku = ease(seg(t, er, er + 1.3)); bud.position.y = lerp(BUD_Y, .7, ku); bud.scale.setScalar(lerp(.9, 1, ku));
    budRoot.visible = ku > .05; budRoot.scale.set(1, Math.max(.05, ku), 1); sac.material.opacity = .9 * (1 - ku);
    L.upper.position.y = lerp(40, 11, eout(seg(t, er + 1, er + 1.8)));
    L.confetti(t, a); if (t > er + .9) sparkleAt(0, 4, 1, seg(t, er + .9, er + 1.7), 3);
    halo.material.opacity = .3 * eout(seg(t, a, a + .6)); halo.position.set(0, 3, -1); halo.scale.set(14, 14, 1);
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    setCam('hook', 'all', ease(seg(t, a, er)));
    if (t > er) setCam('all', 'gap', ease(seg(t, er, er + 1.6)));
    chip('y1', '🎉 ฟันน้ำนมแข็งแรง', 'green', T1, t, a + .3, be(8) - .1);
    chip('y2', '😁 ฟันแท้มีที่ขึ้น', 'dark', T2, t, er, be(8) - .1);
  } else {                                           // under the end card: the permanent tooth in place
    baby.visible = false; bud.position.y = .7; bud.scale.setScalar(1); budRoot.visible = true; sac.visible = false; L.upper.position.y = 11; setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: a decayed baby molar with the permanent bud waiting underneath
export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt, halo } = L;
  L.upper.position.y = 40;
  setCavity(L, .6);
  halo.material.opacity = .4; halo.position.set(0, -5.0, 1); halo.scale.set(6, 6, 1);
  sparkleAt(0, -5.0, 1, (t * .8) % 1, 2.2);
  const k = clamp(t / 2);
  bud.position.y = -6.3; sac.position.y = -5.2;
  cam.position.set(lerp(4.6, 4.2, k), lerp(3.2, 3.0, k), lerp(31, 30, k)); cam.lookAt(0, 2.5, 0);
  return [
    { text: 'ฟันน้ำนมผุ', at: [1.0, 2.6, 1.2], dx: 160, dy: 0 },
    { text: 'หน่อฟันแท้', at: [1.2, -5.0, 0.6], dx: 160, dy: 0 },
  ];
}

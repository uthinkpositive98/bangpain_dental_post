// ep15 ปล่อยฟันคุดไว้ จะเกิดอะไรขึ้น? — cut3d episode (L = tools/cut3d/lib.js)
// Set: the jaw ends at the second molar (x = -SP); the impacted wisdom tooth sits at x≈0.4, tilted toward it (mesioangular).
let xray, wt, flap, flapMat, foodBits = [], decay, filling, cyst, redGlow, melt = [], spreadGlows = [];
const WX = -0.1, TILT = 1.0, Y_IMPACTED = -3.9, Y_PARTIAL = -1.1;

export function setup(L) {
  const { THREE, scene, tooth, gumMatTop, canvasTex, rnd } = L;
  wt = tooth(WX); wt.rotation.z = TILT;
  flapMat = gumMatTop.clone();
  flap = new THREE.Mesh(new THREE.SphereGeometry(1.3, 40, 20, 0, Math.PI * 2, 0, Math.PI / 2), flapMat);
  flap.position.set(-0.85, L.GUM_TOP - .05, 0.3); flap.scale.set(1.15, .5, 1); flap.castShadow = true; scene.add(flap);
  const fm = [new THREE.MeshStandardMaterial({ color: '#e9c98f', roughness: .7 }), new THREE.MeshStandardMaterial({ color: '#b97a3c', roughness: .7 })];
  for (let i = 0; i < 16; i++) { const m = new THREE.Mesh(new THREE.DodecahedronGeometry(.13 + rnd() * .1), fm[i % 2]);
    m.userData = { to: new THREE.Vector3(-2.4 + rnd() * 1.9, L.GUM_TOP + .1 + rnd() * .55, .7 + rnd() * .8), from: new THREE.Vector3(-1 + (rnd() - .5) * 10, 12 + rnd() * 4, 3), d: rnd() * .5 };
    scene.add(m); foodBits.push(m); }
  decay = new THREE.Mesh(new THREE.SphereGeometry(.55, 24, 16), new THREE.MeshStandardMaterial({ color: '#4a2f1a', roughness: .8 }));
  decay.position.set(-2.12, 2.05, .9); decay.scale.set(.5, 1, 1); scene.add(decay);
  filling = new THREE.Mesh(new THREE.SphereGeometry(.58, 24, 16), new THREE.MeshPhysicalMaterial({ color: '#eaf4ff', roughness: .2, clearcoat: 1 }));
  filling.position.copy(decay.position); filling.scale.set(.52, 1, 1); scene.add(filling);
  cyst = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24), new THREE.MeshPhysicalMaterial({ color: '#6fbdf0', transparent: true, opacity: .62, roughness: .1, clearcoat: 1, emissive: '#2f86c4', emissiveIntensity: .45, depthWrite: false }));
  cyst.position.set(-0.5, -2.7, .9); scene.add(cyst);
  const redTex = canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,60,70,.95)'); gr.addColorStop(1, 'rgba(255,60,70,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  const mkGlow = () => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: redTex, transparent: true, depthWrite: false })); scene.add(s); return s; };
  redGlow = mkGlow();
  for (let i = 0; i < 8; i++) { const s = mkGlow(); s.userData = { dir: i < 4 ? 1 : -1, d: (i % 4) * .25, y: L.GUM_TOP + .2 + (i % 2) * .5 }; spreadGlows.push(s); }
  const mm = new THREE.MeshStandardMaterial({ color: '#f1e2bd', roughness: .6, transparent: true });
  for (let i = 0; i < 14; i++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(.08 + rnd() * .06, 0), mm); m.userData = { o: new THREE.Vector3(-2.75 + rnd() * .35, -2.4 + rnd() * 1.4, .9), v: new THREE.Vector3(.6 + rnd(), .5 + rnd(), .3), d: rnd() }; scene.add(m); melt.push(m); }
  L.germs.forEach(g => { g.userData.to.x -= 1.1; });
  // real X-ray look: dark film, dim bone, glowing teeth (swapped in/out each frame)
  const film = new THREE.Color('#0b1419');
  const xBone = new THREE.MeshBasicMaterial({ map: L.bone.material[4].map, color: '#4d5c66' }), xBoneSide = new THREE.MeshBasicMaterial({ color: '#2c363d' });
  const xGum = new THREE.MeshBasicMaterial({ color: '#1a2329' });
  const keep = { bone: L.bone.material, gum: L.gum.material, bg: scene.background, fog: scene.fog };
  xray = on => {
    L.bone.material = on ? [xBoneSide, xBoneSide, xBoneSide, xBoneSide, xBone, xBoneSide] : keep.bone;
    L.gum.material = on ? xGum : keep.gum;
    scene.background = on ? film : keep.bg; scene.fog = on ? null : keep.fog;
    L.enamel.emissive.set(on ? '#dcefff' : '#000000'); L.enamel.emissiveIntensity = on ? .85 : 1;
    L.rootMat.emissive.set(on ? '#a9c3d6' : '#000000'); L.rootMat.emissiveIntensity = on ? .7 : 1;
  };
  Object.assign(L.SHOTS, {
    wideL: [[12, 10, 44], [-2, 0, 0]],
    wt: [[3, 5, 19], [-1.6, 0.4, 0]],
    wtTop: [[4, 8, 15], [-1.3, 1.5, 0]],
    wtC: [[3, 3.4, 11.5], [-2.0, 1.4, 0]],
    wtRoot: [[2.5, 0, 13], [-2.3, -1.5, 0]],
    wtBone: [[3.5, -0.4, 22], [-1.0, -2.6, 0]],
  });
  L.onReset(() => {
    xray(false);
    L.neighbors.slice(3).forEach(n => n.visible = false);      // the jaw ends behind the wisdom tooth
    L.centerTooth.visible = false; L.upper.position.y = 40;
    wt.visible = true; wt.position.set(WX, Y_IMPACTED, 0); wt.rotation.set(0, 0, TILT); wt.scale.setScalar(1);
    [flap, decay, filling, cyst, redGlow, ...foodBits, ...melt, ...spreadGlows].forEach(o => o.visible = false);
    flap.scale.set(1.15, .5, 1); flapMat.color.set('#ee8399'); L.inflam.scale.set(1, .8, 1); L.inflam.position.x = -1.0; L.inflamF.position.x = -1.0;
  });
}


export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt, germs, inflam, inflamF, warn, halo, brush } = L;
  let blur = 0, flash = 0, filter = '';
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  // persistent "built so far" state ---------------------------------------------------------
  const bumpT = mk(1, 'bump', .5), foodT = mk(2, 'food', .35), decayT = mk(4, 'decay', .7);
  const outT = mk(10, 'out', 0), safeT = mk(10, 'safe', .45);
  const risen = eout(seg(t, bs(1) + .2, bumpT));
  wt.position.y = lerp(Y_IMPACTED, Y_PARTIAL, risen);
  if (t > bumpT && t < bumpT + .5) wt.position.x = WX + Math.sin((t - bumpT) * 40) * .06 * (1 - seg(t, bumpT, bumpT + .5));
  const showFlap = t >= bs(2) && t < outT + .4;
  if (showFlap) { flap.visible = true; const k = back(seg(t, bs(2) + .05, bs(2) + .45)); flap.scale.set(1.15 * k, .5 * k, 1 * k); }
  const showFood = t >= foodT && t < bs(8);
  if (showFood) foodBits.forEach(f => { const k = eout(seg(t, foodT + f.userData.d * .6, foodT + .5 + f.userData.d * .6)); f.visible = true; f.position.lerpVectors(f.userData.from, f.userData.to, k); });
  if (t >= decayT && t < safeT) { decay.visible = true; const k = eout(seg(t, decayT, decayT + .8)); decay.scale.set(.5 * k, k, k); }
  if (t >= safeT) { filling.visible = true; filling.scale.set(.52 * back(seg(t, safeT, safeT + .4)), back(seg(t, safeT, safeT + .4)), 1); }

  if (t < be(0)) {                                   // hook: hidden under the gum
    const a = bs(0), d = B[0].dur;
    warn.material.opacity = t > a + .6 ? .85 * (.55 + .45 * Math.sin(t * 7)) : 0; warn.position.set(-1.35, -3.0, 1.5); warn.scale.setScalar(.85);
    setCam('wideL', 'wt', ease(seg(t, a + .5, a + d)));
    chip('q', 'ไม่ปวด = ไม่เป็นไร?', 'dark', 190, t, a + .9, be(0) - .1);
  } else if (t < be(1)) {                            // last molar, stuck behind the one in front -> half erupted
    const a = bs(1);
    if (t > bumpT) flash = .2 * Math.exp(-(t - bumpT) * 10);
    setCam('wt', 'wt', 0, t > bumpT && t < bumpT + .4 ? .12 : 0, t);
    chip('last', 'ฟันกรามซี่สุดท้าย', 'dark', 190, t, a + .3, bumpT - .05);
    chip('stuck', '💥 ติดฟันซี่ข้างหน้า!', 'red', 190, t, bumpT, be(1) - .1, -3);
  } else if (t < be(2)) {                            // gum flap traps food; the brush can't reach
    const a = bs(2), d = B[2].dur, bt = mk(2, 'brush', .65);
    const bk = seg(t, bt, be(2) - .1);
    if (bk > 0 && bk < 1) { brush.visible = true; const hit = Math.abs(Math.sin(bk * Math.PI * 3));
      brush.position.set(lerp(-3.2, -.6, hit), L.GUM_TOP + 1.6 + (hit > .95 ? .08 * Math.sin(t * 80) : 0), 2.1); brush.rotation.set(0, 0, .15); }
    setCam('wtTop', 'wtTop', 0);
    chip('pocket', 'ซอกเก็บเศษอาหาร', 'yel', 190, t, foodT + .2, be(2) - .1);
    chip('nobrush', '🪥 แปรงไม่ถึง!', 'red', 320, t, bt + .4, be(2) - .1, 3);
  } else if (t < be(3)) {                            // germs -> pericoronitis
    const a = bs(3), d = B[3].dur, sw = mk(3, 'swell', .4);
    L.germsArrive(t, a + .05);
    const k = seg(t, sw, sw + .8);
    flapMat.color.set('#ee8399').lerp(new L.THREE.Color('#e0475f'), k); const s = 1 + .25 * k + .03 * Math.sin(t * 8) * k; flap.scale.set(1.15 * s, .5 * s, s);
    inflam.material.opacity = .55 * k; inflamF.material.opacity = .45 * k;
    setCam('wtTop', 'wt', ease(seg(t, a + d * .5, a + d)));
    chip('peri', 'เหงือกอักเสบรอบฟันคุด', 'red', 190, t, mk(3, 'term', .7), be(3) - .1);
  } else if (t < be(4)) {                            // the good neighbour decays
    const a = bs(4);
    germs.forEach(g => { g.visible = true; g.position.copy(g.userData.to); g.rotation.set(t * 2, t, 0); });
    flapMat.color.set('#e0475f'); flap.scale.set(1.4, .62, 1.25); inflam.material.opacity = .55; inflamF.material.opacity = .45;
    warn.material.opacity = t > decayT ? .8 * (.5 + .5 * Math.sin((t - decayT) * 12)) : 0; warn.position.set(-2.12, 2.05, 1.35); warn.scale.setScalar(.45);
    blur = whip(4);
    setCam('wt', 'wtC', ease(seg(t, a, a + 1.2)));
    chip('rot', 'ฟันข้างเคียงผุ', 'red', 190, t, decayT, be(4) - .1);
  } else if (t < be(5)) {                            // root of the neighbour resorbs
    const a = bs(5), mt = mk(5, 'melt', .5);
    redGlow.visible = true; redGlow.position.set(-2.5, -1.7, 1.1); const p = .5 + .5 * Math.sin(t * 7); redGlow.scale.set(2.2 + p, 2.2 + p, 1); redGlow.material.opacity = .55 + .3 * p;
    melt.forEach(m => { const k = seg(t, mt + m.userData.d * .6, mt + 1.4 + m.userData.d * .6); m.visible = k > 0 && k < 1; m.position.copy(m.userData.o).addScaledVector(m.userData.v, k * 1.6); m.material.opacity = 1 - k; });
    blur = whip(5);
    setCam('wtRoot', 'wtRoot', 0, t > mt && t < mt + .3 ? .06 : 0, t);
    chip('res', 'รากฟันข้างเคียงละลาย', 'red', 190, t, mt, be(5) - .1);
  } else if (t < be(6)) {                            // infection spreads
    const a = bs(6), d = B[6].dur, sp = mk(6, 'spread', .2);
    germs.forEach(g => { g.visible = true; g.position.copy(g.userData.to); g.rotation.set(t * 2, t, 0); });
    flapMat.color.set('#e0475f'); flap.scale.set(1.4, .62, 1.25);
    const k = eout(seg(t, sp, sp + 1.6));
    inflam.scale.set(1 + 2.4 * k, .8 + 1.4 * k, 1); inflam.material.opacity = .55; inflamF.material.opacity = .45 + .2 * k;
    spreadGlows.forEach(s => { const kk = seg(t, sp + s.userData.d, sp + 1.4 + s.userData.d); s.visible = kk > 0; s.position.set(s.userData.dir * (1 + 7 * kk) - 1.1, s.userData.y, 1.2); s.scale.set(2.4, 1.6, 1); s.material.opacity = .8 * (1 - kk * .6); });
    warn.material.opacity = .7 * (.5 + .5 * Math.sin(t * 12)); warn.position.set(-1.2, 1.5, 1.4); warn.scale.setScalar(1.1 + .4 * k);
    setCam('wt', 'wideL', ease(seg(t, sp, sp + 1.5)));
    chip('sp', '⚠ ติดเชื้อลาม หน้าบวม', 'red', 190, t, sp, be(6) - .1, -2);
    chip('doc', 'รีบพบทันตแพทย์', 'dark', 330, t, mk(6, 'doc', .65), be(6) - .1);
  } else if (t < be(7)) {                            // rare: a cyst grows in the bone
    const a = bs(7), ct = mk(7, 'cyst', .45);
    if (t > ct) { cyst.visible = true; const k = eout(seg(t, ct, ct + 1.6)); const s = .2 + 2.1 * k + .04 * Math.sin(t * 5); cyst.scale.set(s, s * .85, s * .7); }
    blur = whip(7);
    setCam('wtBone', 'wtBone', 0);
    chip('cy', 'ถุงน้ำ (พบได้น้อย)', 'yel', 190, t, ct, be(7) - .1);
  } else if (t < be(8)) {                            // myth twist: not every one needs removing
    const a = bs(8), d = B[8].dur, no = mk(8, 'no', .6);
    blur = whip(8);
    setCam('wideL', 'wt', ease(seg(t, a, a + d)) * .4);
    chip('m1', 'ฟันคุดทุกซี่ต้องผ่า?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่เสมอไป!', 'red', 330, t, no, be(8) - .1, -4);
  } else if (t < be(9)) {                            // X-ray decides
    const a = bs(9), xt = mk(9, 'xray', .1), kt = mk(9, 'keep', .55), rt = mk(9, 'remove', .78);
    if (t > xt) { xray(true); flap.visible = false; foodBits.forEach(f => f.visible = false); flash = .55 * Math.exp(-(t - xt) * 9); filter = 'saturate(.5)'; }
    warn.material.opacity = t > rt ? .9 * (.5 + .5 * Math.sin((t - rt) * 12)) : 0; warn.position.set(-1.3, -.4, 1.4); warn.scale.setScalar(1.4);
    setCam('wt', 'wideL', ease(seg(t, a, a + .8)) * .35);
    chip('x', '🩻 เอกซเรย์ดูท่าฟันคุด', 'dark', 190, t, xt, be(9) - .1);
    chip('k', '✓ ขึ้นตรง ทำความสะอาดได้ → เก็บไว้ได้', 'green', 330, t, kt, be(9) - .1);
    chip('r', '✕ นอนเอียง ชนฟัน → ควรเอาออก', 'red', 450, t, rt, be(9) - .1);
  } else if (t < be(10)) {                           // payoff: the troublemaker comes out, neighbour fixed
    const a = bs(10), d = B[10].dur;
    if (t > outT) { const k = ein(seg(t, outT, outT + .8)); wt.position.y = Y_PARTIAL + 14 * k; wt.rotation.z = TILT - k * 2; if (k >= 1) wt.visible = false;
      sparkleAt(-1.2, 1.4, 0, seg(t, outT + .1, outT + .8), 2.6); }
    if (t > safeT) sparkleAt(-2.15, 2.1, .4, seg(t, safeT, safeT + .7), 1.8);
    L.confetti(t, safeT);
    setCam('wt', 'wideL', ease(seg(t, safeT, safeT + d * .6)));
  } else {                                           // under the end card
    wt.visible = false; setCam('wideL', 'wideL', 0);
  }
  return { blur, flash, filter };
}

export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt, germs, warn, inflam, inflamF } = L;
  wt.position.y = Y_PARTIAL; flap.visible = true; flap.scale.set(1.3, .58, 1.15); flapMat.color.set('#e8687f');
  germs.forEach((g, i) => { g.visible = i % 2 === 0; g.position.copy(g.userData.to); g.position.y += Math.sin(t * 5 + i) * .08; g.rotation.set(t * 2 + i, t, 0); });
  inflam.material.opacity = .4; inflamF.material.opacity = .3;
  warn.material.opacity = .85 * (.6 + .4 * Math.sin(t * 6)); warn.position.set(-2.3, .6, 1.5); warn.scale.setScalar(.7);
  const k = clamp(t / 2);
  cam.position.set(lerp(4.6, 4.2, k), lerp(8.8, 8.6, k), lerp(19.5, 18.3, k)); cam.lookAt(-1.0, 4.7, 0);
  return [
    { text: 'ฟันคุด', at: [0.2, -1.4, 1], dx: 70 },
    { text: 'เหงือกคลุม', at: [0.4, 1.7, 0], dx: 60 },
    { text: 'ฟันข้างเคียง', at: [-2.4, 3.9, 0], dx: 60, dy: -30 },
  ];
}

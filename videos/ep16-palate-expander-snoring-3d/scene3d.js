// ep16 ขยายขากรรไกรบนโดยไม่ผ่าตัด ช่วยเรื่องนอนกรนได้ยังไง — cut3d episode with its own set:
// a CORONAL (front) cut of the head: nasal cavity + septum on top, the palate (= nasal floor) split at the midpalatal
// suture into two halves that can move apart, upper molars on both sides, tongue, lower jaw. Cut face at z = 0.
let halves = [], septum, fill, bridge, sutureGlow, floorGlow, lower, tongue, device, rod, key, pins = [], air = [], mouthAir = [], rings = [], xray;
const EXP = 1.35;                 // how far each half moves out when fully expanded

export function setup(L) {
  const { THREE, scene, tooth, canvasTex, rnd, gumMatTop, enamel } = L;
  const boneMap = L.bone.material[4].map.clone(); boneMap.wrapS = boneMap.wrapT = THREE.RepeatWrapping; boneMap.needsUpdate = true;
  const capMat = new THREE.MeshStandardMaterial({ map: boneMap, color: '#f3dfb6', roughness: .85 });
  const sideMat = new THREE.MeshStandardMaterial({ color: '#d9bf8f', roughness: .9 });
  const pink = new THREE.MeshStandardMaterial({ color: '#ee8399', roughness: .5 });
  const extrude = (pts, depth) => { const sh = new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1])));
    const g = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: false, curveSegments: 6 }); g.translate(0, 0, -depth);
    const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * .09, uv.getY(i) * .09); return g; };
  const R = [[0, 0], [1.5, -.15], [3.2, 0], [4.1, -.9], [4.5, -1.5], [5.5, -1.5], [5.9, -.6], [6.5, 2.6], [6.1, 6.6], [2.4, 6.6], [2.8, 5.2], [3.1, 2.6], [2.6, 1.2], [.9, 1.05], [0, 1.05]];
  const gumR = [[0, 0], [1.5, -.15], [3.2, 0], [4.1, -.9], [4.5, -1.5], [4.6, -1.85], [4.0, -1.25], [3.1, -.38], [1.5, -.5], [0, -.36]];
  for (const s of [1, -1]) {
    const g = new THREE.Group(); scene.add(g);
    const pts = R.map(([x, y]) => [x * s, y]); const gp = gumR.map(([x, y]) => [x * s, y]);
    if (s < 0) { pts.reverse(); gp.reverse(); }
    const m = new THREE.Mesh(extrude(pts, 9), [capMat, sideMat]); m.castShadow = m.receiveShadow = true; g.add(m);
    const gm = new THREE.Mesh(extrude(gp, 9), pink); g.add(gm);
    const t = tooth(4.95 * s); g.add(t); t.position.set(4.95 * s, -1.25, 0); t.rotation.set(Math.PI, 0, .1 * s);
    halves.push(g);
  }
  // cavities' back wall (inside of nose and mouth)
  const back = new THREE.Mesh(new THREE.PlaneGeometry(12.6, 14.6), new THREE.MeshStandardMaterial({ color: '#9b4558', roughness: .9 }));
  back.position.set(0, -.7, -8.9); back.material.color.set('#7d3446'); scene.add(back);
  septum = new THREE.Mesh(new THREE.BoxGeometry(.38, 5.55, 9), new THREE.MeshStandardMaterial({ color: '#ecd4ad', roughness: .8 }));
  septum.position.set(0, 1.05 + 5.55 / 2, -4.5); scene.add(septum);
  fill = new THREE.Mesh(new THREE.BoxGeometry(1, .95, 9), new THREE.MeshStandardMaterial({ color: '#f6e6c4', roughness: .8, transparent: true }));
  fill.position.set(0, .55, -4.5); scene.add(fill);
  bridge = new THREE.Mesh(new THREE.BoxGeometry(.5, .95, 9.02), new THREE.MeshStandardMaterial({ color: '#c79f63', roughness: .8 }));
  bridge.position.set(0, .55, -4.5); scene.add(bridge);
  const glowMat = c => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0, depthWrite: false });
  sutureGlow = new THREE.Mesh(new THREE.PlaneGeometry(.22, 1.05), glowMat('#ffe14d')); sutureGlow.position.set(0, .52, .03); scene.add(sutureGlow);
  floorGlow = new THREE.Mesh(new THREE.PlaneGeometry(5.4, .16), glowMat('#ffe14d')); floorGlow.position.set(0, 1.12, .03); scene.add(floorGlow);
  // lower jaw (moves down for mouth breathing)
  lower = new THREE.Group(); scene.add(lower);
  const LJ = [[-7.2, -12], [7.2, -12], [7.2, -7.6], [6.9, -7.3], [4.7, -7.3], [4.4, -7.9], [-4.4, -7.9], [-4.7, -7.3], [-6.9, -7.3], [-7.2, -7.6]];
  const lj = new THREE.Mesh(extrude(LJ, 9), [capMat, sideMat]); lower.add(lj);
  for (const s of [1, -1]) { const t = tooth(5.85 * s); lower.add(t); t.position.set(5.85 * s, -7.45, 0); t.rotation.set(0, 0, -.06 * s);
    const gg = new THREE.Mesh(new THREE.BoxGeometry(2.6, .35, 9), pink); gg.position.set(5.8 * s, -7.25, -4.5); lower.add(gg); }
  tongue = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), new THREE.MeshPhysicalMaterial({ color: '#e5677f', roughness: .45, clearcoat: .5 }));
  tongue.castShadow = true; scene.add(tongue);
  // expander: bands on the upper molars + arms + a split body with a screw between the halves
  const steel = L.titanium;
  device = new THREE.Group(); scene.add(device);
  for (const [i, s] of [[0, 1], [1, -1]]) {
    const part = new THREE.Group(); halves[i].add(part); part.userData.dev = true;
    const band = new THREE.Mesh(new THREE.CylinderGeometry(1.62, 1.62, .9, 40, 1, true), steel); band.position.set(4.95 * s, -2.1, 0); part.add(band);
    const body = new THREE.Mesh(new L.RoundedBoxGeometry(1.1, .55, 2.0, 3, .12), steel); body.position.set(.62 * s, -.62, -.4); part.add(body);
    for (const dz of [-1.1, .5]) { const a = new THREE.Mesh(new THREE.CylinderGeometry(.09, .09, 1, 10), steel);
      const p0 = new THREE.Vector3(.9 * s, -.62, dz - .2), p1 = new THREE.Vector3(3.55 * s, -1.9, dz); a.position.copy(p0).add(p1).multiplyScalar(.5);
      a.scale.y = p0.distanceTo(p1); a.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p1.clone().sub(p0).normalize()); part.add(a); }
    for (const dz of [-1.6, .9]) { const pin = new THREE.Mesh(new THREE.CylinderGeometry(.12, .07, 1.6, 12), new THREE.MeshStandardMaterial({ color: '#8fd0ff', metalness: .8, roughness: .25 }));
      pin.position.set(.62 * s, .1, dz - .4); pin.userData = { y: .1 }; halves[i].add(pin); pins.push(pin); }
  }
  rod = new THREE.Mesh(new THREE.CylinderGeometry(.16, .16, 1, 16), new THREE.MeshStandardMaterial({ color: '#9aa3ad', metalness: 1, roughness: .35 }));
  rod.rotation.z = Math.PI / 2; rod.position.set(0, -.62, -.4); scene.add(rod);
  key = new THREE.Group(); scene.add(key);
  { const k1 = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, 3.2, 8), steel); k1.rotation.x = Math.PI / 2; k1.position.z = 1.6; key.add(k1);
    const k2 = new THREE.Mesh(new THREE.TorusGeometry(.45, .08, 8, 24), new THREE.MeshStandardMaterial({ color: '#2EC4B6', roughness: .4 })); k2.position.z = 3.4; key.add(k2); }
  key.position.set(0, -.62, .7);
  // air: nose stream + mouth stream (move into the screen, -z)
  const airMat = new THREE.MeshBasicMaterial({ color: '#bfe9ff', transparent: true, opacity: .9 });
  for (let i = 0; i < 70; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.09, 8, 6), airMat); m.userData = { side: i % 2 ? 1 : -1, u: rnd(), v: rnd(), ph: rnd(), sp: .7 + rnd() * .6 }; scene.add(m); air.push(m); }
  for (let i = 0; i < 30; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.1, 8, 6), new THREE.MeshBasicMaterial({ color: '#ffd1d9', transparent: true, opacity: .9 })); m.userData = { u: rnd(), v: rnd(), ph: rnd(), sp: .8 + rnd() * .5 }; scene.add(m); mouthAir.push(m); }
  const ringTex = canvasTex(128, 128, g => { g.strokeStyle = 'rgba(255,255,255,.95)'; g.lineWidth = 10; g.beginPath(); g.arc(64, 64, 50, 0, 7); g.stroke(); });
  for (let i = 0; i < 4; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: ringTex, color: '#ffe0e6', transparent: true, depthWrite: false })); scene.add(s); rings.push(s); }
  // background + X-ray mode
  const bg = canvasTex(16, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#9fd3ee'); gr.addColorStop(1, '#fde9dc'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const film = new THREE.Color('#0b1419'), xCap = new THREE.MeshBasicMaterial({ map: boneMap, color: '#56656f' }), xSide = new THREE.MeshBasicMaterial({ color: '#2c363d' }), xSoft = new THREE.MeshBasicMaterial({ color: '#141c21' });
  const swaps = [];
  scene.traverse(o => { if (o.isMesh && (o.material === capMat || (Array.isArray(o.material) && o.material[0] === capMat))) swaps.push([o, o.material, [xCap, xSide]]);
    if (o.isMesh && o.material === pink) swaps.push([o, o.material, xSoft]); });
  swaps.push([back, back.material, xSoft], [tongue, tongue.material, xSoft], [septum, septum.material, xSide]);
  xray = on => { swaps.forEach(([o, m, x]) => o.material = on ? x : m); scene.background = on ? film : bg; scene.fog = null;
    enamel.emissive.set(on ? '#dcefff' : '#000000'); enamel.emissiveIntensity = on ? .85 : 1; L.rootMat.emissive.set(on ? '#a9c3d6' : '#000000'); L.rootMat.emissiveIntensity = on ? .7 : 1; };
  Object.assign(L.SHOTS, {
    face: [[0, -1, 52], [0, -1.6, -3]],
    faceR: [[13, 1.5, 48], [0, -1.6, -3]],
    nose: [[0, 5.5, 27], [0, 3.2, -3]],
    palate: [[0, -5.5, 23], [0, -.9, -3]],
    suture: [[3.5, -3, 16], [0, .2, -2]],
    mouth: [[0, -2.5, 31], [0, -3.2, -3]],
  });
  L.onReset(() => {
    xray(false);
    [L.bone, L.gum, L.centerTooth, ...L.neighbors].forEach(o => o.visible = false); L.upper.visible = false;
    halves.forEach((h, i) => { h.position.set(0, 0, 0); h.children.forEach(c => { if (c.userData.dev) c.visible = false; }); });
    pins.forEach(p => p.visible = false); rod.visible = false; key.visible = false;
    [fill, bridge].forEach(o => o.visible = false); sutureGlow.material.opacity = 0; floorGlow.material.opacity = 0;
    lower.position.set(0, 0, 0); tongue.position.set(0, -4.6, -4.4); tongue.scale.set(4.0, 2.4, 4.4); tongue.rotation.set(0, 0, 0);
    [...air, ...mouthAir, ...rings].forEach(o => o.visible = false);
  });
}

// ---------------------------------------------------------------- helpers
function setWidth(w) { halves[0].position.x = EXP * w; halves[1].position.x = -EXP * w; }
function showDevice(on, w, pinK = 0) {
  halves.forEach(h => h.children.forEach(c => { if (c.userData.dev) c.visible = on; }));
  rod.visible = on; rod.scale.y = 1.0 + 2 * EXP * w;
  pins.forEach((p, i) => { p.visible = pinK > 0; p.position.y = .1 - 1.4 * (1 - pinK); p.rotation.y = pinK * 12; });
}
function flowAir(t, L, rate, w, tint = 0) {   // rate 0..1: how much air gets through the nose
  const n = Math.round(air.length * rate);
  air.forEach((m, i) => { const u = m.userData; m.visible = i < n; if (!m.visible) return;
    const k = ((t * u.sp * (0.35 + rate * .65) + u.ph) % 1);
    const wx = .45 + u.u * (1.9 + 1.2 * w), x = u.side * (wx + EXP * w * .6);
    m.position.set(x, 1.5 + u.v * 4.6, 2.5 - k * 11.5); m.material.color.set(tint ? '#ff9aa8' : '#bfe9ff'); });
}
function mouthFlow(t, on) { mouthAir.forEach(m => { const u = m.userData; m.visible = on; if (!on) return; const k = ((t * u.sp + u.ph) % 1); m.position.set((u.u - .5) * 4, -2.4 - u.v * 1.2, 3 - k * 11); }); }
function snore(t, t0, L) { rings.forEach((r, i) => { const k = ((t - t0) * .9 + i / rings.length) % 1; r.visible = t > t0; const s = .8 + k * 4.5; r.scale.set(s, s, 1); r.position.set(0, -3.6, -6.5); r.material.opacity = (1 - k) * .8; }); }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, back, lerp, clamp, setCam, chip, sparkleAt } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const i = L.beatAt(t);
  // width of the upper jaw over the story
  let w = 0, dev = false, pinK = 0, fillA = 0, bridgeOn = false, tongueUp = 0, tongueDrop = 0, mouthOpen = 0, noseRate = .22, snoreOn = false, tint = 1;
  if (i === 4) { const s0 = mk(4, 'split', .55), b0 = mk(4, 'bone', .8); w = .6 * ease(seg(t, s0, b0)); dev = t > mk(4, 'device', .25); fillA = seg(t, b0, b0 + .8); }
  if (i === 5) { bridgeOn = t < mk(5, 'many', .75); dev = true; pinK = eout(seg(t, mk(5, 'so', .4), mk(5, 'so', .4) + .9)); w = ease(seg(t, mk(5, 'many', .75), be(5) - .1)); }
  if (i >= 6) { w = 1; fillA = 1; dev = i < 9; pinK = i < 9 ? 1 : 0; noseRate = 1; tint = 0; tongueUp = i === 6 ? eout(seg(t, mk(6, 'tongue', .6), mk(6, 'tongue', .6) + .9)) : 1; }
  if (i === 2) { mouthOpen = eout(seg(t, mk(2, 'mouth', .25), mk(2, 'mouth', .25) + .5)); tongueDrop = eout(seg(t, mk(2, 'tongue', .5), mk(2, 'tongue', .5) + .6)); snoreOn = t > mk(2, 'snore', .8); }
  if (i === 3) { tongueDrop = 1; mouthOpen = 1 - seg(t, bs(3), bs(3) + .6); }
  if (i === 0) { tongueDrop = 1; mouthOpen = .6; snoreOn = true; }
  setWidth(w); showDevice(dev, w, pinK);
  if (fillA > 0) { fill.visible = true; fill.scale.x = Math.max(.01, 2 * EXP * w); fill.material.opacity = fillA; }
  bridge.visible = bridgeOn;
  lower.position.y = -1.1 * mouthOpen;
  tongue.position.y = -4.6 - 1.0 * tongueDrop + 1.6 * tongueUp - 1.0 * mouthOpen; tongue.rotation.x = -.3 * tongueDrop;
  tongue.scale.set(4.0 + .5 * tongueUp, 2.4, 4.4);
  flowAir(t, L, noseRate, w, tint); mouthFlow(t, mouthOpen > .5);
  if (snoreOn) snore(t, i === 0 ? bs(0) : mk(2, 'snore', .8), L);

  if (i === 0) {                                     // hook: snoring, mouth open
    setCam('face', 'faceR', ease(seg(t, bs(0), be(0))));
    chip('zz', '😪 ครอก~ ฟี้~', 'dark', 190, t, bs(0) + .3, be(0) - .1, -3);
  } else if (i === 1) {                              // palate = floor of the nose; narrow jaw = narrow nose
    const nz = mk(1, 'nose', .3), nr = mk(1, 'narrow', .6);
    floorGlow.material.opacity = t > nz ? .85 * (.6 + .4 * Math.sin(t * 8)) : 0;
    if (t > nr) { const k = Math.sin((t - nr) * 30) * .04 * (1 - seg(t, nr, nr + .6)); halves[0].position.x = -k; halves[1].position.x = k; }
    setCam('face', 'nose', ease(seg(t, bs(1), nz + .6)));
    chip('pf', 'เพดานปาก = พื้นจมูก', 'yel', 190, t, nz, be(1) - .1);
    chip('nr', 'ขากรรไกรบนแคบ → จมูกแคบ', 'red', 320, t, nr, be(1) - .1);
  } else if (i === 2) {                              // nose blocked -> mouth breathing, tongue drops -> snore
    blur = whip(2);
    setCam('nose', 'mouth', ease(seg(t, mk(2, 'mouth', .25) - .2, mk(2, 'mouth', .25) + .8)));
    chip('mb', 'อ้าปากหายใจ', 'dark', 190, t, mk(2, 'mouth', .25), be(2) - .1);
    chip('tg', 'ลิ้นตกไปด้านหลัง', 'red', 320, t, mk(2, 'tongue', .5), be(2) - .1);
    chip('sn', '😪 เสียงกรน', 'yel', 450, t, mk(2, 'snore', .8), be(2) - .1, 3);
  } else if (i === 3) {                              // the midpalatal suture
    const sm = mk(3, 'seam', .45);
    sutureGlow.material.opacity = t > sm ? .9 * (.6 + .4 * Math.sin(t * 9)) : 0;
    blur = whip(3);
    setCam('mouth', 'suture', ease(seg(t, bs(3), sm + .4)));
    chip('st', 'รอยต่อกลางเพดาน', 'yel', 190, t, mk(3, 'term', .7), be(3) - .1);
  } else if (i === 4) {                              // child: expander + turning the screw, the suture opens, bone fills in
    const tn = mk(4, 'turn', .45), s0 = mk(4, 'split', .55), b0 = mk(4, 'bone', .8);
    if (t > tn && t < b0) { key.visible = true; key.rotation.z = (t - tn) * 6; }
    sutureGlow.material.opacity = t < s0 ? .7 : 0;
    if (t > b0) sparkleAt(0, .5, .3, seg(t, b0, b0 + .8), 1.6);
    setCam('suture', 'palate', ease(seg(t, bs(4), mk(4, 'device', .25) + .5)));
    chip('kid', '👧 เด็ก: รอยต่อยังไม่ปิด', 'green', 190, t, bs(4) + .1, be(4) - .1);
    chip('turn', '🔧 หมุนสกรูทีละนิด', 'dark', 320, t, tn, be(4) - .1);
    chip('bone', 'กระดูกงอกมาเติม', 'yel', 450, t, b0, be(4) - .1);
  } else if (i === 5) {                              // adult: fused -> mini-screws (MARPE) -> expands
    const so = mk(5, 'so', .4), many = mk(5, 'many', .75);
    if (t < so) { const k = Math.sin(t * 40) * .03; halves[0].position.x += k; halves[1].position.x -= k; }
    if (Math.abs(t - many) < .1) flash = .35;
    blur = whip(5);
    setCam('palate', 'palate', 0, t < so && t > bs(5) + .6 ? .05 : 0, t);
    chip('ad', '🧑 ผู้ใหญ่: รอยต่อปิดแล้ว 🔒', 'red', 190, t, bs(5) + .2, so - .05);
    chip('mp', 'MARPE (มาร์พ) = หมุดยึดในกระดูก', 'dark', 190, t, mk(5, 'term', .55), be(5) - .1);
    chip('ns', '✓ หลายคนไม่ต้องผ่าตัด', 'green', 320, t, many, be(5) - .1);
  } else if (i === 6) {                              // wider floor -> air flows, tongue has room
    blur = whip(6);
    setCam('palate', 'face', ease(seg(t, bs(6), bs(6) + B[6].dur * .6)));
    chip('af', '🌬️ ลมผ่านจมูกสะดวก', 'green', 190, t, mk(6, 'nose', .1), be(6) - .1);
    chip('tr', 'ลิ้นมีที่วาง ไม่ขวางคอ', 'dark', 320, t, mk(6, 'tongue', .6), be(6) - .1);
  } else if (i === 7) {                              // myth: not every snore
    const no = mk(7, 'no', .45);
    setCam('face', 'faceR', ease(seg(t, bs(7), be(7))) * .6);
    chip('m1', 'กรนทุกแบบแก้ได้?', 'dark', 190, t, bs(7) + .2, no - .05);
    chip('m2', '✕ ไม่ใช่!', 'red', 330, t, no, be(7) - .1, -4);
    chip('m3', 'ทอนซิล • น้ำหนัก • จมูก', 'yel', 190, t, mk(7, 'causes', .65), be(7) - .1);
  } else if (i === 8) {                              // check first: X-ray + sleep test
    const xt = mk(8, 'xray', .2);
    if (t > xt) { xray(true); flash = .5 * Math.exp(-(t - xt) * 9); }
    setCam('faceR', 'face', ease(seg(t, bs(8), be(8))));
    chip('x', '🩻 เอกซเรย์ดูขากรรไกร', 'dark', 190, t, xt, be(8) - .1);
    chip('sl', '😴 + ตรวจการนอนหลับ', 'green', 320, t, mk(8, 'sleep', .55), be(8) - .1);
  } else if (i === 9) {                              // payoff
    L.confetti(t, bs(9));
    sparkleAt(0, 3, 0, seg(t, bs(9), bs(9) + 1), 3.5);
    setCam('nose', 'face', ease(seg(t, bs(9), be(9))));
    chip('ok', '😌 หายใจโล่ง', 'green', 190, t, bs(9) + .3, be(9) - .1);
  } else {
    setCam('face', 'face', 0);
  }
  return { blur, flash };
}

export function cover(t, L) {
  const { lerp, clamp, cam, sparkleAt } = L;
  setWidth(1); showDevice(true, 1, 1); fill.visible = true; fill.scale.x = 2 * EXP; fill.material.opacity = 1;
  tongue.position.set(0, -3.0, -4.4); tongue.scale.set(4.5, 2.4, 4.4);
  flowAir(t, L, 1, 1, 0);
  sutureGlow.material.opacity = 0; floorGlow.material.opacity = .7 + .3 * Math.sin(t * 6);
  const k = clamp(t / 2);
  cam.position.set(lerp(8, 7, k), lerp(-1, -1, k), lerp(44, 41, k)); cam.lookAt(0, 4.6, -3);
  return [
    { text: 'โพรงจมูก', at: [2.2, 4.4, 0], dx: 60 },
    { text: 'พื้นจมูก', at: [2.4, 1.15, 0], dx: 60 },
    { text: 'เครื่องมือขยาย', at: [1.2, -.9, .5], dx: 70, dy: 30 },
  ];
}

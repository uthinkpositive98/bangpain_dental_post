// ep22 หลังถอนฟัน 24 ชม. แรก อย่าทำ 5 อย่างนี้ — cut3d episode (L = tools/cut3d/lib.js)
// The x=0 tooth is pulled out; its socket shows on the cut face (z=0) and as a hole on top of the gum.
// A glossy blood clot fills the socket (clipped by a rising level plane). The 5 don'ts each threaten the clot:
// rinsing (water swirl), straw (suction), smoking (smoke), heat/alcohol/exercise (oozing blood), tongue/brush.
// Then dry socket (clot pops out, pale bone), the do's (gauze bite, ice pack, soft food, pills), the myth
// (a little blood in saliva is normal), salt-water after 24 h, and the payoff: the gum closes over a healed socket.
let P, levelPlane, sockFace, clotFace, clotMat, voidMat, hole, dome, gauze, straw, cig, ember, ice, pill, chili, tongue, drops = [], water = [], smoke = [], steam = [], rim, gumCap;
const GT = 1.2;                                   // gum top (L.GUM_TOP)
const SOCK = [[-1.36, GT], [-1.38, .2], [-1.5, -1.0], [-1.34, -2.6], [-1.12, -4.2], [-.92, -5.25], [-.66, -5.45], [-.44, -5.2], [-.36, -3.2], [-.3, -1.7],
  [0, -1.35], [.3, -1.7], [.36, -3.2], [.44, -5.2], [.66, -5.45], [.92, -5.25], [1.12, -4.2], [1.34, -2.6], [1.5, -1.0], [1.38, .2], [1.36, GT]];

function shape(THREE, pts, k = 1) { const s = new THREE.Shape(); pts.forEach(([x, y], i) => { const X = x * k, Y = y; i ? s.lineTo(X, Y) : s.moveTo(X, Y); }); s.closePath(); return s; }
function softTex(L, rgba) { return L.canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, rgba(1)); gr.addColorStop(.5, rgba(.45)); gr.addColorStop(1, rgba(0)); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }); }

export function setup(L) {
  const { THREE, scene, rnd, canvasTex, RoundedBoxGeometry } = L;
  L.renderer.localClippingEnabled = true;
  P = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);          // keep z <= 0 (behind the cut face)
  levelPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), -6); // keep y <= level (clot fill level); constant = level
  // socket on the cut face: dark empty hole, then the clot over it
  // textures mapped onto the socket's own (x, y) coordinates: x -1.6..1.6, y -5.6..1.3
  const fitUV = tex => { tex.repeat.set(1 / 3.2, 1 / 6.9); tex.offset.set(.5, 5.6 / 6.9); return tex; };
  const clotTex = fitUV(canvasTex(256, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, '#5a0a12'); gr.addColorStop(.25, '#9a1a26'); gr.addColorStop(.55, '#b4232f'); gr.addColorStop(.8, '#8a1420'); gr.addColorStop(1, '#4e0810'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${40 + rnd() * 60},0,${rnd() * 10},${rnd() * .25})`; g.beginPath(); g.arc(rnd() * w, rnd() * h, 2 + rnd() * 9, 0, 7); g.fill(); }
    for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(255,170,180,${.08 + rnd() * .18})`; g.beginPath(); g.ellipse(rnd() * w, rnd() * h, 1 + rnd() * 4, 3 + rnd() * 10, rnd() * 3, 0, 7); g.fill(); } }));
  const voidTex = fitUV(canvasTex(256, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, '#1e0507'); gr.addColorStop(.5, '#4a1016'); gr.addColorStop(1, '#1e0507'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }));
  const lamina = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, SOCK.map(([x, y]) => [x * 1.09, y < -5 ? y - .14 : y]))), new THREE.MeshStandardMaterial({ color: '#bf9a66', roughness: .8 }));
  lamina.position.z = .008; scene.add(lamina); L.onReset(() => lamina.visible = false);
  voidMat = new THREE.MeshStandardMaterial({ map: voidTex, roughness: .8 });
  sockFace = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, SOCK)), voidMat); sockFace.position.z = .012; scene.add(sockFace);
  sockFace.onBeforeRender = () => { lamina.visible = true; };
  clotMat = new THREE.MeshPhysicalMaterial({ map: clotTex, roughness: .18, clearcoat: 1, clearcoatRoughness: .08, sheen: .5, sheenColor: new THREE.Color('#ff7080'), clippingPlanes: [levelPlane] });
  clotFace = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, SOCK.map(([x, y]) => [x * .9, y > GT - .01 ? GT + .02 : y + .08]))), clotMat); clotFace.position.z = .02; scene.add(clotFace);
  // pale bone rim shown in a dry socket
  rim = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, SOCK.map(([x, y]) => [x * .9, y > GT - .01 ? GT + .02 : y + .08]))), new THREE.MeshStandardMaterial({ color: '#efe1c2', roughness: .85, transparent: true, opacity: 0 })); rim.position.z = .024; scene.add(rim);
  // hole on top of the gum + clot dome (both clipped at the cut face)
  hole = new THREE.Mesh(new THREE.CircleGeometry(1.36, 48), new THREE.MeshStandardMaterial({ color: '#3a0b10', roughness: .8, clippingPlanes: [P] }));
  hole.rotation.x = -Math.PI / 2; hole.position.set(0, GT + .012, -1.25); hole.scale.set(1, .95, 1); scene.add(hole);
  dome = new THREE.Mesh(new THREE.SphereGeometry(1.26, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshPhysicalMaterial({ color: '#7e0f1c', roughness: .2, clearcoat: 1, clearcoatRoughness: .1, sheen: .4, sheenColor: new THREE.Color('#ff6070'), clippingPlanes: [P], clipShadows: true }));
  dome.position.set(0, GT, -1.2); dome.scale.set(1, .3, .94); dome.castShadow = true; scene.add(dome);
  // gum closing over the socket (payoff)
  gumCap = new THREE.Mesh(new THREE.SphereGeometry(1.4, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), L.gumMatTop.clone()); gumCap.material.clippingPlanes = [P];
  gumCap.position.set(0, GT - .02, -1.2); scene.add(gumCap);
  // gauze roll: woven white texture
  const weave = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#fbfbf7'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(170,170,160,.45)'; g.lineWidth = 2;
    for (let i = 0; i < w; i += 9) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, h); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(w, i); g.stroke(); } });
  weave.wrapS = weave.wrapT = THREE.RepeatWrapping; weave.repeat.set(2, 2);
  gauze = new THREE.Mesh(new RoundedBoxGeometry(2.9, 1.5, 2.7, 6, .6), new THREE.MeshStandardMaterial({ map: weave, roughness: .95 }));
  gauze.castShadow = true; scene.add(gauze);
  // drinking straw: white with red stripes, open tube
  const stripes = canvasTex(64, 512, (g, w, h) => { g.fillStyle = '#ffffff'; g.fillRect(0, 0, w, h); g.fillStyle = '#ef4a5c'; for (let y = -64; y < h + 64; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y + 40); g.lineTo(w, y + 64); g.lineTo(0, y + 24); g.fill(); } });
  straw = new THREE.Mesh(new THREE.CylinderGeometry(.42, .42, 12, 32, 1, true), new THREE.MeshPhysicalMaterial({ map: stripes, roughness: .3, clearcoat: .6, side: THREE.DoubleSide }));
  straw.castShadow = true; scene.add(straw);
  // cigarette: paper body, orange filter, glowing ember
  cig = new THREE.Group(); scene.add(cig);
  { const body = new THREE.Mesh(new THREE.CylinderGeometry(.3, .3, 4.2, 24), new THREE.MeshStandardMaterial({ color: '#f7f4ec', roughness: .7 })); body.position.y = .9; cig.add(body);
    const filt = new THREE.Mesh(new THREE.CylinderGeometry(.31, .31, 1.6, 24), new THREE.MeshStandardMaterial({ color: '#d98a3c', roughness: .65 })); filt.position.y = 3.8; cig.add(filt);
    ember = new THREE.Mesh(new THREE.CylinderGeometry(.3, .26, .35, 24), new THREE.MeshStandardMaterial({ color: '#ff5a1f', emissive: '#ff3a00', emissiveIntensity: 1.6, roughness: .5 })); ember.position.y = -1.33; cig.add(ember); }
  // ice pack (frosted blue), capsule pill, red chili
  ice = new THREE.Mesh(new RoundedBoxGeometry(4.2, 1.2, 3.0, 6, .5), new THREE.MeshPhysicalMaterial({ color: '#9ad8ff', roughness: .25, transmission: .35, thickness: 1, clearcoat: 1, transparent: true, opacity: .95 })); scene.add(ice);
  pill = new THREE.Group(); scene.add(pill);
  { const a = new THREE.Mesh(new THREE.CapsuleGeometry(.42, .6, 8, 20), new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .25, clearcoat: 1 })); a.position.y = -.3; a.scale.y = .5;
    const b = new THREE.Mesh(new THREE.CapsuleGeometry(.42, .6, 8, 20), new THREE.MeshPhysicalMaterial({ color: '#2ec4b6', roughness: .25, clearcoat: 1 })); b.position.y = .3; b.scale.y = .5; pill.add(a, b); }
  chili = new THREE.Group(); scene.add(chili);
  { const pts = []; for (let i = 0; i <= 20; i++) { const k = i / 20; pts.push(new THREE.Vector2(Math.sin(k * Math.PI) * .55 * (1 - k * .55) + .02, k * 3.6)); }
    const body = new THREE.Mesh(new THREE.LatheGeometry(pts, 32), new THREE.MeshPhysicalMaterial({ color: '#e0201f', roughness: .2, clearcoat: 1 })); body.rotation.z = .25; chili.add(body);
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(.12, .2, .9, 12), new THREE.MeshStandardMaterial({ color: '#3f8a2c', roughness: .6 })); stem.position.set(-.85, 3.7, 0); stem.rotation.z = .8; chili.add(stem); }
  // tongue: soft pink capsule with a centre groove sheen
  tongue = new THREE.Mesh(new THREE.CapsuleGeometry(1.5, 5, 12, 32), new THREE.MeshPhysicalMaterial({ color: '#e7818f', roughness: .45, clearcoat: .5, sheen: .6, sheenColor: new THREE.Color('#ffc0c8') }));
  tongue.rotation.x = Math.PI / 2; tongue.scale.set(1.25, 1, .55); scene.add(tongue);
  // particles: blood drops, water droplets, smoke and steam puffs
  const dm = new THREE.MeshPhysicalMaterial({ color: '#a3101f', roughness: .15, clearcoat: 1 });
  for (let i = 0; i < 14; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.16 + rnd() * .12, 16, 12), dm); m.userData = { a: rnd() * 6.28, d: rnd(), v: .6 + rnd() * .8 }; scene.add(m); drops.push(m); }
  const wm = new THREE.MeshPhysicalMaterial({ color: '#bfe8ff', roughness: .05, transmission: .6, thickness: .5, transparent: true, opacity: .8, clearcoat: 1 });
  for (let i = 0; i < 46; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.12 + rnd() * .14, 14, 10), wm); m.userData = { a: rnd() * 6.28, r: 1 + rnd() * 2.6, y: rnd() * 1.6, s: 2 + rnd() * 3 }; scene.add(m); water.push(m); }
  const smokeTex = softTex(L, a => `rgba(190,190,195,${a * .75})`), steamTex = softTex(L, a => `rgba(255,255,255,${a * .8})`);
  for (let i = 0; i < 16; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, transparent: true, depthWrite: false })); s.userData = { d: rnd(), x: rnd() - .5 }; scene.add(s); smoke.push(s); }
  for (let i = 0; i < 10; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: steamTex, transparent: true, depthWrite: false })); s.userData = { d: rnd(), x: rnd() - .5 }; scene.add(s); steam.push(s); }
  Object.assign(L.SHOTS, {
    sock: [[3.2, 1.2, 17.5], [0, -1.6, 0]],      // the whole socket on the cut face
    sockC: [[2.6, 3.4, 11.5], [0, .4, 0]],       // socket top + clot, close
    sockTop: [[2.4, 9.5, 9.5], [0, 1.2, -1.2]],  // looking down into the gum hole
    side: [[1.2, 5.6, 23], [2.0, 1.6, 0]],         // socket left of centre, room for props on the right
  });
  L.onReset(() => {
    L.centerTooth.visible = true;
    [gauze, straw, cig, ice, pill, chili, tongue, ...drops, ...water, ...smoke, ...steam].forEach(o => o.visible = false);
    [sockFace, clotFace, hole, dome].forEach(o => o.visible = false); rim.material.opacity = 0; gumCap.visible = false;
    levelPlane.constant = 6; dome.position.set(0, GT, -1.2); dome.scale.set(1, .3, .94); dome.rotation.set(0, 0, 0); clotMat.color.set('#ffffff'); dome.material.color.set('#7e0f1c');
    voidMat.color.set('#ffffff');
  });
}

export function frame(t, L) {
  const { bs, be, mk, B, T, seg, ease, eout, ein, back, lerp, clamp, SP, setCam, chip, sparkleAt, centerTooth: ct, upper, warn, halo, brush, inflam, inflamF, confetti } = L;
  let blur = 0, flash = 0;
  const whip = i => (t < bs(i) + .35 ? (1 - seg(t, bs(i), bs(i) + .35)) * 13 : 0);
  const outT = mk(0, 'out', .25), clotT = mk(1, 'blood', .2), popT = mk(7, 'pop', .3);
  // --- socket + clot state helpers
  const socket = () => { ct.visible = false; sockFace.visible = true; hole.visible = true; };
  const clotFull = () => { clotFace.visible = true; dome.visible = true; levelPlane.constant = GT + .1; };
  const wobble = (amp, f = 9) => { const w = Math.sin(t * f) * amp; dome.scale.set(1 + w, .3 - w * 1.4, .94 + w); };
  const num = (id, n, t0, t1) => chip(id, `ข้อ ${n}`, 'yel', 175, t, t0, t1, -3);
  const badX = (id, text, y, t0, t1) => chip(id, '✕ ' + text, 'red', y, t, t0, t1);

  if (t < be(0)) {                                   // hook: the tooth comes out
    const a = bs(0), d = B[0].dur, k = seg(t, outT, outT + .9);
    upper.position.y = 40;
    if (k > 0) { ct.position.set(lerp(0, 2.5, k), .7 + 13 * eout(k), lerp(0, 3, k)); ct.rotation.set(-k * .8, k * 2.5, -k * 1.2); ct.visible = k < 1;
      sockFace.visible = hole.visible = true; if (k < .25) flash = .25 * (1 - k * 4); }
    if (t > outT + .4) { clotFace.visible = true; levelPlane.constant = lerp(-5.5, -3.8, eout(seg(t, outT + .4, be(0)))); }
    if (t > mk(0, 'h24', .7)) L.calendar('ช่วงสำคัญ', '24 ชม.', back(seg(t, mk(0, 'h24', .7), mk(0, 'h24', .7) + .35)));
    setCam('gap', 'sock', ease(seg(t, outT + .2, be(0))));
    chip('h1', '🦷 ถอนฟันเสร็จ = จบ?', 'dark', 330, t, a + .2, mk(0, 'no', .4) - .05);
    chip('h2', '✕ ยังค่ะ!', 'red', 330, t, mk(0, 'no', .4), be(0) - .1, -4);
  } else if (t < be(1)) {                            // the blood clot = the wound's plaster
    const a = bs(1), d = B[1].dur, ck = mk(1, 'clot', .5);
    socket(); clotFace.visible = true;
    levelPlane.constant = lerp(-3.8, GT + .1, ease(seg(t, a, ck + .3)));
    if (t > ck) { dome.visible = true; const k = back(seg(t, ck, ck + .5)); dome.scale.set(1, .3 * k, .94); halo.material.opacity = .35 * Math.sin(seg(t, ck, be(1)) * Math.PI); halo.position.set(0, GT + .4, 1); halo.scale.set(6, 4, 1); }
    L.calendar('ช่วงสำคัญ', '24 ชม.', t < a + .3 ? 1 - seg(t, a, a + .3) : 0.0001);
    blur = whip(1);
    setCam('sock', 'sockC', ease(seg(t, ck - .3, be(1))));
    chip('c1', '🩸 ลิ่มเลือด (Blood Clot)', 'yel', 190, t, ck + .1, be(1) - .1);
    chip('c2', '🩹 เหมือนพลาสเตอร์ปิดแผล', 'green', 320, t, mk(1, 'plaster', .7), be(1) - .1);
  } else if (t < be(2)) {                            // soft clot · don't #1: rinse hard / gargle
    const a = bs(2), d = B[2].dur, sp = mk(2, 'spit', .45);
    socket(); clotFull();
    if (t < sp) wobble(.04 * Math.sin(seg(t, a, sp) * Math.PI));
    if (t > sp - .2) { const k = seg(t, sp - .2, be(2)), lift = Math.sin(k * Math.PI);
      water.forEach(m => { const u = m.userData, ang = u.a + t * u.s; m.visible = true; m.position.set(Math.cos(ang) * u.r, GT + .3 + u.y * .7 + Math.sin(t * 3 + u.a) * .2, -1.2 + Math.sin(ang) * u.r * .9); });
      wobble(.06 * lift, 14); dome.position.y = GT + .35 * lift; dome.rotation.z = Math.sin(t * 7) * .12 * lift;
      warn.material.opacity = .75 * lift * (.5 + .5 * Math.sin(t * 14)); warn.position.set(0, GT + .2, 1); warn.scale.set(1, .6, 1); }
    blur = whip(2);
    setCam('sockC', 'sockTop', ease(seg(t, sp - .5, sp + .6)));
    chip('s1', 'ลิ่มเลือดยังนิ่ม หลุดง่าย', 'dark', 320, t, a + .2, be(2) - .1);
    num('n1', 1, mk(2, 'n1', .45), be(2) - .1);
    badX('x1', 'บ้วนปากแรงๆ / กลั้วคอ', 450, sp, be(2) - .1);
  } else if (t < be(3)) {                            // don't #2: straws — suction pulls the clot up
    const a = bs(3), d = B[3].dur, st = mk(3, 'straw', .3), pl = mk(3, 'pull', .45);
    socket(); clotFull();
    straw.visible = true; const k = seg(t, a, st + .2);
    straw.position.set(0, lerp(16, GT + 6.6, eout(k)), -1.2); straw.rotation.set(0, t * .3, 0);
    const suck = Math.sin(seg(t, pl, be(3) - .2) * Math.PI);
    if (t > pl) { dome.position.y = GT + 1.3 * suck; dome.scale.set(1 - .25 * suck, .3 + 1.1 * suck, .94 - .2 * suck); levelPlane.constant = GT + .1 - 1.6 * suck;
      for (let i = 0; i < 6; i++) { const m = water[i]; m.visible = true; const p = ((t * 1.6 + i / 6) % 1); m.position.set(Math.sin(i * 2) * .25, GT + 2 + p * 4, -1.2); m.scale.setScalar(.5); }
      warn.material.opacity = .75 * suck; warn.position.set(0, GT + 1.4, 1); warn.scale.set(.8, .8, 1); }
    blur = whip(3);
    setCam('sockTop', 'sockC', ease(seg(t, a, a + d * .6)), suck > .5 ? .04 : 0, t);
    num('n2', 2, mk(3, 'n2', .3), be(3) - .1);
    badX('x2', 'ดูดหลอด', 320, st, be(3) - .1);
    chip('s2', '⬆ แรงดูด ดึงลิ่มเลือดหลุด', 'dark', 450, t, pl + .2, be(3) - .1);
  } else if (t < be(4)) {                            // don't #3: smoking
    const a = bs(4), d = B[4].dur, sm = mk(4, 'smoke', .3);
    socket(); clotFull();
    cig.visible = true; const k = seg(t, a, a + .6);
    cig.position.set(lerp(9, 3.4, eout(k)), GT + 3.4, .5); cig.rotation.set(0, 0, 1.15);
    ember.material.emissiveIntensity = 1.4 + .6 * Math.sin(t * 9);
    smoke.forEach(s => { const p = ((t - sm) * .55 + s.userData.d) % 1; s.visible = t > sm - .3; const ex = 1.95, ey = GT + 2.0;
      s.position.set(lerp(ex, s.userData.x * .8, p), lerp(ey, GT + .5, p) + Math.sin(p * 6 + s.userData.d * 6) * .3, lerp(.6, -1.2, p)); s.scale.setScalar(1 + p * 2.6); s.material.opacity = Math.sin(p * Math.PI) * .9; });
    const dark = seg(t, sm, be(4)); dome.material.color.set('#7e0f1c').lerp(new L.THREE.Color('#4a1a14'), dark * .6); clotMat.color.set('#ffffff').lerp(new L.THREE.Color('#8a6a5a'), dark * .6);
    blur = whip(4);
    setCam('side', 'sockC', ease(seg(t, sm, be(4))));
    num('n3', 3, mk(4, 'n3', .3), be(4) - .1);
    badX('x3', 'สูบบุหรี่', 320, a + .4, be(4) - .1);
    chip('s3', '🐢 แผลหายช้า', 'dark', 450, t, mk(4, 'slow', .5), be(4) - .1);
  } else if (t < be(5)) {                            // don't #4: alcohol, very hot / spicy food, hard exercise → bleeding
    const a = bs(5), d = B[5].dur, ht = mk(5, 'hot', .3), bl = mk(5, 'bleed', .3);
    socket(); clotFull();
    chili.visible = t > ht; { const k = back(seg(t, ht, ht + .5)); chili.position.set(2.5, GT + 3.0 + .2 * Math.sin(t * 3), 3); chili.rotation.set(.3, t * .8, -.6); chili.scale.setScalar(Math.max(.001, k) * .9); }
    steam.forEach(s => { const p = ((t - ht) * .7 + s.userData.d) % 1; s.visible = t > ht; s.position.set(2.5 + s.userData.x * 1.2, GT + 6.2 + p * 3, 3); s.scale.setScalar(.8 + p * 1.8); s.material.opacity = Math.sin(p * Math.PI) * .8; });
    if (t > bl) drops.forEach(m => { const p = ((t - bl) * m.userData.v + m.userData.d) % 1; m.visible = true; const r = .9 + .6 * p;
      m.position.set(Math.cos(m.userData.a) * r, GT + .45 - p * .35, -1.2 + Math.sin(m.userData.a) * r * .8); m.scale.setScalar(.6 + p); });
    if (t > bl) { inflam.material.opacity = .35 * seg(t, bl, bl + .6); inflam.position.set(0, GT + .02, -1.4); }
    const beat = t > mk(5, 'gym', .3) ? Math.max(0, Math.sin(t * 9)) : 0; dome.scale.set(1 + beat * .04, .3 + beat * .04, .94 + beat * .04);
    blur = whip(5);
    setCam('side', 'sockC', ease(seg(t, bl - .4, be(5))));
    num('n4', 4, mk(5, 'n4', .3), be(5) - .1);
    badX('x4a', 'เหล้า / อาหารร้อนจัด เผ็ดจัด', 320, ht, be(5) - .1);
    badX('x4b', 'ออกกำลังหนัก', 450, mk(5, 'gym', .3), be(5) - .1);
    chip('s4', '🩸 เลือดออกง่ายขึ้น', 'dark', 580, t, bl + .1, be(5) - .1);
  } else if (t < be(6)) {                            // don't #5: tongue / fingers / toothbrush on the wound
    const a = bs(6), d = B[6].dur, tg = mk(6, 'tongue', .2), br = mk(6, 'brush', .2);
    socket(); clotFull();
    if (t < br) { tongue.visible = true; const k = seg(t, tg - .2, tg + .7), poke = Math.max(0, Math.sin((t - tg) * 7)) * seg(t, tg + .4, tg + .6);
      tongue.position.set(0, GT + 1.7 - .35 * poke, lerp(-12, -5.9, eout(k)) + .5 * poke); if (poke > .5) wobble(.05, 16); }
    else { const k = seg(t, br, be(6) - .2); brush.visible = true; brush.position.set(Math.sin(k * Math.PI * 4) * 2.4, GT + 2.2, -.4); brush.rotation.set(.2, 0, Math.sin(t * 30) * .05);
      if (Math.abs(Math.sin(k * Math.PI * 4)) < .3) { wobble(.05, 18); warn.material.opacity = .7; warn.position.set(0, GT + .3, 1); warn.scale.set(1, .6, 1); } }
    blur = whip(6);
    setCam('sockTop', 'side', ease(seg(t, a, a + d * .7)));
    num('n5', 5, mk(6, 'n5', .3), be(6) - .1);
    badX('x5a', 'เอาลิ้น / นิ้วดุนแผล', 320, tg, be(6) - .1);
    badX('x5b', 'แปรงโดนแผล', 450, br, be(6) - .1);
  } else if (t < be(7)) {                            // dry socket: clot lost, bone exposed, severe pain on day 2–3
    const a = bs(7), d = B[7].dur, bn = mk(7, 'bone', .3), pn = mk(7, 'pain', .3);
    socket();
    const k = seg(t, popT, popT + .8);
    if (k < 1) { clotFull(); dome.position.set(lerp(0, -3, k), GT + 9 * eout(k) - 4 * k * k, lerp(-1.2, 2, k)); dome.rotation.set(k * 5, 0, k * 3); levelPlane.constant = lerp(GT + .1, -5.6, ease(k)); }
    else { clotFace.visible = true; levelPlane.constant = -5.6; }
    if (t > bn) { rim.material.opacity = .95 * seg(t, bn, bn + .5); voidMat.color.set('#ffffff').lerp(new L.THREE.Color('#ffe6c0'), seg(t, bn, bn + .6)); }
    if (t > pn) { warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - pn) * 16)); warn.position.set(0, -1.6, .6); warn.scale.set(1.15, 2.6, 1); inflam.material.opacity = .45; inflam.position.set(0, GT + .02, -1.4); flash = .2 * Math.max(0, Math.sin((t - pn) * 8)) * seg(t, pn, pn + .3);
      L.calendar('หลังถอน (วัน)', '2–3', back(seg(t, pn, pn + .35))); }
    if (k > 0 && k < .3) flash = .3;
    setCam('sockC', 'sock', ease(seg(t, popT, bn + .6)), t > pn ? .06 : 0, t);
    chip('d1', '💥 ลิ่มเลือดหลุด!', 'red', 520, t, popT + .1, be(7) - .1, -3);
    chip('d2', 'ภาวะเบ้าฟันแห้ง (Dry Socket)', 'yel', 650, t, mk(7, 'term', .5), be(7) - .1);
    chip('d3', '⚡ ปวดมาก', 'red', 780, t, pn + .2, be(7) - .1, 2);
  } else if (t < be(8)) {                            // the do's: bite on gauze, cold pack, soft cool food, medicine
    const a = bs(8), d = B[8].dur, gz = mk(8, 'gauze', .2), ic = mk(8, 'ice', .35), fd = mk(8, 'food', .55), md = mk(8, 'med', .8);
    socket(); clotFull();
    if (t < a + .3) flash = .5 * (1 - seg(t, a, a + .3));
    gauze.visible = true; const gk = seg(t, gz - .3, gz + .3); gauze.position.set(0, lerp(9, GT + .66, eout(gk)), -1.5); gauze.rotation.set(0, (1 - gk) * 2, 0);
    if (t > gz + .2 && t < ic) { const bk = seg(t, gz + .2, gz + .7); upper.position.y = lerp(11, 4.25, eout(bk)); gauze.scale.set(1, 1 - .18 * eout(bk), 1); }
    else if (t >= ic) { upper.position.y = lerp(4.25, 11, ease(seg(t, ic, ic + .5))); gauze.scale.set(1, .82, 1); }
    if (t > ic) { ice.visible = true; const k = back(seg(t, ic, ic + .5)); ice.position.set(2.6, GT + 5.0 + .2 * Math.sin(t * 2.5), 3); ice.rotation.set(.3, -.5 + .1 * Math.sin(t * 2), .15); ice.scale.setScalar(Math.max(.001, k) * .75); sparkleAt(2.6, GT + 5.0, 3, (seg(t, ic + .3, be(8)) * 1.5) % 1, 2.4); }
    if (t > md) { pill.visible = true; const k = seg(t, md, md + .6); pill.position.set(-2.4, lerp(10, GT + 4.6, eout(k)) + .2 * Math.sin(t * 3), 3); pill.rotation.set(0, t * 1.5, .9); }
    blur = whip(8);
    setCam('side', 'side', 0);
    chip('g0', '✓ ทำแบบนี้แทน', 'green', 175, t, a + .1, be(8) - .1);
    chip('g1', '✓ กัดผ้าก๊อซให้แน่น', 'green', 305, t, gz + .1, be(8) - .1);
    chip('g2', '🧊 ประคบเย็นที่แก้ม', 'dark', 435, t, ic + .1, be(8) - .1);
    chip('g3', '🍮 อาหารอ่อน เย็นๆ', 'dark', 565, t, fd, be(8) - .1);
    chip('g4', '💊 กินยาตามหมอสั่ง', 'yel', 695, t, md, be(8) - .1);
  } else if (t < be(9)) {                            // myth: a little blood in saliva → must spit? No. If it won't stop, call the clinic
    const a = bs(9), d = B[9].dur, no = mk(9, 'no', .4), ok = mk(9, 'ok', .5), call = mk(9, 'call', .5);
    socket(); clotFull();
    drops.slice(0, 5).forEach((m, i) => { const p = ((t - a) * .5 + i / 5) % 1; m.visible = true; m.position.set(-.6 + i * .3, GT + .5 + p * .25, -.2); m.scale.setScalar(.35 + .2 * Math.sin(p * Math.PI)); });
    if (t > ok) { halo.material.opacity = .3; halo.position.set(0, GT + .4, 1); halo.scale.set(6, 4, 1); }
    blur = whip(9);
    setCam('sockC', 'sockC', 0);
    chip('m1', 'เลือดซึม ต้องบ้วนทิ้ง?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่ต้อง!', 'red', 320, t, no, be(9) - .1, -4);
    chip('m3', '✓ ซึมนิดๆ ปกติ กลืนได้', 'green', 190, t, ok, be(9) - .1);
    chip('m4', '📞 เลือดไม่หยุด โทรหาคลินิก', 'yel', 450, t, call, be(9) - .1);
  } else if (t < be(10)) {                           // after 24 h: gentle warm salt-water rinse, brush the other teeth
    const a = bs(10), d = B[10].dur, sl = mk(10, 'salt', .3), br = mk(10, 'brush', .3);
    socket(); clotFull(); dome.material.color.set('#8e2a30'); clotMat.color.set('#ffd0d0');
    L.calendar('ผ่านไป', '24 ชม. ✓', t > be(10) - .3 ? 1 - seg(t, be(10) - .3, be(10)) : back(seg(t, a + .1, a + .45)));
    if (t > sl && t < br) water.slice(0, 18).forEach(m => { const u = m.userData, ang = u.a + t * .6; m.visible = true; m.position.set(Math.cos(ang) * (u.r + 1), GT + .6 + u.y * .5, -1.2 + Math.sin(ang) * (u.r + 1) * .8); });
    if (t > br) { const k = seg(t, br, be(10) - .1); brush.visible = true; brush.position.set(-2 * SP + Math.sin(k * Math.PI * 6) * 1.8, GT + 4.2, .2); brush.rotation.set(.2, 0, Math.sin(t * 30) * .05);
      if (k > .2) sparkleAt(-2 * SP, GT + 3, 0, (k * 2) % 1, 2.2); }
    setCam('side', 'gap', ease(seg(t, a, a + d * .6)));
    chip('a1', '🧂 บ้วนน้ำเกลืออุ่น เบาๆ', 'green', 520, t, sl, be(10) - .1);
    chip('a2', '🪥 แปรงซี่อื่นได้ตามปกติ', 'dark', 650, t, br, be(10) - .1);
  } else if (t < be(11)) {                           // payoff: the gum closes over a healed socket
    const a = bs(11), d = B[11].dur, hl = mk(11, 'heal', .1);
    socket(); clotFull();
    const k = ease(seg(t, a, hl + 1.2));
    rim.material.opacity = k; dome.visible = k < .6;
    gumCap.visible = true; gumCap.scale.set(Math.max(.01, k), .22 * k + .01, Math.max(.01, k) * .94);
    confetti(t, a); sparkleAt(0, GT + .6, 0, seg(t, hl, hl + .9), 3.2);
    setCam('sockC', 'gap', ease(seg(t, a, a + d * .9)));
    chip('y1', '🎉 แผลปิดสวย หายไว', 'green', 190, t, hl + .2, be(11) - .1);
  } else {                                           // under the end card
    socket(); clotFull(); dome.visible = false; rim.material.opacity = 1; gumCap.visible = true; gumCap.scale.set(1, .23, .94); setCam('gap', 'gap', 0);
  }
  return { blur, flash };
}

// cover: the pulled tooth floats above the socket; a straw aims at the glossy clot
export function cover(t, L) {
  const { lerp, clamp, upper, cam, centerTooth: ct, halo, sparkleAt } = L;
  upper.position.y = 40;
  ct.position.set(-1.9, 5.4 + .25 * Math.sin(t * 2.2), 1.5); ct.rotation.set(.15, t * .5 - .4, .35);
  sockFace.visible = hole.visible = true; clotFace.visible = true; dome.visible = true; levelPlane.constant = GT + .1;
  straw.visible = true; straw.position.set(2.5, GT + 5.4, -.6); straw.rotation.set(0, 0, .45);
  halo.material.opacity = .3; halo.position.set(0, 2.5, -1); halo.scale.set(12, 9, 1);
  sparkleAt(-1.9, 6.8, 1.5, (t * .6) % 1, 3);
  const k = clamp(t / 2);
  cam.position.set(lerp(.8, .6, k), lerp(3.4, 3.2, k), lerp(32, 30.5, k)); cam.lookAt(.4, 7.0, 0);
  return [
    { text: 'ลิ่มเลือด', at: [0, -1.5, .1], dx: 110, dy: 0 },
    { text: 'หลอดดูด', at: [1.6, GT + 3.2, -.6], dx: 40, dy: 0 },
    { text: 'ฟันที่ถอน', at: [-3.4, 3.4, 1.5], dx: -60, dy: 30 },
  ];
}

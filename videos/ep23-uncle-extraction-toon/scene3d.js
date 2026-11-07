// ep23 ลุงสมชาย ถอนฟันแล้วทำแผลพัง 3 อย่าง — HYBRID pilot: cartoon story beats (flat ink characters in a painted
// 3D Thai street, toonworld.js = bundled ToonWorld) + the cut3d jaw for the explanation (beats 7-9).
// Story: uncle leaves the clinic with gauze in his cheek, sucks bubble tea through a straw, smokes, rinses and spits
// -> pop, the clot is out. Luckily the tea was great / unluckily two days of pain. Jaw: clot = the scab on a knee;
// suction, smoke and spitting pull it out -> dry socket; the 24-hour rules. Callback: next extraction the doctor hands
// him a milk tea with no straw and no pearls.
import { ToonWorld } from './toonworld.js';

await document.fonts.load('700 60px K', 'คลินิกทันตกรรมบางปะอิน ชานมไข่มุก');
const LOGO = await new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(null); im.src = '/tools/assets/logo.png'; });

let W, bg0, P, levelPlane, sockFace, clotFace, clotMat, voidMat, hole, dome, rim, straw, cig, ember, smoke = [], water = [];
const GT = 1.2;
const SOCK = [[-1.36, GT], [-1.38, .2], [-1.5, -1.0], [-1.34, -2.6], [-1.12, -4.2], [-.92, -5.25], [-.66, -5.45], [-.44, -5.2], [-.36, -3.2], [-.3, -1.7],
  [0, -1.35], [.3, -1.7], [.36, -3.2], [.44, -5.2], [.66, -5.45], [.92, -5.25], [1.12, -4.2], [1.34, -2.6], [1.5, -1.0], [1.38, .2], [1.36, GT]];
const shape = (THREE, pts) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => i ? s.lineTo(x, y) : s.moveTo(x, y)); s.closePath(); return s; };

export function setup(L) {
  const { THREE, scene, rnd, canvasTex } = L;
  W = new ToonWorld(L.renderer, LOGO);
  bg0 = scene.background;
  L.onReset(() => { scene.background = bg0; scene.visible = true; L.renderer.autoClear = true; });
  // ---- jaw pieces (from ep22)
  L.renderer.localClippingEnabled = true;
  P = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  levelPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), -6);
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
  const inner = SOCK.map(([x, y]) => [x * .9, y > GT - .01 ? GT + .02 : y + .08]);
  clotFace = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, inner)), clotMat); clotFace.position.z = .02; scene.add(clotFace);
  rim = new THREE.Mesh(new THREE.ShapeGeometry(shape(THREE, inner)), new THREE.MeshStandardMaterial({ color: '#efe1c2', roughness: .85, transparent: true, opacity: 0 })); rim.position.z = .024; scene.add(rim);
  hole = new THREE.Mesh(new THREE.CircleGeometry(1.36, 48), new THREE.MeshStandardMaterial({ color: '#3a0b10', roughness: .8, clippingPlanes: [P] }));
  hole.rotation.x = -Math.PI / 2; hole.position.set(0, GT + .012, -1.25); hole.scale.set(1, .95, 1); scene.add(hole);
  dome = new THREE.Mesh(new THREE.SphereGeometry(1.26, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshPhysicalMaterial({ color: '#7e0f1c', roughness: .2, clearcoat: 1, clearcoatRoughness: .1, sheen: .4, sheenColor: new THREE.Color('#ff6070'), clippingPlanes: [P], clipShadows: true }));
  dome.castShadow = true; scene.add(dome);
  const stripes = canvasTex(64, 512, (g, w, h) => { g.fillStyle = '#ffffff'; g.fillRect(0, 0, w, h); g.fillStyle = '#ef4a5c'; for (let y = -64; y < h + 64; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y + 40); g.lineTo(w, y + 64); g.lineTo(0, y + 24); g.fill(); } });
  straw = new THREE.Mesh(new THREE.CylinderGeometry(.42, .42, 12, 32, 1, true), new THREE.MeshPhysicalMaterial({ map: stripes, roughness: .3, clearcoat: .6, side: THREE.DoubleSide }));
  straw.castShadow = true; scene.add(straw);
  cig = new THREE.Group(); scene.add(cig);
  { const body = new THREE.Mesh(new THREE.CylinderGeometry(.3, .3, 4.2, 24), new THREE.MeshStandardMaterial({ color: '#f7f4ec', roughness: .7 })); body.position.y = .9; cig.add(body);
    const filt = new THREE.Mesh(new THREE.CylinderGeometry(.31, .31, 1.6, 24), new THREE.MeshStandardMaterial({ color: '#d98a3c', roughness: .65 })); filt.position.y = 3.8; cig.add(filt);
    ember = new THREE.Mesh(new THREE.CylinderGeometry(.3, .26, .35, 24), new THREE.MeshStandardMaterial({ color: '#ff5a1f', emissive: '#ff3a00', emissiveIntensity: 1.6, roughness: .5 })); ember.position.y = -1.33; cig.add(ember); }
  const soft = rgba => canvasTex(128, 128, g => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, rgba(1)); gr.addColorStop(.5, rgba(.45)); gr.addColorStop(1, rgba(0)); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  const smokeTex = soft(a => `rgba(190,190,195,${a * .75})`);
  for (let i = 0; i < 16; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: smokeTex, transparent: true, depthWrite: false })); s.userData = { d: rnd(), x: rnd() - .5 }; scene.add(s); smoke.push(s); }
  const wm = new THREE.MeshPhysicalMaterial({ color: '#bfe8ff', roughness: .05, transmission: .6, thickness: .5, transparent: true, opacity: .8, clearcoat: 1 });
  for (let i = 0; i < 30; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(.12 + rnd() * .14, 14, 10), wm); m.userData = { a: rnd() * 6.28, r: 1 + rnd() * 2.6, y: rnd() * 1.6, s: 2 + rnd() * 3 }; scene.add(m); water.push(m); }
  Object.assign(L.SHOTS, {
    sock: [[3.2, 1.2, 17.5], [0, -1.6, 0]], sockC: [[2.6, 3.4, 11.5], [0, .4, 0]],
    sockTop: [[2.4, 9.5, 9.5], [0, 1.2, -1.2]], side: [[1.2, 5.6, 23], [2.0, 1.6, 0]], low: [[1.0, -3.4, 21], [0.6, 2.6, 0]],
  });
  L.onReset(() => {
    [straw, cig, ...smoke, ...water].forEach(o => o.visible = false);
    [sockFace, clotFace, hole, dome].forEach(o => o.visible = false); rim.material.opacity = 0;
    levelPlane.constant = 6; dome.position.set(0, GT, -1.2); dome.scale.set(1, .3, .94); dome.rotation.set(0, 0, 0); voidMat.color.set('#ffffff');
  });
}

// ---------------------------------------------------------------- cartoon helpers
const sstep = k => (k = Math.min(1, Math.max(0, k)), k * k * k * (k * (k * 6 - 15) + 10));
const mixV = (a, b, k) => a.map((v, i) => v + (b[i] - v) * k);
/** a shot: from {pos,look} glides (smootherstep) to the end key; holds always creep */
const glide = (t, t0, t1, A, B) => { const k = sstep((t - t0) / (t1 - t0)); return { pos: mixV(A.pos, B.pos, k), look: mixV(A.look, B.look, k), fov: (A.fov ?? 40) + ((B.fov ?? 40) - (A.fov ?? 40)) * k, roll: ((A.roll ?? 0) + ((B.roll ?? 0) - (A.roll ?? 0)) * k) * Math.PI / 180 }; };
const blinkAt = (t, seed) => { const per = 1.7 + (seed * 0.37) % 0.9, ph = ((t + seed * 0.61) % per) / per; return ph > 1 - 0.135 / per ? 1 : 0; };
const kick = (t, t0, amp = 14) => { const f = Math.round((t - t0) * 30); return f >= 0 && f < 7 ? amp * (1 - f / 7) * (f % 2 ? -1 : 1) : 0; };
const SW = 0.16; // sidewalk top

function toon(L, F) { W.frame(F); L.scene.background = null; L.scene.visible = false; L.renderer.autoClear = false; }

export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, back, lerp, setCam, chip, halo, warn, inflam } = L;
  let flash = 0, blur = 0;
  const num = (id, n, text, t0, t1) => { chip(id + 'n', `❌ ${n}`, 'red', 175, t, t0, t1, -4); chip(id, text, 'dark', 300, t, t0 + .15, t1); };
  const uncle = (x, z, o, y = SW) => ({ who: 'uncle', x, z, y, opts: { blink: blinkAt(t, 1), ...o } });
  const doctor = (x, z, o, y = SW) => ({ who: 'doctor', x, z, y, opts: { blink: blinkAt(t, 2), ...o } });
  const vendor = (x, z, o, y = SW) => ({ who: 'vendor', x, z, y, opts: { blink: blinkAt(t, 3), ...o } });

  if (t < be(0)) {                                   // hook: out of the clinic, gauze in the cheek, heading for the car
    const a = bs(0), wk = mk(0, 'walk', .3), th = mk(0, 'three', .8);
    const k = seg(t, a + .4, be(0)), ux = lerp(0.2, 2.6, sstep(seg(t, wk - .6, be(0)))), uz = lerp(-2.6, -1.3, sstep(seg(t, a + .2, wk)));
    const cam = t < th - .1 ? glide(t, a, th, { pos: [-1.2, 1.95, 6.6], look: [0.5, 2.1, -2.5], roll: -1 }, { pos: [-0.7, 1.85, 5.6], look: [0.9, 2.05, -2.0], roll: 0 })
      : glide(t, th - .1, be(0), { pos: [0.6, 1.75, 4.6], look: [2.3, 1.9, -1.3], fov: 36, roll: 4 }, { pos: [0.9, 1.72, 4.1], look: [2.4, 1.9, -1.3], fov: 35, roll: 4.5 });
    cam.pos[0] += kick(t, th, 1) * .004;
    toon(L, { light: 'day', ...cam, cInf: t > th ? 11 : 0, focus: [ux, 1.6, uz],
      actors: [uncle(ux, uz, { mode: t > wk - .6 ? 'stroll' : 'stand', phase: ux / 0.8, prop: 'cheek', expr: t > th ? 'grin' : 'smile', look: .6 }),
        doctor(-1.0, -2.9, { mode: 'stand', expr: 'smile', wave: Math.sin(t * 9) * .5 + .5 })] });
    chip('h1', 'ถอนฟันเสร็จปุ๊บ...', 'dark', 330, t, a + .2, th - .05);
    chip('h2', 'ทำแผลพัง 3 อย่าง!', 'red', 330, t, th, be(0) - .1, -3);
  } else if (t < be(1)) {                            // #1: bubble tea, straw, hard suction
    const a = bs(1), sh = mk(1, 'shop', .2), su = mk(1, 'suck', .5), ch = mk(1, 'cheer', .75);
    const cam = t < su - .05 ? glide(t, a, su, { pos: [0.4, 1.9, 5.6], look: [3.9, 1.8, -1.6], fov: 40 }, { pos: [0.8, 1.8, 5.0], look: [3.8, 1.8, -1.5], fov: 39 })
      : glide(t, su - .05, be(1), { pos: [2.2, 1.75, 2.6], look: [3.1, 1.88, -0.9], fov: 36, roll: -4 }, { pos: [2.25, 1.75, 2.3], look: [3.1, 1.88, -0.9], fov: 35, roll: -4.5 });
    const fx = [];
    if (t > su) fx.push({ kind: 'suck', t: ((t - su) * 1.6) % 1, x: 3.18, y: 1.92, z: -0.7, w: .32 });
    if (t > ch) fx.push({ kind: 'stars', t: ((t - ch) * .8) % 1, x: 3.0, y: 2.25, z: -0.8, w: .7, h: .35 });
    toon(L, { light: 'day', ...cam, cInf: t > su ? 13 : 6, focus: [3.0, 1.6, -0.9], fx,
      actors: [uncle(3.0, -0.9, { mode: 'stand', prop: t > sh + .4 ? 'cup' : 'cheek', expr: t > ch ? 'grin' : t > su ? 'whistle' : 'smile', look: -.3, wave: t > ch ? .8 : undefined }),
        vendor(4.7, -2.75, { mode: 'stand', expr: 'smile', look: -.5 })] });
    num('x1', 1, 'ดูดหลอดแรงๆ', su, be(1) - .1);
  } else if (t < be(2)) {                            // #2: one more cigarette
    const a = bs(2), lt = mk(2, 'light', .3);
    const cam = glide(t, a, be(2), { pos: [4.8, 1.65, 3.7], look: [6.4, 1.75, -1.0], fov: 36, roll: 3 }, { pos: [5.0, 1.68, 3.3], look: [6.4, 1.78, -1.0], fov: 35, roll: 4 });
    const fx = t > lt ? [{ kind: 'smoke', t: ((t - lt) * .7) % 1, x: 6.62, y: 2.15, z: -0.95, w: .7 }, { kind: 'smoke', t: ((t - lt) * .7 + .5) % 1, x: 6.5, y: 2.3, z: -0.95, w: .8 }] : [];
    toon(L, { light: 'day', ...cam, cInf: 12, focus: [6.2, 1.6, -1.0], fx,
      actors: [uncle(6.2, -1.0, { mode: 'stand', prop: t > lt - .3 ? 'cig' : 'cup', expr: t > lt ? 'relief' : 'smile', look: .4 })] });
    num('x2', 2, 'สูบบุหรี่', lt, be(2) - .1);
  } else if (t < be(3)) {                            // #3: sees blood, rinses, spits at the kerb
    const a = bs(3), se = mk(3, 'see', .2), ri = mk(3, 'rinse', .5), sp = mk(3, 'spit', .75);
    const cam = t < sp - .05 ? glide(t, a, sp, { pos: [7.4, 1.6, 4.0], look: [9.4, 1.55, -0.5], fov: 38, roll: -2 }, { pos: [7.8, 1.6, 3.5], look: [9.4, 1.55, -0.5], fov: 37, roll: -3 })
      : glide(t, sp - .05, be(3), { pos: [11.4, 1.35, 3.0], look: [9.7, 0.95, -0.2], fov: 40, roll: 4 }, { pos: [11.2, 1.35, 2.7], look: [9.7, 0.95, -0.2], fov: 39, roll: 4.5 });
    const fx = t > sp ? [{ kind: 'splash', t: Math.min(1, (t - sp) * .9), x: 9.95, y: 0.12, z: 0.3, w: 1.0 }] : [];
    const expr = t > sp ? 'relief_open' : t > ri ? 'whistle' : t > se ? 'shock' : 'relief';
    toon(L, { light: 'day', ...cam, cInf: 10, focus: [9.4, 1.4, -0.4], fx,
      actors: [uncle(9.4, -0.4, { mode: 'stand', prop: t > sp ? 'spit' : t > ri ? 'cupLow' : null, expr, look: t > se && t < ri ? -.6 : .3, headTilt: t > ri && t < sp ? Math.sin(t * 18) * 4 : 0 })] });
    num('x3', 3, 'บ้วนปากแรงๆ', sp, be(3) - .1);
  } else if (t < be(4)) {                            // the snap: pop
    const a = bs(4), pp = mk(4, 'pop', .3);
    const cam = glide(t, a, be(4), { pos: [9.5, 1.68, 2.2], look: [9.4, 1.6, -0.4], fov: 32, roll: 0 }, { pos: [9.5, 1.66, 1.7], look: [9.4, 1.6, -0.4], fov: 30, roll: 0 });
    const kk = kick(t, pp, 10); cam.pos[0] += kk * .003; cam.roll = kk * .003;
    const fx = t > pp ? [{ kind: 'burst', t: Math.min(1, (t - pp) * 2.2), x: 9.62, y: 1.55, z: -0.25, w: .7, col: '#ff8a7a' }] : [];
    toon(L, { light: 'day', ...cam, cInf: 15, focus: [9.4, 1.6, -0.4], fx,
      actors: [uncle(9.4, -0.4, { mode: 'stand', prop: t > pp ? 'cheek' : null, expr: t > pp ? 'shock' : 'relief', look: 0 })] });
    if (t > pp && t < pp + .2) flash = .6 * (1 - (t - pp) / .2);
    chip('p1', '💥 ลิ่มเลือดหลุด!', 'red', 330, t, pp + .05, be(4) - .1, -3);
  } else if (t < be(5)) {                            // luckily...
    const a = bs(5);
    const cam = glide(t, a, be(5), { pos: [8.0, 1.7, 3.4], look: [9.4, 1.7, -0.4], fov: 37, roll: 3 }, { pos: [8.2, 1.7, 3.0], look: [9.4, 1.7, -0.4], fov: 36, roll: 4 });
    toon(L, { light: 'day', ...cam, cInf: 9, focus: [9.4, 1.6, -0.4], fx: [{ kind: 'stars', t: ((t - a) * .9) % 1, x: 9.4, y: 2.3, z: -0.4, w: .75, h: .37 }],
      actors: [uncle(9.4, -0.4, { mode: 'stand', prop: 'cup', expr: 'grin', look: .2 })] });
    chip('l1', '😋 โชคดี...', 'green', 330, t, a + .1, be(5) - .05);
  } else if (t < be(6)) {                            // unluckily... two days of pain, no sleep (golden evening, bedroom)
    const a = bs(6), dy = mk(6, 'days', .15), pn = mk(6, 'pain', .5);
    const cam = glide(t, a, be(6), { pos: [61.5, 2.0, 3.6], look: [60, 2.1, -1.6], fov: 42, roll: -4 }, { pos: [61.3, 1.95, 3.1], look: [60, 2.1, -1.6], fov: 40, roll: -4.5 });
    const fx = t > pn ? [{ kind: 'zzz', t: ((t - pn) * 1.8) % 1, x: 60.5, y: 2.2, z: -1.1, w: .6 }] : [];
    toon(L, { light: 'golden', ...cam, sunAz: 150, sunEl: 22, cInf: 8, focus: [60, 2.0, -1.3], fx,
      actors: [uncle(60, -1.3, { mode: 'sit', prop: 'cheek', expr: t > pn ? 'pained' : 'dazed', look: .1, headTilt: t > pn ? Math.sin(t * 20) * 3 : 0 }, 0.77)].map(a => (a.z = -1.3, a)) });
    if (t > dy) L.calendar('ผ่านไป', '2 วัน', back(seg(t, dy, dy + .35)));
    chip('u1', '😫 ปวดจนนอนไม่หลับ', 'red', 520, t, pn, be(6) - .1, 3);
  } else if (t < be(7)) {                            // JAW: the clot = the scab on a knee
    const a = bs(7), bl = mk(7, 'blood', .25), cl = mk(7, 'clot', .5), kn = mk(7, 'knee', .7);
    L.upper.position.y = 40; L.centerTooth.visible = false; sockFace.visible = hole.visible = clotFace.visible = true;
    levelPlane.constant = lerp(-5.5, GT + .1, ease(seg(t, bl - .2, cl + .3)));
    if (t > cl) { dome.visible = true; dome.scale.set(1, .3 * back(seg(t, cl, cl + .5)), .94); halo.material.opacity = .35 * Math.sin(seg(t, cl, be(7)) * Math.PI); halo.position.set(0, GT + .4, 1); halo.scale.set(6, 4, 1); }
    if (t < a + .25) flash = .7 * (1 - seg(t, a, a + .25));
    setCam('sock', 'sockC', ease(seg(t, a + .2, be(7))));
    chip('c1', '🩸 ลิ่มเลือด ปิดแผล', 'yel', 190, t, cl, be(7) - .1);
    chip('c2', '🩹 เหมือนสะเก็ดแผลที่เข่า', 'green', 320, t, kn, be(7) - .1);
  } else if (t < be(8)) {                            // JAW: suction, smoke, spitting -> clot out, bone shows -> dry socket
    const a = bs(8), su = mk(8, 'suck', .05), sm = mk(8, 'smoke', .15), sp = mk(8, 'spit', .3), pl = mk(8, 'pull', .45), bn = mk(8, 'bone', .65), tm = mk(8, 'term', .85);
    L.upper.position.y = 40; L.centerTooth.visible = false; sockFace.visible = hole.visible = clotFace.visible = true;
    const k = seg(t, pl, pl + .8);
    if (k < 1) { dome.visible = true; levelPlane.constant = GT + .1;
      if (k > 0) { dome.position.set(lerp(0, -3, k), GT + 9 * eout(k) - 4 * k * k, lerp(-1.2, 2, k)); dome.rotation.set(k * 5, 0, k * 3); levelPlane.constant = lerp(GT + .1, -5.6, ease(k)); }
      else { const w = Math.sin(t * 16) * .05 * seg(t, su, pl); dome.scale.set(1 + w, .3 - w * 1.4 + .25 * seg(t, su, pl), .94 + w); dome.position.y = GT + .3 * seg(t, su, pl); } }
    else levelPlane.constant = -5.6;
    if (t < pl) { straw.visible = t > su; straw.position.set(-.4, lerp(16, GT + 6.4, eout(seg(t, su, su + .4))), -1.2);
      cig.visible = t > sm; cig.position.set(lerp(9, 3.6, eout(seg(t, sm, sm + .4))), GT + 3.4, .5); cig.rotation.set(0, 0, 1.15); ember.material.emissiveIntensity = 1.4 + .6 * Math.sin(t * 9);
      smoke.forEach(s => { const p = ((t - sm) * .55 + s.userData.d) % 1; s.visible = t > sm; s.position.set(lerp(2.1, s.userData.x * .8, p), lerp(GT + 2, GT + .5, p), lerp(.6, -1.2, p)); s.scale.setScalar(1 + p * 2.6); s.material.opacity = Math.sin(p * Math.PI) * .9; });
      if (t > sp) water.forEach(m => { const u = m.userData, ang = u.a + t * u.s; m.visible = true; m.position.set(Math.cos(ang) * u.r, GT + .3 + u.y * .7, -1.2 + Math.sin(ang) * u.r * .9); }); }
    if (k > 0 && k < .25) flash = .35;
    if (t > bn) { rim.material.opacity = .95 * seg(t, bn, bn + .5); voidMat.color.set('#ffffff').lerp(new L.THREE.Color('#ffe6c0'), seg(t, bn, bn + .6));
      warn.material.opacity = .9 * (.5 + .5 * Math.sin((t - bn) * 16)); warn.position.set(0, -1.6, .6); warn.scale.set(1.15, 2.6, 1); inflam.material.opacity = .45; inflam.position.set(0, GT + .02, -1.4); }
    setCam(t < pl ? 'side' : 'sockC', 'sock', t < pl ? 0 : ease(seg(t, pl, bn + .6)), t > bn ? .05 : 0, t);
    if (t < pl + .1) { chip('w1', '⬆ แรงดูด', 'dark', 190, t, su, pl); chip('w2', '💨 ควันบุหรี่', 'dark', 310, t, sm, pl); chip('w3', '💦 บ้วนแรงๆ', 'dark', 430, t, sp, pl); }
    chip('w4', '💥 ลิ่มเลือดหลุด → กระดูกโผล่', 'red', 190, t, pl + .1, be(8) - .1);
    chip('w5', 'ภาวะเบ้าฟันแห้ง (Dry Socket)', 'yel', 320, t, tm, be(8) - .1, -2);
  } else if (t < be(9)) {                            // JAW: the 24-hour rules
    const a = bs(9), h = mk(9, 'h24', .1), r = ['r1', 'r2', 'r3', 'r4', 'r5'].map((n, i) => mk(9, n, .3 + i * .13));
    L.upper.position.y = 40; L.centerTooth.visible = false; sockFace.visible = hole.visible = clotFace.visible = dome.visible = true; levelPlane.constant = GT + .1;
    halo.material.opacity = .3; halo.position.set(0, GT + .4, 1); halo.scale.set(6, 4, 1);
    if (t < a + .25) flash = .5 * (1 - seg(t, a, a + .25));
    if (t > h && t < r[0]) L.calendar('ปกป้องลิ่มเลือด', '24 ชม.', back(seg(t, h, h + .35)));
    setCam('low', 'side', ease(seg(t, a, be(9))));
    ['✕ ห้ามดูดหลอด', '✕ ห้ามบ้วนแรง', '✕ งดบุหรี่', '✕ งดเหล้า', '✕ อย่าเอาลิ้นดุนแผล'].forEach((s, i) => chip('r' + i, s, i % 2 ? 'dark' : 'red', 190 + i * 120, t, r[i], be(9) - .1, i % 2 ? 2 : -2));
  } else if (t < be(10)) {                           // callback: a month later, milk tea with no straw and no pearls
    const a = bs(10), hd = mk(10, 'hand', .35), ns = mk(10, 'nostraw', .6), np = mk(10, 'nopearl', .8);
    const cam = t < hd - .05 ? glide(t, a, hd, { pos: [-0.3, 2.1, 7.0], look: [0.1, 1.9, -2.0], fov: 40 }, { pos: [-0.2, 2.0, 6.0], look: [0.1, 1.9, -2.0], fov: 39 })
      : glide(t, hd - .05, be(10), { pos: [0.1, 1.7, 3.6], look: [0.2, 1.65, -2.1], fov: 36, roll: 3 }, { pos: [0.15, 1.7, 3.2], look: [0.2, 1.65, -2.1], fov: 35, roll: 4 });
    const give = t > ns - .3;
    toon(L, { light: 'day', ...cam, cInf: t > hd ? 11 : 0, focus: [0.2, 1.6, -2.2],
      fx: t > np ? [{ kind: 'stars', t: ((t - np) * .9) % 1, x: 0.9, y: 2.25, z: -2.1, w: .7, h: .35 }] : [],
      actors: [doctor(-0.55, -2.35, { mode: 'stand', prop: t > hd && !give ? 'cupLow' : null, expr: t > np ? 'grin' : 'smile', look: .4, wave: give ? .6 : undefined }),
        uncle(0.95, -2.1, { mode: 'stand', prop: give ? 'cupLow' : 'cheek', expr: t > np ? 'dazed' : t > ns ? 'nervous' : 'smile', look: -.4 })] });
    chip('n0', '📅 เดือนต่อมา...', 'dark', 190, t, a + .1, hd - .05);
    chip('n1', '✕ ไม่มีหลอด', 'red', 190, t, ns, be(10) - .1, -3);
    chip('n2', '✕ ไม่มีไข่มุก', 'red', 310, t, np, be(10) - .1, 2);
  } else {                                           // under the end card: the street
    toon(L, { light: 'day', pos: [-0.2, 2.0, 6.0], look: [0.1, 1.9, -2.0], fov: 39, actors: [] });
  }
  return { blur, flash };
}

// cover: uncle at the stall, straw in his mouth, a red burst at his cheek (title text sits in the sky above)
export function cover(t, L) {
  toon(L, { light: 'day', pos: [1.6, 1.25, 3.4], look: [3.2, 2.25, -1.0], fov: 40, roll: -3 * Math.PI / 180, cInf: 10, focus: [3.0, 1.6, -0.9],
    fx: [{ kind: 'burst', t: .55, x: 3.25, y: 1.5, z: -0.7, w: .55, col: '#ff8a7a' }, { kind: 'suck', t: (t * 1.6) % 1, x: 3.18, y: 1.92, z: -0.7, w: .32 }],
    actors: [uncle(3.0, -0.9, { mode: 'stand', prop: 'cup', expr: 'whistle', look: -.3, blink: 0 }), vendor(4.7, -2.75, { mode: 'stand', expr: 'smile', look: -.5 })] });
  return [];
  function uncle(x, z, opts) { return { who: 'uncle', x, z, y: SW, opts }; }
  function vendor(x, z, opts) { return { who: 'vendor', x, z, y: SW, opts }; }
}

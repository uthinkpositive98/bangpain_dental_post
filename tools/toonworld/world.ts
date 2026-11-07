// Cartoon street world for the clinic's hybrid Reels: flat ink-outlined characters in a painted 3D Thai street
// (shophouses, the clinic, a bubble-tea stall, power poles, a parked car), rendered with the look stack of the
// cartoon-3d-short skill (two-tone world shading, lit character cards, world ink pass, thin-lens blur, bloom,
// Neutral tone map, colour grade). It shares the cut3d renderer/canvas; the episode calls frame() for story beats.
import * as THREE from "three";
import { EffectComposer, RenderPass, EffectPass, BloomEffect, ToneMappingEffect, ToneMappingMode, BlendFunction } from "postprocessing";
import { InkPass, noInkFallback, NOINK } from "./ink";
import { LensBlur } from "./lensblur";
import { GradeEffect, gradeFor, GRADES } from "./grade";
import { LIGHTS, LOOK } from "./lights";
import { TONE, CHAR, twoTone, untone } from "./shade";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";
import { Pen, bodyFront, Outfit, FrontOpts, fxBurst, fxSplash, fxPuff, fxStars, fxContact, INK } from "./toon";

type V3 = [number, number, number];
export type LightName = "day" | "golden";
export const FONT = "K, sans-serif";

// ---------------- characters ----------------
export const OUTFITS: Record<string, Outfit> = {
  uncle: { jacket: "#f2a33a", pants: "#5b4a3c", boots: "#3a2a20", hat: null, moustache: "#3a2a20", build: "stout", buttons: "#fff2d6", skin: "#f5c9a0" },
  doctor: { jacket: "#f4f8fa", pants: "#3cc6c2", boots: "#ffffff", hat: "hair", hair: "#2b1d16", skin: "#ffe2c2", buttons: "#3cc6c2" },
  vendor: { jacket: "#e2453c", pants: "#3b3f52", boots: "#2b2b2b", hat: "cap", cap: "#ffd166", skin: "#ecd0b6" },
  aunt: { jacket: "#7b5ac9", pants: "#3b3f52", boots: "#5a3b2a", hat: "hair", hair: "#3a2a20", dress: "#9d7be0", skin: "#f5c9a0" },
};
export type ActorSpec = { who: keyof typeof OUTFITS | string; x: number; z: number; y?: number; opts: FrontOpts; scale?: number };
export type FxSpec = { kind: "burst" | "splash" | "puff" | "stars" | "smoke" | "zzz" | "suck"; t: number; x: number; y: number; z: number; w: number; h?: number; col?: string };
export type Frame = { light: LightName; pos: V3; look: V3; fov?: number; roll?: number; cInf?: number; focus?: V3; sunAz?: number; sunEl?: number;
  actors: ActorSpec[]; fx?: FxSpec[]; shakePx?: number };

const SU = 0.00216, CW = 480, CH = 800, CS = CW / 600;          // metres per design unit; card canvas 0.8 x design
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const rngOf = (seed: number) => { let s = (seed * 9301 + 49297) % 233280 || 1; return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; };

const tex = (w: number, h: number, draw: (g: CanvasRenderingContext2D, r: () => number) => void, seed = 1, wrap = true) => {
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  draw(c.getContext("2d")!, rngOf(seed));
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  if (wrap) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
};
const lam = (o: THREE.MeshLambertMaterialParameters) => twoTone(new THREE.MeshLambertMaterial(o));
const shadeHex = (hex: string, k: number) => { const c = new THREE.Color(hex); c.multiplyScalar(k); return "#" + c.getHexString(); };

// ---------------- painted textures (64 px / m) ----------------
const PXM = 64;
type Shop = { wall: string; trim: string; floors: number; sign?: string; signCol?: string; signInk?: string; shutter?: number; awning?: string; clinic?: boolean; logo?: HTMLImageElement | null };
function shopFacade(wm: number, hm: number, o: Shop, seed: number) {
  const W = Math.round(wm * PXM), H = Math.round(hm * PXM), m = (v: number) => v * PXM;
  return tex(W, H, (g, r) => {
    g.fillStyle = o.wall; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 26; i++) { // soft weathering blotches + rain streaks
      const x = r() * W, y = r() * H, rad = m(0.3 + r() * 1.1);
      const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(60,40,30,${0.04 + r() * 0.05})`); gr.addColorStop(1, "rgba(60,40,30,0)");
      g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
    }
    for (let i = 0; i < 10; i++) { const x = r() * W; g.fillStyle = `rgba(70,55,45,${0.04 + r() * 0.04})`; g.fillRect(x, m(0.4), m(0.05 + r() * 0.08), m(1 + r() * 2.5)); }
    const fl = (H - m(3.4)) / Math.max(1, o.floors - 1);
    // parapet + floor bands
    g.fillStyle = o.trim; g.fillRect(0, 0, W, m(0.35));
    for (let f = 0; f < o.floors - 1; f++) { const y = m(0.35) + f * fl + fl - m(0.12); g.fillRect(0, y, W, m(0.18)); }
    g.fillStyle = "rgba(40,30,40,.55)"; g.fillRect(0, m(0.35), W, 3);
    // upper floors: two windows each with a grille, AC unit on one
    for (let f = 0; f < o.floors - 1; f++) {
      const y0 = m(0.35) + f * fl + m(0.55), wh = Math.min(m(1.6), fl - m(1.0));
      for (let k = 0; k < 2; k++) {
        const x0 = m(0.45) + k * (W / 2), ww = W / 2 - m(0.9);
        g.fillStyle = shadeHex(o.trim, 0.9); g.fillRect(x0 - 6, y0 - 6, ww + 12, wh + 12);
        const gr = g.createLinearGradient(0, y0, 0, y0 + wh); gr.addColorStop(0, "#5d7891"); gr.addColorStop(1, "#2e3d52");
        g.fillStyle = gr; g.fillRect(x0, y0, ww, wh);
        g.fillStyle = "rgba(255,255,255,.18)"; g.beginPath(); g.moveTo(x0 + ww * 0.15, y0); g.lineTo(x0 + ww * 0.45, y0); g.lineTo(x0 + ww * 0.15, y0 + wh); g.lineTo(x0, y0 + wh); g.closePath(); g.fill();
        g.strokeStyle = "rgba(30,24,30,.9)"; g.lineWidth = 3;
        for (let gx = x0; gx <= x0 + ww + 1; gx += ww / 6) { g.beginPath(); g.moveTo(gx, y0); g.lineTo(gx, y0 + wh); g.stroke(); }
        g.beginPath(); g.moveTo(x0, y0 + wh / 2); g.lineTo(x0 + ww, y0 + wh / 2); g.stroke();
        g.strokeRect(x0, y0, ww, wh);
      }
      if ((f + seed) % 2 === 0) { const ax = W - m(1.5), ay = y0 + Math.min(m(1.6), fl - m(1.0)) + m(0.1); g.fillStyle = "#e9ecee"; g.fillRect(ax, ay, m(0.9), m(0.55)); g.strokeStyle = "rgba(30,24,30,.8)"; g.lineWidth = 3; g.strokeRect(ax, ay, m(0.9), m(0.55));
        for (let i = 1; i < 6; i++) { g.beginPath(); g.moveTo(ax + 6, ay + i * m(0.09)); g.lineTo(ax + m(0.9) - 6, ay + i * m(0.09)); g.stroke(); } }
    }
    // ground floor: sign band + shop front
    const gy = H - m(3.4), sh = m(0.75);
    g.fillStyle = o.signCol ?? shadeHex(o.trim, 0.95); g.fillRect(m(0.15), gy, W - m(0.3), sh);
    g.strokeStyle = "rgba(30,24,30,.85)"; g.lineWidth = 4; g.strokeRect(m(0.15), gy, W - m(0.3), sh);
    if (o.sign) {
      let fs = sh * 0.62; g.font = `700 ${fs}px ${FONT}`;
      const lx = o.logo ? sh * 1.0 : 0;
      while (g.measureText(o.sign).width > W - m(0.6) - lx && fs > 10) { fs -= 2; g.font = `700 ${fs}px ${FONT}`; }
      g.fillStyle = o.signInk ?? "#1f2a44"; g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(o.sign, W / 2 + lx / 2, gy + sh * 0.53);
      if (o.logo) { const s = sh * 0.9; g.drawImage(o.logo, W / 2 - g.measureText(o.sign).width / 2 - s * 0.6 + lx / 2 - s / 2, gy + (sh - s) / 2, s, s); }
    }
    const fy = gy + sh + m(0.1), fh = H - fy;
    if (o.clinic) { // glass shop front with a door and a tooth sticker
      g.fillStyle = "#e9f6f6"; g.fillRect(m(0.2), fy, W - m(0.4), fh);
      const gr = g.createLinearGradient(0, fy, 0, H); gr.addColorStop(0, "#a8d8e0"); gr.addColorStop(1, "#6fa7b8");
      g.fillStyle = gr; g.fillRect(m(0.35), fy + m(0.15), W - m(0.7), fh - m(0.15));
      g.strokeStyle = "rgba(30,24,30,.9)"; g.lineWidth = 5;
      for (const x of [m(0.35), W / 2 - m(0.55), W / 2 + m(0.55), W - m(0.35)]) { g.beginPath(); g.moveTo(x, fy + m(0.15)); g.lineTo(x, H); g.stroke(); }
      g.strokeRect(m(0.35), fy + m(0.15), W - m(0.7), fh - m(0.15));
      g.fillStyle = "rgba(255,255,255,.35)"; for (const x of [m(0.6), W / 2 + m(0.8)]) { g.beginPath(); g.moveTo(x, fy + m(0.3)); g.lineTo(x + m(0.4), fy + m(0.3)); g.lineTo(x - m(0.2), H); g.lineTo(x - m(0.6), H); g.fill(); }
      g.fillStyle = "#ffffff"; g.font = `700 ${m(0.42)}px ${FONT}`; g.textAlign = "center"; g.fillText("🦷", W / 2, fy + m(1.2));
      g.fillStyle = "#c9d2d6"; g.fillRect(W / 2 - m(0.08), fy + m(1.4), m(0.05), m(0.5)); g.fillRect(W / 2 + m(0.03), fy + m(1.4), m(0.05), m(0.5));
    } else { // roller shutter half up over a dim shop interior
      const up = o.shutter ?? 0.55;
      g.fillStyle = "#3a3238"; g.fillRect(m(0.2), fy, W - m(0.4), fh);
      for (let i = 0; i < 9; i++) { g.fillStyle = ["#c7a46a", "#7a9cc4", "#d9705a", "#8fbf7a"][i % 4]; g.fillRect(m(0.5) + (i % 3) * (W - m(1)) / 3, fy + m(0.8) + Math.floor(i / 3) * m(0.55), (W - m(1.4)) / 3, m(0.35)); }
      const sb = fy + fh * (1 - up);
      g.fillStyle = "#b9bec4"; g.fillRect(m(0.2), fy, W - m(0.4), sb - fy);
      g.strokeStyle = "rgba(60,64,72,.6)"; g.lineWidth = 2; for (let y = fy; y < sb; y += 7) { g.beginPath(); g.moveTo(m(0.2), y); g.lineTo(W - m(0.2), y); g.stroke(); }
      g.fillStyle = "#8d939a"; g.fillRect(m(0.2), sb - 8, W - m(0.4), 8);
    }
    g.fillStyle = "rgba(30,24,30,.9)"; g.fillRect(0, 0, 3, H); g.fillRect(W - 3, 0, 3, H);
  }, seed, false);
}
const asphalt = () => tex(1024, 1024, (g, r) => {
  g.fillStyle = "#6c6f78"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 9000; i++) { const v = 90 + r() * 40; g.fillStyle = `rgba(${v},${v},${v + 8},${0.25 + r() * 0.3})`; g.fillRect(r() * 1024, r() * 1024, 2 + r() * 3, 2 + r() * 3); }
  for (let i = 0; i < 18; i++) { const x = r() * 1024, y = r() * 1024, rr = 40 + r() * 120; const gr = g.createRadialGradient(x, y, 0, x, y, rr); gr.addColorStop(0, "rgba(40,40,50,.12)"); gr.addColorStop(1, "rgba(40,40,50,0)"); g.fillStyle = gr; g.fillRect(x - rr, y - rr, 2 * rr, 2 * rr); }
}, 3);
const paving = () => tex(512, 512, (g, r) => {
  g.fillStyle = "#b9b0a2"; g.fillRect(0, 0, 512, 512);
  const n = 8, s = 512 / n;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const v = 0.92 + r() * 0.12; g.fillStyle = ["#d8d0c2", "#cfc6b6", "#e0d8ca", "#c9bfae"][(i + j * 3 + Math.floor(r() * 2)) % 4]; g.globalAlpha = v; g.fillRect(i * s + 2, j * s + 2, s - 4, s - 4); g.globalAlpha = 1; }
}, 5);
const stripes = (a: string, b: string) => tex(256, 64, (g) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? a : b; g.fillRect(i * 32, 0, 32, 64); } g.fillStyle = "rgba(30,24,30,.9)"; g.fillRect(0, 58, 256, 6); }, 7);

// ---------------- the world ----------------
class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; blob: THREE.Mesh;
  constructor(parent: THREE.Object3D, blobTex: THREE.Texture) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ alphaTest: 0.5, side: THREE.DoubleSide }));
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(BODY, this.mat); this.mesh.customDepthMaterial = this.dmat;
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    this.mesh.castShadow = true; this.mesh.receiveShadow = true; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    this.blob = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), blobMaterial(blobTex)); this.blob.rotation.x = -Math.PI / 2; this.blob.layers.set(NOINK); this.blob.renderOrder = 0.5;
    parent.add(this.mesh, this.blob);
  }
}
class Card {
  mesh: THREE.Mesh; cut: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial;
  constructor(parent: THREE.Object3D) {
    this.cut = new THREE.MeshBasicMaterial({ alphaTest: 0.5, side: THREE.DoubleSide, toneMapped: true });
    this.soft = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.cut); this.mesh.layers.set(NOINK); this.mesh.renderOrder = 2;
    parent.add(this.mesh);
  }
}

export class ToonWorld {
  scene = new THREE.Scene();
  cam = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.2, 900);
  private renderer: THREE.WebGLRenderer;
  private composer: EffectComposer;
  private ink: InkPass; private lens: LensBlur; private grade: GradeEffect;
  private sun = new THREE.DirectionalLight("#fff3e0", 2.8); private hemi = new THREE.HemisphereLight("#dcecff", "#b49a78", 0.55);
  private skyMat: THREE.ShaderMaterial; private fog = new THREE.Fog("#b8d0ec", 25, 300);
  private actors: Actor[] = []; private cards: Card[] = [];
  private cache = new Map<string, THREE.CanvasTexture>(); private order: string[] = [];
  private blobTex: THREE.Texture;
  private sunKey = "";
  constructor(renderer: THREE.WebGLRenderer, logo: HTMLImageElement | null) {
    this.renderer = renderer;
    const S = this.scene;
    this.blobTex = tex(128, 128, (g) => fxContact(new Pen(g), "#5a5470"), 1, false); this.blobTex.generateMipmaps = false; this.blobTex.minFilter = THREE.LinearFilter;
    // sky dome: 5 elevation stops (lights.ts LOOK), written pre-inverted through the Neutral tone map
    const U: Record<string, THREE.IUniform> = {}; for (let i = 0; i < 5; i++) { U["c" + i] = { value: new THREE.Color() }; U["e" + i] = { value: 0 }; }
    this.skyMat = new THREE.ShaderMaterial({ uniforms: U, side: THREE.BackSide, depthWrite: false, fog: false,
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); gl_Position.z = gl_Position.w; }",
      fragmentShader: `uniform vec3 c0,c1,c2,c3,c4; uniform float e0,e1,e2,e3,e4; varying vec3 vP;
        void main(){ float e = degrees(asin(clamp(vP.y,-1.0,1.0))); vec3 c = c0;
          c = mix(c, c1, smoothstep(e0, e1, e)); c = mix(c, c2, smoothstep(e1, e2, e)); c = mix(c, c3, smoothstep(e2, e3, e)); c = mix(c, c4, smoothstep(e3, e4, e));
          gl_FragColor = vec4(c, 1.0); }` });
    const sky = new THREE.Mesh(new THREE.SphereGeometry(800, 32, 16), this.skyMat); sky.layers.set(NOINK); sky.frustumCulled = false; sky.renderOrder = -10; S.add(sky);
    this.sun.castShadow = true; this.sun.shadow.mapSize.set(2048, 2048); this.sun.shadow.camera.layers.enable(NOINK);
    S.add(this.sun, this.sun.target, this.hemi);
    this.build(logo);
    for (let i = 0; i < 6; i++) this.actors.push(new Actor(S, this.blobTex));
    for (let i = 0; i < 6; i++) this.cards.push(new Card(S));
    // post chain (skill order): world ink -> lens pre -> lens main -> bloom + Neutral tone map + grade
    this.composer = new EffectComposer(renderer, { multisampling: 4, frameBufferType: THREE.HalfFloatType });
    this.composer.addPass(new RenderPass(S, this.cam));
    this.ink = new InkPass(S, this.cam);
    this.composer.addPass(this.ink);
    this.lens = new LensBlur({ maxCoC: 24, nearScale: 1.2 });
    this.composer.addPass(new EffectPass(this.cam, this.lens.pre));
    this.composer.addPass(new EffectPass(this.cam, this.lens.main));
    const bloom = new BloomEffect({ blendFunction: BlendFunction.ADD, intensity: 0.5, luminanceThreshold: 1.0, luminanceSmoothing: 0.2, mipmapBlur: true, levels: 6, radius: 0.6 } as any);
    this.grade = new GradeEffect(GRADES.day);
    this.composer.addPass(new EffectPass(this.cam, bloom, new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }), this.grade));
    const v = new THREE.Vector2(); renderer.getSize(v); this.composer.setSize(v.x, v.y);
  }

  // ---- static set: street along x, shophouse fronts at z = -3.6, road z 0..9 ----
  private build(logo: HTMLImageElement | null) {
    const S = this.scene;
    const road = new THREE.Mesh(new THREE.PlaneGeometry(140, 40), lam({ map: (() => { const t = asphalt(); t.repeat.set(14, 4); return t; })() }));
    road.rotation.x = -Math.PI / 2; road.position.set(0, 0, 14); road.receiveShadow = true; S.add(road);
    for (let x = -60; x < 60; x += 6) { const d = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 0.16), lam({ color: "#f3efe4" })); d.rotation.x = -Math.PI / 2; d.position.set(x, 0.006, 5.2); d.receiveShadow = true; S.add(d); }
    const walkT = paving(); walkT.repeat.set(70, 2);
    const walk = new THREE.Mesh(new THREE.BoxGeometry(140, 0.16, 3.6), [lam({ color: "#a9a094" }), lam({ color: "#a9a094" }), lam({ map: walkT }), lam({ color: "#a9a094" }), lam({ color: "#9c938a" }), lam({ color: "#a9a094" })]);
    walk.position.set(0, 0.08, -1.8); walk.receiveShadow = true; walk.castShadow = true; S.add(walk);
    const curb = new THREE.Mesh(new THREE.BoxGeometry(140, 0.2, 0.22), lam({ map: stripes("#f2efe6", "#d9443c") }));
    (curb.material as THREE.MeshLambertMaterial).map!.repeat.set(70, 1); curb.position.set(0, 0.1, 0.0); curb.receiveShadow = true; S.add(curb);
    // shophouses
    const SHOPS: Shop[] = [
      { wall: "#e7d3a6", trim: "#f4ead2", floors: 3, sign: "ร้านทอง เฮงเฮง", signCol: "#c0353a", signInk: "#ffe08a" },
      { wall: "#cfe0d6", trim: "#f2f4ec", floors: 2, sign: "ก๋วยเตี๋ยวเรือ", signCol: "#2f5aa8", signInk: "#ffffff", shutter: 0.8 },
      { wall: "#f0c9a4", trim: "#fbe9d6", floors: 3, sign: "ร้านยา", signCol: "#2a9d63", signInk: "#ffffff", shutter: 0.9 },
      { wall: "#f6f1e6", trim: "#ffffff", floors: 3, sign: "คลินิกทันตกรรมบางปะอิน", signCol: "#ffffff", signInk: "#178a8a", clinic: true, logo },
      { wall: "#f3dcc0", trim: "#fbefe0", floors: 2, sign: "ชานมไข่มุก", signCol: "#7a4a2a", signInk: "#ffe7c2", shutter: 0.95 },
      { wall: "#e9b07e", trim: "#f6dcc2", floors: 3, sign: "ร้านซ่อมมือถือ", signCol: "#1f2a44", signInk: "#ffd166", shutter: 0.4 },
      { wall: "#c7d8ea", trim: "#eef3f9", floors: 2, sign: "ร้านข้าวมันไก่", signCol: "#e8a33a", signInk: "#1f2a44", shutter: 0.85 },
      { wall: "#ead9b6", trim: "#f7efdc", floors: 3, sign: "ร้านเสริมสวย", signCol: "#d65a8a", signInk: "#ffffff", shutter: 0.6 },
    ];
    const WID = 4.4;
    for (let k = -7; k <= 10; k++) {
      const o = SHOPS[(k + 3 + 80) % 8], x = k * WID, hm = o.floors === 3 ? 10.4 : 7.4, D = 10;
      const front = lam({ map: shopFacade(WID, hm, o, k + 2) }), side = lam({ color: o.wall }), top = lam({ color: "#9a948c" });
      const b = new THREE.Mesh(new THREE.BoxGeometry(WID, hm, D), [side, side, top, top, front, side]);
      b.position.set(x, hm / 2, -3.6 - D / 2); b.castShadow = true; b.receiveShadow = true; S.add(b);
      // awning over the ground floor
      if (!o.clinic) {
        const aw = new THREE.Mesh(new THREE.BoxGeometry(WID - 0.3, 0.08, 1.3), [lam({ color: o.signCol ?? "#c0353a" }), lam({ color: o.signCol ?? "#c0353a" }),
          lam({ map: stripes(o.signCol ?? "#c0353a", "#f4efe2") }), lam({ color: "#e9e2d2" }), lam({ map: stripes(o.signCol ?? "#c0353a", "#f4efe2") }), lam({ color: "#e9e2d2" })]);
        aw.position.set(x, 2.5, -3.0); aw.rotation.x = 0.22; aw.castShadow = true; aw.receiveShadow = true; S.add(aw);
      } else {
        const canopy = new THREE.Mesh(new THREE.BoxGeometry(WID - 0.3, 0.12, 1.0), lam({ color: "#3cc6c2" })); canopy.position.set(x, 2.55, -3.1); canopy.castShadow = true; S.add(canopy);
        for (const dx of [-1.6, 1.6]) { const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.22, 0.5, 16), lam({ color: "#d9d2c6" })); pot.position.set(x + dx, 0.41, -3.2); pot.castShadow = true; S.add(pot);
          const bush = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), lam({ color: "#5fa65a" })); bush.position.set(x + dx, 0.95, -3.2); bush.scale.set(1, 1.2, 1); bush.castShadow = true; S.add(bush); }
      }
    }
    // power poles + sagging wire bundles (a very Thai street)
    const poleM = lam({ color: "#c9c4bc" }), wireM = lam({ color: "#2a262c" });
    const poles = [-24.2, -15.4, -6.6, 11, 19.8, 28.6];
    for (const x of poles) {
      const p = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.19, 9.5, 12), poleM); p.position.set(x, 4.75, -0.45); p.castShadow = true; S.add(p);
      const bar = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.14, 1.6), poleM); bar.position.set(x, 8.7, -0.45); bar.castShadow = true; S.add(bar);
    }
    for (let k = 0; k < poles.length - 1; k++) for (const [dz, dy, sag] of [[-0.6, 8.65, 0.7], [0.0, 8.4, 0.9], [0.55, 8.6, 0.6], [0.2, 7.9, 1.1], [-0.3, 7.7, 1.25]] as V3[]) {
      const a = poles[k], b = poles[k + 1], pts: THREE.Vector3[] = [];
      for (let i = 0; i <= 16; i++) { const u = i / 16; pts.push(new THREE.Vector3(a + (b - a) * u, dy - sag * 4 * u * (1 - u), -0.45 + dz)); }
      const w = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 32, 0.025, 5, false), wireM); w.castShadow = true; S.add(w);
    }
    // street trees
    for (const x of [-11, 17.8, 24.6]) {
      const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, 2.6, 10), lam({ color: "#7a5a3c" })); tr.position.set(x, 1.3, -0.9); tr.castShadow = true; S.add(tr);
      for (const [dx, dy, s] of [[0, 3.0, 1.2], [0.7, 2.7, 0.9], [-0.6, 2.8, 0.95], [0.1, 3.6, 0.85]] as V3[]) {
        const c = new THREE.Mesh(new THREE.IcosahedronGeometry(s, 1), lam({ color: "#5c9f4e" })); c.position.set(x + dx, dy, -0.9); c.castShadow = true; c.receiveShadow = true; S.add(c);
      }
    }
    // bubble-tea stall in front of the tea shop (x = 4.4): wooden cart, striped umbrella, cups
    const SX = 4.4, SZ = -2.0;
    const cart = new THREE.Mesh(new THREE.BoxGeometry(1.9, 1.0, 0.8), lam({ color: "#b8834e" })); cart.position.set(SX, 0.66, SZ); cart.castShadow = true; cart.receiveShadow = true; S.add(cart);
    const ctop = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.08, 0.9), lam({ color: "#f2ead8" })); ctop.position.set(SX, 1.2, SZ); ctop.castShadow = true; S.add(ctop);
    const bannerT = tex(512, 160, (g) => { g.fillStyle = "#fff4e2"; g.fillRect(0, 0, 512, 160); g.fillStyle = "#7a4a2a"; g.font = `700 78px ${FONT}`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("ชานมไข่มุก", 256, 84); }, 1, false);
    const banner = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 0.56), new THREE.MeshBasicMaterial({ map: bannerT })); banner.position.set(SX, 0.7, SZ + 0.41); S.add(banner);
    for (const dx of [-0.6, -0.3, 0.0]) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.055, 0.22, 12), lam({ color: "#d4a06a" })); c.position.set(SX + dx, 1.35, SZ + 0.1); c.castShadow = true; S.add(c); }
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.3, 8), lam({ color: "#e9e2d2" })); pole.position.set(SX + 0.8, 2.3, SZ); S.add(pole);
    const umb = new THREE.Mesh(new THREE.ConeGeometry(1.5, 0.6, 12, 1, true), lam({ map: (() => { const t = stripes("#ef4a5c", "#fff4e2"); t.repeat.set(3, 1); return t; })(), side: THREE.DoubleSide })); umb.position.set(SX + 0.8, 3.4, SZ); umb.castShadow = true; S.add(umb);
    for (const dx of [-0.7, 0.7]) { const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.08, 16), lam({ color: "#3a3238" })); wh.rotation.x = Math.PI / 2; wh.position.set(SX + dx, 0.36, SZ + 0.42); S.add(wh); }
    // uncle's parked car (red hatchback) on the road
    const car = new THREE.Group(); car.position.set(14.5, 0, 1.6); S.add(car);
    const red = lam({ color: "#d9443c" }), glass = lam({ color: "#5d7891" });
    const body = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.8, 1.7), red); body.position.y = 0.75; body.castShadow = true; car.add(body);
    const cab = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.62, 1.55), glass); cab.position.set(-0.25, 1.45, 0); cab.castShadow = true; car.add(cab);
    const roofM = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.08, 1.5), red); roofM.position.set(-0.25, 1.8, 0); car.add(roofM);
    for (const [dx, dz] of [[-1.25, 0.82], [1.25, 0.82], [-1.25, -0.82], [1.25, -0.82]]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.26, 18), lam({ color: "#2a262c" })); w.rotation.x = Math.PI / 2; w.position.set(dx, 0.36, dz); w.castShadow = true; car.add(w); }
    // a bed for the "can't sleep" beat (bedroom corner set far down the street, x = 60)
    const room = new THREE.Group(); room.position.set(60, 0.17, -1.5); S.add(room);
    const wallR = new THREE.Mesh(new THREE.BoxGeometry(8, 5, 0.2), lam({ color: "#8ea3cf" })); wallR.position.set(0, 2.5, -2.2); wallR.receiveShadow = true; room.add(wallR);
    const floorR = new THREE.Mesh(new THREE.BoxGeometry(8, 0.1, 6), lam({ color: "#b98a5e" })); floorR.position.set(0, 0.05, 0.6); floorR.receiveShadow = true; room.add(floorR);
    const bed = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.5, 2.0), lam({ color: "#f2f4f8" })); bed.position.set(0, 0.35, -0.9); bed.castShadow = true; bed.receiveShadow = true; room.add(bed);
    const blanket = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.16, 1.7), lam({ color: "#6f8fd6" })); blanket.position.set(0.15, 0.66, -0.75); blanket.castShadow = true; room.add(blanket);
    const winM = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.3), new THREE.MeshBasicMaterial({ color: "#1f2f5a" })); winM.position.set(-2.2, 3.0, -2.09); room.add(winM);
    const moon = new THREE.Mesh(new THREE.CircleGeometry(0.22, 24), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.8, 2) })); moon.position.set(-1.9, 3.3, -2.08); room.add(moon);
  }

  private texFor(key: string, w: number, h: number, draw: (p: Pen) => void, sx = 1) {
    let t = this.cache.get(key);
    if (t) return t;
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const g = c.getContext("2d")!; g.scale(sx, sx); draw(new Pen(g));
    t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    this.cache.set(key, t); this.order.push(key);
    if (this.order.length > 90) { const k = this.order.shift()!; this.cache.get(k)?.dispose(); this.cache.delete(k); }
    return t;
  }

  /** pose and render one frame into the shared canvas */
  frame(F: Frame) {
    const r = this.renderer, cam = this.cam, L = LIGHTS[F.light], K = LOOK[F.light];
    cam.fov = F.fov ?? 40; cam.aspect = 1080 / 1920; cam.position.set(...F.pos); cam.up.set(0, 1, 0); cam.lookAt(...F.look);
    if (F.roll) cam.rotateZ(F.roll);
    if (F.shakePx) { const k = F.shakePx * 0.002; cam.position.x += k; cam.position.y += k * 0.6; }
    cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    // sun: camera-relative azimuth / elevation (frozen per shot by the caller passing the same values)
    const fwd = new THREE.Vector3(); cam.getWorldDirection(fwd); fwd.y = 0; fwd.normalize();
    const right = new THREE.Vector3(-fwd.z, 0, fwd.x);
    const az = THREE.MathUtils.degToRad(F.sunAz ?? (F.light === "day" ? 128 : L.az)), el = THREE.MathUtils.degToRad(F.sunEl ?? L.el);
    const dir = fwd.clone().multiplyScalar(Math.cos(az)).addScaledVector(right, Math.sin(az)).multiplyScalar(Math.cos(el)).add(new THREE.Vector3(0, Math.sin(el), 0)).normalize();
    const focus = new THREE.Vector3(...(F.focus ?? F.look));
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    this.sun.position.copy(focus).addScaledVector(dir, 120); this.sun.target.position.copy(focus); this.sun.target.updateMatrixWorld();
    const sc = this.sun.shadow.camera; sc.left = -22; sc.right = 22; sc.top = 22; sc.bottom = -22; sc.near = 1; sc.far = 260; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * 2;
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    const su = this.skyMat.uniforms; K.sky.c.forEach((h, i) => untone(h, su["c" + i].value)); K.sky.e.forEach((e, i) => (su["e" + i].value = e));
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear; this.fog.far = L.fogFar; this.scene.fog = this.fog;
    // characters: camera-facing cards (yaw only) with a contact blob under the feet
    const cr = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
    const light2D = Math.round(Math.atan2(-dir.y, dir.dot(cr)) / (Math.PI / 4)) * (Math.PI / 4);   // canvas angle the sun comes from
    this.actors.forEach((a, i) => {
      const s = F.actors[i]; a.mesh.visible = a.blob.visible = !!s; if (!s) return;
      const o = OUTFITS[s.who as string], fo: FrontOpts = { light: light2D, seed: i + 1, ...s.opts };
      const key = `${s.who}|` + JSON.stringify(fo, (_k, v) => (typeof v === "number" ? Math.round(v * 60) / 60 : v));
      const t = this.texFor(key, CW, CH, (p) => bodyFront(p, o, fo), CS);
      a.mat.map = t; a.dmat.map = t; a.mat.needsUpdate = a.mat.map !== t;
      const y = s.y ?? 0.16, sc2 = s.scale ?? 1;
      a.mesh.position.set(s.x, y, s.z); a.mesh.scale.setScalar(sc2); a.mesh.castShadow = L.actorShadow;
      a.mesh.rotation.set(0, Math.atan2(cam.position.x - s.x, cam.position.z - s.z), 0);
      a.blob.position.set(s.x, y + 0.012, s.z); a.blob.scale.set(0.95 * sc2, 0.55 * sc2, 1);
    });
    // effect cards
    this.cards.forEach((c, i) => {
      const s = F.fx?.[i]; c.mesh.visible = !!s; if (!s) return;
      const q = Math.round(s.t * 24) / 24, soft = s.kind === "puff" || s.kind === "smoke";
      let t: THREE.Texture;
      if (s.kind === "burst") t = this.texFor(`burst|${q}|${s.col}`, 500, 500, (p) => fxBurst(p, q, s.col ?? "#fff3b0"));
      else if (s.kind === "splash") t = this.texFor(`splash|${q}`, 400, 400, (p) => { p.g.scale(0.5, 0.5); fxSplash(p, q); });
      else if (s.kind === "stars") t = this.texFor(`stars|${q}`, 420, 210, (p) => fxStars(p, q));
      else if (s.kind === "zzz") t = this.texFor(`zzz|${q}`, 500, 500, (p) => fxBurst(p, q, "#ff6b5e", 8, 30, 200));
      else if (s.kind === "suck") t = this.texFor(`suck|${q}`, 300, 300, (p) => { for (let k = 0; k < 3; k++) { const u = (q + k / 3) % 1; p.arc(150, 260 - 200 * u, 60 + 50 * u, 22, 200, 340, 9, "#ffffff"); } });
      else t = this.texFor(`puff|${q}|${s.col ?? ""}`, 300, 300, (p) => { if (s.kind === "smoke") { const g = p.g; for (let k = 0; k < 4; k++) { const u = q + k * 0.12; g.fillStyle = `rgba(215,215,222,${0.7 * (1 - u)})`; g.beginPath(); g.ellipse(150 + 30 * Math.sin(u * 7 + k), 240 - 190 * u, 40 + 60 * u, 34 + 50 * u, 0, 0, 7); g.fill(); } } else fxPuff(p, q); });
      c.mesh.material = soft ? c.soft : c.cut; (c.mesh.material as THREE.MeshBasicMaterial).map = t;
      c.mesh.position.set(s.x, s.y, s.z); c.mesh.scale.set(s.w, s.h ?? s.w, 1);
      c.mesh.quaternion.copy(cam.quaternion);
    });
    noInkFallback(this.scene);
    // lens: focus distance along the view axis
    const fd = new THREE.Vector3(); cam.getWorldDirection(fd);
    this.lens.focus = Math.max(0.3, focus.clone().sub(cam.position).dot(fd)); this.lens.cInf = F.cInf ?? 0;
    gradeFor(this.grade, F.light);
    const tm = r.toneMapping; r.toneMapping = THREE.NoToneMapping;
    this.composer.render();
    r.toneMapping = tm;
  }
}

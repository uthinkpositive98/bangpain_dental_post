// ep14 รากฟันเทียม ทำงานยังไง? — worked example for the cut3d engine (tools/cut3d/lib.js, passed in as L).
// frame(t, L): pose everything for time t (the engine hides/resets all props before each call) and return {blur, flash}.
// Beats come from the narration (script.txt, one line per beat); marks from episode.json.
export function frame(t, L) {
  const { bs, be, mk, B, seg, ease, eout, ein, lerp, clamp, GUM_TOP, setCam, chip, sparkleAt,
    centerTooth: lost, looseCrown: fake, newCrown, implant, abut, upper, food, cells, glow, warn, inflam, inflamF, brush } = L;
  let blur = 0, flash = 0;
  const t3 = mk(2, 'so', 0), implantDown = t3 + 2.0;
  const healDone = mk(4, 'heal_end', .75);
  const abutT = mk(5, 'so', .55), crownT = mk(6, 'so', .55);
  const seated = () => { implant.visible = true; abut.visible = true; newCrown.visible = true; newCrown.position.set(0, .9, 0); cellsOn(); };
  const cellsOn = () => cells.forEach(c => { c.visible = true; c.position.copy(c.userData.to); c.scale.setScalar(1); });
  if (t >= bs(1)) lost.visible = false;

  if (t < be(0)) {                         // hook — the natural tooth pops out, a loose fake tooth drops in
    const a = bs(0), d = B[0].dur;
    const k = seg(t, a + .15, a + .9);
    lost.position.set(lerp(0, -2, k), .7 + 14 * eout(k) - 6 * k * k, 2 * k); lost.rotation.set(k * 5, 0, k * 3);
    if (k >= 1) lost.visible = false;
    const fk = mk(0, 'fake', .55);
    if (t > fk) { fake.visible = true; const kf = seg(t, fk, fk + .5); fake.position.set(0, lerp(12, GUM_TOP + .6, eout(kf)) + (kf >= 1 ? .08 * Math.sin((t - fk) * 25) * Math.exp(-(t - fk - .5) * 6) : 0), 0); }
    setCam('wide', 'gap', ease(seg(t, a + .6, a + d)));
  } else if (t < be(1)) {                  // chew -> the fake tooth flies off
    const a = bs(1);
    const hit = mk(1, 'fly', .45);
    food.visible = t < hit + .1;
    const down = ein(seg(t, a, hit)); const up = eout(seg(t, hit + .15, hit + .8));
    upper.position.y = lerp(11, 3.5, down) + (t > hit ? lerp(0, 7.5, up) : 0);
    if (t < hit) { food.position.y = Math.min(5.8, upper.position.y - .6); food.scale.y = .8 * clamp((upper.position.y - .6 - 3.4) / 2.4, .35, 1); }
    fake.visible = true;
    if (t < hit) fake.position.set(0, GUM_TOP + .6, 0);
    else { const k = seg(t, hit, hit + 1.1); fake.position.set(lerp(0, 13, eout(k)), GUM_TOP + .6 + 7 * Math.sin(k * Math.PI) * .7, lerp(0, 4, k)); fake.rotation.set(k * 8, k * 3, -k * 10); }
    flash = t > hit ? .25 * Math.exp(-(t - hit) * 12) : 0;
    setCam('bite', 'bite', 0, t > hit ? .5 * Math.exp(-(t - hit) * 5) : 0, t);
  } else if (t < be(2)) {                  // titanium implant spins down into the bone
    const a = bs(2), d = B[2].dur;
    implant.visible = true; const k = seg(t, t3, implantDown);
    implant.position.y = lerp(13, 0, eout(k)); implant.rotation.y = -k * 26;
    blur = t < a + .35 ? (1 - seg(t, a, a + .35)) * 14 : 0;
    setCam('high', 'bone', ease(seg(t, a, a + d * .9)), t > implantDown && t < implantDown + .4 ? .15 * (1 - seg(t, implantDown, implantDown + .4)) : 0, t);
    if (t > implantDown) sparkleAt(0, 0, 0, seg(t, implantDown, implantDown + .6));
    chip('ti', 'รากฟันเทียมไทเทเนียม', 'dark', 190, t, t3 + .3, be(2) - .1);
  } else if (t < be(3)) {                  // loaded too early -> wobble
    const a = bs(3);
    implant.visible = true; newCrown.visible = true;
    newCrown.position.set(0, lerp(9, .9, eout(seg(t, a, a + .45))), 0);
    const wob = mk(3, 'wobble', .55);
    upper.position.y = lerp(11, 2.4, ein(seg(t, wob - .5, wob))) + (t > wob ? 2 + Math.sin((t - wob) * 18) * .4 : 0) * clamp((t - wob) * 3);
    if (t > wob + .3) upper.position.y = lerp(upper.position.y, 11, seg(t, wob + .3, wob + .9));
    const w = t > wob - .1 ? Math.sin((t - wob) * 22) * .16 * clamp((t - wob + .1) * 3) : 0;
    implant.rotation.z = w; newCrown.rotation.z = w; newCrown.position.x = -w * 2.5;
    warn.material.opacity = t > wob ? .9 * (.5 + .5 * Math.sin((t - wob) * 14)) : 0; warn.scale.setScalar(1 + .08 * Math.sin(t * 14));
    setCam('neck', 'neck', 0, t > wob ? .1 : 0, t);
    chip('wob', '⚠ รากเทียมโยก!', 'red', 190, t, wob, be(3) - .1, -3);
  } else if (t < be(4)) {                  // wait 3–6 months: bone grows around it (osseointegration)
    const a = bs(4), d = B[4].dur;
    implant.visible = true;
    if (t < a + .6) { newCrown.visible = true; newCrown.position.set(0, .9 + 12 * ein(seg(t, a, a + .6)), 0); }
    const g0 = a + .4, g1 = healDone;
    cells.forEach(c => { const k = eout(seg(t, g0 + c.userData.d * (g1 - g0) * .5, g1 - (.5 - c.userData.d) * .3)); c.visible = k > 0; c.position.lerpVectors(c.userData.from, c.userData.to, k); c.scale.setScalar(.6 + .4 * k); });
    glow.material.opacity = .22 * Math.sin(seg(t, g0, g1 + .8) * Math.PI);
    L.calendar('เดือนที่', Math.min(6, Math.floor(seg(t, g0, g1) * 6.99)), t > be(4) - .3 ? 1 - seg(t, be(4) - .3, be(4)) : L.back(seg(t, a + .2, a + .55)));
    chip('osseo', 'Osseointegration', 'yel', 500, t, mk(4, 'term', .8), be(4) - .1);
    setCam('bone', 'boneC', ease(seg(t, a, a + d)));
  } else if (t < be(5)) {                  // under the gum -> abutment
    const a = bs(5);
    implant.visible = true; cellsOn();
    const bump = seg(t, a + .2, abutT - .3);
    upper.position.y = lerp(11, 3.3, Math.sin(bump * Math.PI));
    food.visible = bump > 0 && bump < 1; food.position.set(0, GUM_TOP + 1.3 * (1 - .3 * Math.sin(bump * Math.PI)), 0.3); food.scale.set(1.25, .8 * (1 - .25 * Math.sin(bump * Math.PI)), 1);
    if (t > abutT) { abut.visible = true; const k = seg(t, abutT, abutT + .9); abut.position.set(0, lerp(9, .05, eout(k)), 0); abut.rotation.y = -k * 14;
      if (k >= 1) sparkleAt(0, 1.6, 0, seg(t, abutT + .9, abutT + 1.5), 2); }
    blur = t < a + .35 ? (1 - seg(t, a, a + .35)) * 12 : 0;
    setCam('gap', 'neck', ease(seg(t, abutT - .2, abutT + 1)));
    chip('abut', 'Abutment = แกนเชื่อม', 'dark', 190, t, mk(5, 'term', .82), be(5) - .1);
  } else if (t < be(6)) {                  // grey metal -> ceramic crown
    implant.visible = true; abut.visible = true; cellsOn();
    if (t > crownT) { newCrown.visible = true; const k = seg(t, crownT, crownT + .55); newCrown.position.set(0, lerp(10, .9, ein(k)), 0);
      if (k >= 1) { sparkleAt(0, 3, 0, seg(t, crownT + .55, crownT + 1.3), 3.4); flash = .35 * Math.exp(-(t - crownT - .55) * 10); } }
    setCam('neck', 'crown', ease(seg(t, crownT - .3, crownT + 1.2)), t > crownT + .55 && t < crownT + .9 ? .12 : 0, t);
    chip('cer', 'ครอบฟันเซรามิก', 'green', 190, t, crownT + .5, be(6) - .1);
  } else if (t < be(7)) {                  // germs at the gum line -> inflammation
    const a = bs(7), d = B[7].dur; seated();
    L.germsArrive(t, a + .2);
    const inf = seg(t, mk(7, 'inflame', .65), mk(7, 'inflame', .65) + .8); inflam.material.opacity = .55 * inf; inflamF.material.opacity = .45 * inf;
    setCam('crown', 'gumline', ease(seg(t, a, a + d * .7)));
    chip('inf', 'เหงือกอักเสบรอบรากเทียม', 'red', 190, t, mk(7, 'inflame', .65), be(7) - .1, 2);
  } else if (t < be(8)) {                  // brush, floss, check-ups
    const a = bs(8), d = B[8].dur; seated();
    const bk = seg(t, a + .1, a + d * .45);
    brush.visible = bk > 0 && bk < 1; brush.position.set(Math.sin(bk * Math.PI * 4) * 3.2, GUM_TOP + 1.4, 2.0); brush.rotation.set(0, 0, Math.sin(t * 30) * .04);
    L.germsClear(t, a + .25, a + .25 + d * .4);
    const inf = 1 - seg(t, a + .2, a + d * .45); inflam.material.opacity = .55 * inf; inflamF.material.opacity = .45 * inf;
    if (bk >= 1) sparkleAt(0, 3, 0, seg(t, a + d * .45, a + d * .45 + .7), 3.6);
    setCam('gumline', 'crown', ease(seg(t, a + d * .4, a + d)));
    chip('b1', '🪥 แปรงวันละ 2 ครั้ง', 'green', 170, t, mk(8, 'c1', 0), be(8) - .1);
    chip('b2', '🧵 ใช้ไหมขัดฟัน', 'dark', 300, t, mk(8, 'c2', .4), be(8) - .1);
    chip('b3', '🦷 ตรวจทุก 6 เดือน', 'yel', 430, t, mk(8, 'c3', .62), be(8) - .1);
  } else if (t < be(9)) {                  // myth: "only lasts a few years?" -> no
    const a = bs(9), d = B[9].dur; seated();
    upper.position.y = 11 - 7.4 * Math.pow(Math.max(0, Math.sin((t - a) * 2.4 * Math.PI)), 2) * clamp((t - a) * 2);
    blur = t < a + .35 ? (1 - seg(t, a, a + .35)) * 12 : 0;
    setCam('ortho', 'wide', ease(seg(t, a, a + d)));
    const no = mk(9, 'no', .5);
    chip('m1', 'ใช้ได้ไม่กี่ปี ?', 'dark', 190, t, a + .2, no - .05);
    chip('m2', '✕ ไม่จริง!', 'red', 330, t, no, be(9) - .1, -4);
    chip('m3', 'ดูแลดี ใช้ได้นาน 10 ปี+', 'green', 190, t, mk(9, 'care', .7), be(9) - .1);
  } else if (t < be(10)) {                 // congratulations — back to the opening framing, confetti
    const a = bs(10), d = B[10].dur; seated();
    L.confetti(t, a);
    sparkleAt(0, 3, 0, seg(t, a, a + .9), 3.8);
    setCam('gap', 'wide', ease(seg(t, a, a + d * .8)));
  } else {                                 // under the end card
    seated(); setCam('wide', 'wide', 0);
  }
  return { blur, flash };
}

// cover: exploded implant (crown / abutment / implant) floating over the jaw; returns the part labels
export function cover(t, L) {
  const { lerp, clamp, centerTooth, implant, abut, newCrown, halo, upper, cam, sparkleAt } = L;
  centerTooth.visible = false; upper.position.y = 40;
  const f = Math.sin(t * 2.2);
  implant.visible = true; implant.rotation.y = -t * 1.2;
  abut.visible = true; abut.position.set(0, 3.0 + .15 * f, 0); abut.rotation.y = -t * 1.2;
  newCrown.visible = true; newCrown.position.set(0, 6.6 + .25 * f, 0); newCrown.rotation.set(0, t * .4 - .2, 0);
  halo.material.opacity = .3; halo.position.set(0, 3.2, -1.5);
  sparkleAt(0, 3.4, 0, (t * .7) % 1, 4.2);
  const k = clamp(t / 2);
  cam.position.set(lerp(9, 8, k), lerp(10, 9.6, k), lerp(47, 43.5, k)); cam.lookAt(0, 7.8, 0);
  return [
    { text: 'ครอบฟัน', at: [1.9, newCrown.position.y + 1.6, 0] },
    { text: 'แกนเชื่อม', at: [1.0, abut.position.y + 1.2, 0] },
    { text: 'รากเทียม', at: [1.1, -2.6, 0] },
  ];
}

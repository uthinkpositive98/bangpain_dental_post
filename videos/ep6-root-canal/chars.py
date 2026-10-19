"""Characters for ep5 (TMJ): patient (front), side-view jaw with an x-ray lens, the joint close-up (condyle + disc),
the chewing muscle, the dentist (หมอนวรัตน์), occlusal splint, props. Same ink/pastel style as tools/kawaii.py."""
import math, random, os
import skia
from tools.kawaii import *  # noqa: F401,F403

SKIN = '#FFE0CC'; SKIN_D = '#F6C3A6'; HAIR = '#3A2A33'; HAIR_H = '#5B4450'
MUSC = '#FF9AA8'; MUSC_D = '#F06C82'; DISC = '#FFB3C7'; DISC_D = '#F2849F'
COAT = '#FFFFFF'; SCRUB = '#7FD8CF'; RED = '#FF5A5A'

def _poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p

def fill(c, p, col, a=255, stroke=7):
    c.drawPath(p, P(col, a) if isinstance(col, str) else col)
    if stroke: c.drawPath(p, P(INK, a, stroke=stroke))

# ---------------------------------------------------------------- simple face for people
def pface(c, x, y, s=1.0, mood='smile', open_k=0.0, blink=1.0, look=0.0):
    for sx in (-1, 1):
        ex, ey = x + sx * 52 * s + look * 6 * s, y
        if mood in ('happy', 'joy'):
            p = skia.Path(); p.moveTo(ex - 15 * s, ey + 6 * s); p.quadTo(ex, ey - 18 * s, ex + 15 * s, ey + 6 * s)
            c.drawPath(p, P(INK, stroke=7 * s))
        elif mood in ('pain', 'squeeze'):
            p = skia.Path(); p.moveTo(ex + sx * 14 * s, ey - 12 * s); p.lineTo(ex - sx * 12 * s, ey); p.lineTo(ex + sx * 14 * s, ey + 12 * s)
            c.drawPath(p, P(INK, stroke=7 * s))
        elif mood == 'sleep':
            p = skia.Path(); p.moveTo(ex - 15 * s, ey); p.quadTo(ex, ey + 13 * s, ex + 15 * s, ey)
            c.drawPath(p, P(INK, stroke=6 * s))
        else:
            ry = 19 * s * max(0.12, blink)
            c.drawOval(RR(ex, ey, 28 * s, ry * 2), P(INK))
            if blink > 0.4: c.drawCircle(ex + 5 * s, ey - 7 * s, 6 * s, P(WHITE))
            if mood in ('worry', 'sad'):
                p = skia.Path(); p.moveTo(ex - 16 * s, ey - (30 if sx < 0 else 40) * s); p.lineTo(ex + 16 * s, ey - (40 if sx < 0 else 30) * s)
                c.drawPath(p, P(INK, stroke=5 * s))
        c.drawOval(RR(x + sx * 82 * s, y + 34 * s, 40 * s, 20 * s), P(PINK, 170))
    my = y + 52 * s
    if open_k > 0.04:
        h = (14 + 70 * open_k) * s
        p = skia.Path(); p.addRoundRect(RR(x, my + h / 2 - 6 * s, 52 * s, h), 22 * s, 22 * s)
        c.drawPath(p, P('#7A2E3B')); c.drawPath(p, P(INK, stroke=6 * s))
        c.drawOval(RR(x, my + h - 12 * s, 30 * s, 12 * s * min(1, open_k * 3)), P(CORAL))
    elif mood in ('smile', 'happy', 'sleep'):
        p = skia.Path(); p.moveTo(x - 18 * s, my); p.quadTo(x, my + 18 * s, x + 18 * s, my)
        c.drawPath(p, P(INK, stroke=6 * s))
    elif mood == 'joy':
        p = skia.Path(); p.moveTo(x - 26 * s, my - 4 * s); p.quadTo(x, my + 44 * s, x + 26 * s, my - 4 * s); p.close()
        c.drawPath(p, P(INK)); c.drawOval(RR(x, my + 12 * s, 20 * s, 10 * s), P(CORAL))
    elif mood in ('pain', 'worry', 'sad'):
        p = skia.Path(); p.moveTo(x - 18 * s, my + 12 * s); p.quadTo(x, my - 4 * s, x + 18 * s, my + 12 * s)
        c.drawPath(p, P(INK, stroke=6 * s))
        if mood == 'pain':   # clenched wavy mouth
            p = skia.Path(); p.moveTo(x - 20 * s, my + 6 * s)
            for i in range(1, 5): p.lineTo(x - 20 * s + i * 10 * s, my + (0 if i % 2 else 10) * s)
            c.drawPath(p, P(INK, stroke=5 * s))

# ---------------------------------------------------------------- patient (front view)
def person(c, x, y, s=1.0, mood='smile', open_k=0.0, t=0.0, hand=0.0, shirt='#9BD7FF', seed=0, bob=True, ouch=0.0):
    """head centre at (x, y)"""
    yy = y + (math.sin(t * 3 + seed) * 6 if bob else 0)
    c.save(); c.translate(x, yy); c.scale(s, s)
    # body
    body = skia.Path(); body.addRoundRect(skia.Rect.MakeLTRB(-175, 150, 175, 520), 120, 120)
    fill(c, body, lingrad((0, 150), (0, 520), shirt, '#6FB8E8'))
    c.drawLine(-60, 175, 0, 230, P(INK, stroke=6)); c.drawLine(60, 175, 0, 230, P(INK, stroke=6))
    neck = skia.Path(); neck.addRoundRect(RR(0, 150, 90, 70), 30, 30); fill(c, neck, SKIN, stroke=6)
    # back hair
    bh = skia.Path(); bh.addRoundRect(skia.Rect.MakeLTRB(-215, -175, 215, 175), 150, 150); fill(c, bh, HAIR)
    # ears
    for sx in (-1, 1):
        e = skia.Path(); e.addOval(RR(sx * 172, 15, 54, 74)); fill(c, e, SKIN, stroke=6)
    # head
    hd = skia.Path(); hd.addOval(RR(0, 0, 340, 330)); fill(c, hd, lingrad((0, -165), (0, 165), '#FFEADB', SKIN))
    # fringe
    fr = skia.Path(); fr.moveTo(-172, -10); fr.cubicTo(-170, -150, -60, -190, 20, -175)
    fr.cubicTo(110, -170, 175, -110, 172, -10); fr.cubicTo(120, -70, 60, -95, 10, -60)
    fr.cubicTo(-40, -95, -120, -70, -172, -10); fr.close()
    fill(c, fr, HAIR)
    c.drawPath(_poly([(-90, -130), (-40, -150)], False), P(HAIR_H, stroke=10))
    pface(c, 0, 10, 1.0, mood, open_k, blink_at(t, seed), 0)
    if ouch > 0:   # pain zap near the right ear
        a = 255 * ouch
        for i, (dx, dy) in enumerate(((230, -40), (255, 20), (235, 80))):
            z = _poly([(dx, dy - 22), (dx + 16, dy - 6), (dx + 2, dy), (dx + 20, dy + 20)], False)
            c.drawPath(z, P(RED, a, stroke=7))
        c.drawCircle(185, 55, 40 + 8 * math.sin(t * 12), P(RED, 60 * ouch))
    if hand > 0:   # hand on the cheek
        hx, hy = 175 - 10 * (1 - hand), 70
        arm = skia.Path(); arm.moveTo(150, 330); arm.quadTo(230, 230, hx + 5, hy + 40)
        c.drawPath(arm, P(INK, stroke=48)); c.drawPath(arm, P(shirt, stroke=36))
        h = skia.Path(); h.addOval(RR(hx, hy, 74, 86)); fill(c, h, SKIN, stroke=6)
    c.restore()

# ---------------------------------------------------------------- side view with the x-ray lens
PIVOT = (-10, 40)     # TMJ (in front of the ear), head-local coords

def _rot(px, py, ang, ox, oy):
    a = math.radians(ang); dx, dy = px - ox, py - oy
    return ox + dx * math.cos(a) - dy * math.sin(a), oy + dx * math.sin(a) + dy * math.cos(a)

def mandible_path():
    p = skia.Path()
    p.moveTo(-28, 30)                       # back of condyle neck
    p.cubicTo(-40, 90, -46, 150, -30, 200)  # ramus back edge to angle
    p.cubicTo(-18, 228, 20, 232, 80, 228)   # lower border
    p.cubicTo(140, 226, 190, 230, 214, 214) # to chin
    p.cubicTo(232, 196, 226, 160, 210, 140) # chin front
    p.lineTo(200, 132); p.lineTo(64, 136)   # alveolar crest (teeth sit here)
    p.cubicTo(52, 120, 54, 90, 60, 70)      # coronoid front
    p.cubicTo(40, 82, 22, 82, 12, 52)       # sigmoid notch
    p.lineTo(8, 36)
    p.close()
    return p
MANDIBLE = mandible_path()

def side_head(c, x, y, s=1.0, open_k=0.0, t=0.0, mood='smile', lens=True, glow=0.0, pain=0.0, labels=None, body=True):
    """cute profile facing right; open_k 0..1 opens the jaw (rotation about the TMJ + a little glide)"""
    ang = 22 * open_k
    gl = (14 * open_k, 6 * open_k)
    c.save(); c.translate(x, y); c.scale(s, s)
    # neck + shirt
    nk = skia.Path(); nk.addRoundRect(skia.Rect.MakeLTRB(-110, 160, 40, 420), 40, 40); fill(c, nk, SKIN, stroke=6)
    if body:
        sh = skia.Path(); sh.addRoundRect(skia.Rect.MakeLTRB(-260, 330, 160, 640), 140, 140)
        fill(c, sh, lingrad((0, 330), (0, 640), '#9BD7FF', '#6FB8E8'))
    # lower face (moves with the jaw)
    def jaw_tf():
        c.translate(gl[0], gl[1]); c.translate(*PIVOT); c.rotate(ang); c.translate(-PIVOT[0], -PIVOT[1])
    c.save(); jaw_tf()
    lf = skia.Path(); lf.moveTo(-60, 120); lf.lineTo(236, 112); lf.cubicTo(252, 150, 246, 210, 214, 236)
    lf.cubicTo(170, 268, 60, 262, -20, 230); lf.cubicTo(-70, 200, -80, 150, -60, 120); lf.close()
    fill(c, lf, SKIN)
    c.restore()
    # mouth cavity (visible when open)
    if open_k > 0.03:
        mp = skia.Path(); mp.moveTo(150, 112)
        tx, ty = _rot(250 + gl[0], 116 + gl[1], ang, PIVOT[0] + gl[0], PIVOT[1] + gl[1])
        mp.lineTo(252, 112); mp.lineTo(tx, ty); mp.close()
        c.drawPath(mp, P('#7A2E3B')); c.drawPath(mp, P(INK, stroke=5))
    # upper head
    hd = skia.Path(); hd.addCircle(0, -70, 250)
    face_p = skia.Path(); face_p.moveTo(120, -150); face_p.cubicTo(230, -150, 262, -60, 262, -10)
    face_p.lineTo(292, 30); face_p.lineTo(262, 52); face_p.cubicTo(262, 80, 258, 104, 250, 116)
    face_p.lineTo(-40, 120); face_p.close()
    head = skia.Op(hd, face_p, skia.PathOp.kUnion_PathOp)
    fill(c, head, lingrad((0, -320), (0, 120), '#FFEADB', SKIN))
    # hair (back + top)
    hr = skia.Path(); hr.moveTo(-250, -60); hr.cubicTo(-270, -300, 40, -400, 190, -230)
    hr.cubicTo(230, -190, 240, -150, 230, -120); hr.cubicTo(150, -170, 60, -150, 20, -120)
    hr.cubicTo(-30, -80, -70, -40, -100, 10); hr.cubicTo(-150, 120, -230, 120, -250, -60); hr.close()
    fill(c, hr, HAIR)
    # eye, brow, blush
    if mood in ('pain', 'squeeze'):
        c.drawPath(_poly([(150, -78), (176, -64), (150, -50)], False), P(INK, stroke=7))
    elif mood == 'happy':
        p = skia.Path(); p.moveTo(146, -60); p.quadTo(162, -82, 178, -60); c.drawPath(p, P(INK, stroke=7))
    else:
        bl = blink_at(t, 3)
        c.drawOval(RR(165, -64, 26, 38 * max(0.12, bl)), P(INK))
        if bl > 0.4: c.drawCircle(170, -72, 6, P(WHITE))
    c.drawOval(RR(190, 0, 46, 22), P(PINK, 170))
    # ear
    ea = skia.Path(); ea.addOval(RR(-70, 0, 70, 100)); fill(c, ea, SKIN, stroke=6)
    c.drawArc(RR(-66, 0, 34, 56), -80, 200, False, P(SKIN_D, stroke=6))
    # closed-mouth line
    if open_k <= 0.03:
        c.drawLine(196, 114, 250, 114, P(INK, stroke=6))
    if lens:
        lc, lr = (70, 120), 175
        clip = skia.Path(); clip.addCircle(*lc, lr)
        c.drawCircle(lc[0] + 8, lc[1] + 10, lr, P(INK, 50))
        c.save(); c.clipPath(clip, doAntiAlias=True)
        c.drawCircle(*lc, lr, P('#EAF6FF'))
        for i in range(6): c.drawCircle(lc[0], lc[1], lr - 20 - i * 26, P('#D7EEFF', stroke=2))
        # skull base + maxilla with upper teeth
        sk = skia.Path(); sk.moveTo(-120, -60); sk.lineTo(240, -60); sk.lineTo(240, 96); sk.lineTo(64, 100)
        sk.cubicTo(40, 60, 46, 40, 40, 20)       # articular eminence
        sk.cubicTo(30, -6, -30, -6, -36, 20)     # glenoid fossa (socket)
        sk.lineTo(-120, 40); sk.close()
        fill(c, sk, lingrad((0, -60), (0, 100), BONE, BONED), stroke=6)
        for i in range(6):
            tx = 76 + i * 23
            tr = skia.Path(); tr.addRoundRect(skia.Rect.MakeLTRB(tx, 92, tx + 20, 118), 6, 6); fill(c, tr, WHITE, stroke=4)
        # mandible
        c.save(); jaw_tf()
        fill(c, MANDIBLE, lingrad((0, 30), (0, 230), BONE, BONED), stroke=6)
        for i in range(6):
            tx = 76 + i * 22
            tr = skia.Path(); tr.addRoundRect(skia.Rect.MakeLTRB(tx, 114, tx + 19, 138), 6, 6); fill(c, tr, WHITE, stroke=4)
        # condyle
        c.drawCircle(-10, 26, 26, P(BONE)); c.drawCircle(-10, 26, 26, P(INK, stroke=6))
        c.restore()
        # disc (pink) between condyle and fossa
        dxy = (gl[0] * 0.8, gl[1] * 0.5)
        c.drawOval(RR(-10 + dxy[0], 2 + dxy[1], 46, 14), P(DISC)); c.drawOval(RR(-10 + dxy[0], 2 + dxy[1], 46, 14), P(INK, stroke=4))
        if glow > 0 or pain > 0:
            g = max(glow, pain)
            col = TEAL if pain <= 0 else RED
            r = 46 + 10 * math.sin(t * 6)
            c.drawCircle(-10 + gl[0], 26 + gl[1], r, P(col, 70 * g)); c.drawCircle(-10 + gl[0], 26 + gl[1], r, P(col, 230 * g, stroke=6))
        c.restore()
        c.drawCircle(*lc, lr, P(INK, stroke=9)); c.drawCircle(*lc, lr - 8, P(WHITE, 160, stroke=4))
    c.restore()

def tmj_screen_point(x, y, s, open_k=0.0):
    return x + (-10 + 14 * open_k) * s, y + (26 + 6 * open_k) * s

# ---------------------------------------------------------------- joint close-up
def joint_zoom(c, cx, cy, s, open_k, t, disc_mode='normal', cmood='smile', dmood='smile', pain=0.0, jump=None):
    """skull with fossa + eminence on top, condyle (face) below, disc pillow (face) between.
    disc_mode 'normal' rides on the condyle; 'slipped' sits forward until the condyle jumps under it (jump=open_k at
    which it clicks)."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    # skull bone with socket and bump
    sk = skia.Path(); sk.moveTo(-560, -1000); sk.lineTo(560, -1000); sk.lineTo(560, -80)
    sk.cubicTo(440, -80, 330, -60, 270, -14)      # down to the eminence crest
    sk.cubicTo(220, 30, 150, 20, 120, -40)        # back slope of the eminence
    sk.cubicTo(80, -140, 50, -190, -10, -190)     # fossa roof (socket)
    sk.cubicTo(-100, -190, -150, -120, -190, -70)
    sk.lineTo(-560, -70); sk.close()
    fill(c, sk, lingrad((0, -420), (0, 40), BONE, BONED), stroke=8)
    rr = random.Random(9)
    c.save(); c.clipPath(sk, doAntiAlias=True)
    for i in range(40):
        c.drawOval(RR(rr.uniform(-540, 540), rr.uniform(-700, -90), rr.uniform(20, 46), rr.uniform(14, 30)), P(BONED, 140))
    c.restore()
    # condyle path: rest under the fossa -> forward under the eminence
    k = ease_io(clamp(open_k))
    ccx = lerp(-10, 200, k); ccy = lerp(-40, 150, k) - 40 * math.sin(math.pi * k) * 0.3
    rot = 26 * k
    # mandible neck
    c.save(); c.translate(ccx, ccy); c.rotate(rot)
    neck = skia.Path(); neck.moveTo(-80, 20); neck.cubicTo(-90, 200, -110, 380, -140, 700)
    neck.lineTo(100, 700); neck.cubicTo(80, 380, 80, 200, 80, 20); neck.close()
    fill(c, neck, lingrad((0, 0), (0, 700), BONE, BONED), stroke=8)
    head = skia.Path(); head.addOval(RR(0, 0, 240, 190)); fill(c, head, lingrad((0, -95), (0, 95), '#FFF6E6', BONE), stroke=8)
    c.drawOval(RR(-52, -50, 60, 26), P(WHITE, 170))
    face(c, 0, 6, cmood, blink_at(t, 2), 0, 0.95, eye_dx=32)
    c.restore()
    # disc
    if disc_mode == 'normal':
        dx, dy = ccx + 6, ccy - 112
        drot = rot * 0.4
    else:
        j = jump if jump is not None else 0.5
        if open_k < j:
            dx, dy, drot = 175, -66, 32
        else:
            kk = ease_out(seg(open_k, j, j + 0.12))
            dx, dy, drot = lerp(175, ccx + 6, kk), lerp(-66, ccy - 112, kk), lerp(32, rot * 0.4, kk)
    c.save(); c.translate(dx, dy); c.rotate(drot)
    dp = skia.Path(); dp.moveTo(-130, 6); dp.cubicTo(-130, -40, 130, -40, 130, 6); dp.cubicTo(130, 36, 70, 22, 0, 30)
    dp.cubicTo(-70, 22, -130, 36, -130, 6); dp.close()
    fill(c, dp, lingrad((0, -30), (0, 30), '#FFD3E0', DISC), stroke=7)
    face(c, 0, -4, dmood, blink_at(t, 6), 0, 0.5, eye_dx=24)
    c.restore()
    if pain > 0:
        c.drawCircle(ccx, ccy - 60, 170 + 14 * math.sin(t * 10), P(RED, 50 * pain))
        for i in range(3):
            a = -0.6 + i * 0.6
            x0, y0 = ccx + 230 + i * 10, ccy - 120 + i * 70
            z = _poly([(x0 - 12, y0 - 26), (x0 + 10, y0 - 6), (x0 - 6, y0 + 2), (x0 + 14, y0 + 26)], False)
            c.drawPath(z, P(RED, 255 * pain, stroke=8))
    c.restore()
    return (cx + ccx * s, cy + ccy * s)

# ---------------------------------------------------------------- chewing muscle
def muscle(c, x, y, s=1.0, tense=0.0, t=0.0, seed=0):
    sh = math.sin(t * 40) * 6 * tense
    c.save(); c.translate(x + sh, y); c.scale(s * (1 - 0.08 * tense), s * (1 + 0.1 * tense))
    p = skia.Path(); p.moveTo(-80, -150); p.cubicTo(-20, -175, 60, -170, 90, -140)
    p.cubicTo(120, -40, 110, 80, 80, 150); p.cubicTo(20, 175, -60, 170, -90, 140)
    p.cubicTo(-120, 40, -110, -60, -80, -150); p.close()
    col = MUSC if tense < 0.5 else '#FF7A8E'
    fill(c, p, lingrad((0, -170), (0, 170), '#FFC2CC', col))
    c.save(); c.clipPath(p, doAntiAlias=True)
    for i in range(-3, 4):
        c.drawLine(i * 30 - 20, -170, i * 30 + 20, 170, P(MUSC_D, 120, stroke=5))
    c.restore()
    if tense > 0.3:
        c.drawPath(p, P(RED, 120 * tense, stroke=14))
    face(c, 0, -10, 'squeeze' if tense > 0.5 else ('worry' if tense > 0.2 else 'happy'), blink_at(t, seed), 0, 0.9)
    c.restore()
    if tense > 0.5:
        sweat(c, x + 100 * s, y - 120 * s, 0.8 * s)

# ---------------------------------------------------------------- dentist (หมอนวรัตน์, cartoon)
def dentist(c, x, y, s=1.0, t=0.0, mood='smile', wave=0.0, point=0.0, open_k=0.0, face_img=None):
    yy = y + math.sin(t * 2.6) * 5
    c.save(); c.translate(x, yy); c.scale(s, s)
    # coat body
    body = skia.Path(); body.addRoundRect(skia.Rect.MakeLTRB(-190, 150, 190, 560), 130, 130)
    fill(c, body, lingrad((0, 150), (0, 560), WHITE, '#E8F3F7'))
    v = _poly([(-70, 168), (0, 260), (70, 168)]); fill(c, v, SCRUB, stroke=6)
    c.drawLine(0, 260, 0, 540, P('#C9DCE4', stroke=5))
    for sx in (-1, 1):
        lap = _poly([(sx * 70, 168), (sx * 20, 300), (sx * 110, 250)]); fill(c, lap, WHITE, stroke=6)
    # name badge
    c.drawRoundRect(RR(-100, 330, 86, 36), 8, 8, P(TEAL)); c.drawRoundRect(RR(-100, 330, 86, 36), 8, 8, P(INK, stroke=5))
    neck = skia.Path(); neck.addRoundRect(RR(0, 150, 86, 60), 30, 30); fill(c, neck, SKIN, stroke=6)
    if face_img is not None:
        _photo_head(c, face_img, t)
    else:
        _drawn_head(c, t, mood, open_k)
    _dentist_arms(c, t, wave, point)
    c.restore()

def _photo_head(c, img, t):
    R = 182
    c.drawCircle(10, 22, R + 20, P(INK, 70))
    c.drawCircle(0, 0, R + 18, P(WHITE)); c.drawCircle(0, 0, R + 18, P(INK, stroke=7))
    c.save(); clip = skia.Path(); clip.addCircle(0, 0, R); c.clipPath(clip, doAntiAlias=True)
    c.drawImageRect(img, skia.Rect.MakeLTRB(-R, -R, R, R), SAMP, skia.Paint(AntiAlias=True))
    c.restore()
    c.drawCircle(0, 0, R, P(TEAL, stroke=8))
    # little cheek sparkles so the photo still feels part of the cartoon
    sparkle(c, R + 10, -R + 30, 20 + 6 * math.sin(t * 5), YEL, 240)
    sparkle(c, -R - 6, -R + 70, 14 + 5 * math.sin(t * 4 + 1), PINK, 230)

def face_badge(c, img, x, y, r):
    c.drawCircle(x + 6, y + 10, r + 10, P(INK, 70))
    c.drawCircle(x, y, r + 10, P(WHITE)); c.drawCircle(x, y, r + 10, P(INK, stroke=6))
    c.save(); clip = skia.Path(); clip.addCircle(x, y, r); c.clipPath(clip, doAntiAlias=True)
    c.drawImageRect(img, skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), SAMP, skia.Paint(AntiAlias=True))
    c.restore(); c.drawCircle(x, y, r, P(TEAL, stroke=6))

def _drawn_head(c, t, mood, open_k):
    # hair (short bob)
    bh = skia.Path(); bh.addRoundRect(skia.Rect.MakeLTRB(-188, -170, 188, 100), 150, 150); fill(c, bh, HAIR)
    for sx in (-1, 1):
        e = skia.Path(); e.addOval(RR(sx * 170, 20, 50, 70)); fill(c, e, SKIN, stroke=6)
    hd = skia.Path(); hd.addOval(RR(0, 0, 330, 320)); fill(c, hd, lingrad((0, -160), (0, 160), '#FFEADB', SKIN))
    fr = skia.Path(); fr.moveTo(-168, 10); fr.cubicTo(-170, -140, -50, -185, 30, -168)
    fr.cubicTo(120, -160, 172, -100, 168, 0); fr.cubicTo(150, -60, 80, -110, 40, -80)
    fr.cubicTo(-10, -110, -110, -90, -168, 10); fr.close(); fill(c, fr, HAIR)
    pface(c, 0, 14, 0.95, mood, open_k, blink_at(t, 5))
    # round glasses
    for sx in (-1, 1):
        c.drawCircle(sx * 50, 18, 44, P(WHITE, 40)); c.drawCircle(sx * 50, 18, 44, P(INK, stroke=7))
    c.drawLine(-8, 14, 8, 14, P(INK, stroke=6))

def _dentist_arms(c, t, wave, point):
    if wave > 0:
        a = math.sin(t * 8) * 18 * wave
        c.save(); c.translate(170, 230); c.rotate(-130 + a)
        arm = skia.Path(); arm.addRoundRect(RR(0, 90, 60, 180), 30, 30); fill(c, arm, WHITE, stroke=6)
        hnd = skia.Path(); hnd.addCircle(0, 190, 36); fill(c, hnd, SKIN, stroke=6)
        c.restore()
    if point > 0:
        c.save(); c.translate(-170, 230); c.rotate(70 - 30 * point)
        arm = skia.Path(); arm.addRoundRect(RR(0, 90, 60, 180), 30, 30); fill(c, arm, WHITE, stroke=6)
        hnd = skia.Path(); hnd.addCircle(0, 190, 36); fill(c, hnd, SKIN, stroke=6)
        # dental mirror
        c.drawLine(0, 190, 0, 300, P(INK, stroke=12)); c.drawLine(0, 190, 0, 300, P('#C9D6E8', stroke=6))
        c.drawCircle(0, 318, 22, P('#CFF4FF')); c.drawCircle(0, 318, 22, P(INK, stroke=6))
        c.restore()

# ---------------------------------------------------------------- teeth row with the occlusal splint
def splint_on(c, cx, gy_top, k, t):
    """clear guard sliding down over an upper row of teeth (rows drawn by the scene); k 0..1"""
    if k <= 0: return
    y = gy_top - 240 * (1 - ease_out(k))
    p = skia.Path(); p.addRoundRect(skia.Rect.MakeLTRB(cx - 470, y + 40, cx + 470, y + 300), 70, 70)
    c.drawPath(p, P('#BFEFFF', 120 * k)); c.drawPath(p, P('#5CC3E8', 255 * k, stroke=8))
    c.drawLine(cx - 400, y + 80, cx - 200, y + 70, P(WHITE, 200 * k, stroke=10))
    for i in range(4):
        sparkle(c, cx - 380 + i * 250, y + 60 + (i % 2) * 180, 14 + 8 * math.sin(t * 5 + i), WHITE, 230 * k)

# ---------------------------------------------------------------- small props
def bed(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    fr = skia.Path(); fr.addRoundRect(skia.Rect.MakeLTRB(-300, -40, 300, 120), 30, 30); fill(c, fr, '#C9A0FF')
    c.drawRoundRect(skia.Rect.MakeLTRB(-320, -160, -270, 160), 20, 20, P('#B07A4F')); c.drawRoundRect(skia.Rect.MakeLTRB(-320, -160, -270, 160), 20, 20, P(INK, stroke=6))
    pil = skia.Path(); pil.addRoundRect(skia.Rect.MakeLTRB(-260, -110, -110, -30), 40, 40); fill(c, pil, WHITE)
    c.restore()

def blanket(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.moveTo(-130, -70); b.cubicTo(0, -110, 200, -90, 290, -60); b.lineTo(290, 60); b.lineTo(-130, 60); b.close()
    fill(c, b, lingrad((0, -100), (0, 60), '#FFD6E0', '#FF9EBB'))
    for i in range(5): c.drawCircle(-60 + i * 80, 0, 12, P(WHITE, 200))
    c.restore()

def zzz(c, x, y, t):
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1
        draw_img(c, text_img('z', 38 + 14 * k, LAV, 5, INK), x + ph * 40 + k * 18, y - ph * 90 - k * 10, 1, 1 - ph)

def storm(c, x, y, t, s=1.0):
    c.save(); c.translate(x, y + math.sin(t * 3) * 6); c.scale(s, s)
    p = skia.Path()
    for cx_, cy_, r in ((-50, 0, 46), (0, -24, 56), (55, 0, 44), (0, 18, 50)): p.addCircle(cx_, cy_, r)
    c.drawPath(p, P('#9AA9C2')); c.drawPath(p, P(INK, stroke=6))
    z = _poly([(0, 40), (-18, 80), (4, 80), (-14, 120)], False); c.drawPath(z, P(YEL, stroke=10)); c.drawPath(z, P(INK, stroke=3))
    c.restore()

def gum_bubble(c, x, y, r, t):
    c.drawCircle(x, y, r, P('#FFB3D1', 220)); c.drawCircle(x, y, r, P(INK, stroke=6))
    c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.18, P(WHITE, 200))

def ice_cube(c, x, y, s, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.addRoundRect(RR(0, 0, 90, 90), 18, 18); fill(c, p, '#DDF6FF', stroke=6)
    c.drawLine(-24, -20, 10, -28, P(WHITE, stroke=8))
    c.restore()

def soup(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.moveTo(-90, -10); b.lineTo(90, -10); b.cubicTo(86, 60, 40, 80, 0, 80); b.cubicTo(-40, 80, -86, 60, -90, -10); b.close()
    fill(c, b, lingrad((0, -10), (0, 80), WHITE, SHADE))
    c.drawOval(RR(0, -10, 180, 30), P('#FFE7A8')); c.drawOval(RR(0, -10, 180, 30), P(INK, stroke=6))
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        sp = skia.Path(); sx_ = -40 + i * 40; sp.moveTo(sx_, -30 - ph * 60)
        sp.cubicTo(sx_ - 14, -50 - ph * 60, sx_ + 14, -70 - ph * 60, sx_, -90 - ph * 60)
        c.drawPath(sp, P('#C9D6E8', 255 * (1 - ph), stroke=6))
    c.restore()

def towel(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-8)
    p = skia.Path(); p.addRoundRect(RR(0, 0, 200, 110), 30, 30); fill(c, p, '#FFD39B')
    for i in range(3): c.drawLine(-80 + i * 80, -40, -80 + i * 80, 40, P('#F2B568', stroke=6))
    for i in range(3):
        ph = (t * 0.9 + i / 3) % 1
        sp = skia.Path(); sx_ = -50 + i * 50; sp.moveTo(sx_, -70 - ph * 50)
        sp.cubicTo(sx_ - 14, -90 - ph * 50, sx_ + 14, -110 - ph * 50, sx_, -130 - ph * 50)
        c.drawPath(sp, P(CORAL, 200 * (1 - ph), stroke=6))
    c.restore()

def check(c, x, y, s=1.0, col=TEAL):
    c.drawCircle(x, y, 26 * s, P(col)); c.drawCircle(x, y, 26 * s, P(INK, stroke=5 * s))
    c.drawPath(_poly([(x - 12 * s, y), (x - 3 * s, y + 10 * s), (x + 13 * s, y - 10 * s)], False), P(WHITE, stroke=7 * s))

def polaroid(c, img, x, y, w, rot, k, caption=None, tape=YEL):
    if k <= 0: return
    h = w * img.height() / img.width()
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    c.drawRoundRect(RR(10, 16, w + 40, h + 120), 14, 14, P(INK, 70))
    c.drawRoundRect(RR(0, 0, w + 40, h + 120), 14, 14, P(WHITE))
    c.drawRoundRect(RR(0, 0, w + 40, h + 120), 14, 14, P(INK, stroke=6))
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2 - 40, w, h), SAMP, skia.Paint(AntiAlias=True))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 - 40, w, h), P(INK, stroke=4))
    tp = skia.Path(); tp.addRect(skia.Rect.MakeXYWH(-60, -h / 2 - 100, 120, 44)); c.save(); c.rotate(-6); c.drawPath(tp, P(tape, 200)); c.restore()
    c.restore()
    if caption:
        draw_img(c, text_img(caption, 34, INK, 0), x + math.sin(math.radians(rot)) * -(h / 2 + 20) * k,
                 y + math.cos(math.radians(rot)) * (h / 2 + 22) * k, k, 1, rot)

def load_photo(path):
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert('RGBA')
    return skia.Image.fromarray(np.ascontiguousarray(np.array(im)), colorType=skia.ColorType.kRGBA_8888_ColorType,
                                alphaType=skia.AlphaType.kUnpremul_AlphaType)

def clinic_banner(c):
    """the fixed top strip: คลินิกทันตกรรมบางปะอิน"""
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 26, W - 120, 104), 39, 39, P(INK, 70))
    c.drawRoundRect(skia.Rect.MakeLTRB(110, 18, W - 110, 96), 39, 39, lingrad((110, 0), (W - 110, 0), TEAL, '#1B998B'))
    c.drawRoundRect(skia.Rect.MakeLTRB(110, 18, W - 110, 96), 39, 39, P(INK, stroke=5))
    c.save(); c.translate(190, 57); c.scale(0.22, 0.22)
    c.drawPath(TOOTH, P(WHITE)); c.drawPath(TOOTH, P(INK, stroke=16)); c.restore()
    draw_img(c, text_img('คลินิกทันตกรรมบางปะอิน', 44, WHITE, 0), W / 2 + 30, 58)

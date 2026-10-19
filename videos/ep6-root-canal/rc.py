"""ep6 (root canal) drawings: the scrub-wearing photo-head dentist, a detailed dental operatory, the reclined patient,
the open-mouth close-up, the x-ray monitor, the cross-section molar with every treatment state, and small props.
Same ink/pastel style as tools/kawaii.py (thick #23395B outline, flat pastel fills, soft gradients, faces)."""
import math, random
import skia
from tools.kawaii import *  # noqa: F401,F403
from chars import *  # noqa: F401,F403
from chars import _poly, _photo_head

SCRUB_A = '#3FD8CF'; SCRUB_B = '#1FB5B0'; SCRUB_D = '#139790'   # bright sea-green-blue scrubs
GLOVE = '#BFE3FF'; STEEL = '#DCE6F0'; STEEL_D = '#8FA3BC'
DENTIN = ('#FFF6E6', '#FBE2BE'); ENAMEL = ('#FFFFFF', '#E9F6FB')
PULP = '#FFA3BA'; PULP_HOT = '#FF4F6D'; PULP_DEAD = '#B7AAB4'
GP = '#FF9A62'; GP_D = '#E86F3A'; EMPTY = '#FFF9F2'; CLEAN = '#DDFBFF'; MED = '#EDE4FF'
DECAY = '#6E4A2C'; DECAY_L = '#9A6B42'; DAM = '#7ED6A0'; DAM_D = '#4FB97C'
CHAIR = '#B8B8FF'; CHAIR_D = '#8F8FE8'


def mix(a, b, k):
    a, b = a.lstrip('#'), b.lstrip('#'); k = clamp(k)
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]; cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(int(round(x + (y - x) * k)) for x, y in zip(ca, cb))

def grad_paint(p0, p1, c0, c1, a=255):
    g = lingrad(p0, p1, c0, c1); g.setAlphaf(a / 255.0); return g

# ================================================================ the dentist in scrubs (photo head)
def _glove_hand(c, x, y, r=34):
    c.drawCircle(x, y, r, P(GLOVE)); c.drawCircle(x, y, r, P(INK, stroke=6))
    c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.25, P(WHITE, 170))

def _item(c, item, t):
    """drawn in arm-local coords, hand at (0, 225), pointing down the arm"""
    if item == 'mirror':
        c.drawLine(0, 240, 0, 360, P(INK, stroke=14)); c.drawLine(0, 240, 0, 360, P(STEEL, stroke=8))
        c.drawCircle(0, 384, 30, P('#CFF4FF')); c.drawCircle(0, 384, 30, P(INK, stroke=6))
        c.drawCircle(-9, 375, 8, P(WHITE, 220))
    elif item == 'probe':
        c.drawLine(0, 240, 0, 350, P(INK, stroke=14)); c.drawLine(0, 240, 0, 350, P(STEEL, stroke=8))
        p = skia.Path(); p.moveTo(0, 350); p.quadTo(4, 392, 26, 396); p.quadTo(40, 398, 40, 384)
        c.drawPath(p, P(INK, stroke=8)); c.drawPath(p, P(STEEL_D, stroke=3))
    elif item == 'pointer':
        c.drawLine(0, 240, 0, 430, P(INK, stroke=14)); c.drawLine(0, 240, 0, 430, P(YEL, stroke=8))
        sparkle(c, 0, 450, 26 + 4 * math.sin(t * 6), YEL)
    if item:
        _glove_hand(c, 0, 225)

def _sarm(c, side, ang, item, t):
    c.save(); c.translate(side * 158, 215); c.rotate(ang)
    fa = skia.Path(); fa.addRoundRect(RR(0, 150, 56, 150), 28, 28); fill(c, fa, SKIN, stroke=6)
    _item(c, item, t)
    if not item: _glove_hand(c, 0, 225)
    sl = skia.Path(); sl.addRoundRect(RR(0, 52, 92, 118), 40, 40)
    fill(c, sl, grad_paint((0, 0), (0, 110), SCRUB_A, SCRUB_B), stroke=6)
    c.drawLine(-38, 100, 38, 100, P(SCRUB_D, stroke=5))
    c.restore()

def doc(c, x, y, s, t, face_img, left=('down', None), right=('down', None), bob=True, legs=True):
    """dentist in bright aqua scrubs; head centre at (x, y). left/right = (pose|angle, item).
    poses: 'down', 'wave', 'reach' (forward/down), 'up' (raised high), or a number (degrees)"""
    yy = y + (math.sin(t * 2.6) * 5 if bob else 0)
    c.save(); c.translate(x, yy); c.scale(s, s)
    poses = {'down': 14, 'reach': 62, 'up': 150, 'wave': 128}
    la = left[0] if isinstance(left[0], (int, float)) else poses[left[0]]
    ra = right[0] if isinstance(right[0], (int, float)) else poses[right[0]]
    if right[0] == 'wave': ra += math.sin(t * 8) * 14
    if left[0] == 'wave': la += math.sin(t * 8) * 14
    # arms behind body when hanging down
    if la < 40: _sarm(c, -1, la, left[1], t)
    if ra < 40: _sarm(c, 1, -ra, right[1], t)
    if legs:
        for sx in (-1, 1):
            lg = skia.Path(); lg.addRoundRect(skia.Rect.MakeLTRB(sx * 92 - 58, 500, sx * 92 + 58, 830), 40, 40)
            fill(c, lg, grad_paint((0, 500), (0, 830), SCRUB_B, SCRUB_D), stroke=6)
            sh = skia.Path(); sh.addRoundRect(skia.Rect.MakeLTRB(sx * 100 - 74, 800, sx * 100 + 74, 870), 34, 34)
            fill(c, sh, WHITE, stroke=6); c.drawLine(sx * 100 - 50, 846, sx * 100 + 50, 846, P(SKY, stroke=6))
    body = skia.Path(); body.addRoundRect(skia.Rect.MakeLTRB(-182, 150, 182, 580), 128, 128)
    fill(c, body, grad_paint((0, 150), (0, 580), SCRUB_A, SCRUB_B))
    # v-neck and trim
    c.drawPath(_poly([(-66, 160), (0, 262), (66, 160)]), P(SKIN)); c.drawPath(_poly([(-66, 160), (0, 262), (66, 160)], False), P(SCRUB_D, stroke=12))
    c.drawPath(_poly([(-66, 160), (0, 262), (66, 160)], False), P(INK, stroke=5))
    # chest pocket with pens + badge
    pk = skia.Path(); pk.addRoundRect(skia.Rect.MakeLTRB(-150, 320, -64, 410), 14, 14); fill(c, pk, SCRUB_B, stroke=5)
    for i, col in enumerate((CORAL, YEL)):
        c.drawRoundRect(skia.Rect.MakeLTRB(-136 + i * 26, 290, -122 + i * 26, 338), 6, 6, P(col)); c.drawRoundRect(skia.Rect.MakeLTRB(-136 + i * 26, 290, -122 + i * 26, 338), 6, 6, P(INK, stroke=4))
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 320, 150, 360), 10, 10, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(60, 320, 150, 360), 10, 10, P(INK, stroke=5))
    c.drawLine(74, 340, 136, 340, P(TEAL, stroke=8))
    c.drawLine(0, 300, 0, 560, P(SCRUB_D, 160, stroke=5))
    if la >= 40: _sarm(c, -1, la, left[1], t)
    if ra >= 40: _sarm(c, 1, -ra, right[1], t)
    _photo_head(c, face_img, t)
    c.restore()

def speech(c, txt, x, y, t, t0, size=46, tail='left', bg=WHITE, fg=INK):
    """comic speech bubble that pops in; (x, y) = bubble centre"""
    s = pop(t, t0, 0.45)
    if s <= 0: return
    cue(t, t0, 'pop')
    img = text_img(txt, size, fg, 0, INK, FONT_M, spacing=8)
    w, h = img.width() + 80, img.height() + 56
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.addRoundRect(RR(0, 0, w, h), 46, 46)
    tx = -w * 0.28 if tail == 'left' else w * 0.28
    tl = _poly([(tx - 26, h / 2 - 6), (tx - 60 if tail == 'left' else tx + 60, h / 2 + 64), (tx + 30, h / 2 - 6)])
    p = skia.Op(p, tl, skia.PathOp.kUnion_PathOp)
    c.save(); c.translate(8, 12); c.drawPath(p, P(INK, 70)); c.restore()
    c.drawPath(p, P(bg)); c.drawPath(p, P(INK, stroke=7))
    c.restore()
    draw_img(c, img, x, y + 2, s)

# ================================================================ the operatory (room) — back layer
def _cloud(c, x, y, s, a=255):
    p = skia.Path()
    for dx, dy, r in ((-40, 6, 30), (0, -12, 40), (42, 6, 30), (0, 14, 32)): p.addCircle(x + dx * s, y + dy * s, r * s)
    c.drawPath(p, P(WHITE, a))

def room_back(c, t, light=1.0):
    # wall + wainscot + floor
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1400), lingrad((0, 0), (0, 1400), '#F1FCFA', '#D9F4EF'))
    c.drawRect(skia.Rect.MakeLTRB(0, 1110, W, 1400), P('#C6ECE6'))
    c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, 1122), P(TEAL)); c.drawLine(0, 1122, W, 1122, P(INK, 90, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(0, 1400, W, H), lingrad((0, 1400), (0, H), '#CFE6F2', '#A9CCE0'))
    for i in range(-6, 15):
        x0 = 540 + i * 140
        c.drawLine(540 + (x0 - 540) * 0.35, 1400, x0 + (x0 - 540) * 0.9, H, P(WHITE, 90, stroke=3))
    for k, yy in enumerate((1460, 1550, 1670, 1820)): c.drawLine(0, yy, W, yy, P(WHITE, 90, stroke=3))
    c.drawLine(0, 1400, W, 1400, P(INK, 120, stroke=5))
    # window with a sunny view
    wr = skia.Rect.MakeLTRB(66, 330, 440, 690)
    c.drawRoundRect(skia.Rect.MakeLTRB(52, 316, 454, 704), 26, 26, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(52, 316, 454, 704), 26, 26, P(INK, stroke=7))
    c.save(); c.clipRect(wr)
    c.drawRect(wr, lingrad((0, 330), (0, 690), '#8EDBFF', '#E6F8FF'))
    c.drawCircle(370, 400, 44, P('#FFE58A')); c.drawCircle(370, 400, 60, P('#FFE58A', 70))
    _cloud(c, 160 + (t * 14) % 360, 410, 1.0, 230); _cloud(c, 300 + (t * 9) % 300 - 150, 470, 0.7, 210)
    hill = skia.Path(); hill.moveTo(66, 640); hill.cubicTo(160, 560, 300, 580, 440, 620); hill.lineTo(440, 690); hill.lineTo(66, 690); hill.close()
    c.drawPath(hill, P('#9EE6A8')); c.drawPath(hill, P(INK, 120, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(150, 560, 166, 620), P('#B07A4F'))
    c.drawCircle(158, 548, 40, P('#6FD08C')); c.drawCircle(158, 548, 40, P(INK, 120, stroke=4))
    c.restore()
    c.drawLine(253, 330, 253, 690, P(WHITE, stroke=12)); c.drawLine(66, 510, 440, 510, P(WHITE, stroke=12))
    c.drawRoundRect(wr, 6, 6, P(INK, stroke=5))
    for sx, x0 in ((1, 30), (-1, 476)):   # curtains
        cu = skia.Path(); cu.moveTo(x0, 300); cu.lineTo(x0 + sx * 70, 300)
        cu.cubicTo(x0 + sx * 40, 450, x0 + sx * 90, 600, x0 + sx * 50, 730); cu.lineTo(x0, 730); cu.close()
        fill(c, cu, grad_paint((x0, 300), (x0, 730), '#FFD0DC', '#FFB0C4'), stroke=6)
    c.drawRoundRect(skia.Rect.MakeLTRB(16, 286, 490, 304), 9, 9, P('#C8A27A')); c.drawRoundRect(skia.Rect.MakeLTRB(16, 286, 490, 304), 9, 9, P(INK, stroke=5))
    # wall clock
    c.drawCircle(612, 420, 62, P(WHITE)); c.drawCircle(612, 420, 62, P(INK, stroke=7)); c.drawCircle(612, 420, 50, P(MINT, 120))
    for i in range(12):
        a = i * math.pi / 6; c.drawLine(612 + math.cos(a) * 42, 420 + math.sin(a) * 42, 612 + math.cos(a) * 50, 420 + math.sin(a) * 50, P(INK, stroke=4))
    c.drawLine(612, 420, 612 + 26 * math.cos(-1.2), 420 + 26 * math.sin(-1.2), P(INK, stroke=6))
    a2 = t * 1.5 - 1.57; c.drawLine(612, 420, 612 + 40 * math.cos(a2), 420 + 40 * math.sin(a2), P(CORAL, stroke=4))
    # poster with a happy tooth
    c.save(); c.translate(870, 470); c.rotate(3)
    c.drawRoundRect(RR(8, 10, 240, 290), 18, 18, P(INK, 60)); c.drawRoundRect(RR(0, 0, 240, 290), 18, 18, P('#FFF4D6'))
    c.drawRoundRect(RR(0, 0, 240, 290), 18, 18, P(INK, stroke=6))
    c.restore()
    tooth(c, 870, 430, 0.62, 'happy', 3, t=t, seed=4, shadow=False)
    sparkle(c, 790, 380, 14 + 4 * math.sin(t * 4), YEL); sparkle(c, 950, 470, 12, PINK)
    draw_img(c, text_img('ยิ้มสวย', 38, INK, 0), 872, 560, 1, 1, 3)
    # shelf with jars on the right wall
    c.drawRoundRect(skia.Rect.MakeLTRB(700, 760, 1060, 784), 8, 8, P('#C8A27A')); c.drawRoundRect(skia.Rect.MakeLTRB(700, 760, 1060, 784), 8, 8, P(INK, stroke=5))
    for i, (col, h) in enumerate(((SKY, 90), (PINK, 70), (YEL, 100), (MINT, 80))):
        x0 = 730 + i * 82
        c.drawRoundRect(skia.Rect.MakeLTRB(x0, 760 - h, x0 + 58, 760), 14, 14, P(col)); c.drawRoundRect(skia.Rect.MakeLTRB(x0, 760 - h, x0 + 58, 760), 14, 14, P(INK, stroke=5))
        c.drawRoundRect(skia.Rect.MakeLTRB(x0 - 4, 760 - h - 14, x0 + 62, 760 - h + 4), 6, 6, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(x0 - 4, 760 - h - 14, x0 + 62, 760 - h + 4), 6, 6, P(INK, stroke=4))
    # counter cabinet with sink
    c.drawRoundRect(skia.Rect.MakeLTRB(760, 1150, 1100, 1420), 16, 16, P('#FFFFFF')); c.drawRoundRect(skia.Rect.MakeLTRB(760, 1150, 1100, 1420), 16, 16, P(INK, stroke=7))
    for yy in (1220, 1300): c.drawLine(760, yy, 1100, yy, P(INK, 140, stroke=4))
    for yy in (1186, 1260, 1360): c.drawRoundRect(skia.Rect.MakeLTRB(890, yy - 6, 970, yy + 6), 6, 6, P(TEAL))
    c.drawRoundRect(skia.Rect.MakeLTRB(740, 1124, 1100, 1156), 10, 10, P('#9FE3DC')); c.drawRoundRect(skia.Rect.MakeLTRB(740, 1124, 1100, 1156), 10, 10, P(INK, stroke=6))
    fau = skia.Path(); fau.moveTo(1010, 1124); fau.lineTo(1010, 1060); fau.quadTo(1010, 1040, 990, 1040); fau.lineTo(960, 1040)
    c.drawPath(fau, P(INK, stroke=16)); c.drawPath(fau, P(STEEL, stroke=8))
    c.drawRoundRect(skia.Rect.MakeLTRB(790, 1062, 880, 1124), 12, 12, P(GLOVE)); c.drawRoundRect(skia.Rect.MakeLTRB(790, 1062, 880, 1124), 12, 12, P(INK, stroke=5))
    c.drawOval(RR(835, 1064, 40, 12), P(WHITE))
    # plant
    pot = _poly([(36, 1300), (150, 1300), (136, 1420), (50, 1420)]); fill(c, pot, '#FF9F7A', stroke=6)
    for i, a in enumerate((-60, -30, 0, 30, 60)):
        c.save(); c.translate(93, 1300); c.rotate(a + math.sin(t * 1.5 + i) * 3)
        lf = skia.Path(); lf.addOval(RR(0, -90, 46, 150)); fill(c, lf, '#6FD08C' if i % 2 else '#4FBF77', stroke=5)
        c.restore()

def xray_monitor_small(c, x, y, t, on=1.0):
    """little wall-arm monitor showing a tooth (room decor)"""
    c.drawLine(x + 120, y + 70, x + 190, y + 140, P(INK, stroke=14)); c.drawLine(x + 120, y + 70, x + 190, y + 140, P(STEEL, stroke=8))
    r = RR(x, y, 250, 170)
    c.drawRoundRect(r, 20, 20, P('#2B3A55')); c.drawRoundRect(r, 20, 20, P(INK, stroke=7))
    c.drawRoundRect(RR(x, y, 222, 142), 10, 10, P('#0F1B33'))
    if on > 0:
        c.save(); c.translate(x, y + 6); c.scale(0.22, 0.22)
        c.drawPath(TOOTH, P('#DDE6F2', 230 * on)); c.drawPath(TOOTH, P(WHITE, 150 * on, stroke=6))
        c.restore()

def dental_chair(c, t):
    # base + column
    c.drawOval(RR(600, 1420, 420, 60), P(INK, 50))
    c.drawRoundRect(skia.Rect.MakeLTRB(430, 1380, 770, 1424), 20, 20, P(STEEL)); c.drawRoundRect(skia.Rect.MakeLTRB(430, 1380, 770, 1424), 20, 20, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(560, 1210, 640, 1390), 14, 14, P(STEEL)); c.drawRoundRect(skia.Rect.MakeLTRB(560, 1210, 640, 1390), 14, 14, P(INK, stroke=7))
    # foot pedal
    c.drawRoundRect(skia.Rect.MakeLTRB(800, 1440, 880, 1470), 10, 10, P(STEEL_D)); c.drawRoundRect(skia.Rect.MakeLTRB(800, 1440, 880, 1470), 10, 10, P(INK, stroke=5))
    # cushion (reclined): back, seat, leg rest as one thick rounded stroke
    pts = [(300, 1080), (560, 1185), (800, 1192), (975, 1290)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    c.drawPath(p, P(INK, stroke=124)); c.drawPath(p, P(CHAIR, stroke=110))
    hl = skia.Path(); hl.moveTo(330, 1066); hl.lineTo(550, 1156); c.drawPath(hl, P(WHITE, 110, stroke=14))
    c.drawPath(p, P(CHAIR_D, 140, stroke=8))   # seam
    # headrest
    c.save(); c.translate(236, 1040); c.rotate(22)
    hr = skia.Path(); hr.addRoundRect(RR(0, 0, 150, 92), 44, 44); fill(c, hr, CHAIR, stroke=7)
    c.restore()
    # armrest
    c.drawRoundRect(skia.Rect.MakeLTRB(600, 1130, 780, 1160), 15, 15, P(CHAIR_D)); c.drawRoundRect(skia.Rect.MakeLTRB(600, 1130, 780, 1160), 15, 15, P(INK, stroke=6))

def spittoon(c, x, y):
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 14, y, x + 14, y + 260), 10, 10, P(STEEL)); c.drawRoundRect(skia.Rect.MakeLTRB(x - 14, y, x + 14, y + 260), 10, 10, P(INK, stroke=5))
    b = skia.Path(); b.moveTo(x - 70, y); b.quadTo(x, y + 80, x + 70, y); b.close(); fill(c, b, WHITE, stroke=6)
    c.drawOval(RR(x, y, 140, 30), P('#C9F1FF')); c.drawOval(RR(x, y, 140, 30), P(INK, stroke=6))
    cup = _poly([(x + 60, y - 50), (x + 100, y - 50), (x + 94, y), (x + 66, y)]); fill(c, cup, PINK, stroke=5)

def tray(c, x, y, t):
    """instrument tray on a swing arm; (x, y) = tray centre"""
    c.drawLine(x + 60, y + 20, x + 140, y + 420, P(INK, stroke=16)); c.drawLine(x + 60, y + 20, x + 140, y + 420, P(STEEL, stroke=9))
    c.drawRoundRect(RR(x, y + 8, 290, 34), 12, 12, P(INK, 60))
    c.drawRoundRect(RR(x, y, 290, 34), 12, 12, P('#F4F8FF')); c.drawRoundRect(RR(x, y, 290, 34), 12, 12, P(INK, stroke=6))
    # instruments lying on the tray
    for i, kind in enumerate(('mirror', 'probe', 'tweez')):
        x0 = x - 110 + i * 60
        c.drawLine(x0, y - 10, x0 + 70, y - 34, P(INK, stroke=11)); c.drawLine(x0, y - 10, x0 + 70, y - 34, P(STEEL, stroke=5))
        if kind == 'mirror': c.drawCircle(x0 + 80, y - 38, 13, P('#CFF4FF')); c.drawCircle(x0 + 80, y - 38, 13, P(INK, stroke=4))
    for i in range(3):   # cotton rolls
        c.drawRoundRect(RR(x + 80 + i * 22, y - 30, 18, 40), 8, 8, P(WHITE)); c.drawRoundRect(RR(x + 80 + i * 22, y - 30, 18, 40), 8, 8, P(INK, stroke=4))

def lamp(c, t, on=1.0, target=(350, 990), head=(470, 790)):
    hx, hy = head
    arm = skia.Path(); arm.moveTo(700, 240); arm.lineTo(700, 330); arm.lineTo(hx + 90, hy - 150); arm.lineTo(hx + 20, hy - 20)
    c.drawPath(arm, P(INK, stroke=22)); c.drawPath(arm, P(STEEL, stroke=12))
    for jx, jy in ((700, 330), (hx + 90, hy - 150)):
        c.drawCircle(jx, jy, 16, P(STEEL_D)); c.drawCircle(jx, jy, 16, P(INK, stroke=5))
    if on > 0:
        ang = math.atan2(target[1] - hy, target[0] - hx); nx, ny = -math.sin(ang), math.cos(ang)
        cone = skia.Path(); cone.moveTo(hx + nx * 60, hy + ny * 60); cone.lineTo(target[0] + nx * 150, target[1] + ny * 150)
        cone.lineTo(target[0] - nx * 150, target[1] - ny * 150); cone.lineTo(hx - nx * 60, hy - ny * 60); cone.close()
        c.drawPath(cone, P('#FFF3A8', 90 * on * (0.85 + 0.15 * math.sin(t * 5))))
        c.drawCircle(target[0], target[1], 120, P('#FFF7C2', 70 * on, blur=30))
    c.save(); c.translate(hx, hy); c.rotate(math.degrees(math.atan2(target[1] - hy, target[0] - hx)) - 90)
    lh = skia.Path(); lh.addRoundRect(RR(0, 0, 200, 90), 40, 40); fill(c, lh, WHITE, stroke=7)
    c.drawRoundRect(RR(0, 30, 150, 26), 12, 12, P('#FFE36E' if on > 0.5 else '#E3E8EF')); c.drawRoundRect(RR(0, 30, 150, 26), 12, 12, P(INK, stroke=5))
    c.restore()

# ================================================================ reclined patient in the chair
def lying_patient(c, x, y, s, t, mood='worry', open_k=0.0, shirt='#FF9EBB', pants='#7BA7E0'):
    """head (profile, face up) at (x, y); body follows the chair toward the lower right"""
    # legs along the seat and leg rest
    lg = skia.Path(); lg.moveTo(x + 330, y + 140); lg.lineTo(x + 560, y + 150); lg.lineTo(x + 720, y + 240)
    c.drawPath(lg, P(INK, stroke=96)); c.drawPath(lg, P(pants, stroke=82))
    c.drawOval(RR(x + 752, y + 236, 70, 92), P(WHITE)); c.drawOval(RR(x + 752, y + 236, 70, 92), P(INK, stroke=6))
    # torso
    tr = skia.Path(); tr.moveTo(x + 70, y + 30); tr.lineTo(x + 330, y + 135)
    c.drawPath(tr, P(INK, stroke=164)); c.drawPath(tr, P(shirt, stroke=150))
    # bib (dental napkin)
    bib = skia.Path(); bib.addRoundRect(RR(0, 0, 150, 110), 18, 18)
    c.save(); c.translate(x + 150, y + 30); c.rotate(-68); c.drawPath(bib, P('#BFF0FF')); c.drawPath(bib, P(INK, stroke=5)); c.restore()
    # arm resting on the belly
    ar = skia.Path(); ar.moveTo(x + 190, y + 60); ar.quadTo(x + 260, y + 150, x + 360, y + 110)
    c.drawPath(ar, P(INK, stroke=50)); c.drawPath(ar, P(shirt, stroke=38))
    c.drawCircle(x + 372, y + 104, 26, P(SKIN)); c.drawCircle(x + 372, y + 104, 26, P(INK, stroke=5))
    c.save(); c.translate(x, y); c.rotate(-70)
    side_head(c, 0, 0, s, open_k, t, mood, lens=False, body=False)
    c.restore()

# ================================================================ open-mouth close-up (dentist's view)
def _molar_top(c, x, y, w, h, cav=0.0, shade=WHITE):
    r = RR(x, y, w, h)
    c.drawRoundRect(r, w * 0.32, h * 0.32, lingrad((0, y - h / 2), (0, y + h / 2), shade, '#E2F1F7')); c.drawRoundRect(r, w * 0.32, h * 0.32, P(INK, stroke=6))
    c.drawLine(x - w * 0.22, y, x + w * 0.22, y, P('#C7DCE6', stroke=4)); c.drawLine(x, y - h * 0.22, x, y + h * 0.22, P('#C7DCE6', stroke=4))
    if cav > 0:
        p = skia.Path(); p.addOval(RR(x - w * 0.08, y + h * 0.02, w * 0.5 * cav, h * 0.44 * cav))
        c.drawPath(p, P(DECAY)); c.drawPath(p, P(INK, stroke=4))
        c.drawOval(RR(x - w * 0.12, y - h * 0.02, w * 0.18 * cav, h * 0.12 * cav), P(DECAY_L))

def mouth_close(c, cx, cy, t, cavity=1.0, ring=0.0):
    """big open mouth seen from the front-above; the decayed molar sits at lower right. returns its centre."""
    # face skin + cheeks
    c.drawOval(RR(cx, cy, 1040, 940), lingrad((0, cy - 470), (0, cy + 470), '#FFE8D8', SKIN)); c.drawOval(RR(cx, cy, 1040, 940), P(INK, stroke=8))
    for sx in (-1, 1): c.drawOval(RR(cx + sx * 410, cy - 140, 110, 60), P(PINK, 150))
    # lips + mouth cavity
    c.drawOval(RR(cx, cy + 40, 820, 640), P('#FF7F96')); c.drawOval(RR(cx, cy + 40, 820, 640), P(INK, stroke=8))
    c.drawOval(RR(cx, cy + 40, 720, 540), P('#6E2638'))
    c.drawOval(RR(cx, cy + 210, 420, 210), P('#FF8FA3')); c.drawOval(RR(cx, cy + 210, 420, 210), P(INK, 160, stroke=5))
    c.drawLine(cx, cy + 150, cx, cy + 250, P('#E06A85', stroke=5))
    # upper arch (front teeth) and lower arch (molars seen from above)
    up = [(-250, -150, 70, 70), (-180, -190, 74, 82), (-100, -214, 72, 96), (-34, -222, 64, 104),
          (34, -222, 64, 104), (100, -214, 72, 96), (180, -190, 74, 82), (250, -150, 70, 70)]
    for dx, dy, w, h in up:
        r = RR(cx + dx, cy + dy, w, h); c.drawRoundRect(r, 22, 22, P(WHITE)); c.drawRoundRect(r, 22, 22, P(INK, stroke=6))
    lo = [(-262, 210, 96, 86), (-190, 250, 92, 80), (-112, 278, 70, 64), (-40, 290, 58, 58),
          (40, 290, 58, 58), (112, 278, 70, 64), (190, 250, 92, 80), (262, 210, 96, 86)]
    cav_xy = None
    for i, (dx, dy, w, h) in enumerate(lo):
        if i in (0, 1, 6, 7):
            _molar_top(c, cx + dx, cy + dy, w, h, cavity if i == 6 else 0.0)
            if i == 6: cav_xy = (cx + dx, cy + dy)
        else:
            r = RR(cx + dx, cy + dy, w, h); c.drawRoundRect(r, 20, 20, P(WHITE)); c.drawRoundRect(r, 20, 20, P(INK, stroke=6))
    if ring > 0 and cav_xy:
        c.drawCircle(cav_xy[0], cav_xy[1], 70 + 8 * math.sin(t * 8), P(CORAL, 255 * ring, stroke=9))
    return cav_xy

def big_mirror(c, x, y, rot, k=1.0):
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawRoundRect(RR(0, 300, 46, 420), 22, 22, P(INK)); c.drawRoundRect(RR(0, 300, 34, 410), 16, 16, P(STEEL))
    for i in range(6): c.drawLine(-14, 160 + i * 26, 14, 160 + i * 26, P(STEEL_D, stroke=4))
    c.drawLine(0, 90, 0, 130, P(INK, stroke=14)); c.drawLine(0, 90, 0, 130, P(STEEL, stroke=8))
    c.drawCircle(0, 40, 64, P('#CFF4FF')); c.drawCircle(0, 40, 64, P(INK, stroke=8)); c.drawCircle(0, 40, 50, P(WHITE, 90, stroke=6))
    c.drawCircle(-18, 22, 14, P(WHITE, 230))
    c.restore()

def big_probe(c, x, y, rot, k=1.0):
    """explorer; tip at (x, y)"""
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(0, 0); p.quadTo(-30, 10, -40, 50); p.lineTo(-40, 140)
    c.drawPath(p, P(INK, stroke=14)); c.drawPath(p, P(STEEL_D, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-62, 140, -18, 560), 22, 22, P(INK)); c.drawRoundRect(skia.Rect.MakeLTRB(-56, 146, -24, 556), 16, 16, P(STEEL))
    for i in range(7): c.drawLine(-54, 300 + i * 26, -26, 300 + i * 26, P(STEEL_D, stroke=4))
    c.restore()

# ================================================================ cross-section molar
def _outline():
    p = skia.Path(); p.moveTo(-182, -40)
    p.cubicTo(-196, -90, -206, -160, -196, -200); p.cubicTo(-186, -250, -150, -285, -112, -282)
    p.cubicTo(-70, -278, -40, -232, 0, -228); p.cubicTo(40, -232, 70, -278, 112, -282)
    p.cubicTo(150, -285, 186, -250, 196, -200); p.cubicTo(206, -160, 196, -90, 182, -40)
    p.cubicTo(172, 60, 160, 200, 128, 312); p.cubicTo(118, 340, 96, 340, 88, 312)
    p.cubicTo(70, 220, 52, 100, 0, 70); p.cubicTo(-52, 100, -70, 220, -88, 312)
    p.cubicTo(-96, 340, -118, 340, -128, 312); p.cubicTo(-160, 200, -172, 60, -182, -40); p.close()
    return p

def _enamel():
    p = skia.Path(); p.moveTo(-182, -40)
    p.cubicTo(-196, -90, -206, -160, -196, -200); p.cubicTo(-186, -250, -150, -285, -112, -282)
    p.cubicTo(-70, -278, -40, -232, 0, -228); p.cubicTo(40, -232, 70, -278, 112, -282)
    p.cubicTo(150, -285, 186, -250, 196, -200); p.cubicTo(206, -160, 196, -90, 182, -40)
    p.lineTo(150, -50); p.cubicTo(158, -110, 160, -170, 146, -200); p.cubicTo(132, -232, 96, -246, 70, -230)
    p.cubicTo(40, -212, 20, -192, 0, -190); p.cubicTo(-20, -192, -40, -212, -70, -230)
    p.cubicTo(-96, -246, -132, -232, -146, -200); p.cubicTo(-160, -170, -158, -110, -150, -50); p.close()
    return p

def _pulp():
    q = skia.Path(); q.moveTo(-104, -40)
    q.cubicTo(-110, -100, -104, -150, -84, -160); q.cubicTo(-64, -168, -50, -120, 0, -118)
    q.cubicTo(50, -120, 64, -168, 84, -160); q.cubicTo(104, -150, 110, -100, 104, -40)
    q.cubicTo(110, 40, 122, 180, 112, 318); q.lineTo(100, 318); q.cubicTo(98, 190, 86, 80, 50, 20)
    q.cubicTo(30, 0, -30, 0, -50, 20); q.cubicTo(-86, 80, -98, 190, -100, 318); q.lineTo(-112, 318)
    q.cubicTo(-122, 180, -110, 40, -104, -40); q.close()
    return q

def _decay(d):
    depth = lerp(26, 150, d)
    p = skia.Path(); p.moveTo(-112, -282); p.cubicTo(-80, -280, -50, -250, -26, -232)
    p.cubicTo(-30, -232 + depth * 0.6, -48, -246 + depth, -70, -250 + depth)
    p.cubicTo(-96, -252 + depth, -112, -262 + depth * 0.6, -118, -276); p.close()
    return p

def _access():
    p = skia.Path(); p.moveTo(-96, -262); p.cubicTo(-40, -236, 40, -236, 96, -262)
    p.lineTo(70, -120); p.cubicTo(30, -110, -30, -110, -70, -120); p.close()
    return p

def _crown_cap():
    p = skia.Path(); p.moveTo(-190, -30)
    p.cubicTo(-204, -90, -214, -160, -204, -204); p.cubicTo(-194, -258, -154, -296, -112, -292)
    p.cubicTo(-70, -288, -40, -244, 0, -240); p.cubicTo(40, -244, 70, -288, 112, -292)
    p.cubicTo(154, -296, 194, -258, 204, -204); p.cubicTo(214, -160, 204, -90, 190, -30)
    p.cubicTo(120, -14, -120, -14, -190, -30); p.close()
    return p

OUTLINE, ENAMELP, PULPP, ACCESSP, CROWNP = _outline(), _enamel(), _pulp(), _access(), _crown_cap()
CANALS = [(-106, -30, 316), (106, -30, 316)]   # x, top y, apex y

def bone_gum(c, t, boneloss=0.0, w=340):
    bone = skia.Path(); bone.addRoundRect(skia.Rect.MakeLTRB(-w, -30, w, 440), 40, 40)
    c.drawPath(bone, lingrad((0, 0), (0, 440), BONE, BONED)); c.drawPath(bone, P(INK, stroke=7))
    for i in range(26):
        rr = random.Random(30 + i)
        c.drawCircle(rr.uniform(-w + 30, w - 30), rr.uniform(40, 420), rr.uniform(6, 14), P('#EBCB98', 200))
    if boneloss > 0:
        r = 40 + 120 * boneloss
        c.drawOval(RR(-108, 330, r * 1.6, r * 1.9), P('#C99B66', 230)); c.drawOval(RR(-108, 330, r * 1.6, r * 1.9), P(INK, 150, stroke=4))
    gum = skia.Path(); gum.moveTo(-w, -70); gum.cubicTo(-w + 60, -96, -260, -100, -200, -84)
    gum.lineTo(200, -84); gum.cubicTo(260, -100, w - 60, -96, w, -70); gum.lineTo(w, 60); gum.lineTo(-w, 60); gum.close()
    c.drawPath(gum, lingrad((0, -90), (0, 60), GUM, '#F48FA8')); c.drawPath(gum, P(INK, stroke=7))

def tooth_section(c, cx, cy, s, t, st=None, **kw):
    """big cross-section molar; st/kw keys (0..1 unless noted): decay, inflam, dead, abscess, boneloss, access,
    pulp_out, clean, med, fill, temp, core, post, crown, dam, numb, bubbles, pmood (pulp face), tmood (tooth face),
    bone (bool), dark (crown darkening)"""
    st = dict(st or {}); st.update(kw)
    g = lambda k, d=0.0: st.get(k, d)
    c.save(); c.translate(cx, cy); c.scale(s, s)
    if g('bone', True): bone_gum(c, t, g('boneloss'))
    dead = g('dead'); dark = max(dead, g('dark'))
    # dentin body
    c.drawPath(OUTLINE, lingrad((0, -280), (0, 330), mix(DENTIN[0], '#D8CFC2', dark), mix(DENTIN[1], '#BDAE9C', dark)))
    # enamel cap
    c.drawPath(ENAMELP, lingrad((0, -280), (0, -40), mix(ENAMEL[0], '#D9D2C8', dark), mix(ENAMEL[1], '#C9C0B4', dark)))
    c.drawPath(ENAMELP, P(INK, 110, stroke=3))
    hp = skia.Path(); hp.moveTo(-170, -190); hp.cubicTo(-166, -230, -146, -256, -120, -262); c.drawPath(hp, P(WHITE, 220, stroke=12))
    # empty pulp space (seen once opened) + access cavity
    acc, pout = g('access'), g('pulp_out')
    if acc > 0 or pout > 0:
        base = mix(EMPTY, CLEAN, g('clean'))
        if acc > 0: c.drawPath(ACCESSP, P(base, 255 * acc))
        c.drawPath(PULPP, P(base))
        if g('med') > 0: c.drawPath(PULPP, P(MED, 255 * g('med')))
    # living / inflamed / dead pulp tissue
    if pout < 1:
        a = 255 * (1 - pout)
        col = mix(mix(PULP, PULP_HOT, g('inflam')), PULP_DEAD, dead)
        if g('inflam') > 0 and dead < 0.5:
            c.drawPath(PULPP, P(PULP_HOT, 120 * g('inflam') * (0.6 + 0.4 * math.sin(t * 9)) * (1 - pout), blur=18))
        c.drawPath(PULPP, P(col, a))
        for (x0, y0, y1), sx in zip(CANALS, (-1, 1)):
            for off, cc in ((-5, '#FF5D6C'), (5, '#6C8DFF'), (0, '#FFD34D')):
                p = skia.Path(); p.moveTo(x0 + off * 0.6, y1 - 6); p.cubicTo(x0 + off, 160, x0 * 0.9 + off, 20, x0 * 0.5 + off, -50)
                p.quadTo(x0 * 0.75 + off, -120, x0 * 0.8 + off, -150)
                c.drawPath(p, P(mix(cc, '#9C929A', dead), a, stroke=4 if off else 5))
    # obturation (fills from the apex up)
    if g('fill') > 0:
        lvl = lerp(330, -60, ease_io(g('fill')))
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-260, lvl, 260, 340)); c.clipPath(PULPP, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(-260, -200, 260, 340), lingrad((0, -60), (0, 330), GP, GP_D))
        for (x0, y0, y1) in CANALS: c.drawLine(x0 - 3, y1 - 10, x0 - 3, -40, P(WHITE, 90, stroke=4))
        c.restore()
    if g('post') > 0:
        k = ease_out(g('post')); y_top = -150 - 260 * (1 - k)
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-300, -400, 300, 330))
        r = skia.Rect.MakeLTRB(94, y_top, 118, y_top + 300)
        c.drawRoundRect(r, 10, 10, lingrad((94, 0), (118, 0), '#F2F6FA', '#AFC0D4')); c.drawRoundRect(r, 10, 10, P(INK, stroke=4))
        c.restore()
    if g('core') > 0:
        cp = skia.Op(ACCESSP, PULPP, skia.PathOp.kUnion_PathOp)
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-300, -300, 300, -30)); c.drawPath(cp, P('#F7F3EA', 255 * g('core'))); c.restore()
    # decay (removed by the access step)
    d = g('decay') * (1 - acc)
    if d > 0:
        c.save(); c.clipPath(OUTLINE, doAntiAlias=True)
        c.drawPath(_decay(d), P(DECAY)); c.drawPath(_decay(d), P(INK, stroke=4))
        c.drawPath(_decay(d * 0.55), P(DECAY_L, 200))
        c.restore()
    if g('temp') > 0:
        k = ease_out(g('temp'))
        tp = skia.Path(); tp.moveTo(-94, -262); tp.cubicTo(-40, -238, 40, -238, 94, -262); tp.lineTo(80, -190); tp.cubicTo(30, -182, -30, -182, -80, -190); tp.close()
        c.save(); c.translate(0, -160 * (1 - k))
        c.drawPath(tp, P('#F2F2F7', 255 * min(1, g('temp') * 2))); c.drawPath(tp, P(INK, 255 * min(1, g('temp') * 2), stroke=4))
        for i in range(5): c.drawCircle(-50 + i * 25, -224 + (i % 2) * 10, 4, P('#C9C9D6'))
        c.restore()
    c.drawPath(OUTLINE, P(INK, stroke=8))
    # rubber dam sheet + clamp at the neck
    if g('dam') > 0:
        a = 255 * g('dam'); k = ease_out(g('dam')); w = 420 * k
        for sx in (-1, 1):
            r = skia.Rect.MakeLTRB(min(sx * 186, sx * (186 + w)), -78, max(sx * 186, sx * (186 + w)), -46)
            c.drawRoundRect(r, 14, 14, P(DAM, a)); c.drawRoundRect(r, 14, 14, P(INK, a, stroke=5))
            c.drawRoundRect(skia.Rect.MakeLTRB(sx * 176 - 16, -96, sx * 176 + 16, -36), 8, 8, P(STEEL, a)); c.drawRoundRect(skia.Rect.MakeLTRB(sx * 176 - 16, -96, sx * 176 + 16, -36), 8, 8, P(INK, a, stroke=4))
    if g('crown') > 0:
        k = ease_out(g('crown')); a = 255 * min(1, g('crown') * 3)
        c.save(); c.translate(0, -320 * (1 - k))
        c.drawPath(CROWNP, lingrad((0, -300), (0, -20), '#FFFFFF', '#F4ECDD')); c.drawPath(CROWNP, P(INK, a, stroke=8))
        hl = skia.Path(); hl.moveTo(-176, -196); hl.cubicTo(-170, -236, -150, -264, -124, -272); c.drawPath(hl, P(WHITE, a, stroke=14))
        c.restore()
        if g('crown') >= 1:
            for i in range(3): sparkle(c, -150 + i * 150, -330 + (i % 2) * 30, 16 + 6 * math.sin(t * 5 + i), YEL)
    # faces
    pm = g('pmood')
    if pm and pout < 0.5:
        face(c, 0, -60, pm, blink_at(t, 2), 0, 0.78, eye_dx=26, cheeks=dead < 0.5)
    tm = g('tmood')
    if tm:
        fy = -150 if g('crown') >= 0.5 else (-70 if g('fill') > 0.5 or g('core') > 0 else -40)
        face(c, 0, fy, tm, blink_at(t, 6), 0, 0.85, eye_dx=30)
    if g('abscess') > 0:
        r = 26 + 46 * g('abscess') + 4 * math.sin(t * 6)
        c.drawCircle(-108, 352, r, P('#D6B4FF')); c.drawCircle(-108, 352, r, P(INK, stroke=6))
        c.drawCircle(-108 - r * 0.35, 352 - r * 0.35, r * 0.22, P(WHITE, 150))
        if g('abscess') > 0.5: face(c, -108, 350, 'worry', blink_at(t, 9), 0, 0.5 * g('abscess'), eye_dx=22, cheeks=False)
    if g('numb') > 0:
        a = 255 * g('numb')
        for i in range(8):
            ang = i * math.pi / 4 + t * 0.8
            sparkle(c, math.cos(ang) * 300, -100 + math.sin(ang) * 260, 18 + 6 * math.sin(t * 4 + i), SKY, a)
    if g('bubbles') > 0:
        for (x0, y0, y1) in CANALS:
            for i in range(6):
                ph = (t * 0.9 + i / 6) % 1
                yy = lerp(y1 - 10, -240, ph)
                c.drawCircle(x0 + math.sin(ph * 12 + i) * 6, yy, 7 + 4 * (i % 2), P('#9FE7FF', 220 * g('bubbles')))
                c.drawCircle(x0 + math.sin(ph * 12 + i) * 6, yy, 7 + 4 * (i % 2), P(INK, 140 * g('bubbles'), stroke=2))
    c.restore()

def tooth_pt(cx, cy, s, x, y):
    return cx + x * s, cy + y * s

# ================================================================ tools
FILE_COLS = ['#FFD34D', '#FF5D6C', '#5DA8FF', '#5FD38A']
def endo_file(c, x, ytip, s, col, a=255):
    """endodontic file; tip at (x, ytip) in screen coords; length ~430*s"""
    c.save(); c.translate(x, ytip); c.scale(s, s)
    c.drawLine(0, -360, 0, 0, P(INK, a, stroke=12)); c.drawLine(0, -360, 0, -2, P(STEEL, a, stroke=6))
    for i in range(12):
        y = -14 - i * 22; c.drawLine(-7, y, 7, y - 10, P(STEEL_D, a, stroke=3))
    h = skia.Path(); h.addRoundRect(skia.Rect.MakeLTRB(-26, -450, 26, -360), 18, 18); c.drawPath(h, P(col, a)); c.drawPath(h, P(INK, a, stroke=6))
    for i in range(3): c.drawLine(-18, -430 + i * 22, 18, -430 + i * 22, P(INK, a * 0.4, stroke=3))
    c.restore()

def gp_cone(c, x, ytip, s, a=255):
    c.save(); c.translate(x, ytip); c.scale(s, s)
    p = _poly([(-4, 0), (4, 0), (12, -300), (-12, -300)]); c.drawPath(p, P(GP, a)); c.drawPath(p, P(INK, a, stroke=4))
    c.drawRoundRect(skia.Rect.MakeLTRB(-16, -330, 16, -296), 8, 8, P(GP_D, a)); c.drawRoundRect(skia.Rect.MakeLTRB(-16, -330, 16, -296), 8, 8, P(INK, a, stroke=4))
    c.restore()

def handpiece(c, x, y, s, t, on=1.0):
    """dental drill; bur tip at (x, y)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    jit = math.sin(t * 90) * 2 * on
    c.translate(jit, 0)
    c.drawLine(0, 0, 0, -60, P(INK, stroke=12)); c.drawLine(0, 0, 0, -60, P('#FFE08A', stroke=6))
    hd = skia.Path(); hd.addRoundRect(skia.Rect.MakeLTRB(-40, -110, 40, -56), 24, 24); fill(c, hd, STEEL, stroke=6)
    c.save(); c.translate(30, -84); c.rotate(-28)
    bd = skia.Path(); bd.addRoundRect(skia.Rect.MakeLTRB(0, -30, 460, 30), 30, 30); fill(c, bd, grad_paint((0, -30), (0, 30), '#FFFFFF', '#C9D8EA'), stroke=6)
    for i in range(5): c.drawLine(240 + i * 30, -24, 240 + i * 30, 24, P(STEEL_D, stroke=4))
    c.drawRoundRect(skia.Rect.MakeLTRB(120, -12, 200, 12), 8, 8, P(TEAL))
    c.restore()
    if on > 0:
        for i in range(10):
            ph = (t * 3 + i / 10) % 1; ang = math.radians(-150 + i * 34)
            c.drawCircle(math.cos(ang) * 120 * ph, -10 + math.sin(ang) * 80 * ph + 60 * ph * ph, 7 * (1 - ph) + 2, P(SKY, 220 * (1 - ph) * on))
    c.restore()

def calendar_icon(c, x, y, s, t, txt='6'):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(RR(8, 10, 200, 200), 26, 26, P(INK, 60))
    c.drawRoundRect(RR(0, 0, 200, 200), 26, 26, P(WHITE)); c.drawRoundRect(RR(0, 0, 200, 200), 26, 26, P(INK, stroke=7))
    top = skia.Path(); top.addRoundRect(skia.Rect.MakeLTRB(-100, -100, 100, -40), 26, 26); c.drawPath(top, P(CORAL)); c.drawPath(top, P(INK, stroke=7))
    for sx in (-1, 1): c.drawRoundRect(skia.Rect.MakeLTRB(sx * 50 - 9, -122, sx * 50 + 9, -80), 8, 8, P(STEEL)); c.drawRoundRect(skia.Rect.MakeLTRB(sx * 50 - 9, -122, sx * 50 + 9, -80), 8, 8, P(INK, stroke=5))
    c.restore()
    draw_img(c, text_img(txt, int(64 * s), INK, 0), x, y + 30 * s, 1)

def floss(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.addRoundRect(RR(0, 0, 150, 120), 30, 30); fill(c, b, MINT)
    c.drawRoundRect(RR(0, -40, 110, 30), 12, 12, P(TEAL)); c.drawRoundRect(RR(0, -40, 110, 30), 12, 12, P(INK, stroke=5))
    p = skia.Path(); p.moveTo(30, -50); p.cubicTo(80, -140, 140, -60, 160, -150); c.drawPath(p, P(WHITE, stroke=6)); c.drawPath(p, P(INK, 120, stroke=2))
    face(c, 0, 18, 'happy', blink_at(t, 7), 0, 0.6, eye_dx=24)
    c.restore()

def xray_card(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(RR(8, 10, 200, 160), 20, 20, P(INK, 60))
    c.drawRoundRect(RR(0, 0, 200, 160), 20, 20, P('#1B2A47')); c.drawRoundRect(RR(0, 0, 200, 160), 20, 20, P(INK, stroke=7))
    c.save(); c.translate(0, 6); c.scale(0.38, 0.38); c.drawPath(TOOTH, P('#DCE7F5')); c.restore()
    c.restore()

# ================================================================ x-ray on the big monitor
def xray_view(c, cx, cy, w, h, t, decay=1.0, lesion=1.0, ring=0.0, labels_k=0.0, ring2=None):
    ring2 = ring if ring2 is None else ring2
    """monitor with a periapical x-ray of the molar: decay reaches the pulp, dark spot at the root tip"""
    # stand + bezel
    c.drawRoundRect(skia.Rect.MakeLTRB(cx - 30, cy + h / 2, cx + 30, cy + h / 2 + 120), 10, 10, P(STEEL)); c.drawRoundRect(skia.Rect.MakeLTRB(cx - 30, cy + h / 2, cx + 30, cy + h / 2 + 120), 10, 10, P(INK, stroke=6))
    c.drawRoundRect(RR(cx, cy + h / 2 + 124, 260, 30), 14, 14, P(STEEL)); c.drawRoundRect(RR(cx, cy + h / 2 + 124, 260, 30), 14, 14, P(INK, stroke=6))
    c.drawRoundRect(RR(cx + 10, cy + 14, w + 40, h + 40), 34, 34, P(INK, 70))
    c.drawRoundRect(RR(cx, cy, w + 40, h + 40), 34, 34, P('#33456A')); c.drawRoundRect(RR(cx, cy, w + 40, h + 40), 34, 34, P(INK, stroke=8))
    scr = RR(cx, cy, w, h)
    c.save(); c.clipRect(scr)
    c.drawRect(scr, lingrad((0, cy - h / 2), (0, cy + h / 2), '#1A2238', '#0C1222'))
    sc = h / 820
    tx, ty = cx, cy - 20 * sc * 10 / 10
    # bone haze
    c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, ty - 40 * sc, cx + w / 2, cy + h / 2), P('#55607A', 150))
    for i in range(40):
        rr = random.Random(500 + i)
        c.drawCircle(rr.uniform(cx - w / 2, cx + w / 2), rr.uniform(ty, cy + h / 2), rr.uniform(4, 12), P('#6B7894', 90))
    # neighbour teeth (half visible)
    for sx in (-1, 1):
        c.save(); c.translate(tx + sx * 470 * sc, ty); c.scale(sc, sc)
        c.drawPath(OUTLINE, P('#B9C4D8', 230)); c.drawPath(PULPP, P('#5E6A84', 230)); c.restore()
    c.save(); c.translate(tx, ty); c.scale(sc, sc)
    c.drawPath(OUTLINE, P('#C6D1E4')); c.drawPath(ENAMELP, P('#EEF3FB'))
    c.drawPath(PULPP, P('#56627E'))
    if decay > 0:
        c.save(); c.clipPath(OUTLINE, doAntiAlias=True)
        c.drawPath(_decay(decay), P('#2A3350')); c.restore()
    if lesion > 0:
        c.drawOval(RR(-108, 350, 120 * lesion, 110 * lesion), P('#2A3350', 230))
        c.drawCircle(-108, 350, (90 + 8 * math.sin(t * 7)) * lesion, P(CORAL, 255 * ring2, stroke=10))
    if ring > 0:
        c.drawCircle(-70, -190, 80 + 6 * math.sin(t * 7), P(YEL, 255 * ring, stroke=10))
    c.restore()
    c.drawRect(scr, P(WHITE, 18))
    c.restore()
    # glare
    gl = skia.Path(); gl.moveTo(cx - w / 2 + 30, cy - h / 2 + 20); gl.lineTo(cx - w / 2 + 140, cy - h / 2 + 20); gl.lineTo(cx - w / 2 + 40, cy - h / 2 + 140); gl.close()
    c.drawPath(gl, P(WHITE, 30))
    return (tx + -70 * sc, ty - 190 * sc), (tx - 108 * sc, ty + 350 * sc)

# ================================================================ scene 1 props
def ice_cream(c, x, y, s, t, bite=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    cone = _poly([(-70, 0), (70, 0), (0, 220)]); fill(c, cone, grad_paint((0, 0), (0, 220), '#F7C77F', '#E4A35A'))
    for i in range(-2, 3):
        c.drawLine(-60 + i * 30, 10, 0 + i * 30 * 0.2, 200, P('#C98A45', stroke=4))
    for dx, dy, col in ((-36, -40, '#FFB3C7'), (36, -40, '#B8F0D8'), (0, -100, '#FFF1B8')):
        sc = skia.Path(); sc.addCircle(dx, dy, 62); fill(c, sc, col, stroke=7)
    if bite > 0:
        c.drawCircle(50, -136, 40 * bite, P('#FFEFF7')); c.drawCircle(50, -136, 40 * bite, P(INK, stroke=6))
    face(c, 0, -96, 'happy', blink_at(t, 1), 0, 0.7, eye_dx=24)
    for i in range(3): c.drawCircle(-30 + i * 30, -150 + (i % 2) * 14, 6, P(['#FF6B8A', '#4FC3F7', '#FFD34D'][i]))
    c.restore()

def night_room(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), '#26315E', '#4B4F8F'))
    for i in range(30):
        rr = random.Random(900 + i)
        sparkle(c, rr.uniform(40, W - 40), rr.uniform(150, 1000), 6 + 6 * rr.random(), '#FFF7C2', 120 + 100 * math.sin(t * 2 + i))
    wr = skia.Rect.MakeLTRB(600, 330, 980, 760)
    c.drawRoundRect(skia.Rect.MakeLTRB(586, 316, 994, 774), 24, 24, P('#C8D2F0')); c.drawRoundRect(skia.Rect.MakeLTRB(586, 316, 994, 774), 24, 24, P(INK, stroke=7))
    c.drawRect(wr, lingrad((0, 330), (0, 760), '#101A3F', '#2C3A78'))
    c.save(); c.clipRect(wr)
    c.drawCircle(860, 440, 64, P('#FFF3B0')); c.drawCircle(886, 420, 56, P('#1B2552'))
    for i in range(8):
        rr = random.Random(950 + i); sparkle(c, rr.uniform(620, 960), rr.uniform(350, 740), 8, '#FFF7C2', 200)
    c.restore()
    c.drawLine(790, 330, 790, 760, P('#C8D2F0', stroke=12)); c.drawLine(600, 545, 980, 545, P('#C8D2F0', stroke=12))
    c.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), P('#3A3D74'))

def alarm_clock(c, x, y, s, t, txt='02:00'):
    c.save(); c.translate(x, y + math.sin(t * 20) * 2); c.scale(s, s)
    for sx in (-1, 1): c.drawCircle(sx * 70, -96, 34, P(YEL)); c.drawCircle(sx * 70, -96, 34, P(INK, stroke=6))
    c.drawRoundRect(RR(0, 0, 240, 170), 50, 50, P('#FF8FAB')); c.drawRoundRect(RR(0, 0, 240, 170), 50, 50, P(INK, stroke=7))
    c.drawRoundRect(RR(0, 0, 180, 92), 20, 20, P('#1B2552')); c.drawRoundRect(RR(0, 0, 180, 92), 20, 20, P(INK, stroke=5))
    c.restore()
    draw_img(c, text_img(txt, int(58 * s), '#7CFFB2', 0), x, y + 2, 1)

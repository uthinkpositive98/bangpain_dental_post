"""ep12 props (copied for ep13, with the gum props appended at the end): breath cloud, tongue, open mouth cut-away, magnifier, Thai foods (สะตอ, กระเทียม, ส้มตำ, กาแฟเย็น),
water glass, saliva drop, floss, tongue cleaner, mirror, bed/moon/sun, myth/fact stamps, quiz cards, office desk.
Same ink/pastel style as tools/kawaii.py."""
import math, random
import skia
from tools.kawaii import *  # noqa: F401,F403

STINK = '#B9E07A'; STINK_D = '#8FC24F'; LIP = '#FF8FA3'; MOUTH = '#7A2E3B'; TONGUE = '#FF9EB0'; TONGUE_D = '#F2728E'
GREEN = '#7ED957'; GREEN_D = '#3E9B2F'; BROWN = '#A0673A'; COFFEE = '#C98B55'

def fillp(c, p, col, a=255, stroke=7):
    c.drawPath(p, P(col, a) if isinstance(col, str) else col)
    if stroke: c.drawPath(p, P(INK, a, stroke=stroke))

def blobs(c, pts, col, a=255, stroke=7):
    """outlined union of circles [(x, y, r)]"""
    for (x, y, r) in pts: c.drawCircle(x, y, r + stroke / 2, P(INK, a))
    for (x, y, r) in pts: c.drawCircle(x, y, r - stroke / 2, P(col, a))

# ---------------------------------------------------------------- breath cloud (cute mischievous stink)
def breath_cloud(c, x, y, s=1.0, t=0.0, a=255, mood='squeeze', seed=0, face_on=True, col=STINK):
    if s <= 0.01 or a <= 1: return
    c.save(); c.translate(x, y + math.sin(t * 3 + seed) * 6); c.scale(s, s)
    wob = math.sin(t * 5 + seed) * 0.04; c.scale(1 + wob, 1 - wob)
    pts = [(-70, 10, 55), (0, -25, 70), (70, 5, 58), (-20, 40, 50), (40, 40, 48)]
    blobs(c, pts, col, a)
    c.drawCircle(-30, -45, 14, P(WHITE, 0.5 * a))
    # stink squiggles
    for i, dx in enumerate((-60, 0, 60)):
        ph = (t * 0.9 + i * 0.33 + seed * 0.1) % 1
        p = skia.Path(); yy = -100 - ph * 60
        p.moveTo(dx, yy); p.cubicTo(dx + 18, yy - 18, dx - 18, yy - 36, dx, yy - 54)
        c.drawPath(p, P(STINK_D, a * (1 - ph), stroke=7))
    if face_on:
        c.saveLayer(None, skia.Paint(Alphaf=a / 255))
        face(c, 0, 5, mood, blink_at(t, seed + 3), 0, 0.85, eye_dx=28)
        c.restore()
    c.restore()

def fresh_breath(c, x, y, s=1.0, t=0.0, a=255):
    """minty sparkly breath"""
    c.save(); c.translate(x, y); c.scale(s, s)
    blobs(c, [(-50, 0, 40), (0, -20, 50), (50, 0, 42)], MINT, a)
    for i in range(4):
        sparkle(c, -60 + i * 40, -60 - 20 * math.sin(t * 4 + i), 14 + 6 * math.sin(t * 5 + i), YEL, a)
    c.restore()

# ---------------------------------------------------------------- magnifier
def magnifier(c, x, y, s=1.0, rot=-30, glint=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-22, 95, 22, 300), 20, 20, P(BROWN)); c.drawRoundRect(skia.Rect.MakeLTRB(-22, 95, 22, 300), 20, 20, P(INK, stroke=7))
    c.drawCircle(0, 0, 105, P('#CFF4FF', 110)); c.drawCircle(0, 0, 105, P(YEL, stroke=22)); c.drawCircle(0, 0, 105, P(INK, stroke=6))
    c.drawCircle(0, 0, 116, P(INK, stroke=5))
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-75, -75, 75, 75), 200, 60); c.drawPath(p, P(WHITE, 200, stroke=12))
    if glint > 0: sparkle(c, 60, -70, 30 * glint, WHITE)
    c.restore()

# ---------------------------------------------------------------- tongue character (front view)
def tongue_char(c, x, y, s=1.0, t=0.0, coat=0.0, mood='smile', seed=0, clean=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    wob = math.sin(t * 4 + seed) * 0.03; c.scale(1 - wob, 1 + wob)
    p = skia.Path(); p.moveTo(-100, -175); p.lineTo(100, -175); p.quadTo(155, -175, 152, -110)
    p.cubicTo(160, 30, 150, 170, 0, 180); p.cubicTo(-150, 170, -160, 30, -152, -110); p.quadTo(-155, -175, -100, -175); p.close()
    fillp(c, p, lingrad((0, -150), (0, 180), TONGUE_D, TONGUE))
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawLine(0, -150, 0, 40, P(TONGUE_D, stroke=8))
    rr = random.Random(7)
    for i in range(40):   # papillae dots
        c.drawCircle(rr.uniform(-140, 140), rr.uniform(-150, 140), rr.uniform(3, 6), P('#E96A86', 120))
    if coat > 0:
        rr = random.Random(11)
        for i in range(26):
            bx, by = rr.uniform(-130, 130), rr.uniform(-150, -10)
            r = rr.uniform(22, 40) * (1 - 0.7 * clean)
            c.drawCircle(bx, by, r, P('#FFF8E7', 235 * coat))
        c.drawRect(skia.Rect.MakeLTRB(-160, -160, 160, -40), P('#FFF8E7', 150 * coat * (1 - clean)))
    c.restore()
    c.drawPath(p, P(INK, stroke=7))
    face(c, 0, 80, mood, blink_at(t, seed + 1), 0, 0.9, eye_dx=34)
    c.restore()

# ---------------------------------------------------------------- open mouth cut-away (front)
def open_mouth(c, x, y, s=1.0, t=0.0, coat=0.6, food=0.0, germs=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(RR(0, 0, 640, 440), P(LIP)); c.drawOval(RR(0, 0, 640, 440), P(INK, stroke=8))
    inner = skia.Path(); inner.addOval(RR(0, 0, 540, 340))
    c.drawPath(inner, P(MOUTH))
    c.save(); c.clipPath(inner, doAntiAlias=True)
    # throat
    c.drawOval(RR(0, -20, 150, 120), P('#5C1F2B'))
    # tongue (lower)
    tp = skia.Path(); tp.moveTo(-230, 170); tp.cubicTo(-220, 0, -90, -20, 0, -10)
    tp.cubicTo(90, -20, 220, 0, 230, 170); tp.close()
    c.drawPath(tp, lingrad((0, -10), (0, 170), TONGUE_D, TONGUE)); c.drawPath(tp, P(INK, stroke=6))
    if coat > 0:
        rr = random.Random(3)
        for i in range(16):
            c.drawCircle(rr.uniform(-140, 140), rr.uniform(10, 70), rr.uniform(14, 26), P('#FFF8E7', 230 * coat))
    # teeth rows
    for row, yy, fl in ((0, -170, 1), (1, 170, -1)):
        for i in range(8):
            tx = -245 + i * 70
            ty = yy + fl * (abs(tx) / 245) ** 2 * 30
            r = RR(tx, ty + fl * 40, 60, 80)
            c.drawRoundRect(r, 22, 22, P(WHITE)); c.drawRoundRect(r, 22, 22, P(INK, stroke=5))
    if food > 0:
        for (fx, fy) in ((-140, -112), (70, -108), (-75, 118), (140, 112)):
            c.drawCircle(fx + 35, fy, 13 * food, P(YEL)); c.drawCircle(fx + 35, fy, 13 * food, P(INK, stroke=4))
    c.restore()
    c.drawPath(inner, P(INK, stroke=7))
    c.restore()
    if germs:
        for i, (gx, gy) in enumerate(((-110, 30), (60, 50), (150, 20))):
            germ(c, x + gx * s, y + gy * s, 0.32 * s, t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i], mood='happy')

# ---------------------------------------------------------------- foods and drinks
def sator(c, x, y, s=1.0, t=0.0, mood='happy', rot=0, face_on=True):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.moveTo(-170, 10); p.cubicTo(-120, -60, 120, -60, 170, 10); p.cubicTo(120, 40, -120, 40, -170, 10); p.close()
    fillp(c, p, lingrad((0, -50), (0, 40), GREEN, GREEN_D))
    for i in range(5):
        bx = -110 + i * 55
        c.drawCircle(bx, -8, 20, P('#C7F09A')); c.drawCircle(bx, -8, 20, P(INK, stroke=5))
    if face_on: face(c, 0, -2, mood, blink_at(t, 9), 0, 0.5, eye_dx=24, cheeks=False)
    c.restore()

def garlic(c, x, y, s=1.0, t=0.0, mood='happy', seed=0):
    c.save(); c.translate(x, y + math.sin(t * 4 + seed) * 5); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, -110); p.cubicTo(20, -70, 110, -40, 100, 30)
    p.cubicTo(95, 90, -95, 90, -100, 30); p.cubicTo(-110, -40, -20, -70, 0, -110); p.close()
    fillp(c, p, lingrad((0, -110), (0, 90), WHITE, '#EDE3F7'))
    for dx in (-40, 0, 40): c.drawLine(dx * 0.5, -70, dx, 70, P('#CDBDE0', stroke=5))
    face(c, 0, 20, mood, blink_at(t, seed), 0, 0.6, eye_dx=26)
    c.restore()

def onion(c, x, y, s=1.0, t=0.0, mood='happy', seed=0):
    c.save(); c.translate(x, y + math.sin(t * 4 + seed) * 5); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, -120); p.cubicTo(30, -60, 100, -40, 95, 30)
    p.cubicTo(90, 95, -90, 95, -95, 30); p.cubicTo(-100, -40, -30, -60, 0, -120); p.close()
    fillp(c, p, lingrad((0, -120), (0, 90), '#E7A1D6', '#B565A7'))
    face(c, 0, 20, mood, blink_at(t, seed), 0, 0.6, eye_dx=26)
    c.restore()

def plate(c, x, y, s=1.0, kind='somtam', t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(RR(6, 12, 300, 110), P(INK, 60))
    c.drawOval(RR(0, 0, 300, 110), P(WHITE)); c.drawOval(RR(0, 0, 300, 110), P(INK, stroke=6))
    c.drawOval(RR(0, -4, 230, 74), P('#EEF6FA'))
    rr = random.Random(hash(kind) % 100)
    cols = {'somtam': ['#FFE08A', '#FF8F6B', '#9BE15D'], 'sator': ['#7ED957', '#FFB38A', '#C98B55'],
            'egg': ['#FFD166', '#F4A93B', '#FFE7A0']}[kind]
    for i in range(22):
        px, py = rr.uniform(-90, 90), rr.uniform(-40, 10)
        cc = rr.choice(cols)
        if kind == 'somtam':
            c.save(); c.translate(px, py); c.rotate(rr.uniform(0, 180))
            c.drawRoundRect(skia.Rect.MakeLTRB(-26, -5, 26, 5), 5, 5, P(cc)); c.restore()
        else:
            c.drawCircle(px, py, rr.uniform(10, 18), P(cc)); c.drawCircle(px, py, rr.uniform(10, 18), P(INK, 120, stroke=3))
    c.restore()
    # steam
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        p = skia.Path(); sx = x + (i - 1) * 50 * s; sy = y - 50 * s - ph * 90 * s
        p.moveTo(sx, sy); p.cubicTo(sx + 14, sy - 16, sx - 14, sy - 30, sx, sy - 46)
        c.drawPath(p, P(WHITE, 220 * (1 - ph), stroke=7))

def iced_coffee(c, x, y, s=1.0, t=0.0, mood=None, level=1.0, col=COFFEE):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawLine(20, -170, 50, -260, P(INK, stroke=16)); c.drawLine(20, -170, 50, -260, P(CORAL, stroke=9))
    cup = skia.Path(); cup.moveTo(-80, -170); cup.lineTo(80, -170); cup.lineTo(62, 120); cup.lineTo(-62, 120); cup.close()
    c.drawPath(cup, P(WHITE, 160))
    c.save(); c.clipPath(cup, doAntiAlias=True)
    lv = -170 + 290 * (1 - level) + 20
    c.drawRect(skia.Rect.MakeLTRB(-90, lv, 90, 130), lingrad((0, lv), (0, 130), col, '#8A5530'))
    for (ix, iy) in ((-30, lv + 40), (25, lv + 70)):
        c.drawRoundRect(RR(ix, iy, 46, 40), 10, 10, P(WHITE, 160))
    c.restore()
    c.drawPath(cup, P(INK, stroke=7))
    c.drawOval(RR(0, -170, 170, 34), P(WHITE, 160)); c.drawOval(RR(0, -170, 170, 34), P(INK, stroke=6))
    if mood: face(c, 0, 40, mood, blink_at(t, 6), 0, 0.6, eye_dx=24)
    c.restore()

def water_glass(c, x, y, s=1.0, t=0.0, mood='happy', level=0.85):
    c.save(); c.translate(x, y); c.scale(s, s)
    cup = skia.Path(); cup.moveTo(-75, -150); cup.lineTo(75, -150); cup.lineTo(60, 120); cup.lineTo(-60, 120); cup.close()
    c.drawPath(cup, P(WHITE, 170))
    c.save(); c.clipPath(cup, doAntiAlias=True)
    lv = -150 + 270 * (1 - level) + 5 * math.sin(t * 4)
    c.drawRect(skia.Rect.MakeLTRB(-90, lv, 90, 130), lingrad((0, lv), (0, 130), '#9BE7FF', SKY))
    c.drawRect(skia.Rect.MakeLTRB(28, -140, 44, 110), P(WHITE, 120))
    c.restore()
    c.drawPath(cup, P(INK, stroke=7))
    face(c, 0, 30, mood, blink_at(t, 8), 0, 0.6, eye_dx=24)
    c.restore()

def saliva_drop(c, x, y, s=1.0, t=0.0, mood='happy', seed=0):
    c.save(); c.translate(x, y + math.sin(t * 5 + seed) * 6); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, -110); p.cubicTo(60, -30, 80, 20, 70, 50)
    p.cubicTo(55, 100, -55, 100, -70, 50); p.cubicTo(-80, 20, -60, -30, 0, -110); p.close()
    fillp(c, p, lingrad((0, -110), (0, 90), '#E6FAFF', SKY))
    c.drawCircle(-28, -10, 12, P(WHITE, 200))
    face(c, 0, 35, mood, blink_at(t, seed), 0, 0.6, eye_dx=24)
    c.restore()

def candy(c, x, y, s=1.0, rot=0, col=MINT):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for sx in (-1, 1):
        p = skia.Path(); p.moveTo(sx * 40, 0); p.lineTo(sx * 85, -30); p.lineTo(sx * 85, 30); p.close(); fillp(c, p, col, stroke=5)
    c.drawCircle(0, 0, 45, P(col)); c.drawCircle(0, 0, 45, P(INK, stroke=6))
    for i in range(3): c.drawLine(-30 + i * 25, -30, -10 + i * 25, 30, P(WHITE, 200, stroke=8))
    c.restore()

def mouthwash(c, x, y, s=1.0, t=0.0, mood='smile'):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-40, -210, 40, -150), 14, 14, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-40, -210, 40, -150), 14, 14, P(INK, stroke=6))
    b = skia.Path(); b.addRoundRect(skia.Rect.MakeLTRB(-80, -160, 80, 150), 50, 50)
    fillp(c, b, lingrad((0, -160), (0, 150), '#8EF0E0', '#2EC4B6'))
    c.drawRoundRect(skia.Rect.MakeLTRB(-60, -40, 60, 60), 16, 16, P(WHITE, 220))
    face(c, 0, 10, mood, blink_at(t, 4), 0, 0.6, eye_dx=24)
    c.restore()

def floss(c, x0, y0, x1, y1, t=0.0, a=255):
    """floss strand between two little dispensers"""
    c.drawLine(x0, y0, x1, y1, P(INK, a, stroke=10)); c.drawLine(x0, y0, x1, y1, P(WHITE, a, stroke=5))
    for (xx, yy) in ((x0, y0), (x1, y1)):
        c.drawRoundRect(RR(xx, yy, 60, 60), 18, 18, P(SKY, a)); c.drawRoundRect(RR(xx, yy, 60, 60), 18, 18, P(INK, a, stroke=6))

def tongue_cleaner(c, x, y, s=1.0, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.moveTo(-120, -20); p.quadTo(0, -110, 120, -20)
    c.drawPath(p, P(INK, stroke=30)); c.drawPath(p, P(LAV, stroke=18))
    c.drawRoundRect(skia.Rect.MakeLTRB(-130, -30, -100, 220), 15, 15, P(LAV)); c.drawRoundRect(skia.Rect.MakeLTRB(-130, -30, -100, 220), 15, 15, P(INK, stroke=6))
    c.drawRoundRect(skia.Rect.MakeLTRB(100, -30, 130, 220), 15, 15, P(LAV)); c.drawRoundRect(skia.Rect.MakeLTRB(100, -30, 130, 220), 15, 15, P(INK, stroke=6))
    c.restore()

def hand_mirror(c, x, y, s=1.0, rot=0, t=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-24, 120, 24, 330), 20, 20, P(PINK)); c.drawRoundRect(skia.Rect.MakeLTRB(-24, 120, 24, 330), 20, 20, P(INK, stroke=6))
    c.drawOval(RR(0, 0, 250, 280), P(PINK)); c.drawOval(RR(0, 0, 250, 280), P(INK, stroke=7))
    c.drawOval(RR(0, 0, 200, 230), lingrad((0, -115), (0, 115), '#E8FBFF', '#B9E9F7')); c.drawOval(RR(0, 0, 200, 230), P(INK, stroke=5))
    p = skia.Path(); p.moveTo(-50, -60); p.lineTo(-10, -90); c.drawPath(p, P(WHITE, stroke=12))
    c.restore()

def stomach(c, x, y, s=1.0, t=0.0, mood='worry'):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-60, -150); p.cubicTo(-70, -60, -150, -40, -140, 50)
    p.cubicTo(-130, 150, 60, 160, 120, 90); p.cubicTo(170, 30, 130, -40, 60, -20)
    p.cubicTo(20, -10, 0, -80, 10, -150); p.close()
    fillp(c, p, lingrad((0, -150), (0, 150), '#FFC2D1', '#FF8FAB'))
    face(c, -20, 50, mood, blink_at(t, 2), 0, 0.7, eye_dx=28)
    c.restore()

def cigarette_no(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 110, 16), 10, 10, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 110, 16), 10, 10, P(INK, stroke=5))
    c.drawRoundRect(skia.Rect.MakeLTRB(50, -16, 110, 16), 10, 10, P('#F4A93B')); c.drawRoundRect(skia.Rect.MakeLTRB(50, -16, 110, 16), 10, 10, P(INK, stroke=5))
    c.drawCircle(0, 0, 150, P(CORAL, stroke=18)); c.drawLine(-106, -106, 106, 106, P(CORAL, stroke=18))
    c.restore()

def bottle(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.moveTo(-22, -150); b.lineTo(22, -150); b.lineTo(22, -80); b.cubicTo(60, -60, 60, -40, 60, 0)
    b.lineTo(60, 140); b.lineTo(-60, 140); b.lineTo(-60, 0); b.cubicTo(-60, -40, -60, -60, -22, -80); b.close()
    fillp(c, b, lingrad((0, -150), (0, 140), '#9AD48C', '#4E9F48'))
    c.drawRoundRect(skia.Rect.MakeLTRB(-45, 10, 45, 80), 10, 10, P(WHITE, 220))
    c.drawCircle(150 - 150, 45, 0, P(INK))
    c.restore()
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, 175, P(CORAL, stroke=18)); c.drawLine(-124, -124, 124, 124, P(CORAL, stroke=18))
    c.restore()

def denture(c, x, y, s=1.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    g = skia.Path(); g.moveTo(-150, 0); g.cubicTo(-150, -110, 150, -110, 150, 0); g.cubicTo(110, -40, -110, -40, -150, 0); g.close()
    fillp(c, g, lingrad((0, -90), (0, 0), GUM, GUMD))
    for i in range(6):
        ang = math.pi + (i + 0.5) / 6 * math.pi
        tx, ty = math.cos(ang) * 120, math.sin(ang) * 80 + 30
        c.drawRoundRect(RR(tx, ty, 44, 54), 16, 16, P(WHITE)); c.drawRoundRect(RR(tx, ty, 44, 54), 16, 16, P(INK, stroke=5))
    c.restore()

def sinus_nose(c, x, y, s=1.0, t=0.0):
    """a little doctor-referral icon: stethoscope"""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-60, -110); p.cubicTo(-80, 40, 80, 40, 60, -110)
    c.drawPath(p, P(INK, stroke=18)); c.drawPath(p, P(TI2, stroke=10))
    p2 = skia.Path(); p2.moveTo(0, 0); p2.cubicTo(0, 90, 110, 120, 120, 40)
    c.drawPath(p2, P(INK, stroke=18)); c.drawPath(p2, P(TI2, stroke=10))
    c.drawCircle(120, 30, 34, P(TI1)); c.drawCircle(120, 30, 34, P(INK, stroke=7))
    c.restore()

# ---------------------------------------------------------------- scenery
def bedroom(c, t, night=0.0):
    top = '#B8C6FF' if night > 0.5 else '#FFE7C7'; bot = '#E3E8FF' if night > 0.5 else '#FFF5E1'
    background(c, t, top, bot, dots=False)
    # window with sun
    c.drawRoundRect(skia.Rect.MakeLTRB(1340, 130, 1760, 470), 30, 30, P('#BDEBFF')); c.drawRoundRect(skia.Rect.MakeLTRB(1340, 130, 1760, 470), 30, 30, P(INK, stroke=8))
    c.drawCircle(1600, 270, 70 + 6 * math.sin(t * 2), P(YEL)); c.drawCircle(1600, 270, 70 + 6 * math.sin(t * 2), P(INK, stroke=6))
    c.drawLine(1550, 130, 1550, 470, P(INK, stroke=8)); c.drawLine(1340, 300, 1760, 300, P(INK, stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), P('#F2D4B6')); c.drawLine(0, 900, W, 900, P(INK, stroke=7))

def bed(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-420, -260, -360, 160), 24, 24, P(BROWN)); c.drawRoundRect(skia.Rect.MakeLTRB(-420, -260, -360, 160), 24, 24, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-380, 0, 420, 130), 30, 30, P(BROWN)); c.drawRoundRect(skia.Rect.MakeLTRB(-380, 0, 420, 130), 30, 30, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-370, -60, 410, 40), 40, 40, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-370, -60, 410, 40), 40, 40, P(INK, stroke=7))
    c.restore()

def blanket(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.addRoundRect(skia.Rect.MakeLTRB(-330, -40, 420, 90), 50, 50); fillp(c, b, lingrad((0, -40), (0, 90), '#FFB3C7', '#FF8FAB'))
    for i in range(5): c.drawCircle(-250 + i * 150, 25, 16, P(WHITE, 200))
    c.restore()

def office(c, t):
    background(c, t, '#D8F3EE', '#F3FFF9', dots=False)
    for i in range(3):   # wall frames / window
        x0 = 220 + i * 560
        c.drawRoundRect(skia.Rect.MakeLTRB(x0, 140, x0 + 300, 360), 22, 22, P(WHITE, 200)); c.drawRoundRect(skia.Rect.MakeLTRB(x0, 140, x0 + 300, 360), 22, 22, P(INK, 120, stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), P('#E6D3BE')); c.drawLine(0, 860, W, 860, P(INK, stroke=7))

def desk(c, x, y, w=700):
    c.drawRoundRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + 50), 16, 16, P('#F4C27F')); c.drawRoundRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + 50), 16, 16, P(INK, stroke=7))
    for sx in (-1, 1):
        c.drawRoundRect(skia.Rect.MakeLTRB(x + sx * (w / 2 - 60) - 18, y + 50, x + sx * (w / 2 - 60) + 18, y + 220), 10, 10, P('#D9A35E'))
        c.drawRoundRect(skia.Rect.MakeLTRB(x + sx * (w / 2 - 60) - 18, y + 50, x + sx * (w / 2 - 60) + 18, y + 220), 10, 10, P(INK, stroke=6))

def sink(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-260, 0, 260, 60), 26, 26, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-260, 0, 260, 60), 26, 26, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-120, 60, 120, 300), 30, 30, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-120, 60, 120, 300), 30, 30, P(INK, stroke=7))
    c.restore()

# ---------------------------------------------------------------- game pieces
def stamp(c, x, y, ok, t, t0, s=1.0):
    """big round verdict stamp: ok=True -> จริง (green ✓), False -> ไม่จริง (coral ✗)"""
    cue(t, t0, 'ding' if ok else 'boing')
    k = pop(t, t0, 0.4)
    if k <= 0: return
    sc = s * (1 + 0.6 * (1 - seg(t, t0, t0 + 0.25))) * k
    c.save(); c.translate(x, y); c.rotate(-12); c.scale(sc, sc)
    col = GREEN if ok else CORAL
    c.drawCircle(8, 10, 150, P(INK, 70)); c.drawCircle(0, 0, 150, P(WHITE)); c.drawCircle(0, 0, 150, P(col, stroke=22)); c.drawCircle(0, 0, 150, P(INK, stroke=6))
    if ok:
        p = skia.Path(); p.moveTo(-60, -40); p.lineTo(-15, 5); p.lineTo(65, -75)
    else:
        p = skia.Path(); p.moveTo(-50, -90); p.lineTo(50, 0); p.moveTo(50, -90); p.lineTo(-50, 0)
    c.drawPath(p, P(col, stroke=28))
    c.restore()
    draw_img(c, text_img('จริง' if ok else 'ไม่จริง', 64, GREEN_D if ok else '#D94848', 0), x + 12, y + 60 * sc, sc, 1, -12)

def card(c, cx, cy, w, h, t, t0, col=WHITE, rot=0, a=1.0):
    s = pop(t, t0, 0.45)
    if s <= 0: return 0
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(RR(8, 12, w, h), 40, 40, P(INK, 60 * a))
    c.drawRoundRect(RR(0, 0, w, h), 40, 40, P(col, 255 * a)); c.drawRoundRect(RR(0, 0, w, h), 40, 40, P(INK, 255 * a, stroke=7))
    c.restore()
    return s

def num_badge(c, n, x, y, t, t0, col=YEL, r=46):
    s = pop(t, t0, 0.4)
    if s <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(4, 6, r, P(INK, 70)); c.drawCircle(0, 0, r, P(col)); c.drawCircle(0, 0, r, P(INK, stroke=7))
    c.restore()
    draw_img(c, text_img(str(n), int(r * 1.2), INK, 0), x, y + 2, s)

def check(c, x, y, s=1.0, col=GREEN_D, a=255):
    p = skia.Path(); p.moveTo(x - 30 * s, y); p.lineTo(x - 8 * s, y + 24 * s); p.lineTo(x + 34 * s, y - 26 * s)
    c.drawPath(p, P(col, a, stroke=14 * s))

def cross(c, x, y, s=1.0, col=CORAL, a=255):
    c.drawLine(x - 28 * s, y - 28 * s, x + 28 * s, y + 28 * s, P(col, a, stroke=14 * s))
    c.drawLine(x + 28 * s, y - 28 * s, x - 28 * s, y + 28 * s, P(col, a, stroke=14 * s))


# ================================================================ ep13 gum props
GUM_RED = '#E8506E'; GUM_REDD = '#C2334F'; PLAQUE = '#F3E39B'; PLAQUE_D = '#D9C05E'; TARTAR = '#E2C76F'; BLOODPINK = '#FF5C7A'

def mix(c0, c1, k):
    a = [int(c0.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]; b = [int(c1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(int(lerp(x, y, clamp(k))) for x, y in zip(a, b))

def gum_closeup(c, x, y, s=1.0, t=0.0, inflam=0.0, plaque=0.0, bleed=0.0, tartar=0.0, mood=None, seed=0, wobble=0.0):
    """one big tooth standing in its gum (front view). origin = gum line centre. inflam 0..1 = pink+firm -> red+puffy,
    plaque 0..1 = yellow film along the gum line, bleed 0..1 = tiny pink droplets (never gory), tartar 0..1 = crust."""
    c.save(); c.translate(x, y); c.scale(s, s)
    rot = math.sin(t * 9) * 4 * wobble
    m = mood or ('happy' if inflam < 0.3 else ('worry' if inflam < 0.7 else 'sad'))
    tooth(c, 0, -120, 1.25, m, rot, t=t, seed=seed, shadow=False)
    # plaque film along the neck of the tooth
    if plaque > 0:
        a = 230 * plaque
        for i in range(7):
            px = -95 + i * 32; py = -30 + 8 * math.sin(i * 1.7)
            c.drawCircle(px, py, 26 + 6 * math.sin(t * 2 + i), P(PLAQUE, a))
        for i in range(3):
            germ(c, -70 + i * 70, -40 + math.sin(t * 4 + i) * 4, 0.16 * plaque, t, seed=i + seed, col=('#9BE15D', '#B58CFF', '#FFB347')[i], mood='happy')
    if tartar > 0:
        for i in range(6):
            c.drawCircle(-90 + i * 36, -12 + (i % 2) * 8, 22 * tartar, P(TARTAR)); c.drawCircle(-90 + i * 36, -12 + (i % 2) * 8, 22 * tartar, P(INK, 180, stroke=4))
    # gum: scalloped band, puffs up when inflamed
    sw = 26 * inflam
    col0, col1 = mix(GUM, GUM_RED, inflam), mix(GUMD, GUM_REDD, inflam)
    g = skia.Path(); g.moveTo(-330, 260); g.lineTo(-330, 0)
    g.cubicTo(-250, -10 - sw, -170, -40 - sw, -120, 10)
    g.cubicTo(-80, -40 - sw * 1.6, 80, -40 - sw * 1.6, 120, 10)
    g.cubicTo(170, -40 - sw, 250, -10 - sw, 330, 0)
    g.lineTo(330, 260); g.close()
    fillp(c, g, lingrad((0, -40), (0, 260), col0, col1))
    if inflam > 0.4:
        for i, dx in enumerate((-60, 0, 60)):
            c.drawLine(dx - 14, 40 + i % 2 * 10, dx + 14, 40 + i % 2 * 10, P(GUM_REDD, 160 * inflam, stroke=5))
    if bleed > 0:
        for i, dx in enumerate((-70, -10, 55)):
            k = clamp(bleed * 1.5 - i * 0.25)
            if k > 0:
                c.drawCircle(dx, -18 + 6 * i, 9 * k, P(BLOODPINK)); c.drawCircle(dx, -18 + 6 * i, 9 * k, P(INK, stroke=3))
    c.restore()

def foam(c, x, y, s=1.0, t=0.0, pink=0.0, a=255):
    """toothpaste foam blob in the sink; pink 0..1 tints it pink (a hint of blood, never gory)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    col = mix('#FFFFFF', '#FFC2CF', pink)
    blobs(c, [(-50, 0, 34), (0, -14, 42), (48, 2, 32), (10, 20, 30)], col, a)
    for i in range(5):
        c.drawCircle(-40 + i * 22, -10 + (i % 2) * 18, 7, P(BLOODPINK, a * 0.8 * pink))
    c.restore()

def wall_mirror(c, x, y, w=420, h=340):
    c.drawRoundRect(RR(x + 8, y + 10, w, h), 60, 60, P(INK, 60))
    c.drawRoundRect(RR(x, y, w, h), 60, 60, P('#DDF6FF')); c.drawRoundRect(RR(x, y, w, h), 60, 60, P(INK, stroke=8))
    p = skia.Path(); p.moveTo(x - w / 2 + 70, y - h / 2 + 120); p.lineTo(x - w / 2 + 150, y - h / 2 + 40)
    c.drawPath(p, P(WHITE, 220, stroke=16))

def bathroom(c, t):
    background(c, t, '#D8F3EE', '#F0FFFB', dots=False)
    for i in range(12):   # tiles
        c.drawLine(i * 170, 0, i * 170, 860, P(WHITE, 120, stroke=4))
    for j in range(6): c.drawLine(0, j * 170, W, j * 170, P(WHITE, 120, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), P('#BFE3DD')); c.drawLine(0, 860, W, 860, P(INK, stroke=7))

def alarm_bell(c, x, y, s=1.0, t=0.0, ring=1.0):
    c.save(); c.translate(x, y); c.rotate(math.sin(t * 22) * 14 * ring); c.scale(s, s)
    b = skia.Path(); b.moveTo(-90, 60); b.cubicTo(-90, -120, 90, -120, 90, 60); b.lineTo(110, 80); b.lineTo(-110, 80); b.close()
    fillp(c, b, lingrad((0, -100), (0, 80), YEL, '#F5B83D'))
    c.drawCircle(0, 100, 24, P(CORAL)); c.drawCircle(0, 100, 24, P(INK, stroke=6))
    c.drawCircle(0, -100, 16, P(YEL)); c.drawCircle(0, -100, 16, P(INK, stroke=6))
    c.restore()
    if ring > 0:
        for sx in (-1, 1):
            for k in range(2):
                r = 150 + k * 40
                p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r * s, y - r * s, x + r * s, y + r * s), (-40 if sx > 0 else 180 + 0) + (0), 60 if sx > 0 else 60)
                c.drawPath(p, P(INK, 200 * ring * (0.5 + 0.5 * math.sin(t * 10 + k)), stroke=7))

def ninja_band(c, x, y, s=1.0, t=0.0):
    """dark mask band drawn over a germ's eyes (call right after germ())"""
    c.save(); c.translate(x, y + math.sin(t * 6) * 8); c.scale(s, s)
    c.drawRoundRect(RR(0, -6, 150, 40), 18, 18, P(INK, 230))
    for sx in (-1, 1):
        c.drawOval(RR(sx * 26, -6, 26, 14), P(WHITE))
        c.drawCircle(sx * 26 + 4, -6, 5, P(INK))
    tail = skia.Path(); tail.moveTo(70, -10); tail.quadTo(110, -30 + math.sin(t * 8) * 10, 130, -4 + math.sin(t * 8) * 10)
    c.drawPath(tail, P(INK, 230, stroke=12))
    c.restore()

def soft_brush(c, x, y, rot=0, s=1.0, hard=False):
    """toothbrush with soft (wavy, light) or hard (straight, dark) bristles"""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    col = '#7F95B5' if hard else TEAL
    c.drawRoundRect(skia.Rect.MakeLTRB(-20, -10, 360, 26), 18, 18, P(col)); c.drawRoundRect(skia.Rect.MakeLTRB(-20, -10, 360, 26), 18, 18, P(INK, stroke=6))
    c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 10, 32), 14, 14, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 10, 32), 14, 14, P(INK, stroke=6))
    for i in range(6):
        bx = -100 + i * 19
        if hard:
            c.drawRoundRect(skia.Rect.MakeLTRB(bx, -70, bx + 14, -14), 3, 3, P('#9AA9C2')); c.drawRoundRect(skia.Rect.MakeLTRB(bx, -70, bx + 14, -14), 3, 3, P(INK, stroke=4))
        else:
            p = skia.Path(); p.moveTo(bx + 7, -14); p.cubicTo(bx - 4, -35, bx + 18, -50, bx + 7, -74)
            c.drawPath(p, P(INK, stroke=14)); c.drawPath(p, P(MINT if i % 2 else WHITE, stroke=8))
    c.restore()

def scaler(c, x, y, s=1.0, rot=0):
    """dentist's scaling instrument (simple, friendly)"""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-22, 0, 22, 260), 20, 20, P(TI1)); c.drawRoundRect(skia.Rect.MakeLTRB(-22, 0, 22, 260), 20, 20, P(INK, stroke=6))
    for k in range(5): c.drawLine(-18, 60 + k * 30, 18, 60 + k * 30, P(TI2, stroke=4))
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(0, -80); p.quadTo(0, -120, 30, -120)
    c.drawPath(p, P(INK, stroke=14)); c.drawPath(p, P(TI1, stroke=7))
    c.restore()

def cycle(c, cx, cy, r, t, t0, labels, cols):
    """three labels on a ring connected by rotating arrows (a vicious circle)"""
    k = ease_out(seg(t, t0, t0 + 0.8))
    if k <= 0: return
    c.save(); c.translate(cx, cy)
    for i in range(3):
        a0 = -90 + i * 120 + 22
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-r, -r, r, r), a0, 76 * k)
        c.drawPath(p, P(INK, stroke=22)); c.drawPath(p, P(CORAL, stroke=12))
        ae = math.radians(a0 + 76 * k)
        ax, ay = math.cos(ae) * r, math.sin(ae) * r
        c.save(); c.translate(ax, ay); c.rotate(math.degrees(ae) + 90)
        h = skia.Path(); h.moveTo(-26, -20); h.lineTo(14, 0); h.lineTo(-26, 20); h.close(); fillp(c, h, CORAL, stroke=5)
        c.restore()
    c.restore()
    for i, (txt, col) in enumerate(zip(labels, cols)):
        a = math.radians(-90 + i * 120)
        label(c, txt, cx + math.cos(a) * r, cy + math.sin(a) * r, t, t0 + 0.3 + i * 0.5, 54, col, INK if col != CORAL else WHITE, padx=32, pady=20)

def protractor(c, x, y, ang, k=1.0):
    """45-degree angle marker between a vertical tooth axis and the brush"""
    if k <= 0: return
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - 110, y - 110, x + 110, y + 110), -90, -ang * k)
    c.drawPath(p, P(YEL, stroke=16)); c.drawPath(p, P(INK, stroke=4))
    c.drawLine(x, y, x, y - 150, P(INK, 160, stroke=5))

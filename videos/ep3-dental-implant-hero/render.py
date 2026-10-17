import skia, numpy as np, math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_B = os.path.join(ROOT, 'fonts/mitr-700.ttf')
FONT_M = os.path.join(ROOT, 'fonts/mitr-600.ttf')
FONT_R = os.path.join(ROOT, 'fonts/mitr-500.ttf')

# ---------------------------------------------------------------- palette
def C(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

INK = '#23395B'; TEAL = '#2EC4B6'; MINT = '#CBF3F0'; PINK = '#FF8FAB'
GUM = '#F7A1B5'; GUMD = '#E26D8C'; BONE = '#FBE7C6'; BONED = '#E9C48F'
YEL = '#FFD166'; CORAL = '#FF6B6B'; WHITE = '#FFFFFF'; SHADE = '#D7ECF4'
TI1 = '#C9D6E8'; TI2 = '#7F95B5'; TI3 = '#5A6F92'; SKY = '#7BDFF2'; LAV = '#B8B8FF'

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b != a else (1.0 if t >= a else 0.0)
def lerp(a, b, x): return a + (b - a) * x
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in(x): return x ** 3
def ease_io(x): return 3 * x * x - 2 * x * x * x
def back(x, s=1.9):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def elastic(x):
    if x <= 0: return 0
    if x >= 1: return 1
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1
def pop(t, t0, dur=0.45):
    return back(seg(t, t0, t0 + dur)) if t >= t0 else 0.0

# ---------------------------------------------------------------- paints
def P(color, a=None, stroke=None, blur=None, cap=True):
    p = skia.Paint(AntiAlias=True)
    p.setColor(C(color, 255 if a is None else int(a)) if isinstance(color, str) else color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

def lingrad(p0, p1, c0, c1):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [C(c0), C(c1)]))
    return p

def RR(cx, cy, w, h): return skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)

# ---------------------------------------------------------------- text
_tcache = {}
def text_img(txt, size, fill=WHITE, stroke=0, stroke_fill=INK, font=FONT_B, spacing=10):
    key = (txt, size, fill, stroke, stroke_fill, font)
    if key in _tcache: return _tcache[key]
    f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
    pad = int(size * 0.8) + stroke * 2
    tmp = Image.new('RGBA', (10, 10)); d = ImageDraw.Draw(tmp)
    bb = d.multiline_textbbox((0, 0), txt, font=f, stroke_width=stroke, align='center', spacing=spacing)
    w, h = int(math.ceil(bb[2] - bb[0])) + pad * 2, int(math.ceil(bb[3] - bb[1])) + pad * 2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.multiline_text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=stroke,
                     stroke_fill=stroke_fill, align='center', spacing=spacing)
    box = im.getbbox() or (0, 0, 1, 1)
    im = im.crop(box)
    arr = np.ascontiguousarray(np.array(im))
    img = skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType,
                               alphaType=skia.AlphaType.kUnpremul_AlphaType)
    _tcache[key] = img
    return img

SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
def draw_img(c, img, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.001 or alpha <= 0.001: return
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(scale, scale)
    w, h = img.width(), img.height()
    c.drawImageRect(img, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), SAMP, skia.Paint(Alphaf=alpha, AntiAlias=True))
    c.restore()

def label(c, txt, cx, cy, t, t0, size=62, bg=TEAL, fg=WHITE, padx=44, pady=26, rot=0, font=FONT_B, alpha=1.0):
    """pill label that pops in"""
    s = pop(t, t0)
    if s <= 0: return
    img = text_img(txt, size, fg, 0, INK, font)
    w, h = img.width() + padx * 2, img.height() + pady * 2
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    r = min(h / 2, 46)
    c.drawRoundRect(RR(8, 12, w, h), r, r, P(INK, 70 * alpha))
    c.drawRoundRect(RR(0, 0, w, h), r, r, P(bg, 255 * alpha))
    c.drawRoundRect(RR(0, 0, w, h), r, r, P(INK, 255 * alpha, stroke=7))
    c.restore()
    draw_img(c, img, cx, cy + 2, s, alpha, rot)

def big_title(c, txt, cx, cy, t, t0, size=92, fill=WHITE, stroke=12, rot=0, shake=0):
    s = pop(t, t0, 0.5)
    if s <= 0: return
    img = text_img(txt, size, fill, stroke, INK)
    dx = math.sin(t * 60) * shake * (1 - seg(t, t0, t0 + 0.6)) if shake else 0
    draw_img(c, img, cx + dx + 6, cy + 10, s, 0.0, rot)
    draw_img(c, img, cx + dx, cy, s, 1.0, rot)

def step_badge(c, n, cx, cy, t, t0):
    s = pop(t, t0)
    if s <= 0: return
    c.save(); c.translate(cx, cy); c.scale(s, s); c.rotate(-6)
    c.drawRoundRect(RR(6, 8, 250, 92), 46, 46, P(INK, 80))
    c.drawRoundRect(RR(0, 0, 250, 92), 46, 46, P(YEL))
    c.drawRoundRect(RR(0, 0, 250, 92), 46, 46, P(INK, stroke=7))
    c.restore()
    draw_img(c, text_img(f'ขั้นที่ {n}', 58, INK, 0), cx, cy + 2, s, 1, -6)

# ---------------------------------------------------------------- background
_bokeh = [(random.Random(i).uniform(0, W), random.Random(i * 7).uniform(0, H),
           random.Random(i * 13).uniform(30, 120), random.Random(i * 17).uniform(0.2, 0.7)) for i in range(16)]
def background(c, t, top, bot, dots=True):
    c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), top, bot))
    if dots:
        for (x, y, r, sp) in _bokeh:
            yy = (y - t * 40 * sp) % (H + 300) - 150
            xx = x + math.sin(t * sp + y) * 30
            c.drawCircle(xx, yy, r, P(WHITE, 38))
    # subtle polka sparkle
    for i in range(10):
        rr = random.Random(100 + i)
        x, y = rr.uniform(60, W - 60), rr.uniform(200, 1500)
        tw = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        sparkle(c, x, y, 10 + 10 * tw, WHITE, 140 * tw)

def sparkle(c, x, y, r, col=WHITE, a=255):
    if r <= 0 or a <= 1: return
    p = skia.Path()
    p.moveTo(x, y - r); p.quadTo(x, y, x + r, y); p.quadTo(x, y, x, y + r)
    p.quadTo(x, y, x - r, y); p.quadTo(x, y, x, y - r); p.close()
    c.drawPath(p, P(col, a))

def burst(c, cx, cy, t, n=16, r0=180, r1=900, col=YEL, a=120, speed=12):
    c.save(); c.translate(cx, cy); c.rotate(t * speed)
    for i in range(n):
        ang = 2 * math.pi * i / n; da = math.pi / n * 0.55
        p = skia.Path(); p.moveTo(math.cos(ang - da) * r0, math.sin(ang - da) * r0)
        p.lineTo(math.cos(ang - da) * r1, math.sin(ang - da) * r1)
        p.lineTo(math.cos(ang + da) * r1, math.sin(ang + da) * r1)
        p.lineTo(math.cos(ang + da) * r0, math.sin(ang + da) * r0); p.close()
        c.drawPath(p, P(col, a))
    c.restore()

def puff(c, x, y, prog, n=7, spread=170, col=WHITE):
    if prog <= 0 or prog >= 1: return
    for i in range(n):
        ang = math.pi + math.pi * i / (n - 1)
        d = spread * ease_out(prog)
        r = 34 * (1 - prog) + 10
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * 0.35, r, P(col, 230 * (1 - prog)))
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * 0.35, r, P(INK, 120 * (1 - prog), stroke=4))

def heart(c, x, y, s, col=CORAL, a=255):
    p = skia.Path()
    p.moveTo(x, y + 0.9 * s)
    p.cubicTo(x - 1.3 * s, y - 0.1 * s, x - 0.6 * s, y - 1.0 * s, x, y - 0.35 * s)
    p.cubicTo(x + 0.6 * s, y - 1.0 * s, x + 1.3 * s, y - 0.1 * s, x, y + 0.9 * s); p.close()
    c.drawPath(p, P(col, a)); c.drawPath(p, P(INK, a, stroke=4))

def sweat(c, x, y, s=1, a=255):
    p = skia.Path(); p.moveTo(x, y - 26 * s)
    p.cubicTo(x + 18 * s, y - 2 * s, x + 16 * s, y + 18 * s, x, y + 18 * s)
    p.cubicTo(x - 16 * s, y + 18 * s, x - 18 * s, y - 2 * s, x, y - 26 * s); p.close()
    c.drawPath(p, P(SKY, a)); c.drawPath(p, P(INK, a, stroke=4))

def motion_lines(c, x, y, h, a=255):
    for i, dx in enumerate((-60, 0, 60)):
        c.drawLine(x + dx, y - h - i * 30, x + dx, y - 40 - i * 20, P(INK, a * 0.6, stroke=8))

CONF_COLS = [CORAL, YEL, TEAL, PINK, LAV, SKY]
_conf = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(-600, 0), random.Random(i + 7).uniform(150, 380),
          random.Random(i + 3).uniform(0, 360), random.Random(i + 5).choice(CONF_COLS)) for i in range(70)]
def confetti(c, t):
    for (x, y0, v, r0, col) in _conf:
        y = y0 + t * v
        if y > H + 40: continue
        xx = x + math.sin(t * 2 + r0) * 40
        c.save(); c.translate(xx, y); c.rotate(r0 + t * 200)
        c.drawRect(skia.Rect.MakeXYWH(-12, -7, 24, 14), P(col))
        c.restore()

# ---------------------------------------------------------------- tooth character
def tooth_path():
    p = skia.Path()
    p.moveTo(-95, -60)
    p.cubicTo(-100, -125, -40, -140, 0, -112)
    p.cubicTo(40, -140, 100, -125, 95, -60)
    p.cubicTo(92, -10, 80, 30, 70, 70)
    p.cubicTo(62, 110, 56, 150, 40, 150)
    p.cubicTo(22, 150, 18, 110, 12, 82)
    p.cubicTo(8, 64, -8, 64, -12, 82)
    p.cubicTo(-18, 110, -22, 150, -40, 150)
    p.cubicTo(-56, 150, -62, 110, -70, 70)
    p.cubicTo(-80, 30, -92, -10, -95, -60)
    p.close()
    return p
TOOTH = tooth_path()

def face(c, x, y, mood='smile', blink=1.0, look=0.0, s=1.0, eye_dx=32, cheeks=True):
    """face centred at x,y in current coords"""
    ink = P(INK)
    for sx in (-1, 1):
        ex, ey = x + sx * eye_dx * s, y
        if mood in ('happy', 'joy'):
            # ^ ^ eyes
            p = skia.Path(); p.moveTo(ex - 13 * s, ey + 6 * s); p.quadTo(ex, ey - 16 * s, ex + 13 * s, ey + 6 * s)
            c.drawPath(p, P(INK, stroke=7 * s))
        elif mood == 'squeeze':
            p = skia.Path(); p.moveTo(ex + sx * 12 * s, ey - 11 * s); p.lineTo(ex - sx * 12 * s, ey); p.lineTo(ex + sx * 12 * s, ey + 11 * s)
            c.drawPath(p, P(INK, stroke=7 * s))
        elif mood == 'sleep':
            p = skia.Path(); p.moveTo(ex - 13 * s, ey - 2 * s); p.quadTo(ex, ey + 12 * s, ex + 13 * s, ey - 2 * s)
            c.drawPath(p, P(INK, stroke=6 * s))
        else:
            ry = 17 * s * max(0.12, blink) * (1.25 if mood == 'shock' else 1)
            rx = 13 * s * (1.15 if mood == 'shock' else 1)
            c.drawOval(RR(ex + look * 5 * s, ey, rx * 2, ry * 2), ink)
            if blink > 0.4:
                c.drawCircle(ex + look * 5 * s + 4 * s, ey - 6 * s, 5 * s, P(WHITE))
            if mood in ('sad', 'worry'):
                p = skia.Path(); p.moveTo(ex - 14 * s, ey - (24 if sx < 0 else 32) * s); p.lineTo(ex + 14 * s, ey - (32 if sx < 0 else 24) * s)
                c.drawPath(p, P(INK, stroke=5 * s))
            if mood == 'hero':
                p = skia.Path(); p.moveTo(ex - 15 * s, ey - (32 if sx < 0 else 24) * s); p.lineTo(ex + 15 * s, ey - (24 if sx < 0 else 32) * s)
                c.drawPath(p, P(INK, stroke=6 * s))
    if cheeks:
        for sx in (-1, 1):
            c.drawOval(RR(x + sx * (eye_dx + 22) * s, y + 20 * s, 30 * s, 16 * s), P(PINK, 170))
    my = y + 24 * s
    if mood in ('smile', 'hero', 'happy', 'sleep'):
        p = skia.Path(); p.moveTo(x - 14 * s, my); p.quadTo(x, my + 14 * s, x + 14 * s, my)
        c.drawPath(p, P(INK, stroke=6 * s))
    elif mood == 'joy':
        p = skia.Path(); p.moveTo(x - 20 * s, my - 4 * s); p.quadTo(x, my + 34 * s, x + 20 * s, my - 4 * s); p.close()
        c.drawPath(p, ink)
        c.drawOval(RR(x, my + 9 * s, 16 * s, 9 * s), P(CORAL))
    elif mood in ('shock', 'squeeze'):
        c.drawOval(RR(x, my + 6 * s, 22 * s, 28 * s), ink)
        c.drawOval(RR(x, my + 12 * s, 12 * s, 8 * s), P(CORAL))
    elif mood in ('sad', 'worry'):
        p = skia.Path(); p.moveTo(x - 14 * s, my + 10 * s); p.quadTo(x, my - 4 * s, x + 14 * s, my + 10 * s)
        c.drawPath(p, P(INK, stroke=6 * s))

def blink_at(t, seed=0):
    ph = (t + seed * 1.37) % 3.3
    return 0.1 if ph < 0.12 else 1.0

def tooth(c, x, y, s=1.0, mood='smile', rot=0, sq=1.0, flip=False, t=0, seed=0, look=0, shadow=True, alpha=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s / sq ** 0.5, s * sq)
    if flip: c.scale(1, -1)
    if shadow and not flip:
        c.drawOval(RR(0, 165, 170, 26), P(INK, 40 * alpha))
    grad = lingrad((0, -140), (0, 150), WHITE, SHADE)
    grad.setAlphaf(alpha)
    c.drawPath(TOOTH, grad)
    c.drawPath(TOOTH, P(INK, 255 * alpha, stroke=7))
    hp = skia.Path(); hp.moveTo(-66, -70); hp.cubicTo(-70, -100, -50, -112, -30, -108)
    c.drawPath(hp, P(WHITE, 255 * alpha, stroke=10))
    if flip: c.scale(1, -1)
    face(c, 0, (30 if flip else -30), mood, blink_at(t, seed), look)
    c.restore()

def crown(c, x, y, s=1.0, mood='smile', t=0, seed=0, face_on=True, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.save(); c.clipRect(skia.Rect.MakeLTRB(-130, -160, 130, 38))
    c.drawPath(TOOTH, lingrad((0, -140), (0, 40), WHITE, SHADE))
    c.drawPath(TOOTH, P(INK, stroke=7))
    c.restore()
    c.drawLine(-83, 38, 83, 38, P(INK, stroke=7))
    hp = skia.Path(); hp.moveTo(-66, -70); hp.cubicTo(-70, -100, -50, -112, -30, -108)
    c.drawPath(hp, P(WHITE, stroke=10))
    if face_on: face(c, 0, -40, mood, blink_at(t, seed))
    c.restore()

# ---------------------------------------------------------------- implant hero
def screw_body_path():
    p = skia.Path()
    p.moveTo(-75, 36); p.lineTo(75, 36)
    p.cubicTo(72, 120, 55, 230, 42, 286)
    p.cubicTo(30, 318, -30, 318, -42, 286)
    p.cubicTo(-55, 230, -72, 120, -75, 36); p.close()
    return p
SCREW = screw_body_path()

def implant(c, x, y, s=1.0, mood='hero', t=0, phase=0.0, cape=0.0, rot=0, star=True, sq=1.0, alpha=1.0):
    """origin = top of platform centre"""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s / sq ** 0.5, s * sq)
    if cape > 0:
        cp = skia.Path()
        cp.moveTo(-62, 40)
        w1 = math.sin(t * 7) * 18; w2 = math.sin(t * 7 + 1.5) * 18
        cp.cubicTo(-110, 120, -150 + w1, 230, -135 + w1, 300)
        cp.quadTo(-70, 285 + w2, -20, 305 + w1)
        cp.quadTo(40, 285 + w2, 135 + w2, 300)
        cp.cubicTo(150 + w2, 230, 110, 120, 62, 40); cp.close()
        c.save(); c.scale(cape, 1)
        c.drawPath(cp, lingrad((0, 40), (0, 300), CORAL, '#D94848'))
        c.drawPath(cp, P(INK, stroke=7))
        c.restore()
    # body
    c.drawPath(SCREW, lingrad((-75, 0), (75, 0), TI2, TI1))
    c.save(); c.clipPath(SCREW, doAntiAlias=True)
    # highlight stripe
    c.drawRect(skia.Rect.MakeLTRB(18, 36, 40, 320), P(WHITE, 90))
    # threads (lower part)
    for i in range(-1, 8):
        yy = 150 + i * 28 + (phase % 1.0) * 28
        if yy < 140: continue
        c.drawLine(-90, yy, 90, yy + 16, P(TI3, stroke=9))
        c.drawLine(-90, yy + 7, 90, yy + 23, P(WHITE, 110, stroke=4))
    c.restore()
    # thread teeth on the silhouette
    for i in range(-1, 8):
        yy = 150 + i * 28 + (phase % 1.0) * 28
        if yy < 145 or yy > 285: continue
        k = (yy - 36) / 250.0
        hw = 75 - k * 34
        for sx in (-1, 1):
            tp = skia.Path(); tp.moveTo(sx * (hw - 6), yy - 9); tp.lineTo(sx * (hw + 12), yy + (4 if sx < 0 else 12)); tp.lineTo(sx * (hw - 6), yy + 19); tp.close()
            c.drawPath(tp, P(TI2)); c.drawPath(tp, P(INK, stroke=5))
    c.drawPath(SCREW, P(INK, stroke=7))
    # platform
    c.drawRoundRect(skia.Rect.MakeLTRB(-82, 0, 82, 40), 14, 14, lingrad((-82, 0), (82, 0), TI1, '#EEF3FA'))
    c.drawRoundRect(skia.Rect.MakeLTRB(-82, 0, 82, 40), 14, 14, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-30, 8, 30, 22), 6, 6, P(TI3))
    face(c, 0, 92, mood, blink_at(t, 2), 0, 0.95, eye_dx=30)
    if star:
        sparkle(c, 46, 140, 16, YEL)
    c.restore()

def abutment(c, x, y, s=1.0, rot=0):
    """origin = bottom centre (sits on implant platform)"""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.moveTo(-50, 0); p.lineTo(-40, -95); p.quadTo(0, -112, 40, -95); p.lineTo(50, 0); p.close()
    c.drawPath(p, lingrad((-50, 0), (50, 0), TI2, '#E9EFF7')); c.drawPath(p, P(INK, stroke=7))
    c.drawLine(-44, -45, 44, -45, P(TI3, stroke=5))
    c.restore()

# ---------------------------------------------------------------- jaw pieces
def bone_gum(c, top=1200, dip=0.0, gapx=540, gapw=376, sad=0.0, t=0, buddies=False):
    def edge(off):
        p = skia.Path(); p.moveTo(-20, H + 20); p.lineTo(-20, top + off)
        x0, x1 = gapx - gapw / 2 - 60, gapx + gapw / 2 + 60
        p.lineTo(x0, top + off)
        p.cubicTo(x0 + 90, top + off, gapx - 120, top + off + dip, gapx, top + off + dip)
        p.cubicTo(gapx + 120, top + off + dip, x1 - 90, top + off, x1, top + off)
        p.lineTo(W + 20, top + off); p.lineTo(W + 20, H + 20); p.close()
        return p
    bone = edge(0)
    c.drawPath(bone, lingrad((0, top), (0, H), BONE, BONED))
    c.save(); c.clipPath(bone, doAntiAlias=True)
    rr = random.Random(5)
    for i in range(70):
        bx, by = rr.uniform(0, W), rr.uniform(top + 30, H)
        c.drawOval(RR(bx, by, rr.uniform(16, 44), rr.uniform(12, 30)), P(BONED, 150))
    c.restore()
    c.drawPath(bone, P(INK, stroke=7))
    gum = edge(-95)
    c.save(); c.clipPath(bone, skia.ClipOp.kDifference, True)
    c.drawPath(gum, lingrad((0, top - 95), (0, top), GUM, GUMD)); c.drawPath(gum, P(INK, stroke=7))
    c.restore()
    if sad > 0:
        face(c, gapx, top + dip + 140, 'sad', blink_at(t, 4), 0, 1.3 * sad)

def gum_row(c, y, flip=False):
    """horizontal gum band for front-view rows; y = gum line"""
    p = skia.Path()
    if not flip:
        p.moveTo(-20, H); p.lineTo(-20, y)
        for i in range(7):
            x0 = -20 + i * 180
            p.quadTo(x0 + 90, y - 40, x0 + 180, y)
        p.lineTo(W + 20, H); p.close()
        c.drawPath(p, lingrad((0, y), (0, H), GUM, GUMD))
    else:
        p.moveTo(-20, 0); p.lineTo(-20, y)
        for i in range(7):
            x0 = -20 + i * 180
            p.quadTo(x0 + 90, y + 40, x0 + 180, y)
        p.lineTo(W + 20, 0); p.close()
        c.drawPath(p, lingrad((0, 0), (0, y), GUMD, GUM))
    c.drawPath(p, P(INK, stroke=7))

# ---------------------------------------------------------------- props
def calendar(c, x, y, t, months):
    c.save(); c.translate(x, y); c.rotate(5)
    c.drawRoundRect(RR(8, 10, 230, 250), 26, 26, P(INK, 70))
    c.drawRoundRect(RR(0, 0, 230, 250), 26, 26, P(WHITE))
    c.drawRoundRect(skia.Rect.MakeLTRB(-115, -125, 115, -55), 26, 26, P(CORAL))
    c.drawRect(skia.Rect.MakeLTRB(-115, -80, 115, -55), P(CORAL))
    c.drawRoundRect(RR(0, 0, 230, 250), 26, 26, P(INK, stroke=7))
    for sx in (-55, 55):
        c.drawRoundRect(RR(sx, -128, 18, 46), 9, 9, P(INK))
    c.restore()
    n = int(months); fr = months - n
    draw_img(c, text_img('เดือน', 40, WHITE, 0), x - 4, y - 88, 1, 1, 5)
    num = text_img(str(max(1, n)), 120, INK, 0)
    flip = 1 - ease_out(clamp(fr * 3)) if fr > 0 else 0
    draw_img(c, num, x + 6, y + 30, 1.0 - 0.15 * flip, 1, 5)

def toothbrush(c, x, y, rot=0, s=1):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-20, -10, 360, 26), 18, 18, P(TEAL)); c.drawRoundRect(skia.Rect.MakeLTRB(-20, -10, 360, 26), 18, 18, P(INK, stroke=6))
    c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 10, 32), 14, 14, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(-110, -16, 10, 32), 14, 14, P(INK, stroke=6))
    for i in range(6):
        bx = -100 + i * 19
        c.drawRoundRect(skia.Rect.MakeLTRB(bx, -70, bx + 14, -14), 6, 6, P(SKY if i % 2 else WHITE))
        c.drawRoundRect(skia.Rect.MakeLTRB(bx, -70, bx + 14, -14), 6, 6, P(INK, stroke=4))
    c.restore()

def bubbles(c, x, y, t, n=10):
    for i in range(n):
        rr = random.Random(i * 31)
        ph = (t * rr.uniform(0.6, 1.2) + rr.random()) % 1.0
        bx = x + rr.uniform(-150, 150) + math.sin(t * 3 + i) * 12
        by = y - ph * 260
        r = rr.uniform(10, 26) * (0.5 + ph)
        c.drawCircle(bx, by, r, P(WHITE, 200 * (1 - ph)))
        c.drawCircle(bx, by, r, P(SKY, 220 * (1 - ph), stroke=4))

def bone_buddy(c, x, y, s, t, seed, mood='happy'):
    c.save(); c.translate(x, y); c.scale(s, s)
    wob = math.sin(t * 9 + seed) * 0.06
    c.scale(1 + wob, 1 - wob)
    p = skia.Path(); p.addOval(RR(0, 0, 90, 76))
    c.drawPath(p, P(BONE)); c.drawPath(p, P(INK, stroke=6))
    face(c, 0, -6, mood, blink_at(t, seed), 0, 0.55, eye_dx=22)
    c.restore()

def hand_text(c, txt, x, y, t, t0, size=48, col=INK, rot=0):
    s = pop(t, t0)
    if s > 0: draw_img(c, text_img(txt, size, col, 6, WHITE), x, y, s, 1, rot)

# ================================================================ scenes
TITLE_Y = 330
SUB_Y = 1530

def subtitle(c, txt, t, t0, t1=99, y=SUB_Y, size=56, bg=WHITE, fg=INK):
    if t < t0 or t > t1: return
    a = 1 - seg(t, t1 - 0.25, t1)
    label(c, txt, W / 2, y, t, t0, size, bg, fg, alpha=a, font=FONT_M)

ROW_X = [140, 340, 540, 740, 940]

def scene1(c, t):
    T0 = t; t = t + 0.75
    background(c, t, '#9BF6FF', MINT)
    gy = 1320
    for i, x in enumerate(ROW_X):
        bob = math.sin(t * 5 + i) * 6
        mood = 'smile'
        if t > 1.35: mood = 'shock'
        look = 0
        if t > 1.35 and i != 2: look = (1 if i < 2 else -1)
        if i == 2:
            if t < 1.2:
                sq = 1 - 0.12 * seg(t, 0.85, 1.2)
                tooth(c, x, gy - 120 + bob, 0.95, 'worry' if t > 0.7 else 'smile', 0, sq, t=t, seed=i)
            else:
                k = t - 1.2
                tooth(c, x + k * 520, gy - 120 - k * 1500 + k * k * 900, 0.95, 'shock', k * 520, t=t, seed=i, shadow=False)
            continue
        jump = 0
        if 1.3 < t < 1.75: jump = -math.sin(seg(t, 1.3, 1.75) * math.pi) * 60
        tooth(c, x, gy - 120 + bob + jump, 0.95, mood, 0, t=t, seed=i, look=look)
        if t > 1.5:
            sweat(c, x + 80, gy - 230, 0.9, 255 * seg(t, 1.5, 1.7))
    gum_row(c, gy)
    if 1.15 < t < 1.8:
        k = seg(t, 1.15, 1.8)
        burst(c, 540, gy - 140, t, 12, 60, 60 + 260 * ease_out(k), YEL, 200 * (1 - k))
        hand_text(c, 'ป๊อก!', 640, 880, t, 1.2, 90, CORAL, 10)
    elif t >= 1.8 and t < 2.6:
        hand_text(c, 'ป๊อก!', 640, 880, t, 1.2, 90, CORAL, 10)
    big_title(c, 'ฟันหายไป 1 ซี่', W / 2, TITLE_Y, T0, 1.1, 104)
    big_title(c, 'ไม่ใช่เรื่องเล็กนะ!', W / 2, TITLE_Y + 150, T0, 2.7, 96, YEL, shake=18, rot=-3)
    subtitle(c, 'แล้วจะเกิดอะไรขึ้นต่อ...?', T0, 4.5)

def scene2(c, t):
    T0 = t; t = t - 1.0
    background(c, t, '#FFD6E0', '#FFF1E6')
    gy = 1360; uy = 640
    gum_row(c, uy, flip=True)
    # upper teeth (upside down)
    drop = ease_io(seg(t, 4.0, 6.4)) * 120
    for i, x in enumerate(ROW_X):
        d = drop if i == 2 else 0
        mood = 'sleep' if (i == 2 and t > 4.2) else 'smile'
        tooth(c, x, uy + 120 + d + math.sin(t * 4 + i) * 4, 0.85, mood, 0, flip=True, t=t, seed=i + 10, shadow=False)
    if t > 4.6:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            draw_img(c, text_img('z', 40 + 14 * k, LAV, 5, INK), ROW_X[2] + 110 + ph * 40, uy + 180 - ph * 70 + drop, 1, 1 - ph)
    # lower teeth with gap; neighbours tilt
    tilt = ease_io(seg(t, 1.0, 3.6)) * 22
    for i, x in enumerate(ROW_X):
        if i == 2: continue
        rot = 0; mood = 'smile'; dx = 0
        if i == 1: rot = tilt; mood = 'worry' if t > 1.2 else 'smile'; dx = tilt * 2.4
        if i == 3: rot = -tilt; mood = 'worry' if t > 1.2 else 'smile'; dx = -tilt * 2.4
        wob = math.sin(t * 14) * 2 * seg(t, 1.0, 3.6) * (1 - seg(t, 3.5, 3.8))
        c.save(); c.translate(x + dx, gy); c.rotate(rot + wob); c.translate(-(x + dx), -gy)
        tooth(c, x + dx, gy - 120 + math.sin(t * 5 + i) * 4, 0.85, mood, 0, t=t, seed=i, shadow=False)
        c.restore()
    gum_row(c, gy)
    if t > 1.4:
        hand_text(c, 'เอ๊ะ!', ROW_X[1] - 10, gy - 330, t, 1.4, 54, CORAL, -10)
        hand_text(c, 'เอ๊ะ!', ROW_X[3] + 10, gy - 330, t, 1.5, 54, CORAL, 10)
    big_title(c, 'ปล่อยช่องว่างไว้นานๆ', W / 2, TITLE_Y - 20, T0, 0.3, 92)
    subtitle(c, '1. ฟันข้างๆ ล้มเอียงเข้าหาช่อง', t, 1.0, 3.9)
    subtitle(c, '2. ฟันคู่สบด้านบน ยื่นลงมา', t, 4.0)

def cut_neighbors(c, t, moods=('smile', 'smile'), top=1200, s=1.6):
    for j, x in enumerate((200, 880)):
        tooth(c, x, top - 115 + math.sin(t * 4 + j) * 3, s, moods[j], 0, t=t, seed=j + 20, shadow=False)

def scene3(c, t):
    background(c, t, '#E2ECFF', '#F4F0FF')
    dip = ease_io(seg(t, 1.5, 4.5)) * 120
    bone_gum(c, 1200, dip, sad=seg(t, 0.8, 1.3), t=t)
    cut_neighbors(c, t, ('worry', 'worry') if t > 2 else ('smile', 'smile'))
    if 1.0 < t < 4.6:
        a = 255 * min(seg(t, 1.0, 1.3), 1 - seg(t, 4.2, 4.6))
        for k, dx in enumerate((-70, 0, 70)):
            yy = 1250 + ((t * 120 + k * 40) % 120)
            p = skia.Path(); p.moveTo(540 + dx - 22, yy); p.lineTo(540 + dx, yy + 30); p.lineTo(540 + dx + 22, yy)
            c.drawPath(p, P(CORAL, a, stroke=10))
    big_title(c, 'กระดูกตรงนั้น', W / 2, TITLE_Y - 30, t, 0.3, 96)
    big_title(c, 'ก็ค่อยๆ ยุบ', W / 2, TITLE_Y + 100, t, 1.7, 96, YEL)
    if t > 2.0:
        hand_text(c, 'ยุบ...', 790, 1470, t, 2.0, 64, CORAL, 8)
    subtitle(c, 'เพราะไม่มีรากฟันช่วยรับแรงเคี้ยว', t, 3.3, y=1720, size=50)

def scene4(c, t):
    background(c, t, '#FFF3B0', '#FFD6A5')
    land = 1.2
    if t > land:
        burst(c, 540, 1050, t, 18, 120, 1300 * ease_out(seg(t, land, land + 0.5)), WHITE, 110)
    gy = 1500
    c.drawOval(RR(540, gy + 10, 420 * (seg(t, 0.5, land)), 50), P(INK, 50))
    if t < land:
        k = seg(t, 0.4, land)
        y = lerp(-700, gy - 520, ease_in(k))
        implant(c, 540, y, 1.55, 'hero', t, cape=1.0, star=False)
        if t > 0.5: motion_lines(c, 540, y, 260, 255)
    else:
        k = seg(t, land, land + 0.5)
        sq = 1 - 0.18 * math.sin(k * math.pi) * (1 - k)
        mood = 'hero' if not (6.4 < t < 6.9) else 'happy'
        implant(c, 540, gy - 520 + (1 - sq) * 300, 1.55, mood, t, cape=1.0, sq=sq)
        puff(c, 540, gy, seg(t, land, land + 0.8), 9, 280)
    if 6.4 < t < 7.2:
        sparkle(c, 640, 1060, 40 * math.sin(seg(t, 6.4, 7.2) * math.pi), YEL)
    big_title(c, 'ฮีโร่มาแล้ว!', W / 2, TITLE_Y - 20, t, 1.4, 112, YEL, rot=-4, shake=10)
    big_title(c, 'รากฟันเทียม', W / 2, TITLE_Y + 130, t, 3.1, 100)
    subtitle(c, 'ทำจากไทเทเนียม แข็งแรง', t, 4.4, y=1660, size=54, bg=TEAL, fg=WHITE)
    subtitle(c, 'เข้ากับร่างกายได้ดี', t, 5.6, y=1770, size=54, bg=TEAL, fg=WHITE)

def step_header(c, t, n, line):
    step_badge(c, n, W / 2, TITLE_Y - 90, t, 0.2)
    big_title(c, line, W / 2, TITLE_Y + 40, t, 0.45, 76)

IMP_S = 1.3
def scene5(c, t):
    background(c, t, '#D0F4DE', '#E4FDE1')
    top = 1200
    bone_gum(c, top, 0)
    cut_neighbors(c, t, ('smile', 'smile') if t < 4.7 else ('happy', 'happy'))
    k = ease_io(seg(t, 1.0, 4.7))
    y_end = top - 95 + 2   # platform at gum line
    y = lerp(640, y_end, k)
    spin = t * 3 if 1.0 < t < 4.7 else 0
    mood = 'squeeze' if 1.0 < t < 4.7 else ('happy' if t >= 4.7 else 'hero')
    shake = math.sin(t * 70) * 3 if 1.0 < t < 4.7 else 0
    implant(c, 540 + shake, y, IMP_S, mood, t, phase=spin, star=False)
    if 1.0 < t < 4.7:
        for i in range(4):
            ang = t * 8 + i * math.pi / 2
            sparkle(c, 540 + math.cos(ang) * 210, y + 200 + math.sin(ang) * 30, 18, YEL)
        hand_text(c, 'วี้~', 770, 760, t, 1.1, 64, TEAL, 8)
    if t > 4.7:
        burst(c, 540, y + 30, t, 12, 60, 60 + 200 * ease_out(seg(t, 4.7, 5.2)), YEL, 200 * (1 - seg(t, 5.0, 5.6)))
        hand_text(c, 'คลิก!', 330, 780, t, 4.7, 80, CORAL, -8)
    step_header(c, t, 1, 'ฝังรากเทียมลงในกระดูก')
    subtitle(c, 'ใส่ยาชาก่อนเริ่มทำ', t, 1.3, 4.6, y=1700)
    subtitle(c, 'เข้าที่พอดีเป๊ะ!', t, 5.1, y=1700, bg=YEL)

def implant_in_bone(c, t, mood, top=1200):
    implant(c, 540, top - 93, IMP_S, mood, t, star=False)

def scene6(c, t):
    background(c, t, '#E0C3FC', '#F8E1FF')
    top = 1200
    bone_gum(c, top, 0)
    cut_neighbors(c, t, ('sleep', 'sleep'))
    implant_in_bone(c, t, 'sleep')
    # bone buddies walk in and hug
    targets = [(375, 1300), (705, 1300), (385, 1425), (695, 1425), (420, 1545), (660, 1545)]
    for i, (tx, ty) in enumerate(targets):
        st = 0.9 + i * 0.35
        k = ease_out(seg(t, st, st + 1.2))
        sx = -120 if tx < 540 else W + 120
        x = lerp(sx, tx, k); y = ty - abs(math.sin(t * 10 + i)) * 18 * (1 - k)
        bone_buddy(c, x, y, 1.2, t, i, 'happy' if k >= 1 else 'smile')
    for i in range(5):
        st = 3.0 + i * 0.45
        if t > st:
            ph = (t - st) / 2.4
            if ph < 1:
                heart(c, 540 + math.sin(i * 2.1) * 170 + math.sin(t * 3 + i) * 15, 1450 - ph * 420, 26 * (0.6 + ph), CORAL, 255 * (1 - ph))
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        draw_img(c, text_img('z', 46 + 16 * k, LAV, 6, INK), 300 + ph * 50, 860 - ph * 90, 1, 1 - ph)
    months = 1 + 5 * ease_io(seg(t, 1.4, 5.6))
    if t > 0.6:
        s = pop(t, 0.6)
        c.save(); c.translate(820, 690); c.scale(s, s); c.translate(-820, -690)
        calendar(c, 820, 690, t, months)
        c.restore()
    step_header(c, t, 2, 'รอให้กระดูกยึดรากเทียม')
    subtitle(c, 'กระดูกค่อยๆ ยึดแน่น', t, 1.4, 4.0, y=1660, bg=YEL)
    subtitle(c, 'เหมือนรากฟันจริง', t, 1.6, 4.0, y=1770, bg=YEL)
    subtitle(c, 'ใช้เวลาประมาณ 3–6 เดือน', t, 4.1, y=1660)
    subtitle(c, '(ขึ้นกับแต่ละคน)', t, 6.2, y=1770, size=44, bg=MINT)

def scene7(c, t):
    background(c, t, '#BDE0FE', '#E7F5FF')
    top = 1200
    bone_gum(c, top, 0)
    cut_neighbors(c, t, ('smile', 'smile') if t < 3.0 else ('joy', 'joy'))
    implant_in_bone(c, t, 'smile' if t < 3.0 else 'joy')
    plat = top - 93
    # abutment drop
    ka = seg(t, 0.7, 1.1)
    if t > 0.7:
        ya = lerp(600, plat + 2, ease_in(ka))
        abutment(c, 540, ya, IMP_S * 0.95)
    if 1.1 < t < 2.0:
        hand_text(c, 'คลิก!', 330, 760, t, 1.1, 80, CORAL, -8)
    # crown descends
    if t > 1.9:
        kc = ease_out(seg(t, 1.9, 3.0))
        yc = lerp(520, plat - 45, kc)
        wob = math.sin(t * 6) * 6 * (1 - kc)
        crown(c, 540, yc, 1.6, 'joy' if t > 3.0 else 'sleep', t, 3, True, wob)
        if t < 3.0:
            for i in range(3):
                sparkle(c, 540 + math.sin(t * 5 + i * 2) * 160, yc - 40 + math.cos(t * 4 + i) * 60, 22, WHITE)
    if t > 3.0:
        burst(c, 540, plat - 120, t, 14, 180, 180 + 500 * ease_out(seg(t, 3.0, 3.6)), YEL, 80)
        for i in range(6):
            ang = i * math.pi / 3 + t
            sparkle(c, 540 + math.cos(ang) * 300, plat - 160 + math.sin(ang) * 230, 26 * (0.6 + 0.4 * math.sin(t * 6 + i)), YEL)
        hand_text(c, 'ติ๊ง!', 800, 720, t, 3.0, 84, TEAL, 8)
    step_header(c, t, 3, 'ใส่แกนต่อ + ครอบฟัน')
    subtitle(c, 'ต่อแกนเชื่อมด้านบน', t, 1.2, 2.9, y=1700)
    subtitle(c, 'สวมครอบฟัน ได้ฟันซี่ใหม่!', t, 3.1, y=1700, bg=YEL)

def scene8(c, t):
    background(c, t, '#A0E7E5', '#FBE7C6')
    burst(c, 540, 1000, t, 16, 150, 1200, WHITE, 70, 8)
    gy = 1180
    for i, x in enumerate(ROW_X):
        ph = (t * 2.4 + i * 0.5) % 1.0
        j = -abs(math.sin(ph * math.pi)) * 70
        sq = 1 + 0.08 * math.cos(ph * 2 * math.pi)
        tooth(c, x, gy - 120 + j, 0.95, 'joy', math.sin(t * 5 + i) * 6, sq, t=t, seed=i)
    gum_row(c, gy)
    s = pop(t, 0.6)
    if s > 0:
        label(c, 'ใหม่!', ROW_X[2], gy - 330 + math.sin(t * 5) * 8, t, 0.6, 40, CORAL, WHITE, 26, 12, -8)
    confetti(c, t)
    big_title(c, 'ได้ฟันกลับมาครบ!', W / 2, TITLE_Y - 20, t, 0.3, 100, YEL, rot=-3)
    chips = ['เคี้ยวได้มั่นใจ', 'ไม่ต้องกรอฟันข้างเคียง', 'ช่วยชะลอกระดูกยุบ', 'สวยเป็นธรรมชาติ']
    cols = [TEAL, CORAL, '#7B6CF6', '#F4A261']
    for i, ch in enumerate(chips):
        label(c, ch, W / 2 + (-30 if i % 2 else 30), 1330 + i * 112, t, [0.5, 1.6, 2.9, 4.4][i], 50, cols[i], WHITE, rot=(-2 if i % 2 else 2), font=FONT_M)

def scene9(c, t):
    background(c, t, '#CAFFBF', '#FDFFB6')
    gy = 1180
    tooth(c, 540, 860, 1.6, 'happy' if 1.8 < t < 5.4 else 'smile', 0, t=t, seed=7)
    if 1.8 < t < 3.8:
        k = seg(t, 1.8, 2.1) * (1 - seg(t, 3.5, 3.8))
        bx = 540 + math.sin(t * 16) * 70
        c.save(); c.translate(bx + 40, 600 + (1 - k) * -500); c.scale(1, -1); toothbrush(c, 0, 0, 10, 1.1); c.restore()
        bubbles(c, 540, 700, t, 12)
    if 3.8 < t < 5.6:
        k = seg(t, 3.8, 4.1) * (1 - seg(t, 5.3, 5.6))
        fy = 820 + math.sin(t * 9) * 110
        a = 255 * k
        c.drawLine(120, fy - 60, 960, fy + 60, P(WHITE, a, stroke=10))
        c.drawLine(120, fy - 60, 960, fy + 60, P(SKY, a, stroke=4))
        for sx, sy in ((120, fy - 60), (960, fy + 60)):
            c.drawCircle(sx, sy, 24, P(TEAL, a)); c.drawCircle(sx, sy, 24, P(INK, a, stroke=5))
    big_title(c, 'ดูแลเหมือนฟันจริง', W / 2, TITLE_Y - 20, t, 0.3, 96)
    label(c, 'แปรงฟันวันละ 2 ครั้ง', W / 2, 1290, t, 2.0, 52, TEAL, WHITE, font=FONT_M, rot=2)
    label(c, 'ใช้ไหมขัดฟัน', W / 2, 1405, t, 3.7, 52, CORAL, WHITE, font=FONT_M, rot=-2)
    label(c, 'ตรวจกับหมอฟันทุก 6 เดือน', W / 2, 1520, t, 4.6, 52, '#7B6CF6', WHITE, font=FONT_M, rot=1)
    s = pop(t, 6.6)
    if s > 0:
        img = text_img('*ก่อนทำ ทันตแพทย์จะตรวจและเอกซเรย์\nว่าเหมาะกับเราไหม', 40, INK, 0, INK, FONT_R)
        c.save(); c.translate(W / 2, 1680); c.scale(s, s)
        c.drawRoundRect(RR(0, 0, img.width() + 60, img.height() + 40), 24, 24, P(WHITE, 225))
        c.restore()
        draw_img(c, img, W / 2, 1680, s)

def scene10(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), TEAL, '#1B998B'))
    burst(c, 540, 640, t, 20, 200, 1400, WHITE, 28, 6)
    for i in range(12):
        rr = random.Random(200 + i)
        sparkle(c, rr.uniform(60, W - 60), rr.uniform(150, 1750), 14 + 10 * math.sin(t * 3 + i), WHITE, 160)
    # logo
    s = pop(t, 0.15, 0.6)
    if s > 0:
        c.save(); c.translate(540, 620); c.scale(s, s); c.rotate(math.sin(t * 2) * 2)
        c.drawCircle(10, 16, 232, P(INK, 70)); c.drawCircle(0, 0, 232, P(WHITE))
        clip = skia.Path(); clip.addCircle(0, 0, 222)
        c.save(); c.clipPath(clip, doAntiAlias=True)
        c.drawImageRect(LOGO, skia.Rect.MakeXYWH(-232, -232, 464, 464), SAMP, skia.Paint(AntiAlias=True))
        c.restore()
        c.drawCircle(0, 0, 232, P(INK, stroke=9))
        c.restore()
    big_title(c, 'คลินิกทันตกรรม', W / 2, 960, t, 0.5, 92)
    big_title(c, 'บางปะอิน', W / 2, 1085, t, 0.7, 120, YEL)
    label(c, 'โทร / LINE  092-359-5963', W / 2, 1290, t, 1.1, 60, WHITE, INK)
    label(c, 'ตรงข้ามการไฟฟ้าบางปะอิน', W / 2, 1420, t, 1.4, 48, CORAL, WHITE, font=FONT_M)
    label(c, 'เปิด จ.–อา. 09:30–14:00 (ปิดวันศุกร์)', W / 2, 1530, t, 1.7, 42, MINT, INK, font=FONT_M)
    label(c, 'ปรึกษาเรื่องรากฟันเทียม ทักมาได้เลย!', W / 2, 1680, t, 2.3, 48, YEL, INK, rot=-2)

_lg = np.ascontiguousarray(np.array(Image.open(os.path.join(ROOT, 'logo.png')).convert('RGBA').crop((10, 12, 754, 756))))
LOGO = skia.Image.fromarray(_lg, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)

SCENES = [(scene1, 5.79), (scene2, 8.09), (scene3, 5.44), (scene4, 7.55), (scene5, 6.20),
          (scene6, 6.92), (scene7, 4.75), (scene8, 5.57), (scene9, 9.69), (scene10, 6.5)]
STARTS = []
_acc = 0
for fn, d in SCENES:
    STARTS.append(_acc); _acc += d
TOTAL = _acc
TR = 0.4  # iris transition length

def draw_frame(c, T):
    idx = 0
    for i, st in enumerate(STARTS):
        if T >= st: idx = i
    fn, d = SCENES[idx]
    lt = T - STARTS[idx]
    if idx > 0 and lt < TR:
        pfn, pd = SCENES[idx - 1]
        pfn(c, pd + lt)
        k = ease_io(lt / TR)
        r = k * 1250
        ring = skia.Path(); ring.addCircle(540, 960, r)
        c.save(); c.clipPath(ring, doAntiAlias=True)
        fn(c, lt)
        c.restore()
        c.drawCircle(540, 960, r, P(WHITE, 255 * (1 - k), stroke=40))
    else:
        fn(c, lt)
    # progress bar
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 120, W - 60, 132), 6, 6, P(WHITE, 110))
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 120, 60 + (W - 120) * T / TOTAL, 132), 6, 6, P(CORAL, 230))

def render(out, start=0.0, end=None, preview_times=None):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    if preview_times:
        for T in preview_times:
            c.clear(skia.ColorWHITE); draw_frame(c, T)
            arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
            Image.fromarray(arr).convert('RGB').resize((540, 960)).save(f'{out}_{T:05.2f}.png')
        return
    end = TOTAL if end is None else end
    n = int(round((end - start) * FPS))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        T = start + f / FPS
        c.clear(skia.ColorWHITE); draw_frame(c, T)
        pr.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).tobytes())
        if f % 300 == 0: print('frame', f, '/', n, flush=True)
    pr.stdin.close(); pr.wait()

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        ts = [float(x) for x in sys.argv[3:]]
        render(sys.argv[2], preview_times=ts)
    else:
        start = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
        render(sys.argv[2], start)
        print('TOTAL', TOTAL)

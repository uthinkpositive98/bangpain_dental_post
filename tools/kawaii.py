"""Kawaii cartoon Reel toolkit for คลินิกทันตกรรมบางปะอิน (the house style since ep3, 2026-10-18).

Pastel 2D cartoon drawn in code with skia: teeth with faces (big eyes, blush, blinking), squash-and-stretch bounces,
cut-away gum/bone diagrams, the titanium implant hero, bouncy pop-in Thai titles and pill captions, sparkles, bursts,
confetti, iris transitions between scenes, a progress bar, and the clinic end card with the real logo.

An episode is videos/<slug>/scenes.py:

    from tools.kawaii import *
    def s1(c, t): ...                       # draw one frame of scene 1 at local time t (seconds)
    SCENES = [Scene(s1, 6.0), ..., Scene(endcard('ปรึกษาเรื่อง... ทักมาได้เลย!'), 6.0)]

Every pop-in text (label / big_title / step_badge / hand_text) plays a pop automatically; call
cue(t, t0, 'click') etc. for other sound effects (see tools/kawaii_audio.py SFX). Scenes may be held longer
than their nominal length when the narration needs it, so every animation must settle into a final pose
(use seg()/pop() which clamp) - never loop something that must end.
Render with tools/kawaii_render.py.
"""
import skia, numpy as np, math, random, subprocess, os
from PIL import Image, ImageDraw, ImageFont, features

# Format: 9:16 Reel (default) or 16:9 landscape. Set KAWAII_FORMAT=landscape, or put a file named FORMAT containing
# `landscape` in the episode folder (tools/kawaii_render.py reads it before importing this module).
FORMAT = os.environ.get('KAWAII_FORMAT', 'portrait').strip().lower()
LANDSCAPE = FORMAT == 'landscape'
W, H, FPS = (1920, 1080, 30) if LANDSCAPE else (1080, 1920, 30)
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_B = os.path.join(ROOT, 'fonts', 'mitr-700.ttf')
FONT_M = os.path.join(ROOT, 'fonts', 'mitr-600.ttf')
FONT_R = os.path.join(ROOT, 'fonts', 'mitr-500.ttf')
assert features.check('raqm'), 'Pillow needs raqm for Thai text shaping (pip install -U pillow)'

# ---------------------------------------------------------------- sound cues (collected while rendering)
_CUE = {'on': False, 'start': 0.0, 'dt': 1.0 / FPS, 'events': set()}
def cue(t, t0, kind, gain=None):
    """Play sound effect `kind` when the scene clock passes t0 (call it every frame, like pop())."""
    if _CUE['on'] and t0 <= t < t0 + _CUE['dt'] - 1e-9:
        _CUE['events'].add((round(_CUE['start'] + t0, 3), kind, gain))

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
    """pill label that pops in (with a pop sound)"""
    cue(t, t0, 'pop')
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
    cue(t, t0, 'pop')
    s = pop(t, t0, 0.5)
    if s <= 0: return
    img = text_img(txt, size, fill, stroke, INK)
    dx = math.sin(t * 60) * shake * (1 - seg(t, t0, t0 + 0.6)) if shake else 0
    draw_img(c, img, cx + dx + 6, cy + 10, s, 0.0, rot)
    draw_img(c, img, cx + dx, cy, s, 1.0, rot)

def step_badge(c, n, cx, cy, t, t0):
    cue(t, t0, 'pop')
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
        x, y = rr.uniform(60, W - 60), rr.uniform(H * 0.1, H * 0.78)
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
def bone_gum(c, top=None, dip=0.0, gapx=None, gapw=376, sad=0.0, t=0, buddies=False):
    top = GUM_TOP if top is None else top
    gapx = W / 2 if gapx is None else gapx
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
    cue(t, t0, 'pop')
    s = pop(t, t0)
    if s > 0: draw_img(c, text_img(txt, size, col, 6, WHITE), x, y, s, 1, rot)


# ================================================================ layout helpers shared by episodes
if LANDSCAPE:
    TITLE_Y = 150      # big title line; keep characters between y~280 and y~860
    SUB_Y = 965        # caption pill near the bottom edge
    GUM_TOP = 720      # default top of the gum/bone cut-away
else:
    TITLE_Y = 330      # big title line; keep characters between y~600 and y~1450
    SUB_Y = 1530       # caption pill; Reels UI covers roughly y>1780 and the right edge
    GUM_TOP = 1200
ROW_X = [W / 2 - 400, W / 2 - 200, W / 2, W / 2 + 200, W / 2 + 400]   # five teeth in a row

def subtitle(c, txt, t, t0, t1=99, y=SUB_Y, size=56, bg=WHITE, fg=INK):
    if t < t0 or t > t1: return
    a = 1 - seg(t, t1 - 0.25, t1)
    label(c, txt, W / 2, y, t, t0, size, bg, fg, alpha=a, font=FONT_M)

def cut_neighbors(c, t, moods=('smile', 'smile'), top=None, s=1.6):
    """two neighbour teeth standing in a gum/bone cut-away (use with bone_gum(c, top))"""
    top = GUM_TOP if top is None else top
    for j, x in enumerate((W / 2 - 340, W / 2 + 340)):
        tooth(c, x, top - 115 + math.sin(t * 4 + j) * 3, s, moods[j], 0, t=t, seed=j + 20, shadow=False)

def step_header(c, t, n, line):
    step_badge(c, n, W / 2, TITLE_Y - 90, t, 0.2)
    big_title(c, line, W / 2, TITLE_Y + 40, t, 0.45, 76)

IMP_S = 1.3
def implant_in_bone(c, t, mood, top=None):
    top = GUM_TOP if top is None else top
    implant(c, W / 2, top - 93, IMP_S, mood, t, star=False)

def germ(c, x, y, s=1.0, t=0, seed=0, col='#9BE15D', mood='hero'):
    """cute mischievous germ blob (never gross)"""
    c.save(); c.translate(x, y + math.sin(t * 6 + seed) * 8); c.scale(s, s)
    wob = math.sin(t * 8 + seed) * 0.05; c.scale(1 + wob, 1 - wob)
    for i in range(9):
        a = 2 * math.pi * i / 9 + t * 0.6
        bx, by = math.cos(a) * 70, math.sin(a) * 70
        c.drawLine(math.cos(a) * 50, math.sin(a) * 50, bx, by, P(INK, stroke=6))
        c.drawCircle(bx, by, 13, P(col)); c.drawCircle(bx, by, 13, P(INK, stroke=5))
    body = skia.Path(); body.addCircle(0, 0, 62)
    c.drawPath(body, P(col)); c.drawPath(body, P(INK, stroke=7))
    c.drawCircle(-24, -26, 10, P(WHITE, 120))
    face(c, 0, -6, mood, blink_at(t, seed + 5), 0, 0.85, eye_dx=26)
    c.restore()

def brush_buddy(c, x, y, s=1.0, mood='smile', t=0, seed=0, rot=0, sq=1.0, fluff=1.0, cape=0.0):
    """standing toothbrush character (ep4): soft bristle 'hair' on top, face on the handle.
    origin = face centre; fluff > 1 splays the bristles (a worn-out brush)."""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s / sq ** 0.5, s * sq)
    c.drawOval(RR(0, 350, 200, 30), P(INK, 40))
    if cape > 0:
        w1 = math.sin(t * 7 + seed) * 16
        cp = skia.Path(); cp.moveTo(-60, -110)
        cp.cubicTo(-130, 0, -160 + w1, 200, -140 + w1, 300); cp.quadTo(0, 270 + w1, 140 - w1, 300)
        cp.cubicTo(160 - w1, 200, 130, 0, 60, -110); cp.close()
        c.save(); c.scale(cape, 1)
        c.drawPath(cp, lingrad((0, -110), (0, 300), LAV, '#7B6CF6')); c.drawPath(cp, P(INK, stroke=7))
        c.restore()
    # bristle tufts (behind the head block)
    n = 6
    for i in range(n):
        bx = -78 + i * 31.2
        ang = (i - (n - 1) / 2) * 7 * (fluff - 1) * 1.6 + math.sin(t * 5 + i + seed) * 2.5
        c.save(); c.translate(bx, -250); c.rotate(ang)
        r = skia.Rect.MakeLTRB(-16, -112 - 10 * (fluff - 1), 16, 10)
        c.drawRoundRect(r, 16, 16, P(SKY if i % 2 else WHITE)); c.drawRoundRect(r, 16, 16, P(INK, stroke=6))
        c.restore()
    # head block
    hb = skia.Rect.MakeLTRB(-100, -270, 100, -170)
    c.drawRoundRect(hb, 34, 34, lingrad((0, -270), (0, -170), WHITE, SHADE)); c.drawRoundRect(hb, 34, 34, P(INK, stroke=7))
    # handle body
    body = skia.Rect.MakeLTRB(-78, -185, 78, 340)
    c.drawRoundRect(body, 70, 70, lingrad((-78, 0), (78, 0), '#1FA99C', TEAL)); c.drawRoundRect(body, 70, 70, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(30, -120, 48, 260), 9, 9, P(WHITE, 90))
    c.drawRoundRect(skia.Rect.MakeLTRB(-78, 150, 78, 200), 4, 4, P(MINT, 200))
    c.drawLine(-74, 150, 74, 150, P(INK, stroke=5)); c.drawLine(-74, 200, 74, 200, P(INK, stroke=5))
    face(c, 0, 0, mood, blink_at(t, seed + 3), 0, 1.0, eye_dx=30)
    c.restore()

def gauge(c, x, y, val, s=1.0):
    """pressure meter: val 0 (gentle, green) .. 1 (too hard, red)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-215, -215, 215, 60), 40, 40, P(INK, 60))
    c.drawRoundRect(skia.Rect.MakeLTRB(-225, -225, 205, 45), 40, 40, P(WHITE))
    c.drawRoundRect(skia.Rect.MakeLTRB(-225, -225, 205, 45), 40, 40, P(INK, stroke=7))
    c.translate(-10, 0)
    ov = skia.Rect.MakeLTRB(-165, -165, 165, 165)
    for a0, sw, col in ((180, 75, '#7ED957'), (255, 45, YEL), (300, 60, CORAL)):
        pth = skia.Path(); pth.addArc(ov, a0, sw)
        c.drawPath(pth, P(col, stroke=44))
    pth = skia.Path(); pth.addArc(skia.Rect.MakeLTRB(-188, -188, 188, 188), 180, 180); c.drawPath(pth, P(INK, stroke=6))
    pth = skia.Path(); pth.addArc(skia.Rect.MakeLTRB(-142, -142, 142, 142), 180, 180); c.drawPath(pth, P(INK, stroke=6))
    ang = math.radians(180 + 180 * clamp(val, -0.05, 1.05))
    c.drawLine(0, 0, math.cos(ang) * 135, math.sin(ang) * 135, P(INK, stroke=14))
    c.drawCircle(0, 0, 26, P(CORAL)); c.drawCircle(0, 0, 26, P(INK, stroke=6))
    c.restore()
    draw_img(c, text_img('เบา', 40, '#3E9B2F', 0), x - 10 - 150 * s, y + 10 * s, s)
    draw_img(c, text_img('แรง', 40, CORAL, 0), x - 10 + 150 * s, y + 10 * s, s)

def timer_clock(c, x, y, frac, s=1.0, t=0):
    """round timer that fills up (frac 0..1)"""
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(t * 6) * 2)
    c.drawRoundRect(RR(0, -165, 60, 40), 12, 12, P(CORAL)); c.drawRoundRect(RR(0, -165, 60, 40), 12, 12, P(INK, stroke=6))
    c.drawCircle(8, 12, 150, P(INK, 70)); c.drawCircle(0, 0, 150, P(WHITE))
    if frac > 0:
        pie = skia.Path(); pie.moveTo(0, 0); pie.arcTo(skia.Rect.MakeLTRB(-122, -122, 122, 122), -90, 360 * clamp(frac) - 0.01, False); pie.close()
        c.drawPath(pie, P(MINT))
    c.drawCircle(0, 0, 150, P(INK, stroke=8)); c.drawCircle(0, 0, 132, P(CORAL, stroke=10))
    for i in range(12):
        a = 2 * math.pi * i / 12
        c.drawLine(math.cos(a) * 108, math.sin(a) * 108, math.cos(a) * 120, math.sin(a) * 120, P(INK, stroke=6))
    a = -math.pi / 2 + 2 * math.pi * clamp(frac)
    c.drawLine(0, 0, math.cos(a) * 95, math.sin(a) * 95, P(INK, stroke=10))
    c.drawCircle(0, 0, 14, P(INK))
    c.restore()

def ice_cube(c, x, y, s=1.0, t=0, seed=0, mood='happy', rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    r = RR(0, 0, 150, 150)
    c.drawRoundRect(r, 34, 34, lingrad((0, -75), (0, 75), '#E8FBFF', '#A9E7F7')); c.drawRoundRect(r, 34, 34, P(INK, stroke=7))
    c.drawRoundRect(skia.Rect.MakeLTRB(-52, -56, -20, -40), 8, 8, P(WHITE, 220))
    face(c, 0, 4, mood, blink_at(t, seed), 0, 0.7, eye_dx=24)
    c.restore()

def zap(c, x, y, s=1.0, rot=0, a=255):
    """little lightning bolt (sensitivity 'zing')"""
    if a <= 1: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.moveTo(10, -60); p.lineTo(-28, 6); p.lineTo(0, 6); p.lineTo(-12, 60); p.lineTo(30, -10); p.lineTo(2, -10); p.close()
    c.drawPath(p, P(YEL, a)); c.drawPath(p, P(INK, a, stroke=5))
    c.restore()

# ================================================================ Dr. นวรัตน์ (hero dentist) and the cover card
SKIN = '#FFE0CC'; SKIN_D = '#F6C3A6'; HAIR = '#3A2A33'; SCRUB = '#2EC4B6'; SCRUB_D = '#1B998B'; CAPE = '#FF5A6E'

def _fill(c, p, col, stroke=7):
    c.drawPath(p, P(col) if isinstance(col, str) else col)
    if stroke: c.drawPath(p, P(INK, stroke=stroke))

def dr_nawarat(c, x, y, s=1.0, t=0.0, mood='smile', wave=0.0, point=0.0, cape=1.0, hold=None):
    """หมอนวรัตน์ in bright aqua scrubs with a superhero cape (knowledge scenes). origin = centre of the head;
    the body reaches ~+560*s below it. wave/point 0..1 raise the right/left arm; hold='brush'|'mirror' in the left hand;
    cape 0 hides the cape (clinic scenes)."""
    yy = y + math.sin(t * 2.6) * 5
    c.save(); c.translate(x, yy); c.scale(s, s)
    if cape > 0:
        w1 = math.sin(t * 5) * 22
        cp = skia.Path(); cp.moveTo(-150, 170)
        cp.cubicTo(-260 - w1, 330, -300 - w1, 520, -250 - w1, 620); cp.quadTo(0, 560 + w1 * 0.5, 250 + w1, 620)
        cp.cubicTo(300 + w1, 520, 260 + w1, 330, 150, 170); cp.close()
        c.save(); c.scale(cape, 1)
        _fill(c, cp, lingrad((0, 170), (0, 620), CAPE, '#C9184A'))
        c.restore()
    body = skia.Path(); body.addRoundRect(skia.Rect.MakeLTRB(-190, 150, 190, 560), 130, 130)
    _fill(c, body, lingrad((0, 150), (0, 560), SCRUB, SCRUB_D))
    v = skia.Path(); v.moveTo(-70, 165); v.lineTo(0, 270); v.lineTo(70, 165); v.close(); _fill(c, v, SKIN, 6)
    c.drawLine(-120, 380, 120, 380, P(SCRUB_D, stroke=8))
    # hero badge (golden circle with a tooth)
    c.drawCircle(-92, 330, 46, P(YEL)); c.drawCircle(-92, 330, 46, P(INK, stroke=6))
    c.save(); c.translate(-92, 330); c.scale(0.28, 0.28); c.drawPath(TOOTH, P(WHITE)); c.drawPath(TOOTH, P(INK, stroke=14)); c.restore()
    c.drawRoundRect(RR(92, 320, 70, 40), 8, 8, P(WHITE)); c.drawRoundRect(RR(92, 320, 70, 40), 8, 8, P(INK, stroke=5))
    neck = skia.Path(); neck.addRoundRect(RR(0, 150, 86, 60), 30, 30); _fill(c, neck, SKIN, 6)
    # head: short bob, round glasses
    bh = skia.Path(); bh.addRoundRect(skia.Rect.MakeLTRB(-188, -170, 188, 100), 150, 150); _fill(c, bh, HAIR)
    for sx in (-1, 1):
        e = skia.Path(); e.addOval(RR(sx * 170, 20, 50, 70)); _fill(c, e, SKIN, 6)
    hd = skia.Path(); hd.addOval(RR(0, 0, 330, 320)); _fill(c, hd, lingrad((0, -160), (0, 160), '#FFEADB', SKIN))
    fr = skia.Path(); fr.moveTo(-168, 10); fr.cubicTo(-170, -140, -50, -185, 30, -168)
    fr.cubicTo(120, -160, 172, -100, 168, 0); fr.cubicTo(150, -60, 80, -110, 40, -80)
    fr.cubicTo(-10, -110, -110, -90, -168, 10); fr.close(); _fill(c, fr, HAIR)
    face(c, 0, 22, mood, blink_at(t, 5), 0, 1.45, eye_dx=50)
    for sx in (-1, 1):
        c.drawCircle(sx * 72, 22, 44, P(WHITE, 40)); c.drawCircle(sx * 72, 22, 44, P(INK, stroke=7))
    c.drawLine(-28, 18, 28, 18, P(INK, stroke=6))
    # arms
    def arm(side, ang, item=None):
        c.save(); c.translate(side * 170, 230); c.rotate(ang)
        a = skia.Path(); a.addRoundRect(RR(0, 90, 64, 180), 32, 32); _fill(c, a, SCRUB, 6)
        h = skia.Path(); h.addCircle(0, 190, 36); _fill(c, h, SKIN, 6)
        if item == 'brush':
            c.save(); c.translate(0, 230); c.rotate(180); toothbrush(c, 0, 0, 0, 0.8); c.restore()
        elif item == 'mirror':
            c.drawLine(0, 190, 0, 300, P(INK, stroke=12)); c.drawLine(0, 190, 0, 300, P('#C9D6E8', stroke=6))
            c.drawCircle(0, 318, 22, P('#CFF4FF')); c.drawCircle(0, 318, 22, P(INK, stroke=6))
        c.restore()
    arm(1, -20 - 110 * wave + math.sin(t * 8) * 16 * wave)
    arm(-1, 20 + 50 * point, hold)
    c.restore()

def cover(title, sub='', chip='', top='#FFE7C7', bot='#FFC8A2', cast=None):
    """opening title card (first scene, ~4 s): pastel sunburst, big two-tone title, subtitle pill, episode chip and
    the cast (default: a happy tooth + หมอนวรัตน์). `cast(c, t)` may draw custom characters instead."""
    def draw(c, t):
        c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), top, bot))
        burst(c, W / 2, H * 0.62, t, 22, 120, max(W, H) * 1.2, WHITE, 80, 5)
        cue(t, 0.1, 'fanfare')
        if cast: cast(c, t)
        elif LANDSCAPE:
            tooth(c, 360, 720 + math.sin(t * 4) * 8, 1.5 * pop(t, 0.3), 'joy', t=t, seed=1)
            dr_nawarat(c, 1540, 470, 0.78 * pop(t, 0.5), t, 'happy', wave=1.0)
        else:
            tooth(c, 300, 1350 + math.sin(t * 4) * 8, 1.6 * pop(t, 0.3), 'joy', t=t, seed=1)
            dr_nawarat(c, 780, 1150, 0.7 * pop(t, 0.5), t, 'happy', wave=1.0)
        ty = H * (0.30 if LANDSCAPE else 0.24)
        big_title(c, title, W / 2, ty, t, 0.15, 128 if LANDSCAPE else 112, YEL, 14, rot=-2)
        if sub:
            label(c, sub, W / 2, ty + (150 if LANDSCAPE else 190), t, 0.6, 54, CORAL, WHITE, rot=-1)
        if chip:
            label(c, chip, 230 if LANDSCAPE else 230, 110 if LANDSCAPE else 230, t, 0.9, 46, TEAL, WHITE, rot=-8)
        for i in range(8):
            rr = random.Random(300 + i)
            sparkle(c, rr.uniform(80, W - 80), rr.uniform(80, H - 80), 12 + 9 * math.sin(t * 3 + i), WHITE, 200)
    draw.is_cover = True
    return draw

# ================================================================ clinic end card (always the last scene)
_lg = Image.open(os.path.join(ROOT, 'assets', 'logo.png')).convert('RGBA')
_lw, _lh = _lg.size; _m = int(min(_lw, _lh) * 0.014)
_lg = np.ascontiguousarray(np.array(_lg.crop((_m, _m, min(_lw, _lh) - _m, min(_lw, _lh) - _m))))
LOGO = skia.Image.fromarray(_lg, colorType=skia.ColorType.kRGBA_8888_ColorType, alphaType=skia.AlphaType.kUnpremul_AlphaType)

def endcard(cta='ปรึกษาทันตแพทย์ ทักมาได้เลย!'):
    """returns a scene function: logo, clinic name, phone/LINE, address, hours, and a call to action"""
    # (logo centre, logo radius, text column x, y of: name1, name2, phone, address, hours, cta)
    if LANDSCAPE:
        lx, ly, lr, tx, ys = 500, 520, 250, 1260, (250, 380, 560, 680, 790, 920)
    else:
        lx, ly, lr, tx, ys = 540, 620, 232, W / 2, (960, 1085, 1290, 1420, 1530, 1680)
    def draw(c, t):
        c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), TEAL, '#1B998B'))
        burst(c, lx, ly, t, 20, 200, 1400, WHITE, 28, 6)
        for i in range(12):
            rr = random.Random(200 + i)
            sparkle(c, rr.uniform(60, W - 60), rr.uniform(H * 0.08, H * 0.92), 14 + 10 * math.sin(t * 3 + i), WHITE, 160)
        cue(t, 0.15, 'sparkle')
        s = pop(t, 0.15, 0.6)
        if s > 0:
            k = lr / 232
            c.save(); c.translate(lx, ly); c.scale(s * k, s * k); c.rotate(math.sin(t * 2) * 2)
            c.drawCircle(10, 16, 232, P(INK, 70)); c.drawCircle(0, 0, 232, P(WHITE))
            clip = skia.Path(); clip.addCircle(0, 0, 222)
            c.save(); c.clipPath(clip, doAntiAlias=True)
            c.drawImageRect(LOGO, skia.Rect.MakeXYWH(-232, -232, 464, 464), SAMP, skia.Paint(AntiAlias=True))
            c.restore()
            c.drawCircle(0, 0, 232, P(INK, stroke=9))
            c.restore()
        big_title(c, 'คลินิกทันตกรรม', tx, ys[0], t, 0.5, 92)
        big_title(c, 'บางปะอิน', tx, ys[1], t, 0.7, 120, YEL)
        label(c, 'โทร / LINE  092-359-5963', tx, ys[2], t, 1.1, 60, WHITE, INK)
        label(c, 'ตรงข้ามการไฟฟ้าบางปะอิน', tx, ys[3], t, 1.4, 48, CORAL, WHITE, font=FONT_M)
        label(c, 'เปิด จ.–อา. 09:30–14:00 (ปิดวันศุกร์)', tx, ys[4], t, 1.7, 42, MINT, INK, font=FONT_M)
        if cta:
            label(c, cta, tx, ys[5], t, 2.3, 48, YEL, INK, rot=-2)
    draw.is_endcard = True
    return draw

# ================================================================ timeline engine
class Scene:
    def __init__(self, draw, dur):
        self.draw, self.dur = draw, float(dur)

TR = 0.4  # iris transition between scenes

def timeline(scenes):
    starts, acc = [], 0.0
    for sc in scenes:
        starts.append(acc); acc += sc.dur
    return starts, acc

def draw_frame(c, scenes, starts, total, T, progress=True):
    idx = max(i for i, st in enumerate(starts) if T >= st - 1e-9)
    sc = scenes[idx]; lt = T - starts[idx]
    if idx > 0 and lt < TR:
        prev = scenes[idx - 1]
        _CUE['on'], on = False, _CUE['on']
        prev.draw(c, prev.dur + lt)
        _CUE['on'] = on
        k = ease_io(lt / TR)
        r = k * math.hypot(W, H) * 0.6
        ring = skia.Path(); ring.addCircle(W / 2, H / 2, r)
        _CUE['start'] = starts[idx]
        c.save(); c.clipPath(ring, doAntiAlias=True); sc.draw(c, lt); c.restore()
        c.drawCircle(W / 2, H / 2, r, P(WHITE, 255 * (1 - k), stroke=40))
    else:
        _CUE['start'] = starts[idx]
        sc.draw(c, lt)
    if progress:
        py = 40 if LANDSCAPE else 120
        c.drawRoundRect(skia.Rect.MakeLTRB(60, py, W - 60, py + 12), 6, 6, P(WHITE, 110))
        c.drawRoundRect(skia.Rect.MakeLTRB(60, py, 60 + (W - 120) * T / total, py + 12), 6, 6, P(CORAL, 230))

def snapshot(surf):
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

def render_video(scenes, out, fps=FPS):
    """silent MP4; returns the sound cues [(time, kind, gain)] collected while drawing (+ a whoosh per cut)"""
    starts, total = timeline(scenes)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    _CUE.update(on=True, dt=1.0 / fps, events=set())
    n = int(round(total * fps))
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                           '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                           '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(n):
        c.clear(skia.ColorWHITE)
        draw_frame(c, scenes, starts, total, f / fps)
        ff.stdin.write(snapshot(surf).tobytes())
        if f % 300 == 0: print(f'  frame {f}/{n}', flush=True)
    ff.stdin.close(); ff.wait()
    _CUE['on'] = False
    cues = sorted(_CUE['events'])
    cues += [(st, 'whoosh', None) for st in starts[1:]]
    return sorted(cues), total

def contact_sheet(scenes, out_png, moments=(0.15, 0.5, 0.92)):
    starts, total = timeline(scenes)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    tw, th = (480, 270) if LANDSCAPE else (270, 480)
    sheet = Image.new('RGB', (len(moments) * (tw + 8) + 50, len(scenes) * (th + 8)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, (sc, st) in enumerate(zip(scenes, starts)):
        d.text((10, i * (th + 8) + 10), str(i + 1), fill='black')
        for j, k in enumerate(moments):
            c.clear(skia.ColorWHITE)
            draw_frame(c, scenes, starts, total, st + max(TR + 0.01, sc.dur * k) if i else st + sc.dur * k)
            im = Image.fromarray(snapshot(surf)).convert('RGB').resize((tw, th))
            sheet.paste(im, (50 + j * (tw + 8), i * (th + 8)))
    sheet.save(out_png)
    return out_png

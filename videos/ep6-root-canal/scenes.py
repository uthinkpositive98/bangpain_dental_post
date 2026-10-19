"""ep6 ปวดฟันจี๊ด! ต้องรักษารากฟันไหม — สมจี๊ด's toothache, หมอนวรัตน์'s exam in a detailed operatory, the x-ray,
root canal step by step, what comes after, and what happens if it is left untreated. Cover first, clinic banner on every
story scene, captions synced to Nueng's narration, clinic end card last."""
import sys, os, math, re, subprocess, wave, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from tools.kawaii import *  # noqa: F401,F403
from chars import *  # noqa: F401,F403
from rc import *  # noqa: F401,F403
from rc import _poly
from script import SPOKEN, CAPS

N_VO = len(SPOKEN)
LEAD = 0.15
WORK = os.path.join(HERE, '.work'); os.makedirs(WORK, exist_ok=True)
SR = 22050

# ---------------------------------------------------------------- caption timing from the narration
def _trimmed(i):
    src = os.path.join(HERE, 'narration', f'scene{i}.mp3'); dst = os.path.join(WORK, f'cap{i}.wav')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        f = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
             "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', f, '-ac', '1', '-ar', str(SR), dst], check=True)
    w = wave.open(dst)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

def _weight(s):
    return max(1, len(re.sub(r'[\s,.!?:ัิ-ฺ็-๎]', '', s)))

def _timing(i):
    a = _trimmed(i); dur = len(a) / SR; hop = int(SR * 0.02)
    rms = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2) + 1e-12) for k in range(0, len(a), hop)])
    env = np.clip(rms / (rms.max() + 1e-9) * 1.8, 0, 1)
    quiet = rms < rms.max() * 0.06
    gaps, k = [], 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]: j += 1
            if (j - k) * 0.02 >= 0.12 and k > 0 and j < len(quiet): gaps.append((k + j) / 2 * 0.02)
            k = j
        else: k += 1
    ws = [_weight(s) for s in SPOKEN[i - 1]]
    cum = np.cumsum(ws) / sum(ws)
    bounds = [0.0]
    for cc in cum[:-1]:
        g = cc * dur
        near = [x for x in gaps if abs(x - g) < 0.9]
        bounds.append(min(near, key=lambda x: abs(x - g)) if near else g)
    bounds.append(dur)
    return dur, [(LEAD + bounds[k], LEAD + bounds[k + 1]) for k in range(len(ws))], env

VO = [_timing(i) for i in range(1, N_VO + 1)]
def S(i, k): return VO[i - 1][1][k][0]
def L(i, extra=1.0, minimum=0.0): return max(minimum, LEAD + VO[i - 1][0] + extra)

def captions(c, i, t, y=1630, size=46):
    dur, segs, _ = VO[i - 1]
    for k, ((a, b), txt) in enumerate(zip(segs, CAPS[i - 1])):
        b2 = segs[k + 1][0] - 0.05 if k + 1 < len(segs) else b + 0.9
        if a - 0.05 <= t < b2:
            s = pop(t, a - 0.05, 0.3)
            img = text_img(txt, size, INK, 0, INK, FONT_M, spacing=8)
            w, h = img.width() + 70, img.height() + 40
            c.save(); c.translate(W / 2, y); c.scale(s, s)
            c.drawRoundRect(RR(6, 9, w, h), 34, 34, P(INK, 70))
            c.drawRoundRect(RR(0, 0, w, h), 34, 34, P(WHITE, 245))
            c.drawRoundRect(RR(0, 0, w, h), 34, 34, P(INK, stroke=6))
            c.restore()
            draw_img(c, img, W / 2, y + 2, s)

def arrow(c, x0, y0, x1, y1, k=1.0, col=INK, w=6):
    if k <= 0: return
    x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k)
    c.drawLine(x0, y0, x1, y1, P(col, stroke=w))
    c.drawCircle(x1, y1, 9, P(col))

def callout(c, txt, x, y, tx, ty, t, t0, bg=WHITE, fg=INK, size=38, rot=0):
    if t < t0: return
    arrow(c, x, y, tx, ty, ease_out(seg(t, t0, t0 + 0.35)))
    label(c, txt, x, y, t, t0, size, bg, fg, 28, 16, rot=rot)

def card(c, cx, cy, w, h, t, t0, col=WHITE, rot=0):
    s = pop(t, t0, 0.45)
    if s <= 0: return 0
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(RR(8, 12, w, h), 40, 40, P(INK, 60))
    c.drawRoundRect(RR(0, 0, w, h), 40, 40, P(col)); c.drawRoundRect(RR(0, 0, w, h), 40, 40, P(INK, stroke=7))
    c.restore()
    return s

def num_badge(c, n, x, y, t, t0, col=YEL):
    s = pop(t, t0, 0.4)
    if s <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(4, 6, 46, P(INK, 70)); c.drawCircle(0, 0, 46, P(col)); c.drawCircle(0, 0, 46, P(INK, stroke=7))
    c.restore()
    draw_img(c, text_img(str(n), 56, INK, 0), x, y + 2, s)

def no_sign(c, x, y, r, a=255):
    c.drawCircle(x, y, r, P(CORAL, a, stroke=16))
    d = r * 0.707; c.drawLine(x - d, y - d, x + d, y + d, P(CORAL, a, stroke=16))

FACE = load_photo(os.path.join(HERE, 'photos', 'face.png'))
SHIRT = '#FF9EBB'
GERM_COLS = ['#9BE15D', '#B58CFF', '#FFB347']

def zaps(c, x, y, t, k=1.0, n=3, s=1.0):
    for i in range(n):
        a = 255 * k * (0.6 + 0.4 * abs(math.sin(t * 9 + i)))
        zap(c, x + math.cos(i * 2.1) * 70 * s, y + math.sin(i * 2.1) * 60 * s, 0.9 * s, -20 + i * 30, a)

# ================================================================ 0 cover (frame 0 = thumbnail)
def scene0(c, t):
    t = t + 4.0
    c.drawRect(skia.Rect.MakeWH(W, H), lingrad((0, 0), (0, H), '#FFE1EA', '#FFF3D9'))
    burst(c, 540, 1000, t * 0.3, 18, 260, 1300, WHITE, 70, 4)
    for i in range(14):
        rr = random.Random(800 + i)
        sparkle(c, rr.uniform(60, W - 60), rr.uniform(200, 1800), 12 + 8 * rr.random(), WHITE, 210)
    person(c, 330, 900, 1.15, 'pain', 0, t, hand=1.0, shirt=SHIRT, bob=False, ouch=1.0)
    zaps(c, 560, 760, t, 1.0, 3, 1.3)
    # "inside the tooth" bubble
    for i, (bx, by, br) in enumerate(((560, 900, 16), (600, 950, 24))):
        c.drawCircle(bx, by, br, P(WHITE)); c.drawCircle(bx, by, br, P(INK, stroke=5))
    cx, cy, r = 800, 1080, 235
    c.drawCircle(cx + 10, cy + 14, r + 12, P(INK, 70)); c.drawCircle(cx, cy, r + 12, P(WHITE)); c.drawCircle(cx, cy, r + 12, P(INK, stroke=8))
    clip = skia.Path(); clip.addCircle(cx, cy, r)
    c.save(); c.clipPath(clip, doAntiAlias=True)
    c.drawCircle(cx, cy, r, P('#FFF2E0'))
    tooth_section(c, cx, cy + 50, 0.62, t, decay=1, inflam=1, pmood='squeeze')
    germ(c, cx - 70, cy - 150, 0.32, t, 1, GERM_COLS[0])
    c.restore()
    c.drawCircle(cx, cy, r, P(TEAL, stroke=10))
    hand_text(c, 'จี๊ด!!', 820, 770, 9, 0, 110, CORAL, 10)
    big_title(c, 'ปวดฟันจี๊ด!', W / 2, 250, 9, 0, 124, '#FF6B8A', rot=-2)
    big_title(c, 'ต้องรักษารากฟันไหม?', W / 2, 395, 9, 0, 86)
    c.save(); c.translate(W / 2, 1560); c.rotate(-2)
    c.drawRoundRect(RR(10, 14, 920, 220), 50, 50, P(INK, 80))
    c.drawRoundRect(RR(0, 0, 920, 220), 50, 50, lingrad((0, -110), (0, 110), '#2EC4B6', '#1B998B'))
    c.drawRoundRect(RR(0, 0, 920, 220), 50, 50, P(INK, stroke=8))
    c.restore()
    draw_img(c, text_img('รักษารากฟัน ทำยังไง?', 70, WHITE, 8, INK), W / 2, 1518, 1, 1, -2)
    draw_img(c, text_img('ทำอะไรต่อ / ไม่รักษาได้ไหม?', 52, YEL, 8, INK), W / 2, 1610, 1, 1, -2)
    label(c, 'ไปดูกับหมอนวรัตน์', W / 2 + 70, 1765, 9, 0, 44, WHITE, INK, rot=2)
    face_badge(c, FACE, W / 2 - 270, 1745, 88)
    clinic_banner(c)

# ================================================================ 1 ice cream -> จี๊ด! -> can't sleep
def scene1(c, t):
    k1 = S(1, 1)
    if t < k1:
        background(c, t, '#FFF0F5', '#FFF8E6')
        hit = 1.0
        mood = 'happy' if t < hit else 'pain'
        if t >= hit: burst(c, 700, 760, t, 14, 80, 600, YEL, 90, 10)
        person(c, 470, 880, 1.3, mood, 0.35 if t < hit else 0, t, hand=seg(t, hit + 0.1, hit + 0.4), shirt=SHIRT, ouch=seg(t, hit, hit + 0.2))
        ice_cream(c, 840, 1150 - 30 * ease_out(seg(t, 0.2, 0.8)), 0.95, t, bite=seg(t, 0.8, 0.95))
        if t >= hit:
            cue(t, hit, 'boing')
            zaps(c, 740, 700, t, 1.0, 3, 1.4)
            hand_text(c, 'จี๊ด!!', 780, 540, t, hit, 120, CORAL, 10)
            big_title(c, 'โอ๊ย!', 250, 540, t, hit + 0.1, 100, '#FF6B8A', rot=-8)
    else:
        u = t - k1
        night_room(c, t)
        # headboard + bed
        hb = skia.Path(); hb.addRoundRect(skia.Rect.MakeLTRB(80, 760, 760, 1460), 80, 80); fill(c, hb, '#B79CFF', stroke=8)
        c.drawRoundRect(skia.Rect.MakeLTRB(130, 810, 710, 1000), 60, 60, P('#C9B5FF'))
        person(c, 420, 980, 1.05, 'pain', 0, t, hand=1.0, shirt=SHIRT, ouch=0.6 + 0.4 * math.sin(t * 6))
        bl = skia.Path(); bl.moveTo(40, 1300); bl.cubicTo(250, 1250, 600, 1270, 800, 1300); bl.lineTo(820, 1560); bl.lineTo(40, 1560); bl.close()
        fill(c, bl, lingrad((0, 1260), (0, 1560), '#FFD6E0', '#FF9EBB'), stroke=8)
        for i in range(6): c.drawCircle(120 + i * 120, 1400 + (i % 2) * 50, 16, P(WHITE, 200))
        # nightstand + alarm clock
        ns = skia.Path(); ns.addRoundRect(skia.Rect.MakeLTRB(800, 1260, 1040, 1560), 24, 24); fill(c, ns, '#C8A27A', stroke=7)
        c.drawLine(820, 1400, 1020, 1400, P(INK, 140, stroke=5)); c.drawCircle(920, 1340, 10, P(INK)); c.drawCircle(920, 1470, 10, P(INK))
        alarm_clock(c, 920, 1160, 0.85, t, '02:00')
        storm(c, 420, 640, t, 1.1)
        for j, t0 in enumerate((0.5, 1.3, 2.1, 2.9)):
            if u >= t0:
                cue(t, k1 + t0, 'thud', 0.5)
                ph = seg(u, t0, t0 + 0.6)
                if ph < 1: draw_img(c, text_img('ตุบ!', 64, CORAL, 7, WHITE), 640 + j % 2 * 60, 820 - ph * 60, 0.8 + 0.4 * ph, 1 - ph, -8)
        c.drawRect(skia.Rect.MakeWH(W, H), P(WHITE, 255 * (1 - seg(u, 0, 0.35))))
    captions(c, 1, t)

# ================================================================ 2 the operatory: หมอนวรัตน์ walks in, lamp on
def room_scene(c, t, open_k=0.0, mood='worry', lamp_on=1.0, doc_x=170, right=('down', None), left=('down', None)):
    room_back(c, t)
    xray_monitor_small(c, 640, 640, t)
    lamp(c, t, lamp_on, target=(430, 990))
    dental_chair(c, t)
    tray(c, 800, 900, t)
    lying_patient(c, 400, 1010, 0.42, t, mood, open_k, shirt=SHIRT)
    doc(c, doc_x, 790, 0.7, t, FACE, left=left, right=right)

def scene2(c, t):
    k1, k2 = S(2, 1), S(2, 2)
    walk = ease_out(seg(t, 0.2, 1.7))
    on = seg(t, k1 + 0.7, k1 + 0.9)
    pose = ('wave', None) if t < k2 - 0.3 else ('reach', 'mirror')
    room_scene(c, t, open_k=0.5 * seg(t, k2 + 0.6, k2 + 1.0), lamp_on=on, doc_x=lerp(-260, 170, walk), right=pose)
    if on > 0:
        cue(t, k1 + 0.7, 'click')
        for i in range(4): sparkle(c, 380 + i * 50, 960 + (i % 2) * 40, 12 + 6 * math.sin(t * 6 + i), YEL, 220 * on)
    speech(c, 'มาค่ะ หมอขอ\nตรวจหน่อยนะคะ', 590, 560, t, k2, 46, 'left')
    captions(c, 2, t)

# ================================================================ 3 exam inside the mouth
def scene3(c, t):
    k1, k2 = S(3, 1), S(3, 2)
    background(c, t, '#E3FFF5', '#EAF4FF')
    cx, cy = 540, 930
    # warm lamp glow on the face
    c.drawCircle(cx, cy, 560, P('#FFF7C2', 90, blur=40))
    mouth_close(c, cx, cy, t, 1.0, seg(t, k1, k1 + 0.3))
    tx, ty = cx + 190, cy + 250       # the decayed molar
    # mirror comes in from lower left and props the cheek
    mk = ease_out(seg(t, 0.2, 0.9))
    big_mirror(c, lerp(-100, 330, mk), lerp(1700, 1150, mk), 28, 1.0)
    # explorer scans along the lower teeth, finds the cavity, then taps
    pk = ease_out(seg(t, 0.4, 1.1))
    if t < k1:
        sx = lerp(cx - 260, tx, ease_io(seg(t, 1.1, k1)))
        px, py = lerp(1200, sx, pk), lerp(1700, ty - 10 + 20 * math.sin(t * 7), pk)
    else:
        tap = abs(math.sin((t - k2) * 10)) if k2 <= t < k2 + 1.2 else 0
        px, py = tx, ty - 6 - 22 * tap
    big_probe(c, px, py, -28, 1.0)
    if t >= k1:
        cue(t, k1, 'ding')
        label(c, 'เจอแล้ว! ฟันกรามผุเป็นรูลึก', 540, 1470, t, k1 + 0.1, 46, CORAL, WHITE, rot=-2)
    if t >= k2:
        for j in range(3): cue(t, k2 + j * 0.31, 'tick', 0.6)
        zaps(c, tx + 140, ty - 120, t, seg(t, k2 + 0.1, k2 + 0.3), 3, 1.0)
        hand_text(c, 'เจ็บ!', 900, 900, t, k2 + 0.2, 80, CORAL, 10)
    big_title(c, 'ตรวจในปาก', W / 2, TITLE_Y - 30, t, 0.2, 84)
    captions(c, 3, t)

# ================================================================ 4 the x-ray
def scene4(c, t):
    k1, k2 = S(4, 1), S(4, 2)
    background(c, t, '#E2F3FF', '#F1EDFF')
    p1, p2 = xray_view(c, 540, 900, 820, 600, t, decay=1.0, lesion=ease_out(seg(t, k2 - 0.2, k2 + 0.5)),
                       ring=seg(t, k1, k1 + 0.3), ring2=seg(t, k2, k2 + 0.3))
    # scan bar
    if t < 1.2:
        y = lerp(600, 1200, seg(t, 0.2, 1.1))
        c.drawRect(skia.Rect.MakeLTRB(130, y - 6, 950, y + 6), P('#7CFFB2', 160 * (1 - seg(t, 1.0, 1.2))))
        cue(t, 0.2, 'sparkle')
    if t >= k1:
        cue(t, k1, 'ding')
        callout(c, 'ผุถึงโพรงประสาท!', 320, 1370, p1[0], p1[1] + 40, t, k1 + 0.1, YEL, INK, 40, -3)
    if t >= k2:
        cue(t, k2, 'ding')
        callout(c, 'อักเสบที่ปลายราก', 760, 1470, p2[0] + 30, p2[1] + 10, t, k2 + 0.1, CORAL, WHITE, 40, 3)
    big_title(c, 'ถ่ายเอกซเรย์', W / 2, TITLE_Y - 30, t, 0.2, 88)
    captions(c, 4, t)

# ================================================================ 5 what's inside a tooth + germs invade
def scene5(c, t):
    k1, k2 = S(5, 1), S(5, 2)
    background(c, t, '#FFF1E8', '#FFF8EE')
    cx, cy, s = 540, 940, 1.38
    inv = seg(t, k1 + 0.2, k1 + 1.6)
    tooth_section(c, cx, cy, s, t, decay=lerp(0.25, 1.0, inv), inflam=seg(t, k1 + 1.0, k1 + 1.8),
                  pmood='smile' if t < k1 + 1.0 else 'squeeze')
    if t < k1:
        callout(c, 'เคลือบฟัน', 150, 560, cx - 175 * s, cy - 215 * s, t, 0.4, WHITE, INK, 38, -4)
        callout(c, 'เนื้อฟัน', 940, 610, cx + 150 * s, cy - 120 * s, t, 0.9, WHITE, INK, 38, 4)
        callout(c, 'โพรงประสาท', 170, 1090, cx - 60 * s, cy - 60 * s, t, 1.5, PINK, WHITE, 38, -3)
        callout(c, 'เส้นประสาท\n+ หลอดเลือด', 910, 1240, cx + 104 * s, cy + 130 * s, t, 2.2, YEL, INK, 34, 3)
    # germs sneak in through the cavity
    for i in range(3):
        g0 = k1 - 0.3 + i * 0.35
        if t < g0: continue
        k = ease_io(seg(t, g0, g0 + 1.6))
        gx = lerp(cx - 260 + i * 120, cx - 80 * s + i * 22, k)
        gy = lerp(cy - 520, cy - (140 - i * 30) * s, k)
        germ(c, gx, gy, 0.3, t, i + 3, GERM_COLS[i])
    if t >= k1 + 1.0:
        cue(t, k1 + 1.0, 'boing')
        zaps(c, cx + 230, cy - 260, t, seg(t, k1 + 1.0, k1 + 1.2), 3, 1.2)
    if t >= k2:
        hand_text(c, 'จี๊ด!', 220, 760, t, k2, 96, CORAL, -10)
        hand_text(c, 'ตุบ ตุบ', 880, 780, t, k2 + 0.6, 72, '#FF6B8A', 8)
    big_title(c, 'ข้างในฟันมีอะไร?', W / 2, TITLE_Y - 30, t, 0.2, 86)
    captions(c, 5, t)

# ================================================================ 6 the plan
def scene6(c, t):
    k1, k2 = S(6, 1), S(6, 2)
    room_back(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), P(WHITE, 90))
    # whiteboard on an easel
    bx, by, bw, bh = 735, 900, 590, 620
    for sx in (-1, 1):
        c.drawLine(bx + sx * 200, by + bh / 2 - 20, bx + sx * 250, 1420, P(INK, stroke=16)); c.drawLine(bx + sx * 200, by + bh / 2 - 20, bx + sx * 250, 1420, P('#C8A27A', stroke=9))
    c.drawRoundRect(RR(bx + 10, by + 14, bw + 30, bh + 30), 30, 30, P(INK, 70))
    c.drawRoundRect(RR(bx, by, bw + 30, bh + 30), 30, 30, P('#C8D7E8')); c.drawRoundRect(RR(bx, by, bw + 30, bh + 30), 30, 30, P(INK, stroke=8))
    c.drawRoundRect(RR(bx, by, bw, bh), 20, 20, P(WHITE))
    draw_img(c, text_img('แผนการรักษา', 54, TEAL, 6, INK), bx, by - 230)
    items = [('ทำความสะอาดคลองราก', MINT), ('อุดคลองราก', '#FFE3B3'), ('อุด / ครอบฟัน', '#FFD6E0')]
    for i, (txt, col) in enumerate(items):
        t0 = k1 + 0.3 + i * 0.7
        if t < t0: continue
        cue(t, t0, 'pop')
        yy = by - 110 + i * 130
        s_ = pop(t, t0, 0.4)
        c.save(); c.translate(bx, yy); c.scale(s_, s_)
        c.drawRoundRect(RR(0, 0, 520, 100), 30, 30, P(col)); c.drawRoundRect(RR(0, 0, 520, 100), 30, 30, P(INK, stroke=5))
        c.restore()
        num_badge(c, i + 1, bx - 225, yy, t, t0, YEL)
        draw_img(c, text_img(txt, 38, INK, 0), bx + 40, yy + 2, s_)
    if t >= k2:
        calendar_icon(c, bx - 150, by + 280, 0.62, t, 'นัด')
        label(c, 'อาจนัดหลายครั้ง', bx + 90, by + 280, t, k2 + 0.2, 40, CORAL, WHITE, rot=-3)
    point = ease_out(seg(t, k1, k1 + 0.4))
    doc(c, 215, 820, 0.74, t, FACE, right=(lerp(14, 105, point), 'pointer' if point > 0.5 else None))
    speech(c, 'ฟันซี่นี้ต้อง\nรักษารากฟันค่ะ', 300, 470, t, 0.3, 44, 'left')
    captions(c, 6, t)

# ================================================================ 7 step 1: numb, dam, open
CX, CY, SC = 540, 960, 1.2
def scene7(c, t):
    k1, k2 = S(7, 1), S(7, 2)
    background(c, t, '#E8FBFF', '#F3FFF6')
    acc = seg(t, k2 + 0.5, k2 + 2.2)
    tooth_section(c, CX, CY, SC, t, decay=1, inflam=1 - 0.6 * seg(t, 0.6, 1.4), dam=seg(t, k1, k1 + 0.8), access=acc,
                  numb=seg(t, 0.3, 0.8) * (1 - seg(t, k1 + 0.2, k1 + 0.8)), pmood='sleep' if t > 1.2 else 'squeeze')
    if t < k1:
        label(c, 'ยาชา', 220, 700, t, 0.4, 50, SKY, WHITE, rot=-6)
        zzz(c, 640, 860, t) if t > 1.2 else None
    if t >= k1:
        cue(t, k1, 'slide_down')
        callout(c, 'แผ่นยางกันน้ำลาย', 300, 1450, CX - 300 * SC, CY - 62 * SC, t, k1 + 0.5, DAM, INK, 38, -3)
    if k2 <= t < k2 + 2.6:
        cue(t, k2 + 0.4, 'drill')
        hk = ease_out(seg(t, k2, k2 + 0.5)) * (1 - ease_in(seg(t, k2 + 2.2, k2 + 2.6)))
        handpiece(c, CX - 20, lerp(300, CY - 250 * SC + 70 * acc, hk), 0.9, t, 1.0 if t > k2 + 0.4 else 0)
    if acc >= 1:
        label(c, 'เปิดทางเข้าโพรงประสาท', 760, 520, t, k2 + 2.2, 38, YEL, INK, rot=3)
    step_header(c, t, 1, 'เตรียมฟัน แล้วเปิดทาง')
    captions(c, 7, t)

# ================================================================ 8 step 2: clean + shape, medicine, temporary filling
def scene8(c, t):
    k1, k2 = S(8, 1), S(8, 2)
    background(c, t, '#E8FBFF', '#F3FFF6')
    pout = seg(t, 0.5, k1 + 0.4)
    clean = seg(t, k1 + 0.4, k2)
    tooth_section(c, CX, CY, SC, t, access=1, pulp_out=pout, clean=clean, dam=1, inflam=0.4 * (1 - pout),
                  bubbles=seg(t, k1, k1 + 0.4) * (1 - seg(t, k2 - 0.3, k2 + 0.2)),
                  med=seg(t, k2 + 0.2, k2 + 1.0), temp=seg(t, k2 + 1.2, k2 + 1.9), pmood='sleep')
    # files working up and down the two canals
    if 0.3 < t < k2 - 0.2:
        fa = seg(t, 0.3, 0.6) * (1 - seg(t, k2 - 0.6, k2 - 0.2))
        for j, (x0, y0, y1) in enumerate(CANALS):
            ph = 0.5 + 0.5 * math.sin(t * 5 + j * 1.7)
            ytip = CY + lerp(40, 290, ph) * SC
            endo_file(c, CX + x0 * SC, ytip, 0.85, FILE_COLS[(j + int(t * 0.8)) % 4], 255 * fa)
        cue(t, 0.4, 'scrub')
    # germs washed out of the opening
    if k1 + 0.2 <= t < k2 + 0.6:
        for i in range(4):
            g0 = k1 + 0.3 + i * 0.5
            if t < g0: continue
            ph = seg(t, g0, g0 + 1.3)
            if ph >= 1:
                continue
            gx = CX + (-120 + i * 80) * (0.3 + ph)
            gy = lerp(CY - 100 * SC, CY - 520 * SC, ease_out(ph))
            germ(c, gx, gy, 0.26 * (1 - 0.4 * ph), t, i + 7, GERM_COLS[i % 3])
            if ph > 0.8: puff(c, gx, gy, (ph - 0.8) * 5, 6, 60)
        label(c, 'ล้างเชื้อโรคออก', 830, 1360, t, k1 + 0.5, 40, SKY, WHITE, rot=3)
    if t < k1:
        label(c, 'ขยายคลองราก', 250, 1400, t, 0.8, 40, YEL, INK, rot=-3)
    if t >= k2 + 1.2:
        cue(t, k2 + 1.2, 'thud')
        label(c, 'อุดชั่วคราว', 250, 1400, t, k2 + 1.6, 40, '#EDEBFF', INK, rot=-3)
        calendar_icon(c, 900, 1330, 0.6, t, 'นัด')
    if k2 + 0.2 <= t < k2 + 1.6:
        label(c, 'ใส่ยาในคลองราก', 800, 1400, t, k2 + 0.3, 40, LAV, INK, rot=3)
    step_header(c, t, 2, 'ทำความสะอาดคลองราก')
    captions(c, 8, t)

# ================================================================ 9 step 3: fill the canals, seal
def scene9(c, t):
    k1, k2 = S(9, 1), S(9, 2)
    background(c, t, '#E8FBFF', '#F3FFF6')
    fl = seg(t, k1 + 0.4, k1 + 2.2)
    tooth_section(c, CX, CY, SC, t, access=1, pulp_out=1, clean=1, dam=1, temp=1 - seg(t, 0.2, 0.7),
                  fill=fl, core=seg(t, k2 - 0.2, k2 + 0.4), tmood='happy' if fl >= 1 else None)
    if t < 1.2:
        sparkle(c, CX, CY - 200 * SC, 30 * math.sin(math.pi * seg(t, 0.2, 1.2)), WHITE)
        label(c, 'สะอาดแล้ว!', 780, 640, t, 0.5, 42, MINT, INK, rot=4)
    if k1 - 0.6 <= t < k1 + 0.9:
        a = 255 * (1 - seg(t, k1 + 0.5, k1 + 0.9))
        dn = ease_out(seg(t, k1 - 0.6, k1 + 0.3))
        for x0, y0, y1 in CANALS:
            gp_cone(c, CX + x0 * SC, lerp(CY - 340 * SC, CY + (y1 - 20) * SC, dn), 1.0, a)
    if t >= k1 + 0.4:
        cue(t, k1 + 0.4, 'slide_down')
        callout(c, 'อุดแน่นตลอดราก', 860, 1300, CX + 106 * SC, CY + 200 * SC, t, k1 + 0.8, '#FFD9C2', INK, 38, 3)
    if t >= k2:
        # a germ tries to get back in and bounces off the seal
        u = t - k2
        bounce = abs(math.sin(min(u, 1.6) * 3.4)) * (1 - seg(u, 0.3, 1.6))
        gy = lerp(380, CY - 330 * SC, min(1, u / 0.35)) - 160 * bounce
        germ(c, CX + 60 + u * 140, gy, 0.3, t, 5, GERM_COLS[1], 'worry')
        if u > 0.35:
            cue(t, k2 + 0.35, 'boing')
            c.drawCircle(CX, CY - 260 * SC, 150 + 10 * math.sin(t * 6), P(MINT, 120 * seg(u, 0.3, 0.5), stroke=12))
        label(c, 'เชื้อกลับเข้าไม่ได้!', 300, 600, t, k2 + 0.5, 42, TEAL, WHITE, rot=-4)
    step_header(c, t, 3, 'อุดคลองรากให้แน่น')
    captions(c, 9, t)

# ================================================================ 10 after: (1) restore / crown  (2) post
def scene10(c, t):
    k1, k2 = S(10, 1), S(10, 2)
    background(c, t, '#FFF6D9', '#FFE9F0')
    if t < k1:
        confetti(c, t)
        k = pop(t, 0.3, 0.5) * (1 - seg(t, k1 - 0.3, k1))
        if k > 0:
            c.save(); c.translate(540, 1060); c.scale(k, k); c.translate(-540, -1060)
            tooth_section(c, 540, 1080, 0.95, t, access=1, pulp_out=1, fill=1, core=1, tmood='happy')
            c.restore()
            for i in range(5): sparkle(c, 300 + i * 120, 700 + (i % 2) * 60, 18 + 6 * math.sin(t * 5 + i), YEL, 255 * k)
    for j, (x, t0, txt, col) in enumerate(((282, k1, 'อุด หรือ ครอบฟัน', MINT), (798, k2, 'เดือยฟัน + ครอบ', '#FFD6E0'))):
        s_ = card(c, x, 1060, 480, 700, t, t0, WHITE)
        if s_ <= 0: continue
        c.save(); c.translate(x, 1080); c.scale(s_, s_); c.translate(-x, -1080)
        c.save(); c.clipRect(RR(x, 1060, 460, 680))
        if j == 0:
            tooth_section(c, x, 1130, 0.62, t, access=1, pulp_out=1, fill=1, core=1, crown=seg(t, t0 + 0.6, t0 + 1.4),
                          tmood='happy')
        else:
            tooth_section(c, x, 1130, 0.62, t, access=1, pulp_out=1, fill=1, post=seg(t, t0 + 0.4, t0 + 1.1),
                          core=seg(t, t0 + 1.1, t0 + 1.5), crown=seg(t, t0 + 1.6, t0 + 2.3), tmood='happy' if t > t0 + 2.3 else None)
        c.restore()
        c.restore()
        num_badge(c, j + 1, x - 190, 735, t, t0 + 0.1, YEL)
        label(c, txt, x, 1370, t, t0 + 0.3, 38, col, INK)
        cue(t, t0 + 1.4 if j == 0 else t0 + 2.3, 'sparkle')
    big_title(c, 'รักษารากเสร็จ', W / 2, TITLE_Y - 40, t, 0.2, 86)
    big_title(c, 'ยังไม่จบนะ!', W / 2, TITLE_Y + 70, t, 0.5, 76, YEL)
    if t >= k1:
        label(c, 'ฟันหลังรักษารากอาจเปราะ', W / 2, 1470, t, k1 + 1.0, 36, CORAL, WHITE, rot=-2) if t < k2 else None
    captions(c, 10, t)

# ================================================================ 11 after: (3) no hard food  (4) follow-up + care
def scene11(c, t):
    k1, k2 = S(11, 1), S(11, 2)
    background(c, t, '#E3FFF5', '#FFF4E6')
    rows = [(650, 0.3, '#FFF0F3'), (960, k1, '#EAF6FF'), (1275, k2, '#F1FFE9')]
    for i, (y, t0, col) in enumerate(rows):
        if card(c, 540, y, 960, 270, t, t0, col) <= 0: continue
        if i < 2: num_badge(c, i + 3, 95, y - 120, t, t0 + 0.1, YEL)
        if i == 0:
            ice_cube(c, 200, y, 0.75, -8)
            c.drawCircle(330, y + 10, 52, P('#C98A45')); c.drawCircle(330, y + 10, 52, P(INK, stroke=6))
            for a in range(5): c.drawCircle(330 + math.cos(a * 1.3) * 26, y + 10 + math.sin(a * 1.3) * 22, 6, P('#7A4A2B'))
            no_sign(c, 265, y, 115, 255 * seg(t, t0 + 0.5, t0 + 0.8))
            draw_img(c, text_img('เลี่ยงเคี้ยวของแข็ง\nด้วยฟันซี่นั้น', 42, INK, 0), 680, y, pop(t, t0 + 0.3))
            cue(t, t0 + 0.5, 'thud')
        elif i == 1:
            calendar_icon(c, 200, y + 10, 0.7, t, 'นัด')
            xray_card(c, 380, y + 10, 0.85, t)
            draw_img(c, text_img('มาตามนัด\nเอกซเรย์ติดตามผล', 42, INK, 0), 720, y, pop(t, t0 + 0.3))
        else:
            toothbrush(c, 230, y - 20, -20, 0.62)
            floss(c, 380, y + 40, 0.75, t)
            bubbles(c, 170, y - 40, t, 6)
            draw_img(c, text_img('แปรงฟัน ใช้ไหมขัดฟัน\nตรวจฟันทุก 6 เดือน', 42, INK, 0), 700, y, pop(t, t0 + 0.3))
    big_title(c, 'ดูแลต่อให้ดีนะ', W / 2, TITLE_Y - 20, t, 0.2, 86)
    captions(c, 11, t)

# ================================================================ 12 untreated: dies, darkens, abscess, swelling
def scene12(c, t):
    k1, k2, k3 = S(12, 1), S(12, 2), S(12, 3)
    background(c, t, '#EEE8FF', '#FFEFF2')
    dead = seg(t, k1, k1 + 1.0)
    ab = seg(t, k2 + 0.2, k2 + 1.4)
    cy = 1000
    tooth_section(c, CX, cy, SC, t, decay=1, inflam=1 - dead, dead=dead, abscess=ab, boneloss=0.35 * ab,
                  pmood='squeeze' if dead < 0.5 else 'sad')
    if ab > 0:   # swollen gum bump + germs around the root tip
        r = 60 * ease_out(ab)
        c.drawCircle(CX - 255 * SC, cy - 80 * SC, r + 4 * math.sin(t * 5), P('#FF8FAB')); c.drawCircle(CX - 255 * SC, cy - 80 * SC, r + 4 * math.sin(t * 5), P(INK, stroke=6))
        for i in range(3):
            germ(c, CX - 108 * SC + math.cos(t * 1.5 + i * 2.1) * 120, cy + 352 * SC + math.sin(t * 1.5 + i * 2.1) * 60, 0.22, t, i + 11, GERM_COLS[i])
        callout(c, 'ฝีปลายราก', 880, 1380, CX - 60 * SC, cy + 352 * SC, t, k2 + 0.6, '#D6B4FF', INK, 40, 3)
        callout(c, 'เหงือกบวม', 150, 1180, CX - 255 * SC, cy - 60 * SC, t, k2 + 1.2, PINK, WHITE, 38, -3)
    if t >= k1:
        cue(t, k1, 'sad')
        callout(c, 'ฟันตาย สีคล้ำ', 870, 640, CX + 150 * SC, cy - 180 * SC, t, k1 + 0.4, '#B7AAB4', WHITE, 40, 3)
    if t >= k3:
        label(c, 'หายปวด ไม่ได้แปลว่าหาย!', W / 2, 520, t, k3, 56, CORAL, WHITE, rot=-3)
    big_title(c, 'ถ้าไม่รักษาล่ะ?', W / 2, TITLE_Y - 30, t, 0.2, 96, shake=seg(t, 0.2, 0.8))
    captions(c, 12, t)

# ================================================================ 13 untreated: bone loss -> extraction -> neighbours tilt
def dull_tooth(c, x, y, s, t, rot=0, mood='sad'):
    tooth(c, x, y, s, mood, rot, t=t, seed=3)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawPath(TOOTH, P('#8C7F8A', 110)); c.restore()

def scene13(c, t):
    k1, k2 = S(13, 1), S(13, 2)
    background(c, t, '#EEE8FF', '#FFF4EA')
    if t < k1:
        tooth_section(c, CX, 1000, SC, t, decay=1, dead=1, abscess=1, boneloss=lerp(0.35, 1.0, seg(t, 0.3, 2.0)), pmood='sad')
        callout(c, 'กระดูกรอบรากถูกทำลาย', 330, 1440, CX - 108 * SC, 1000 + 370 * SC, t, 0.6, BONED, INK, 38, -3)
    else:
        u = t - k1
        c.drawRect(skia.Rect.MakeWH(W, H), P(WHITE, 255 * (1 - seg(u, 0, 0.3))))
        gy = 1180
        tilt = ease_io(seg(t, k2 + 0.2, k2 + 1.4))
        out = ease_in(seg(u, 0.5, 1.4))
        xs = [170, 400, 650, 880]
        for i, x in enumerate(xs):
            if i == 2:
                if out < 1:
                    dull_tooth(c, x, gy - 120 - 950 * out, 1.0, t, 25 * out)
                continue
            rot = 0
            if i == 1: rot, x = 16 * tilt, x + 40 * tilt
            if i == 3: rot, x = -16 * tilt, x - 40 * tilt
            tooth(c, x, gy - 120, 1.0, 'worry' if tilt > 0.3 else 'smile', rot, t=t, seed=i)
        gum = skia.Path(); gum.addRoundRect(skia.Rect.MakeLTRB(-40, gy - 10, W + 40, 1500), 60, 60)
        c.drawPath(gum, lingrad((0, gy), (0, 1500), GUM, '#F48FA8')); c.drawPath(gum, P(INK, stroke=8))
        if out > 0:
            c.drawOval(RR(650, gy + 20, 130 * min(1, out * 2), 40 * min(1, out * 2)), P('#C9566F'))
            cue(t, k1 + 0.5, 'boing')
            puff(c, 650, gy - 40, seg(u, 0.5, 1.2), 8, 160)
        label(c, 'ต้องถอนฟัน', 650, 560, t, k1 + 0.4, 50, CORAL, WHITE, rot=-3)
        if t >= k2:
            cue(t, k2 + 0.2, 'slide_down')
            label(c, 'ฟันข้างๆ ล้มเอียง', 540, 1380, t, k2 + 0.8, 44, YEL, INK, rot=2)
            if t > k2 + 1.6: hand_text(c, 'เคี้ยวลำบาก...', 540, 780, t, k2 + 1.6, 60, '#7C6FB0', -4)
    big_title(c, 'ปล่อยไว้นาน...', W / 2, TITLE_Y - 30, t, 0.2, 92)
    captions(c, 13, t)

# ================================================================ 14 payoff
def scene14(c, t):
    k1, k2 = S(14, 1), S(14, 2)
    background(c, t, '#FFF1D6', '#E3FFF5')
    cue(t, 0.3, 'fanfare')
    burst(c, 540, 900, t, 18, 150, 1200, YEL, 60, 8)
    confetti(c, t)
    chew = 0.3 + 0.3 * math.sin(t * 8)
    person(c, 360, 900, 1.0, 'happy', chew if t < k1 else 0, t, shirt=SHIRT)
    doc(c, 820, 830, 0.66, t, FACE, right=('wave', None))
    for i in range(4): heart(c, 160 + i * 250, 640 + (i % 2) * 50, 22, PINK)
    label(c, 'เก็บฟันธรรมชาติไว้ได้', W / 2, 520, t, 0.5, 52, TEAL, WHITE, rot=-2) if t < k2 else \
        label(c, 'อย่ารอนะคะ!', W / 2, 520, t, k2, 64, CORAL, WHITE, rot=-3)
    big_title(c, 'ยิ้มได้ เคี้ยวสบาย!', W / 2, TITLE_Y - 30, t, 0.2, 88)
    captions(c, 14, t)

# ================================================================ banner on every story scene + end card
def with_banner(fn):
    def draw(c, t):
        fn(c, t); clinic_banner(c)
    return draw

END = endcard('ปวดฟันจี๊ด ปรึกษาหมอได้เลย!')
STORY = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12, scene13, scene14]
EXTRA = {7: 1.6, 8: 1.4, 9: 1.2, 10: 1.6, 13: 1.4}
SCENES = [Scene(scene0, 1.8)] + [Scene(with_banner(f), L(i + 1, EXTRA.get(i + 1, 1.0))) for i, f in enumerate(STORY)] + \
    [Scene(END, max(6.5, L(15, 2.0)))]

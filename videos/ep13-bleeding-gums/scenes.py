"""ep13 เหงือกเลือดออก หยุดแปรงดีไหม? — long 16:9 kawaii episode (house format since 2026-10-22, like ep11).
สมจี๊ด spits pink foam and decides to skip brushing there -> a week later the gum is redder -> หมอนวรัตน์ flies in:
bleeding = a warning sign of gingivitis, plaque along the gum line, healthy vs inflamed gum, the vicious circle,
plaque -> tartar, what happens if it is left (periodontitis), it is often painless, risk factors, self-check ->
a myth-or-fact round (5) -> five habits (soft brush 2-2-2, 45 degrees at the gum line, floss, check-ups + scaling,
no smoking/less sugar) with a viewer quiz -> recap -> happy ending.
Scene lengths come from durations.json (the measured narration clips) when present."""
import sys, os, json, re, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOTDIR = os.path.join(HERE, '..', '..')
sys.path.insert(0, ROOTDIR); sys.path.insert(0, HERE); sys.path.append(os.path.join(ROOTDIR, 'videos', 'ep6-root-canal'))
from tools.kawaii import *  # noqa: F401,F403
from chars import person    # สมจี๊ด (ep6)
from props import *          # noqa: F401,F403
from script import NARR

SHIRT = '#FF9EBB'

# ---------------------------------------------------------------- helpers
def caps(c, t, D, lines, y=SUB_Y, size=50, bg=WHITE, fg=INK, start=0.5):
    n = len(lines)
    span = max(1.0, D - start - 0.6)
    for i, txt in enumerate(lines):
        a = start + span * i / n
        b = start + span * (i + 1) / n if i < n - 1 else 999
        subtitle(c, txt, t, a, b, y, size, bg, fg)

def mouth_pt(x, y, s, t): return x, y + math.sin(t * 3) * 6 + 66 * s

def step_hdr(c, t, n, line):
    step_badge(c, n, 300, TITLE_Y, t, 0.2)
    big_title(c, line, W / 2 + 140, TITLE_Y, t, 0.45, 84)

def flying_in(c, t, x, y, s, t0=0.0, t1=1.2, mood='hero', point=0.0, hold=None, wave=0.0, from_x=W + 500, from_y=-300):
    k = ease_out(seg(t, t0, t1))
    xx, yy = lerp(from_x, x, k), lerp(from_y, y, k)
    if t < t1:
        for i in range(4):
            c.drawLine(xx + 260 + i * 60, yy + 100 + i * 70, xx + 520 + i * 60, yy - 40 + i * 70, P(WHITE, 200, stroke=10))
    dr_nawarat(c, xx, yy, s, t, mood, wave=wave, point=point, cape=1, hold=hold)
    return xx, yy

def brushing(c, x, y, s, t, on=True):
    """toothbrush scrubbing at the person's mouth"""
    mx, my = mouth_pt(x, y, s, t)
    dx = math.sin(t * 14) * 30 * s if on else 0
    toothbrush(c, mx + 150 * s + dx, my + 10 * s, -8, 0.75 * s / 0.7)
    if on: bubbles(c, mx + 40 * s, my, t, 5)

# ================================================================ cover
def cast_cover(c, t):
    k = pop(t, 0.3)
    if k > 0:
        gum_closeup(c, 420, 760, 1.0 * k, t, inflam=0.75, bleed=0.6, mood='worry')
        sweat(c, 560, 470, 1.2 * k)
    soft_brush(c, 760, 560, -60, 0.8 * pop(t, 0.6))
    dr_nawarat(c, 1560, 470, 0.72 * pop(t, 0.5), t, 'happy', wave=1.0)
    if t > 0.8: magnifier(c, 1330, 760, 0.7 * pop(t, 0.8), -25, 0.5 + 0.5 * math.sin(t * 4))
COVER = cover('เหงือกเลือดออก!', 'หยุดแปรงตรงนั้นดีไหม?', 'ตอนที่ 13', top='#FFE4EC', bot='#FFC7D6', cast=cast_cover)

# ================================================================ story
def s1(c, t, D):   # morning brushing, pink foam
    bathroom(c, t)
    wall_mirror(c, 1300, 420)
    sink(c, 1300, 760, 1.0)
    x, y, s = 640, 430, 0.7
    shock = t > 4.6
    person(c, x, y, s, 'worry' if shock else ('smile' if t < 3.2 else 'happy'), 0.0 if t < 3.2 else 0.4 * (1 - seg(t, 4.2, 4.6)), t, shirt=SHIRT)
    if t < 3.2: brushing(c, x, y, s, t); cue(t, 0.6, 'scrub')
    # reflection in the mirror (small)
    c.save(); pth = skia.Path(); pth.addRoundRect(RR(1300, 420, 400, 320), 56, 56); c.clipPath(pth, doAntiAlias=True)
    person(c, 1300, 420, 0.42, 'worry' if shock else 'smile', 0, t, shirt=SHIRT, seed=2); c.restore()
    if t > 3.4:
        k = ease_out(seg(t, 3.4, 4.2))
        foam(c, lerp(760, 1300, k), lerp(520, 790, k), 0.6 + 0.2 * k, t, seg(t, 4.2, 4.8))
        cue(t, 3.5, 'slide_down', 0.3)
    if shock:
        sweat(c, x - 190, y - 80, 1.1, 255 * seg(t, 4.7, 5.0))
        hand_text(c, 'อุ๊ย!', x - 300, y - 170, t, 4.7, 96, CORAL, -10)
        hand_text(c, 'ฟองสีชมพู?!', 1300, 640, t, 5.2, 58, BLOODPINK, 6)
        cue(t, 4.7, 'thud')
    big_title(c, 'แปรงฟันตอนเช้า', W / 2, TITLE_Y, t, 0.3, 96, YEL)
    caps(c, t, D, ['ถูไปถูมา แล้วบ้วน...', 'เหงือกเลือดออก!'])

def s2(c, t, D):   # the question
    background(c, t, '#FFF3B0', '#FFE1EA')
    gum_closeup(c, 960, 800, 1.05, t, inflam=0.6 * seg(t, 0.5, 2.0), bleed=seg(t, 1.5, 2.5), mood='worry' if t > 1.5 else 'smile')
    soft_brush(c, 1400, 560, -30, 1.1)
    big_title(c, 'เหงือกเลือดออก', W / 2, TITLE_Y, t, 0.3, 104, WHITE, shake=12)
    label(c, 'หยุดแปรงตรงนั้นดีไหม?', W / 2, 300, t, 1.4, 60, CORAL, WHITE, rot=-2)
    for i, (qx, qy) in enumerate(((420, 520), (1500, 330))):
        hand_text(c, '?', qx, qy + math.sin(t * 4 + i) * 10, t, 2.0 + i * 0.3, 130, CORAL, (-1) ** i * 12)
    caps(c, t, D, ['เคยเป็นแบบนี้ไหมคะ?', 'มาหาคำตอบกัน!'])

def s3(c, t, D):   # she skips that spot, germs cheer
    bathroom(c, t)
    x, y, s = 480, 430, 0.7
    person(c, x, y, s, 'smile', 0, t, shirt=SHIRT)
    brushing(c, x, y, s, t)
    cue(t, 0.4, 'scrub')
    # thought bubble: tooth row with one spot skipped
    k = pop(t, 0.8)
    if k > 0:
        c.save(); c.translate(1220, 520); c.scale(k, k)
        b = skia.Path(); b.addRoundRect(RR(0, 0, 980, 560), 120, 120); fillp(c, b, WHITE)
        c.restore()
        for i, cx in enumerate((900, 1000)):
            c.drawCircle(cx - 160 + i * 40, 760 + i * 30, 26 - i * 8, P(WHITE)); c.drawCircle(cx - 160 + i * 40, 760 + i * 30, 26 - i * 8, P(INK, stroke=5))
        if k > 0.9:
            for i in range(5):
                tooth(c, 900 + i * 160, 540, 0.5, 'worry' if i == 2 else 'smile', 0, t=t, seed=i, shadow=False)
            g = skia.Path(); g.addRoundRect(skia.Rect.MakeLTRB(800, 590, 1640, 660), 30, 30); fillp(c, g, GUM, stroke=6)
            c.drawCircle(1220, 600, 40, P(GUM_RED, 220))
            ph = ((t - 1.4) / 1.6) % 1
            bx = lerp(820, 1620, ph)
            if abs(bx - 1220) > 110: soft_brush(c, bx + 40, 400, 0, 0.55)
            else: hand_text(c, 'ข้าม!', 1220, 380, t, 0, 54, CORAL)
    if t > 3.5:
        for i in range(3):
            gx = 1100 + i * 120
            germ(c, gx, 720 - 40 * abs(math.sin(t * 5 + i)), 0.3 * pop(t, 3.5 + i * 0.2), t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i], mood='joy')
        hand_text(c, 'เย้!', 1500, 700, t, 3.9, 64, GREEN_D, 8); cue(t, 3.9, 'boing')
    big_title(c, 'ไม่แปรงตรงนั้นดีกว่า...', W / 2, TITLE_Y, t, 0.3, 88)
    caps(c, t, D, ['ตรงไหนเลือดออก ก็แปรงข้ามไป', 'เชื้อโรคดีใจใหญ่!'])

def s4(c, t, D):   # one week later
    background(c, t, '#FFE7E7', '#FFF5F5')
    m = 1 + 6 * ease_io(seg(t, 0.4, 2.0))
    c.save(); c.translate(330, 520); c.rotate(-4)
    c.drawRoundRect(RR(8, 10, 260, 270), 26, 26, P(INK, 70)); c.drawRoundRect(RR(0, 0, 260, 270), 26, 26, P(WHITE))
    c.drawRoundRect(skia.Rect.MakeLTRB(-130, -135, 130, -65), 26, 26, P(CORAL)); c.drawRoundRect(RR(0, 0, 260, 270), 26, 26, P(INK, stroke=7))
    c.restore()
    draw_img(c, text_img('วันที่', 40, WHITE, 0), 330, 420, 1, 1, -4)
    draw_img(c, text_img(str(int(m)), 130, INK, 0), 330, 560, 1, 1, -4)
    cue(t, 0.4, 'tick')
    infl = 0.3 + 0.7 * ease_io(seg(t, 1.0, 4.0))
    gum_closeup(c, 960, 820, 1.05, t, inflam=infl, plaque=0.6 + 0.4 * seg(t, 1, 4), bleed=seg(t, 3.0, 4.5))
    if t > 3.0: hand_text(c, 'แดง + บวม!', 960, 300, t, 3.0, 64, CORAL, -4)
    if t > 4.5:
        breath_cloud(c, 1520, 520, 0.8 * pop(t, 4.5), t, 255, 'squeeze')
        label(c, 'กลิ่นปาก', 1520, 720, t, 4.7, 48, STINK_D, WHITE)
    big_title(c, 'ผ่านไป 1 สัปดาห์', W / 2, TITLE_Y, t, 0.2, 96, YEL)
    caps(c, t, D, ['ยิ่งแดง ยิ่งบวม เลือดออกง่าย', 'เริ่มมีกลิ่นปากด้วย'])

def s5(c, t, D):   # Dr. Nawarat flies in
    background(c, t, '#FFF3B0', '#FFD6A5')
    land = 1.3
    cue(t, 0.1, 'slide_down', 0.3); cue(t, land, 'thud', 0.7); cue(t, land + 0.1, 'fanfare')
    if t > land: burst(c, 1180, 560, t, 18, 120, 1500 * ease_out(seg(t, land, land + 0.6)), WHITE, 110)
    flying_in(c, t, 1180, 330, 0.75, 0, land, 'hero' if t < 3 else 'happy', wave=seg(t, land, land + 0.4))
    puff(c, 1180, 790, seg(t, land, land + 0.8), 9, 300)
    if t > land:
        magnifier(c, 900, 760, 0.6 * pop(t, land + 0.3), -20, 0.5 + 0.5 * math.sin(t * 5))
    big_title(c, 'มุมความรู้', 520, 330, t, land + 0.2, 100, YEL, rot=-4, shake=10)
    big_title(c, 'กับหมอนวรัตน์', 520, 470, t, land + 0.6, 92)
    label(c, 'ภารกิจ: ทำไมเหงือกเลือดออก?', 480, 640, t, land + 1.6, 46, CORAL, WHITE, rot=-2)
    caps(c, t, D, ['ไม่ต้องห่วงนะคะ!', 'ไปสืบหาสาเหตุกันค่ะ'], start=land + 1.0)

def s6(c, t, D):   # warning sign
    background(c, t, '#FFF1E6', '#FFE1EA')
    gum_closeup(c, 640, 820, 1.0, t, inflam=0.7, bleed=0.8)
    alarm_bell(c, 640, 340, 0.9 * pop(t, 0.6), t, 1 - seg(t, 4, 5))
    cue(t, 0.7, 'ding')
    dr_nawarat(c, 1560, 380, 0.6, t, 'smile', point=0.7)
    big_title(c, 'สัญญาณเตือน!', W / 2, TITLE_Y, t, 0.3, 100, YEL, shake=10)
    label(c, 'ส่วนใหญ่มักเป็น', 1150, 520, t, 2.4, 46, WHITE, INK, font=FONT_M)
    label(c, 'เหงือกอักเสบ', 1150, 640, t, 3.0, 64, CORAL, WHITE, rot=-3)
    caps(c, t, D, ['เลือดออกเวลาแปรงฟัน = เหงือกส่งสัญญาณ'], start=D * 0.45)

def s7(c, t, D):   # plaque along the gum line
    background(c, t, '#FFFBE0', '#FFF3C4')
    pl = ease_io(seg(t, 0.6, 3.0))
    gum_closeup(c, 700, 830, 1.1, t, inflam=0.2, plaque=pl, mood='worry' if pl > 0.5 else 'smile')
    magnifier(c, 700 + 120 * math.sin(t * 1.3), 760, 0.75, -25, seg(t, 3, 3.4))
    big_title(c, 'ตัวการ: คราบจุลินทรีย์', W / 2, TITLE_Y, t, 0.3, 88, YEL)
    label(c, 'คราบพลัค', 1400, 400, t, 1.2, 60, PLAQUE, INK)
    label(c, 'แผ่นเหนียวๆ', 1400, 530, t, 2.0, 46, WHITE, INK, font=FONT_M)
    label(c, 'เชื้อโรคเต็มไปหมด', 1400, 640, t, 2.8, 46, WHITE, INK, font=FONT_M)
    if t > 3.6:
        k = ease_out(seg(t, 3.6, 4.2))
        c.drawLine(1180, 760, lerp(1180, 900, k), lerp(760, 790, k), P(INK, stroke=7))
        label(c, 'ชอบเกาะขอบเหงือก', 1400, 770, t, 3.6, 48, CORAL, WHITE)
    caps(c, t, D, ['เกาะตามขอบเหงือก ทุกวัน'], start=D * 0.6)

def s8(c, t, D):   # gum fights back -> inflamed, bleeds easily
    background(c, t, '#FFE1EA', '#FFF5F8')
    infl = ease_io(seg(t, 1.0, 4.0))
    gum_closeup(c, 760, 830, 1.1, t, inflam=infl, plaque=1.0, bleed=seg(t, 5.0, 6.0))
    # little gum "defender" puffs
    if 1.0 < t < 4.5:
        for i in range(4):
            ph = ((t - 1.0) * 0.9 + i / 4) % 1
            c.drawCircle(600 + i * 100, 790 - ph * 200, 14, P(CORAL, 220 * (1 - ph)))
        hand_text(c, 'สู้!', 520, 560, t, 1.1, 70, CORAL, -10); cue(t, 1.1, 'boing')
    label(c, 'อักเสบ', 1450, 380, t, 2.0, 56, CORAL, WHITE)
    label(c, 'แดง + บวม', 1450, 500, t, 3.0, 56, GUM_RED, WHITE)
    label(c, 'เส้นเลือดเล็กๆ เปราะ', 1450, 620, t, 4.0, 46, WHITE, INK, font=FONT_M)
    if t > 5.0:
        soft_brush(c, lerp(1100, 900, ease_out(seg(t, 5.0, 5.5))), 690, -10, 0.7)
        cue(t, 5.4, 'pop')
    big_title(c, 'เหงือกสู้กับเชื้อโรค', W / 2, TITLE_Y, t, 0.3, 88, YEL)
    caps(c, t, D, ['แปรงโดนนิดเดียว ก็มีเลือดออก'], start=D * 0.6)

def s9(c, t, D):   # healthy vs inflamed
    background(c, t, '#E4FDE1', '#FFE1EA')
    big_title(c, 'มาเทียบกัน!', W / 2, TITLE_Y, t, 0.2, 100, YEL)
    for j, (x, infl, name, col, t0) in enumerate(((520, 0.0, 'เหงือกแข็งแรง', GREEN, 0.8), (1400, 0.9, 'เหงือกอักเสบ', CORAL, 3.6))):
        s = card(c, x, 600, 760, 640, t, t0, WHITE)
        if s <= 0: continue
        c.save(); c.translate(x, 600); c.scale(s, s); c.translate(-x, -600)
        c.save(); clip = skia.Path(); clip.addRoundRect(RR(x, 600, 750, 630), 38, 38); c.clipPath(clip, doAntiAlias=True)
        gum_closeup(c, x, 700, 0.85, t, inflam=infl, bleed=0.8 * infl)
        c.restore(); c.restore()
        label(c, name, x, 340, t, t0 + 0.2, 54, col, WHITE if j else INK)
    for i, txt in enumerate(('ชมพู', 'แน่น', 'ไม่มีเลือด')):
        label(c, txt, 300 + i * 220, 860, t, 1.6 + i * 0.5, 40, MINT, INK, padx=24, pady=14)
    for i, txt in enumerate(('แดง', 'บวม', 'เลือดออกง่าย')):
        label(c, txt, 1180 + i * 220, 860, t, 4.4 + i * 0.5, 40, '#FFD6E0', INK, padx=24, pady=14)
    cue(t, 1.2, 'ding'); cue(t, 4.0, 'boing')

def s10(c, t, D):   # vicious circle
    background(c, t, '#E2ECFF', '#F4F0FF')
    big_title(c, 'หยุดแปรง = ยิ่งแย่!', W / 2, TITLE_Y, t, 0.2, 96, YEL, shake=8)
    cycle(c, 1180, 600, 260, t, 0.8, ['คราบสะสม', 'ยิ่งอักเสบ', 'เลือดยิ่งออก'], [PLAQUE, CORAL, '#FFD6E0'])
    soft_brush(c, 330, 560, -20, 1.0)
    cross(c, 360, 520, 2.2 * pop(t, 0.5))
    cue(t, 0.5, 'boing')
    for i in range(int(1 + 4 * seg(t, 1.5, 4.5))):
        rr = random.Random(30 + i)
        germ(c, rr.uniform(200, 560), rr.uniform(700, 860), 0.28, t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i % 3], mood='joy')
    caps(c, t, D, ['วนเป็นวงกลม ไม่จบ!'], start=D * 0.6)

def s11(c, t, D):   # plaque -> tartar
    background(c, t, '#FFF1E6', '#FFF8EE')
    hard = ease_io(seg(t, 1.0, 3.5))
    gum_closeup(c, 640, 830, 1.1, t, inflam=0.4, plaque=1 - hard, tartar=hard, mood='worry' if hard > 0.5 else 'smile')
    if 1.0 < t < 3.5:
        hand_text(c, 'แข็งตัว...', 640, 330, t, 1.2, 60, BROWN, -6); cue(t, 1.2, 'tick')
    label(c, 'คราบ', 1250, 400, t, 0.6, 54, PLAQUE, INK)
    k = ease_out(seg(t, 1.0, 1.6))
    if k > 0:
        c.drawLine(1250, 470, 1250, lerp(470, 560, k), P(INK, stroke=10))
    label(c, 'หินปูน', 1250, 620, t, 2.6, 64, TARTAR, INK)
    if t > 4.0:
        x = lerp(1050, 820, ease_out(seg(t, 4.0, 4.6)))
        toothbrush(c, x, 640 + math.sin(t * 14) * 10, -10, 0.7)
        cross(c, 900, 520, 1.4 * pop(t, 4.8)); cue(t, 4.8, 'boing')
        hand_text(c, 'แปรงไม่ออก!', 1000, 450, t, 4.9, 54, CORAL, 6)
    if t > 6.0:
        dr_nawarat(c, 1620, 400, 0.5 * pop(t, 6.0), t, 'smile', cape=0)
        scaler(c, 1450, 700, 0.8 * pop(t, 6.3), -30)
        label(c, 'หมอฟันช่วยขูดออก', 1560, 900, t, 6.4, 44, TEAL, WHITE)
    big_title(c, 'คราบ กลายเป็นหินปูน', W / 2, TITLE_Y, t, 0.3, 100, YEL)

def s12(c, t, D):   # periodontitis: gum recedes, bone lost, tooth loose
    background(c, t, '#FFE1EA', '#FFF5F8')
    dip = 150 * ease_io(seg(t, 1.0, 4.5))
    bone_gum(c, GUM_TOP, dip=dip, gapx=W / 2, gapw=300, t=t)
    cut_neighbors(c, t, ('worry', 'worry'))
    wob = seg(t, 4.0, 4.5)
    rot = math.sin(t * 10) * 7 * wob
    tooth(c, W / 2, GUM_TOP - 115 + dip * 0.4, 1.6, 'sad' if t > 3 else 'worry', rot, t=t, seed=7, shadow=False)
    if t > 4.0:
        motion_lines(c, W / 2 - 230, 520, 120, 200)
        hand_text(c, 'โยก!', W / 2 + 260, 440, t, 4.2, 70, CORAL, 8); cue(t, 4.2, 'boing')
    label(c, 'เหงือกร่น', 330, 380, t, 1.5, 48, GUM_RED, WHITE)
    label(c, 'กระดูกถูกทำลาย', 330, 500, t, 2.6, 44, BONED, INK)
    label(c, 'อาจสูญเสียฟัน', 1600, 380, t, 5.5, 48, CORAL, WHITE)
    big_title(c, 'ถ้าปล่อยไว้...', W / 2, TITLE_Y, t, 0.2, 96, WHITE, shake=8)
    caps(c, t, D, ['โรคปริทันต์อักเสบ'], y=SUB_Y, bg=YEL, start=1.0)

def s13(c, t, D):   # silent, painless
    background(c, t, '#3D4A8F', '#7B86C9', dots=False)
    for i in range(12):
        rr = random.Random(700 + i)
        sparkle(c, rr.uniform(40, W - 40), rr.uniform(60, 700), 10 + 6 * math.sin(t * 3 + i), WHITE, 200)
    gum_closeup(c, 600, 850, 0.95, t, inflam=0.6 + 0.3 * seg(t, 1, 5), plaque=0.8, mood='smile')
    gx = lerp(1700, 1200, ease_out(seg(t, 0.6, 3.0)))
    germ(c, gx, 620, 1.7, t, seed=3, col='#B58CFF', mood='happy')
    ninja_band(c, gx, 620 - 6 * 1.7, 1.7, t)
    if t > 1.0:
        draw_img(c, text_img('ย่อง~ ย่อง~', 60, WHITE, 6, INK), gx, 400, 1, 1, -4)
    label(c, 'ไม่ค่อยเจ็บ', 1500, 820, t, 2.5, 54, WHITE, INK)
    big_title(c, 'โรคเหงือก มาแบบเงียบๆ', W / 2, TITLE_Y, t, 0.3, 88, YEL)
    caps(c, t, D, ['หลายคนไม่รู้ตัว จนอาการมากแล้ว'], start=D * 0.5)

def s14(c, t, D):   # risk factors
    background(c, t, '#E2ECFF', '#F4F0FF')
    big_title(c, 'ตัวเร่งเหงือกอักเสบ', W / 2, TITLE_Y, t, 0.2, 92, YEL)
    xs = [300, 740, 1180, 1620]
    names = ['สูบบุหรี่', 'แปรงแรงเกินไป', 'ช่วงตั้งครรภ์', 'โรคประจำตัว\nเช่น เบาหวาน']
    for i, x in enumerate(xs):
        t0 = 0.8 + i * 1.6
        s = card(c, x, 560, 400, 480, t, t0, WHITE)
        if s <= 0: continue
        c.save(); c.translate(x, 520); c.scale(s, s)
        if i == 0: cigarette_no(c, 0, 0, 0.9)
        elif i == 1:
            soft_brush(c, 60, 20, -20, 0.6, hard=True); motion_lines(c, -20, -60, 110, 220)
        elif i == 2:
            heart(c, -40, 0, 70, PINK); heart(c, 60, 40, 40, CORAL)
        else:
            cb = skia.Path(); cb.addRoundRect(RR(0, 0, 170, 210), 20, 20); fillp(c, cb, MINT)
            c.drawRect(RR(0, -30, 40, 110), P(CORAL)); c.drawRect(RR(0, -30, 110, 40), P(CORAL))
        c.restore()
        label(c, names[i], x, 770, t, t0 + 0.2, 40, CORAL if i != 2 else PINK, WHITE, padx=30, pady=18)
    caps(c, t, D, ['ยิ่งต้องดูแลเหงือกให้ดีนะคะ'], start=D * 0.65)

def s15(c, t, D):   # self check
    background(c, t, '#FFE1EA', '#FFF5F8')
    person(c, 480, 440, 0.7, 'happy', 0.2, t, shirt=SHIRT)
    hand_mirror(c, 1000, 520, 1.2, 8, t)
    c.save(); p = skia.Path(); p.addOval(RR(1000, 520, 230, 265)); c.clipPath(p, doAntiAlias=True)
    gum_closeup(c, 1000, 600, 0.55, t, inflam=0.7, bleed=0.5)
    c.restore()
    checks = ['เหงือกแดง?', 'บวม?', 'เลือดออกเวลาแปรง?', 'มีกลิ่นปาก?']
    for i, txt in enumerate(checks):
        t0 = 1.2 + i * 1.1
        s = pop(t, t0)
        if s > 0:
            y = 330 + i * 140
            c.save(); c.translate(1440, y); c.scale(s, s)
            c.drawRoundRect(RR(-180, 0, 60, 60), 14, 14, P(WHITE)); c.drawRoundRect(RR(-180, 0, 60, 60), 14, 14, P(INK, stroke=6))
            c.restore()
            check(c, 1440 - 180, y, 0.9 * s, CORAL)
            label(c, txt, 1560, y, t, t0, 44, WHITE, INK, font=FONT_M)
            cue(t, t0, 'tick')
    big_title(c, 'เช็กเองง่ายๆ', W / 2, TITLE_Y, t, 0.3, 100, YEL)
    caps(c, t, D, ['ถ้ามี ต้องดูแลเหงือกเพิ่มแล้ว!'], start=D * 0.7)

def myth(n, statement, verdict, draw_icon, pills, t_verdict=0.45):
    def f(c, t, D):
        background(c, t, '#FFF3B0', '#FFD6E0')
        burst(c, W / 2, 560, t, 16, 150, 1300, WHITE, 60, 6)
        big_title(c, 'จริง หรือ ไม่จริง?', W / 2, TITLE_Y - 10, t, 0.2, 96, YEL, rot=-2)
        label(c, f'ข้อ {n}', 220, TITLE_Y - 10, t, 0.4, 52, TEAL, WHITE, rot=-8)
        s = card(c, 760, 560, 1060, 470, t, 0.6, WHITE)
        if s > 0:
            draw_img(c, text_img(statement, 58, INK, 0, INK, FONT_B, 14), 900, 560, s)
            c.save(); c.translate(380, 580); c.scale(s, s); draw_icon(c, t); c.restore()
        tv = max(2.5, D * t_verdict)
        if t > 1.5 and t < tv:
            for i in range(3):
                draw_img(c, text_img('?', 80, CORAL, 6, WHITE), 1450 + i * 110, 380 + math.sin(t * 6 + i) * 12, 1, 0.5 + 0.5 * math.sin(t * 4 + i))
        stamp(c, 1560, 600, verdict, t, tv, 1.0)
        if verdict and tv < t < tv + 2.5: confetti(c, t - tv)
        caps(c, t, D, pills, start=tv + 0.6)
    return f

def _icon_bleed(c, t):
    c.save(); c.scale(0.45, 0.45); gum_closeup(c, 0, 200, 1.0, t, inflam=0.7, bleed=0.8); c.restore()
def _icon_hard(c, t):
    soft_brush(c, 40, 0, -30, 0.7, hard=True); motion_lines(c, -40, -80, 100, 220)
def _icon_scale(c, t):
    c.save(); c.scale(0.5, 0.5); gum_closeup(c, 0, 200, 1.0, t, inflam=0.3, tartar=1.0, mood='smile'); c.restore()
    scaler(c, 110, -40, 0.6, -35)
def _icon_nopain(c, t):
    tooth(c, 0, 0, 0.9, 'smile', 0, t=t, seed=3)
    germ(c, 90, 90, 0.35, t, seed=1, col='#B58CFF', mood='happy')
def _icon_heal(c, t):
    c.save(); c.scale(0.45, 0.45); gum_closeup(c, 0, 200, 1.0, t, inflam=0.0, mood='joy'); c.restore()
    sparkle(c, 90, -110, 26 + 8 * math.sin(t * 5), YEL)

s16 = myth(1, 'เหงือกเลือดออก\nต้องหยุดแปรงตรงนั้น', False, _icon_bleed, ['ยิ่งต้องแปรงให้สะอาด', 'แต่แปรงเบาๆ นะคะ'], 0.5)
s17 = myth(2, 'แปรงขนแข็ง แปรงแรงๆ\nเหงือกจะแข็งแรง', False, _icon_hard, ['แปรงแรง เหงือกบาดเจ็บ และร่นได้', 'ใช้แปรงขนนุ่มดีกว่า'], 0.35)
s18 = myth(3, 'ขูดหินปูน\nทำให้ฟันห่าง', False, _icon_scale, ['ช่องนั้นเคยมีหินปูนอุดอยู่', 'เหงือกหายอักเสบ จะกระชับขึ้น'], 0.26)
s19 = myth(4, 'ไม่เจ็บ แปลว่า\nเหงือกไม่เป็นอะไร', False, _icon_nopain, ['โรคเหงือกมักไม่เจ็บ', 'เลือดออกเวลาแปรง = สัญญาณ'], 0.3)
s20 = myth(5, 'เหงือกอักเสบ ดูแลถูกวิธี\nกลับมาแข็งแรงได้', True, _icon_heal, ['ทำความสะอาดดีต่อเนื่อง', 'เหงือกอักเสบมักดีขึ้น'], 0.4)

def s21(c, t, D):   # habit 1: soft brush, 2-2-2
    background(c, t, '#D8F3EE', '#F0FFF8')
    step_hdr(c, t, 1, 'แปรงขนนุ่ม สูตร 2-2-2')
    soft_brush(c, 420, 520, -20, 1.2)
    label(c, 'ขนนุ่ม', 360, 700, t, 0.9, 50, MINT, INK)
    names = ['ครั้งต่อวัน', 'นาทีต่อครั้ง', 'ชม. งดขนม\nหลังแปรง']
    for i, nm in enumerate(names):
        x = 1000 + i * 350; t0 = 1.8 + i * 1.6
        s = card(c, x, 540, 320, 330, t, t0, (YEL, MINT, '#FFD6E0')[i])
        if s > 0:
            draw_img(c, text_img('2', 150, CORAL, 10, INK), x, 480, s)
            draw_img(c, text_img(nm, 44, INK, 0, INK, FONT_B), x, 640, s)
    label(c, 'ยาสีฟันผสมฟลูออไรด์', 1350, 800, t, 6.6, 48, TEAL, WHITE)
    caps(c, t, D, ['สูตรของกรมอนามัย'], start=D * 0.75)

def s22(c, t, D):   # habit 2: 45 degrees at the gum line
    background(c, t, '#FFE1EA', '#FFF5F8')
    step_hdr(c, t, 2, 'เอียง 45° เข้าหาขอบเหงือก')
    gx, gy = 720, 830
    gum_closeup(c, gx, gy, 1.1, t, inflam=0.3 * (1 - seg(t, 3, 7)), plaque=1 - seg(t, 2.0, 6.0), mood='happy' if t > 4 else 'smile')
    k = ease_out(seg(t, 0.8, 1.8))
    wig = math.sin(t * 16) * 10 * seg(t, 1.8, 2.0) * (1 - seg(t, 7.0, 7.3))
    soft_brush(c, gx + 260 + wig, gy - 140 - 160 * (1 - k), -45, 0.9)
    protractor(c, gx + 120, gy - 40, 45, seg(t, 1.6, 2.4))
    if t > 2.0: label(c, '45°', gx + 330, gy - 300, t, 2.0, 56, YEL, INK)
    if 1.8 < t < 7: bubbles(c, gx + 60, gy - 60, t, 6); cue(t, 1.9, 'scrub')
    label(c, 'ขยับสั้นๆ เบาๆ', 1460, 450, t, 2.6, 50, WHITE, INK)
    label(c, 'ทำความสะอาดร่องเหงือก', 1460, 600, t, 3.6, 46, TEAL, WHITE)
    caps(c, t, D, ['ไม่ต้องกดแรง ไม่ต้องถูยาวๆ'], start=D * 0.65)

def s23(c, t, D):   # habit 3: floss
    background(c, t, '#D0F4DE', '#F0FFF4')
    step_hdr(c, t, 3, 'ใช้ไหมขัดฟันทุกวัน')
    gy = 940
    out = seg(t, 3.4, 4.2)
    heal = seg(t, 5.5, 8.0)
    for j, x in enumerate((760, 1160)):
        tooth(c, x, gy - 300 + math.sin(t * 4 + j) * 4, 1.25, 'worry' if out < 1 else 'joy', (-1) ** j * 2, t=t, seed=j, shadow=False)
    p = skia.Path(); p.moveTo(-20, H); p.lineTo(-20, gy)
    for i in range(7):
        x0 = -20 + i * 330; p.quadTo(x0 + 165, gy - 50, x0 + 330, gy)
    p.lineTo(W + 20, H); p.close()
    fillp(c, p, lingrad((0, gy), (0, H), mix(GUM_RED, GUM, heal), mix(GUM_REDD, GUMD, heal)))
    gx = 960
    if out < 1:
        c.drawCircle(gx, 640 - 400 * ease_in(out), 26, P(GREEN)); c.drawCircle(gx, 640 - 400 * ease_in(out), 26, P(INK, stroke=5))
    if 2.6 < t < 5.5:
        for i in range(2): c.drawCircle(gx - 20 + i * 40, gy - 6, 8, P(BLOODPINK, 220 * (1 - seg(t, 4.5, 5.5))))
    k = ease_out(seg(t, 1.2, 3.2)) * (1 - 0.5 * seg(t, 4.4, 5.0))
    fy = lerp(300, 700, k)
    c.drawLine(gx - 30, 260, gx - 6, fy, P(INK, stroke=10)); c.drawLine(gx - 30, 260, gx - 6, fy, P(WHITE, stroke=5))
    c.drawLine(gx + 30, 260, gx + 6, fy, P(INK, stroke=10)); c.drawLine(gx + 30, 260, gx + 6, fy, P(WHITE, stroke=5))
    c.drawRoundRect(RR(gx, 250, 120, 70), 22, 22, P(SKY)); c.drawRoundRect(RR(gx, 250, 120, 70), 22, 22, P(INK, stroke=6))
    draw_img(c, text_img('ไหมขัดฟัน', 30, INK, 0), gx, 252, 1)
    cue(t, 1.2, 'slide_down', 0.3); cue(t, 3.4, 'pop'); cue(t, 5.5, 'ding')
    label(c, 'ช่วงแรกอาจมีเลือดออกบ้าง', 1550, 470, t, 2.8, 40, WHITE, INK, font=FONT_M)
    if t > 5.5:
        hand_text(c, 'ค่อยๆ ดีขึ้น!', 1550, 620, t, 5.6, 60, TEAL, -6)
        for i in range(4): sparkle(c, gx - 300 + i * 200, 420 + 30 * math.sin(t * 4 + i), 20, YEL)
    caps(c, t, D, ['ทำต่อเนื่อง อย่างนุ่มนวล'], start=D * 0.7)

def s24(c, t, D):   # mini quiz
    background(c, t, '#FFF3B0', '#FFE7C7')
    burst(c, W / 2, 560, t, 16, 150, 1300, WHITE, 50, 6)
    big_title(c, 'ควิซ! เหงือกแบบไหนแข็งแรง?', W / 2, TITLE_Y, t, 0.2, 90, YEL, rot=-2)
    reveal = D * 0.74
    opts = [('ก.', 'แดงและบวม', 0.9, 0.0), ('ข.', 'ชมพู แน่น\nไม่มีเลือดออก', 0.0, 0.0), ('ค.', 'เลือดออกนิดหน่อย\nตอนแปรง', 0.5, 0.7)]
    for i, (k, nm, infl, bl) in enumerate(opts):
        x = 420 + i * 540; t0 = 1.6 + i * 1.6
        dim = (0.45 if (t > reveal and i != 1) else 1.0)
        s = card(c, x, 600, 460, 460, t, t0, MINT if (t > reveal and i == 1) else WHITE, a=dim)
        if s > 0:
            c.save(); c.translate(x, 600); c.scale(s, s); c.translate(-x, -600)
            clip = skia.Path(); clip.addRoundRect(RR(x, 520, 440, 280), 30, 30)
            c.save(); c.clipPath(clip, doAntiAlias=True)
            if dim < 1: c.saveLayer(None, skia.Paint(Alphaf=dim))
            gum_closeup(c, x, 600, 0.55, t, inflam=infl, bleed=bl)
            if dim < 1: c.restore()
            c.restore(); c.restore()
            draw_img(c, text_img(k, 70, CORAL, 8, INK), x - 170, 420, s, dim)
            draw_img(c, text_img(nm, 44, INK, 0, INK, FONT_B, 10), x, 760, s, dim)
            if t > reveal:
                if i == 1: check(c, x + 160, 420, 2.0)
                else: cross(c, x + 160, 420, 1.4, CORAL, 200)
    if 5.5 < t < reveal:
        timer_clock(c, 1780, 330, seg(t, 5.5, reveal), 0.4, t)
        cue(t, 5.6, 'tick')
    cue(t, reveal, 'fanfare')
    if t > reveal:
        confetti(c, t - reveal)
        label(c, 'เฉลย ข้อ ข. ค่ะ!', W / 2, SUB_Y, t, reveal + 0.1, 58, TEAL, WHITE, rot=-2)

def s25(c, t, D):   # habit 4: check-ups + scaling every 6 months
    background(c, t, '#D8F3EE', '#F0FFF8')
    step_hdr(c, t, 4, 'ตรวจฟัน ขูดหินปูน ทุก 6 เดือน')
    dr_nawarat(c, 400, 360, 0.62, t, 'happy', wave=0.4, cape=0, hold='mirror')
    m = 1 + 5 * ease_io(seg(t, 1.0, 3.0))
    calendar(c, 900, 560, t, m)
    cue(t, 3.0, 'ding')
    tooth(c, 1170, 600, 0.9, 'joy' if t > 3 else 'smile', 0, t=t, seed=4)
    label(c, 'กรมอนามัยแนะนำ', 900, 790, t, 3.1, 40, TEAL, WHITE)
    label(c, 'เจอปัญหาเหงือก', 1600, 480, t, 3.6, 48, WHITE, INK)
    label(c, 'ตั้งแต่เนิ่นๆ', 1600, 640, t, 4.4, 52, YEL, INK)
    caps(c, t, D, ['หินปูนต้องให้หมอฟันขูดออก'], start=D * 0.65)

def s26(c, t, D):   # habit 5: no smoking, less sugar, veggies; see the dentist if it persists
    background(c, t, '#E4FDE1', '#FFF5E1')
    step_hdr(c, t, 5, 'ดูแลตัวเองด้วย')
    names = ['ไม่สูบบุหรี่', 'ลดของหวาน', 'กินผักผลไม้']
    for i, nm in enumerate(names):
        x = 380 + i * 420; t0 = 0.9 + i * 1.2
        s = card(c, x, 540, 360, 380, t, t0, WHITE)
        if s <= 0: continue
        c.save(); c.translate(x, 500); c.scale(s, s)
        if i == 0: cigarette_no(c, 0, 0, 0.8)
        elif i == 1:
            candy(c, -30, 0, 1.1, -20, PINK); cross(c, 50, -50, 1.2)
        else:
            c.drawCircle(-40, 10, 60, P(CORAL)); c.drawCircle(-40, 10, 60, P(INK, stroke=6))
            c.drawLine(-40, -50, -30, -80, P(GREEN_D, stroke=10))
            c.drawOval(RR(60, 20, 90, 120), P(GREEN)); c.drawOval(RR(60, 20, 90, 120), P(INK, stroke=6))
            face(c, -40, 10, 'happy', 1, 0, 0.6, eye_dx=22)
        c.restore()
        label(c, nm, x, 760, t, t0 + 0.2, 44, (CORAL, PINK, GREEN)[i], WHITE if i < 2 else INK)
    dr_nawarat(c, 1650, 380, 0.55, t, 'smile', point=0.6, cape=0)
    caps(c, t, D, ['ดูแลดีแล้ว เลือดยังออก ให้หมอฟันตรวจนะคะ'], start=D * 0.55)

def s27(c, t, D):   # recap
    background(c, t, '#FFE1EA', '#FFF3B0')
    big_title(c, 'สรุป 5 ข้อ เหงือกแข็งแรง', W / 2, TITLE_Y, t, 0.2, 90, YEL)
    tips = ['อย่าหยุด\nแปรง', 'แปรง\nขนนุ่ม', 'เบาๆ ที่\nขอบเหงือก', 'ไหมขัดฟัน\nทุกวัน', 'ตรวจฟัน\nทุก 6 เดือน']
    cols = [YEL, '#FFD6E0', MINT, '#CFF4FF', LAV]
    for i, tip in enumerate(tips):
        x = 230 + i * 365; t0 = 0.8 + i * 1.3
        s = card(c, x, 580, 320, 420, t, t0, cols[i], rot=(-1) ** i * 3)
        if s > 0:
            draw_img(c, text_img(tip, 50, INK, 0, INK, FONT_B, 12), x, 620, s)
            num_badge(c, i + 1, x, 400, t, t0 + 0.1, CORAL)
            cue(t, t0, 'ding')
    if t > 7.5: confetti(c, t - 7.5)

def s28(c, t, D):   # happy ending
    bathroom(c, t)
    burst(c, W / 2, 560, t, 18, 150, 1400, WHITE, 70, 6)
    x, y, s = 520, 430, 0.7
    person(c, x, y, s, 'joy' if t > 2.5 else 'happy', 0, t, shirt=SHIRT)
    if t < 2.5: brushing(c, x, y, s, t); cue(t, 0.3, 'scrub')
    else: soft_brush(c, 300, 820, -40, 0.7)
    heal = seg(t, 1.0, 3.0)
    card(c, 1300, 560, 640, 560, t, 0.6, WHITE)
    if t > 0.9:
        c.save(); clip = skia.Path(); clip.addRoundRect(RR(1300, 560, 630, 550), 38, 38); c.clipPath(clip, doAntiAlias=True)
        gum_closeup(c, 1300, 680, 0.8, t, inflam=0.8 * (1 - heal), mood='joy' if heal > 0.9 else None)
        c.restore()
    for i in range(3):
        heart(c, 900 + i * 90, 360 - ((t * 60 + i * 40) % 160), 22, CORAL, 220)
    cue(t, 3.0, 'fanfare')
    if t > 3.0: confetti(c, t - 3.0)
    big_title(c, 'เหงือกชมพู ยิ้มมั่นใจ!', W / 2, TITLE_Y, t, 3.0, 100, YEL, rot=-2)
    caps(c, t, D, ['แปรงให้ทั่ว เบาๆ ทุกวัน', 'เหงือกกลับมาแข็งแรง!'])

STORY = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
         s21, s22, s23, s24, s25, s26, s27, s28]
assert len(STORY) == len(NARR) - 2

# ---------------------------------------------------------------- durations: measured clips (durations.json) or estimates
_dp = os.path.join(HERE, 'durations.json')
_meas = json.load(open(_dp)) if os.path.exists(_dp) else {}
def dur(i, est_extra=1.1):
    if str(i) in _meas: return round(max(8.5, min(14.0, _meas[str(i)] + 1.7)), 2)
    n = len(re.sub(r'\[.*?\]', '', NARR[i]))
    return round(max(8.0, min(14.0, n / 11.5 + est_extra)), 2)

def bind(f, D):
    return lambda c, t: f(c, t, D)

SCENES = [Scene(COVER, 4.0)] + [Scene(bind(f, dur(i + 1)), dur(i + 1)) for i, f in enumerate(STORY)] + \
    [Scene(endcard('ปรึกษาเรื่องเหงือก ทักมาได้เลย!'), round(max(6.0, _meas.get(str(len(NARR) - 1), 0) + 1.6), 2))]

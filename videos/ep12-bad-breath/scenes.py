"""ep12 กลิ่นปากมาจากไหน? แก้ยังไงให้ถูกจุด — long 16:9 kawaii episode (house format since 2026-10-22, like ep11).
สมจี๊ด's morning breath and a garlicky Thai lunch -> หมอนวรัตน์ flies in with her cape and a magnifier -> five suspects
(tongue coating, food between teeth, mouth problems, dry mouth, strong foods) + other causes -> self-check -> a
myth-or-fact round -> five fixes (2-2-2, tongue, floss, water, check-ups) with a viewer quiz -> recap -> happy ending.
Scene lengths come from durations.json (the measured narration clips) when present."""
import sys, os, json, re, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOTDIR = os.path.join(HERE, '..', '..')
sys.path.insert(0, ROOTDIR); sys.path.insert(0, HERE); sys.path.append(os.path.join(ROOTDIR, 'videos', 'ep6-root-canal'))
from tools.kawaii import *  # noqa: F401,F403
from chars import person    # สมจี๊ด (ep6)
from props import *          # noqa: F401,F403
from script import NARR

SHIRT = '#FF9EBB'; FRIEND = '#FFD166'

# ---------------------------------------------------------------- helpers
def caps(c, t, D, lines, y=SUB_Y, size=50, bg=WHITE, fg=INK, start=0.5):
    """caption pills shown one after another, spread over the scene"""
    n = len(lines)
    span = max(1.0, D - start - 0.6)
    for i, txt in enumerate(lines):
        a = start + span * i / n
        b = start + span * (i + 1) / n if i < n - 1 else 999
        subtitle(c, txt, t, a, b, y, size, bg, fg)

def at(D, f): return D * f

def hand_on_mouth(c, x, y, s, t, k=1.0, shirt=SHIRT):
    """a little mitten hand pressed over the mouth (no arm, kawaii style)"""
    if k <= 0: return
    yy = y + math.sin(t * 3) * 6
    hx, hy = x + 10 * s, yy + (72 + 60 * (1 - k)) * s
    c.save(); c.translate(hx, hy); c.rotate(-8); c.scale(s * k, s * k)
    h = skia.Path(); h.addRoundRect(RR(0, 0, 130, 86), 42, 42); fillp(c, h, '#FFE0CC', stroke=6)
    for dx in (-22, 8, 38): c.drawLine(dx, -40, dx, -14, P('#E8B49A', stroke=5))
    c.drawRoundRect(RR(0, 58, 70, 40), 16, 16, P(shirt)); c.drawRoundRect(RR(0, 58, 70, 40), 16, 16, P(INK, stroke=6))
    c.restore()

def mouth_pt(x, y, s, t): return x, y + math.sin(t * 3) * 6 + 66 * s

def suspect(c, n, t, t0=0.2, x=290, y=TITLE_Y):
    cue(t, t0, 'pop')
    k = pop(t, t0)
    if k <= 0: return
    img = text_img(f'ผู้ต้องสงสัย #{n}', 50, WHITE, 0)
    bw = img.width() + 70
    c.save(); c.translate(x, y); c.scale(k, k); c.rotate(-6)
    c.drawRoundRect(RR(6, 8, bw, 96), 48, 48, P(INK, 80)); c.drawRoundRect(RR(0, 0, bw, 96), 48, 48, P(CORAL))
    c.drawRoundRect(RR(0, 0, bw, 96), 48, 48, P(INK, stroke=7))
    c.restore()
    draw_img(c, img, x, y + 2, k, 1, -6)

def step_hdr(c, t, n, line, x=None):
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

# ================================================================ cover
def cast_cover(c, t):
    k = pop(t, 0.3)
    person(c, 330, 520, 0.62 * k, 'worry', 0, t, shirt=SHIRT) if k > 0 else None
    if k > 0: hand_on_mouth(c, 330, 520, 0.62 * k, t, 1.0)
    breath_cloud(c, 600, 760, 0.8 * pop(t, 0.6), t, 255, 'squeeze')
    dr_nawarat(c, 1560, 470, 0.72 * pop(t, 0.5), t, 'happy', wave=1.0)
    if t > 0.8: magnifier(c, 1330, 760, 0.7 * pop(t, 0.8), -25, 0.5 + 0.5 * math.sin(t * 4))
COVER = cover('กลิ่นปากมาจากไหน?', 'แก้ยังไงให้ถูกจุด', 'ตอนที่ 12', top='#E4FFF2', bot='#BDF4E3', cast=cast_cover)

# ================================================================ story
def s1(c, t, D):   # morning yawn
    bedroom(c, t)
    bed(c, 960, 800, 1.0)
    x, y, s = 900, 470, 0.7
    sleep = t < 1.6
    yawn = seg(t, 1.6, 2.4) * (1 - seg(t, 4.0, 4.4))
    shock = t > 4.4
    mood = 'sleep' if sleep else ('worry' if shock else 'smile')
    person(c, x, y, s, mood, 0.9 * yawn if not shock else 0.0, t, shirt=SHIRT)
    blanket(c, 960, 770, 1.0)
    if sleep:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            draw_img(c, text_img('z', 50 + 14 * k, LAV, 6, INK), x + 200 + ph * 50, y - 120 - ph * 90, 1, 1 - ph)
    cue(t, 1.6, 'boing')
    mx, my = mouth_pt(x, y, s, t)
    bk = ease_out(seg(t, 2.6, 4.0))
    if t > 2.6:
        breath_cloud(c, lerp(mx + 60, mx + 420, bk), lerp(my, my - 90, bk), 0.3 + 0.7 * bk, t, 255, 'squeeze')
    cue(t, 2.7, 'whoosh')
    if shock:
        hand_on_mouth(c, x, y, s, t, ease_out(seg(t, 4.4, 4.8)))
        sweat(c, x - 190, y - 80, 1.1, 255 * seg(t, 4.6, 4.9))
        hand_text(c, 'อุ๊ย!', x - 320, y - 170, t, 4.5, 96, CORAL, -10)
        cue(t, 4.5, 'thud')
    big_title(c, 'อรุณสวัสดิ์~', W / 2, TITLE_Y, t, 0.3, 96, YEL)
    if t > 1.6: hand_text(c, 'ฮ้าาา~', x + 250, y - 150, t, 1.8, 70, TEAL, 8)
    caps(c, t, D, ['ตื่นมา หาวกว้างๆ...', 'ทำไมลมหายใจมีกลิ่น?!'])

def s2(c, t, D):   # the question
    background(c, t, '#FFF3B0', '#FFE1EA')
    gy = 900
    for i, x in enumerate(ROW_X):
        look = -1 if x > W / 2 else 1
        tooth(c, x, gy - 140 + math.sin(t * 5 + i) * 6, 0.85, 'worry' if t > 1.5 else 'smile', 0, t=t, seed=i, look=look)
    gum_row(c, gy)
    for i, (bx, by) in enumerate(((330, 420), (1600, 400), (960, 330))):
        breath_cloud(c, bx, by + math.sin(t * 2 + i) * 15, 0.7 * pop(t, 0.6 + i * 0.3), t, 230, 'squeeze', seed=i)
    big_title(c, 'กลิ่นปาก มาจากไหน?', W / 2, TITLE_Y, t, 0.3, 104, WHITE, shake=12)
    for i, (qx, qy) in enumerate(((560, 300), (1360, 300))):
        hand_text(c, '?', qx, qy + math.sin(t * 4 + i) * 10, t, 1.2 + i * 0.3, 120, CORAL, (-1) ** i * 12)
    caps(c, t, D, ['หลายคนแอบกังวล', 'แก้ยังไงให้ถูกจุด?'])

def s3(c, t, D):   # office, mint candies
    office(c, t)
    desk(c, 960, 800, 1300)
    person(c, 1400, 440, 0.68, 'happy' if t < 2.5 else 'smile', 0, t, shirt=FRIEND, seed=3)
    label(c, 'สวัสดีจ้า!', 1400, 220, t, 0.6, 50, WHITE, INK)
    x, y, s = 560, 440, 0.68
    person(c, x, y, s, 'worry', 0, t, shirt=SHIRT)
    hand_on_mouth(c, x, y, s, t, ease_out(seg(t, 1.6, 2.0)))
    if t > 2.0: sweat(c, x - 170, y - 60, 1.0)
    n = int(clamp((t - 3.2) / 1.1, 0, 4))
    for i in range(4):
        k = pop(t, 3.2 + i * 1.1)
        if k > 0:
            candy(c, 820 + i * 120, 760 - 20 * math.sin(t * 3 + i), 0.7 * k, 20 * i, (MINT, SKY, MINT, LAV)[i])
    if n > 0: hand_text(c, f'เม็ดที่ {n}!', 1000, 620, t, 3.2, 60, TEAL, 6)
    big_title(c, 'ไม่กล้าพูดใกล้ๆ', W / 2, TITLE_Y, t, 1.6, 96)
    caps(c, t, D, ['เอามือปิดปาก...', 'อมลูกอมมิ้นต์ เม็ดแล้วเม็ดเล่า'])

def s4(c, t, D):   # lunch
    background(c, t, '#FFE7C7', '#FFF6E5')
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 640, 1800, 720), 30, 30, P('#F4C27F')); c.drawRoundRect(skia.Rect.MakeLTRB(120, 640, 1800, 720), 30, 30, P(INK, stroke=7))
    items = [(330, 'sator', 'ผัดสะตอกะปิ', 0.5), (720, 'somtam', 'ส้มตำปลาร้า', 1.4), (1110, 'egg', 'ไข่เจียวกระเทียม', 2.3)]
    for x, kind, name, t0 in items:
        k = pop(t, t0)
        if k > 0:
            plate(c, x, 620, 1.1 * k, kind, t)
            label(c, name, x, 790, t, t0 + 0.2, 42, WHITE, INK, font=FONT_M)
    if t > 0.8: sator(c, 330, 470, 0.7 * pop(t, 0.8), t, 'happy', -8)
    if t > 2.6: garlic(c, 1110, 470, 0.8 * pop(t, 2.6), t, 'happy')
    if t > 3.3:
        iced_coffee(c, 1470, 560, 0.85 * pop(t, 3.3), t, 'happy')
        label(c, 'กาแฟเย็น', 1470, 790, t, 3.5, 42, WHITE, INK, font=FONT_M)
    if t > 5.0:
        k = pop(t, 5.0)
        water_glass(c, 1720, 520, 0.6 * k, t, 'sad', 0.85)
        cross(c, 1720, 420, 1.3 * k)
        hand_text(c, 'ลืมดื่มน้ำ!', 1700, 300, t, 5.3, 54, CORAL, 8)
    big_title(c, 'มื้อเที่ยงจัดเต็ม!', W / 2, TITLE_Y, t, 0.2, 96, YEL)
    caps(c, t, D, ['เมนูกลิ่นแรง + กาแฟเย็น', 'แทบไม่ได้ดื่มน้ำเปล่าเลย'])

def s5(c, t, D):   # Dr. Nawarat flies in
    background(c, t, '#FFF3B0', '#FFD6A5')
    land = 1.3
    cue(t, 0.1, 'slide_down', 0.3); cue(t, land, 'thud', 0.7); cue(t, land + 0.1, 'fanfare')
    if t > land: burst(c, 1180, 560, t, 18, 120, 1500 * ease_out(seg(t, land, land + 0.6)), WHITE, 110)
    xx, yy = flying_in(c, t, 1180, 330, 0.75, 0, land, 'hero' if t < 3 else 'happy', wave=seg(t, land, land + 0.4))
    puff(c, 1180, 790, seg(t, land, land + 0.8), 9, 300)
    if t > land:
        magnifier(c, 900, 760, 0.6 * pop(t, land + 0.3), -20, 0.5 + 0.5 * math.sin(t * 5))
    big_title(c, 'มุมความรู้', 520, 330, t, land + 0.2, 100, YEL, rot=-4, shake=10)
    big_title(c, 'กับหมอนวรัตน์', 520, 470, t, land + 0.6, 92)
    label(c, 'ภารกิจ: ตามหาต้นตอกลิ่นปาก', 480, 640, t, land + 1.6, 46, CORAL, WHITE, rot=-2)
    caps(c, t, D, ['ไม่ต้องห่วงนะคะ!', 'ไปสืบหาต้นตอกันค่ะ'], start=land + 1.0)

def s6(c, t, D):   # mostly from the mouth
    background(c, t, '#D8F3EE', '#F0FFF8')
    open_mouth(c, 760, 640, 0.95, t, 0.6, 0.6)
    k = ease_io(seg(t, 0.6, 3.5))
    mx = lerp(560, 920, 0.5 + 0.5 * math.sin(k * math.pi * 2 - math.pi / 2)); my = 620 + 40 * math.sin(k * math.pi * 3)
    magnifier(c, mx, my, 0.9, -25, seg(t, 3.5, 3.8))
    dr_nawarat(c, 1560, 360, 0.6, t, 'smile' if t < 3.5 else 'happy', point=0.6)
    big_title(c, 'ส่วนใหญ่มาจาก', W / 2, TITLE_Y - 10, t, 0.3, 84)
    big_title(c, 'ในช่องปาก!', 760, 300, t, 3.5, 96, YEL, rot=-3)
    if t > 3.5: hand_text(c, 'เจอแล้ว!', 1200, 820, t, 3.6, 64, CORAL, 8)
    caps(c, t, D, ['ข่าวดี! กลิ่นปากส่วนใหญ่ เกิดในช่องปาก', 'ดูแลถูกวิธี ช่วยลดกลิ่นได้'])

def s7(c, t, D):   # suspect 1: tongue coating
    background(c, t, '#FFE1EA', '#FFF5F8')
    suspect(c, 1, t)
    big_title(c, 'ฝ้าบนลิ้น', W / 2 + 140, TITLE_Y, t, 0.5, 100, YEL)
    tongue_char(c, 760, 590, 1.25, t, seg(t, 0.8, 1.8), 'worry' if t > 2 else 'smile')
    for i, (gx, gy) in enumerate(((650, 450), (800, 420), (900, 480))):
        k = pop(t, 2.4 + i * 0.4)
        if k > 0: germ(c, gx, gy - 30 * k, 0.33 * k, t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i], mood='happy')
    cue(t, 2.4, 'boing')
    if t > 3.6:
        k = ease_out(seg(t, 3.6, 4.0))
        c.drawLine(1180, 420, lerp(1180, 930, k), lerp(420, 440, k), P(INK, stroke=7))
        label(c, 'โคนลิ้น', 1260, 420, t, 3.6, 46, CORAL, WHITE)
    if t > 1.2:
        label(c, 'ร่องเล็กๆ เต็มลิ้น', 1300, 640, t, 1.3, 44, WHITE, INK, font=FONT_M)
    dr_nawarat(c, 1650, 420, 0.5, t, 'smile', point=0.7)
    caps(c, t, D, ['เศษอาหาร + เชื้อโรค ซ่อนในร่องลิ้น', 'โดยเฉพาะที่โคนลิ้น'])

def s8(c, t, D):   # germs make smelly gas
    background(c, t, '#E2ECFF', '#F4F0FF')
    gx = [520, 960, 1400]
    for i, x in enumerate(gx):
        y = 600
        for j in range(3):   # food bits flying into the germ
            ph = seg(t, 0.6 + j * 0.5 + i * 0.2, 1.1 + j * 0.5 + i * 0.2)
            if 0 < ph < 1:
                bx, by = lerp(x - 260, x, ph), lerp(800, y, ph) - math.sin(ph * math.pi) * 80
                c.drawCircle(bx, by, 16, P(YEL)); c.drawCircle(bx, by, 16, P(INK, stroke=4))
        munch = 'joy' if (int(t * 4) % 2 == 0 and t < 2.6) else 'happy'
        germ(c, x, y, 0.85, t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i], mood=munch if t < 2.8 else 'happy')
        if t > 2.8:
            k = ease_out(seg(t, 2.8 + i * 0.2, 4.2 + i * 0.2))
            breath_cloud(c, x + 40, lerp(y - 60, y - 230, k), 0.25 + 0.5 * k, t, 240, 'squeeze', seed=i)
    cue(t, 0.6, 'tick'); cue(t, 2.8, 'slide_up', 0.3)
    if t < 2.8: hand_text(c, 'งั่มๆ', 960, 780, t, 0.8, 60, TEAL, 6)
    big_title(c, 'เชื้อโรคกินเศษอาหาร', W / 2, TITLE_Y, t, 0.3, 84)
    label(c, 'ปล่อยก๊าซกลิ่นเหม็น ~ คล้ายไข่เน่า', W / 2, 820, t, 3.4, 48, STINK_D, WHITE)
    caps(c, t, D, ['ตัวการสำคัญของกลิ่นปาก!'], start=D * 0.55)

def s9(c, t, D):   # why mornings are worse: less saliva while sleeping
    background(c, t, '#3D4A8F', '#7B86C9', dots=False)
    for i in range(14):
        rr = random.Random(500 + i)
        sparkle(c, rr.uniform(40, W - 40), rr.uniform(60, 600), 10 + 6 * math.sin(t * 3 + i), WHITE, 220)
    c.drawCircle(1700, 200, 80, P('#FFF3B0')); c.drawCircle(1740, 175, 70, P('#3D4A8F'))
    c.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), P('#5A639E')); c.drawLine(0, 900, W, 900, P(INK, stroke=7))
    bed(c, 640, 790, 0.9)
    person(c, 600, 520, 0.6, 'sleep', 0, t, shirt=SHIRT, bob=False)
    blanket(c, 640, 760, 0.9)
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        draw_img(c, text_img('z', 50 + 14 * k, LAV, 6, INK), 800 + ph * 50, 400 - ph * 90, 1, 1 - ph)
    # saliva meter
    lvl = 1 - 0.75 * ease_io(seg(t, 1.0, 4.0))
    c.drawRoundRect(skia.Rect.MakeLTRB(1180, 330, 1290, 830), 40, 40, P(WHITE)); c.drawRoundRect(skia.Rect.MakeLTRB(1180, 330, 1290, 830), 40, 40, P(INK, stroke=7))
    c.save(); c.clipRect(skia.Rect.MakeLTRB(1180, 830 - 500 * lvl, 1290, 830))
    c.drawRoundRect(skia.Rect.MakeLTRB(1190, 340, 1280, 820), 34, 34, P(SKY)); c.restore()
    saliva_drop(c, 1235, 260, 0.6, t, 'sad' if lvl < 0.6 else 'happy')
    label(c, 'น้ำลาย', 1235, 880, t, 0.6, 44, SKY, INK)
    cue(t, 1.0, 'slide_down', 0.3)
    n = int(1 + 6 * seg(t, 2.0, 5.0))
    for i in range(n):
        rr = random.Random(40 + i)
        germ(c, rr.uniform(1420, 1820), rr.uniform(420, 800), 0.32, t, seed=i, col=('#9BE15D', '#B58CFF', '#FFB347')[i % 3], mood='happy')
    if t > 2.0: hand_text(c, 'เพิ่มจำนวน!', 1620, 360, t, 2.2, 54, CORAL, 6)
    big_title(c, 'ทำไมตอนเช้ากลิ่นแรง?', W / 2, TITLE_Y, t, 0.3, 88, YEL)
    caps(c, t, D, ['ตอนนอน น้ำลายน้อยลง ปากแห้ง', 'น้ำลาย = ตัวช่วยชะล้างเศษอาหาร'])

def s10(c, t, D):   # suspect 2: food between teeth
    background(c, t, '#D0F4DE', '#F0FFF4')
    suspect(c, 2, t)
    big_title(c, 'เศษอาหารติดซอกฟัน', W / 2 + 160, TITLE_Y, t, 0.5, 84, YEL)
    gy = 920
    stuck = 1 - seg(t, 5.2, 5.8)
    for i, x in enumerate(ROW_X):
        tooth(c, x, gy - 150 + math.sin(t * 5 + i) * 4, 0.82, 'worry' if stuck > 0.5 and t > 1.5 else 'happy', 0, t=t, seed=i, shadow=False)
    gum_row(c, gy)
    for j in range(4):
        gx = (ROW_X[j] + ROW_X[j + 1]) / 2
        a = 255 * pop(t, 1.0 + j * 0.25) if t < 5.2 else 255 * stuck
        if j == 1 and t > 5.2:
            dy = -300 * seg(t, 5.2, 5.8)
        else:
            dy = 0
        if a > 1:
            c.drawCircle(gx, 690 + dy, 22, P(GREEN, a)); c.drawCircle(gx, 690 + dy, 22, P(INK, a, stroke=5))
            p = skia.Path(); yy = 640 - (t * 40 % 40)
            p.moveTo(gx, yy); p.cubicTo(gx + 12, yy - 14, gx - 12, yy - 28, gx, yy - 42)
            c.drawPath(p, P(STINK_D, a * 0.8, stroke=6))
    # brush passes over the top but misses the gaps
    if 2.2 < t < 4.4:
        bx = lerp(300, 1600, (t - 2.2) / 2.2)
        toothbrush(c, bx, 520, 0, 1.0); bubbles(c, bx - 60, 560, t, 6)
        cue(t, 2.3, 'scrub')
        hand_text(c, 'แปรงไม่ถึง!', W / 2, 400, t, 3.4, 60, CORAL, -6)
    if t > 4.6:
        k = ease_out(seg(t, 4.6, 5.2))
        gx = (ROW_X[1] + ROW_X[2]) / 2
        fy = lerp(380, 690, k)
        c.drawLine(gx, 330, gx, fy, P(INK, stroke=10)); c.drawLine(gx, 330, gx, fy, P(WHITE, stroke=5))
        c.drawRoundRect(RR(gx, 320, 80, 60), 18, 18, P(SKY)); c.drawRoundRect(RR(gx, 320, 80, 60), 18, 18, P(INK, stroke=6))
        cue(t, 5.2, 'ding')
        if t > 5.3: sparkle(c, gx, 690, 40 * math.sin(seg(t, 5.3, 6.0) * math.pi), YEL)
    caps(c, t, D, ['แปรงไม่ทั่ว / ไม่ใช้ไหมขัดฟัน', 'เศษอาหารค้าง บูดเน่า ส่งกลิ่น'])

def tooth_card(c, x, y, t, t0, name, kind):
    s = card(c, x, y, 470, 520, t, t0, WHITE)
    if s <= 0: return
    c.save(); c.translate(x, y); c.scale(s, s); c.translate(-x, -y)
    if kind == 'gum':
        tooth(c, x, y - 40, 0.75, 'worry', 0, t=t, seed=3, shadow=False)
        g = skia.Path(); g.addRoundRect(skia.Rect.MakeLTRB(x - 190, y + 40, x + 190, y + 140), 40, 40); fillp(c, g, lingrad((0, y + 40), (0, y + 140), '#FF7A9A', GUMD))
        for dx in (-90, 0, 90): c.drawCircle(x + dx, y + 50, 18, P('#FF5A7A'))
    else:
        tooth(c, x, y - 10, 0.85, 'sad', 0, t=t, seed=1 if kind == 'hole' else 2, shadow=False)
        if kind == 'hole':
            c.drawOval(RR(x + 40, y - 100, 44, 36), P('#5A3A2A')); c.drawOval(RR(x + 40, y - 100, 44, 36), P(INK, stroke=4))
        else:
            for i in range(5):
                c.drawCircle(x - 60 + i * 30, y + 70 + (i % 2) * 8, 22, P('#E9D27A')); c.drawCircle(x - 60 + i * 30, y + 70 + (i % 2) * 8, 22, P(INK, 160, stroke=4))
    c.restore()
    label(c, name, x, y + 200, t, t0 + 0.2, 46, CORAL, WHITE)

def s11(c, t, D):   # suspect 3: mouth problems
    background(c, t, '#FFF1E6', '#FFE1EA')
    suspect(c, 3, t)
    big_title(c, 'ปัญหาในช่องปาก', W / 2 + 140, TITLE_Y, t, 0.5, 88, YEL)
    tooth_card(c, 420, 560, t, 1.0, 'ฟันผุเป็นรู', 'hole')
    tooth_card(c, 960, 560, t, 2.0, 'หินปูนเกาะ', 'calc')
    tooth_card(c, 1500, 560, t, 3.0, 'เหงือกอักเสบ', 'gum')
    caps(c, t, D, ['แหล่งสะสมเชื้อโรค', 'ให้หมอฟันช่วยดูแลนะคะ'], start=D * 0.45)

def s12(c, t, D):   # suspect 4: dry mouth
    background(c, t, '#FFF3B0', '#FFE7C7')
    suspect(c, 4, t)
    big_title(c, 'ปากแห้ง', W / 2 + 140, TITLE_Y, t, 0.5, 100, YEL)
    c.drawCircle(220, 330, 80 + 6 * math.sin(t * 3), P(YEL)); c.drawCircle(220, 330, 80 + 6 * math.sin(t * 3), P(INK, stroke=6))
    shrink = 1 - 0.45 * ease_io(seg(t, 1.0, 5.5))
    saliva_drop(c, 380, 600, 1.3 * shrink, t, 'sad')
    if t > 1.0: sweat(c, 500, 470, 0.9)
    label(c, 'น้ำลายน้อยลง', 380, 820, t, 1.0, 46, SKY, INK)
    names = ['ดื่มน้ำน้อย', 'กาแฟบ่อย', 'พูดนานๆ', 'หายใจทางปาก']
    for i, nm in enumerate(names):
        x = 760 + i * 315; t0 = 1.4 + i * 0.9
        s = card(c, x, 560, 290, 400, t, t0, WHITE)
        if s <= 0: continue
        c.save(); c.translate(x, 520); c.scale(s, s)
        if i == 0: water_glass(c, 0, 0, 0.8, t, 'sad', 0.15)
        elif i == 1: iced_coffee(c, 0, 40, 0.75, t, 'happy')
        elif i == 2:
            for j in range(2):
                b = skia.Path(); b.addRoundRect(RR(-30 + j * 60, -40 + j * 90, 170, 90), 40, 40); fillp(c, b, (MINT, '#FFD6E0')[j], stroke=6)
                draw_img(c, text_img('บลาๆ', 34, INK, 0), -30 + j * 60, -40 + j * 90, 1)
        else:
            m = skia.Path(); m.addOval(RR(0, 0, 150, 110)); fillp(c, m, MOUTH, stroke=7)
            for j in range(3):
                ph = (t * 0.9 + j / 3) % 1
                c.drawCircle(0, -70 - ph * 90, 14 + 10 * ph, P(SKY, 220 * (1 - ph)))
        c.restore()
        label(c, nm, x, 780, t, t0 + 0.2, 42, CORAL, WHITE, padx=30, pady=18)
    caps(c, t, D, ['กลิ่นปากมาเยือนง่าย!'], start=D * 0.6)

def s13(c, t, D):   # suspect 5: strong foods
    background(c, t, '#E4FDE1', '#FFF5E1')
    suspect(c, 5, t)
    big_title(c, 'อาหารกลิ่นแรง', W / 2 + 140, TITLE_Y, t, 0.5, 92, YEL)
    garlic(c, 260, 470, 1.25 * pop(t, 0.8), t, 'happy', 1)
    onion(c, 560, 470, 1.15 * pop(t, 1.2), t, 'happy', 2)
    sator(c, 900, 480, 1.0 * pop(t, 1.6), t, 'happy', -10)
    for i, (name, t0) in enumerate((('ชะอม', 2.0), ('ปลาร้า', 2.3), ('ทุเรียน', 2.6))):
        label(c, name, 280 + i * 290, 720, t, t0, 54, (GREEN, '#C98B55', YEL)[i], INK)
    # breath loop
    if t > 3.4:
        k = ease_out(seg(t, 3.4, 4.6))
        breath_cloud(c, 1420, lerp(700, 480, k), 0.4 + 0.5 * k, t, 255, 'squeeze')
        label(c, 'ออกมากับลมหายใจได้อีกพักใหญ่', 1440, 780, t, 3.8, 42, WHITE, INK, font=FONT_M)
    if t > 5.5:
        timer_clock(c, 1700, 470, seg(t, 5.5, 8.0), 0.55, t)
        cue(t, 5.5, 'tick')
    caps(c, t, D, ['แปรงฟันแล้ว กลิ่นอาจยังไม่หายทันที', 'แต่จะค่อยๆ จางไปเอง'], start=D * 0.5)

def s14(c, t, D):   # other causes
    background(c, t, '#E2ECFF', '#F4F0FF')
    big_title(c, 'สาเหตุอื่นๆ', W / 2, TITLE_Y, t, 0.2, 100, YEL)
    xs = [300, 740, 1180, 1620]
    names = ['บุหรี่', 'แอลกอฮอล์', 'ฟันปลอม\nไม่สะอาด', 'ไซนัส /\nทอนซิลอักเสบ']
    for i, x in enumerate(xs):
        t0 = 0.8 + i * 1.6
        s = card(c, x, 560, 400, 480, t, t0, WHITE if i < 3 else MINT)
        if s <= 0: continue
        c.save(); c.translate(x, 520); c.scale(s, s)
        if i == 0: cigarette_no(c, 0, 0, 0.9)
        elif i == 1: bottle(c, 0, 0, 0.8)
        elif i == 2:
            denture(c, 0, 20, 1.0, t)
            for k in range(3):
                ph = (t * 0.8 + k / 3) % 1; pp = skia.Path(); xx = -60 + k * 60; yy = -60 - ph * 60
                pp.moveTo(xx, yy); pp.cubicTo(xx + 12, yy - 14, xx - 12, yy - 28, xx, yy - 42); c.drawPath(pp, P(STINK_D, 255 * (1 - ph), stroke=6))
        else: sinus_nose(c, -40, 0, 1.0, t)
        c.restore()
        label(c, names[i], x, 770, t, t0 + 0.2, 40, CORAL if i < 3 else TEAL, WHITE, padx=30, pady=18)
    caps(c, t, D, ['สงสัยโรคอื่น ควรปรึกษาแพทย์นะคะ'], start=D * 0.6)

def s15(c, t, D):   # self check with a mirror
    background(c, t, '#FFE1EA', '#FFF5F8')
    person(c, 520, 460, 0.7, 'worry' if t < 3 else 'smile', 0.35 if t < 3 else 0.0, t, shirt=SHIRT)
    if t < 3:
        mx, my = mouth_pt(520, 460, 0.7, t)
        tg = skia.Path(); tg.addRoundRect(RR(mx, my + 40, 50, 70), 25, 25); fillp(c, tg, TONGUE, stroke=5)
    hand_mirror(c, 1230, 470, 1.4, 8, t)
    c.save(); p = skia.Path(); p.addOval(RR(1230, 470, 270, 310)); c.clipPath(p, doAntiAlias=True)
    tongue_char(c, 1230, 510, 0.75, t, 1.0 if t < 3.5 else 1.0, 'shock' if t > 2.5 else 'smile')
    c.restore()
    if t > 2.6:
        label(c, 'คราบขาว/เหลืองหนาๆ?', 1300, 820, t, 2.6, 44, CORAL, WHITE)
        cue(t, 2.6, 'boing')
    big_title(c, 'เช็กเองง่ายๆ', W / 2, TITLE_Y, t, 0.3, 100, YEL)
    caps(c, t, D, ['แลบลิ้น ส่องกระจก', 'ถึงเวลาทำความสะอาดลิ้นแล้ว!'], y=990)

def myth(n, statement, verdict, draw_icon, pills, t_verdict=0.45):
    def f(c, t, D):
        background(c, t, '#FFF3B0', '#FFD6E0')
        burst(c, W / 2, 560, t, 16, 150, 1300, WHITE, 60, 6)
        big_title(c, 'จริง หรือ ไม่จริง?', W / 2, TITLE_Y - 10, t, 0.2, 96, YEL, rot=-2)
        label(c, f'ข้อ {n}', 220, TITLE_Y - 10, t, 0.4, 52, TEAL, WHITE, rot=-8)
        s = card(c, 760, 560, 1060, 470, t, 0.6, WHITE)
        if s > 0:
            draw_img(c, text_img(statement, 60, INK, 0, INK, FONT_B, 14), 900, 560, s)
            c.save(); c.translate(380, 580); c.scale(s, s); draw_icon(c, t); c.restore()
        tv = max(2.5, D * t_verdict)
        if t > 1.5 and t < tv:
            for i in range(3):
                draw_img(c, text_img('?', 80, CORAL, 6, WHITE), 1450 + i * 110, 380 + math.sin(t * 6 + i) * 12, 1, 0.5 + 0.5 * math.sin(t * 4 + i))
        stamp(c, 1560, 600, verdict, t, tv, 1.0)
        if verdict and tv < t < tv + 2.5: confetti(c, t - tv)
        caps(c, t, D, pills, start=tv + 0.6)
    return f

s16 = myth(1, 'น้ำยาบ้วนปาก\nแก้กลิ่นปากได้หายขาด', False, lambda c, t: mouthwash(c, 0, 0, 0.9, t, 'smile'),
           ['ช่วยได้แค่ชั่วคราว', 'ต้องแก้ที่ต้นเหตุ'], 0.55)
s17 = myth(2, 'อมลูกอมบ่อยๆ\nช่วยดับกลิ่นปาก', False,
           lambda c, t: (candy(c, -40, -40, 1.1, -20, MINT), candy(c, 50, 90, 0.9, 25, LAV)),
           ['แค่กลบกลิ่น + มีน้ำตาลเสี่ยงฟันผุ', 'อยากเคี้ยว เลือกหมากฝรั่งไม่มีน้ำตาล'], 0.3)
def _sun(c, t):
    burst(c, 0, 0, t, 12, 90, 170, YEL, 255, 20); c.drawCircle(0, 0, 100, P(YEL)); c.drawCircle(0, 0, 100, P(INK, stroke=7))
    face(c, 0, 0, 'happy', 1, 0, 1.0)
s18 = myth(3, 'กลิ่นปากตอนเช้า\nเกิดได้กับทุกคน', True, _sun,
           ['น้ำลายน้อยตอนนอน', 'แปรงฟัน + อาหารเช้า + ดื่มน้ำ กลิ่นลดลง'], 0.3)
s19 = myth(4, 'กลิ่นปาก มาจาก\nกระเพาะอาหารเสมอ', False, lambda c, t: stomach(c, 0, 0, 0.95, t, 'worry'),
           ['ส่วนใหญ่มาจากในช่องปาก', 'ดูแลแล้วยังไม่หาย ค่อยปรึกษาหมอ'], 0.35)

def s20(c, t, D):   # fix 1: 2-2-2
    background(c, t, '#D8F3EE', '#F0FFF8')
    step_hdr(c, t, 1, 'แปรงฟันสูตร 2-2-2')
    gy = 880
    tooth(c, 420, gy - 260, 1.2, 'happy' if t > 2 else 'smile', 0, t=t, seed=2)
    bx = 420 + math.sin(t * 10) * 70 * seg(t, 0.8, 1.0) * (1 - seg(t, 5.5, 5.8))
    toothbrush(c, bx + 40, 430, -15, 1.1); bubbles(c, 420, 520, t, 10)
    cue(t, 0.8, 'scrub')
    names = ['ครั้งต่อวัน', 'นาทีต่อครั้ง', 'ชม. งดขนม\nหลังแปรง']
    for i, nm in enumerate(names):
        x = 1000 + i * 350; t0 = 1.6 + i * 1.6
        s = card(c, x, 540, 320, 330, t, t0, (YEL, MINT, '#FFD6E0')[i])
        if s > 0:
            draw_img(c, text_img('2', 150, CORAL, 10, INK), x, 480, s)
            draw_img(c, text_img(nm, 44, INK, 0, INK, FONT_B), x, 640, s)
    label(c, 'ยาสีฟันผสมฟลูออไรด์', 1350, 800, t, 6.5, 48, TEAL, WHITE)
    caps(c, t, D, ['สูตรของกรมอนามัย'], start=D * 0.75)

def s21(c, t, D):   # fix 2: clean the tongue
    background(c, t, '#FFE1EA', '#FFF5F8')
    step_hdr(c, t, 2, 'ทำความสะอาดลิ้น')
    cl = ease_io(seg(t, 1.5, 6.5))
    tongue_char(c, 760, 600, 1.25, t, 1.0, 'worry' if cl < 0.5 else 'joy', clean=cl)
    if 1.2 < t < 7.0:
        ph = ((t - 1.2) / 1.3) % 1
        tongue_cleaner(c, 760, lerp(430, 700, ease_io(ph)), 0.9, 0)
        cue(t, 1.3, 'scrub')
    if cl > 0.95: sparkle(c, 900, 470, 40 * math.sin(seg(t, 6.5, 7.2) * math.pi), YEL)
    # arrow back -> front
    k = ease_out(seg(t, 0.8, 1.6))
    if k > 0:
        c.drawLine(1180, 420, 1180, lerp(420, 760, k), P(INK, stroke=12)); c.drawLine(1180, 420, 1180, lerp(420, 760, k), P(TEAL, stroke=6))
        if k > 0.95:
            p = skia.Path(); p.moveTo(1150, 740); p.lineTo(1180, 790); p.lineTo(1210, 740); p.close(); fillp(c, p, TEAL, stroke=5)
    label(c, 'โคนลิ้น', 1380, 420, t, 0.9, 44, CORAL, WHITE)
    label(c, 'ปลายลิ้น', 1380, 760, t, 1.3, 44, TEAL, WHITE)
    caps(c, t, D, ['แปรงสีฟัน หรือที่ขูดลิ้น', 'ปัดเบาๆ ไม่ต้องกดแรง'])

def s22(c, t, D):   # fix 3: floss
    background(c, t, '#D0F4DE', '#F0FFF4')
    step_hdr(c, t, 3, 'ใช้ไหมขัดฟันทุกวัน')
    gy = 940
    out = seg(t, 3.4, 4.2)
    for j, x in enumerate((760, 1160)):
        tooth(c, x, gy - 300 + math.sin(t * 4 + j) * 4, 1.25, 'worry' if out < 1 else 'joy', (-1) ** j * 2, t=t, seed=j, shadow=False)
    gum_row(c, gy)
    gx = 960
    if out < 1:
        c.drawCircle(gx, 640 - 400 * ease_in(out), 26, P(GREEN)); c.drawCircle(gx, 640 - 400 * ease_in(out), 26, P(INK, stroke=5))
    k = ease_out(seg(t, 1.2, 3.2)) * (1 - 0.5 * seg(t, 4.4, 5.0))
    fy = lerp(300, 700, k)
    c.drawLine(gx - 30, 260, gx - 6, fy, P(INK, stroke=10)); c.drawLine(gx - 30, 260, gx - 6, fy, P(WHITE, stroke=5))
    c.drawLine(gx + 30, 260, gx + 6, fy, P(INK, stroke=10)); c.drawLine(gx + 30, 260, gx + 6, fy, P(WHITE, stroke=5))
    c.drawRoundRect(RR(gx, 250, 120, 70), 22, 22, P(SKY)); c.drawRoundRect(RR(gx, 250, 120, 70), 22, 22, P(INK, stroke=6))
    draw_img(c, text_img('ไหมขัดฟัน', 30, INK, 0), gx, 252, 1)
    cue(t, 1.2, 'slide_down', 0.3); cue(t, 3.4, 'pop'); cue(t, 4.2, 'ding')
    if t > 4.2:
        hand_text(c, 'สะอาดแล้ว!', gx + 380, 380, t, 4.3, 64, TEAL, -6)
        for i in range(4): sparkle(c, gx - 300 + i * 200, 420 + 30 * math.sin(t * 4 + i), 20, YEL)
    caps(c, t, D, ['เอาเศษอาหารที่แปรงเข้าไม่ถึงออกมา'])

def s23(c, t, D):   # fix 4: water
    background(c, t, '#E2F6FF', '#F0FBFF')
    step_hdr(c, t, 4, 'ดื่มน้ำ ไม่ให้ปากแห้ง')
    grow = 0.7 + 0.35 * ease_out(seg(t, 0.8, 2.5))
    water_glass(c, 520, 560, 1.3, t, 'joy', 0.85)
    saliva_drop(c, 860, 600, grow, t, 'happy')
    for i in range(3):
        k = pop(t, 0.8 + i * 0.3)
        if k > 0: sparkle(c, 700 + i * 80, 380 - i * 30, 22 * k, SKY)
    label(c, 'ดื่มน้ำเปล่าบ่อยๆ', 1420, 380, t, 1.0, 50, SKY, INK)
    label(c, 'กินอาหารเช้า', 1420, 560, t, 2.4, 50, YEL, INK)
    label(c, 'กินอาหารกลิ่นแรงแล้ว บ้วนปากด้วยน้ำ', 1360, 740, t, 3.8, 44, WHITE, INK, font=FONT_M)
    caps(c, t, D, ['น้ำลายดี ปากสดชื่น'], start=D * 0.7)

def s24(c, t, D):   # mini quiz
    background(c, t, '#FFF3B0', '#FFE7C7')
    burst(c, W / 2, 560, t, 16, 150, 1300, WHITE, 50, 6)
    big_title(c, 'ควิซ! ข้อไหนแก้ที่ต้นเหตุ?', W / 2, TITLE_Y, t, 0.2, 90, YEL, rot=-2)
    reveal = D * 0.78
    opts = [('ก.', 'อมลูกอมมิ้นต์'), ('ข.', 'ทำความสะอาด\nลิ้นและซอกฟัน'), ('ค.', 'ฉีดสเปรย์\nดับกลิ่น')]
    for i, (k, nm) in enumerate(opts):
        x = 420 + i * 540; t0 = 1.6 + i * 1.6
        dim = (0.45 if (t > reveal and i != 1) else 1.0)
        s = card(c, x, 600, 440, 420, t, t0, MINT if (t > reveal and i == 1) else WHITE, a=dim)
        if s > 0:
            draw_img(c, text_img(k, 90, CORAL, 8, INK), x, 470, s, dim)
            draw_img(c, text_img(nm, 54, INK, 0, INK, FONT_B, 12), x, 650, s, dim)
            if t > reveal:
                if i == 1: check(c, x + 150, 440, 2.0)
                else: cross(c, x + 150, 440, 1.4, CORAL, 200)
    if 5.5 < t < reveal:
        timer_clock(c, 1780, 330, seg(t, 5.5, reveal), 0.4, t)
        cue(t, 5.6, 'tick')
    cue(t, reveal, 'fanfare')
    if t > reveal:
        confetti(c, t - reveal)
        label(c, 'เฉลย ข้อ ข. ค่ะ!', W / 2, SUB_Y, t, reveal + 0.1, 58, TEAL, WHITE, rot=-2)

def s25(c, t, D):   # fix 5: dentist every 6 months
    background(c, t, '#D8F3EE', '#F0FFF8')
    step_hdr(c, t, 5, 'ตรวจฟันทุก 6 เดือน')
    dr_nawarat(c, 400, 360, 0.62, t, 'happy', wave=0.4, cape=0, hold='mirror')
    m = 1 + 5 * ease_io(seg(t, 1.0, 3.0))
    calendar(c, 900, 560, t, m)
    cue(t, 3.0, 'ding')
    tooth(c, 1170, 600, 0.9, 'joy' if t > 3 else 'smile', 0, t=t, seed=4)
    label(c, 'กรมอนามัยแนะนำ', 900, 790, t, 3.1, 40, TEAL, WHITE)
    label(c, 'ขูดหินปูน', 1600, 420, t, 3.4, 48, WHITE, INK)
    label(c, 'รักษาฟันผุ\nเหงือกอักเสบ', 1600, 580, t, 4.2, 44, WHITE, INK)
    label(c, 'แต่เนิ่นๆ', 1600, 740, t, 5.0, 48, YEL, INK)
    caps(c, t, D, ['ดูแลดีแล้วยังมีกลิ่น ให้หมอตรวจหาสาเหตุ'], start=D * 0.65)

def s26(c, t, D):   # recap
    background(c, t, '#FFE1EA', '#FFF3B0')
    big_title(c, 'สรุป 5 ข้อ ลมหายใจสดชื่น', W / 2, TITLE_Y, t, 0.2, 90, YEL)
    tips = ['แปรงฟัน\n2-2-2', 'ทำความ\nสะอาดลิ้น', 'ใช้ไหม\nขัดฟัน', 'ดื่มน้ำ\nบ่อยๆ', 'ตรวจฟัน\nทุก 6 เดือน']
    cols = [YEL, '#FFD6E0', MINT, '#CFF4FF', LAV]
    for i, tip in enumerate(tips):
        x = 230 + i * 365; t0 = 0.8 + i * 1.3
        s = card(c, x, 580, 320, 420, t, t0, cols[i], rot=(-1) ** i * 3)
        if s > 0:
            draw_img(c, text_img(tip, 50, INK, 0, INK, FONT_B, 12), x, 620, s)
            num_badge(c, i + 1, x, 400, t, t0 + 0.1, CORAL)
            cue(t, t0, 'ding')
    if t > 7.5: confetti(c, t - 7.5)

def s27(c, t, D):   # happy ending
    office(c, t)
    burst(c, W / 2, 560, t, 18, 150, 1400, WHITE, 70, 6)
    desk(c, 960, 800, 1300)
    person(c, 1400, 440, 0.68, 'happy', 0, t, shirt=FRIEND, seed=3)
    x, y, s = 560, 440, 0.68
    person(c, x, y, s, 'joy' if t > 1.5 else 'happy', 0, t, shirt=SHIRT)
    fresh_breath(c, 860, 470 + math.sin(t * 2) * 10, 0.9 * pop(t, 1.0), t)
    toothbrush(c, 300, 780, -40, 0.7 * pop(t, 0.5))
    water_glass(c, 1680, 720, 0.5 * pop(t, 0.8), t, 'joy')
    for i in range(3):
        heart(c, 1000 + i * 90, 360 - ((t * 60 + i * 40) % 160), 22, CORAL, 220)
    cue(t, 1.0, 'sparkle'); cue(t, 2.0, 'fanfare')
    if t > 2.0: confetti(c, t - 2.0)
    big_title(c, 'ลมหายใจสดชื่น มั่นใจ!', W / 2, TITLE_Y, t, 2.0, 100, YEL, rot=-2)
    caps(c, t, D, ['แปรงฟัน แปรงลิ้น ดื่มน้ำ', 'พร้อมลุยงานแล้ว!'])

STORY = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
         s21, s22, s23, s24, s25, s26, s27]
assert len(STORY) == len(NARR) - 2

# ---------------------------------------------------------------- durations: measured clips (durations.json) or estimates
_dp = os.path.join(HERE, 'durations.json')
_meas = json.load(open(_dp)) if os.path.exists(_dp) else {}
def dur(i, est_extra=1.1):
    if str(i) in _meas: return round(max(8.0, min(14.0, _meas[str(i)] + 0.15 + 0.9)), 2)
    n = len(re.sub(r'\[.*?\]', '', NARR[i]))
    return round(max(8.0, min(14.0, n / 11.5 + est_extra)), 2)

def bind(f, D):
    g = lambda c, t: f(c, t, D)
    return g

SCENES = [Scene(COVER, 4.0)] + [Scene(bind(f, dur(i + 1)), dur(i + 1)) for i, f in enumerate(STORY)] + \
    [Scene(endcard('ปรึกษาเรื่องกลิ่นปาก ทักมาได้เลย!'), round(max(6.0, _meas.get(str(len(NARR) - 1), 0) + 1.6), 2))]

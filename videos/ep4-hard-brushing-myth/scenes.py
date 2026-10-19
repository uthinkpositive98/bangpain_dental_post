"""ep4 แปรงแรงๆ ยิ่งสะอาด? — myth vs fact, kawaii house style (tools/kawaii.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from tools.kawaii import *  # noqa: F401,F403

# ---------------------------------------------------------------- one big tooth standing in the gum (front view)
GT_X, GT_Y, GT_S, G0 = 540, 880, 2.1, 1040
ROOT_TOP = '#FFF1CF'


def gum_band(c, gy, t=0, mood=None):
    p = skia.Path(); p.moveTo(-20, H + 20); p.lineTo(-20, G0 - 70)
    p.cubicTo(200, G0 - 70, 330, gy + 15, 540, gy + 15)
    p.cubicTo(750, gy + 15, 880, G0 - 70, W + 20, G0 - 70)
    p.lineTo(W + 20, H + 20); p.close()
    c.drawPath(p, lingrad((0, G0 - 70), (0, H), GUM, GUMD)); c.drawPath(p, P(INK, stroke=7))
    if mood:
        face(c, 540, gy + 230, mood, blink_at(t, 9), 0, 1.25)


def big_tooth(c, t, mood, rec=0.0, notch=0.0, shake=0.0, side=('smile', 'smile'), gum_mood=None):
    for j, x in enumerate((70, 1010)):
        tooth(c, x, GT_Y + 40 + math.sin(t * 4 + j) * 3, 1.7, side[j], 0, t=t, seed=j + 20, shadow=False)
    x = GT_X + shake; y = GT_Y + math.sin(t * 4) * 3
    tooth(c, x, y, GT_S, mood, t=t, seed=7, shadow=False)
    c.save(); c.translate(x, y); c.scale(GT_S, GT_S)
    c.save(); c.clipPath(TOOTH, doAntiAlias=True)
    yr = (G0 + 4 - y) / GT_S
    c.drawRect(skia.Rect.MakeLTRB(-200, yr, 200, 200), lingrad((0, yr), (0, 150), ROOT_TOP, BONED))
    c.restore()
    c.drawPath(TOOTH, P(INK, stroke=7))
    if notch > 0:
        yn = (G0 - 12 - y) / GT_S
        for sx in (-1, 1):
            q = skia.Path(); q.moveTo(sx * 74, yn - 16); q.lineTo(sx * (74 - 34 * notch), yn); q.lineTo(sx * 74, yn + 16); q.close()
            c.drawPath(q, P(BONED)); c.drawPath(q, P(INK, stroke=4))
    c.restore()
    gum_band(c, G0 + rec, t, gum_mood)


def brush_flat(c, x, y, rot=0, s=1.2, down=False):
    c.save(); c.translate(x, y); c.rotate(rot)
    if down: c.scale(1, -1)
    toothbrush(c, 0, 0, 0, s)
    c.restore()


# ---------------------------------------------------------------- scenes
def scene1(c, t):
    cue(t, 0.3, 'scrub'); cue(t, 1.7, 'scrub'); cue(t, 3.4, 'boing')
    background(c, t, '#9BF6FF', MINT)
    scrub = 0.3 < t < 3.4
    sh = math.sin(t * 50) * 6 if scrub else 0
    mood = 'squeeze' if scrub else ('shock' if t < 3.9 else 'worry')
    tooth(c, 540 + sh, 900 + math.sin(t * 4) * 4, 1.9, mood, 0, t=t, seed=1, shadow=False)
    gum_row(c, 1160)
    if t > 0.6:
        a = 255 * seg(t, 0.6, 0.9)
        sweat(c, 760, 680, 1.3, a); sweat(c, 330, 720, 1.0, a)
    if t < 4.0:
        k_in = ease_out(seg(t, 0.0, 0.3)); k_out = ease_in(seg(t, 3.4, 4.0))
        bx = 540 + (math.sin(t * 28) * 140 if scrub else 0) + (1 - k_in) * 900 + k_out * 1000
        brush_flat(c, bx, 1080, 0, 1.3)
        if scrub:
            for i in range(3):
                yy = 1000 + i * 34
                c.drawLine(bx - 280 - i * 30, yy, bx - 180 - i * 30, yy, P(INK, 120, stroke=7))
            bubbles(c, 540, 1000, t, 8)
    if scrub:
        hand_text(c, 'ขัด! ขัด! ขัด!', 540, 600, t, 0.5, 64, CORAL, -6)
    big_title(c, 'แปรงแรงๆ', W / 2, TITLE_Y - 20, t, 0.2, 108)
    big_title(c, 'ยิ่งสะอาด?', W / 2, TITLE_Y + 120, t, 1.2, 108, YEL, rot=-3, shake=16)
    subtitle(c, 'จริงหรือเปล่านะ...?', t, 3.6, y=1560)


def scene2(c, t):
    background(c, t, '#FFD6E0', '#FFF1E6')
    cue(t, 0.3, 'thud'); cue(t, 1.9, 'scrub', 0.5); cue(t, 4.3, 'chime')
    happy = t > 4.3
    tooth(c, 540, 900 + math.sin(t * 4) * 4, 1.9, 'joy' if happy else ('worry' if t < 1.8 else 'smile'), 0, t=t, seed=1, shadow=False)
    gum_row(c, 1160)
    bx = lerp(-260, 1340, ease_io(seg(t, 1.8, 4.4)))
    germs = [(380, 1000, '#9BE15D'), (480, 940, '#FFB86B'), (600, 1010, '#B8B8FF'), (700, 950, '#9BE15D')]
    for i, (gx, gy, col) in enumerate(germs):
        hit = bx - 40 > gx
        if not hit:
            germ(c, gx, gy, 0.46, t, i, col, 'shock' if bx > gx - 260 else 'hero')
        else:
            tt = (bx - 40 - gx) / 900.0
            if tt < 0.5:
                germ(c, gx + tt * 400, gy - tt * 900, 0.46 * (1 - tt), t, i, col, 'squeeze')
                puff(c, gx, gy + 20, tt * 2, 6, 90)
    if -200 < bx < 1300:
        brush_flat(c, bx, 1080, 0, 1.3)
        bubbles(c, bx - 60, 1010, t, 6)
    if happy:
        for i in range(6):
            ang = i * math.pi / 3 + t
            sparkle(c, 540 + math.cos(ang) * 290, 880 + math.sin(ang) * 260, 24 * (0.6 + 0.4 * math.sin(t * 6 + i)), YEL)
    big_title(c, 'ไม่จริงนะคะ!', W / 2, TITLE_Y, t, 0.3, 116, CORAL, rot=-3, shake=20)
    subtitle(c, 'คราบจุลินทรีย์นุ่มนิ่ม', t, 1.3, 2.95)
    subtitle(c, 'แปรงเบาๆ ก็ออกแล้ว!', t, 3.0, bg=YEL)
    subtitle(c, 'สำคัญที่ "ทั่วถึง" ไม่ใช่ "แรง"', t, 4.6, y=1660, bg=TEAL, fg=WHITE, size=52)


def scene3(c, t):
    background(c, t, '#E2ECFF', '#F4F0FF')
    cue(t, 0.9, 'scrub'); cue(t, 2.6, 'scrub'); cue(t, 5.1, 'sad')
    scrub = 0.8 < t < 4.6
    nt = ease_io(seg(t, 1.4, 4.6))
    mood = 'squeeze' if scrub else ('sad' if t > 4.6 else 'smile')
    big_tooth(c, t, mood, notch=nt, shake=(math.sin(t * 50) * 5 if scrub else 0),
              side=('worry', 'worry') if t > 1.0 else ('smile', 'smile'))
    if t < 5.2:
        k_in = ease_out(seg(t, 0.4, 0.8)); k_out = ease_in(seg(t, 4.6, 5.2))
        bx = 540 + (math.sin(t * 28) * 150 if scrub else 0) + (1 - k_in) * 1000 + k_out * 1100
        brush_flat(c, bx, 1100, 0, 1.25)
        if scrub:
            for i in range(3):
                c.drawLine(bx - 290 - i * 30, 1020 + i * 34, bx - 190 - i * 30, 1020 + i * 34, P(INK, 120, stroke=7))
    if scrub:
        hand_text(c, 'แรงไป!', 820, 640, t, 1.0, 62, CORAL, 8)
    if t > 5.0:
        hand_text(c, 'สึกเป็นร่อง...', 540, 1250, t, 5.0, 56, CORAL, -3)
        for sx in (-1, 1):
            r = 26 + 6 * math.sin(t * 6)
            c.drawCircle(540 + sx * 140, G0 - 12, r * 1.6, P(CORAL, 220, stroke=6))
    big_title(c, 'แปรงแรงเกินไป', W / 2, TITLE_Y, t, 0.3, 100)
    subtitle(c, '1. เคลือบฟันตรงคอฟันอาจสึก', t, 1.4, size=52)


def scene4(c, t):
    background(c, t, '#FFF3B0', '#FFE5D9')
    cue(t, 1.0, 'slide_down'); cue(t, 4.0, 'sad')
    rec = 80 * ease_io(seg(t, 1.0, 4.0))
    big_tooth(c, t, 'worry' if t > 1.2 else 'sad', rec=rec, notch=1.0, side=('worry', 'worry'),
              gum_mood='sad' if t > 0.6 else 'worry')
    if 1.0 < t < 4.3:
        a = 255 * min(seg(t, 1.0, 1.3), 1 - seg(t, 3.9, 4.3))
        for dx in (-250, 250):
            for k in range(2):
                yy = 1130 + ((t * 110 + k * 55) % 110)
                q = skia.Path(); q.moveTo(540 + dx - 26, yy); q.lineTo(540 + dx, yy + 32); q.lineTo(540 + dx + 26, yy)
                c.drawPath(q, P(CORAL, a, stroke=11))
    if t > 4.0:
        hand_text(c, 'รากฟันโผล่!', 820, 700, t, 4.0, 58, CORAL, 8)
        a = 255 * seg(t, 4.0, 4.3)
        c.drawLine(760, 760, 640, 1050, P(CORAL, a, stroke=9))
        q = skia.Path(); q.moveTo(632, 1012); q.lineTo(640, 1055); q.lineTo(674, 1028)
        c.drawPath(q, P(CORAL, a, stroke=9))
    big_title(c, 'เหงือกอาจร่นลง', W / 2, TITLE_Y, t, 0.3, 100)
    subtitle(c, '2. จนเห็นรากฟัน', t, 2.2, y=1560, size=54)


def scene5(c, t):
    background(c, t, '#D7F2FF', '#EEF9FF')
    zing = t > 1.7
    sh = math.sin(t * 60) * 7 * (1 - seg(t, 1.7, 3.2)) if zing else 0
    big_tooth(c, t, 'shock' if zing and t < 4.2 else ('worry' if zing else 'smile'), rec=80, notch=1.0, shake=sh,
              side=('shock', 'shock') if zing else ('smile', 'smile'))
    for i, (x, t0) in enumerate(((300, 0.5), (780, 0.9))):
        cue(t, t0 + 0.55, 'boing', 0.6)
        if t > t0:
            k = seg(t, t0, t0 + 0.55)
            yy = lerp(-150, 1270, ease_in(k)) - (abs(math.sin(seg(t, t0 + 0.55, t0 + 1.2) * math.pi)) * 80 * (1 - seg(t, t0 + 0.55, t0 + 1.2)) if k >= 1 else 0)
            ice_cube(c, x, yy, 1.05, t, i + 3, 'happy' if not zing else 'joy', (1 - k) * 40 * (1 if i else -1))
    for i in range(8):
        rr = random.Random(50 + i)
        sparkle(c, rr.uniform(80, 1000), (rr.uniform(500, 1400) + t * 60) % 900 + 500, 14 + 6 * math.sin(t * 4 + i), SKY, 200)
    if zing:
        cue(t, 1.7, 'thud')
        for i, (zx, zy, zr) in enumerate(((380, 1085, -20), (700, 1085, 20), (540, 1170, 0), (300, 960, -30), (790, 960, 30))):
            fl = 0.6 + 0.4 * abs(math.sin(t * 12 + i))
            zap(c, zx, zy, 0.9 * pop(t, 1.7 + i * 0.08) * fl, zr, 255)
        hand_text(c, 'จี๊ด!', 800, 640, t, 1.8, 96, CORAL, 10)
    big_title(c, 'เสียวฟันจี๊ด!', W / 2, TITLE_Y, t, 1.75, 108, YEL, rot=-3, shake=18)
    subtitle(c, '3. ดื่มเย็นๆ ก็อาจเสียวฟัน', t, 2.7, y=1560, size=52)


def scene6(c, t):
    background(c, t, '#FFF3B0', '#FFD6A5')
    land = 1.2
    cue(t, 0.0, 'sparkle'); cue(t, 0.5, 'slide_down', 0.3); cue(t, land, 'thud', 0.8); cue(t, 1.4, 'fanfare')
    if t > land:
        burst(c, 540, 1000, t, 18, 120, 1300 * ease_out(seg(t, land, land + 0.5)), WHITE, 110)
    gy = 1420
    c.drawOval(RR(540, gy + 4, 420 * seg(t, 0.5, land), 50), P(INK, 50))
    if t < land:
        y = lerp(-500, 1000, ease_in(seg(t, 0.4, land)))
        brush_buddy(c, 540, y, 1.2, 'hero', t, cape=1.0)
        if t > 0.5: motion_lines(c, 540, y - 420, 260, 255)
    else:
        k = seg(t, land, land + 0.5)
        sq = 1 - 0.16 * math.sin(k * math.pi) * (1 - k)
        brush_buddy(c, 540, 1000 + (1 - sq) * 400, 1.2, 'hero' if t < 5.6 else 'happy', t, sq=sq, cape=1.0)
        puff(c, 540, gy, seg(t, land, land + 0.8), 9, 300)
    for i in range(4):
        ang = t * 2 + i * math.pi / 2
        sparkle(c, 540 + math.cos(ang) * 300, 800 + math.sin(ang) * 120, 22 * seg(t, land, land + 0.4), YEL)
    big_title(c, 'ฮีโร่ตัวจริง!', W / 2, TITLE_Y - 20, t, 1.4, 112, YEL, rot=-4, shake=10)
    big_title(c, 'แปรงขนนุ่ม', W / 2, TITLE_Y + 130, t, 2.8, 100)
    subtitle(c, 'อ่อนโยนกับฟันและเหงือก', t, 3.8, y=1580, size=54, bg=TEAL, fg=WHITE)
    subtitle(c, 'แปรงเบาๆ อย่างถูกวิธี', t, 4.9, y=1700, size=54, bg=TEAL, fg=WHITE)


def scene7(c, t):
    background(c, t, '#D0F4DE', '#E4FDE1')
    press = 0.9 < t < 2.8
    cue(t, 0.9, 'drill', 0.5); cue(t, 2.8, 'slide_up'); cue(t, 3.3, 'ding')
    val = 0.15 + 0.8 * ease_out(seg(t, 0.9, 1.8)) - 0.82 * ease_io(seg(t, 2.8, 3.5))
    val += math.sin(t * 40) * 0.03 if press else 0
    gauge(c, 540, 820, val, 1.15)
    good = t > 3.3
    tooth(c, 340, 1270, 1.3, 'squeeze' if press else ('joy' if good else 'smile'), 0,
          1 - 0.08 * seg(t, 0.9, 1.4) * (1 - seg(t, 2.8, 3.2)), t=t, seed=2)
    dx = -40 * ease_out(seg(t, 0.9, 1.3)) * (1 - ease_io(seg(t, 2.8, 3.3)))
    brush_buddy(c, 610 + dx + (math.sin(t * 40) * 4 if press else 0), 1270, 0.6, 'squeeze' if press else ('happy' if good else 'smile'),
                t, 1, rot=-35, sq=1 - 0.1 * ease_out(seg(t, 0.9, 1.3)) * (1 - seg(t, 2.8, 3.3)))
    if press:
        hand_text(c, 'แรงไป!', 860, 1120, t, 1.3, 66, CORAL, 8)
        sweat(c, 450, 1080, 1.1, 255 * seg(t, 1.2, 1.4))
    if good:
        hand_text(c, 'พอดี!', 220, 1010, t, 3.3, 72, TEAL, -8)
        for i in range(4):
            sparkle(c, 540 + math.cos(t * 3 + i * 1.6) * 360, 1150 + math.sin(t * 3 + i * 1.6) * 120, 22, YEL)
    step_header(c, t, 1, 'จับแปรงเบาๆ')
    subtitle(c, 'ไม่ต้องกดแรงนะคะ', t, 1.2, 2.75, y=1600)
    subtitle(c, 'จับเบาๆ เหมือนจับปากกา', t, 3.0, y=1600, bg=YEL)


def scene8(c, t):
    background(c, t, '#BDE0FE', '#E7F5FF')
    cue(t, 1.0, 'scrub', 0.5); cue(t, 5.3, 'chime')
    big_tooth(c, t, 'happy' if t > 1.2 else 'smile', side=('happy', 'happy') if t > 2 else ('smile', 'smile'))
    k = ease_out(seg(t, 0.4, 1.0))
    jig = math.sin(t * 16) * 14 if 1.0 < t < 5.3 else 0
    hx, hy = lerp(1300, 470, k) + jig, lerp(700, 985, k)
    brush_flat(c, hx, hy, -35, 1.15, down=True)
    if 1.0 < t < 5.3:
        bubbles(c, 470, 1000, t, 8)
    if t > 1.2:
        a = 255 * seg(t, 1.2, 1.5)
        c.drawLine(360, 1040, 700, 1040, P(WHITE, a, stroke=8))
        hand_text(c, '45°', 300, 1150, t, 1.3, 64, '#7B6CF6', -4)
    if t > 3.0:
        hand_text(c, 'สั้นๆ เบาๆ', 300, 600, t, 3.0, 60, TEAL, -8)
    if t > 5.3:
        for i in range(5):
            sparkle(c, 380 + i * 80, 1030 + math.sin(t * 5 + i) * 20, 22 * (0.6 + 0.4 * math.sin(t * 6 + i)), YEL)
    step_header(c, t, 2, 'เอียงเข้าหาขอบเหงือก')
    subtitle(c, 'เอียงหัวแปรงเข้าหาขอบเหงือก', t, 1.0, 3.35, y=1560, size=52)
    subtitle(c, 'ขยับสั้นๆ เบาๆ ทีละ 2–3 ซี่', t, 3.4, y=1560, size=52, bg=YEL)


def scene9(c, t):
    background(c, t, '#E0C3FC', '#F8E1FF')
    for k in range(4): cue(t, 1.0 + k * 0.6, 'tick')
    cue(t, 3.4, 'ding'); cue(t, 4.3, 'boing'); cue(t, 5.9, 'sparkle')
    frac = ease_io(seg(t, 0.8, 3.4))
    s = pop(t, 0.5)
    if s > 0:
        c.save(); c.translate(300, 860); c.scale(s, s); c.translate(-300, -860)
        timer_clock(c, 300, 860, frac, 1.0, t if frac < 1 else 0)
        c.restore()
        draw_img(c, text_img('2 นาที', 56, INK, 6, WHITE), 300, 1060, s)
    if t > 3.4 and t < 4.2:
        burst(c, 300, 860, t, 12, 160, 160 + 160 * ease_out(seg(t, 3.4, 3.9)), YEL, 160 * (1 - seg(t, 3.7, 4.2)))
    fluff = 1 + 1.4 * ease_out(seg(t, 4.2, 4.9)) - 1.4 * ease_out(seg(t, 5.9, 6.3))
    worn = 4.3 < t < 5.9
    s2 = pop(t, 0.9)
    if s2 > 0:
        c.save(); c.translate(790, 1000); c.scale(s2, s2); c.translate(-790, -1000)
        brush_buddy(c, 790, 1000, 0.68, 'worry' if worn else ('joy' if t > 5.9 else 'smile'), t, 5, fluff=fluff)
        c.restore()
    if worn:
        hand_text(c, 'ขนบาน!', 800, 690, t, 4.4, 60, CORAL, 8)
    if t > 5.9:
        puff(c, 790, 830, seg(t, 5.9, 6.6), 8, 200)
        label(c, 'ใหม่!', 900, 700 + math.sin(t * 5) * 8, t, 6.0, 44, CORAL, WHITE, 26, 12, 8)
    step_header(c, t, 3, 'แปรง 2 นาที วันละ 2 ครั้ง')
    label(c, 'แปรงนาน 2 นาที วันละ 2 ครั้ง', W / 2, 1320, t, 1.0, 50, TEAL, WHITE, font=FONT_M, rot=2)
    label(c, 'ใช้ยาสีฟันผสมฟลูออไรด์', W / 2, 1440, t, 2.6, 50, CORAL, WHITE, font=FONT_M, rot=-2)
    label(c, 'ขนแปรงบาน = เปลี่ยนแปรงใหม่', W / 2, 1560, t, 4.6, 50, '#7B6CF6', WHITE, font=FONT_M, rot=1)


def scene10(c, t):
    cue(t, 0.2, 'fanfare', 0.5)
    background(c, t, '#A0E7E5', '#FBE7C6')
    burst(c, 540, 1000, t, 16, 150, 1200, WHITE, 70, 8)
    gy = 1180
    for i, x in enumerate(ROW_X):
        ph = (t * 2.4 + i * 0.5) % 1.0
        j = -abs(math.sin(ph * math.pi)) * 70 * (1 - seg(t, 5.2, 5.8))
        sq = 1 + 0.08 * math.cos(ph * 2 * math.pi) * (1 - seg(t, 5.2, 5.8))
        tooth(c, x, gy - 120 + j, 0.95, 'joy', math.sin(t * 5 + i) * 6, sq, t=t, seed=i)
    gum_row(c, gy)
    brush_buddy(c, 540, 680 + math.sin(t * 4) * 10, 0.42, 'joy', t, 8, rot=math.sin(t * 3) * 8)
    confetti(c, t)
    big_title(c, 'เบาๆ แต่ทั่วถึง!', W / 2, TITLE_Y - 20, t, 0.3, 104, YEL, rot=-3)
    chips = ['ถนอมเคลือบฟัน', 'ถนอมเหงือก', 'ลดโอกาสเสียวฟัน']
    cols = [TEAL, CORAL, '#7B6CF6']
    for i, ch in enumerate(chips):
        label(c, ch, W / 2 + (-30 if i % 2 else 30), 1330 + i * 112, t, [0.6, 1.5, 2.4][i], 52, cols[i], WHITE,
              rot=(-2 if i % 2 else 2), font=FONT_M)
    s = pop(t, 3.6)
    if s > 0:
        img = text_img('*ถ้าเสียวฟันหรือเหงือกร่น\nให้ทันตแพทย์ตรวจนะคะ', 42, INK, 0, INK, FONT_R)
        c.save(); c.translate(W / 2, 1700); c.scale(s, s)
        c.drawRoundRect(RR(0, 0, img.width() + 60, img.height() + 40), 24, 24, P(WHITE, 225))
        c.restore()
        draw_img(c, img, W / 2, 1700, s)


SCENES = [Scene(scene1, 5.5), Scene(scene2, 6.5), Scene(scene3, 6.5), Scene(scene4, 6.0), Scene(scene5, 6.0),
          Scene(scene6, 6.5), Scene(scene7, 6.0), Scene(scene8, 6.5), Scene(scene9, 7.0), Scene(scene10, 6.5),
          Scene(endcard('ปรึกษาเรื่องการแปรงฟัน ทักมาได้เลย!'), 6.0)]

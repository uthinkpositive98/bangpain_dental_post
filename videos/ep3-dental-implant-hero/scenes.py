"""ep3 รากฟันเทียม ฮีโร่ไทเทเนียม — the worked example of the kawaii house style (tools/kawaii.py).
Scene durations here are the narrated lengths of the original single-take voiceover; a new episode uses nominal
lengths and lets tools/kawaii_render.py stretch them to its per-scene narration."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from tools.kawaii import *  # noqa: F401,F403


def scene1(c, t):
    T0 = t; t = t + 0.75
    cue(T0, 0.45, 'boing'); cue(T0, 2.7, 'thud')
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
    cue(T0, 3.4, 'boing'); cue(T0, 5.2, 'slide_down')
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

def scene3(c, t):
    background(c, t, '#E2ECFF', '#F4F0FF')
    dip = ease_io(seg(t, 1.5, 4.5)) * 120
    cue(t, 1.8, 'sad')
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
    cue(t, 0.0, 'sparkle'); cue(t, 0.5, 'slide_down', 0.3); cue(t, land, 'thud', 0.8); cue(t, 1.4, 'fanfare'); cue(t, 6.4, 'ding')
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

def scene5(c, t):
    background(c, t, '#D0F4DE', '#E4FDE1')
    top = 1200
    bone_gum(c, top, 0)
    cut_neighbors(c, t, ('smile', 'smile') if t < 4.7 else ('happy', 'happy'))
    k = ease_io(seg(t, 1.0, 4.7))
    cue(t, 1.0, 'drill'); cue(t, 4.7, 'click'); cue(t, 4.72, 'ding')
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
    for k in range(5): cue(t, 1.8 + k * 0.8, 'tick')
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
    cue(t, 1.1, 'click'); cue(t, 3.0, 'chime')
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
    cue(t, 0.2, 'fanfare', 0.5)
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
    cue(t, 1.9, 'scrub')
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


SCENES = [Scene(scene1, 5.79), Scene(scene2, 8.09), Scene(scene3, 5.44), Scene(scene4, 7.55), Scene(scene5, 6.20),
          Scene(scene6, 6.92), Scene(scene7, 4.75), Scene(scene8, 5.57), Scene(scene9, 9.69),
          Scene(endcard('ปรึกษาเรื่องรากฟันเทียม ทักมาได้เลย!'), 6.5)]

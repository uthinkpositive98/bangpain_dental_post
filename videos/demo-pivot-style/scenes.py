"""Style test for the Pivot-style engine: 4 story shots + the clinic end card (silent)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tools.pivot import *  # noqa

TON = STAND.but(x=540, y=1330, s=1.25)


# 1 — Hook: ต้น strolls through the meadow munching candy, very pleased with himself
def s1(t):
    p = walk(TON.but(mood="happy", rsh=70, rel=120, hand_r=candy()), t, speed=120, x0=300)
    if t > 2.4:
        p = p.but(mood="big")
    out = drifting_clouds(t, 520) + stickman(p, t, seed=1) + ambient(t, "petals", 14, 2)
    out += sparkle(p.x + 120, p.y - 420, 18 + 6 * math.sin(t * 6))
    for i in range(3):                                     # candy wrappers fluttering behind him
        k = (t * .8 + i * .33) % 1
        out += (f'<g transform="translate({p.x - 160 - k * 260:.0f},{p.y + 120 - k * 80 - 30 * math.sin(k * 9):.0f}) '
                f'rotate({k * 400:.0f})"><path d="M-14 -8 h28 v16 h-28z" fill="{["#ff6fa8", "#ffd84a", "#7ad0ff"][i]}" '
                f'stroke="{INK}" stroke-width="3"/></g>')
    return out


# 2 — Bathroom, bedtime: he looks at the toothbrush ... shrugs it off
def s2(t):
    B = TON.but(x=790, y=1300, s=1.15)
    track = [(0, B.but(mood="sleepy", look=(-1, 0), lsh=10, rsh=10)),
             (1.2, THINK.but(x=790, y=1300, s=1.15, look=(-1, -.3))),
             (2.2, SHRUG.but(x=790, y=1300, s=1.15, mood="bored"), "back"),
             (3.2, B.but(mood="smug", lean=6, rsh=20, lsh=20)),
             (4, walk(B.but(mood="smug"), 0.4, speed=160, x0=800))]
    out = ambient(t, "bubbles", 10, 3, (100, 900, 700, 1500)) + actor(track, t, seed=2)
    out += speech_bubble(560, 760, "ไว้พรุ่งนี้~", t, 2.3, 400, 130, (150, 150))
    if 1.0 < t < 2.2:
        out += pop_text(1000, 860, "?", t, 1.0, 120, "#fff", INK, 8)
    return out


# 3 — Inside the mouth: germs party on the tooth, a cavity grows
def s3(t):
    dec = clamp((t - .6) / 2.6)
    out = tooth_icon(540, 950, 1.9, "worried" if dec < .6 else "cry", dec, t)
    for i, (gx, gy, c) in enumerate(((300, 1250, "#9b6bd6"), (790, 1230, "#7ac943"), (560, 1340, "#ff8a5b"),
                                     (420, 700, "#7ac943"))):
        out += germ(gx + 30 * math.sin(t * 2 + i), gy, t, 1.1, c, "smug" if i % 2 else "big", seed=i)
    out += pop_text(540, 420, "ฟันผุแล้ว!", t, 2.6, 110, "#ff6b6b", INK, -5)
    return out


# 4 — Clinic: หมอฟันยิ้ม pops in to help, ต้น jumps for joy
def s4(t):
    out = mascot(720, 1180, t, 1.0, "big", wave=clamp(t - .4))
    tp = TON.but(x=300, y=1330, s=1.15)
    if t < 1.2:
        p = tween(tp.but(mood="surprised", lsh=40, rsh=40), tp.but(mood="surprised", lsh=120, lel=40, rsh=120, rel=40), ease(t / 1.2))
    else:
        p = hop(CHEER.but(x=300, y=1330, s=1.15), t - 1.2, 110, .55)
    out += stickman(p, t, seed=4)
    out += ambient(t, "pollen", 22, 4)
    for i in range(6):
        a = t * 2 + i
        out += sparkle(540 + 380 * math.cos(a), 900 + 160 * math.sin(a * 1.3), 16)
    return out


SCENES = [
    Scene("meadow", s1, "กินขนมหวานทั้งวัน ฟันยังโอเคอยู่ไหมนะ?", title="ขนมหวานทั้งวัน",
          cam=[(0, (1.0, 120, 0)), (4, (1.08, -60, -20))]),
    Scene("bathroom", s2, "ถึงเวลานอน... ขี้เกียจแปรงฟัน ไว้พรุ่งนี้ละกัน", title="ขี้เกียจแปรง",
          cam=[(0, (1.0, 0, 0)), (4, (1.1, -40, 30))]),
    Scene("mouth", s3, "แต่คืนนั้น เชื้อโรคจัดปาร์ตี้ กัดกินฟันทั้งคืน!", title=None,
          cam=[(0, (1.0, 0, 0)), (2.6, (1.04, 0, 0)), (4, (1.22, 0, 120), "out")],
          shake=lambda t: shake(t, 9) if t > 2.6 else (0, 0)),
    Scene("clinic", s4, "ไม่ต้องกลัวค่ะ ตรวจฟันเร็ว รักษาง่าย จบไว", title="เจอเร็ว จบเร็ว",
          cam=[(0, (1.12, 0, 60)), (4, (1.0, 0, 0))]),
    Scene("endcard", endcard_fg, "ตรวจสุขภาพฟันได้ที่ คลินิกทันตกรรมบางปะอิน โทร 092-359-5963 ค่ะ", sub="", dur=5,
          cam=[(0, (1.0, 0, 0)), (5, (1.03, 0, 0))]),
]

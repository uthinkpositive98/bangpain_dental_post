"""Episode 1 scenes — worked example of composing scenes with tools/cartoon.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.cartoon import *  # noqa

scenes = {}

# 1 Hook — lazy on sofa at night, dusty toothbrush
scenes[1] = page(f'''
<rect x="0" y="1300" width="{W}" height="620" fill="#4a3b5c"/>
<rect x="110" y="330" width="330" height="420" rx="16" fill="#0f1830" stroke="{K}" stroke-width="10"/>
<circle cx="350" cy="430" r="46" fill="#fff6c9"/><circle cx="370" cy="418" r="40" fill="#0f1830"/>
<g fill="#fff">{''.join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x,y in [(170,400),(230,520),(300,610),(180,660),(390,560)])}</g>
<line x1="275" y1="330" x2="275" y2="750" stroke="{K}" stroke-width="8"/><line x1="110" y1="540" x2="440" y2="540" stroke="{K}" stroke-width="8"/>
<circle cx="880" cy="760" r="300" fill="url(#lamp)"/>
<path d="M840 640 h80 l30 90 h-140 z" fill="#ffd27a" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>
<line x1="880" y1="730" x2="880" y2="1240" stroke="{K}" stroke-width="10"/><path d="M820 1250 h120" stroke="{K}" stroke-width="12" stroke-linecap="round"/>
<rect x="60" y="1040" width="760" height="300" rx="60" fill="#7b5ea7" stroke="{K}" stroke-width="10"/>
<rect x="40" y="980" width="130" height="330" rx="50" fill="#8e70ba" stroke="{K}" stroke-width="10"/>
<rect x="710" y="980" width="130" height="330" rx="50" fill="#8e70ba" stroke="{K}" stroke-width="10"/>
<rect x="100" y="1330" width="40" height="60" fill="{K}"/><rect x="740" y="1330" width="40" height="60" fill="{K}"/>
{person(560, 1010, 0.95, "bored", rot=-82, arms=((-30, -150), (40, -150)), legs=((-70, 170), (60, 190)))}
<rect x="400" y="830" width="70" height="115" rx="12" fill="#2a2a2e" stroke="{K}" stroke-width="7" transform="rotate(-70 435 887)"/>
<rect x="410" y="842" width="50" height="90" rx="6" fill="#9fe7ff" transform="rotate(-70 435 887)"/>
<rect x="640" y="1480" width="380" height="24" rx="8" fill="#c79a6a" stroke="{K}" stroke-width="7"/>
<rect x="700" y="1360" width="70" height="120" rx="10" fill="#bfe9f5" stroke="{K}" stroke-width="7"/>
<g transform="rotate(-12 800 1420)"><rect x="790" y="1290" width="18" height="190" rx="8" fill="#ff9e80" stroke="{K}" stroke-width="6"/>
<rect x="784" y="1262" width="30" height="46" rx="6" fill="#fff" stroke="{K}" stroke-width="6"/></g>
<g fill="#b9b2a8" opacity=".9">{''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x,y,r in [(800,1300,8),(786,1340,6),(812,1380,7),(796,1420,5),(818,1450,6),(728,1372,5),(752,1400,6)])}</g>
<path d="M880 1296 q40 30 100 10 M900 1296 l20 60 M940 1300 l0 70 M980 1306 l-14 60 M890 1330 q50 20 90 0" fill="none" stroke="#ddd" stroke-width="3"/>
''', "url(#night)")

# 2 Day 1 — film on tooth, germs pitching tents
scenes[2] = page(f'''
<rect width="{W}" height="{H}" fill="#f7b3b8"/>
<path d="M0 1500 Q540 1350 1080 1500 V1920 H0Z" fill="#e8848f" stroke="{K}" stroke-width="10"/>
<g transform="translate(130,520) scale(3.15)"><path d="{tooth_path()}" fill="#fffdf6" stroke="{K}" stroke-width="3.2" stroke-linejoin="round"/></g>
<g transform="translate(130,520) scale(3.15)"><path d="{tooth_path()}" fill="#d9f7c6" opacity=".22"/></g>
<path d="M220 640 q140 -60 280 -10" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round" opacity=".8"/>
<path d="M260 760 q60 -20 120 -4" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".6"/>
<g>
 <path d="M300 560 l70 -110 l70 110 z" fill="{ORANGE}" stroke="{K}" stroke-width="7" stroke-linejoin="round"/><path d="M370 450 v110" stroke="{K}" stroke-width="5"/>
 <path d="M600 520 l80 -120 l80 120 z" fill="#ffd54a" stroke="{K}" stroke-width="7" stroke-linejoin="round"/><path d="M680 400 v120" stroke="{K}" stroke-width="5"/>
</g>
{germ(250, 560, 1.3, "#9b59d0")}
{germ(500, 540, 1.2, "#7ac943", hat=f'<rect x="-30" y="-90" width="60" height="60" rx="10" fill="#4a90e2" stroke="{K}" stroke-width="5" transform="rotate(10)"/>')}
{germ(820, 530, 1.4, "#9b59d0", flip=True)}
{germ(700, 700, 1.0, "#7ac943")}
<g fill="#fff">{''.join(f'<circle cx="{x}" cy="{y}" r="{r}" opacity=".7"/>' for x,y,r in [(160,420,10),(940,380,8),(980,820,12),(110,980,9)])}</g>
''', "#f7b3b8")

# 3 Day 3 — office, coworker holds nose
scenes[3] = page(f'''
<rect x="0" y="0" width="{W}" height="1380" fill="#f2efe6"/>
<rect x="0" y="1380" width="{W}" height="540" fill="#c7b9a0"/>
<rect x="620" y="260" width="380" height="420" rx="12" fill="#bfe9f5" stroke="{K}" stroke-width="9"/>
<path d="M620 470 h380 M810 260 v420" stroke="{K}" stroke-width="7"/>
<path d="M650 640 l90 -140 l70 90 l60 -60 l100 110" fill="#9dd5c9" stroke="{K}" stroke-width="5" stroke-linejoin="round"/>
<rect x="60" y="300" width="300" height="200" rx="10" fill="#fff" stroke="{K}" stroke-width="7"/>
<path d="M100 450 l60 -70 l50 40 l70 -90" fill="none" stroke="{TEAL}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="40" y="1300" width="1000" height="40" rx="10" fill="#9b7350" stroke="{K}" stroke-width="8"/>
<rect x="80" y="1340" width="30" height="300" fill="#7a5a3e" stroke="{K}" stroke-width="6"/><rect x="970" y="1340" width="30" height="300" fill="#7a5a3e" stroke="{K}" stroke-width="6"/>
<rect x="430" y="1170" width="220" height="130" rx="10" fill="#3a3a40" stroke="{K}" stroke-width="7"/><rect x="520" y="1300" width="40" height="10" fill="{K}"/>
<g transform="translate(900,1200)"><path d="M-40 100 h80 l-12 -100 h-56 z" fill="{ORANGE}" stroke="{K}" stroke-width="6"/>
<path d="M0 0 q-60 -80 -20 -150 M0 0 q50 -70 30 -160 M0 0 q-10 -90 10 -190" fill="none" stroke="#3f9e5a" stroke-width="16" stroke-linecap="round"/></g>
{person(330, 1250, 1.05, "talk", arms=((-90, 90), (120, -40)))}
{person(770, 1250, 1.05, "squint", shirt="#4a90e2", hair=False, rot=8, arms=((-36, -104), (-120, 40)))}
<g fill="none" stroke="#7ac943" stroke-width="12" stroke-linecap="round" opacity=".85">
<path d="M420 900 q30 -30 60 0 t60 0 t60 0"/><path d="M430 960 q30 -30 60 0 t60 0 t60 0"/><path d="M440 840 q30 -30 60 0 t60 0"/></g>
<g fill="#7ac943" opacity=".8"><circle cx="630" cy="820" r="12"/><circle cx="650" cy="990" r="9"/></g>
<path d="M880 760 l40 -30 M900 800 l50 -10 M880 720 l30 -50" stroke="{K}" stroke-width="6" stroke-linecap="round"/>
''', "#f2efe6")

# 4 Tartar — germs build brick wall at gumline
scenes[4] = page(f'''
<rect width="{W}" height="{H}" fill="#f7b3b8"/>
<g transform="translate(150,330) scale(3.0)"><path d="{tooth_path()}" fill="#fffdf6" stroke="{K}" stroke-width="3.3" stroke-linejoin="round"/></g>
<path d="M0 1080 Q270 980 540 1060 Q810 980 1080 1080 V1920 H0 Z" fill="#e8848f" stroke="{K}" stroke-width="10"/>
<path d="M190 1000 Q540 930 900 1000 L900 1100 Q540 1030 190 1100 Z" fill="url(#bricks)" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>
<g transform="translate(250,880)"><path d="M0 0 q40 -60 100 -40 l-10 40 z" fill="#c9c9c9" stroke="{K}" stroke-width="6"/></g>
{germ(200, 930, 1.2, "#9b59d0", hat=f'<path d="M-36 -40 q36 -50 72 0 z" fill="#ffd54a" stroke="{K}" stroke-width="5"/><rect x="-44" y="-44" width="88" height="10" rx="4" fill="#ffd54a" stroke="{K}" stroke-width="5"/>')}
{germ(540, 880, 1.3, "#7ac943", hat=f'<path d="M-36 -40 q36 -50 72 0 z" fill="#ffd54a" stroke="{K}" stroke-width="5"/><rect x="-44" y="-44" width="88" height="10" rx="4" fill="#ffd54a" stroke="{K}" stroke-width="5"/>')}
{germ(860, 920, 1.2, "#9b59d0", flip=True, hat=f'<path d="M-36 -40 q36 -50 72 0 z" fill="#ffd54a" stroke="{K}" stroke-width="5"/><rect x="-44" y="-44" width="88" height="10" rx="4" fill="#ffd54a" stroke="{K}" stroke-width="5"/>')}
<g transform="translate(700,820) rotate(-30)"><rect x="-10" y="-120" width="20" height="120" fill="#8a6a2e" stroke="{K}" stroke-width="5"/><path d="M-30 -120 h60 l-10 -30 h-40 z" fill="#9aa5ab" stroke="{K}" stroke-width="5"/></g>
<g transform="translate(540,1420) rotate(-15)"><rect x="-260" y="-26" width="420" height="52" rx="24" fill="#4fb3b8" stroke="{K}" stroke-width="8"/>
<rect x="160" y="-40" width="150" height="80" rx="14" fill="#fff" stroke="{K}" stroke-width="8"/>
<path d="M175 -40 v-50 M200 -40 v-50 M225 -40 v-50 M250 -40 v-50 M275 -40 v-50 M300 -40 v-50" stroke="#7fd3ff" stroke-width="12" stroke-linecap="round"/></g>
<path d="M800 1220 q30 -40 70 -30 M820 1270 q40 -20 80 0 M760 1200 q10 -50 50 -60" fill="none" stroke="{K}" stroke-width="7" stroke-linecap="round"/>
''', "#f7b3b8")

# 5 Week 2 — mirror, worried, red puffy gums inset
scenes[5] = page(f'''
<rect width="{W}" height="{H}" fill="url(#tiles)"/>
<rect x="140" y="220" width="800" height="760" rx="40" fill="#d6f1f3" stroke="{K}" stroke-width="12"/>
<path d="M220 300 l120 -40 M240 360 l200 -80" stroke="#fff" stroke-width="18" stroke-linecap="round" opacity=".8"/>
<g transform="translate(540,560)">
 <ellipse cx="0" cy="0" rx="300" ry="200" fill="url(#mouth)" stroke="{K}" stroke-width="10"/>
 <path d="M-280 -40 Q0 -150 280 -40 L280 -110 Q0 -230 -280 -110 Z" fill="#ff5a6e" stroke="{K}" stroke-width="8"/>
 <g fill="#fffdf6" stroke="{K}" stroke-width="6">{''.join(f'<rect x="{x}" y="-118" width="80" height="96" rx="20"/>' for x in range(-250, 250, 84))}</g>
 <path d="M-280 -40 Q0 -100 280 -40" fill="none" stroke="#c9303f" stroke-width="20"/>
 <g fill="#ff8a96" opacity=".9">{''.join(f'<ellipse cx="{x}" cy="-110" rx="34" ry="18"/>' for x in range(-210, 260, 84))}</g>
 <path d="M-200 100 Q0 180 200 100" fill="none" stroke="#ff8a80" stroke-width="40" stroke-linecap="round"/>
</g>
<rect x="260" y="1220" width="560" height="140" rx="30" fill="#fff" stroke="{K}" stroke-width="10"/>
<ellipse cx="540" cy="1290" rx="160" ry="40" fill="#c9eef0" stroke="{K}" stroke-width="6"/>
{person(300, 1700, 0.95, "worried", arms=((90, -160), (-80, 90)), legs=((-50, 190), (50, 190)))}
<g transform="translate(395,1355) rotate(-50)"><rect x="-8" y="-150" width="16" height="150" rx="6" fill="#ff9e80" stroke="{K}" stroke-width="5"/>
<rect x="-14" y="-178" width="28" height="40" rx="6" fill="#fff" stroke="{K}" stroke-width="5"/><circle cx="18" cy="-166" r="7" fill="#e5394b"/></g>
<path d="M240 1220 q-10 -30 10 -50 M200 1250 q-30 -20 -20 -50" fill="none" stroke="#4fa3e0" stroke-width="10" stroke-linecap="round"/>
''', "#e8f6f5")

# 6 Week 3 — germ party in the mouth
teeth_top = ''.join(f'<path d="M{x} 360 h90 v100 q-45 30 -90 0 z" fill="#fffdf6" stroke="{K}" stroke-width="6"/>' for x in range(110, 960, 96))
teeth_bot = ''.join(f'<path d="M{x} 1640 h90 v-100 q-45 -30 -90 0 z" fill="#fffdf6" stroke="{K}" stroke-width="6"/>' for x in range(110, 960, 96))
party = f'<path d="M-20 -40 l20 -60 l20 60 z" fill="{ORANGE}" stroke="{K}" stroke-width="5"/><circle cx="0" cy="-102" r="8" fill="#ffd54a" stroke="{K}" stroke-width="4"/>'
scenes[6] = page(f'''
<rect width="{W}" height="{H}" fill="url(#mouth)"/>
<rect x="60" y="250" width="960" height="140" rx="60" fill="#e8848f" stroke="{K}" stroke-width="8"/>
<rect x="60" y="1610" width="960" height="140" rx="60" fill="#e8848f" stroke="{K}" stroke-width="8"/>
{teeth_top}{teeth_bot}
<circle cx="606" cy="420" r="18" fill="#f3efe0" stroke="#d8d2bd" stroke-width="3"/>
<path d="M540 300 v200" stroke="#ccc" stroke-width="5"/>
<circle cx="540" cy="580" r="80" fill="#cfd8dc" stroke="{K}" stroke-width="7"/>
<g stroke="#9aa5ab" stroke-width="4">{''.join(f'<path d="M{460+i*20} 520 v120"/>' for i in range(9))}{''.join(f'<path d="M470 {520+i*20} h140"/>' for i in range(7))}</g>
<g stroke="#ffe066" stroke-width="8" stroke-linecap="round" opacity=".8"><path d="M440 680 l-120 160 M640 680 l130 170 M540 690 v190"/></g>
<path d="M0 1500 Q540 1350 1080 1500 V1620 H0 Z" fill="#c95463" stroke="{K}" stroke-width="8"/>
{germ(250, 1120, 1.5, "#9b59d0", hat=party)}{germ(520, 1040, 1.6, "#7ac943", hat=party)}
{germ(800, 1140, 1.5, "#9b59d0", hat=party, flip=True)}{germ(380, 1350, 1.2, "#7ac943", hat=party)}{germ(700, 1360, 1.25, "#9b59d0")}
<g transform="translate(160,1420) rotate(-20)"><rect x="-34" y="-70" width="68" height="120" rx="12" fill="#e53935" stroke="{K}" stroke-width="6"/><rect x="-34" y="-30" width="68" height="34" fill="#fff"/></g>
<g transform="translate(930,1430) rotate(18)"><circle r="40" fill="#ff80ab" stroke="{K}" stroke-width="6"/><path d="M-40 0 l-30 -24 v48 z M40 0 l30 -24 v48 z" fill="#ff80ab" stroke="{K}" stroke-width="6" stroke-linejoin="round"/></g>
<g transform="translate(560,1470)"><path d="M-70 40 h140 l-14 -70 h-112 z" fill="#ffcc80" stroke="{K}" stroke-width="6"/><path d="M-80 -30 q80 -60 160 0 z" fill="#fff" stroke="{K}" stroke-width="6"/><circle cx="0" cy="-60" r="14" fill="#e53935" stroke="{K}" stroke-width="5"/></g>
<g fill="#ffd54a">{''.join(f'<rect x="{x}" y="{y}" width="16" height="16" transform="rotate(30 {x} {y})"/>' for x,y in [(200,820),(330,900),(760,860),(880,960),(420,760),(650,940),(140,1000),(960,780)])}</g>
<g fill="#4fc3f7">{''.join(f'<circle cx="{x}" cy="{y}" r="9"/>' for x,y in [(260,760),(820,780),(560,900),(980,1020),(100,860)])}</g>
''', "#3d0b19")

# 7 Day 30 — alone on a bench at dusk
crowd = ''.join(person(x, 1260, 0.55, "big", shirt=c, hair=h, arms=((-60, -120), (60, -120))) for x, c, h in
                [(640, "#a5a9c9", False), (780, "#b7a3c9", True), (920, "#a3bfc9", False)])
scenes[7] = page(f'''
<rect width="{W}" height="{H}" fill="url(#dusk)"/>
<circle cx="820" cy="420" r="70" fill="#ffe0b2" opacity=".8"/>
<path d="M0 1240 Q300 1180 600 1240 T1080 1220 V1920 H0 Z" fill="#5d6f8f"/>
<path d="M0 1340 Q540 1290 1080 1340 V1920 H0 Z" fill="#6b7f9c"/>
<g opacity=".75">{crowd}</g>
<g transform="translate(120,1180)"><rect x="-14" y="0" width="28" height="200" fill="#4a3b2a"/><circle cx="0" cy="-30" r="110" fill="#3f5c4a"/></g>
<rect x="80" y="1460" width="560" height="40" rx="10" fill="#8d6e63" stroke="{K}" stroke-width="8"/>
<rect x="80" y="1380" width="560" height="30" rx="10" fill="#8d6e63" stroke="{K}" stroke-width="8"/>
<rect x="110" y="1500" width="26" height="140" fill="#5d4037" stroke="{K}" stroke-width="6"/><rect x="584" y="1500" width="26" height="140" fill="#5d4037" stroke="{K}" stroke-width="6"/>
{person(360, 1450, 1.0, "sad", arms=((24, -86), (-110, 40)), legs=((-90, 40), (90, 40)),
        extra=f'<path d="M-90 40 v150 M90 40 v150" stroke="{K}" stroke-width="{SW}" stroke-linecap="round"/>')}
<path d="M300 1080 q-40 30 -20 80" fill="none" stroke="#9fd3ff" stroke-width="8" stroke-linecap="round"/>
''', "#3d4f8f")

# 8 Fix — clinic room, mascot hands brush, germs flee
scenes[8] = page(f'''
<rect width="{W}" height="{H}" fill="#e9fbf9"/>
<rect x="0" y="1420" width="{W}" height="500" fill="#bfe7e3"/>
<rect x="80" y="200" width="420" height="320" rx="20" fill="#fff" stroke="{K}" stroke-width="8"/>
<path d="M140 460 l90 -120 l70 80 l60 -50 l80 90" fill="#9dd5c9" stroke="{K}" stroke-width="5" stroke-linejoin="round"/>
<circle cx="880" cy="320" r="120" fill="#fff6c9" stroke="{K}" stroke-width="8"/>
<path d="M820 320 h120 M880 260 v120" stroke="{ORANGE}" stroke-width="14" stroke-linecap="round" opacity=".0"/>
<g transform="translate(820,1300)"><path d="M-160 0 h320 l-30 100 h-260 z" fill="{TEAL}" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>
<path d="M120 0 l80 -260 l60 10 l-70 250" fill="{TEAL}" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>
<rect x="-20" y="100" width="40" height="120" fill="#9aa5ab" stroke="{K}" stroke-width="6"/></g>
{mascot(310, 1090, 1.15, item=f'<g transform="translate(300,124) rotate(-60)"><rect x="-8" y="-120" width="16" height="120" rx="6" fill="#4fb3b8" stroke="{K}" stroke-width="5"/><rect x="-14" y="-150" width="28" height="40" rx="6" fill="#fff" stroke="{K}" stroke-width="5"/></g>')}
{person(690, 1430, 0.95, "big", arms=((-60, -170), (110, 40)))}
<g transform="translate(650,1050) rotate(-10)"><rect x="-8" y="-150" width="16" height="150" rx="6" fill="{ORANGE}" stroke="{K}" stroke-width="5"/><rect x="-14" y="-176" width="28" height="40" rx="6" fill="#fff" stroke="{K}" stroke-width="5"/></g>
{germ(160, 1640, 1.0, "#9b59d0", scared=True, flip=True)}{germ(330, 1720, 0.9, "#7ac943", scared=True, flip=True)}{germ(70, 1780, 0.8, "#9b59d0", scared=True, flip=True)}
<path d="M230 1640 h80 M240 1680 h60 M400 1720 h70" stroke="{K}" stroke-width="6" stroke-linecap="round"/>
<g fill="#fff">{''.join(f'<path d="M{x} {y} l8 20 20 8 -20 8 -8 20 -8 -20 -20 -8 20 -8z"/>' for x,y in [(560,820),(980,980),(480,1000)])}</g>
''', "#e9fbf9")

# 9 CTA — clinic front, sky space for text
scenes[9] = page(f'''
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g fill="#fff" opacity=".9"><ellipse cx="220" cy="300" rx="120" ry="44"/><ellipse cx="300" cy="270" rx="90" ry="50"/><ellipse cx="830" cy="420" rx="130" ry="46"/><ellipse cx="900" cy="390" rx="80" ry="44"/></g>
<rect x="0" y="1560" width="{W}" height="360" fill="#8d9599"/>
<path d="M0 1700 h1080" stroke="#fff" stroke-width="10" stroke-dasharray="60 40"/>
<rect x="0" y="1540" width="{W}" height="30" fill="#c9cfd2"/>
<rect x="120" y="840" width="840" height="700" fill="#fff" stroke="{K}" stroke-width="10"/>
<path d="M90 840 h900 l-40 -110 h-820 z" fill="{TEAL}" stroke="{K}" stroke-width="10" stroke-linejoin="round"/>
<rect x="180" y="880" width="720" height="120" rx="16" fill="{TEAL_D}" stroke="{K}" stroke-width="7"/>
<text x="540" y="962" text-anchor="middle" font-size="62" font-weight="bold" fill="#fff">คลินิกทันตกรรมบางปะอิน</text>
<rect x="180" y="1060" width="250" height="230" rx="10" fill="#bfe9f5" stroke="{K}" stroke-width="7"/>
<rect x="650" y="1060" width="250" height="230" rx="10" fill="#bfe9f5" stroke="{K}" stroke-width="7"/>
<rect x="450" y="1100" width="180" height="440" rx="8" fill="#e6f7f6" stroke="{K}" stroke-width="7"/><circle cx="600" cy="1330" r="9" fill="{K}"/>
<g transform="translate(305,1175)"><path d="M-40 -40 C-40 -70,-6 -70,0 -56 C6 -70,40 -70,40 -40 C40 -10,32 0,30 26 C28 44,14 44,12 26 C10 14,-10 14,-12 26 C-14 44,-28 44,-30 26 C-32 0,-40 -10,-40 -40Z" fill="#fff" stroke="{TEAL_D}" stroke-width="6"/></g>
<g transform="translate(160,1440)"><path d="M-40 100 h80 l-12 -100 h-56 z" fill="{ORANGE}" stroke="{K}" stroke-width="6"/><circle cx="0" cy="-30" r="56" fill="#5cbf7a" stroke="{K}" stroke-width="6"/></g>
<g transform="translate(920,1440)"><path d="M-40 100 h80 l-12 -100 h-56 z" fill="{ORANGE}" stroke="{K}" stroke-width="6"/><circle cx="0" cy="-30" r="56" fill="#5cbf7a" stroke="{K}" stroke-width="6"/></g>
{mascot(760, 1400, 0.85, wave=True)}
{person(330, 1720, 0.85, "big", arms=((-100, 80), (110, -150)), legs=((-70, 190), (60, 190)))}
''', "#8fd3f4")




TEXT = [('ไม่แปรงฟัน 30 วัน?!', 'ถ้าคุณไม่แปรงฟันเลย 30 วัน จะเกิดอะไรขึ้นกับปากของคุณ?'), ('วันที่ 1', 'ทุกอย่างดูปกติ แต่ภายในไม่กี่ชั่วโมง คราบจุลินทรีย์บาง ๆ ก็เริ่มเกาะผิวฟันแล้ว'), ('วันที่ 3', 'ฟันเริ่มรู้สึกสาก ๆ ลมหายใจเริ่มมีกลิ่น คนข้าง ๆ เริ่มขยับหนีห่าง'), ('หินปูนมาแล้ว', 'คราบที่สะสมเริ่มแข็งตัวเป็นหินปูน แปรงฟันอย่างเดียวเอาออกไม่ได้แล้ว'), ('สัปดาห์ที่ 2', 'เหงือกเริ่มแดง บวม และมีเลือดออกง่าย นี่คือสัญญาณของเหงือกอักเสบ'), ('สัปดาห์ที่ 3', 'กลิ่นปากหนักขึ้น เชื้อโรคยิ่งสะสม และถ้ากินหวานบ่อย ฟันก็เสี่ยงเริ่มผุ'), ('วันที่ 30', 'ต้นไม่กล้ายิ้ม ไม่กล้าคุยใกล้ใครอีกเลย'), ('กลับมาดีได้!', 'เหงือกอักเสบระยะแรกกลับมาดีได้ แปรงฟันวันละ 2 ครั้ง ใช้ไหมขัดฟัน และให้ทันตแพทย์ขูดหินปูน'), (None, 'อย่ารอให้ถึงวันที่ 30 นะคะ ตรวจสุขภาพฟันได้ที่คลินิกทันตกรรมบางปะอิน')]

# SCENES: list of dicts {html, title (None = clinic end card), sub}
SCENES = [dict(html=scenes[i + 1], title=t, sub=s) for i, (t, s) in enumerate(TEXT)]

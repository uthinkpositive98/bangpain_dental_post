import numpy as np, wave, random
SR = 44100
TOTAL = 66.5
N = int(SR * TOTAL)
rng = np.random.default_rng(1)

def tt(d): return np.arange(int(SR * d)) / SR
def env(n, a=0.005, r=0.2):
    e = np.ones(n); ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    t = np.arange(n) / SR; e *= np.exp(-t / r); return e
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i] * g
def midi(m): return 440 * 2 ** ((m - 69) / 12)

def pluck(f, d=0.6):
    n = int(SR * d); p = int(SR / f)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out
_pl = {}
def pl(m, d=0.6):
    if (m, d) not in _pl: _pl[(m, d)] = pluck(midi(m), d)
    return _pl[(m, d)]
def marimba(f, d=0.5):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)) * env(len(t), 0.002, 0.18)
def bass(f, d=0.4):
    t = tt(d); x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return x * env(len(t), 0.005, 0.25)
def kick():
    t = tt(0.25); f = 120 * np.exp(-t / 0.04) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.12)
def hat():
    x = rng.uniform(-1, 1, int(SR * 0.05)); x = np.diff(np.concatenate([[0], x]))
    return x * env(len(x), 0.001, 0.012)
def clap():
    x = rng.uniform(-1, 1, int(SR * 0.15)); return x * env(len(x), 0.001, 0.04)

# ---------------- music 112bpm, C G Am F
music = np.zeros(N)
bpm = 112; beat = 60 / bpm; bar = beat * 4
prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]
mel_pat = [[72, None, 76, 79, None, 76, 74, 72], [74, None, 71, 74, None, 79, 77, 74],
           [76, None, 72, 76, 81, None, 79, 76], [77, None, 76, 72, None, 74, 72, None]]
b = 0; tcur = 0.0
while tcur < TOTAL:
    root, ch = prog[b % 4]
    for k in range(4):
        add(music, bass(midi(root), beat * 0.9), tcur + k * beat, 0.55)
        add(music, kick(), tcur + k * beat, 0.5 if k in (0, 2) else 0.25)
        if k in (1, 3): add(music, clap(), tcur + k * beat, 0.12)
    for e in range(8):
        add(music, hat(), tcur + e * beat / 2, 0.12)
        add(music, pl(ch[e % 3] + (12 if e % 4 == 3 else 0), 0.5), tcur + e * beat / 2, 0.22)
    if b >= 2:
        for e, m in enumerate(mel_pat[b % 4]):
            if m: add(music, marimba(midi(m), 0.5), tcur + e * beat / 2, 0.16)
    b += 1; tcur += bar
fade = np.ones(N); fi = int(1.8 * SR); fade[-fi:] = np.linspace(1, 0, fi)
fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
music *= fade

# ---------------- sfx
sfx = np.zeros(N)
def s_pop():
    t = tt(0.12); f = 900 * np.exp(-t / 0.03) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.04)
def s_whoosh(d=0.45):
    x = rng.normal(0, 1, int(SR * d)); x = np.convolve(x, np.ones(18) / 18, 'same')
    e = np.sin(np.linspace(0, np.pi, len(x))) ** 2; return x * e * 0.8
def s_boing(d=0.5, f0=300):
    t = tt(d); f = f0 * (1 + 0.5 * np.exp(-t / 0.15)) * (1 + 0.08 * np.sin(2 * np.pi * 12 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.2)
def s_thud():
    t = tt(0.6); f = 90 * np.exp(-t / 0.08) + 40
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.001, 0.25)
    n = rng.normal(0, 1, len(t)) * env(len(t), 0.001, 0.05) * 0.4
    return x + n
def s_click():
    t = tt(0.08); return (np.sin(2 * np.pi * 2400 * t) * env(len(t), 0.0005, 0.01) + rng.uniform(-1, 1, len(t)) * env(len(t), 0.0005, 0.005))
def s_chime(notes=(84, 88, 91, 96), gap=0.07):
    out = np.zeros(int(SR * (gap * len(notes) + 0.8)))
    for i, m in enumerate(notes):
        t = tt(0.8); x = (np.sin(2 * np.pi * midi(m) * t) + 0.4 * np.sin(2 * np.pi * midi(m) * 2.76 * t)) * env(len(t), 0.002, 0.25)
        i0 = int(i * gap * SR); out[i0:i0 + len(x)] += x
    return out * 0.5
def s_fanfare():
    out = np.zeros(int(SR * 1.4))
    for i, m in enumerate((67, 72, 76, 79)):
        t = tt(0.9 if i == 3 else 0.2); f = midi(m)
        x = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 7)) * env(len(t), 0.01, 0.5 if i == 3 else 0.15)
        i0 = int(i * 0.12 * SR); out[i0:i0 + len(x)] += x
    return out * 0.35
def s_sad():
    out = np.zeros(int(SR * 2.6))
    for i, m in enumerate((62, 61, 60, 59)):
        d = 0.9 if i == 3 else 0.42
        t = tt(d); f = midi(m) * (1 + (0.02 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0))
        x = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.3 for h in range(1, 6)) * env(len(t), 0.02, 0.6)
        i0 = int(i * 0.45 * SR); out[i0:i0 + len(x)] += x
    return out * 0.25
def s_slide(d=1.6, f0=1200, f1=300):
    t = tt(d); f = np.linspace(f0, f1, len(t)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, np.pi, len(t))) * 0.35
def s_drill(d=3.6):
    t = tt(d); f = 210 + 15 * np.sin(2 * np.pi * 3 * t)
    ph = np.cumsum(f) / SR; x = 2 * (ph % 1) - 1
    x = np.convolve(x, np.ones(10) / 10, 'same')
    e = np.minimum(1, np.minimum(t / 0.2, (d - t) / 0.2)); return x * e * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * t) ** 2) * 0.18
def s_tick():
    t = tt(0.05); return np.sin(2 * np.pi * 1800 * t) * env(len(t), 0.0005, 0.01)
def s_scrub(d=2.2):
    x = rng.normal(0, 1, int(SR * d)); x = np.convolve(x, np.ones(8) / 8, 'same')
    t = np.arange(len(x)) / SR; return x * (0.5 + 0.5 * np.sin(2 * np.pi * 8 * t)) ** 2 * 0.25

S = [0, 5.79, 13.88, 19.32, 26.87, 33.07, 39.99, 44.74, 50.31, 60.0]
ev = []
def E(sc, t, fn, g=1.0): ev.append((S[sc] + t, fn, g))
for sc in range(1, 10): E(sc, 0.0, s_whoosh(0.4), 0.2)
# 1 (tooth pops at 0.45)
E(0, 0.45, s_pop(), .7); E(0, 0.47, s_boing(0.6, 420), .3); E(0, 0.55, s_whoosh(0.5), .25)
E(0, 1.1, s_pop(), .35); E(0, 2.7, s_thud(), .5); E(0, 4.5, s_pop(), .3)
# 2 (t-1.0 shift)
E(1, 0.3, s_pop(), .35); E(1, 2.0, s_pop(), .3); E(1, 2.4, s_boing(0.5, 260), .25); E(1, 2.5, s_boing(0.5, 300), .25)
E(1, 5.0, s_pop(), .3); E(1, 5.2, s_slide(2.0, 900, 350), .35)
# 3
E(2, 0.3, s_pop(), .35); E(2, 1.7, s_pop(), .3); E(2, 1.8, s_sad(), .6); E(2, 3.3, s_pop(), .3)
# 4
E(3, 0.0, s_chime((96, 100, 103)), .35); E(3, 0.5, s_slide(0.7, 1500, 400), .4); E(3, 1.2, s_thud(), .8)
E(3, 1.4, s_fanfare(), .6); E(3, 3.1, s_pop(), .3); E(3, 4.4, s_pop(), .3); E(3, 5.6, s_pop(), .3); E(3, 6.4, s_chime((96, 103)), .4)
# 5
E(4, 0.2, s_pop(), .3); E(4, 0.45, s_pop(), .3); E(4, 1.0, s_drill(3.7), .7); E(4, 1.3, s_pop(), .3)
E(4, 4.7, s_click(), .8); E(4, 4.72, s_chime((88, 96)), .4); E(4, 5.1, s_pop(), .3)
# 6
E(5, 0.2, s_pop(), .3); E(5, 0.45, s_pop(), .3); E(5, 0.6, s_boing(0.4, 500), .25); E(5, 1.4, s_pop(), .3)
for k in range(5): E(5, 1.4 + k * 0.8 + 0.4, s_tick(), .5)
for k in range(6): E(5, 0.9 + k * 0.35, s_boing(0.25, 600 + k * 40), .1)
for k in range(5): E(5, 3.0 + k * 0.45, s_pop(), .15)
E(5, 4.1, s_pop(), .3); E(5, 6.2, s_pop(), .25)
# 7
E(6, 0.2, s_pop(), .3); E(6, 0.45, s_pop(), .3); E(6, 0.7, s_slide(0.4, 1000, 500), .3); E(6, 1.1, s_click(), .8)
E(6, 1.2, s_pop(), .3); E(6, 1.9, s_whoosh(1.0), .25); E(6, 3.0, s_chime((84, 88, 91, 96, 100)), .55); E(6, 3.1, s_pop(), .3)
# 8
E(7, 0.2, s_fanfare(), .5)
for tk in (0.5, 1.6, 2.9, 4.4): E(7, tk, s_pop(), .35)
for k in range(8): E(7, 0.4 + k * 0.6, s_pop(), .08)
# 9
E(8, 0.3, s_pop(), .35); E(8, 2.0, s_pop(), .35); E(8, 1.9, s_scrub(1.8), 0.4); E(8, 3.7, s_pop(), .35)
E(8, 3.9, s_slide(1.2, 700, 900), .15); E(8, 4.6, s_pop(), .35); E(8, 6.6, s_pop(), .25)
# 10
E(9, 0.15, s_chime((84, 88, 91, 96)), .5); E(9, 0.5, s_pop(), .3); E(9, 0.7, s_pop(), .3)
for tk in (1.1, 1.4, 1.7, 2.3): E(9, tk, s_pop(), .25)
for t0, x, g in ev: add(sfx, x, t0, g)

import subprocess
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', 'vo/voice.mp3', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
voice = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
vo = np.zeros(N); add(vo, voice, 0.4)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.95
# envelope for ducking
win = int(0.05 * SR)
def mavg(x, w):
    c = np.cumsum(np.concatenate([[0], x])); y = (c[w:] - c[:-w]) / w
    return np.concatenate([np.full(w // 2, y[0]), y, np.full(len(x) - len(y) - w // 2, y[-1])])
envv = np.sqrt(mavg(vo ** 2, win))
active = (envv > 0.02).astype(float)
sm = int(0.35 * SR)
active = mavg(active, sm)
duck = 1 - 0.6 * np.clip(active * 1.5, 0, 1)
mix = music * 0.5 * duck + sfx * 0.55 * (1 - 0.35 * np.clip(active, 0, 1)) + vo * 1.0

# gentle limiter
mix = np.tanh(mix * 1.1) * 0.9
st = np.stack([mix, mix], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open('audio2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('peak', np.abs(mix).max(), 'rms', np.sqrt((mix ** 2).mean()))

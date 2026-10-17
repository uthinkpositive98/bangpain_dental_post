"""Soundtrack for kawaii Reels: an upbeat original music bed (112 bpm, synthesized, copyright-free),
cartoon sound effects, and the per-scene narration mixed on top with automatic music ducking.
Used by tools/kawaii_render.py; nothing here needs network access."""
import numpy as np, subprocess, wave
SR = 44100
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


SFX = {
    'pop': lambda: s_pop(), 'whoosh': lambda: s_whoosh(0.4), 'boing': lambda: s_boing(0.5, 380),
    'thud': lambda: s_thud(), 'click': lambda: s_click(), 'chime': lambda: s_chime(),
    'ding': lambda: s_chime((88, 96)), 'sparkle': lambda: s_chime((96, 100, 103)),
    'fanfare': lambda: s_fanfare(), 'sad': lambda: s_sad(), 'slide_down': lambda: s_slide(1.6, 1100, 350),
    'slide_up': lambda: s_slide(0.9, 400, 1200), 'drill': lambda: s_drill(3.0), 'tick': lambda: s_tick(),
    'scrub': lambda: s_scrub(1.8),
}
# default loudness of each effect under narration (pops are frequent, so they stay quiet)
SFX_GAIN = {'pop': 0.32, 'whoosh': 0.22, 'boing': 0.3, 'thud': 0.7, 'click': 0.8, 'chime': 0.55, 'ding': 0.45,
            'sparkle': 0.4, 'fanfare': 0.6, 'sad': 0.6, 'slide_down': 0.4, 'slide_up': 0.35, 'drill': 0.7,
            'tick': 0.5, 'scrub': 0.4}


def make_music(total):
    n = int(SR * total) + SR
    music = np.zeros(n)
    bpm = 112; beat = 60 / bpm; bar = beat * 4
    prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]
    mel = [[72, None, 76, 79, None, 76, 74, 72], [74, None, 71, 74, None, 79, 77, 74],
           [76, None, 72, 76, 81, None, 79, 76], [77, None, 76, 72, None, 74, 72, None]]
    b = 0; tcur = 0.0
    while tcur < total:
        root, ch = prog[b % 4]
        for k in range(4):
            add(music, bass(midi(root), beat * 0.9), tcur + k * beat, 0.55)
            add(music, kick(), tcur + k * beat, 0.5 if k in (0, 2) else 0.25)
            if k in (1, 3): add(music, clap(), tcur + k * beat, 0.12)
        for e in range(8):
            add(music, hat(), tcur + e * beat / 2, 0.12)
            add(music, pl(ch[e % 3] + (12 if e % 4 == 3 else 0), 0.5), tcur + e * beat / 2, 0.22)
        if b >= 2:
            for e, m in enumerate(mel[b % 4]):
                if m: add(music, marimba(midi(m), 0.5), tcur + e * beat / 2, 0.16)
        b += 1; tcur += bar
    music = music[:int(SR * total)]
    fi = int(1.8 * SR); music[-fi:] *= np.linspace(1, 0, fi)
    fo = int(0.3 * SR); music[:fo] *= np.linspace(0, 1, fo)
    return music


def load_audio(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768


def _mavg(x, w):
    c = np.cumsum(np.concatenate([[0], x])); y = (c[w:] - c[:-w]) / w
    return np.concatenate([np.full(w // 2, y[0]), y, np.full(len(x) - len(y) - w // 2, y[-1])])


def build_soundtrack(total, cues, voices, out_wav, music_gain=0.5):
    """cues: [(time_s, kind, gain_or_None)], voices: [(path, start_s, tempo)] -> stereo 16-bit wav."""
    n = int(SR * total)
    music = make_music(total)
    sfx = np.zeros(n)
    for t0, kind, g in cues:
        if kind in SFX:
            add(sfx, SFX[kind](), t0, SFX_GAIN.get(kind, 0.4) if g is None else g)
    vo = np.zeros(n)
    for path, start, tempo in voices:
        x = load_audio(path)
        if tempo and tempo > 1.001:
            idx = np.arange(0, len(x) - 1, tempo)
            x = np.interp(idx, np.arange(len(x)), x)
        add(vo, x, start)
    if np.abs(vo).max() > 0:
        vo = vo / np.abs(vo).max() * 0.95
        env_v = np.sqrt(_mavg(vo ** 2, int(0.05 * SR)))
        active = _mavg((env_v > 0.02).astype(float), int(0.35 * SR))
    else:
        active = np.zeros(n)
    duck = 1 - 0.6 * np.clip(active * 1.5, 0, 1)
    mix = music * music_gain * duck + sfx * 0.8 * (1 - 0.35 * np.clip(active, 0, 1)) + vo
    mix = np.tanh(mix * 1.1) * 0.9
    pcm = (np.clip(np.stack([mix, mix], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return out_wav

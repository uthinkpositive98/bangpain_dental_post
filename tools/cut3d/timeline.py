"""Build videos/<slug>/.work/timeline.json from script.txt + vo/NN.mp3 + episode.json.
   python3 tools/cut3d/timeline.py videos/<slug>
script.txt: one line per beat; the LAST line is the end-card line. Words are split with | (caption chunks) and spaces
(phrases); an optional leading [tag] (ElevenLabs v4 direction) is dropped from captions.
episode.json: tempo (voice speed-up, pitch kept), keys (words shown in yellow), marks [[beat, name, first-token, occurrence]]
-> the time of the caption chunk starting with that token, readable in scene3d.js as L.mk(beat, name, fallback)."""
import json, os, re, subprocess, sys
import numpy as np

SR = 16000
GAP = 0.18          # silence between beats
END_MIN = 6.0       # end card seconds (at least)
EP = sys.argv[1].rstrip('/')
CFG = json.load(open(os.path.join(EP, 'episode.json'), encoding='utf-8'))
TEMPO = float(CFG.get('tempo', 1.0))
KEYS = tuple(CFG.get('keys', []))
MARKS = [tuple(m) for m in CFG.get('marks', [])]


def load(path):
    af = [] if TEMPO == 1 else ['-af', f'atempo={TEMPO}']
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, *af, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768


def islands(x):
    fr = int(SR * .01); n = len(x) // fr
    rms = np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(1))
    on = rms > max(0.012, rms.max() * 0.06)
    idx = np.where(on)[0]
    if not len(idx): return 0, n * .01, [(0, n * .01)]
    first, last = idx[0], idx[-1]
    segs, s, quiet = [], first, 0
    for i in range(first, last + 1):
        if on[i]:
            if quiet >= 12: segs.append((s * .01, (i - quiet) * .01)); s = i
            quiet = 0
        else: quiet += 1
    segs.append((s * .01, (last + 1) * .01))
    return first * .01, (last + 1) * .01, segs


lines = [l for l in open(os.path.join(EP, 'script.txt'), encoding='utf-8').read().splitlines() if l.strip()]
beats, clips, t = [], [], 0.4
end = None
for bi, line in enumerate(lines):
    text = re.sub(r'\[[a-z ]+\]\s*', '', line)
    path = os.path.join(EP, 'vo', f'{bi + 1:02d}.mp3')
    if not os.path.exists(path): sys.exit(f'missing voice clip {path}')
    a, b, segs = islands(load(path))
    mark_tokens = {m[2] for m in MARKS if m[0] == bi}
    toks = [(tok, k == 0) for phrase in text.split(' ') for k, tok in enumerate(phrase.split('|'))]
    chunks = []
    for tok, newphrase in toks:
        clean = tok.strip('.?!')
        if chunks and not newphrase and len(chunks[-1]['raw'].strip('.?!')) < 5 and clean not in mark_tokens:
            chunks[-1]['raw'] += tok; chunks[-1]['toks'].append(clean)
        else:
            chunks.append({'raw': tok, 'toks': [clean]})
    speech = sum(e - s for s, e in segs)
    weights = [max(1, len(re.sub(r'[\.\?!่้๊๋ั็ิีึืุู์]', '', c['raw']))) for c in chunks]
    tot = sum(weights); acc = 0

    def real(u):  # seconds of speech -> seconds into the clip (skipping pauses)
        for s, e in segs:
            if u <= e - s: return s + u
            u -= e - s
        return segs[-1][1]
    out = []
    for c, w in zip(chunks, weights):
        u0 = acc / tot * speech; acc += w
        disp = c['raw'].replace('...', '').strip()
        out.append({'t': round(t + real(u0) - a - 0.04, 3), 'text': disp, 'key': any(k in disp for k in KEYS), 'toks': c['toks']})
    for i, c in enumerate(out):
        c['end'] = out[i + 1]['t'] if i + 1 < len(out) else round(t + (b - a) + 0.15, 3)
    marks = {}
    for (mb, name, tok, occ) in MARKS:
        if mb != bi: continue
        n = 0
        for c in out:
            if c['toks'][0].startswith(tok):
                n += 1
                if n == occ: marks[name] = c['t']; break
        else: print(f'warning: mark {name} (beat {mb}, token {tok} #{occ}) not found')
    for c in out: del c['toks']
    clips.append({'path': path, 'start': round(t - a, 3)})
    dur = (b - a) + GAP
    if bi == len(lines) - 1:                     # end-card line
        end = {'start': round(t, 3), 'dur': round(max(END_MIN, dur + 0.8), 3)}
        t += end['dur']
        break
    beats.append({'start': round(t, 3), 'dur': round(dur, 3), 'chunks': out, 'marks': marks})
    t += dur
tl = {'beats': beats, 'end': end, 'total': round(t, 3), 'clips': clips, 'tempo': TEMPO}
os.makedirs(os.path.join(EP, '.work'), exist_ok=True)
json.dump(tl, open(os.path.join(EP, '.work', 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
print(f'total {t:.2f}s  (end card from {end["start"]:.2f}s)')
for i, b in enumerate(beats): print(f'{i:2d} {b["start"]:6.2f} +{b["dur"]:.2f}  {b["marks"]}  ' + ' / '.join(c['text'] for c in b['chunks']))

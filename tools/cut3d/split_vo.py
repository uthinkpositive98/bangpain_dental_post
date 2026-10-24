"""Split one ElevenLabs take that reads several script lines (separated by blank lines) into vo/NN.mp3 files.
   python3 tools/cut3d/split_vo.py videos/<slug> <take.mp3> <first_line_number>
Cuts at the pauses nearest to where each line should end (by character count), preferring long pauses.
Check the printed list: each clip's length should roughly match its line."""
import os, re, subprocess, sys
import numpy as np
EP, TAKE, FIRST = sys.argv[1].rstrip('/'), sys.argv[2], int(sys.argv[3]); SR = 22050
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', TAKE, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
fr = int(SR * .01); n = len(x) // fr; rms = np.sqrt((x[:n * fr].reshape(n, fr) ** 2).mean(1)); on = rms > max(.01, rms.max() * .05)
sil, s = [], None
for i in range(n):
    if not on[i] and s is None: s = i
    if on[i] and s is not None:
        if i - s >= 20: sil.append((s * .01, i * .01))
        s = None
idx = np.where(on)[0]; t0, t1 = idx[0] * .01, idx[-1] * .01
all_lines = [re.sub(r'\[[a-z ]+\]\s*', '', l).replace('|', '') for l in open(os.path.join(EP, 'script.txt'), encoding='utf-8').read().splitlines() if l.strip()]
lines = all_lines[FIRST - 1:]
L = np.array([len(l) for l in lines], float); exp = t0 + np.cumsum(L)[:-1] / L.sum() * (t1 - t0)
cuts, last = [], 0
for e in exp:
    cand = [(abs((a + b) / 2 - e) - 1.2 * (b - a), a, b) for a, b in sil if (a + b) / 2 > last + .5]
    if not cand: sys.exit('not enough pauses to split the take — generate the remaining lines separately')
    _, a, b = min(cand); cuts.append((a, b)); last = (a + b) / 2
bounds = [max(0, t0 - .05)] + [(a + b) / 2 for a, b in cuts] + [t1 + .3]
os.makedirs(os.path.join(EP, 'vo'), exist_ok=True)
for k, line in enumerate(lines):
    out = os.path.join(EP, 'vo', f'{FIRST + k:02d}.mp3')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', TAKE, '-ss', f'{bounds[k]:.3f}', '-to', f'{bounds[k + 1]:.3f}', '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
    print(f'{FIRST + k:02d}  {bounds[k + 1] - bounds[k]:5.2f}s  expected≈{L[k] / L.sum() * (t1 - t0):5.2f}s  {line[:40]}')

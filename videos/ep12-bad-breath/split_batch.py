"""split a multi-scene narration clip at the pauses between scenes: python3 split_batch.py batch.mp3 first last"""
import re, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import NARR
src, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
log = subprocess.run(['ffmpeg', '-i', src, '-af', 'silencedetect=noise=-40dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
sil = [(s, e) for s, e in zip(st, en) if e < dur - 0.2]
w = [len(re.sub(r'\[.*?\]|\s', '', NARR[i])) for i in range(a, b + 1)]
tot = sum(w); cum = 0; cuts = []
for k in range(len(w) - 1):
    cum += w[k]; target = dur * cum / tot
    cands = [s for s in sil if (not cuts or (s[0] + s[1]) / 2 > cuts[-1] + 2)]
    best = min(cands, key=lambda s: abs((s[0] + s[1]) / 2 - target) - 1.5 * (s[1] - s[0]))
    cuts.append((best[0] + best[1]) / 2)
    print(f'scene {a + k}: target {target:.1f} -> cut {cuts[-1]:.2f} (gap {best[1] - best[0]:.2f})')
edges = [0.0] + cuts + [dur]
for k, i in enumerate(range(a, b + 1)):
    out = os.path.join(os.path.dirname(src), f'scene{i}.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{edges[k]:.3f}', '-i', src, '-t', f'{edges[k + 1] - edges[k]:.3f}', '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
    print(i, round(edges[k + 1] - edges[k], 2))

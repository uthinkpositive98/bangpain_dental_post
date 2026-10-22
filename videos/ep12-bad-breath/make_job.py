"""measure narration/sceneN.mp3 -> durations.json (speech length after trimming silence) and write job.json with
local clip paths (committed next to the episode, so they cannot expire)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script import NARR
F = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
     "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
def speech_len(p):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-af', F, '-ac', '1', '-ar', '22050', '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return len(out) / (22050 * 2)
durs, voices = {}, []
for i, n in enumerate(NARR):
    p = os.path.join(HERE, 'narration', f'scene{i}.mp3')
    if n is None or not os.path.exists(p):
        voices.append(None); continue
    durs[str(i)] = round(speech_len(p), 2)
    voices.append(f'narration/scene{i}.mp3')
json.dump(durs, open(os.path.join(HERE, 'durations.json'), 'w'), indent=1)
json.dump({'output': 'ep12-bad-breath.mp4', 'voices': voices}, open(os.path.join(HERE, 'job.json'), 'w'), indent=1)
print(durs, sum(durs.values()))

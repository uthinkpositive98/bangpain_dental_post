"""Build a cut3d episode end to end.
   python3 tools/cut3d/build.py videos/<slug> --preview   # timeline + contact.jpg (cover + 3 moments per beat + end card), ~1–2 min
   python3 tools/cut3d/build.py videos/<slug>             # full render -> videos/<slug>/<slug>.mp4 (cover, story, end card, badges, audio)
Options: --fps N (default 30), env RS (3D resolution scale, default 0.6667)."""
import importlib.util, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
EP = sys.argv[1].rstrip('/'); SLUG = os.path.basename(EP); WORK = os.path.join(EP, '.work'); os.makedirs(WORK, exist_ok=True)
FPS = int(sys.argv[sys.argv.index('--fps') + 1]) if '--fps' in sys.argv else 30
CFG = json.load(open(os.path.join(EP, 'episode.json'), encoding='utf-8'))
COVER = float(CFG.get('cover', {}).get('seconds', 1.8)) if CFG.get('cover') else 0.0
BADGES = os.path.join(HERE, 'badges.png')
def run(*a): print('+', ' '.join(map(str, a))[:160], flush=True); subprocess.run(list(map(str, a)), check=True, cwd=ROOT)
render = lambda *a: run('node', os.path.join(HERE, 'render.js'), EP, *a)

run(sys.executable, os.path.join(HERE, 'timeline.py'), EP)
tl = json.load(open(os.path.join(WORK, 'timeline.json')))

if '--preview' in sys.argv:
    ts = []
    for b in tl['beats']: ts += [b['start'] + b['dur'] * f for f in (.2, .55, .9)]
    ts.append(tl['end']['start'] + 3)
    for f in os.listdir(WORK):
        if f.startswith('pv_'): os.remove(os.path.join(WORK, f))
    if COVER: render('--stills', '0.6', os.path.join(WORK, 'pv_cover'), '--cover')
    render('--stills', ','.join(f'{t:.2f}' for t in ts), os.path.join(WORK, 'pv'))
    files = ([os.path.join(WORK, 'pv_cover_0.60.jpg')] if COVER else []) + [os.path.join(WORK, f'pv_{t:.2f}.jpg') for t in ts]
    cols = 8; n = len(files); rows = (n + cols - 1) // cols
    inputs = sum([['-i', f] for f in files], [])
    lab = ''.join(f"[{i}]scale=270:-1,drawtext=text='{('cover' if COVER and i == 0 else f'{ts[i - (1 if COVER else 0)]:.1f}s')}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7[v{i}];" for i in range(n))
    layout = '|'.join(f'{(i % cols) * 270}_{(i // cols) * 480}' for i in range(n))
    run('ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', lab + ''.join(f'[v{i}]' for i in range(n)) + f'xstack=inputs={n}:layout={layout}:fill=black', os.path.join(EP, 'contact.jpg'))
    print('preview ->', os.path.join(EP, 'contact.jpg')); sys.exit(0)

# ---- full render
parts = []
if COVER:
    render(os.path.join(WORK, 'cover.mp4'), '--cover', '--fps', FPS, '--t0', 0, '--t1', COVER); parts.append(os.path.join(WORK, 'cover.mp4'))
render(os.path.join(WORK, 'main.mp4'), '--fps', FPS); parts.append(os.path.join(WORK, 'main.mp4'))

# ---- soundtrack: voices + kawaii music bed + episode sound effects (cues.py), all shifted by the cover length
import kawaii_audio as KA
B = tl['beats']; bs = lambda i: B[i]['start']; be = lambda i: B[i]['start'] + B[i]['dur']
mk = lambda i, n, d=0: B[i]['marks'].get(n, bs(i) + d * B[i]['dur'])
cl = []
cue = lambda t, k, g=None: cl.append((t + COVER, k, g))
cp = os.path.join(EP, 'cues.py')
if os.path.exists(cp):
    spec = importlib.util.spec_from_file_location('cues', cp); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.cues(B, bs, be, mk, cue, tl['end']['start'])
if COVER: cl += [(0.05, 'sparkle', .45), (COVER - .3, 'whoosh', .35)]
tempo = tl.get('tempo', 1.0); voices = []
for c in tl['clips']:
    src = os.path.join(ROOT, c['path']) if not os.path.isabs(c['path']) else c['path']
    q = os.path.join(WORK, 'vo_' + os.path.basename(src).replace('.mp3', '.wav'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, *(['-af', f'atempo={tempo}'] if tempo != 1 else []), q], check=True)
    voices.append((q, c['start'] + COVER, 1.0))
wav = os.path.join(WORK, 'mix.wav')
KA.build_soundtrack(tl['total'] + COVER, cl, voices, wav, music_gain=0.32)

# ---- concat + audio + badges (bottom-right, whole clip)
out = os.path.join(EP, f'{SLUG}.mp4')
ins = sum([['-i', p] for p in parts], [])
n = len(parts)
fc = ''.join(f'[{i}:v]' for i in range(n)) + f'concat=n={n}:v=1:a=0[cat];[{n + 1}]format=rgba,colorchannelmixer=aa=0.92[bd];[cat][bd]overlay=W-w-30:H-h-56[v]'
run('ffmpeg', '-y', '-loglevel', 'error', *ins, '-i', wav, '-i', BADGES, '-filter_complex', fc, '-map', '[v]', '-map', f'{n}:a',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out)
dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip()
print(f'done -> {out} ({float(dur):.1f}s)')

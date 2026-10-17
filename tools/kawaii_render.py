"""Render a kawaii-cartoon episode (videos/<ep>/scenes.py using tools/kawaii.py) to a finished Reel.

  python3 tools/kawaii_render.py videos/<ep> --preview   # 3 stills per scene -> videos/<ep>/contact.png (seconds)
  python3 tools/kawaii_render.py videos/<ep> --silent    # animation + music + sound effects, no narration
                                                         #   -> videos/<ep>/.work/silent_preview.mp4 (~3-4 min)
  python3 tools/kawaii_render.py videos/<ep>             # full build with narration from job.json -> <output>.mp4

job.json: {"output": "<ep>.mp4", "voices": ["https://...scene1.mp3", ..., null for a silent scene]}
One clip per scene, in order (the end card may have one too). Each clip starts 0.15 s into its scene. A scene whose
clip is longer than the scene is held longer (its animation simply rests on the final pose), up to +3 s; beyond that
the clip is sped up slightly (max 1.2x).
"""
import argparse, importlib.util, json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from tools import kawaii as K            # noqa: E402
from tools import kawaii_audio as A      # noqa: E402

VOICE_LEAD = 0.15


def load(ep):
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(ep, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scenes = list(mod.SCENES)
    if not scenes or not getattr(scenes[-1].draw, "is_endcard", False):
        print("  no end card at the end -> adding the clinic end card automatically")
        scenes.append(K.Scene(K.endcard(), 6.0))
    scenes[-1].dur = max(scenes[-1].dur, 5.0)
    return scenes


def duration(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True).stdout
    return float(o)


def trim(src, dst):
    f = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", f, "-ar", "44100", dst], check=True)
    return dst


def fetch_voices(ep, job, work):
    vdir = os.path.join(ep, "voice")
    os.makedirs(vdir, exist_ok=True)
    out = []
    for i, url in enumerate(job.get("voices", []), 1):
        if not url:
            out.append(None); continue
        dst = os.path.join(vdir, f"scene{i}.mp3")
        if url.startswith("http"):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
                f.write(r.read())
        else:
            src = url if os.path.isabs(url) or os.path.exists(url) else os.path.join(ep, url)
            subprocess.run(["cp", src, dst], check=True)    # keep a copy next to the others for the release
        out.append(trim(dst, os.path.join(work, f"voice{i}.wav")))
    return out


def fit(scenes, voices, max_hold=3.0, max_tempo=1.2):
    tempos = []
    for k, sc in enumerate(scenes):
        v = voices[k] if k < len(voices) else None
        if not v:
            tempos.append(1.0); continue
        need = duration(v) + VOICE_LEAD + 0.45
        tempo = 1.0
        if need > sc.dur:
            new = round(min(sc.dur + max_hold, need), 2)
            print(f"  scene {k + 1}: narration {need - 0.6:.2f}s -> scene {sc.dur:.2f}s held to {new:.2f}s")
            sc.dur = new
            if need > new + 0.02:
                tempo = min(max_tempo, (need - 0.6) / (new - 0.6))
                print(f"  scene {k + 1}: narration sped up x{tempo:.2f}")
        tempos.append(tempo)
    return tempos


def mux(video, wav, out, total):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
    print(out, round(duration(out), 1), "s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--silent", action="store_true")
    a = ap.parse_args()
    scenes = load(a.ep)
    work = os.path.join(a.ep, ".work")
    os.makedirs(work, exist_ok=True)
    if a.preview:
        print(f"{len(scenes)} scenes, {sum(s.dur for s in scenes):.1f} s (before narration fitting)")
        print("preview ->", K.contact_sheet(scenes, os.path.join(a.ep, "contact.png")))
        return
    voices, tempos, out = [], [1.0] * len(scenes), os.path.join(work, "silent_preview.mp4")
    if not a.silent:
        job = json.load(open(os.path.join(a.ep, "job.json"), encoding="utf-8"))
        voices = fetch_voices(a.ep, job, work)
        tempos = fit(scenes, voices)
        out = os.path.join(a.ep, job["output"])
    starts, total = K.timeline(scenes)
    print(f"{len(scenes)} scenes, {total:.1f} s")
    silent = os.path.join(work, "silent.mp4")
    cues, total = K.render_video(scenes, silent)
    vlist = [(v, starts[k] + VOICE_LEAD, tempos[k]) for k, v in enumerate(voices) if v and k < len(scenes)]
    wav = A.build_soundtrack(total, cues, vlist, os.path.join(work, "soundtrack.wav"))
    mux(silent, wav, out, total)


if __name__ == "__main__":
    main()

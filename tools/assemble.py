"""Assemble a Reel from pre-rendered frames + voice clips listed in a job file.

Run by GitHub Actions (see .github/workflows/build-video.yml) whenever a videos/<episode>/job.json is pushed.

job.json:
{
  "output": "ep1-no-brushing-30-days.mp4",
  "dissolve_into_scene": 8,          # optional: soft fade into this scene number (1-based)
  "voices": ["https://...scene1.mp3", "..."]   # one URL per scene, in order
}
Frames are read from videos/<episode>/frames/frame1.png ... frameN.png (1080x1920).
Writes videos/<episode>/voice/sceneN.mp3 and videos/<episode>/<output>.
"""
import json, os, subprocess, sys, urllib.request

FPS, W, H, PAD, XF = 30, 1080, 1920, 0.4, 0.6


def run(*args):
    subprocess.run(args, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def main(ep_dir):
    job = json.load(open(os.path.join(ep_dir, "job.json"), encoding="utf-8"))
    voice_dir = os.path.join(ep_dir, "voice")
    work = os.path.join(ep_dir, ".work")
    os.makedirs(voice_dir, exist_ok=True)
    os.makedirs(work, exist_ok=True)

    voices = []
    for i, url in enumerate(job["voices"], 1):
        dst = os.path.join(voice_dir, f"scene{i}.mp3")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
            f.write(r.read())
        voices.append(dst)

    durs = [round(duration(v) + PAD, 2) for v in voices]
    clips = []
    for i, d in enumerate(durs, 1):
        frame = os.path.join(ep_dir, "frames", f"frame{i}.png")
        n = int(round(d * FPS))
        clip = os.path.join(work, f"clip{i}.mp4")
        vf = (f"scale=2160:-1,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={n}:s={W}x{H}:fps={FPS},format=yuv420p")
        run("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", frame, "-vf", vf, "-frames:v", str(n),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", clip)
        clips.append(clip)

    dis = job.get("dissolve_into_scene")
    inputs = sum((["-i", c] for c in clips), [])
    filt, last, starts, t = [], "[0:v]", [0.0], durs[0]
    for k in range(1, len(clips)):
        out = f"[v{k}]"
        if dis and k == dis - 1:
            filt.append(f"{last}settb=AVTB,fps={FPS}[pa{k}];[{k}:v]settb=AVTB,fps={FPS}[pb{k}];"
                        f"[pa{k}][pb{k}]xfade=transition=fade:duration={XF}:offset={t - XF:.3f}{out}")
            t -= XF
        else:
            filt.append(f"{last}[{k}:v]concat=n=2:v=1:a=0{out}")
        starts.append(t)
        t += durs[k]
        last = out
    video = os.path.join(work, "video.mp4")
    run("ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", last,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", video)

    ain = sum((["-i", v] for v in voices), [])
    af = "".join(f"[{k + 1}:a]adelay={int(s * 1000)}|{int(s * 1000)}[a{k}];" for k, s in enumerate(starts))
    af += "".join(f"[a{k}]" for k in range(len(voices))) + f"amix=inputs={len(voices)}:normalize=0[a]"
    final = os.path.join(ep_dir, job["output"])
    run("ffmpeg", "-y", "-loglevel", "error", "-i", video, *ain, "-filter_complex", af,
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", final)
    print(final, round(duration(final), 1), "s")


if __name__ == "__main__":
    main(sys.argv[1])

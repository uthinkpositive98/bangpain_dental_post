"""Render a Pivot-style episode (videos/<ep>/scenes.py) to MP4, and mix in the narration.

  python3 tools/pivot_render.py videos/<ep> --preview      # stills of every scene -> videos/<ep>/contact.png (fast check)
  python3 tools/pivot_render.py videos/<ep> --silent       # full animation without voice -> videos/<ep>/.work/silent.mp4
  python3 tools/pivot_render.py videos/<ep>                # full build: animation + voices from job.json -> <output>.mp4

scenes.py must define SCENES = [Scene(...), ...] (see tools/pivot.py). job.json:
  {"output": "<ep>.mp4", "voices": ["https://...scene1.mp3", ...]}   one URL per scene, in order.
Each voice clip starts 0.15 s into its scene; a clip longer than its scene is sped up slightly (max 1.25x) to fit.
"""
import argparse, importlib.util, json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from tools.pivot import W, H, FPS, track_value  # noqa: E402

FONT_CSS = "".join(
    f"@font-face{{font-family:K;font-weight:{w};src:url(file://{HERE}/fonts/kanit-{sub}-{w}-normal.woff2);"
    f"unicode-range:{rng}}}"
    for w in (400, 600, 700) for sub, rng in (("thai", "U+0E00-0E7F"), ("latin", "U+0000-024F,U+2000-206F,U+20AC")))

PAGE = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:#fff;font-family:K,Loma,sans-serif}}
#stage{{position:absolute;inset:0;overflow:hidden}}
#cam{{position:absolute;inset:0;transform-origin:50% 50%}}
#bg{{position:absolute;inset:0;width:{W}px;height:{H}px}}
#fg{{position:absolute;inset:0}}
#title{{position:absolute;top:120px;left:40px;right:40px;text-align:center;font-size:100px;font-weight:700;color:#fff;
  -webkit-text-stroke:16px #2b2622;paint-order:stroke fill;line-height:1.18;letter-spacing:1px;text-wrap:balance}}
#sub{{position:absolute;bottom:80px;left:60px;right:60px;text-align:center;font-size:54px;font-weight:600;color:#fff;
  line-height:1.42;text-wrap:balance;background:rgba(14,94,99,.84);border-radius:30px;padding:24px 34px;box-shadow:0 10px 0 rgba(0,0,0,.22)}}
#sub:empty,#title:empty{{display:none}}
</style></head><body><div id="stage"><div id="cam"><img id="bg"><svg id="fg" width="{W}" height="{H}"
 viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"></svg></div><div id="title"></div><div id="sub"></div></div>
<script>
function setScene(bg, title, sub){{document.getElementById('bg').src=bg;
 document.getElementById('title').innerHTML=title||'';document.getElementById('sub').innerHTML=sub||'';
 return new Promise(r=>{{const i=document.getElementById('bg'); if(i.complete) r(); else {{i.onload=()=>r(); i.onerror=()=>r(); setTimeout(r,5000);}}}});}}
function frame(svg, z, x, y){{document.getElementById('fg').innerHTML=svg;
 document.getElementById('cam').style.transform=`translate(${{x}}px,${{y}}px) scale(${{z}})`;}}
</script></body></html>"""


def load(ep):
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(ep, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scenes = list(mod.SCENES)
    # Owner's standing rule: every video ends with the 5-second clinic end card (logo + phone + all contact channels).
    from tools.pivot import Scene, endcard_fg
    if not scenes or scenes[-1].bg != "endcard":
        print("  no end card at the end -> adding the 5 s clinic end card automatically")
        scenes.append(Scene("endcard", endcard_fg, "", sub="", dur=5))
    scenes[-1].dur = max(scenes[-1].dur, 5.0)
    return scenes


def svg_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}html,body{{margin:0;width:{W}px;'
            f'height:{H}px;overflow:hidden}}</style></head><body><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'xmlns="http://www.w3.org/2000/svg">{body}</svg></body></html>')


def render_backgrounds(pg, scenes, work):
    from tools.pivot import BG
    paths = []
    for i, sc in enumerate(scenes, 1):
        body = BG[sc.bg]() if sc.bg in BG else sc.bg
        out = os.path.abspath(os.path.join(work, f"bg{i}.png"))
        html = os.path.join(work, f"bg{i}.html")
        open(html, "w", encoding="utf-8").write(svg_doc(body))
        pg.goto("file://" + os.path.abspath(html))
        pg.evaluate("document.fonts.ready.then(() => 1)")
        pg.wait_for_timeout(120)
        pg.screenshot(path=out)
        paths.append(out)
    return paths


def cam_at(sc, t):
    z, x, y = track_value(sc.cam, t, (1.0, 0, 0))
    if sc.shake:
        dx, dy = sc.shake(t)
        x, y = x + dx, y + dy
    return z, x, y


def goto_stage(pg, work):
    html = os.path.join(work, "stage.html")
    open(html, "w", encoding="utf-8").write(PAGE)
    pg.goto("file://" + os.path.abspath(html))


def open_page(p):
    b = p.chromium.launch(args=["--disable-gpu", "--font-render-hinting=none"])
    pg = b.new_page(viewport={"width": W, "height": H})
    return b, pg


def preview(ep, scenes, work):
    from PIL import Image
    from playwright.sync_api import sync_playwright
    shots = []
    with sync_playwright() as p:
        b, pg = open_page(p)
        bgs = render_backgrounds(pg, scenes, work)
        goto_stage(pg, work)
        for i, (sc, bgp) in enumerate(zip(scenes, bgs), 1):
            pg.evaluate("([b,t,s]) => setScene(b,t,s)", ["file://" + bgp, sc.title or "", sc.sub])
            pg.evaluate("document.fonts.ready.then(() => 1)")
            row = []
            for k in (0.12, 0.5, 0.88):
                t = sc.dur * k
                z, x, y = cam_at(sc, t)
                pg.evaluate("([s,z,x,y]) => frame(s,z,x,y)", [sc.draw(t), z, x, y])
                out = os.path.join(work, f"prev{i}_{int(k * 100)}.png")
                pg.screenshot(path=out)
                row.append(out)
            shots.append(row)
        b.close()
    tw, th = 240, 427
    sheet = Image.new("RGB", (3 * (tw + 8) + 60, len(shots) * (th + 8)), "white")
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for r, row in enumerate(shots):
        dr.text((10, r * (th + 8) + 10), str(r + 1), fill="black")
        for c, f in enumerate(row):
            sheet.paste(Image.open(f).resize((tw, th)), (60 + c * (tw + 8), r * (th + 8)))
    out = os.path.join(ep, "contact.png")
    sheet.save(out)
    print("preview ->", out)
    return out


def render_video(scenes, work, out, fps=FPS):
    from playwright.sync_api import sync_playwright
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg",
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-r", str(fps), out], stdin=subprocess.PIPE)
    total = sum(int(round(sc.dur * fps)) for sc in scenes)
    done = 0
    with sync_playwright() as p:
        b, pg = open_page(p)
        bgs = render_backgrounds(pg, scenes, work)
        goto_stage(pg, work)
        for sc, bgp in zip(scenes, bgs):
            pg.evaluate("([b,t,s]) => setScene(b,t,s)", ["file://" + bgp, sc.title or "", sc.sub])
            pg.evaluate("document.fonts.ready.then(() => 1)")
            for f in range(int(round(sc.dur * fps))):
                t = f / fps
                z, x, y = cam_at(sc, t)
                pg.evaluate("([s,z,x,y]) => frame(s,z,x,y)", [sc.draw(t), z, x, y])
                ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
                done += 1
                if done % 150 == 0:
                    print(f"  frame {done}/{total}", flush=True)
        b.close()
    ff.stdin.close()
    ff.wait()
    return out


def duration(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True).stdout
    return float(o)


def mix(scenes, video, voices, out):
    starts, t = [], 0.0
    for sc in scenes:
        starts.append(t)
        t += sc.dur
    inputs, filt, labels = ["-i", video], [], []
    for k, (v, st, sc) in enumerate(zip(voices, starts, scenes)):
        if not v:
            continue
        dv = duration(v)
        room = sc.dur - 0.25
        tempo = min(1.25, dv / room) if dv > room else 1.0
        if tempo > 1:
            print(f"  scene {k + 1}: voice {dv:.2f}s > {room:.2f}s, sped up x{tempo:.2f}")
        inputs += ["-i", v]
        n = len(labels) + 1
        ms = int((st + 0.15) * 1000)
        filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,atempo={tempo:.4f},adelay={ms}|{ms}[a{n}]")
        labels.append(f"[a{n}]")
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,"
                f"loudnorm=I=-14:TP=-1.5:LRA=11,apad[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "0:v",
                    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{t:.3f}",
                    "-movflags", "+faststart", out], check=True)
    print(out, round(duration(out), 1), "s")


def trim(src, dst):
    """Cut leading/trailing silence from a voice clip so it fits its 4-second scene."""
    f = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", f, "-ar", "48000", dst], check=True)
    return dst


def fit_scenes(scenes, voices, max_stretch=1.6):
    """A scene is exactly its nominal length (4 s) unless its narration needs more: then it is held up to +1.6 s
    (last pose and camera simply hold); anything longer still is sped up in mix()."""
    for k, (sc, v) in enumerate(zip(scenes, voices)):
        if not v:
            continue
        need = duration(v) + 0.4
        if need > sc.dur:
            new = round(min(sc.dur + max_stretch, need), 2)
            print(f"  scene {k + 1}: voice {need - 0.4:.2f}s -> scene {sc.dur:.1f}s held to {new:.2f}s")
            sc.dur = new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--silent", action="store_true")
    ap.add_argument("--fps", type=int, default=FPS)
    a = ap.parse_args()
    scenes = load(a.ep)
    work = os.path.join(a.ep, ".work")
    os.makedirs(work, exist_ok=True)
    print(f"{len(scenes)} scenes, {sum(s.dur for s in scenes):.1f} s")
    if a.preview:
        preview(a.ep, scenes, work)
        return
    if a.silent:
        print(render_video(scenes, work, os.path.join(work, "silent.mp4"), a.fps))
        return
    job = json.load(open(os.path.join(a.ep, "job.json"), encoding="utf-8"))
    vdir = os.path.join(a.ep, "voice")
    os.makedirs(vdir, exist_ok=True)
    voices = []
    for i, url in enumerate(job["voices"], 1):
        if not url:
            voices.append(None)
            continue
        dst = os.path.join(vdir, f"scene{i}.mp3")
        if url.startswith("http"):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
                f.write(r.read())
        else:
            dst = url
        voices.append(trim(dst, os.path.join(work, f"voice{i}.wav")))
    fit_scenes(scenes, voices)
    silent = render_video(scenes, work, os.path.join(work, "silent.mp4"), a.fps)
    mix(scenes, silent, voices, os.path.join(a.ep, job["output"]))


if __name__ == "__main__":
    main()

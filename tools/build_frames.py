"""Render an episode's scenes to final 1080x1920 frames (scene art + Thai title + subtitle box).

Usage: python3 tools/build_frames.py videos/<episode>
Reads videos/<episode>/scenes.py (must define SCENES = [dict(html=..., title=..., sub=...)]).
Writes videos/<episode>/frames/frame1.png ... and videos/<episode>/contact.png (review sheet).
title=None renders the clinic end card (name + phone) instead of a title.
"""
import base64, importlib.util, os, sys
from playwright.sync_api import sync_playwright
from PIL import Image

W, H = 1080, 1920
CSS = """
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:'Loma',sans-serif;}
.wrap{position:relative;width:1080px;height:1920px;}
.bg{position:absolute;inset:0;width:1080px;height:1920px;}
.title{position:absolute;top:120px;left:40px;right:40px;text-align:center;font-size:104px;font-weight:bold;color:#fff;
  -webkit-text-stroke:14px #1d1d1f;paint-order:stroke fill;line-height:1.2;}
.sub{position:absolute;bottom:70px;left:70px;right:70px;text-align:center;font-size:58px;font-weight:bold;color:#fff;
  line-height:1.45;background:rgba(14,94,99,.8);border-radius:28px;padding:26px 34px;box-shadow:0 10px 0 rgba(0,0,0,.25);}
.cta{position:absolute;top:110px;left:40px;right:40px;text-align:center;color:#fff;font-weight:bold;
  -webkit-text-stroke:12px #138a8f;paint-order:stroke fill;}
.cta .a{font-size:84px;line-height:1.2}.cta .b{font-size:96px;margin-top:20px;-webkit-text-stroke:12px #f08a3c;}
"""


def main(ep_dir):
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(ep_dir, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scenes = mod.SCENES
    raw_dir, out_dir = os.path.join(ep_dir, ".work", "raw"), os.path.join(ep_dir, "frames")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, sc in enumerate(scenes, 1):
            raw = os.path.join(raw_dir, f"scene{i}.png")
            pg.set_content(sc["html"])
            pg.wait_for_timeout(150)
            pg.screenshot(path=raw)
            img = base64.b64encode(open(raw, "rb").read()).decode()
            top = (f'<div class="title">{sc["title"]}</div>' if sc.get("title") else
                   '<div class="cta"><div class="a">คลินิกทันตกรรมบางปะอิน</div><div class="b">☎ 092-359-5963</div></div>')
            pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
                           f'<div class="wrap"><img class="bg" src="data:image/png;base64,{img}">{top}'
                           f'<div class="sub">{sc["sub"]}</div></div></body></html>')
            pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(out_dir, f"frame{i}.png"))
        b.close()
    # contact sheet for a quick visual check
    thumbs = [Image.open(os.path.join(out_dir, f"frame{i}.png")).resize((270, 480)) for i in range(1, len(scenes) + 1)]
    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 280, rows * 490), "white")
    for k, t in enumerate(thumbs):
        sheet.paste(t, ((k % cols) * 280, (k // cols) * 490))
    sheet.save(os.path.join(ep_dir, "contact.png"))
    print(f"{len(scenes)} frames -> {out_dir}; review sheet {ep_dir}/contact.png")


if __name__ == "__main__":
    main(sys.argv[1])

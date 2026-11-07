"""
โพสต์คลิปของตอนหนึ่ง (Release <slug>/<slug>.mp4 + videos/<slug>/caption.txt) ลงเพจคลินิกเป็น Facebook Reel โดยตรง
ผ่าน Graph API (ไม่ผ่าน Metricool) — ใช้กับ .github/workflows/facebook-post-reel.yml
ต้องมี GitHub Secrets: ACCESS_TOKEN (Page token ของเพจคลินิก), FB_PAGE_ID
"""
import json, os, sys, time
import requests

VERSION = "v27.0"
GRAPH = f"https://graph.facebook.com/{VERSION}"
REPO = os.environ.get("GITHUB_REPOSITORY", "uthinkpositive98/bangpain_dental_post")


class FBError(Exception):
    pass


def check(r, what):
    try:
        data = r.json()
    except ValueError:
        data = {}
    err = data.get("error") if isinstance(data, dict) else None
    if r.status_code >= 400 or err:
        err = err or {}
        code = err.get("code")
        hint = " — token หมดอายุ/ใช้ไม่ได้: ทำ Page token ใหม่แล้วใส่ ACCESS_TOKEN" if code == 190 else ""
        raise FBError(f"{what} ไม่สำเร็จ (HTTP {r.status_code}, code {code}): {err.get('error_user_msg') or err.get('message') or r.text[:300]}{hint}")
    return data


def summary(line):
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(line + "\n\n")


def main():
    slug = sys.argv[1].strip()
    page, token = os.environ["FB_PAGE_ID"].strip(), os.environ["FB_PAGE_TOKEN"].strip()
    cap_path = f"videos/{slug}/caption.txt"
    if not os.path.exists(cap_path):
        sys.exit(f"::error::ไม่พบ {cap_path}")
    caption = open(cap_path, encoding="utf-8").read().strip()[:5000]
    url = f"https://github.com/{REPO}/releases/download/{slug}/{slug}.mp4"
    path = f"{slug}.mp4"
    with requests.get(url, stream=True, timeout=300) as r:
        if r.status_code != 200:
            sys.exit(f"::error::ดาวน์โหลดคลิปไม่ได้ ({r.status_code}): {url}")
        with open(path, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    size = os.path.getsize(path)
    print(f"คลิป {path} {size/1e6:.1f} MB")

    start = check(requests.post(f"{GRAPH}/{page}/video_reels", data={"upload_phase": "start", "access_token": token}, timeout=60), "เริ่มอัปโหลด Reel")
    vid, up = start["video_id"], start["upload_url"]
    with open(path, "rb") as fh:
        r = requests.post(up, headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)}, data=fh, timeout=900)
    if not check(r, "อัปโหลดไฟล์ Reel").get("success"):
        raise FBError(f"อัปโหลดไฟล์ไม่สำเร็จ: {r.text[:300]}")
    check(requests.post(f"{GRAPH}/{page}/video_reels", data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                                              "description": caption, "access_token": token}, timeout=120), "เผยแพร่ Reel")
    print(f"ส่ง Reel แล้ว video_id={vid} รอ Facebook ประมวลผล...")
    status = "?"
    for _ in range(48):
        time.sleep(15)
        st = check(requests.get(f"{GRAPH}/{vid}", params={"fields": "status", "access_token": token}, timeout=60), "เช็กสถานะ").get("status", {})
        phases = [st.get(k, {}) for k in ("uploading_phase", "processing_phase", "publishing_phase")]
        if st.get("video_status") == "error" or any(p.get("status") == "error" for p in phases):
            raise FBError(f"Facebook ประมวลผล Reel ไม่ผ่าน: {json.dumps(st, ensure_ascii=False)[:500]}")
        status = st.get("publishing_phase", {}).get("status") or st.get("video_status")
        if status == "complete" or st.get("video_status") == "ready":
            break
    link = ""
    try:
        link = check(requests.get(f"{GRAPH}/{vid}", params={"fields": "permalink_url", "access_token": token}, timeout=60), "ขอลิงก์").get("permalink_url", "")
        if link.startswith("/"):
            link = "https://www.facebook.com" + link
    except FBError as e:
        print(e)
    print(f"REEL_ID={vid}\nREEL_STATUS={status}\nREEL_URL={link}")
    summary(f"โพสต์ Reel `{slug}` แล้ว — สถานะ {status} — {link or vid}")


if __name__ == "__main__":
    try:
        main()
    except (FBError, requests.RequestException) as e:
        print(f"::error::{e}")
        summary(f"โพสต์ไม่สำเร็จ: {e}")
        sys.exit(1)

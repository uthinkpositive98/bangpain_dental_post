"""
ดึงสถิติเพจคลินิกจาก Facebook Graph API (อ่านอย่างเดียว ไม่โพสต์อะไร ไม่พิมพ์ token)
เขียนผลลง data/fb_stats.json (ภาพล่าสุด) และ data/fb_history.json (สะสมรายวัน ไว้ดูแนวโน้ม)
ใช้กับ .github/workflows/facebook-stats.yml — ต้องมี Secrets: ACCESS_TOKEN, FB_PAGE_ID

ตัวเลขที่ token ปัจจุบัน (pages_read_engagement) อ่านได้: ผู้ติดตาม, โพสต์/Reel, ไลก์, คอมเมนต์, แชร์, ยอดวิว (ถ้า Facebook ให้)
ตัวเลขเชิงลึก (reach, เวลาดูเฉลี่ย) ต้องมีสิทธิ์ read_insights — สคริปต์จะลองขอ ถ้าไม่ได้จะจดไว้ใน "unavailable"
"""
import datetime as dt
import json
import os
import requests

G = "https://graph.facebook.com/v27.0"
TOKEN = os.environ["FB_PAGE_TOKEN"].strip()
PAGE = os.environ["FB_PAGE_ID"].strip()
H = {"Authorization": f"Bearer {TOKEN}"}
TZ = dt.timezone(dt.timedelta(hours=7))
DAYS = 90
unavailable = []


def get(path, **params):
    """คืน (data, error_message). ไม่ใส่ token ใน URL เพื่อไม่ให้หลุดใน log"""
    try:
        r = requests.get(f"{G}/{path}", params=params, headers=H, timeout=60)
        d = r.json()
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__
    if isinstance(d, dict) and d.get("error"):
        e = d["error"]
        return None, f"({e.get('code')}) {str(e.get('message'))[:200]}"
    return d, None


def paged(path, limit_pages=10, **params):
    out, err = [], None
    d, err = get(path, **params)
    pages = 0
    while d and pages < limit_pages:
        out += d.get("data", [])
        after = (d.get("paging", {}).get("cursors") or {}).get("after")
        if not after or not d.get("paging", {}).get("next"):
            break
        d, err = get(path, after=after, **params)
        pages += 1
    return out, err


def first_ok(path, field_sets, **params):
    """ลองชุด field จากมากไปน้อย จนกว่าจะมีชุดที่ Facebook ยอมให้"""
    for fields in field_sets:
        data, err = paged(path, fields=fields, **params)
        if err is None:
            return data, fields
        unavailable.append({"what": f"{path.split('/')[-1]}: {fields[:60]}", "why": err})
    return [], None


def total(obj, key):
    return ((obj.get(key) or {}).get("summary") or {}).get("total_count")


def main():
    now = dt.datetime.now(TZ)
    since = int((now - dt.timedelta(days=DAYS)).timestamp())

    page, err = get(PAGE, fields="name,followers_count,fan_count")
    if err:
        page, err2 = get(PAGE, fields="name")
        unavailable.append({"what": "followers_count", "why": err})
        if err2:
            raise SystemExit(f"::error::อ่านเพจไม่ได้: {err2}")

    eng = "shares,reactions.summary(total_count).limit(0),comments.summary(total_count).limit(0)"
    posts, _ = first_ok(
        f"{PAGE}/published_posts",
        [
            f"id,created_time,message,permalink_url,status_type,attachments{{media_type,target}},{eng}",
            f"id,created_time,message,permalink_url,{eng}",
            "id,created_time,message,permalink_url",
        ],
        since=since, limit=50,
    )

    vfields_eng = "likes.summary(total_count).limit(0),comments.summary(total_count).limit(0)"
    base = "id,description,title,created_time,permalink_url,length"
    reels, _ = first_ok(f"{PAGE}/video_reels", [f"{base},views,{vfields_eng}", f"{base},{vfields_eng}", base], limit=50)
    videos, _ = first_ok(f"{PAGE}/videos", [f"{base},views,{vfields_eng}", f"{base},{vfields_eng}", base], limit=50)

    # รวม Reel + วิดีโอ (ตัด id ซ้ำ) แล้วจับคู่กับโพสต์เพื่อเอายอดแชร์/รีแอคชัน
    post_by_target = {}
    for p in posts:
        for a in ((p.get("attachments") or {}).get("data") or []):
            tid = (a.get("target") or {}).get("id")
            if tid:
                post_by_target[tid] = p
    clips, seen = [], set()
    for kind, rows in (("reel", reels), ("video", videos)):
        for v in rows:
            if v["id"] in seen:
                continue
            seen.add(v["id"])
            p = post_by_target.get(v["id"], {})
            link = v.get("permalink_url") or ""
            if link.startswith("/"):
                link = "https://www.facebook.com" + link
            clips.append({
                "id": v["id"], "kind": kind,
                "created": v.get("created_time"),
                "text": (v.get("description") or v.get("title") or p.get("message") or "").strip()[:400],
                "seconds": round(v.get("length") or 0),
                "url": link,
                "views": v.get("views"),
                "likes": total(v, "likes"),
                "reactions": total(p, "reactions"),
                "comments": total(v, "comments") if total(v, "comments") is not None else total(p, "comments"),
                "shares": (p.get("shares") or {}).get("count", 0 if p else None),
            })

    # ลองขอตัวเลขเชิงลึก (ต้องมี read_insights) — ลองกับคลิปล่าสุดคลิปเดียวก่อน ถ้าได้ค่อยขอทั้งหมด
    clips.sort(key=lambda c: c["created"] or "", reverse=True)
    vm_try = ["blue_reels_play_count", "fb_reels_total_plays", "post_impressions_unique", "post_video_avg_time_watched",
              "post_video_view_time", "post_video_social_actions", "post_video_views", "total_video_impressions_unique",
              "total_video_avg_time_watched", "total_video_views"]
    vm_ok = []
    if clips:
        for m in vm_try:  # ลองทีละตัวกับคลิปล่าสุด เก็บเฉพาะตัวที่ Facebook ยอมให้
            d, err = get(f"{clips[0]['id']}/video_insights", metric=m)
            if err is None and d.get("data"):
                vm_ok.append(m)
            elif err:
                unavailable.append({"what": f"video_insights:{m}", "why": err})
        if vm_ok:
            for c in clips[:40]:
                d, e = get(f"{c['id']}/video_insights", metric=",".join(vm_ok))
                if d:
                    c["insights"] = {m["name"]: (m.get("values") or [{}])[0].get("value") for m in d.get("data", [])}
    page_insights = {}
    for m in ["page_impressions_unique", "page_post_engagements", "page_video_views", "page_views_total",
              "page_daily_follows_unique", "page_follows"]:
        pi, err = get(f"{PAGE}/insights", metric=m, period="day",
                      since=int((now - dt.timedelta(days=28)).timestamp()), until=int(now.timestamp()))
        if err:
            unavailable.append({"what": f"page_insights:{m}", "why": err})
        elif pi.get("data"):
            page_insights[m] = [{"d": v.get("end_time", "")[:10], "v": v.get("value")} for v in pi["data"][0].get("values", [])]
    page_insights = page_insights or None

    other_posts = []
    clip_post_ids = {p["id"] for p in post_by_target.values()}

    def is_clip_post(p):
        # ไม่มีสิทธิ์อ่าน attachments ก็จับคู่ด้วยข้อความ+เวลา (โพสต์ของ Reel ถูกสร้างภายในไม่กี่นาทีหลังคลิป)
        t = (p.get("message") or "").strip()
        for c in clips:
            if not c["created"] or not p.get("created_time"):
                continue
            gap = abs((dt.datetime.fromisoformat(p["created_time"].replace("+0000", "+00:00"))
                       - dt.datetime.fromisoformat(c["created"].replace("+0000", "+00:00"))).total_seconds())
            if gap <= 600 and (not t or not c["text"] or t[:30] == c["text"][:30]):
                return True
        return False

    for p in posts:
        if p["id"] in clip_post_ids or is_clip_post(p):
            continue
        other_posts.append({
            "id": p["id"], "created": p.get("created_time"), "text": (p.get("message") or "").strip()[:300],
            "url": p.get("permalink_url"), "reactions": total(p, "reactions"),
            "comments": total(p, "comments"), "shares": (p.get("shares") or {}).get("count", 0),
        })

    stats = {
        "fetched_at": now.isoformat(timespec="seconds"),
        "source": "Facebook Graph API v27.0 (page token ใน GitHub Secrets)",
        "page": {"name": page.get("name"), "followers": page.get("followers_count"), "likes": page.get("fan_count")},
        "window_days": DAYS,
        "clips": clips,
        "other_posts": other_posts,
        "page_insights": page_insights,
        "unavailable": unavailable,
    }
    os.makedirs("data", exist_ok=True)
    with open("data/fb_stats.json", "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=1)

    # สะสมรายวัน: ผู้ติดตาม + ยอดของแต่ละคลิป ณ วันนั้น (ใช้คำนวณ "เพิ่มขึ้นเท่าไรใน 1 วัน / 7 วัน")
    hpath = "data/fb_history.json"
    hist = json.load(open(hpath, encoding="utf-8")) if os.path.exists(hpath) else {}
    hist[now.date().isoformat()] = {
        "followers": page.get("followers_count"),
        "clips": {c["id"]: [c["views"], c["reactions"] if c["reactions"] is not None else c["likes"], c["comments"], c["shares"]]
                  for c in clips},
    }
    for k in sorted(hist)[:-400]:
        del hist[k]
    with open(hpath, "w", encoding="utf-8") as fh:
        json.dump(hist, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    print(f"เพจ: {page.get('name')} | ผู้ติดตาม {page.get('followers_count')} | คลิป {len(clips)} | โพสต์อื่น {len(other_posts)}")
    for u in unavailable:
        print(f"ไม่ได้: {u['what']} — {u['why']}")


if __name__ == "__main__":
    main()

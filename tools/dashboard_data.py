"""
สร้างไฟล์ข้อมูลของแดชบอร์ด "Marketing System — คลินิกทันตกรรมบางปะอิน" จากสถิติที่ดึงมาจาก Facebook
อ่าน: data/fb_stats.json, data/fb_history.json, data/clip_labels.json, data/ideas.json
เขียน: <out>/summary.json clips.json patterns.json calendar.json ideas.json  (แต่ละไฟล์ = {rows, meta})
ใช้: python tools/dashboard_data.py [out_dir]
"""
import datetime as dt
import json
import statistics
import sys

TZ = dt.timezone(dt.timedelta(hours=7))
NEW_ERA = "2026-10-01"          # ตั้งแต่วันนี้ = ยุคคลิปความรู้ที่ทำด้วย Claude
POST_DAYS = {1, 3, 5, 6}        # อ./พฤ./ส./อา. 19:00 (Mon=0)
TH_MONTH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


def load(p, default=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        return default


def thai_dt(d):
    return f"{d.day} {TH_MONTH[d.month - 1]} {d.year} {d:%H:%M}"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data/dash"
    s = load("data/fb_stats.json")
    hist = load("data/fb_history.json", {})
    labels = load("data/clip_labels.json", {})
    ideas = load("data/ideas.json", {"ideas": []})["ideas"]
    fetched = dt.datetime.fromisoformat(s["fetched_at"])
    today = fetched.date()

    clips = []
    for c in s["clips"]:
        when = dt.datetime.fromisoformat(c["created"].replace("+0000", "+00:00")).astimezone(TZ)
        days = max((fetched - when).total_seconds() / 86400, 0)
        hook = (c["text"].split("\n")[0].strip() or "(ไม่มีแคปชัน)")[:90]
        new = when.date().isoformat() >= NEW_ERA
        clips.append({
            "id": c["id"], "date": when.date().isoformat(), "posted": thai_dt(when), "hook": hook,
            "pattern": labels.get(c["id"], "ยังไม่จัดกลุ่ม") if new else "คลิปยุคก่อน ต.ค. 2026",
            "era": "new" if new else "old", "in_28d": 0,
            "seconds": c["seconds"], "views": c["views"] or 0, "likes": c["likes"] or 0, "comments": c["comments"] or 0,
            "days_live": round(days, 1), "views_per_day": round((c["views"] or 0) / max(days, 1), 1), "url": c["url"],
        })
    clips.sort(key=lambda c: c["date"], reverse=True)

    def since(n):
        lo = (today - dt.timedelta(days=n - 1)).isoformat()
        return [c for c in clips if c["date"] >= lo]

    w28 = since(28)
    for c in w28:
        c["in_28d"] = 1
    month = [c for c in clips if c["date"][:7] == today.isoformat()[:7]]
    best = max(w28, key=lambda c: c["views"]) if w28 else None

    # แนว hook: ใช้เฉพาะคลิปยุคใหม่ที่ออกมาแล้วอย่างน้อย 3 วัน (คลิปใหม่กว่านั้นยอดยังไม่นิ่ง)
    groups = {}
    for c in clips:
        if c["era"] == "new" and c["days_live"] >= 3 and c["pattern"] != "ยังไม่จัดกลุ่ม":
            groups.setdefault(c["pattern"], []).append(c)
    patterns = []
    for name, rows in groups.items():
        top = max(rows, key=lambda c: c["views"])
        patterns.append({"pattern": name, "clips": len(rows), "median_views": round(statistics.median(c["views"] for c in rows)),
                         "max_views": top["views"], "best_hook": top["hook"]})
    patterns.sort(key=lambda p: p["median_views"], reverse=True)
    solid = [p for p in patterns if p["clips"] >= 3]

    # เทียบกับเมื่อวาน / 7 วันก่อน จากประวัติที่สะสมรายวัน (เริ่มเก็บ 15 พ.ย. 2026)
    def snap(days_ago):
        return hist.get((today - dt.timedelta(days=days_ago)).isoformat())
    y, w = snap(1), snap(7)
    cur_views = {c["id"]: c["views"] for c in clips}
    views_gain_1d = sum(max(v - ((y["clips"].get(i) or [0])[0] or 0), 0) for i, v in cur_views.items()) if y else None
    foll = s["page"]["followers"]
    summary = [{
        "fetched": thai_dt(fetched), "followers": foll,
        "followers_change_7d": (foll - w["followers"]) if w and w.get("followers") is not None else None,
        "views_gain_1d": views_gain_1d,
        "clips_28d": len(w28), "views_28d": sum(c["views"] for c in w28),
        "median_views_28d": round(statistics.median(c["views"] for c in w28)) if w28 else 0,
        "likes_28d": sum(c["likes"] for c in w28), "comments_28d": sum(c["comments"] for c in w28),
        "clips_month": len(month),
        "best_hook": best["hook"] if best else "", "best_views": best["views"] if best else 0,
        "top_pattern": solid[0]["pattern"] if solid else "", "top_pattern_median": solid[0]["median_views"] if solid else 0,
        "low_pattern": solid[-1]["pattern"] if len(solid) > 1 else "", "low_pattern_median": solid[-1]["median_views"] if len(solid) > 1 else 0,
        "old_best_views": max((c["views"] for c in clips if c["era"] == "old"), default=0),
        "new_best_views": max((c["views"] for c in clips if c["era"] == "new"), default=0),
    }]

    # ปฏิทิน: 4 สัปดาห์ที่ผ่านมา (รวมสัปดาห์นี้) + 2 สัปดาห์ข้างหน้า; ช่องอนาคต = วันโพสต์ประจำ + หัวข้อแนะนำตามลำดับ
    start = today - dt.timedelta(days=today.weekday() + 21)
    by_date = {}
    for c in clips:
        by_date.setdefault(c["date"], []).append(c)
    cal, idea_i = [], 0
    idea_rows = []
    for i in range(42):
        d = start + dt.timedelta(days=i)
        iso = d.isoformat()
        posted = by_date.get(iso, [])
        row = {"date": iso, "day": d.day, "month": TH_MONTH[d.month - 1], "kind": "none", "n": len(posted),
               "views": sum(c["views"] for c in posted), "label": " • ".join(c["hook"] for c in posted)}
        if posted:
            row["kind"] = "posted"
        elif d >= today and d.weekday() in POST_DAYS and idea_i < len(ideas):
            row["kind"], row["label"] = "suggested", ideas[idea_i]["hook"]
            idea_rows.append({"rank": idea_i + 1, "slot": f"{d.day} {TH_MONTH[d.month - 1]} 19:00", **ideas[idea_i]})
            idea_i += 1
        if d == today:
            row["today"] = 1
        cal.append(row)
    for j in range(idea_i, len(ideas)):
        idea_rows.append({"rank": j + 1, "slot": "ถัดไป", **ideas[j]})

    code = open(__file__, encoding="utf-8").read()
    meta = [{"label": "dashboard_data.py", "value": code, "type": "code", "lang": "python"},
            {"label": "ข้อมูลต้นทาง", "value": f"Facebook Graph API ดึงเมื่อ {thai_dt(fetched)} (data/fb_stats.json ใน GitHub repo bangpain_dental_post)"}]
    import os
    os.makedirs(out, exist_ok=True)
    for name, rows in (("summary", summary), ("clips", clips), ("patterns", patterns), ("calendar", cal), ("ideas", idea_rows)):
        with open(f"{out}/{name}.json", "w", encoding="utf-8") as fh:
            json.dump({"rows": rows, "meta": meta}, fh, ensure_ascii=False)
    print(json.dumps(summary[0], ensure_ascii=False, indent=1))
    for p in patterns:
        print(p)


if __name__ == "__main__":
    main()

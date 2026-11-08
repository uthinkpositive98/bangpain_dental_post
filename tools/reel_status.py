"""ตรวจสถานะ Reel ที่โพสต์ไปแล้ว: python tools/reel_status.py <video_id> [<video_id> ...]
พิมพ์สถานะการประมวลผล/เผยแพร่ของวิดีโอ และ Reels ล่าสุดของเพจ (ไม่พิมพ์ token)"""
import json, os, sys, requests
G = "https://graph.facebook.com/v21.0"; tok = os.environ["FB_PAGE_TOKEN"]; page = os.environ["FB_PAGE_ID"]
def get(path, **p):
    r = requests.get(f"{G}/{path}", params={**p, "access_token": tok}, timeout=60)
    try: return r.json()
    except Exception: return {"http": r.status_code, "text": r.text[:300]}
for vid in sys.argv[1:]:
    print(f"== video {vid}")
    print(json.dumps(get(vid, fields="status,published,permalink_url,created_time,updated_time,description,length,is_instagram_eligible"), ensure_ascii=False, indent=1)[:3000])
print("== page video_reels (latest 6)")
print(json.dumps(get(f"{page}/video_reels", fields="id,created_time,published,permalink_url,status", limit=6), ensure_ascii=False, indent=1)[:4000])
print("== page published_posts (latest 4)")
print(json.dumps(get(f"{page}/published_posts", fields="id,created_time,permalink_url,message", limit=4), ensure_ascii=False, indent=1)[:3000])

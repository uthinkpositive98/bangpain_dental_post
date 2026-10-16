# คู่มือโพสต์รายวัน — เพจคลินิกทันตกรรมบางปะอิน

Each scheduled run follows this guide exactly. One post per day, published at **17:28 Asia/Bangkok** on the Facebook page via Metricool.

## Fixed IDs
- Metricool brand / blogId: `7459912` (timezone Asia/Bangkok, network: facebook)
- Image host: this repo, public raw URL
  `https://raw.githubusercontent.com/uthinkpositive98/bangpain_dental_post/main/images/<file>.png`

## Steps for each run
1. `git pull` this repo. Read `topics.md` and `posted.md`.
2. Call Metricool `getScheduledPosts` for today (Asia/Bangkok). If a post with an image is already scheduled for today at 17:28, stop and report — do not post twice.
3. Pick today's topic:
   - Choose the category (A–G in `topics.md`) used least recently in `posted.md`.
   - Within it, pick a topic not yet in `posted.md`. If all in a category are used, write a new topic in the same spirit and add it to `topics.md`.
   - Never repeat a topic already in `posted.md`.
4. Write the post text (rules below).
5. Build the image (rules below): write an HTML file, render with
   `python3 render.py <file>.html images/YYYY-MM-DD-<slug>.png`, then **open the PNG and look at it**. Fix clipped/overlapping Thai text, empty areas, or anything unclear, and re-render.
6. Append one line to `posted.md`, commit image + log, `git push origin main`.
7. Call Metricool `createScheduledPost` (blogId 7459912), date today 17:28 +07:00:
   - `autoPublish: true`, `draft: false`, providers `[{"network":"facebook"}]`, `facebookData: {"type":"POST"}`
   - `media`: [raw URL of the pushed image], `mediaAltText`: [short Thai description]
   - `firstCommentText`: `""` (empty). **No link in the first comment either.**
   - If Metricool can't fetch the image, wait ~60 s and retry once.
   - If it is already past 17:28 when you reach this step, schedule for 5 minutes from now instead and say so in the report.
8. Report in one or two lines: topic, scheduled time, planner link.

## Post text rules
- Thai, friendly and plain; polite particle **ค่ะ / นะคะ**.
- Opening line: emoji + a question or hook as the headline.
- Body ~120–250 words: what it is / why it happens / what to do, with ✅ or numbered points. One clear takeaway.
- End the body with when to see a dentist (signs that need a check-up), worded gently.
- **No URL anywhere — not in the post text and not in any comment.** Facebook now limits Pages without a paid Meta One plan to 2 posts/comments with links per month, and a link in the first comment counts. Point people to the LINE/phone and the link on the Page profile instead.
- Then this footer, verbatim:

```
━━━━━━━━━━
ปรึกษาทันตแพทย์ได้ที่คลินิกทันตกรรมบางปะอิน
📍 ตรงข้ามการไฟฟ้าบางปะอิน
📞 โทร 092-359-5963
🕘 เปิดวันจันทร์ - วันอาทิตย์ 09:30 – 14:00 น. (หยุดวันศุกร์)
💬 แอดไลน์นัดหมายล่วงหน้า สะดวก ไม่ต้องรอนาน แอดไลน์ได้ที่เบอร์ 0923595963
🗓 ลงนัดออนไลน์ได้จากลิงก์บนหน้าเพจค่ะ
```
- Then 3–5 hashtags, always including `#คลินิกทันตกรรมบางปะอิน #บางปะอิน`.

## Accuracy and advertising rules (สถานพยาบาล — สบส.)
- Only well-established dental guidance. Do not invent statistics, studies, or percentages. Use "อาจ" for possibilities; no diagnosis, no medicine names or doses.
- Complications are explained calmly: what is normal, what is not, when to come back — never alarming.
- **Never**: prices, discounts, promotions, free offers; superlatives or guarantees ("ดีที่สุด", "อันดับ 1", "ไม่เจ็บแน่นอน", "หายขาด", "100%"); before/after; testimonials or patient stories; comparisons with other clinics; real patient photos; claims about specific doctors.

## Image rules
- 1080×1080 PNG, rendered from HTML with `render.py` (Playwright Chromium). Font: `Loma` (installed Thai font). Keep everything inline in one HTML file.
- Brand palette: deep teal `#0e5e63`, teal `#138a8f`, mint background `#e9fbf9 → #9fdcd8`, accent orange `#f08a3c`, white cards, blush `#ffb3a7`.
- Layout: big headline (≤ 2 lines) at top, an SVG illustration drawn for the topic (cute cartoon teeth, food, tools, simple diagrams), 2–4 short key points, bottom bar "คลินิกทันตกรรมบางปะอิน ☎ 092-359-5963".
- Vary the layout and illustration day to day (cards row, numbered list, split left/right, myth-vs-fact, do/don't columns, food icons…). `templates/example-floss.html` is one reference, not a fixed template.
- No real people, no blood/gore or surgical detail, no brand logos.

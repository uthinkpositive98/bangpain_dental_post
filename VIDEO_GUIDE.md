# คู่มือคลิป Reel อัตโนมัติ — คลินิกทันตกรรมบางปะอิน

One narrated cartoon Reel per run, published on the clinic Facebook page as a **Facebook Reel at 19:00 Asia/Bangkok**
every Monday, Tuesday, Thursday and Saturday. Each run does every step itself; nothing is left for the owner to do.

Fixed IDs
- Metricool blogId `7459912` (timezone Asia/Bangkok, network facebook)
- ElevenLabs voice: **Malee** `mYcpTKg1oj1H5CtzUZNO`, model `eleven_v4`, `generations_count: 1` per scene
- Repo `uthinkpositive98/bangpain_dental_post`; finished video URL:
  `https://github.com/uthinkpositive98/bangpain_dental_post/releases/download/<slug>/<slug>.mp4`

## Posting days and the Metricool cap (free plan: 20 scheduled posts per month)
- Until 2026-10-31: Reels on Monday, Tuesday, Thursday, Saturday.
- From 2026-11-01: Reels on **Monday, Thursday, Saturday only**. If today is a Tuesday on or after 2026-11-01, do nothing
  and report "skipped: Tuesday is not a Reel day from November".

## Pipeline (do in order)

1. **Setup.** Repo in session (add with push access if missing), cloned, `git pull`. Read this guide, `video_topics.md`,
   `videos_posted.md`, `tools/cartoon.py` (the drawing toolkit) and `videos/ep1-no-brushing-30-days/scenes.py` (worked example).
2. **Double-post guard.** Metricool `getScheduledPosts` for today. If a Facebook REEL is already scheduled today at 19:00,
   stop and report. If it is already past 18:40, schedule for the next free 19:00 slot of Mon/Tue/Thu/Sat instead.
3. **Pick the topic.** Next unused topic in `video_topics.md`, rotating categories so the last two episodes differ. Never
   repeat one in `videos_posted.md`. Slug: `epN-<short-english-slug>` (N = last episode number + 1).
4. **Storyboard first** → write `videos/<slug>/storyboard.md` (rules below): logline, characters, 8–11 scenes, each with
   time, what we see (setting, characters, poses, props, background details), narration line, on-screen title, subtitle.
5. **Draw** → write `videos/<slug>/scenes.py` using `tools/cartoon.py` (art direction below), then
   `python3 tools/build_frames.py videos/<slug>`. **Open `videos/<slug>/contact.png` and every frame you are unsure about
   and look at them.** Fix and re-render anything wrong: text clipped or overlapping, a character cut off or hidden under
   the subtitle box, empty-looking scenes, a face that reads the wrong emotion, anatomy that would mislead.
6. **Voice.** For each scene call ElevenLabs `creative_generate_speech` (one shared flow per episode via
   `creative_create_flow`; voice Malee; eleven_v4; generations_count 1). Then one `creative_get_flow_run_status` with all
   session_ids; keep each generation's `content_url` in scene order. If a generation failed, regenerate only that scene once.
7. **Build.** Write `videos/<slug>/job.json`:
   `{"output": "<slug>.mp4", "dissolve_into_scene": <scene number where the mood turns, or omit>, "voices": [url1, ...]}`
   Commit storyboard, scenes.py, frames/, contact.png, job.json; push to main. GitHub Actions ("Build video") downloads the
   voices, fits each scene to its clip length, and publishes `<slug>.mp4` to a Release tagged `<slug>`.
   Wait for it: poll `git ls-remote --tags https://github.com/uthinkpositive98/bangpain_dental_post` every 20 s for the tag
   (up to 15 min). The signed voice URLs expire after 2 hours, so push right after generating.
8. **Post.** Metricool `createScheduledPost`, date today 19:00 +07:00:
   `providers [{"network":"facebook"}]`, `facebookData {"type":"REEL"}`, `autoPublish true`, `media [release mp4 URL]`,
   `firstCommentText ""`, `text` = caption (rules below). Metricool re-hosts the file; the response media URL should be
   static.metricool.com.
9. **Log.** Append to `videos_posted.md`, commit, push. Report in two lines: episode title, scheduled time, planner link.
   On any failure, say exactly which step failed and what was done before it.

## Story and script rules
- 45–70 seconds total, 8–11 scenes, 4–9 seconds of narration each. Thai, friendly, light humour; polite particle ค่ะ/นะคะ.
- Structure: **Hook** (a question or a funny situation, scene 1) → **problem escalates** (2–3 beats, each a little funnier or
  worse) → **turn** (what really causes it / the myth busted) → **what to do** (2–3 concrete tips) → **end card** (last scene,
  `title=None`, narration ends with "ตรวจสุขภาพฟันได้ที่ คลินิกทันตกรรมบางปะอิน โทร 092-359-5963 ค่ะ").
- Recurring cast: **ต้น** (teal shirt, everyman who makes the mistakes), **หมอฟันยิ้ม** (tooth mascot = the clinic, appears
  at the turn), **แก๊งเชื้อโรค** (cute villains). New side characters are fine (friend, mum, kid — plain stick figures in
  other shirt colours).
- Each scene should have a small visual gag or a clear action, not just a character standing.
- Narration lines: short sentences, "..." for a pause, punctuation for rhythm. ElevenLabs v4 tags allowed sparingly at the
  start of a line: `[curious]`, `[excited]`, `[sad]`, `[happy]`, `[warmly]`, `[mischievously]`. Write numbers as digits.
- Subtitle (`sub`) = the narration without tags or "...", ≤ 2 lines (~70 Thai characters). Title = 1–4 words or None.
- Accuracy: only well-established dental guidance; no invented statistics; "อาจ" for possibilities; no medicine names or doses.
- Advertising rules (สบส.): no prices, promotions, superlatives, guarantees, before/after, testimonials, competitor comparisons.

## Art direction (target: hand-drawn cartoon feel like popular stick-figure story channels)
- Canvas 1080×1920. Keep characters and key action between y≈300 and y≈1620 (the title sits at the top, the subtitle box
  covers y≈1640–1850). `person(x, y)` takes the **hip** point; feet are at about y + 200×scale.
- **Rich backgrounds**: every scene gets a real setting with 5+ props and texture — walls with `speckles()` and maybe
  `cracks()`, floors with `planks()` or tiles, `window()`, furniture, shelves with objects, `plant()`, `ceiling_lamp()`,
  posters, a door. Add depth: a darker floor band, `shadow()` under every character and object, and `vignette()` last.
- Strong expressions and poses (moods: happy, big, talk, worried, sad, bored, squint, surprised, scared, angry). Use arms,
  tilt (`rot`), `sweat()`, `motion_lines()`, `sparkle()`, `speech_bubble()` (≤ 4 Thai words).
- Mouth/teeth close-ups: big cartoon teeth and gums like ep1 scenes 2, 4, 6 — friendly, never gory (no realistic blood,
  wounds, needles, or surgery). Germs are cute.
- Colours: warm, saturated, consistent; brand teal #138a8f / orange #f08a3c for the clinic and mascot.
- No text inside the art except speech bubbles and the clinic sign; the builder adds titles and subtitles.
- Vary camera: wide room shots, medium shots, extreme close-ups of teeth, an over-the-top reaction shot.

## Caption rules
```
<emoji> <episode title as a question or hook>

<2–3 short sentences: the key takeaway of the clip>

━━━━━━━━━━
ปรึกษาทันตแพทย์ได้ที่คลินิกทันตกรรมบางปะอิน
📍 ตรงข้ามการไฟฟ้าบางปะอิน
📞 โทร 092-359-5963
🕘 เปิดวันจันทร์ - วันอาทิตย์ 09:30 – 14:00 น. (หยุดวันศุกร์)
💬 แอดไลน์นัดหมายล่วงหน้า สะดวก ไม่ต้องรอนาน แอดไลน์ได้ที่เบอร์ 0923595963
🗓 ลงนัดออนไลน์ได้จากลิงก์บนหน้าเพจค่ะ

#คลินิกทันตกรรมบางปะอิน #บางปะอิน + 2–3 topic hashtags
```
No URL anywhere (Facebook limits Pages to 2 link posts/comments a month without a paid plan).

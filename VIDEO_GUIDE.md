# คู่มือคลิป Reel อัตโนมัติ — คลินิกทันตกรรมบางปะอิน

One narrated **Pivot-Animator-style stickman animation** per run, published on the clinic Facebook page as a
**Facebook Reel at 19:00 Asia/Bangkok** on the Reel days below. Each run does every step itself; nothing is left for the
owner to do.

**Standing rule from the owner (2026-10-18): every video is made in Pivot Animator style, following the "Stickman
Animation Video Engine" workflow, as detailed and spectacular as possible — the most fun storyboard, the most beautiful
cartoon linework, Ghibli-like colouring.** Pivot Animator itself is a Windows desktop app and cannot run in these cloud
sessions, so `tools/pivot.py` reproduces its technique: jointed stick skeletons posed on key frames and tweened in
between, at 30 fps. Do not fall back to still frames (`tools/cartoon.py` / `tools/assemble.py` are for old episodes only).

Fixed IDs
- Metricool blogId `7459912` (timezone Asia/Bangkok, network facebook)
- ElevenLabs voice: **Malee** `mYcpTKg1oj1H5CtzUZNO`, model `eleven_v4`, `generations_count: 1` per scene, one shared flow per episode
- Repo `uthinkpositive98/bangpain_dental_post`; finished video URL:
  `https://github.com/uthinkpositive98/bangpain_dental_post/releases/download/<slug>/<slug>.mp4`

## Posting days and the Metricool cap (free plan: 20 scheduled posts per month)
- Until 2026-10-31: Reels on Monday, Tuesday, Thursday, Saturday.
- From 2026-11-01: Reels on **Monday, Thursday, Saturday only**. If today is a Tuesday on or after 2026-11-01, do nothing
  and report "skipped: Tuesday is not a Reel day from November".

## The stickman workflow, answered once for this clinic (the steps that would ask the owner)
| Workflow step | Fixed answer |
|---|---|
| 1 Niche | Education — dental health (topics from `video_topics.md`) |
| 2 Character | **Character 1 — Orange Hoodie Pointer**: our hero **ต้น**, white round head, black oval eyes, expressive brows, bright orange hoodie with hood up and white drawstrings, dark trousers (`stickman()` in tools/pivot.py). Supporting cast: **หมอฟันยิ้ม** (tooth-doctor mascot = the clinic, `mascot()`), **แก๊งเชื้อโรค** (cute germs, `germ()`), the patient's tooth (`tooth_icon()`). Never change ต้น's outfit, face, colours or proportions. |
| 3 Format | 9:16 vertical, 1080×1920 |
| 4 Length | 60 seconds = **15 scenes**: 14 story scenes of exactly **4 s** + the clinic end card (5 s) → 61 s |
| 5 Idea | Generate the idea yourself from the next unused topic; do not ask |
Do every remaining step of the workflow (script, image prompts, animation prompts, thumbnail, titles, description)
in one go without stopping — the owner is not there to type NEXT.

## Pipeline (do in order)

1. **Setup.** Repo in session (add with push access if missing), cloned, `git pull`. Read this guide, `video_topics.md`,
   `videos_posted.md`, `tools/pivot.py` (the animation toolkit — read all of it) and the worked example
   `videos/demo-pivot-style/scenes.py`.
2. **Double-post guard.** Metricool `getScheduledPosts` for today. If a Facebook REEL is already scheduled today at 19:00,
   stop and report. If it is already past 18:30, schedule for the next free 19:00 slot of a Reel day instead.
3. **Pick the topic.** Next unused topic in `video_topics.md`, rotating categories so the last two episodes differ. Never
   repeat one in `videos_posted.md`. Slug: `epN-<short-english-slug>` (N = last episode number + 1).
4. **Storyboard** → `videos/<slug>/storyboard.md`, in the workflow's output format:
   VIDEO TITLE / NICHE / CHARACTER / FORMAT / DURATION / full VOICEOVER SCRIPT, then for **each of the 15 scenes**:
   voiceover line · what we see (setting, poses, props, gag) · the workflow's **Image prompt** (template below) ·
   the **4-second Animation prompt** (template below) · on-screen title · subtitle.
   Then: 10 title ideas, 1 thumbnail prompt, the caption (rules at the end) and keywords.
5. **Animate** → `videos/<slug>/scenes.py` with tools/pivot.py (art + animation rules below), then
   `python3 tools/pivot_render.py videos/<slug> --preview` and **open `videos/<slug>/contact.png`** (3 moments per scene).
   Fix anything wrong and re-preview: a limb at a broken angle, a character cut off or under the subtitle box, text
   clipped/overlapping, a scene that is empty or cluttered, a face that reads the wrong emotion. For a final check,
   `--silent` renders the full animation (~2 min); pull a few frames with ffmpeg and look at them.
6. **Voice.** `creative_create_flow` once, then per scene `creative_generate_speech` (voice Malee, eleven_v4,
   generations_count 1). One `creative_get_flow_run_status` with all session_ids; keep each `content_url` in scene order
   and read each `duration_secs` (it includes ~0.5 s of silence that the renderer trims). Aim for ≤ 4.2 s per story
   line; the renderer holds a scene's last pose up to +1.6 s when the narration needs it, and only beyond that speeds the
   voice up (max 1.25×, sounds rushed). Shorten and regenerate, once, any story line over 5.6 s.
7. **Build.** Write `videos/<slug>/job.json`: `{"output": "<slug>.mp4", "voices": [url1, ... url15]}`.
   Commit storyboard, scenes.py, contact.png, job.json; push to main. GitHub Actions ("Build video") renders the
   animation with `tools/pivot_render.py`, mixes each voice at the start of its scene, and publishes `<slug>.mp4` to a
   Release tagged `<slug>`. Wait for it: poll `git ls-remote --tags https://github.com/uthinkpositive98/bangpain_dental_post`
   every 30 s for the tag (up to 25 min). Signed voice URLs expire after 2 hours, so push right after generating.
8. **Post.** Metricool `createScheduledPost`, date today 19:00 +07:00:
   `providers [{"network":"facebook"}]`, `facebookData {"type":"REEL", "title": "<video title>"}`, `autoPublish true`,
   `media [release mp4 URL]`, `videoCoverMilliseconds` = a strong moment of scene 1 (e.g. 2500), `firstCommentText ""`,
   `text` = caption (rules below). The response media URL should be static.metricool.com.
9. **Log.** Append to `videos_posted.md`, commit, push. Report in two lines: episode title, scheduled time, planner link.
   On any failure, say exactly which step failed and what was done before it.

## Story and script rules (most fun storyboard possible)
- Thai, friendly, light humour, polite ค่ะ/นะคะ. Narrator style, clear and conversational, fast pacing, curiosity and
  tension; **hook in the first 3–5 seconds**; simple words; a natural conclusion + the clinic CTA at the end.
- Each story scene = one 4-second beat with **one clear action and a visual gag**. Structure across the 14 story scenes:
  hook (1) → ต้น's situation (2–3) → it escalates, each beat funnier or worse (4–7) → the turn: หมอฟันยิ้ม appears
  and explains/busts the myth (8–9) → what to do, 2–3 concrete tips shown as actions (10–13) → happy payoff (14) →
  end card (15: `Scene("endcard", endcard_fg, ..., sub="", dur=5)`, narration "ตรวจสุขภาพฟันได้ที่ คลินิกทันตกรรมบางปะอิน
  โทร 092-359-5963 ค่ะ").
- Narration per story scene: about **10–15 Thai syllables** (fits 3.7 s). Write numbers as digits. ElevenLabs v4 tags
  allowed sparingly at the start of a line: `[curious]`, `[excited]`, `[sad]`, `[happy]`, `[warmly]`, `[mischievously]`.
- Subtitle (`sub`) = the narration without tags or "...", ≤ 2 lines. Title = 1–4 words or None.
- Accuracy: only well-established dental guidance; no invented statistics; "อาจ" for possibilities; no medicine names or doses.
- Advertising rules (สบส.): no prices, promotions, superlatives about the clinic, guarantees, before/after, testimonials,
  competitor comparisons.

## Image prompt and animation prompt templates (write one of each per scene in storyboard.md)
Image prompt: "Create a clean 2D stickman animation frame in a simple viral YouTube explainer style. Use ต้น — the
orange hoodie stickman (round white head, black oval eyes, expressive eyebrows, orange hoodie with hood up and white
drawstrings, dark trousers) — as the main character. Maintain the exact same character design, outfit, face style, body
shape and colour palette across every scene. The scene shows [exact action]. Background: [BG key] painted in soft
Ghibli-like colours, kept minimal and uncluttered, with only the props needed. Composition: [camera angle, framing,
where the character is]. Emotion: [face + body language]. Thick ink outlines, flat colours with soft painted shading,
strong readable silhouettes, clear at small size." Character consistency lock + negative prompt: no photorealism, no 3D,
no clutter, no tiny text, no gore, no character changes.
Animation prompt (4 s): "Keep the character design exactly the same. No dialogue, lip-sync, captions or audio. ต้น
[movement / reaction / expression change]. Props: [subtle motion]. Camera: [push-in / pan / zoom / shake]. Simple,
readable motion matched to the emotion." — then implement exactly that in scenes.py.

## Animation and art direction (Pivot style, Ghibli colour, maximum detail)
- **Every scene moves.** Minimum per scene: 2–4 key poses for ต้น on a timeline (`[(t, P(...)), ...]` + `actor()`),
  with snappy easing (`"back"` for comic poses), plus a camera move in `cam` (push-in, pan, pull-back) and at least one
  secondary motion (`ambient()` petals/pollen/bubbles/fireflies, `drifting_clouds()`, bouncing germs, sparkles, props
  falling/flying, `pop_text()` comic words, `speech_bubble()` ≤ 4 Thai words, `shake()` on big moments).
  Use the motion helpers: `walk()`, `run()`, `hop()`, and the ready poses `WAVE, POINT, SHRUG, CHEER, SHOCK, SAD, THINK,
  FACEPALM, HANDS_HIPS, SIT` (modify with `.but(...)`). Breathing and blinking are automatic.
- Faces: use the 18 moods in `FACES` with big contrast between beats; eyes follow the action via `look=(dx,dy)`.
- **Backgrounds** (`BG`): `meadow`, `sunset`, `night` (stars, fireflies), `room`, `bathroom`, `clinic`, `mouth`
  (giant friendly teeth close-up), `paper` (white watercolour explainer), `endcard`. Painted once per scene: soft skies,
  big cumulus clouds, layered hills, warm window light beams, paper grain. Vary them across the episode; you may add new
  painted backgrounds to tools/pivot.py in the same style (gradients, `cloud()`, `ghibli_tree()`, `grass_tufts()`,
  `flowers()`, `filter="url(#wash)"`, `_paper_overlay()`), but keep compositions uncluttered.
- Framing: ต้น around s=1.1–1.3 for medium shots, bigger for close-ups. Keep characters and action between y≈300 and
  y≈1620 (title at the top, subtitle box covers y≈1640–1850); remember the camera zoom enlarges everything.
- Colours: warm, saturated but soft (Ghibli); brand teal #138a8f / orange #f08a3c. Germs are cute, teeth friendly,
  never gory (no blood, wounds, needles, surgery).
- No text in the art except titles, speech bubbles, pop words and the clinic sign.

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

# คู่มือคลิป Reel อัตโนมัติ — คลินิกทันตกรรมบางปะอิน

One narrated **kawaii cartoon Reel** per run, published on the clinic Facebook page as a **Facebook Reel at 19:00
Asia/Bangkok** on the Reel days below. Each run does every step itself; nothing is left for the owner to do.

**Standing rule from the owner (2026-10-18, replaces the earlier stickman rule): every video must match the quality and
look of ep3 "รากฟันเทียม ฮีโร่ไทเทเนียม"** (`videos/ep3-dental-implant-hero/`, watch its contact.png): a pastel 2D
cartoon drawn in code with `tools/kawaii.py` — characters with faces (teeth, the titanium implant hero, bone buddies,
germs) with big eyes, blush and blinking, squash-and-stretch bounces, cut-away gum/bone diagrams that explain the
treatment, bouncy pop-in Thai titles and pill captions, sparkles/bursts/confetti, iris transitions, a progress bar,
synthesized upbeat music with cartoon sound effects, a cheerful Thai narrator, and the clinic end card with the real
logo. **No stickman / Pivot style** (tools/pivot.py and the still-frame tools are for old episodes only).

Fixed IDs
- Metricool blogId `7459912` (timezone Asia/Bangkok, network facebook)
- ElevenLabs voice: **Nueng** `RIc0VzgLsI8EhceUkZx4` (cheerful young female), model `eleven_v4`,
  `generations_count: 1` per scene, one shared flow per episode
- Repo `uthinkpositive98/bangpain_dental_post`; finished video URL:
  `https://github.com/uthinkpositive98/bangpain_dental_post/releases/download/<slug>/<slug>.mp4`

## Posting days and the Metricool cap (free plan: 20 scheduled posts per month)
- Until 2026-10-31: Reels on Monday, Tuesday, Thursday, Saturday.
- From 2026-11-01: Reels on **Monday, Thursday, Saturday only**. If today is a Tuesday on or after 2026-11-01, do nothing
  and report "skipped: Tuesday is not a Reel day from November".

## Format (fixed — do not ask the owner)
| Item | Answer |
|---|---|
| Niche | Education — dental health (topics from `video_topics.md`) |
| Format | 9:16 vertical, 1080×1920, 30 fps |
| Length | **60–75 s**: **8–10 story scenes of 5–8 s** + the clinic end card (6 s, always last) |
| Cast | Teeth with faces (`tooth()`, rows with `gum_row()`), cut-away jaw (`bone_gum()`, `cut_neighbors()`), titanium implant hero (`implant()`, `abutment()`, `crown()`), bone buddies (`bone_buddy()`), cute germs (`germ()`), props (`toothbrush()`, `bubbles()`, `calendar()`, `heart()`, `sweat()`). Add new characters/props to tools/kawaii.py in the same style (thick #23395B ink outline, flat pastel fill with soft gradient, face via `face()`). |
| Idea | Generate it yourself from the next unused topic; do not ask |

## Pipeline (do in order)

1. **Setup.** Repo in session (add with push access if missing), cloned, `git pull`. Read this guide,
   `video_topics.md`, `videos_posted.md`, **all of tools/kawaii.py**, and the worked example
   `videos/ep3-dental-implant-hero/scenes.py` + `storyboard.md` + `narration.txt`.
2. **Double-post guard.** Metricool `getScheduledPosts` for today. If a Facebook REEL is already scheduled today at 19:00,
   stop and report. If it is already past 18:30, schedule for the next free 19:00 slot of a Reel day instead.
3. **Pick the topic.** Next unused topic in `video_topics.md`, rotating categories so the last two episodes differ. Never
   repeat one in `videos_posted.md`. Slug: `epN-<short-english-slug>` (N = last episode number + 1).
4. **Storyboard** → `videos/<slug>/storyboard.md`: title, the full narration, then a table per scene: time, narration
   line, what we see (characters, action, visual gag, sound effect), on-screen title and caption pills. Also the
   Facebook title, the caption (rules at the end) and keywords. Write `narration.txt` (one line per scene).
5. **Animate** → `videos/<slug>/scenes.py` (`from tools.kawaii import *`, one function per scene,
   `SCENES = [Scene(fn, seconds), ..., Scene(endcard('<short CTA for this topic>'), 6)]`).
   `python3 tools/kawaii_render.py videos/<slug> --preview` (a few seconds) and **open `videos/<slug>/contact.png`**
   (3 moments per scene). Fix anything wrong and re-preview: text clipped/overlapping, a character cut off or under a
   caption, an empty or cluttered scene, a face with the wrong emotion, something drawn outside y≈200–1800. Then
   `--silent` (~3–4 min, animation + music + effects) and pull a few frames with ffmpeg to check motion.
6. **Voice.** `creative_create_flow` once, then per scene `creative_generate_speech` (voice Nueng, eleven_v4,
   generations_count 1) — the end card gets a short CTA line too. One `creative_get_flow_run_status` with all
   session_ids; keep each `content_url` in scene order. If ElevenLabs refuses for lack of credits, do not stop: use
   `null` for every voice (the captions carry the story over music) and say so in the report.
7. **Build.** Write `videos/<slug>/job.json`: `{"output": "<slug>.mp4", "voices": [url1, ..., urlN]}` (one per scene,
   end card included). Commit storyboard, narration.txt, scenes.py, contact.png, job.json; push to main.
   GitHub Actions ("Build video") renders with `tools/kawaii_render.py`: it downloads the clips, trims silence, holds a
   scene longer when its narration needs it (+3 s max, then speeds the clip up to 1.2×), draws every frame, adds the
   music bed + sound effects with the music ducked under the voice, normalises to −14 LUFS and publishes `<slug>.mp4`
   to a Release tagged `<slug>`. Wait for it: poll `git ls-remote --tags https://github.com/uthinkpositive98/bangpain_dental_post`
   every 30 s for the tag (up to 25 min). Signed voice URLs expire after 2 hours, so push right after generating.
8. **Post.** Metricool `createScheduledPost`, date today 19:00 +07:00:
   `providers [{"network":"facebook"}]`, `facebookData {"type":"REEL", "title": "<video title>"}`, `autoPublish true`,
   `media [release mp4 URL]`, `videoCoverMilliseconds` = the most eye-catching moment (a hero/payoff frame with its
   title showing), `firstCommentText ""`, `text` = caption (rules below). The response media URL should be
   static.metricool.com.
9. **Log.** Append to `videos_posted.md`, commit, push. Report in two lines: episode title, scheduled time, planner link.
   On any failure, say exactly which step failed and what was done before it.

## Story and narration rules (as fun as ep3)
- Arc: **hook in the first 3 s** (something pops, breaks, a surprise question) → the problem escalates with a gag per
  beat → a hero/turning point → how it works or what to do, as numbered steps with `step_header()` → happy payoff with
  confetti and 3–4 benefit/tip pills → end card.
- Every scene moves: characters bob/blink, at least one key action with easing (`back`, `ease_out`), plus secondary
  motion (sparkles, bubbles, hearts, sweat drops, burst rays, comic words with `hand_text()` like ป๊อก! คลิก! ติ๊ง!).
  Big moments get a sound: `cue(t, t0, 'click' | 'thud' | 'boing' | 'chime' | 'ding' | 'sparkle' | 'fanfare' | 'sad' |
  'slide_down' | 'slide_up' | 'drill' | 'tick' | 'scrub')`; pop-in texts pop by themselves.
- Animations must settle on a final pose (scenes can be held longer for the narration).
- Narration: Thai, cheerful and conversational, simple words, polite ค่ะ/นะคะ, 1–3 short sentences per scene
  (≈ 4–7 s spoken). ElevenLabs v4 tags sparingly at the start of a line: `[excited]`, `[surprised]`, `[sad]`,
  `[playful]`, `[cheerful]`. On-screen text = short versions of the narration (title ≤ 4 words, pills ≤ 1 line).
- Accuracy: only well-established dental guidance; no invented statistics; "อาจ" for possibilities; no medicine names or
  doses; mention that the dentist examines first when a treatment is not for everyone.
- Advertising rules (สบส.): no prices, promotions, superlatives about the clinic, guarantees, before/after, testimonials,
  competitor comparisons. Nothing gory (no blood, wounds, needles, scary surgery).

## Layout
- Title at `TITLE_Y` (330), characters between y≈600 and y≈1450, caption pills from `SUB_Y` (1530) down to ≈1780; the
  Reels UI covers the bottom and the right edge. Thai text uses the Mitr fonts in tools/fonts (needs Pillow with raqm).

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

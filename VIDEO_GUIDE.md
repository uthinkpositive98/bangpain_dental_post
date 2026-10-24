# คู่มือคลิป Reel อัตโนมัติ — คลินิกทันตกรรมบางปะอิน

**Owner request 2026-10-24 — CURRENT HOUSE FORMAT (replaces the 5-minute landscape cartoon):** every new episode is a
**~1-minute vertical 3D cut-away Reel** like `videos/ep14-implant-3d/` ("รากฟันเทียม ทำงานยังไง?"), built with the
**cut3d** engine in `tools/cut3d/`. Read the section "3D cut-away Reels (cut3d)" right below and follow it; the older
sections further down (kawaii / landscape) are only for re-building old episodes. Caption rules, Metricool IDs, voice,
accuracy and advertising rules further down still apply.

## 3D cut-away Reels (cut3d) — house format from 2026-10-24

The style copies a viral 3D explainer the owner sent: one persistent 3D set (a jaw cut in half so you see gum, bone and
roots), a fast **"แต่… → งั้น…" (problem → fix) chain** where each fix creates the next problem, word-by-word captions,
no intro, a myth twist near the end and a payoff. Watch `videos/ep14-implant-3d/contact.jpg` (and its release MP4) first.

| Item | Answer |
|---|---|
| Format | 9:16 vertical 1080×1920, 30 fps, **55–65 s total**: cover 1.8 s + 9–11 story beats + end card ~6 s |
| Post | Metricool Facebook **REEL** (`facebookData {"type":"REEL","title":"<episode.json title>"}`), `videoCoverMilliseconds` **600** (the cover), 19:00 +07:00 |
| Cover | 3D hero shot + big title — `episode.json` "cover": `tag` (hook question), `title` (≤ 11 Thai chars at 200 px; set `titleSize` smaller if longer), `title2`, `sub`, `seconds` 1.8; `cover(t, L)` in scene3d.js poses the scene and returns ≤ 4 part labels |
| Badges | added automatically bottom-right for the whole clip: หมอนวรัตน์'s real photo (cut-out sticker, `tools/cut3d/dr_photo.png`, owner request 2026-10-25) above "ให้ความรู้โดย ทญ.นวรัตน์" + "คลินิกทันตกรรมบางปะอิน" — all in `tools/cut3d/badges.png` |
| End card | automatic (logo, phone/LINE, address, hours) + `episode.json` `endcta`; the last script line is spoken over it |
| Voice | Nueng `RIc0VzgLsI8EhceUkZx4`, `eleven_v4`, `generations_count` 1; `episode.json` `tempo` 1.12 (sped up, pitch kept) |

### Story formula (write `script.txt`)
- **One line per beat**; the **last line is the end-card line**. ~600–750 Thai characters in total (≈ 50 s spoken at 1.12×).
- Line 1 = hook: a wrong-but-simple idea as a question ("ฟันหลุด… แค่เอาฟันปลอมมาแปะ ก็จบแล้ว?").
- Then alternate **แต่… (what goes wrong)** / **งั้น… (the fix)**, 2–3 short phrases per line; each fix causes the next problem.
- Name the real term right after the fix: "…เรียกว่า ออสซีโออินทิเกรชั่น" → also shown as a chip.
- Use concrete, checked numbers (เดือน, ครั้ง, ปี) — only well-established facts (กรมอนามัย / ทันตแพทยสมาคม / WHO); "อาจ" for possibilities.
- Near the end, a myth twist: "หลายคนคิดว่า… ไม่ใช่นะ!" then the payoff "ยินดีด้วย! …". End-card line: if it is a treatment, say the dentist examines first, then "ปรึกษาคลินิกทันตกรรมบางปะอินได้เลยค่ะ".
- Split words with `|` (caption chunks, ~1–2 words) and phrases with spaces; an optional `[excited]`/`[playful]`/`[cheerful]` tag at the start of a line. No prices, promotions, superlatives, guarantees, before/after, testimonials, gore (no blood/needles/scary surgery).

### Files in `videos/<slug>/` (slug `epN-<english>-3d`)
`script.txt` · `episode.json` (title, tempo, cover, endcta, keys = yellow caption words, marks) · `scene3d.js` (the animation) ·
`cues.py` (sound effects) · `vo/01.mp3 … NN.mp3` (one per script line, committed) · `contact.jpg` (preview) · `job3d.json` (triggers the build, last).
Copy `videos/ep14-implant-3d/` as the starting point.

**marks** (`episode.json`): `[beat, "name", "first token of a caption chunk", occurrence]` → `L.mk(beat, "name", fallbackFraction)`
gives the time that chunk is spoken, so actions land on the words (e.g. the fix lands on "งั้น", the wobble on "รากเทียม").

### scene3d.js — the engine API (`L` = tools/cut3d/lib.js; read lib.js once, it is short)
- `export function frame(t, L)` — before each call the engine resets every prop (hidden, default pose; `centerTooth` visible, upper jaw open).
  Branch on beats with `L.bs(i)`, `L.be(i)`, `L.B[i].dur`, `L.mk(...)`; pose props; call `L.setCam(shotA, shotB, k, shake, t)`;
  return `{blur, flash}` (whip blur ~12–14 px for 0.35 s at a beat start, white flash on impacts). After the last beat keep the final state under the end card.
- `export function cover(t, L)` — pose for the cover; return labels `[{text, at:[x,y,z], dx?, dy?}]`. Optional `export function setup(L)` to build extra meshes once (`L.THREE`, `L.scene`, `L.onReset(fn)` to reset them each frame).
- Set: `bone`, `gum` (top at `GUM_TOP` 1.2), `neighbors` (teeth at x = ±3.75·i), `centerTooth` (x=0 natural tooth), `looseCrown`, `newCrown`,
  `upper` (y 11 open, ≈3.3 bite), `food`, `implant`, `abut`, `cells` (bone cells, from→to), `germs` + `germsArrive(t,t0)` / `germsClear(t,t0,t1)`,
  `brush`, `inflam`/`inflamF` (red gum patch, opacity), `glow`, `warn` (red ring), `halo`, `confetti(t,t0)`, `sparkleAt(x,y,z,k,R)`,
  materials `enamel`, `rootMat`, `titanium`, `gumMatTop`, geometry `CROWN`, `ROOT`, `tooth(x, withRoot, mat)`.
- Shots `L.SHOTS`: wide, high, gap, bite, bone, boneC, neck, crown, gumline, ortho (add your own as `[[eye],[target]]`).
- Overlays: `L.chip(id, text, cls, y, t, t0, t1, rot)` (cls '' | dark | red | green | yel; y ≈ 170–500 px, keep clear of the caption at 880–1010 px),
  `L.calendar(header, number, scale)`. Captions are automatic from script.txt.
- Easing: `seg, ease, eout, ein, back, lerp, clamp`. Build new props for other topics (cavity = dark patch on a crown, plaque = yellow film,
  filling = coloured cap, floss, X-ray, toothpaste blob…) from simple Three.js shapes in `setup()`; keep the same look (clean, soft, slightly glossy).
- Every beat must visibly change something; the set keeps what was built (continuity); return to the opening framing for the payoff.

### Pipeline (cut3d)
1. Double-post guard (Metricool `getScheduledPosts` today), pick the next unused topic (`video_topics.md`, rotate categories, never repeat `videos_posted.md`).
2. Write `script.txt`, `episode.json`, `scene3d.js`, `cues.py` (copy ep14 and rewrite).
3. **Voice (ElevenLabs is rate-limited — make as few requests as possible):** `creative_create_flow` once, then ONE
   `creative_generate_speech` whose prompt is ALL script lines separated by a blank line (tags kept, `|` removed). Poll
   `creative_get_flow_run_status`, download `content_url` with curl, then `python3 tools/cut3d/split_vo.py videos/<slug> take.mp3 1`
   and check every clip length ≈ expected. If a split looks wrong, regenerate only the bad lines (one request each) and save them as `vo/NN.mp3`.
   On `429 rate_limited` nothing was charged: wait 2–5 minutes (do other work) and retry the same call, up to 6 times.
4. Local tools: `cd tools/cut3d && npm install` (installs three.js; Playwright + Chromium are preinstalled in the session, and the CI workflow installs its own).
   `python3 tools/cut3d/build.py videos/<slug> --preview` (~2 min) → **open `videos/<slug>/contact.jpg`** and fix: anything off-screen or hidden,
   chips overlapping, empty beats, a prop that pops in without motion, text clipped on the cover. Re-preview until clean.
5. Commit everything (not `.work/`), push, then add `videos/<slug>/job3d.json` = `{"output": "<slug>.mp4"}` in its own commit and push.
   GitHub Actions "Build 3D video" renders (~25–45 min) and publishes `https://github.com/uthinkpositive98/bangpain_dental_post/releases/download/<slug>/<slug>.mp4`.
   Poll `git ls-remote --tags https://github.com/uthinkpositive98/bangpain_dental_post` every 60 s for the tag (up to 75 min). If the build fails, read the run's error annotations with `gh run view`, fix, push again.
6. Metricool `createScheduledPost` (blogId 7459912): `providers [{"network":"facebook"}]`, `facebookData {"type":"REEL","title":…}`, `autoPublish true`,
   `media [release mp4 URL]`, `videoCoverMilliseconds 600`, `firstCommentText ""`, text = caption (rules below), today 19:00 +07:00.
7. Log in `videos_posted.md` (note "3D 1 นาที"), commit, push. Report: title + length, scheduled time, planner link.


## Older formats (kawaii cartoon / landscape) — for old episodes only


One narrated **kawaii cartoon episode** per run, published on the clinic Facebook page as a **Facebook video at 19:00
Asia/Bangkok** on the posting days below. Each run does every step itself; nothing is left for the owner to do.

**Owner request 2026-10-22 (replaces the 60–75 s vertical Reel format): every new episode is a ~5-minute 16:9
landscape cartoon like ep11 "อาหารไทยแอบหวาน" — an opening cover card, the kawaii house style, หมอนวรัตน์ in her
bright aqua scrubs with a superhero cape in the knowledge scenes (`dr_nawarat()`), cheerful Thai narration, end card.**
See "Long landscape episodes" below; where it differs from the older Reel rules further down, it wins.
**Read `videos/_reference/ep11-thai-food-sugar.md` first** — the owner's model episode (story, scene-by-scene script, what to keep).

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
- Videos on **Tuesday, Thursday, Saturday and Sunday** at 19:00 (about 17 posts a month). The daily image posts were
  cancelled by the owner on 2026-10-21, so videos are the only scheduled posts.

## Long landscape episodes (former house format 2026-10-22 → 2026-10-24)
| Item | Answer |
|---|---|
| Format | 16:9 landscape, 1920×1080, 30 fps. Put a file `videos/<slug>/FORMAT` containing `landscape` (the renderer reads it). |
| Length | **about 5 minutes (4:30–5:30)**: `Scene(cover(...), 4)` first, then **22–28 story scenes of 8–14 s**, then the end card (6 s) |
| Arc | cover → hook in the first 10 s → the problem as a little story with characters (teeth, germs, food/props, people) → **"มุมความรู้กับหมอนวรัตน์"** chapters: `dr_nawarat()` explains with cut-away diagrams and numbered `step_header()` steps → a quick myth-or-fact round → summary of 3–5 tips with confetti → end card |
| Cover | `cover('<title ≤ 18 chars>', '<question/subtitle>', 'ตอนที่ N')` — pastel sunburst, big two-tone title, happy tooth + หมอนวรัตน์ (or `cast=` your own characters) |
| Dr. นวรัตน์ | `dr_nawarat(c, x, y, s, t, mood, wave=, point=, cape=1, hold='brush'|'mirror')`; origin = centre of her head, body reaches ~560·s below. Cape on in knowledge scenes; `cape=0` inside the clinic. |
| Layout | `TITLE_Y` 150, characters between y≈280 and y≈860, caption pills at `SUB_Y` 965, `GUM_TOP` 720, `ROW_X` centred; the helpers (`bone_gum`, `cut_neighbors`, `endcard`, iris transition, progress bar) adapt automatically. |
| Narration | Voice Nueng, one clip per scene (1–3 short sentences, ≤ 13 s), ~3,500–4,500 Thai characters in total (≈ 4–5k ElevenLabs credits). |
| Post | Metricool `facebookData {"type":"POST","title":"<title>"}` (a 5-minute landscape video is a normal video post, not a REEL), `videoCoverMilliseconds` 2000 (the cover card). |

- **No silent long videos.** If ElevenLabs refuses for lack of credits, do not post: commit what was made, and report
  "ElevenLabs out of credits — episode <slug> not posted" so the owner can top up.
- **ElevenLabs rate limit.** Start one generation at a time. A `429 rate_limited` error means nothing was generated or
  charged: wait 60 s and retry that same call (up to 3 times). Poll `creative_get_flow_run_status` with ≤ 8 sessions
  per call. If a voice is not available on the account's plan, use another Thai female library voice and say so.
- The GitHub Actions build of a 5-minute episode takes longer: wait for the release tag for up to **60 min**.

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

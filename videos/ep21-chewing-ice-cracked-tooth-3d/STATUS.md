# ep21 — status (2026-11-03 scheduled run)

Not posted yet: the voice take could not be downloaded.

- Script, episode.json, scene3d.js, cues.py are done; contact.jpg was previewed with **placeholder timing** (silent stand-in clips, not committed).
- ElevenLabs take generated (voice Mali 7XW5JhaNn90bnFojQ5DA — Nueng is not on the account; eleven_v4, 1 generation, 830 credits):
  flow `OOBZvVnuiKEJ9utp4rhC`, generation `5uRbqM56TBAV1l9OafAx`, 70.8 s. Prompt = take_prompt.txt.
- This session's network policy blocks `elevenlabsusercontent.com`, so the MP3 could not be fetched.

To finish: put the take at `videos/ep21-chewing-ice-cracked-tooth-3d/take.mp3` (download it from the ElevenLabs flow),
or allow `elevenlabsusercontent.com` for Claude's cloud sessions, then
`python3 tools/cut3d/split_vo.py videos/ep21-chewing-ice-cracked-tooth-3d take.mp3 1` → `build.py --preview` → push job3d.json → schedule.

## 2026-11-05 scheduled run
Still blocked: `elevenlabsusercontent.com` is not reachable from this session, so the take (and any new take) cannot be downloaded.
Nothing scheduled in Metricool for 2026-11-05. The signed take URL expires 2026-11-05 10:00 UTC; after that,
get a fresh link from the ElevenLabs flow (generation `5uRbqM56TBAV1l9OafAx`) — no new credits needed.
Fix: allow `elevenlabsusercontent.com` in claude.ai Settings > Capabilities (allowed domains), or commit take.mp3 here.

## 2026-11-07 scheduled run
Still blocked: `elevenlabsusercontent.com` is still refused by this session's network policy (403 at the proxy), so the
existing take cannot be downloaded and a new take would be stuck the same way — no new credits spent, nothing scheduled.
Metricool had nothing scheduled for 2026-11-07. Fresh signed link for the take (valid until 2026-11-07 10:00 UTC / 17:00 น.)
is available from the ElevenLabs flow `OOBZvVnuiKEJ9utp4rhC`, generation `5uRbqM56TBAV1l9OafAx`.
Fix (owner): allow `elevenlabsusercontent.com` in claude.ai Settings > Capabilities (allowed domains), or commit the take
as `videos/ep21-chewing-ice-cracked-tooth-3d/take.mp3` — the next run then finishes and schedules ep21.

## 2026-11-07 23:45 (owner allowed elevenlabsusercontent.com)
Take downloaded, split into vo/, real-timing preview OK; render triggered.

## Done
Rendered and scheduled in Metricool for 2026-11-08 19:00 (id 420103585).

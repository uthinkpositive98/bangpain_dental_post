# ep21 — status (2026-11-03 scheduled run)

Not posted yet: the voice take could not be downloaded.

- Script, episode.json, scene3d.js, cues.py are done; contact.jpg was previewed with **placeholder timing** (silent stand-in clips, not committed).
- ElevenLabs take generated (voice Mali 7XW5JhaNn90bnFojQ5DA — Nueng is not on the account; eleven_v4, 1 generation, 830 credits):
  flow `OOBZvVnuiKEJ9utp4rhC`, generation `5uRbqM56TBAV1l9OafAx`, 70.8 s. Prompt = take_prompt.txt.
- This session's network policy blocks `elevenlabsusercontent.com`, so the MP3 could not be fetched.

To finish: put the take at `videos/ep21-chewing-ice-cracked-tooth-3d/take.mp3` (download it from the ElevenLabs flow),
or allow `elevenlabsusercontent.com` for Claude's cloud sessions, then
`python3 tools/cut3d/split_vo.py videos/ep21-chewing-ice-cracked-tooth-3d take.mp3 1` → `build.py --preview` → push job3d.json → schedule.

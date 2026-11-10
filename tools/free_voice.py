"""เสียงพากย์สำรองฟรี (ใช้เมื่อเครดิต ElevenLabs หมด): VachanaTTS ผ่าน PyThaiTTS
   python tools/free_voice.py videos/<slug> [th_f_1|th_m_2|auto]
สร้าง vo/NN.mp3 ทีละบรรทัดของ script.txt (ไฟล์เดียวกับที่ split_vo.py ทำ) แล้ว timeline.py / build.py ใช้ต่อได้ทันที
เจ้าของกำหนด: ใช้สองเสียงนี้สลับกัน — Vachana th_f_1 (หญิง) และ th_m_2 (ชาย); 'auto' สลับจากครั้งก่อน (tools/free_voice_state.json)
เสียงชาย: เปลี่ยน ค่ะ/คะ ใน script.txt เป็น ครับ เพื่อให้คำบรรยายบนจอตรงกับเสียง"""
import json, os, re, subprocess, sys
EP = sys.argv[1].rstrip('/'); want = sys.argv[2] if len(sys.argv) > 2 else 'auto'
VOICES = ['th_f_1', 'th_m_2']; STATE = os.path.join(os.path.dirname(__file__), 'free_voice_state.json')
st = json.load(open(STATE)) if os.path.exists(STATE) else {'last': 'th_m_2'}
voice = want if want in VOICES else VOICES[(VOICES.index(st.get('last', 'th_m_2')) + 1) % 2]
sp = os.path.join(EP, 'script.txt'); raw = open(sp, encoding='utf-8').read()
if voice.startswith('th_m'):
    male = raw
    for a, b in [('นะคะ', 'นะครับ'), ('ค่ะ', 'ครับ'), ('คะ', 'ครับ')]: male = male.replace(a, b)
    if male != raw: open(sp, 'w', encoding='utf-8').write(male); raw = male; print('script.txt: ค่ะ/คะ -> ครับ (เสียงชาย)')
lines = [l for l in raw.splitlines() if l.strip()]
from pythaitts import TTS
tts = TTS(pretrained='vachana'); os.makedirs(os.path.join(EP, 'vo'), exist_ok=True)
for i, l in enumerate(lines, 1):
    text = re.sub(r'\[[a-z ]+\]\s*', '', l).replace('|', '').replace('...', ' ').replace('…', ' ').strip()
    wav = f'/tmp/fv_{i:02d}.wav'; tts.tts(text, speaker_idx=voice, filename=wav)
    out = os.path.join(EP, 'vo', f'{i:02d}.mp3')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=0.25',
                    '-ar', '44100', '-c:a', 'libmp3lame', '-q:a', '2', out], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    print(f'{i:02d} {d:5.2f}s  {text[:50]}')
json.dump({'last': voice}, open(STATE, 'w')); open(os.path.join(EP, 'VOICE.txt'), 'w').write(f'VachanaTTS {voice} (free fallback; ElevenLabs out of credits)\n')
print('VOICE', voice)

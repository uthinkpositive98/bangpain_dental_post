"""สร้างเสียงตัวอย่างจากโมเดลเสียงไทยฟรี/โอเพนซอร์ส: python make.py <engine> <outdir>"""
import asyncio, os, subprocess, sys, traceback
TEXT = "หลังถอนฟัน ยี่สิบสี่ชั่วโมงแรก ห้ามดูดหลอด ห้ามบ้วนแรง และงดบุหรี่นะคะ ถอนฟันแล้วสงสัย ปรึกษาคลินิกทันตกรรมบางปะอินได้เลยค่ะ"
eng, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
def mp3(wav, name):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ar", "44100", "-b:a", "128k", f"{out}/{name}.mp3"], check=True); print("OK", name)
if eng == "edge":
    import edge_tts
    async def go():
        for v in ["th-TH-PremwadeeNeural", "th-TH-AcharaNeural", "th-TH-NiwatNeural"]:
            await edge_tts.Communicate(TEXT, v).save(f"/tmp/{v}.mp3"); mp3(f"/tmp/{v}.mp3", f"edge-tts_{v}")
    asyncio.run(go())
elif eng == "gtts":
    from gtts import gTTS
    gTTS(TEXT, lang="th").save("/tmp/g.mp3"); mp3("/tmp/g.mp3", "gTTS_google-translate")
elif eng == "pythaitts":
    from pythaitts import TTS
    for pre, spk in [("vachana", "th_f_1"), ("vachana", "th_f_2"), ("vachana", "th_m_1"), ("vachana", "th_m_2"),
                     ("khanomtan", "Linda"), ("lunarlist_onnx", None), ("fastthaig2p", "thai_som")]:
        try:
            t = TTS(pretrained=pre); f = f"/tmp/{pre}_{spk}.wav"
            t.tts(TEXT, speaker_idx=spk, filename=f) if spk else t.tts(TEXT, filename=f)
            mp3(f, f"pythaitts_{pre}" + (f"_{spk}" if spk else ""))
        except Exception: traceback.print_exc()
elif eng == "f5th":
    # F5-TTS-THAI (CC-BY-4.0) โคลนเสียงจากคลิปอ้างอิง — ใช้เสียง VachanaTTS th_f_1 เป็นต้นแบบ
    from pythaitts import TTS as V
    ref_text = "สวัสดีค่ะ ยินดีต้อนรับสู่คลินิกทันตกรรมค่ะ"
    V(pretrained="vachana").tts(ref_text, speaker_idx="th_f_1", filename="/tmp/ref.wav")
    from f5_tts_th.tts import TTS
    import soundfile as sf
    wav = TTS(model="v1").infer(ref_audio="/tmp/ref.wav", ref_text=ref_text, gen_text=TEXT, step=32, cfg=2.0, speed=1.0)
    sf.write("/tmp/f5.wav", wav, 24000); mp3("/tmp/f5.wav", "F5-TTS-THAI_clone-of-vachana-f1")

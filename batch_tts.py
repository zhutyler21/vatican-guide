import os, sys, json, subprocess
from pathlib import Path

# 脱离父会话组，避免 Hermes 会话回收时被一起杀掉
try:
    os.setsid()
except OSError:
    pass

COSY_ROOT = Path('/Users/zhutyler21/.hermes/tools/CosyVoice')
os.chdir(COSY_ROOT)
sys.path.insert(0, str(COSY_ROOT))
sys.path.insert(0, str(COSY_ROOT / 'third_party/Matcha-TTS'))

PROJ = Path('/Users/zhutyler21/Downloads/Hermes/wangning/05-代码/20260630-vatican-guide-app')
AUDIO = PROJ / 'audio'
TMP = PROJ / '_tts_tmp'
AUDIO.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

REF_WAV = '/Users/zhutyler21/.hermes/skills/media/cosyvoice3-voice-cloning/assets/chenxuning-voice-example/reference_clean.wav'
REF_TXT = '小时候住在一座小城里，所以也没有机器的声音。春归何处？寂寞无行路。若有人知春去处，唤取归来同住。一天，我对父亲说：“我爱听这表的声音。燕子去了，还有再来的时候；杨柳枯了，还有再青的时候；桃花谢了，还有再开的时候。我们的日子为什么一去不复返呢？” A B C D E F G'
PROMPT_TEXT = 'You are a helpful assistant.<|endofprompt|>' + REF_TXT
FFMPEG = '/opt/homebrew/bin/ffmpeg'

works = json.loads((PROJ / 'scripts_manifest.json').read_text())

import torchaudio
from cosyvoice.cli.cosyvoice import AutoModel

print('loading model...', flush=True)
cosy = AutoModel(model_dir='/Users/zhutyler21/.hermes/local-model/Fun-CosyVoice3-0.5B',
                 load_trt=False, load_vllm=False, fp16=False)
print(f'model: {cosy.__class__.__name__}, sr={cosy.sample_rate}', flush=True)

done = 0
for w in works:
    wid, text = w['id'], w['text']
    final_mp3 = AUDIO / f'{wid}.mp3'
    if final_mp3.exists() and final_mp3.stat().st_size > 5000:
        print(f'skip {wid}', flush=True); done += 1; continue
    raw_wav = TMP / f'{wid}.wav'
    import torch
    parts = []
    for item in cosy.inference_zero_shot(text, PROMPT_TEXT, REF_WAV, stream=False, speed=1.0):
        parts.append(item['tts_speech'].cpu())
    audio = torch.cat(parts, dim=1)
    torchaudio.save(str(raw_wav), audio, cosy.sample_rate)
    subprocess.run([FFMPEG, '-y', '-i', str(raw_wav),
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                    '-ar', '44100', '-b:a', '128k', str(final_mp3)],
                   check=True, capture_output=True)
    print(f'OK {wid} -> {final_mp3.stat().st_size} bytes', flush=True)
    done += 1

print(f'DONE {done}/{len(works)}', flush=True)
Path('/tmp/vatican_tts.done').write_text(f'{done}/{len(works)}')

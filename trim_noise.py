import torchaudio, torch, glob, os, sys, subprocess
from pathlib import Path

PROJ = Path('/Users/zhutyler21/Downloads/Hermes/wangning/05-代码/20260630-vatican-guide-app')
TMP = PROJ / '_tts_tmp'
AUDIO = PROJ / 'audio'
FFMPEG = '/opt/homebrew/bin/ffmpeg'
DRY = '--apply' not in sys.argv

HOP_MS = 10
THR = 0.030
PAD_MS = 60
MAX_CUT_MS = 700
MIN_GAP_MS = 30

# borgia/pieta 噪音黏语音紧，自动检测保守跳过；用人工确认的更激进阈值兜底
FORCE = {'borgia_apartment': True, 'pieta': True}
# 手动切割值（自动检测找不到谷时用）：pieta噪音块0-80ms,谷90-120ms,语音130ms起
MANUAL_CUT = {'pieta': 80}

def detect_cut(wav, sr, force=False):
    mono = wav.mean(0) if wav.dim() > 1 else wav
    hop = int(sr * HOP_MS / 1000)
    n = min(int(sr * 1.2), len(mono))
    rms = []
    for i in range(0, n, hop):
        seg = mono[i:i+hop]
        rms.append((seg**2).mean().sqrt().item())
    thr = THR * (0.6 if force else 1.0)   # force 模式用更低阈值，更敏感地找谷
    min_gap = (10 if force else MIN_GAP_MS)
    voiced = [r > thr for r in rms]
    if not voiced or not voiced[0]:
        return 0, 'no_leading_noise'
    i = 0
    while i < len(voiced) and voiced[i]:
        i += 1
    noise_end = i
    while i < len(voiced) and not voiced[i]:
        i += 1
    gap_frames = i - noise_end
    speech_start = i
    if speech_start >= len(voiced):
        return 0, 'no_speech_after_gap'
    gap_ms = gap_frames * HOP_MS
    if gap_ms < min_gap:
        return 0, f'gap_too_short({gap_ms}ms)'
    cut_ms = max(0, speech_start * HOP_MS - PAD_MS)
    if cut_ms > MAX_CUT_MS:
        return 0, f'cut_too_large({cut_ms}ms)'
    return cut_ms, f'noise_end={noise_end*HOP_MS}ms gap={gap_ms}ms speech={speech_start*HOP_MS}ms'

print(f"{'文件':<28} {'裁(ms)':<8} 说明")
print('-'*78)
applied = 0
for wav_path in sorted(TMP.glob('*.wav')):
    name = wav_path.stem
    wav, sr = torchaudio.load(str(wav_path))
    cut_ms, info = detect_cut(wav, sr, force=FORCE.get(name, False))
    if cut_ms == 0 and name in MANUAL_CUT:
        cut_ms = MANUAL_CUT[name]
        info = f'manual_cut={cut_ms}ms'
    tag = '[force]' if FORCE.get(name) else ''
    print(f"{name:<28} {cut_ms:<8} {info} {tag}")
    if not DRY and cut_ms > 0:
        cut = int(sr * cut_ms / 1000)
        trimmed = wav[:, cut:]
        raw = TMP / f'{name}_trim.wav'
        torchaudio.save(str(raw), trimmed, sr)
        subprocess.run([FFMPEG, '-y', '-i', str(raw),
                        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                        '-ar', '44100', '-b:a', '128k', str(AUDIO / f'{name}.mp3')],
                       check=True, capture_output=True)
        raw.unlink()
        applied += 1

print('-'*78)
print(f"模式: {'DRY-RUN' if DRY else f'APPLY — 已重新生成 {applied} 段mp3'}")

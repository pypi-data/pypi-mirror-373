import numpy as np
from scipy.signal import correlate


def compute_audio_sync_offset(audio1, audio2, sr):
    audio1_norm = (audio1 - np.mean(audio1)) / (np.std(audio1) + 1e-9)
    audio2_norm = (audio2 - np.mean(audio2)) / (np.std(audio2) + 1e-9)

    corr = correlate(audio1_norm, audio2_norm, mode='full')
    lag = np.argmax(corr) - (len(audio2_norm) - 1)
    ms_offset = lag * 1000 / sr

    earlier = 'video1' if lag >= 0 else 'video2'
    print(f"Earlier video: {earlier}")
    print(f"Offset in milliseconds: {abs(ms_offset):.2f}")

    return lag, ms_offset

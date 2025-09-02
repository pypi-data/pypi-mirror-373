import os
import cv2
import numpy as np
import soundfile as sf
from pathlib import Path
from tqdm import tqdm


def extract_audio(video_path, audio_out_path, sr):
    print('[Extracting audio]: ', Path(audio_out_path).name)
    cmd = f'ffmpeg -hide_banner -loglevel error -y -i "{video_path}" -vn -acodec pcm_s16le -ar {sr} -ac 1 "{audio_out_path}"'
    os.system(cmd)


def load_audio(audio_path):
    data, sr = sf.read(audio_path)
    print(f'[Sampling rate]: {sr} ({Path(audio_path).name})')
    return data, sr


def get_video_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    print(f'[FPS]: {fps:.1f} ({Path(video_path).name})')
    return fps


def get_video_length_sec(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return n_frames / fps if fps > 0 else 0


def get_video_frame_size(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    print(f'[Resolution]: {w}x{h} ({Path(video_path).name})')
    return w, h


def pad_audio(audio, pad_start_frames, pad_end_frames, target_fps, sr):
    """Pad audio with zeros corresponding to black frame padding at start and end."""
    samples_per_frame = sr / target_fps
    pad_start_samples = int(round(pad_start_frames * samples_per_frame))
    pad_end_samples = int(round(pad_end_frames * samples_per_frame))
    padded_audio = np.pad(audio, (pad_start_samples, pad_end_samples), mode='constant')
    return padded_audio


def mux_audio_video(video_path, audio_path, out_path):
    """Mux video and audio into a single file."""
    print(f"[Muxing audio and video]: {Path(out_path).name}")
    cmd = (
        f'ffmpeg -hide_banner -loglevel error -y -i "{video_path}" -i "{audio_path}" '
        f'-c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 "{out_path}"'
    )
    os.system(cmd)


def save_synced_video(video_path, out_path, pad_start_frames, pad_end_frames, target_fps):
    w, h = get_video_frame_size(video_path)
    fps = get_video_fps(video_path)
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, target_fps, (w, h))

    black_frame = np.zeros((h, w, 3), dtype=np.uint8)

    # pad start with black frames
    for _ in tqdm(range(pad_start_frames), desc=f"[Output padding start frames]: {Path(out_path).name}"):
        out.write(black_frame)

    # write frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for _ in tqdm(range(total_frames), desc=f"[Output writing frames]: {Path(out_path).name}"):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()

    # pad end with black frames
    for _ in tqdm(range(pad_end_frames), desc=f"[Output padding end frames]: {Path(out_path).name}"):
        out.write(black_frame)
    out.release()

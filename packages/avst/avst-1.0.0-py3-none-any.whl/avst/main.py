import os
import argparse
import tempfile
from pathlib import Path
import cv2
import soundfile as sf
from avst.io import (
    extract_audio,
    load_audio,
    get_video_fps,
    get_video_length_sec,
    pad_audio,
    mux_audio_video,
    save_synced_video,
)
from avst.sync import compute_audio_sync_offset


def sync_videos(video1_path, video2_path, output1_path, output2_path, synced_session_path, target_fps=60, target_sr=48000):
    with tempfile.TemporaryDirectory() as tmpdir:
        audio1_path = Path(tmpdir) / 'audio1.wav'
        audio2_path = Path(tmpdir) / 'audio2.wav'

        # Extract audio from videos
        extract_audio(video1_path, audio1_path, target_sr)
        extract_audio(video2_path, audio2_path, target_sr)

        audio1, sr1 = load_audio(audio1_path)
        audio2, sr2 = load_audio(audio2_path)
        assert sr1 == sr2, "Sampling rates must match"
        sr = sr1

        lag, ms_offset = compute_audio_sync_offset(audio1, audio2, sr)

        pad_video1_start = 0
        pad_video2_start = 0

        if lag > 0:
            pad_video2_start = int(round((lag / sr) * target_fps))
        elif lag < 0:
            pad_video1_start = int(round((-lag / sr) * target_fps))

        cap1 = cv2.VideoCapture(video1_path)
        cap2 = cv2.VideoCapture(video2_path)
        n_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT)) + pad_video1_start
        n_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT)) + pad_video2_start
        max_frames = max(n_frames1, n_frames2)
        cap1.release()
        cap2.release()

        pad_video1_end = max_frames - n_frames1
        pad_video2_end = max_frames - n_frames2

        # Save videos with black frame padding (no audio)
        tmp_video1_path = Path(tmpdir) / 'tmp_video1.mp4'
        tmp_video2_path = Path(tmpdir) / 'tmp_video2.mp4'
        save_synced_video(video1_path, tmp_video1_path, pad_video1_start, pad_video1_end, target_fps)
        save_synced_video(video2_path, tmp_video2_path, pad_video2_start, pad_video2_end, target_fps)

        # Pad audios accordingly
        padded_audio1 = pad_audio(audio1, pad_video1_start, pad_video1_end, target_fps, sr)
        padded_audio2 = pad_audio(audio2, pad_video2_start, pad_video2_end, target_fps, sr)

        padded_audio1_path = Path(tmpdir) / 'padded_audio1.wav'
        padded_audio2_path = Path(tmpdir) / 'padded_audio2.wav'
        sf.write(padded_audio1_path, padded_audio1, sr)
        sf.write(padded_audio2_path, padded_audio2, sr)

        # Mux padded audio and video for each synced video
        mux_audio_video(tmp_video1_path, padded_audio1_path, output1_path)
        mux_audio_video(tmp_video2_path, padded_audio2_path, output2_path)

        # Create stacked session video with audio1 original (unpadded) audio for sync session video
        cmd_stack = (
            f'ffmpeg -hide_banner -loglevel error -y -i "{output1_path}" -i "{output2_path}" -i "{padded_audio2_path}" '
            f'-filter_complex "[0:v][1:v]vstack=inputs=2[v]" -map "[v]" -map 2:a '
            f'-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k "{synced_session_path}"'
        )
        print(f"[Stacking videos]: {Path(synced_session_path).name}")
        os.system(cmd_stack)

        print(f"[Synced video1] length: {get_video_length_sec(output1_path):.2f} seconds, {get_video_fps(output1_path):.1f} FPS")
        print(f"[Synced video2] length: {get_video_length_sec(output2_path):.2f} seconds, {get_video_fps(output2_path):.1f} FPS")
        print(f"[Synced session] length: {get_video_length_sec(synced_session_path):.2f} seconds, {get_video_fps(synced_session_path):.1f} FPS")


def main():
    parser = argparse.ArgumentParser(description='Sync two videos based on audio.')
    parser.add_argument('--video1', type=str, required=True, help='Path to the first video file')
    parser.add_argument('--video2', type=str, required=True, help='Path to the second video file')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS for the videos')
    parser.add_argument('--sr', type=int, default=48000, help='Target sampling rate for the audio')
    args = parser.parse_args()

    for video_file in [args.video1, args.video2]:
        if not Path(video_file).exists():
            raise FileNotFoundError(f"Video file {video_file} does not exist")

    sync_videos(args.video1, args.video2, "synced_video1.mp4", "synced_video2.mp4", "synced_session.mp4", args.fps, args.sr)


if __name__ == "__main__":
    main()

# AVST
Audio Video Sync Tool

## Description
AVST is a tool that syncs two videos based on their audio.

Steps:
1. Extract audio from both videos
2. Sync the audio of both videos, using cross correlation
3. Pad the audios and videos to the same length considering the delay
4. Save the corresponding synced audios and videos, then mux them into a single video
5. Save the synced videos stacked vertically for easier visualization

## Dependencies
- Python >=3.11
- ffmpeg

Additional python packages are listed in the requirements.txt file.

## Install
```bash
pip install avst
```

## Install for dev

```bash
conda create -n avst python=3.11
conda activate avst
git clone https://github.com/fodorad/AVST
cd AVST
pip install -e .
```

## Usage
```bash
avst --video1 path/to/video1.mp4 --video2 path/to/video2.mp4
```

## Expected outputs
| Video Name        | Description                                                    |
|-------------------|----------------------------------------------------------------|
| synced_video1.mp4 | Video 1 synced to Video 2                                      |
| synced_video2.mp4 | Video 2 synced to Video 1                                      |
| synced_session.mp4| synced_video1.mp4 and synced_video2.mp4 stacked vertically for easier visualization |


# Contact

* Ádám Fodor (fodorad201@gmail.com) [[website](https://adamfodor.com)]
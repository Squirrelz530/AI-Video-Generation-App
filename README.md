# AI Video Generator

Turn a written idea into a captioned MP4 video. The app uses Hugging Face to
make AI images for each scene, adds a gentle zoom effect and captions, and can
optionally generate narration and mix in your music.

## What you need

1. **Python 3.10 or newer.** On Windows, install it from
   [python.org](https://www.python.org/downloads/) and check **Add Python to PATH**.
2. A free [Hugging Face account](https://huggingface.co/join).
3. A Hugging Face **access token** with permission to use Inference Providers.
   Create one at <https://huggingface.co/settings/tokens>. Keep it private;
   never post it in GitHub or send it to anyone.
4. **FFmpeg** only if you want narration or background music. Install it and
   make sure `ffmpeg` works in Command Prompt. The app can still make a silent
   video without it.

## Run it on Windows

1. Download or clone this repository.
2. Double-click **`run_app.bat`**.
3. Wait while it sets up the needed Python packages.
4. Enter what you want in the video, for example: `A peaceful moonlit forest
   with fireflies`.
5. Paste your Hugging Face access token. It is not saved by the app.
6. Choose the number of scenes, their length, and video size.
7. Optionally select a music file and leave narration enabled.
8. Click **Generate Video**.

Your finished video will be at **`output/ai_video.mp4`**. The generated scene
images and temporary silent video are also in `output/`.

## How it works

`app.py` is the desktop application. It sends your description to the hosted
Hugging Face image model for each scene, renders those images into an MP4 with
captions, asks a hosted text-to-speech model for narration, then asks FFmpeg
to mix the audio. Your token is sent directly to Hugging Face for that request
and is not written to a file.

## Existing simple converter

`auto_convert.py` remains available if you only want to convert an image in
this folder into a 10-second, still video.

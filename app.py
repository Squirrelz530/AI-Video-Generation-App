#!/usr/bin/env python3
"""A small desktop app that turns a written idea into a captioned video."""

import json
import os
import shutil
import subprocess
import threading
import tkinter as tk
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "output"
IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
TTS_MODEL = "facebook/mms-tts-eng"


def hf_request(model, token, payload):
    """Call Hugging Face's hosted inference endpoint and return raw bytes."""
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read(), response.headers.get_content_type()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Hugging Face returned {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach Hugging Face: {error.reason}") from error


def scene_prompts(prompt, count):
    """Create simple visual beats from the user's idea without another AI call."""
    beats = ["an establishing shot", "a closer, detailed moment", "a dramatic final shot"]
    return [f"{prompt}. {beats[index % len(beats)]}. Cinematic, high quality." for index in range(count)]


def generate_image(prompt, token, destination):
    data, content_type = hf_request(IMAGE_MODEL, token, {"inputs": prompt})
    if not content_type.startswith("image/"):
        raise RuntimeError(f"The image model did not return an image: {data.decode('utf-8', errors='replace')}")
    destination.write_bytes(data)


def generate_narration(text, token, destination):
    data, content_type = hf_request(TTS_MODEL, token, {"inputs": text})
    if not content_type.startswith("audio/"):
        raise RuntimeError(f"The narration model did not return audio: {data.decode('utf-8', errors='replace')}")
    destination.write_bytes(data)


def captioned_frame(image, caption, width, height, progress):
    """Make a gently zooming video frame with a readable bottom caption."""
    source = image.convert("RGB")
    scale = 1.0 + (0.08 * progress)
    crop_width, crop_height = int(source.width / scale), int(source.height / scale)
    left = (source.width - crop_width) // 2
    top = (source.height - crop_height) // 2
    frame = source.crop((left, top, left + crop_width, top + crop_height)).resize(
        (width, height), Image.Resampling.LANCZOS
    )
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()
    caption = "\n".join(textwrap.wrap(caption.strip(), width=58))
    draw.rectangle((0, height - 82, width, height), fill=(0, 0, 0, 150))
    draw.multiline_text(
        (width // 2, height - 41), caption, font=font, fill="white", anchor="mm",
        align="center", spacing=4,
    )
    return cv2.cvtColor(np.array(Image.alpha_composite(frame.convert("RGBA"), overlay)), cv2.COLOR_RGBA2BGR)


def write_video(images, caption, output, width, height, seconds, status):
    fps = 24
    frames_per_scene = fps * seconds
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("Could not create the MP4 file.")
    try:
        for scene_number, image_path in enumerate(images, start=1):
            status(f"Rendering scene {scene_number} of {len(images)}...")
            with Image.open(image_path) as image:
                for frame_number in range(frames_per_scene):
                    writer.write(captioned_frame(image, caption, width, height, frame_number / frames_per_scene))
    finally:
        writer.release()


def add_audio(video, music, narration, output):
    """Mix optional music and narration with ffmpeg, when it is installed."""
    ffmpeg = shutil.which("ffmpeg")
    sources = [item for item in (music, narration) if item]
    if not sources:
        shutil.copy2(video, output)
        return output
    if not ffmpeg:
        raise RuntimeError("Audio was requested, but FFmpeg is not installed. Install FFmpeg or uncheck audio options.")
    command = [ffmpeg, "-y", "-i", str(video)]
    for source in sources:
        command.extend(["-stream_loop", "-1", "-i", str(source)])
    if len(sources) == 1:
        filter_graph = "[1:a]volume=0.7[aout]"
    else:
        filter_graph = "[1:a]volume=0.25[music];[2:a]volume=1.0[voice];[music][voice]amix=inputs=2:duration=longest[aout]"
    command.extend([
        "-filter_complex", filter_graph, "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-shortest", str(output),
    ])
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"FFmpeg could not add audio: {result.stderr[-500:]}")
    return output


class VideoGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Video Generator")
        self.resizable(False, False)
        self.prompt = tk.StringVar()
        self.token = tk.StringVar(value=os.environ.get("HF_TOKEN", ""))
        self.scene_count = tk.IntVar(value=3)
        self.seconds = tk.IntVar(value=4)
        self.size = tk.StringVar(value="1280x720")
        self.music = tk.StringVar()
        self.narration = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Ready. Describe the video you want to make.")
        self._build()

    def _build(self):
        box = ttk.Frame(self, padding=18)
        box.grid()
        ttk.Label(box, text="AI Video Generator", font=("", 18, "bold")).grid(columnspan=3, sticky="w")
        ttk.Label(box, text="Describe your video").grid(row=1, sticky="w", pady=(14, 2))
        ttk.Entry(box, textvariable=self.prompt, width=64).grid(row=2, columnspan=3, sticky="ew")
        ttk.Label(box, text="Hugging Face access token").grid(row=3, sticky="w", pady=(10, 2))
        ttk.Entry(box, textvariable=self.token, show="*", width=64).grid(row=4, columnspan=3, sticky="ew")
        ttk.Label(box, text="Your token is used only for this run and is never saved.").grid(
            row=5, columnspan=3, sticky="w"
        )
        ttk.Label(box, text="Scenes").grid(row=6, sticky="w", pady=(12, 2))
        ttk.Spinbox(box, from_=1, to=6, textvariable=self.scene_count, width=8).grid(row=7, sticky="w")
        ttk.Label(box, text="Seconds per scene").grid(row=6, column=1, sticky="w", pady=(12, 2))
        ttk.Spinbox(box, from_=2, to=12, textvariable=self.seconds, width=14).grid(row=7, column=1, sticky="w")
        ttk.Label(box, text="Video size").grid(row=6, column=2, sticky="w", pady=(12, 2))
        ttk.Combobox(box, values=("1280x720", "720x1280", "1920x1080"), textvariable=self.size, width=14,
                     state="readonly").grid(row=7, column=2, sticky="w")
        ttk.Checkbutton(box, text="Create AI narration", variable=self.narration).grid(
            row=8, columnspan=3, sticky="w", pady=(12, 0)
        )
        ttk.Button(box, text="Choose optional background music", command=self.choose_music).grid(
            row=9, sticky="w", pady=(8, 0)
        )
        ttk.Label(box, textvariable=self.music, width=48).grid(row=9, column=1, columnspan=2, sticky="w")
        self.generate_button = ttk.Button(box, text="Generate Video", command=self.start_generation)
        self.generate_button.grid(row=10, columnspan=3, pady=(16, 6))
        ttk.Label(box, textvariable=self.status, wraplength=500).grid(row=11, columnspan=3, sticky="w")

    def choose_music(self):
        chosen = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.m4a"), ("All files", "*.*")])
        if chosen:
            self.music.set(chosen)

    def set_status(self, message):
        self.after(0, self.status.set, message)

    def start_generation(self):
        if not self.prompt.get().strip() or not self.token.get().strip():
            messagebox.showerror("Missing information", "Enter both a video description and a Hugging Face access token.")
            return
        self.generate_button.configure(state="disabled")
        threading.Thread(target=self.generate, daemon=True).start()

    def generate(self):
        try:
            OUTPUTS.mkdir(exist_ok=True)
            prompt = self.prompt.get().strip()
            width, height = map(int, self.size.get().split("x"))
            scene_dir = OUTPUTS / "scenes"
            scene_dir.mkdir(exist_ok=True)
            image_paths = []
            for number, scene_prompt in enumerate(scene_prompts(prompt, self.scene_count.get()), start=1):
                self.set_status(f"Creating AI image {number} of {self.scene_count.get()}...")
                image_path = scene_dir / f"scene_{number}.png"
                generate_image(scene_prompt, self.token.get().strip(), image_path)
                image_paths.append(image_path)
            silent_video = OUTPUTS / "video_silent.mp4"
            write_video(image_paths, prompt, silent_video, width, height, self.seconds.get(), self.set_status)
            narration_path = None
            if self.narration.get():
                self.set_status("Creating AI narration...")
                narration_path = OUTPUTS / "narration.wav"
                generate_narration(prompt, self.token.get().strip(), narration_path)
            self.set_status("Adding audio...")
            final_video = add_audio(silent_video, self.music.get() or None, narration_path, OUTPUTS / "ai_video.mp4")
            self.set_status(f"Finished! Your video is: {final_video}")
            self.after(0, messagebox.showinfo, "Finished", f"Your video is ready:\n{final_video}")
        except Exception as error:
            self.set_status(f"Error: {error}")
            self.after(0, messagebox.showerror, "Could not generate video", str(error))
        finally:
            self.after(0, self.generate_button.configure, {"state": "normal"})


if __name__ == "__main__":
    VideoGeneratorApp().mainloop()

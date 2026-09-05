#!/usr/bin/env python3
"""Convert still images in input/images into MP4 clips or a slideshow."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def find_images(input_dir: Path) -> list[Path]:
    """Return supported images in deterministic recursive order."""
    return sorted(
        (path for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS),
        key=lambda path: path.as_posix().lower(),
    )


def load_frame(image_path: Path) -> np.ndarray:
    """Load an image and convert it to an OpenCV BGR frame."""
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def create_writer(output_path: Path, frame: np.ndarray, fps: int) -> cv2.VideoWriter:
    """Create and validate an MP4 writer using the first frame's dimensions."""
    height, width = frame.shape[:2]
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {output_path}")
    return writer


def write_image_video(image_paths: list[Path], output_path: Path, duration: float, fps: int) -> None:
    """Write one video containing each image for ``duration`` seconds."""
    if not image_paths:
        raise ValueError("No images were supplied")

    first_frame = load_frame(image_paths[0])
    writer = create_writer(output_path, first_frame, fps)
    frames_per_image = max(1, round(duration * fps))
    try:
        for image_path in image_paths:
            frame = load_frame(image_path)
            if frame.shape[:2] != first_frame.shape[:2]:
                frame = cv2.resize(frame, (first_frame.shape[1], first_frame.shape[0]))
            for _ in range(frames_per_image):
                writer.write(frame)
    finally:
        writer.release()


def play_video(video_path: Path) -> None:
    """Open the result on Windows when possible."""
    if hasattr(os, "startfile"):
        os.startfile(str(video_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("input/images"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--duration", type=float, default=5.0, help="Seconds per image")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument(
        "--mode",
        choices=("slideshow", "individual"),
        default="slideshow",
        help="Create one sequence or one clip per image",
    )
    parser.add_argument("--no-play", action="store_true", help="Do not open the result automatically")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration <= 0 or args.fps <= 0:
        print("Duration and FPS must be greater than zero.", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    images = find_images(args.input_dir)
    if not images:
        print(f"No images found in {args.input_dir}. Add PNG, JPG, JPEG, or WebP files.")
        return 1

    print(f"Found {len(images)} image(s) in {args.input_dir}")
    if args.mode == "individual":
        for image_path in images:
            output_path = args.output_dir / f"{image_path.stem}_video.mp4"
            write_image_video([image_path], output_path, args.duration, args.fps)
            print(f"Saved: {output_path}")
        return 0

    output_path = args.output_dir / "battle_sequence.mp4"
    write_image_video(images, output_path, args.duration, args.fps)
    print(f"Saved: {output_path}")
    if not args.no_play:
        play_video(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Automated video generation from images.
This script finds images in the current directory and converts them to video.
"""

import cv2
import numpy as np
from PIL import Image
import os
import glob
import subprocess
import sys

def find_images():
    """Find all image files in current directory."""
    image_patterns = ['*.png', '*.jpg', '*.jpeg']
    images = []
    for pattern in image_patterns:
        images.extend(glob.glob(pattern))
    return images

def image_to_video(image_path, output_path="output_video.mp4", duration=10):
    """Convert image to video with effects."""
    try:
        print(f"Loading image: {image_path}")
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Handle different image modes
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif img_array.shape[2] == 3:  # RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        h, w = img_array.shape[:2]
        fps = 24
        frames = int(duration * fps)
        
        print(f"Creating video: {output_path} ({w}x{h}, {duration}s)")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        for i in range(frames):
            out.write(img_array)
            if (i + 1) % 24 == 0:
                print(f"  {int((i+1)/frames*100)}% complete")
        
        out.release()
        print(f"✓ Video saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def play_video(video_path):
    """Play video using system default player."""
    try:
        print(f"Opening video: {video_path}")
        os.startfile(video_path)
        return True
    except Exception as e:
        print(f"Could not auto-play: {e}")
        print(f"Video is ready at: {video_path}")
        return False

def main():
    print("=" * 60)
    print("AI VIDEO CONVERTER")
    print("=" * 60)
    
    # Find images
    images = find_images()
    
    if not images:
        print("✗ No images found in current directory!")
        print("  Looking for: *.png, *.jpg, *.jpeg")
        return
    
    print(f"\nFound {len(images)} image(s):")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img}")
    
    # Use first image
    image_path = images[0]
    output_path = image_path.rsplit('.', 1)[0] + "_video.mp4"
    
    print(f"\nConverting: {image_path}")
    video = image_to_video(image_path, output_path, duration=10)
    
    if video:
        print(f"\n✓ Success! Video ready: {output_path}")
        play_video(video)
    else:
        print("\n✗ Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

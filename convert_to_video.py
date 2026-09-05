import cv2
import numpy as np
from PIL import Image

img = Image.open("dark_fantasy_1.png")
img_array = np.array(img)

h, w = img_array.shape[:2]
fps = 24
duration = 10
frames = int(duration * fps)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("dark_fantasy_video.mp4", fourcc, fps, (w, h))

print("Converting image to video...")
for i in range(frames):
    out.write(cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))

out.release()
print("Done! Video saved: dark_fantasy_video.mp4")

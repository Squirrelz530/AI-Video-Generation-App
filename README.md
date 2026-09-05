# AI Video Generation App

This project currently provides a reliable image-to-video foundation for
realistic, cinematic, anime, fantasy, and sci-fi storyboards. It supports
single images, ordered image sequences, and individual clips. Text-to-video
generation is not implemented yet; prompts can be used to plan scenes, but a
generative model and its runtime still need to be added.

## Quick start (Windows)

1. Install Python 3.10 or newer.
2. Run `run_converter.bat` to create `.venv`, install dependencies, and create
   the input and output folders.
3. Put PNG, JPG, JPEG, or WebP scene images in `input/images/`.
4. Run `AI Video Generator.bat` to prepare the environment and start conversion.
5. Find the default sequence at `output/battle_sequence.mp4`.

Images are read recursively and sorted by filename. Name them with a numeric
prefix (`001-opening.png`, `002-charge.png`, `003-clash.png`) to control the
scene order. Images with different dimensions are resized to match the first
image.

## Commands

The default command creates one slideshow-style sequence and holds each image
for five seconds:

```text
python auto_convert.py
```

Create one five-second video per image:

```text
python auto_convert.py --mode individual
```

Useful options:

```text
python auto_convert.py --input-dir input/images --output-dir output --duration 8 --fps 24 --no-play
```

## Workflow

`AI Video Generator.bat` -> `run_converter.bat` (environment setup) ->
`convert.bat` (conversion) -> `input/images/` -> sorted scene images -> OpenCV
MP4 writer -> `output/`.

The converter does not yet animate pixels, generate images from prompts, or
create new battle footage. Those capabilities require integrating a selected
text-to-image or text-to-video model, its model weights, and hardware/runtime
requirements. The current pipeline is safe to use with any visual style as
long as the source images already represent that style.

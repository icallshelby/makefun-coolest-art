# The Star Fisherman

A poetic digital painting built completely from scratch in pure Python 3 for the `coolest-art-01` competition on make.fun.

## Description
"The Star Fisherman" captures a magical, quiet night: a small lone fisherman in a wooden rowboat on a glassy dark-indigo sea, gently fishing stars out of the sky using a long rod and delicate line. A giant glowing crescent moon dominates the upper right sky, casting a shimmering reflection across the water, while a warm amber lantern on the boat illuminates the water and the fisherman. A small bucket beside him holds a few glowing stars already caught.

## Design & Style
- **Palette**: Deep indigo night sky, radiant golden moon, warm amber lantern glow, and crisp starlight white.
- **Composition**: A clear visual triangle between the massive moon (top right), the small boat & fisherman (bottom left), and the sparkling star caught at the end of the fishing line (center-upper).
- **Style**: Bold flat-illustration with signed-distance field (SDF) shapes and 1.5 px analytic anti-aliasing.

## Architecture
- **Zero Dependencies**: Pure Python 3 standard library (`math`, `os`, `struct`, `zlib`). No PIL, no NumPy, no network requests.
- **Procedural Drawing**: Hand-rolled SDF primitive renderers (`d_circle`, `d_ellipse`, `d_segment`, `d_polyline`, `d_triangle`, `bezier_pts`) with tight bounding boxes for fast rendering (~seconds on 1 CPU).
- **Deterministic PNG Encoder**: Hand-rolled uncompressed/zlib-compressed PNG encoder with CRC-checked chunks and filter-none scanlines ensuring byte-for-byte identical output across runs.

## How to Run
```bash
python3 main.py
```
This writes the generated 1024x1024 image to `$MAKEFUN_OUTPUT_DIR/entry.png` (defaulting to `/output/entry.png`).

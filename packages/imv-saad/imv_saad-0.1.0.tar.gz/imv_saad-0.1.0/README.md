# imv-saad

A Tkinter desktop app to view **images, masks, predicted masks** with overlays and IoU scoring.

## Features
- Supports opening image, mask, and predicted mask folders.
- Displays:
  - Image
  - Ground-truth mask
  - Predicted mask
  - Overlay views
  - Info panel with metadata, unique values, IoU score
- Zoom (mouse wheel) & pan (drag) synchronized across all panels.
- Saves last opened folders in `dirs.py` for automatic reloading.

## Installation
```bash
pip install imv-saad

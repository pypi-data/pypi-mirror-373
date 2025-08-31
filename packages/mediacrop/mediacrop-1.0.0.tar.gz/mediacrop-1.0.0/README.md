# ✂️ MediaCrop - Visual FFmpeg Crop Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mediacrop.svg)](https://badge.fury.io/py/mediacrop)

MediaCrop is a lightweight, web-based visual tool that helps you easily get FFmpeg crop coordinates for any media file (video, image, audio). No more guesswork – just drag and resize to select the perfect crop area!

The tool runs a local server on your machine and opens an interface in your browser, providing an intuitive and user-friendly experience.

![MediaCrop Interface Screenshot](https://raw.githubusercontent.com/mallikmusaddiq1/MediaCrop/main/assets/screenshot.png)

---

## ✨ Features

* **🌐 Web-Based Interface:** Runs in your default browser, no separate GUI installation needed.
* **🖱️ Interactive Crop Box:** Easily drag, resize, and adjust the crop area with your mouse.
* **📐 Aspect Ratios:** Set presets like freeform, 16:9, 4:3, 1:1 (Square), or define a custom aspect ratio.
* **⌨️ Keyboard Shortcuts:** Use arrow keys for pixel-perfect adjustments and other handy shortcuts.
* **📊 Live Info Panel:** See the crop box's position (X, Y), size (width, height), and aspect ratio in real-time.
* **🚀 Zero Dependencies:** Uses only the Python standard library.
* **💻 Cross-Platform:** Works on Windows, macOS, and Linux.
* **✅ Universal Support:** Previews many common video, image, and audio formats. You can still set coordinates even if a preview is not supported.

## ⚙️ Installation

You only need Python 3.7+ installed.

### Option 1: From PyPI (Recommended)

```bash
pip install mediacrop
```

### Option 2: From Source

If you want to use the latest development version:

```bash
# Clone the repository
git clone https://github.com/mallikmusaddiq1/MediaCrop.git

# Navigate into the directory
cd MediaCrop

# Install locally
pip install .
```

---

## 🚀 Usage

Using the tool is very straightforward.

1. Run the following command in your terminal:

   ```bash
   mediacrop "/path/to/your/mediafile.mp4"
   ```

   Using quotes ("") around the file path is a good practice, especially if the file name contains spaces.

2. Your default web browser will automatically open to [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. Adjust the crop box visually in the browser.

4. When you're ready, click the **"Save Coordinates"** button.

5. The crop filter string `(crop=w:h:x:y)` will be printed to your terminal.

6. Press **Ctrl+C** in the terminal to stop the server.

### Command-line Options

* `-p <port>`, `--port <port>`: Use a specific port number (default: 8000).
* `-v`, `--verbose`: Show detailed server logs in the terminal.
* `-h`, `--help`: Display the help message.

---

## 🎬 Using the Output with FFmpeg

`mediacrop` will give you an FFmpeg-ready filter string.

**Example Output (in your terminal):**

```
crop=1280:720:320:180
```

Now, use this string with the `-vf` (video filter) flag in your ffmpeg command:

```bash
ffmpeg -i input.mp4 -vf "crop=1280:720:320:180" output.mp4
```

This command will crop `input.mp4` to the specified coordinates and save it as `output.mp4`.

---

## ⌨️ Keyboard Shortcuts

* **Arrow Keys:** Move the crop box by 10px.
* **Shift + Arrow Keys:** Move the crop box by 1px (for fine adjustments).
* **G:** Toggle the grid overlay.
* **C:** Center the crop box.
* **Enter:** Save the coordinates.
* **? / Esc:** Open/Close the help modal.

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more details.

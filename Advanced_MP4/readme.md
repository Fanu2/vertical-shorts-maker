# 🎬 Advanced MP4 Shorts Editor GUI

> A powerful, beginner‑friendly **Python GUI tool** to turn any MP4 into a **YouTube Shorts–ready video** with **audio replacement, fades, caption bars, vertical crop, and preset trims**.

Perfect for:

* YouTube Shorts
* Instagram Reels
* TikTok
* Motivational videos
* Podcast clips
* Music edits

---

## ✨ Key Features

✅ **MP4 Input** – Load any video file
✅ **🎯 Preset Trims** – 15s / 30s / 60s / Custom
✅ **🔊 Audio Replacement** – Strip original audio & add your own MP3
✅ **🔁 Loop Video to Match MP3** (optional)
✅ **🔊 Audio Fade In & Fade Out**
✅ **📍 Top & Bottom Caption Bars** (classic viral style)
✅ **🎥 Vertical Shorts Crop (9:16 toggle)**
✅ **Thread‑Safe GUI** – No freezing or crashes
✅ **MoviePy 2.x Compatible**
✅ **Linux / macOS / Windows**

---

## 🧠 How It Works

1. Select an **MP4 video**
2. Choose a **trim preset** (15s / 30s / 60s) or **custom time range**
3. Add **Top & Bottom caption text**
4. (Optional) Add an **MP3 soundtrack**
5. Enable:

   * Vertical crop (9:16)
   * Audio fade in/out
   * Video looping to match MP3
6. Click **Process & Export**
7. Get a **Shorts‑ready MP4** instantly ✅

---

## 🖥️ User Interface Overview

* **Select MP4 Video** – Load your source video
* **Select MP3 (optional)** – Background music
* **Trim Presets** – 15 / 30 / 60 seconds
* **Custom Trim Slots** – Start & End time in seconds
* **Top Caption Text** – Headline / Hook
* **Bottom Caption Text** – CTA / Branding
* **Checkbox Options**:

  * Strip original audio
  * Audio fade in/out
  * Loop video to MP3
  * Vertical Shorts crop (9:16)

---

## 📦 Requirements

* **Python 3.10+**
* **ffmpeg** installed on your system

### Install Dependencies (Recommended in a venv)

```bash
pip install "numpy<2" moviepy opencv-python pillow imageio imageio-ffmpeg
```

---

## 🚀 How To Run

Save the script as:

```text
advanced_mp4_shorts_editor_gui.py
```

Then run:

```bash
python3 advanced_mp4_shorts_editor_gui.py
```

---

## 🎥 Output Specs

* **Format:** MP4 (H.264 + AAC)
* **Orientation:**

  * Horizontal (default)
  * Vertical 9:16 (if enabled)
* **Durations:** 15s / 30s / 60s / Custom
* **Audio:**

  * Original stripped (optional)
  * MP3 added with fade in/out

---

## 🎨 Caption Bar Style

* Solid black cinematic bars
* White bold text
* Optimized for Shorts safe zones
* Fully customizable in the GUI

---

## 🔊 Audio Processing Logic

| Scenario               | Behavior                        |
| ---------------------- | ------------------------------- |
| No MP3 selected        | Original audio can be stripped  |
| MP3 longer than video  | Trim MP3                        |
| MP3 shorter than video | Loop MP3                        |
| Loop Video Enabled     | Video repeats to match full MP3 |
| Fade Enabled           | Smooth 1s fade-in & fade-out    |

---

## ⚡ Stability & Performance

✔ Frame‑by‑frame processing (low RAM usage)
✔ Thread‑safe Tkinter updates
✔ No GPU required
✔ Works on budget systems
✔ Tested on Python 3.11 + MoviePy 2.x

---

## 🗂 Suggested Project Structure

```text
advanced-mp4-shorts-editor/
├── advanced_mp4_shorts_editor_gui.py
├── README.md
├── requirements.txt
├── LICENSE
└── examples/
    ├── demo.gif
    ├── before.mp4
    └── after.mp4
```

---

## 🎥 Demo (Add Your Own)

Place a demo file here:

```text
examples/demo.gif
or
examples/demo.mp4
```

And embed it in this README like this:

```md
![Demo](examples/demo.gif)
```

---

## 🔒 Legal Notice

You are responsible for:

* Music licensing
* Copyright compliance
* Platform publishing rules (YouTube, Instagram, TikTok)

This software is provided for **educational and creative automation use**.

---

## ❤️ Credits

Built using:

* Python
* Tkinter
* MoviePy 2.x
* OpenCV
* Pillow
* ImageIO + FFmpeg

---

## ⭐ Support This Project

If this tool helped you:

* ⭐ Star the repo on GitHub
* 📢 Share with your creator friends
* 🚀 Build something awesome with it

---

**Happy Editing & Going Viral! 🎬🔥**

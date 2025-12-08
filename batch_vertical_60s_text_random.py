import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageEnhance
import imageio
import numpy as np
import cv2
import threading
from moviepy import VideoFileClip, AudioFileClip
import os
import random

# =========================
# CONFIG
# =========================
VIDEO_SECONDS = 60
VIDEO_FPS = 24
TOTAL_FRAMES = VIDEO_SECONDS * VIDEO_FPS

EXPORT_WIDTH = 1088
EXPORT_HEIGHT = 1920

BASE_EFFECTS = 50
FRAMES_PER_EFFECT = TOTAL_FRAMES // BASE_EFFECTS

CAPTION_TEXT = "Follow for More"


# =========================
# RANDOM EFFECT GENERATOR
# =========================
def generate_random_effects():
    effects = []
    for i in range(BASE_EFFECTS):
        t = i / (BASE_EFFECTS - 1)

        brightness = random.uniform(0.2, 2.5) * t + 0.2
        contrast   = random.uniform(0.3, 2.8) * t + 0.3
        saturation = random.uniform(0.0, 3.5) * t
        warmth     = random.randint(-120, 120)
        invert     = random.choice([False, False, True])

        effects.append((brightness, contrast, saturation, warmth, invert))
    return effects


# =========================
# APPLY EFFECT
# =========================
def apply_effect(img, b, c, s, warmth, invert):
    img = ImageEnhance.Brightness(img).enhance(b)
    img = ImageEnhance.Contrast(img).enhance(c)
    img = ImageEnhance.Color(img).enhance(s)

    frame = np.array(img).astype(np.int16)

    frame[:, :, 0] = np.clip(frame[:, :, 0] + warmth, 0, 255)
    frame[:, :, 2] = np.clip(frame[:, :, 2] - warmth, 0, 255)

    if invert:
        frame = 255 - frame

    return frame.astype(np.uint8)


# =========================
# ANIMATED CAPTION
# =========================
def add_animated_caption(frame, frame_index):
    h, w, _ = frame.shape
    y = int(h * 0.9 + 25 * np.sin(frame_index / 12))

    overlay = frame.copy()

    cv2.putText(
        overlay,
        CAPTION_TEXT,
        (int(w * 0.15), y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.1,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    return cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)


# =========================
# IMAGE → VERTICAL FIT
# =========================
def fit_to_vertical(img):
    img_ratio = img.width / img.height
    target_ratio = EXPORT_WIDTH / EXPORT_HEIGHT

    if img_ratio > target_ratio:
        new_height = img.height
        new_width = int(new_height * target_ratio)
    else:
        new_width = img.width
        new_height = int(new_width / target_ratio)

    left = (img.width - new_width) // 2
    top = (img.height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    img = img.crop((left, top, right, bottom))
    return img.resize((EXPORT_WIDTH, EXPORT_HEIGHT))


# =========================
# MAIN APP
# =========================
class BatchVerticalExporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Shorts – Random + Animated Text + Music")
        self.root.geometry("540x820")

        self.image_folder = None
        self.audio_path = None

        tk.Button(root, text="Select Image Folder (20)", command=self.select_folder).pack(pady=8)
        tk.Button(root, text="Add MP3 Music", command=self.load_audio).pack(pady=8)
        tk.Button(root, text="Start Batch Export", command=self.export_threaded).pack(pady=10)

        self.progress = ttk.Progressbar(root, length=420)
        self.progress.pack(pady=20)

        self.status = tk.Label(root, text="Waiting...", fg="blue")
        self.status.pack(pady=10)

    def ui(self, text=None, value=None, color=None):
        def update():
            if text:
                self.status.config(text=text)
            if value is not None:
                self.progress["value"] = value
            if color:
                self.status.config(fg=color)
        self.root.after(0, update)

    def select_folder(self):
        self.image_folder = filedialog.askdirectory()
        self.ui("Image folder selected ✅", 0, "green")

    def load_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3")])
        self.ui("MP3 loaded ✅", 0, "green")

    def export_threaded(self):
        threading.Thread(target=self.export_batch, daemon=True).start()

    def export_batch(self):
        if not self.image_folder:
            self.ui("Select image folder ❌", 0, "red")
            return

        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        images = sorted([
            f for f in os.listdir(self.image_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])[:20]

        for idx, filename in enumerate(images, start=1):
            try:
                self.ui(f"Rendering {idx}/20", (idx / len(images)) * 100, "orange")

                img_path = os.path.join(self.image_folder, filename)
                base_pil = Image.open(img_path).convert("RGB")
                base_img = fit_to_vertical(base_pil)

                effects = generate_random_effects()

                temp_video = os.path.join(output_dir, f"temp_{idx}.mp4")
                final_video = os.path.join(output_dir, f"{idx:02d}_{os.path.splitext(filename)[0]}.mp4")

                writer = imageio.get_writer(temp_video, fps=VIDEO_FPS)
                frame_counter = 0

                for i in range(len(effects) - 1):
                    b1, c1, s1, w1, inv1 = effects[i]
                    b2, c2, s2, w2, inv2 = effects[i + 1]

                    frame_a = apply_effect(base_img, b1, c1, s1, w1, inv1)
                    frame_b = apply_effect(base_img, b2, c2, s2, w2, inv2)

                    for step in range(FRAMES_PER_EFFECT):
                        alpha = step / FRAMES_PER_EFFECT
                        frame = cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)
                        frame = add_animated_caption(frame, frame_counter)
                        writer.append_data(frame)
                        frame_counter += 1

                writer.close()

                if self.audio_path:
                    video_clip = VideoFileClip(temp_video)
                    audio_clip = AudioFileClip(self.audio_path)

                    if audio_clip.duration > VIDEO_SECONDS:
                        audio_clip = audio_clip.subclipped(0, VIDEO_SECONDS)
                    else:
                        audio_clip = audio_clip.audio_loop(duration=VIDEO_SECONDS)

                    final_clip = video_clip.with_audio(audio_clip)
                    final_clip.write_videofile(final_video, fps=VIDEO_FPS, codec="libx264", audio_codec="aac")
                    os.remove(temp_video)
                else:
                    os.rename(temp_video, final_video)

            except Exception as e:
                print("ERROR:", e)

        self.ui("✅ Batch Export Completed!", 100, "green")


# =========================
# RUN APP
# =========================
root = tk.Tk()
app = BatchVerticalExporter(root)
root.mainloop()

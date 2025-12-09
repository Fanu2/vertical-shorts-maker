import tkinter as tk
from tkinter import filedialog, ttk
import threading
import os
import math

import cv2
import numpy as np
from PIL import Image
import imageio

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


# =========================
# CONFIG
# =========================
VERTICAL_W = 1088
VERTICAL_H = 1920


# =========================
# IMAGE FIT FOR SHORTS
# =========================
def crop_to_vertical(frame):
    h, w, _ = frame.shape
    target_ratio = VERTICAL_W / VERTICAL_H
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x1 = (w - new_w) // 2
        frame = frame[:, x1:x1 + new_w]
    else:
        new_h = int(w / target_ratio)
        y1 = (h - new_h) // 2
        frame = frame[y1:y1 + new_h, :]

    return cv2.resize(frame, (VERTICAL_W, VERTICAL_H))


# =========================
# TEXT BAR OVERLAY
# =========================
def add_caption_bars(frame, top_text, bottom_text):
    h, w, _ = frame.shape
    bar_h = int(h * 0.12)

    overlay = frame.copy()

    # Top bar
    cv2.rectangle(overlay, (0, 0), (w, bar_h), (0, 0, 0), -1)
    cv2.putText(
        overlay, top_text,
        (int(w * 0.03), int(bar_h * 0.65)),
        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA
    )

    # Bottom bar
    cv2.rectangle(overlay, (0, h - bar_h), (w, h), (0, 0, 0), -1)
    cv2.putText(
        overlay, bottom_text,
        (int(w * 0.03), int(h - bar_h * 0.35)),
        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA
    )

    return cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)


# =========================
# MAIN GUI
# =========================
class MP4ShortsEditor:
    def __init__(self, root):
        self.root = root
        root.title("Advanced MP4 Shorts Editor")
        root.geometry("720x520")
        root.resizable(False, False)

        self.video_path = None
        self.audio_path = None

        # --- FILE BUTTONS ---
        tk.Button(root, text="Select MP4 Video", command=self.select_video).pack(pady=5)
        tk.Button(root, text="Select MP3 (optional)", command=self.select_audio).pack(pady=5)

        # --- PRESET TRIM ---
        preset_frame = tk.Frame(root)
        preset_frame.pack()

        tk.Label(preset_frame, text="Trim Preset:").grid(row=0, column=0)
        self.trim_var = tk.StringVar(value="60")

        for i, txt in enumerate(["15", "30", "60", "Custom"]):
            tk.Radiobutton(preset_frame, text=txt, value=txt, variable=self.trim_var).grid(row=0, column=i+1)

        # --- CUSTOM TRIM ---
        custom_frame = tk.Frame(root)
        custom_frame.pack(pady=4)
        tk.Label(custom_frame, text="Custom Start (s)").grid(row=0, column=0)
        self.start_entry = tk.Entry(custom_frame, width=6)
        self.start_entry.insert(0, "0")
        self.start_entry.grid(row=0, column=1)

        tk.Label(custom_frame, text="Custom End (s)").grid(row=0, column=2)
        self.end_entry = tk.Entry(custom_frame, width=6)
        self.end_entry.grid(row=0, column=3)

        # --- TEXT BARS ---
        text_frame = tk.Frame(root)
        text_frame.pack(pady=5)

        tk.Label(text_frame, text="Top Bar Text").grid(row=0, column=0)
        self.top_text = tk.Entry(text_frame, width=36)
        self.top_text.insert(0, "TOP CAPTION")
        self.top_text.grid(row=0, column=1)

        tk.Label(text_frame, text="Bottom Bar Text").grid(row=1, column=0)
        self.bottom_text = tk.Entry(text_frame, width=36)
        self.bottom_text.insert(0, "FOLLOW FOR MORE")
        self.bottom_text.grid(row=1, column=1)

        # --- OPTIONS ---
        options = tk.Frame(root)
        options.pack(pady=5)

        self.strip_audio = tk.BooleanVar(value=True)
        self.fade_audio = tk.BooleanVar(value=True)
        self.loop_video = tk.BooleanVar(value=False)
        self.vertical_crop = tk.BooleanVar(value=True)

        tk.Checkbutton(options, text="Strip original audio", variable=self.strip_audio).grid(row=0, column=0)
        tk.Checkbutton(options, text="Audio fade in/out", variable=self.fade_audio).grid(row=0, column=1)
        tk.Checkbutton(options, text="Loop video to MP3", variable=self.loop_video).grid(row=1, column=0)
        tk.Checkbutton(options, text="Vertical Shorts crop 9:16", variable=self.vertical_crop).grid(row=1, column=1)

        # --- ACTION ---
        tk.Button(root, text="Process & Export", command=self.start_thread).pack(pady=12)

        self.progress = ttk.Progressbar(root, length=600)
        self.progress.pack(pady=5)

        self.status = tk.Label(root, text="Waiting...", fg="blue")
        self.status.pack()

    def ui(self, text=None, value=None, color=None):
        def _u():
            if text:
                self.status.config(text=text)
            if value is not None:
                self.progress["value"] = value
            if color:
                self.status.config(fg=color)
        self.root.after(0, _u)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4", "*.mp4")])
        if self.video_path:
            self.ui("Video loaded ✅", 0, "green")

    def select_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("MP3", "*.mp3")])
        if self.audio_path:
            self.ui("MP3 loaded ✅", None, "green")

    def start_thread(self):
        threading.Thread(target=self.process_video, daemon=True).start()

    def process_video(self):
        if not self.video_path:
            self.ui("Please select MP4 ❌", None, "red")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if not save_path:
            return

        self.ui("Loading video...", 5, "orange")
        clip = VideoFileClip(self.video_path)

        # --- TRIM LOGIC ---
        if self.trim_var.get() != "Custom":
            end_time = min(float(self.trim_var.get()), clip.duration)
            start_time = 0.0
        else:
            start_time = float(self.start_entry.get() or 0)
            end_time = float(self.end_entry.get() or clip.duration)

        trimmed = clip.subclipped(start_time, end_time)

        # --- FRAME PROCESSING ---
        self.ui("Rendering frames & captions...", 20, "orange")
        temp_video = save_path + ".tmp.mp4"
        writer = imageio.get_writer(temp_video, fps=clip.fps)

        for frame in trimmed.iter_frames(dtype="uint8"):
            if self.vertical_crop.get():
                frame = crop_to_vertical(frame)

            frame = add_caption_bars(frame, self.top_text.get(), self.bottom_text.get())
            writer.append_data(frame)

        writer.close()
        trimmed.close()
        clip.close()

        final_clip = VideoFileClip(temp_video)

        # --- AUDIO ---
        if self.audio_path:
            self.ui("Processing audio...", 80, "orange")
            audio = AudioFileClip(self.audio_path)

            if audio.duration > final_clip.duration:
                audio = audio.subclipped(0, final_clip.duration)
            else:
                audio = audio.audio_loop(duration=final_clip.duration)

            if self.fade_audio.get():
                audio = audio.audio_fadein(1.0).audio_fadeout(1.0)

            final_clip = final_clip.with_audio(audio)

        elif self.strip_audio.get():
            final_clip = final_clip.with_audio(None)

        # --- EXPORT ---
        self.ui("Exporting...", 90, "orange")
        final_clip.write_videofile(save_path, codec="libx264", audio_codec="aac")

        final_clip.close()
        os.remove(temp_video)

        self.ui("✅ Export complete!", 100, "green")


if __name__ == "__main__":
    root = tk.Tk()
    app = MP4ShortsEditor(root)
    root.mainloop()

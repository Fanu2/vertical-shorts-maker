import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image
import imageio
import numpy as np
import cv2
import threading
from moviepy import VideoFileClip, AudioFileClip
import os

# =========================
# CONFIG
# =========================
VIDEO_SECONDS = 60          # target length for Shorts
VIDEO_FPS = 24
TOTAL_FRAMES = VIDEO_SECONDS * VIDEO_FPS

EXPORT_WIDTH = 1088         # divisible by 16 for codecs
EXPORT_HEIGHT = 1920        # vertical 9:16


def fit_to_vertical(img: Image.Image) -> Image.Image:
    """
    Center-crop the image to 9:16 ratio and resize to EXPORT_WIDTH x EXPORT_HEIGHT.
    """
    img_ratio = img.width / img.height
    target_ratio = EXPORT_WIDTH / EXPORT_HEIGHT

    if img_ratio > target_ratio:
        # too wide -> crop left/right
        new_height = img.height
        new_width = int(new_height * target_ratio)
    else:
        # too tall -> crop top/bottom
        new_width = img.width
        new_height = int(new_width / target_ratio)

    left = (img.width - new_width) // 2
    top = (img.height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    img = img.crop((left, top, right, bottom))
    return img.resize((EXPORT_WIDTH, EXPORT_HEIGHT))


def add_text_overlay(frame: np.ndarray, text: str, frame_index: int) -> np.ndarray:
    """
    Add static (but slightly animated) text overlay near bottom of frame.
    """
    if not text:
        return frame

    h, w, _ = frame.shape
    # small vertical float animation for some life
    y = int(h * 0.9 + 20 * np.sin(frame_index / 12.0))

    overlay = frame.copy()
    cv2.putText(
        overlay,
        text,
        (int(w * 0.1), y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    # blend overlay and base for soft look
    return cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)


class ImagesToShortsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Images → YouTube Shorts Maker")
        self.root.geometry("560x320")
        self.root.resizable(False, False)

        self.images_folder = None
        self.audio_path = None

        # UI elements
        tk.Button(root, text="Select Images Folder", command=self.select_images_folder).pack(pady=5)
        tk.Button(root, text="Select MP3 (optional)", command=self.select_audio).pack(pady=5)

        # Text overlay
        text_frame = tk.Frame(root)
        text_frame.pack(pady=5)
        tk.Label(text_frame, text="Overlay Text:").pack(side=tk.LEFT, padx=5)
        self.text_entry = tk.Entry(text_frame, width=30)
        self.text_entry.insert(0, "Follow for more ✨")
        self.text_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(root, text="Create Shorts Video", command=self.start_thread).pack(pady=10)

        self.progress = ttk.Progressbar(root, length=440)
        self.progress.pack(pady=10)

        self.status = tk.Label(root, text="Waiting...", fg="blue")
        self.status.pack(pady=5)

    def ui(self, text=None, value=None, color=None):
        """
        Thread-safe UI updater using root.after()
        """
        def _update():
            if text is not None:
                self.status.config(text=text)
            if value is not None:
                self.progress["value"] = value
            if color is not None:
                self.status.config(fg=color)
        self.root.after(0, _update)

    def select_images_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_folder = folder
            self.ui("Images folder selected ✅", 0, "green")

    def select_audio(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 Audio", "*.mp3")])
        if path:
            self.audio_path = path
            self.ui("MP3 selected ✅", None, "green")

    def start_thread(self):
        t = threading.Thread(target=self.build_video, daemon=True)
        t.start()

    def build_video(self):
        if not self.images_folder:
            self.ui("Select images folder first ❌", None, "red")
            return

        # Gather images
        images = sorted(
            f for f in os.listdir(self.images_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        )

        if not images:
            self.ui("No images found in folder ❌", None, "red")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if not save_path:
            return

        temp_path = save_path + ".temp_no_audio.mp4"

        # Preprocess images to vertical format
        self.ui("Loading and resizing images...", 0, "orange")
        pil_images = []
        for img_name in images:
            img_path = os.path.join(self.images_folder, img_name)
            try:
                img = Image.open(img_path).convert("RGB")
                img = fit_to_vertical(img)
                pil_images.append(img)
            except Exception as e:
                print("Error loading image:", img_path, e)
                continue

        if not pil_images:
            self.ui("No valid images to use ❌", None, "red")
            return

        num_images = len(pil_images)
        frames_per_image = max(1, TOTAL_FRAMES // num_images)

        writer = imageio.get_writer(temp_path, fps=VIDEO_FPS)
        overlay_text = self.text_entry.get().strip()

        frame_index = 0
        total_frames_written = 0

        self.ui("Building video from images...", 0, "orange")

        try:
            for i, img in enumerate(pil_images):
                base_frame = np.array(img)

                for _ in range(frames_per_image):
                    if total_frames_written >= TOTAL_FRAMES:
                        break

                    frame = base_frame.copy()
                    frame = add_text_overlay(frame, overlay_text, frame_index)
                    writer.append_data(frame)

                    frame_index += 1
                    total_frames_written += 1

                progress = (total_frames_written / TOTAL_FRAMES) * 70  # first 70% for video
                self.ui(value=progress)

                if total_frames_written >= TOTAL_FRAMES:
                    break

            # If still short, pad with last image
            while total_frames_written < TOTAL_FRAMES:
                base_frame = np.array(pil_images[-1])
                frame = add_text_overlay(base_frame, overlay_text, frame_index)
                writer.append_data(frame)
                frame_index += 1
                total_frames_written += 1
                progress = (total_frames_written / TOTAL_FRAMES) * 70
                self.ui(value=progress)

        finally:
            writer.close()

        # Attach audio if provided
        if self.audio_path:
            try:
                self.ui("Attaching audio...", 85, "orange")
                video_clip = VideoFileClip(temp_path)
                audio_clip = AudioFileClip(self.audio_path)

                # Make audio exactly 60 seconds: trim or loop
                if audio_clip.duration > VIDEO_SECONDS:
                    audio_clip = audio_clip.subclipped(0, VIDEO_SECONDS)
                else:
                    audio_clip = audio_clip.audio_loop(duration=VIDEO_SECONDS)

                final_clip = video_clip.with_audio(audio_clip)
                final_clip.write_videofile(
                    save_path,
                    fps=VIDEO_FPS,
                    codec="libx264",
                    audio_codec="aac"
                )

                video_clip.close()
                final_clip.close()
                audio_clip.close()
                os.remove(temp_path)
            except Exception as e:
                print("Audio attach error:", e)
                # If audio fails, keep video-only file
                if os.path.exists(temp_path):
                    os.rename(temp_path, save_path)
        else:
            # No audio selected: just rename temp to final
            os.rename(temp_path, save_path)

        self.ui("✅ Shorts video created!", 100, "green")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagesToShortsGUI(root)
    root.mainloop()

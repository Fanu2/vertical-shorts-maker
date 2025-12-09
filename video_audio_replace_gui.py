import tkinter as tk
from tkinter import filedialog, ttk
import os
import math
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import threading


class AudioReplaceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Audio Replacer – Loop Video to MP3 Length")
        self.root.geometry("540x260")
        self.root.resizable(False, False)

        self.video_folder = None
        self.audio_path = None

        # Buttons
        tk.Button(root, text="Select Videos Folder", command=self.select_folder).pack(pady=5)
        tk.Button(root, text="Select MP3 Audio", command=self.select_audio).pack(pady=5)
        tk.Button(root, text="Start Processing", command=self.start_thread).pack(pady=10)

        # Progress + status
        self.progress = ttk.Progressbar(root, length=420)
        self.progress.pack(pady=10)

        self.status = tk.Label(root, text="Waiting...", fg="blue")
        self.status.pack(pady=5)

    # Helper to safely update UI from worker thread
    def update_ui(self, text=None, value=None, color=None):
        def _inner():
            if text is not None:
                self.status.config(text=text)
            if value is not None:
                self.progress["value"] = value
            if color is not None:
                self.status.config(fg=color)
        self.root.after(0, _inner)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.video_folder = folder
            self.update_ui("Video folder selected ✅", 0, "green")

    def select_audio(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 Audio", "*.mp3")])
        if path:
            self.audio_path = path
            self.update_ui("MP3 audio selected ✅", None, "green")

    def start_thread(self):
        t = threading.Thread(target=self.process_videos, daemon=True)
        t.start()

    def process_videos(self):
        if not self.video_folder:
            self.update_ui("Select videos folder first ❌", None, "red")
            return

        if not self.audio_path:
            self.update_ui("Select MP3 audio first ❌", None, "red")
            return

        # Ask where to save processed videos
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        # Collect mp4 files
        videos = sorted(
            f for f in os.listdir(self.video_folder)
            if f.lower().endswith(".mp4")
        )

        if not videos:
            self.update_ui("No .mp4 files found in folder ❌", None, "red")
            return

        # Load audio clip once
        try:
            base_audio = AudioFileClip(self.audio_path)
            target_duration = base_audio.duration
        except Exception as e:
            print("Audio load error:", e)
            self.update_ui("Error loading audio ❌", None, "red")
            return

        total_videos = len(videos)

        for idx, filename in enumerate(videos, start=1):
            video_path = os.path.join(self.video_folder, filename)
            out_name = os.path.splitext(filename)[0] + "_with_audio.mp4"
            out_path = os.path.join(output_dir, out_name)

            try:
                self.update_ui(
                    text=f"Processing {idx}/{total_videos}: {filename}",
                    value=(idx - 1) / total_videos * 100,
                    color="orange"
                )

                # Load video
                clip = VideoFileClip(video_path)

                # Loop or trim video to match audio length
                video_duration = clip.duration

                if video_duration >= target_duration:
                    # Just trim video to audio duration
                    base_video = clip.subclipped(0, target_duration)
                else:
                    # Loop video enough times, then trim
                    loops = math.ceil(target_duration / video_duration)
                    clips = [clip] * loops
                    long_video = concatenate_videoclips(clips)
                    base_video = long_video.subclipped(0, target_duration)

                # Attach audio (overwrite existing)
                final_audio = base_audio  # same audio for all videos
                final_clip = base_video.with_audio(final_audio)

                # Write output
                final_clip.write_videofile(
                    out_path,
                    fps=clip.fps,
                    codec="libx264",
                    audio_codec="aac"
                )

                # Close clips to free resources
                clip.close()
                base_video.close()
                final_clip.close()

            except Exception as e:
                print("Error processing", filename, ":", e)
                continue

        self.update_ui("✅ All videos processed!", 100, "green")
        # Close audio at the end
        base_audio.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioReplaceGUI(root)
    root.mainloop()

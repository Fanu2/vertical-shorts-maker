import os
import requests
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image

# ============================
# SETTINGS
# ============================
URL = "https://fifty-shades-react.vercel.app/"
OUTPUT_DIR = "downloaded_images"
OUTPUT_VIDEO = "fifty_shades_video.mp4"
SECONDS_PER_IMAGE = 2
FPS = 30  # Video smoothness

# ============================
# CREATE IMAGE FOLDER
# ============================
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================
# SCRAPE IMAGE URLS
# ============================
print("🔍 Fetching webpage...")
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

image_tags = soup.find_all("img")
image_urls = [
    urljoin(URL, img.get("src"))
    for img in image_tags
    if img.get("src")
]

print(f"✅ Found {len(image_urls)} images")

# ============================
# DOWNLOAD IMAGES
# ============================
downloaded_images = []

for i, img_url in enumerate(image_urls):
    try:
        img_data = requests.get(img_url).content
        filename = os.path.join(OUTPUT_DIR, f"img_{i:03d}.jpg")

        with open(filename, "wb") as f:
            f.write(img_data)

        downloaded_images.append(filename)
        print(f"⬇️ Downloaded: {filename}")

    except Exception as e:
        print(f"❌ Failed to download {img_url}: {e}")

# ============================
# CREATE VIDEO FROM IMAGES
# ============================
if not downloaded_images:
    print("❌ No images downloaded. Exiting.")
    exit()

# Load first image to get size
first_img = Image.open(downloaded_images[0])
width, height = first_img.size

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))

frames_per_image = FPS * SECONDS_PER_IMAGE

for img_path in downloaded_images:
    img = cv2.imread(img_path)

    # Resize just in case sizes differ
    img = cv2.resize(img, (width, height))

    for _ in range(frames_per_image):
        video.write(img)

video.release()

print(f"\n🎬 VIDEO CREATED SUCCESSFULLY: {OUTPUT_VIDEO}")


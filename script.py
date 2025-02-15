import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Website URL
BASE_URL = "https://webmarce.com/html/scrapcar/index.html"

# Create a folder to store the files
os.makedirs("scraped_files", exist_ok=True)

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# Function to clean file names by removing query parameters
def clean_filename(url):
    parsed_url = urlparse(url)  # Parse the URL
    filename = os.path.basename(parsed_url.path)  # Get only the file name (ignore query parameters)
    return filename


# Function to download and save a file
def download_file(url, folder):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            filename = clean_filename(url)  # Clean file name
            filepath = os.path.join(folder, filename)
            with open(filepath, "wb") as file:
                file.write(response.content)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Failed to download: {url} (Status Code: {response.status_code})")
    except requests.RequestException as e:
        print(f"❌ Error downloading {url}: {e}")


# Step 1: Download the main HTML page
try:
    session = requests.Session()
    response = session.get(BASE_URL, headers=HEADERS, timeout=10)

    if response.status_code == 200:
        html_content = response.text
        with open("scraped_files/index.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        print("✅ Saved: index.html")
    else:
        print(f"❌ Failed to download main page. Status Code: {response.status_code}")
        exit()

    # Step 2: Parse the HTML to find CSS, JS, Images, and other assets
    soup = BeautifulSoup(html_content, "html.parser")

    # Find CSS files
    css_links = [urljoin(BASE_URL, link["href"]) for link in soup.find_all("link", rel="stylesheet") if "href" in link.attrs]
    
    # Find JS files
    js_links = [urljoin(BASE_URL, script["src"]) for script in soup.find_all("script") if "src" in script.attrs]

    # Find Image files (png, jpg, jpeg, gif, svg)
    img_links = [urljoin(BASE_URL, img["src"]) for img in soup.find_all("img") if "src" in img.attrs]

    # Find Font files (woff, woff2, ttf, otf)
    font_links = [urljoin(BASE_URL, link["href"]) for link in soup.find_all("link", rel="stylesheet") if "href" in link.attrs and any(ext in link["href"] for ext in [".woff", ".woff2", ".ttf", ".otf"])]

    # Find Other Assets (Optional) - Videos, Audio
    video_links = [urljoin(BASE_URL, source["src"]) for source in soup.find_all("source") if "src" in source.attrs and source["src"].endswith((".mp4", ".webm"))]
    audio_links = [urljoin(BASE_URL, source["src"]) for source in soup.find_all("source") if "src" in source.attrs and source["src"].endswith((".mp3", ".wav"))]

    # Create folders for assets
    os.makedirs("scraped_files/css", exist_ok=True)
    os.makedirs("scraped_files/js", exist_ok=True)
    os.makedirs("scraped_files/images", exist_ok=True)
    os.makedirs("scraped_files/fonts", exist_ok=True)
    os.makedirs("scraped_files/videos", exist_ok=True)
    os.makedirs("scraped_files/audio", exist_ok=True)

    # Download CSS & JS files
    for css_link in css_links:
        download_file(css_link, "scraped_files/css")

    for js_link in js_links:
        download_file(js_link, "scraped_files/js")

    # Download Images
    for img_link in img_links:
        download_file(img_link, "scraped_files/images")

    # Download Fonts
    for font_link in font_links:
        download_file(font_link, "scraped_files/fonts")

    # Download Videos (if available)
    for video_link in video_links:
        download_file(video_link, "scraped_files/videos")

    # Download Audio (if available)
    for audio_link in audio_links:
        download_file(audio_link, "scraped_files/audio")

    print("🎉 Scraping completed! All files are saved in the 'scraped_files' folder.")

except requests.RequestException as e:
    print(f"❌ Failed to fetch the webpage: {e}")

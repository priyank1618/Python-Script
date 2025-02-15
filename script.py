import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Website URL
BASE_URL = "https://webmarce.com/html/scrapcar/index.html"

# Create a folder to store the files
os.makedirs("scraped_files", exist_ok=True)

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# Function to download and save a file
def download_file(url, folder):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            filename = url.split("/")[-1]
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

    # Step 2: Parse the HTML to find CSS & JS files
    soup = BeautifulSoup(html_content, "html.parser")

    # Find CSS files
    css_links = [urljoin(BASE_URL, link["href"]) for link in soup.find_all("link", rel="stylesheet") if
                 "href" in link.attrs]
    # Find JS files
    js_links = [urljoin(BASE_URL, script["src"]) for script in soup.find_all("script") if "src" in script.attrs]

    # Create folders for CSS and JS
    os.makedirs("scraped_files/css", exist_ok=True)
    os.makedirs("scraped_files/js", exist_ok=True)

    # Download CSS & JS files
    for css_link in css_links:
        download_file(css_link, "scraped_files/css")

    for js_link in js_links:
        download_file(js_link, "scraped_files/js")

    print("🎉 Scraping completed! All files are saved in the 'scraped_files' folder.")

except requests.RequestException as e:
    print(f"❌ Failed to fetch the webpage: {e}")

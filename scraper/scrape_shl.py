import json
import time
import os
import requests

from bs4 import BeautifulSoup

BASE_URL = (
    "https://www.shl.com"
)

CATALOG_URL = (
    "https://www.shl.com/"
    "solutions/products/product-catalog/"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0"
    )
}

response = requests.get(
    CATALOG_URL,
    headers=headers
)

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

assessment_links = set()

# Collect all links
for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/products/" in href:

        full_url = href

        if not href.startswith("http"):

            full_url = BASE_URL + href

        assessment_links.add(full_url)

print(
    f"Found {len(assessment_links)} links"
)

results = []

visited = set()

for url in assessment_links:

    if url in visited:
        continue

    visited.add(url)

    try:

        print(f"Scraping: {url}")

        page = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        page_soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        title = (
    page_soup.title.text
    .replace("| SHL", "")
    .replace("- SHL", "")
    .strip()
)

        # Extract visible text
        paragraphs = page_soup.find_all("p")

        description = " ".join([
            p.get_text(" ", strip=True)
            for p in paragraphs
        ])

        # Basic filtering
        if (
    len(title) < 3
    or "cookie" in title.lower()
    or "error" in title.lower()
):
             continue
    

        # Detect assessment type
        lower_desc = description.lower()

        test_type = "Assessment"

        if "personality" in lower_desc:
             test_type = "P"
    

        elif "cognitive" in lower_desc:
             test_type = "C"
    

        elif "behavior" in lower_desc:
             test_type = "B"
    

        elif "knowledge" in lower_desc:
             test_type = "K"
    

        assessment = {
    "name": title,
    "url": url,
    "description": description[:5000],
    "test_type": test_type
}

        results.append(assessment)

        print(f"Added: {title}")

        time.sleep(1)

    except Exception as e:

        print(
            f"Error scraping {url}: {e}"
        )

# Remove duplicates
unique = []

seen = set()

for item in results:

    if item["url"] not in seen:

        unique.append(item)

        seen.add(item["url"])

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

catalog_path = os.path.join(
    BASE_DIR,
    "..",
    "app",
    "catalog.json"
)

with open(
    catalog_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        unique,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(unique)} assessments"
)
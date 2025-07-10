import requests
import os
import pandas as pd
from urllib.parse import quote_plus
from tqdm import tqdm
from rapidfuzz import process, fuzz
import time
import re

BASE_URL = "http://127.0.0.1:8000/books/"  # my API endpoint
OUTDIR = "gutenberg_shortstory_collections"
CSV_OUT = "matched_books.csv"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/shortstoryclassifier/short_story_collections_circulating_library.csv")

df = df.dropna(subset=["Title", "Author"])
df = df.drop_duplicates(subset=["Title", "Author"])
books_to_fetch = list(df[["Title", "Author"]].itertuples(index=False, name=None))

def search_book(title, author=None):
    query = quote_plus(f"{title} {author}" if author else title)
    try:
        response = requests.get(f"{BASE_URL}?search={query}", timeout=10)
        if response.ok:
            return response.json().get("results", [])
    except Exception as e:
        print(f"✘ error during API search: {e}")
    return []

def find_text_url(book):
    formats = book.get("formats", {})
    # look for best matching plain text url
    for key, url in formats.items():
        key_lower = key.lower()
        if "text/plain" in key_lower:
            return url
    return None

def sanitize_filename(name):
    name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
    return name[:100]

def download_text(url, out_path):
    try:
        r = requests.get(url, timeout=20)
        if r.ok:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(r.text)
            return True
        else:
            print(f"✘ HTTP error {r.status_code} for {url}")
    except Exception as e:
        print(f"✘ error downloading {url}: {e}")
    return False

results_metadata = []
success_count = 0

for title, author in tqdm(books_to_fetch, desc="downloading texts"):
    candidates = search_book(title, author)
    if not candidates:
        print(f"not found: {title} by {author}")
        continue

    # use rapidfuzz to find best title match
    match = process.extractOne(title, [b["title"] for b in candidates], scorer=fuzz.token_sort_ratio)
    if match and match[1] >= 75:
        matched_title = match[0]
        chosen = next(b for b in candidates if b["title"] == matched_title)
        url = find_text_url(chosen)
        if url:
            safe_title = sanitize_filename(title.replace(' ', '_'))
            filename = f"{safe_title}_{chosen['id']}.txt"
            path = os.path.join(OUTDIR, filename)
            if download_text(url, path):
                success_count += 1
                print(f"✔ downloaded {title} by {author}")
                results_metadata.append({
                    "title": title,
                    "author": author,
                    "gutenberg_id": chosen["id"],
                    "download_url": url,
                    "saved_filename": filename
                })
            else:
                print(f"✘ failed to download {title}")
        else:
            print(f"no plain text URL for: {title}")
    else:
        print(f"no close match found for: {title}")

    time.sleep(1)  # polite delay

pd.DataFrame(results_metadata).to_csv(CSV_OUT, index=False)
print(f"\nfinished! successfully downloaded {success_count} out of {len(books_to_fetch)} books.")
print(f"metadata saved to {CSV_OUT}")

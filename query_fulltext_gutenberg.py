import requests
import os
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/books/"
CSV_IN = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/perspectiveclassifier/gutenberg_perspective_metadata.csv"
OUTDIR_BASE = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/perspectiveclassifier"
PERSPECTIVE_DIRS = {
    "1st": os.path.join(OUTDIR_BASE, "1st person"),
    "3rd": os.path.join(OUTDIR_BASE, "3rd person"),
}

df = pd.read_csv(CSV_IN)
df = df[df["narr-perspective"].isin(["1st", "3rd"])].copy()
df["gutenberg_id"] = df["gutenberg_id"].astype(int)

def find_text_url(book):
    formats = book.get("formats", {})
    preferred_order = [
        "text/plain; charset=utf-8",
        "text/plain; charset=us-ascii",
        "text/plain; charset=iso-8859-1",
        "text/plain"
    ]
    for encoding in preferred_order:
        for mime, url in formats.items():
            if mime.startswith(encoding):
                return url
    for mime, url in formats.items():
        if mime.startswith("text/plain"):
            return url
    return None

def download_text(gid, title, perspective):
    try:
        response = requests.get(f"{BASE_URL}{gid}", timeout=15)
        if not response.ok:
            return (gid, title, "metadata fetch failed")

        book = response.json()
        text_url = find_text_url(book)
        if not text_url:
            return (gid, book.get("title", "unknown title"), "no plain text URL")

        filename = f"pg{gid}.txt"
        outdir = PERSPECTIVE_DIRS.get(perspective)
        if not outdir:
            return (gid, book.get("title", "unknown title"), f"unknown perspective '{perspective}'")
        filepath = os.path.join(outdir, filename)

        r = requests.get(text_url, timeout=30)
        if r.ok:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(r.text)
            return (gid, book.get("title", "unknown title"), "success")
        else:
            return (gid, book.get("title", "unknown title"), f"HTTP {r.status_code}")

    except Exception as e:
        return (gid, title, f"error: {e}")

success_count = 0
failures = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {
        executor.submit(download_text, row["gutenberg_id"], row["title"], row["narr-perspective"]): row["gutenberg_id"]
        for _, row in df.iterrows()
    }
    with tqdm(total=len(futures), desc="downloading texts") as pbar:
        for future in as_completed(futures):
            gid, title, status = future.result()
            pbar.update(1)
            if status == "success":
                success_count += 1
            else:
                tqdm.write(f"✘ {status} for ID {gid} - '{title}'")
                failures.append((gid, title, status))

print(f"\nfinished! successfully downloaded {success_count} out of {len(df['gutenberg_id'])} books.")

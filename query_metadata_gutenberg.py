import requests
import csv
import pandas as pd
from tqdm import tqdm

# read from /Users/starrothkopf/Desktop/HDW/noveltmmeta/perspectiveclassifier/perspective_classifier_test_set.csv
# if the row has a gut-ebook number, add the book to a csv

"""
params = { # 24,511
    "topic": "fiction",
    "languages": "en",
    "copyright": "false",
    "min_year": 1789,
    "max_year": 1913,
}
"""

"""
params = {
    "topic": "short stories",
    "languages": "en",
    "copyright": "false",
    "min_year": 1789,
    "max_year": 1913,
}
"""

CSV_IN = "/Users/starrothkopf/Desktop/HDW/noveltmmeta/perspectiveclassifier/perspective_classifier_test_set.csv"
BASE_URL = "http://127.0.0.1:8000/books/"
CSV_OUT = "gutenberg_perspective_metadata.csv"

def flatten_person_list(person_list):
    # format a list of persons into a semi-colon separated string of names (with birth/death years)
    return "; ".join(
        f"{p.get('name','Unknown')} ({p.get('birth_year','?')}-{p.get('death_year','?')})" 
        for p in person_list
    ) if person_list else ""

def flatten_formats(formats_dict):
    # flatten the formats dict into a single string of mime-type=url pairs
    return "; ".join(f"{k}={v}" for k, v in formats_dict.items()) if formats_dict else ""

df = pd.read_csv(CSV_IN)

# drop rows without a Gutenberg ID
df = df[df['gut-ebook'].notna()].copy()
df['gut-ebook'] = df['gut-ebook'].astype(int)

with open(CSV_OUT, mode="w", newline="", encoding="utf-8") as f:
    headers = [
        "gutenberg_id", "title", "subjects", "bookshelves", "languages", "copyright", "media_type",
        "download_count", "authors", "translators", "summaries", "formats", "narr-perspective"
    ]
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Fetching metadata"):
        gut_id = row["gut-ebook"]
        narr_perspective = row["narr-perspective"]
        response = requests.get(BASE_URL + str(gut_id))
        if response.ok:
            book = response.json()
            out_row = {
                "gutenberg_id": book.get("id"),
                "title": book.get("title", "").strip(),
                "subjects": "; ".join(book.get("subjects", [])),
                "bookshelves": "; ".join(book.get("bookshelves", [])),
                "languages": "; ".join(book.get("languages", [])),
                "copyright": book.get("copyright"),
                "media_type": book.get("media_type"),
                "download_count": book.get("download_count"),
                "authors": flatten_person_list(book.get("authors", [])),
                "translators": flatten_person_list(book.get("translators", [])),
                "summaries": "; ".join(book.get("summaries", [])),
                "formats": flatten_formats(book.get("formats", {})),
                "narr-perspective": narr_perspective
            }
            writer.writerow(out_row)
        else:
            print(f"error fetching book ID {gut_id}: {response.status_code}")

print(f"done! exported metadata to {CSV_OUT}")

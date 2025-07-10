import requests
import csv
import pandas as pd
from tqdm import tqdm

# read from /Users/starrothkopf/Desktop/HDW/noveltmmeta/perspectiveclassifier/perspective_classifier_test_set.csv
# ,filename,author,title,pub-year,pub-decade,source,gutenberg_url,gut-ebook,HathiTrust ItemID,ht_bib_key,narr-perspective,nation,genre,canonical,Multi-volume
# organize and populate what we can, some from hathi some from gutenberg, either way put id first
# if from gutenberg, query the API for metadata to fill in the other fields
# if from hathi, just move the hathi id column first

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
CSV_OUT = "combined_perspective_metadata.csv"
BASE_URL = "http://127.0.0.1:8000/books/"

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

output_fields = [
    "id", "source", "title", "author", "pub-year", "pub-decade", "nation",
    "genre", "canonical", "Multi-volume", "gutenberg_url", "ht_bib_key", "narr-perspective",
    "subjects", "bookshelves", "copyright", "download_count", "authors"
]

with open(CSV_OUT, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=output_fields)
    writer.writeheader()

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Building combined metadata"):
        source = row.get("source", "").strip().lower()
        narr_perspective = row.get("narr-perspective", "")

        out_row = {
            "source": source,
            "title": row.get("title", ""),
            "author": row.get("author", ""),
            "pub-year": row.get("pub-year", ""),
            "pub-decade": row.get("pub-decade", ""),
            "nation": row.get("nation", ""),
            "genre": row.get("genre", ""),
            "canonical": row.get("canonical", ""),
            "Multi-volume": row.get("Multi-volume", ""),
            "gutenberg_url": row.get("gutenberg_url", ""),
            "ht_bib_key": row.get("ht_bib_key", ""),
            "narr-perspective": narr_perspective,
            "subjects": "",
            "bookshelves": "",
            "copyright": "",
            "download_count": "",
            "authors": "",
        }

        if source == "gutenberg" and pd.notna(row.get("gut-ebook")):
            gut_id = int(row["gut-ebook"])
            out_row["id"] = gut_id
            try:
                response = requests.get(BASE_URL + str(gut_id))
                if response.ok:
                    book = response.json()
                    out_row.update({
                        "subjects": "; ".join(book.get("subjects", [])),
                        "bookshelves": "; ".join(book.get("bookshelves", [])),
                        "copyright": book.get("copyright"),
                        "download_count": book.get("download_count"),
                        "authors": flatten_person_list(book.get("authors", [])),
                    })
                else:
                    print(f"failed to fetch metadata for Gutenberg ID {gut_id}")
            except Exception as e:
                print(f"error fetching Gutenberg ID {gut_id}: {e}")

        elif source == "hathi" and pd.notna(row.get("HathiTrust ItemID")):
            htid = row["HathiTrust ItemID"]
            out_row["id"] = htid
        else:
            out_row["id"] = ""

        writer.writerow(out_row)

print(f"\ndone! combined metadata written to {CSV_OUT}")
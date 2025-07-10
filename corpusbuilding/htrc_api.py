# decided not to do this, would take 4 hours just to get access_rights and part_of_journal

import requests
import time
import pandas as pd
from tqdm import tqdm 

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/ef_rich_features_cleaned.csv")
df_missing = df[df["page_count"].isna()]
results = []

HEADERS = {'User-Agent': 'HTRC Metadata Fetcher for Research'}
BASE_URL = "http://catalog.hathitrust.org/api/volumes/full/htid/"

def fetch_metadata(htid, max_retries=5):
    url = BASE_URL + htid + ".json"
    retries = 0
    wait = 2

    while retries < max_retries:
        try:
            start = time.time()
            res = requests.get(url, headers=HEADERS, timeout=10)
            duration = time.time() - start

            if res.status_code == 429:
                print(f"[{htid}] Throttled! Sleeping for {wait*2} seconds...")
                time.sleep(wait * 2)
                retries += 1
                wait *= 2
                continue

            if duration > 5:
                print(f"[{htid}] Slow response: {duration:.2f}s")

            if res.status_code != 200:
                print(f"[{htid}] Error {res.status_code}")
                return None

            data = res.json()
            record = data.get("records", {}).get(htid, {}).get("record", {})

            return {
                "id": htid,
                "page_count": record.get("pageCount"),
                "access_rights": record.get("accessRights"),
                "part_of_journal": record.get("isPartOf", {}).get("journalTitle", None)
            }

        except Exception as e:
            print(f"[{htid}] Exception: {e}")
            time.sleep(wait)
            retries += 1
            wait *= 2

    print(f"[{htid}] Failed after {max_retries} retries.")
    return None


print(f"Fetching metadata for {len(df_missing)} volumes...")

for _, row in tqdm(df_missing.iterrows(), total=len(df_missing)):
    htid = row["id"]
    result = fetch_metadata(htid)
    if result:
        results.append(result)
    time.sleep(1.5)  # polite interval

meta_df = pd.DataFrame(results)
meta_df.to_csv("bib_metadata_fill.csv", index=False)


import json
from pathlib import Path
import pandas as pd

docids_path = Path("corpusbuilding/my_docids.txt")
genre_dir = Path("genrepredictions/") 

with open(docids_path) as f:
    docids = [line.strip() for line in f if line.strip()]

data = []

for docid in docids:
    json_path = genre_dir / f"{docid}.json"
    if not json_path.exists():
        continue  # skip if missing
    with open(json_path) as jf:
        info = json.load(jf)

    try:
        row = {
            "docid": docid,
            "title": info.get("hathi_metadata", {}).get("title"),
            "author": info.get("hathi_metadata", {}).get("author"),
            "inferred_date": info.get("hathi_metadata", {}).get("inferred_date"),
            "pages_fic": info.get("fiction", {}).get("pages_fic"),
            "pct_fic": info.get("fiction", {}).get("pct_fic"),
            "totalpages": info.get("added_metadata", {}).get("totalpages")
        }
        data.append(row)
    except Exception as e:
        print(f"Error with {docid}: {e}")

df = pd.DataFrame(data)
df.to_csv("fiction_proportions.csv", index=False)
print(f"{len(df)} out of {len(docids)} volumes had genre predictions.")

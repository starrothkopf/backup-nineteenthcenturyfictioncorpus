import pandas as pd
import re
from pathlib import Path

df = pd.read_csv("rich_noveltm_ef_filtered.csv").fillna("")
title_fields = df[['title', 'parttitle', 'shorttitle']].astype(str)

df['full_title'] = title_fields.apply(lambda x: ' '.join(x).lower(), axis=1)

keywords = [
    "stories", "tales", "sketches", "narratives", "fables", "anecdotes",
    "legends", "yarns", "episodes", "chronicles", "recollections",
    "short stories", "collection", "miscellanies", "selections", "scenes"
]

# output folder
output_dir = Path("keyword_analysis_outputs")
output_dir.mkdir(exist_ok=True)

summary = []

for kw in keywords:
    pattern = rf'\b{re.escape(kw)}\b'
    
    df[kw + '_match'] = df['full_title'].str.contains(pattern, regex=True)
    match_df = df[df[kw + '_match']].copy()

    # save sample of matches
    sample = match_df[['docid', 'title', 'parttitle', 'shorttitle']].head(20)
    sample.to_csv(output_dir / f"{kw}_sample.csv", index=False)

    # save all matches if needed
    match_df.to_csv(output_dir / f"{kw}_all_matches.csv", index=False)

    summary.append({
        "keyword": kw,
        "match_count": len(match_df),
        "example_docid": sample['docid'].tolist()
    })

pd.DataFrame(summary).to_csv(output_dir / "keyword_summary.csv", index=False)

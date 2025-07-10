import pandas as pd
import re

df = pd.read_csv("rich_noveltm_ef_filtered.csv")

keywords = [
    "stories", "tales", "sketches", "narratives", "fables", "anecdotes",
    "legends", "yarns", "episodes", "chronicles", "recollections",
    "short stories", "collection", "miscellanies", "selections", "scenes"
]

pattern = r'\b(?:' + '|'.join(re.escape(k) for k in keywords) + r')\b'
pattern = pattern.lower()

title_fields = df[['title', 'parttitle', 'shorttitle']].fillna("").astype(str).apply(lambda x: ' '.join(x), axis=1).str.lower()

df_seed = df[title_fields.str.contains(pattern, regex=True)]

df_seed.to_csv("short_story_seed_volumes.csv", index=False)
print(f"likely {len(df_seed)} volumes are short story collections")

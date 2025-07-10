import pandas as pd
from collections import Counter

df = pd.read_csv('/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/filtered_titlemeta_with_gender.tsv', sep='\t')
print(f"\nTotal entries: {len(df)}")

genre_series = df['genres'].dropna().astype(str).str.lower().str.split('|')
all_genres = [g.strip() for sublist in genre_series for g in sublist]
genre_counts = Counter(all_genres)

# top genres
for genre, count in genre_counts.most_common(50):
    print(f"{genre}: {count}")

# pub years
if 'inferreddate' in df.columns:
    df['year_bucket'] = (df['inferreddate'] // 10 * 10).astype(int)
    print("\n publication year distribution by decade:")
    print(df['year_bucket'].value_counts().sort_index())

# top authors
if 'author' in df.columns:
    print("\n most common authors:")
    print(df['author'].value_counts().head(15))

# top places (no ireland?)
if 'place' in df.columns:
    print("\n most common MARC country codes:")
    print(df['place'].value_counts().head(10))

contents_series = df['contents'].dropna().astype(str).str.lower().str.split('|')
all_contents = [g.strip() for sublist in contents_series for g in sublist]
contents_counts = Counter(all_contents)

# contents??
for contents, count in contents_counts.most_common(50):
    print(f"{contents}: {count}")
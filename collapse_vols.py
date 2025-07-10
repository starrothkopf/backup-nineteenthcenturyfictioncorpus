import pandas as pd

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/rich_noveltm_ef_filtered.csv")

df['title'] = df['title'].fillna("").astype(str).str.strip().str.lower()
df['shorttitle'] = df['shorttitle'].fillna("").astype(str).str.strip().str.lower()

# use shorttitle when available, otherwise fall back to title
df['group_title'] = df['shorttitle'].where(df['shorttitle'] != "", df['title'])

# group by title + author to better identify works
df['author'] = df['author'].fillna("").astype(str).str.strip().str.lower()
df['volume_key'] = df['group_title'] + "::" + df['author']

# count how many rows would be collapsed if we only kept one row per volume_key
volume_groups = df.groupby('volume_key')
collapsed_df = volume_groups.first().reset_index()

original_count = len(df)
collapsed_count = len(collapsed_df)
rows_lost = original_count - collapsed_count

print(f"original rows: {original_count}")
print(f"collapsed rows: {collapsed_count}")
print(f"rows lost if collapsing volumes: {rows_lost}")

# output high-volume groups for inspection
multi_volume_works = volume_groups.size().reset_index(name='volume_count')
multi_volume_works = multi_volume_works[multi_volume_works['volume_count'] > 1]
multi_volume_works.to_csv("multi_volume_candidates.csv", index=False)

# show 3 random multi-volume works and the rows from df that belong to them
sample_keys = multi_volume_works['volume_key'].sample(3, random_state=42).tolist()

for key in sample_keys:
    print(f"\n--- Group: {key} ---")
    display_cols = ['docid', 'title', 'shorttitle', 'enumcron', 'volnum', 'author']
    print(df[df['volume_key'] == key][display_cols])
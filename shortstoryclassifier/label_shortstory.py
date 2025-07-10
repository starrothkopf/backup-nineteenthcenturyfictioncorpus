import pandas as pd

df_all = pd.read_csv("rich_noveltm_ef_filtered.csv")
df_short = pd.read_csv("short_story_seed_volumes.csv")

df_short['shortstory'] = 1

# create a set of all short story docids
short_ids = set(df_short['docid'])
df_all['shortstory'] = df_all['docid'].apply(lambda x: 1 if x in short_ids else 0)

df_all.to_csv("rich_noveltm_ef_labeled.csv", index=False)

print("Saved labeled dataset to 'rich_noveltm_ef_labeled.csv'")

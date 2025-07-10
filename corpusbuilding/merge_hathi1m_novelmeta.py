import pandas as pd

df_hathi = pd.read_csv("hathi1m.csv")
df_noveltm = pd.read_csv("filtered_titlemeta_with_gender.tsv", sep="\t")

df_hathi['docid'] = df_hathi['htid']  
# df_noveltm['htid'] = df_noveltm['docid']

# merge on docid
df_merged = df_hathi.merge(
    df_noveltm[
        ['docid', 'author', 'inferreddate', 'enumcron', 'volnum', 'nonficprob',
         'place', 'genres', 'first_name', 'estimated_gender']
    ],
    on='docid',
    how='inner'  # only keep rows where docid is in both
)

df_merged.to_csv("merged_hathi1m_with_novelmeta.csv", index=False)

print(f"Merged dataset contains {len(df_merged)} rows.")
print("Sample:")
print(df_merged.head())
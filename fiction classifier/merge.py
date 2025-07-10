import pandas as pd

meta_df = pd.read_csv("noveltm_ef.csv")
fic_df = pd.read_csv("fiction_proportions.csv")

merged_df = meta_df.merge(fic_df[['docid', 'pct_fic']], on='docid', how='left')

merged_df['label_fiction'] = merged_df['pct_fic'].apply(lambda x: 1 if x >= 0.7 else 0 if pd.notnull(x) else None)

merged_df.to_csv("noveltm_with_fiction_labels.csv", index=False)

print(f"Labeled fiction in {merged_df.shape[0]} volumes.")
print(merged_df['label_fiction'].value_counts())

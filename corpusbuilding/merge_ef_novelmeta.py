import pandas as pd

meta_df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/filtered_titlemeta_with_gender.tsv", sep="\t")
ef_df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/ef_rich_features_cleaned.csv")

# normalize
ef_df = ef_df.rename(columns={"id": "docid"})
def normalize_id(htid):
    return htid.replace(':', '+').replace('/', '=')
ef_df['docid'] = ef_df['docid'].apply(normalize_id)
meta_df['docid'] = meta_df['docid'].apply(str)

# merge
merged_df = pd.merge(meta_df, ef_df, on="docid", how="inner")

merged_df.to_csv("merged_metadata_with_ef.csv", index=False)
print(f"Merged dataset has {len(merged_df)} rows.")
print("Saved to merged_metadata_with_ef.csv")

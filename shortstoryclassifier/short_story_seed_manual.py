import pandas as pd

df = pd.read_csv("short_story_seed_volumes.csv")

selected_rows = []

manual_ids = [
    "nyp.33433088073691",
    "mdp.39015030708971",
    "njp.32101071963480",
    "hvd.hn2u4x",
    "nyp.33433074918859",
    "mdp.39015024477674",
    "uc2.ark+=13960=t9t14wb76",
    "njp.32101048392763",
    "nyp.33433087358507",
    "hvd.hwkd81",
    "hvd.hwjvwl",
    "uc2.ark+=13960=t4qj7c31z",
    "mdp.39015064443982",
    "uc1.b3322552",
    "mdp.39015048902913",
    "mdp.39015002151234",
    "uc2.ark+=13960=t9z03906q",
    "uc1.b3327099",
    "nyp.33433068032923",
    "nyp.33433068188691",
    "mdp.39015028703083",
    "uc2.ark+=13960=t3gx4d83s",

]

# good label: and other stories 

for docid in manual_ids:
    match = df[df['docid'] == docid]
    if not match.empty:
        selected_rows.append(match.iloc[0]) 

short_story_df = pd.DataFrame(selected_rows)

short_story_df.to_csv("short_story_seed_manual.csv", index=False)
print(f"saved {len(short_story_df)} manually selected volumes")

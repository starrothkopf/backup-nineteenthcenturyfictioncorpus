import pandas as pd

df = pd.read_csv("short_story_seed_volumes.csv")

# randomly sample 100 rows to avoid selection bias
sample = df.sample(n=100, random_state=42)  # set seed for reproducibility

sample.to_csv("short_story_sample_for_manual_check.csv", index=False)
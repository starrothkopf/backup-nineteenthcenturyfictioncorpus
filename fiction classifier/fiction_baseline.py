import pandas as pd

df = pd.read_csv("noveltm_ef.csv")
fiction_df = df[df['genre'].str.contains('fiction', case=False, na=False)]

threshold = 150
fiction_df = fiction_df[fiction_df['page_count'] >= threshold]

fiction_df.to_csv("fiction_baseline_filtered.csv", index=False)
print(f"remaining entries after filtering: {len(fiction_df)}")

"""
threshold: 70 pages → remaining entries: 10394 (98.81%)
threshold: 100 pages → remaining entries: 10296 (97.88%)
threshold: 125 pages → remaining entries: 10178 (96.76%)
threshold: 150 pages → remaining entries: 9996 (95.03%)
threshold: 200 pages → remaining entries: 9529 (90.59%)
threshold: 250 pages → remaining entries: 8720 (82.90%)
"""
import pandas as pd
from collections import Counter
import ast

# Load data
df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/ef_rich_features_cleaned.csv", dtype=str)

# Convert numeric columns
numeric_cols = [
    'avg_sentence_count', 'var_sentence_count',
    'avg_line_count', 'var_line_count',
    'avg_tokens_per_page', 'var_tokens_per_page',
    'cap_alpha_freq', 'page_count'
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

print("== Dataset Overview ==")
print(f"Total rows: {len(df)}\n")
print("== Missing Values per Column ==")
print(df.isna().sum())

print("\n== Basic Stats for Numeric Columns ==")
print(df[numeric_cols].describe().T)


# Helper to parse list-likes
def safe_parse_list(x):
    if pd.isna(x):
        return []
    try:
        return ast.literal_eval(x)
    except:
        return [x]

# Parse and flatten genre_tag and lcc_category
genres = df['genre_tag'].dropna().map(safe_parse_list).explode()
lccs = df['lcc_category'].dropna().map(safe_parse_list).explode()

print("\n== Most Common Genres ==")
print(genres.value_counts().head(12))

print("\n== Most Common LCC Categories ==")
print(lccs.value_counts().head(20))

print("\n== Top Part-of-Journal Titles ==")
print(df['part_of_journal'].dropna().value_counts().head(10))

# Find columns with low information content
print("\n== Mostly Empty or Single-Value Columns ==")
for col in df.columns:
    unique_vals = df[col].nunique(dropna=True)
    if unique_vals <= 1 or df[col].isna().mean() > 0.9:
        print(f"{col}: {unique_vals} unique, {df[col].isna().mean():.2%} missing")
